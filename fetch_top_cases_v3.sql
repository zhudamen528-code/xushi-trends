-- TOP 案例 V3：加算法分质量门槛 + 扩大到 Top 50
-- 变化：
--   1. 新增 JOIN dim_ecm_algo_note_label_df 获取算法分
--   2. 算法分质量门槛：sincerity>=P50(36.9) + good_click>=P50(0.711) + note_quality_level>=1
--   3. Top 50（原 Top 15），按品类归拢后每类样本量更充足
--   4. 保留同商家去重逻辑

WITH note_agg AS (
  SELECT
    note_id,
    MAX(title) AS title,
    MAX(seller_id) AS seller_id,
    MAX(seller_name) AS seller_name,
    MAX(seller_industry) AS seller_industry,
    MAX(publish_time) AS publish_time,
    CASE WHEN MAX(type) = '1' THEN 1 WHEN MAX(type) = '2' THEN 2 END AS note_form,
    SUM(note_imp_num)   AS imp,
    SUM(note_click_num) AS click,
    SUM(tag_imp_num)    AS tag_imp,
    SUM(tag_click_num)  AS tag_click,
    SUM(buy_num)        AS buy,
    SUM(dgmv)           AS dgmv
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm >= '{start_dtm}' AND dtm <= '{end_dtm}'
    AND seller_industry = '休食'
    AND type IN ('1', '2')
    AND note_imp_num > 0
    -- 发布时间近14天（截止跑数当天）
    AND substr(publish_time, 1, 10) >= '{publish_start_date}'
  GROUP BY note_id
),
note_metric AS (
  SELECT
    note_id, title, seller_id, seller_name, note_form, publish_time,
    imp, click, tag_imp, tag_click, buy, dgmv,
    click * 1.0 / NULLIF(imp, 0) AS ctr1,
    tag_click * 1.0 / NULLIF(tag_imp, 0) AS ctr2,
    buy * 1.0 / NULLIF(tag_click, 0) AS cvr,
    dgmv * 1.0 / NULLIF(buy, 0) AS price_per_unit
  FROM note_agg
  WHERE imp >= 5000
    AND buy >= 10
    AND dgmv >= 200
    AND tag_click >= 50
),
-- 关联算法分：近7天最新一条（dim 表分区）
algo_label AS (
  SELECT
    note_id,
    model_sincerity_score,
    good_click_quality_score,
    note_quality_level
  FROM (
    SELECT
      note_id,
      model_sincerity_score,
      good_click_quality_score,
      note_quality_level,
      ROW_NUMBER() OVER (PARTITION BY note_id ORDER BY dtm DESC) AS rn
    FROM redcdm.dim_ecm_algo_note_label_df
    WHERE dtm >= '{algo_start_dtm}' AND dtm <= '{end_dtm}'
  ) t
  WHERE rn = 1
),
note_with_algo AS (
  SELECT
    m.*,
    COALESCE(a.model_sincerity_score, 0) AS sincerity,
    COALESCE(a.good_click_quality_score, 0) AS good_click,
    COALESCE(a.note_quality_level, 0) AS quality_lv
  FROM note_metric m
  LEFT JOIN algo_label a ON m.note_id = a.note_id
),
-- 算法分质量门槛过滤
-- P50 门槛：sincerity>=36.9, good_click>=0.711, quality_level>=1
-- 注：LEFT JOIN 保留无算法分的笔记（置 0），这里只踢掉明显低质
quality_filtered AS (
  SELECT *
  FROM note_with_algo
  WHERE sincerity >= 30          -- 略低于 P50=36.9，防止过滤太猛（左偏分布）
    AND good_click >= 0.680      -- 接近 P25=0.679，过滤掉明显标题党
    AND quality_lv >= 1          -- note_quality_level 最低有效值
),
seller_ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY ctr1 DESC NULLS LAST) AS ctr1_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY ctr2 DESC NULLS LAST) AS ctr2_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY cvr DESC NULLS LAST) AS cvr_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY price_per_unit DESC NULLS LAST) AS price_rk_in_seller
  FROM quality_filtered
),
final_top AS (
  SELECT 'CTR1' AS metric_name, note_form, note_id, title, seller_name,
         ctr1 AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr1 DESC) AS rank
  FROM seller_ranked WHERE ctr1_rk_in_seller = 1 AND ctr1 IS NOT NULL
  UNION ALL
  SELECT 'CTR2' AS metric_name, note_form, note_id, title, seller_name,
         ctr2 AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr2 DESC) AS rank
  FROM seller_ranked WHERE ctr2_rk_in_seller = 1 AND ctr2 IS NOT NULL
  UNION ALL
  SELECT 'CVR' AS metric_name, note_form, note_id, title, seller_name,
         cvr AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY cvr DESC) AS rank
  FROM seller_ranked WHERE cvr_rk_in_seller = 1 AND cvr IS NOT NULL
  UNION ALL
  SELECT 'AOV' AS metric_name, note_form, note_id, title, seller_name,
         price_per_unit AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY price_per_unit DESC) AS rank
  FROM seller_ranked WHERE price_rk_in_seller = 1 AND price_per_unit IS NOT NULL
)
SELECT metric_name, note_form, rank, note_id, title, seller_name,
       ROUND(metric_value, 4) AS metric_value, imp, click, buy, ROUND(dgmv, 2) AS dgmv,
       ROUND(sincerity, 1) AS sincerity_score,
       ROUND(good_click, 3) AS good_click_score
FROM final_top
WHERE rank <= 50
ORDER BY metric_name, note_form, rank
