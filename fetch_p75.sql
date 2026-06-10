WITH note_agg AS (
  SELECT
    note_id,
    seller_industry,
    CASE WHEN type = 1 THEN '图文' WHEN type = 2 THEN '视频' END AS note_form,
    SUM(note_imp_num)   AS imp,
    SUM(note_click_num) AS click,
    SUM(tag_imp_num)    AS tag_imp,
    SUM(tag_click_num)  AS tag_click,
    SUM(buy_num)        AS buy,
    SUM(dgmv)           AS dgmv
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm >= '{start_dtm}' AND dtm <= '{end_dtm}'
    AND seller_industry IN ('休食','大健康','生鲜','亲子生活','宠物','家用')
    AND type IN (1, 2)
    AND note_imp_num > 0
  GROUP BY note_id, seller_industry, type
),
note_metric AS (
  SELECT
    seller_industry, note_form, note_id,
    click * 1.0 / NULLIF(imp, 0) AS ctr1,
    tag_click * 1.0 / NULLIF(tag_imp, 0) AS ctr2,
    buy * 1.0 / NULLIF(tag_click, 0) AS cvr,
    dgmv * 1.0 / NULLIF(buy, 0) AS price_per_unit
  FROM note_agg
  WHERE imp >= 100
)
SELECT
  seller_industry,
  note_form,
  COUNT(*) AS note_cnt,
  ROUND(percentile_approx(ctr1, 0.5), 4) AS ctr1_p50,
  ROUND(percentile_approx(ctr1, 0.75), 4) AS ctr1_p75,
  ROUND(percentile_approx(ctr2, 0.5), 4) AS ctr2_p50,
  ROUND(percentile_approx(ctr2, 0.75), 4) AS ctr2_p75,
  ROUND(percentile_approx(cvr, 0.5), 4) AS cvr_p50,
  ROUND(percentile_approx(cvr, 0.75), 4) AS cvr_p75,
  ROUND(percentile_approx(price_per_unit, 0.5), 2) AS price_p50,
  ROUND(percentile_approx(price_per_unit, 0.75), 2) AS price_p75
FROM note_metric
GROUP BY seller_industry, note_form
ORDER BY seller_industry, note_form
