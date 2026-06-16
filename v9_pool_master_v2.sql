-- V9 PoolV2 · 30 天滑窗 / 算法分参与筛选
-- 时间窗：20260516 - 20260614（最近 30 天，截止 T-1）
-- 目标：在算法分约束下取最优 N 条笔记，方法论复用

WITH note_metric AS (
  SELECT
    note_id,
    MAX(seller_id) AS seller_id,
    MAX(seller_name) AS seller_name,
    MAX(goods_id) AS goods_id,
    MAX(bridge_type) AS bridge_type,
    SUM(note_imp_num) AS total_imp,
    SUM(note_click_num) AS total_clk,
    SUM(goods_view_num) AS total_gv,
    SUM(buy_num) AS total_buy,
    SUM(dgmv) AS total_dgmv,
    1000.0 * SUM(dgmv) / NULLIF(SUM(note_imp_num),0) AS gpm,
    100.0 * SUM(note_click_num) / NULLIF(SUM(note_imp_num),0) AS ctr1_pct
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm BETWEEN '20260516' AND '20260614'
    AND bridge_type IN ('goods_v2','goods_seller')
    AND seller_industry = '休食'
  GROUP BY note_id
  HAVING SUM(note_imp_num) >= 500 AND SUM(dgmv) >= 100
),
note_with_algo AS (
  SELECT
    nm.*,
    -- 算法分（来自 394 字段宽表）
    s.good_click_quality_score,
    s.low_bad_market_score,
    s.model_sincerity_score,
    s.model_sincerity_level,
    s.creation_level,
    s.aigc_score,
    s.first_img_aesthetic_level,
    s.first_img_beauty_level,
    s.first_img_quality_level,
    s.first_img_definition_level,
    s.note_unfriendly_score,
    s.neg_emotion_score,
    s.spam_level,
    s.level AS audit_level,
    s.ces_score_td,
    s.fans_num,
    s.real_fans_num_accum,
    s.publish_days,
    s.tob_b_level_30d,
    s.tob_seller_period_level,
    -- 算法质量结论
    a.note_quality_level,
    a.score AS purchase_intent_score
  FROM note_metric nm
  LEFT JOIN redapp.app_ecm_ark_ai_note_score_base_nd_di s
    ON s.dtm = '20260614' AND s.note_id = nm.note_id
  LEFT JOIN redcdm.dim_ecm_algo_note_label_df a
    ON a.dtm = '20260614' AND a.note_id = nm.note_id
),
note_filtered AS (
  -- 4 道算法筛
  SELECT *
  FROM note_with_algo
  WHERE COALESCE(good_click_quality_score, 0) > 0.7    -- 非标题党
    AND COALESCE(low_bad_market_score, 0) < 0.5         -- 非低质营销
    AND COALESCE(creation_level, 'X') IN ('E','S','A','B')  -- 非低劣作者
    AND COALESCE(model_sincerity_score, 0) > 10         -- 不算过度营销
    AND COALESCE(spam_level, '正常') = '正常'           -- 非作弊
    AND COALESCE(audit_level, 2) IN (2,3,4)             -- 已通过审核（含限流过滤）
)
SELECT
  COUNT(*) AS total_count,
  SUM(CASE WHEN total_dgmv >= 50000 THEN 1 ELSE 0 END) AS tier_baokuan,
  SUM(CASE WHEN total_dgmv >= 10000 AND total_dgmv < 50000 THEN 1 ELSE 0 END) AS tier_youxiu,
  SUM(CASE WHEN total_imp < 10000 AND gpm > 100 THEN 1 ELSE 0 END) AS tier_heima,
  -- 算法分布
  AVG(good_click_quality_score) AS avg_good_click,
  AVG(low_bad_market_score) AS avg_low_bad,
  AVG(model_sincerity_score) AS avg_sincerity,
  COUNT(DISTINCT seller_id) AS uniq_seller,
  COUNT(DISTINCT goods_id) AS uniq_goods
FROM note_filtered
;
