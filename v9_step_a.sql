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
algo_raw AS (
  SELECT
    nm.note_id, nm.seller_id, nm.seller_name, nm.goods_id, nm.bridge_type,
    nm.total_imp, nm.total_clk, nm.total_gv, nm.total_buy, nm.total_dgmv,
    nm.gpm, nm.ctr1_pct,
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
    s.publish_days,
    s.tob_b_level_30d,
    s.tob_seller_period_level,
    s.cover_url,
    a.note_quality_level,
    a.score AS purchase_intent_score
  FROM note_metric nm
  LEFT JOIN redapp.app_ecm_ark_ai_note_score_base_nd_di s
    ON s.dtm = '20260614' AND s.note_id = nm.note_id
  LEFT JOIN redcdm.dim_ecm_algo_note_label_df a
    ON a.dtm = '20260614' AND a.note_id = nm.note_id
  WHERE s.note_id IS NOT NULL
    AND s.good_click_quality_score IS NOT NULL
    AND s.low_bad_market_score IS NOT NULL
    AND s.model_sincerity_score IS NOT NULL
),
algo_ranked AS (
  SELECT *,
    PERCENT_RANK() OVER (ORDER BY low_bad_market_score) AS rk_low_bad,
    PERCENT_RANK() OVER (ORDER BY good_click_quality_score DESC) AS rk_good_click,
    PERCENT_RANK() OVER (ORDER BY model_sincerity_score DESC) AS rk_sincerity
  FROM algo_raw
),
algo_scored AS (
  SELECT *,
    (rk_low_bad + rk_good_click + rk_sincerity) / 3 AS algo_quality_rank
  FROM algo_ranked
),
note_filtered AS (
  SELECT *,
    CASE
      WHEN total_dgmv >= 50000 THEN '爆款'
      WHEN total_dgmv >= 10000 THEN '优秀'
      WHEN total_imp < 10000 AND gpm > 100 THEN '黑马'
      ELSE '常规'
    END AS tier
  FROM algo_scored
  WHERE algo_quality_rank < 0.5
    AND COALESCE(creation_level, 'X') IN ('E','S','A','B')
    AND COALESCE(spam_level, '正常') = '正常'
    AND COALESCE(audit_level, 2) IN (2,3,4)
)
SELECT *,
  ROW_NUMBER() OVER (PARTITION BY tier ORDER BY gpm DESC) AS rn_in_tier
FROM note_filtered
WHERE tier IN ('爆款','优秀','黑马')
ORDER BY tier, gpm DESC
LIMIT 1500
