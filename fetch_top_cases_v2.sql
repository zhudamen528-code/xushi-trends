-- TOP 案例 V2：发布时间近14天 + 同商家去重 + 提高质量阈值
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
  WHERE imp >= 5000        -- 曝光>=5000 (过滤虚高)
    AND buy >= 10          -- 下单>=10
    AND dgmv >= 200        -- 实际成交>=200元 (确保是真"优秀")
    AND tag_click >= 50    -- 商品卡点击>=50 (CTR2/CVR有意义)
),
seller_ranked AS (
  -- 同商家每个指标×形态最多保留1篇（取该指标最高的那篇）
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY ctr1 DESC NULLS LAST) AS ctr1_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY ctr2 DESC NULLS LAST) AS ctr2_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY cvr DESC NULLS LAST) AS cvr_rk_in_seller,
    ROW_NUMBER() OVER (PARTITION BY seller_id, note_form ORDER BY price_per_unit DESC NULLS LAST) AS price_rk_in_seller
  FROM note_metric
),
final_top AS (
  SELECT 'CTR1' AS metric_name, note_form, note_id, title, seller_name, ctr1 AS metric_value, imp, click, buy, dgmv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr1 DESC) AS rank
  FROM seller_ranked WHERE ctr1_rk_in_seller = 1 AND ctr1 IS NOT NULL
  UNION ALL
  SELECT 'CTR2' AS metric_name, note_form, note_id, title, seller_name, ctr2 AS metric_value, imp, click, buy, dgmv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY ctr2 DESC) AS rank
  FROM seller_ranked WHERE ctr2_rk_in_seller = 1 AND ctr2 IS NOT NULL
  UNION ALL
  SELECT 'CVR' AS metric_name, note_form, note_id, title, seller_name, cvr AS metric_value, imp, click, buy, dgmv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY cvr DESC) AS rank
  FROM seller_ranked WHERE cvr_rk_in_seller = 1 AND cvr IS NOT NULL
  UNION ALL
  SELECT 'AOV' AS metric_name, note_form, note_id, title, seller_name, price_per_unit AS metric_value, imp, click, buy, dgmv,
         ROW_NUMBER() OVER (PARTITION BY note_form ORDER BY price_per_unit DESC) AS rank
  FROM seller_ranked WHERE price_rk_in_seller = 1 AND price_per_unit IS NOT NULL
)
SELECT metric_name, note_form, rank, note_id, title, seller_name,
       ROUND(metric_value, 4) AS metric_value, imp, click, buy, ROUND(dgmv, 2) AS dgmv
FROM final_top
WHERE rank <= 15   -- 多取5条做兜底，前端检测后过滤已删除
ORDER BY metric_name, note_form, rank
