-- TOP 案例 V3：算法分质量门槛（3核心 + 4封面）+ 扩大到 Top 50
-- 门槛说明：
--   核心门槛（dim_ecm_algo_note_label_df）：
--     sincerity >= 30（P50=36.9，左偏分布容错）
--     good_click >= 0.680（P25=0.679，过滤标题党）
--     note_quality_level >= 1
--   封面门槛（app_ecm_ark_ai_note_score_base_nd_di，仅 CTR1 聚类用到）：
--     first_img_aesthetic_level != '低'（83条/5.6% 过滤）
--     first_img_definition_level != '低'（124条/8.3% 过滤）
--     first_img_quality_level != '低'（8条/0.5% 过滤）
--     注：first_img_beauty_level 不设门槛（44% 低，过滤太猛）
--   输出 Top 50 × 4 指标 × 2 形态 = 最多 400 条案例
--   同商家去重保留

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
-- 所有算法分统一从 394字段宽表拉取
-- 注：note_quality_level 在宽表中不存在，改用 creation_level（E>S>A>B>C，C=低劣）
algo_all AS (
  SELECT
    note_id,
    model_sincerity_score,
    good_click_quality_score,
    creation_level,
    first_img_aesthetic_level,
    first_img_beauty_level,
    first_img_quality_level,
    first_img_definition_level
  FROM (
    SELECT
      note_id,
      model_sincerity_score,
      good_click_quality_score,
      creation_level,
      first_img_aesthetic_level,
      first_img_beauty_level,
      first_img_quality_level,
      first_img_definition_level,
      ROW_NUMBER() OVER (PARTITION BY note_id ORDER BY dtm DESC) AS rn
    FROM redapp.app_ecm_ark_ai_note_score_base_nd_di
    WHERE dtm >= '{algo_start_dtm}' AND dtm <= '{end_dtm}'
  ) t
  WHERE rn = 1
),
note_with_algo AS (
  SELECT
    m.*,
    COALESCE(a.model_sincerity_score, 0) AS sincerity,
    COALESCE(a.good_click_quality_score, 0) AS good_click,
    COALESCE(a.creation_level, 'B') AS creation_lv,
    COALESCE(a.first_img_aesthetic_level, '中') AS aesthetic_lv,
    COALESCE(a.first_img_quality_level, '高') AS quality_img_lv,
    COALESCE(a.first_img_definition_level, '中') AS definition_lv
  FROM note_metric m
  LEFT JOIN algo_all a ON m.note_id = a.note_id
),
-- 门槛：sincerity>=30, good_click>=0.68, creation_level!=C, 封面三项!=低
quality_filtered AS (
  SELECT *
  FROM note_with_algo
  WHERE sincerity >= 30
    AND good_click >= 0.680
    AND creation_lv != 'C'
    AND aesthetic_lv != '低'
    AND definition_lv != '低'
    AND quality_img_lv != '低'
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
         sincerity, good_click, aesthetic_lv, definition_lv, quality_img_lv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr1 DESC) AS rank
  FROM seller_ranked WHERE ctr1_rk_in_seller = 1 AND ctr1 IS NOT NULL
  UNION ALL
  SELECT 'CTR2' AS metric_name, note_form, note_id, title, seller_name,
         ctr2 AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click, aesthetic_lv, definition_lv, quality_img_lv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr2 DESC) AS rank
  FROM seller_ranked WHERE ctr2_rk_in_seller = 1 AND ctr2 IS NOT NULL
  UNION ALL
  SELECT 'CVR' AS metric_name, note_form, note_id, title, seller_name,
         cvr AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click, aesthetic_lv, definition_lv, quality_img_lv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY cvr DESC) AS rank
  FROM seller_ranked WHERE cvr_rk_in_seller = 1 AND cvr IS NOT NULL
  UNION ALL
  SELECT 'AOV' AS metric_name, note_form, note_id, title, seller_name,
         price_per_unit AS metric_value, imp, click, buy, dgmv,
         sincerity, good_click, aesthetic_lv, definition_lv, quality_img_lv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY price_per_unit DESC) AS rank
  FROM seller_ranked WHERE price_rk_in_seller = 1 AND price_per_unit IS NOT NULL
)
SELECT metric_name, note_form, rank, note_id, title, seller_name,
       ROUND(metric_value, 4) AS metric_value, imp, click, buy, ROUND(dgmv, 2) AS dgmv,
       ROUND(sincerity, 1) AS sincerity_score,
       ROUND(good_click, 3) AS good_click_score,
       aesthetic_lv AS cover_aesthetic,
       definition_lv AS cover_definition,
       quality_img_lv AS cover_quality
FROM final_top
WHERE rank <= 50
ORDER BY metric_name, note_form, rank
