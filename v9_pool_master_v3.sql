-- V9 PoolV3 · 30 天滑窗 + 类目内相对分位算法筛
-- 输出每条笔记：行为指标 + 算法分（含相对分位）+ 笔记内容 + 商品 + 评论 Top5
-- 算法筛逻辑：综合算法 quality rank（低差营销+有效点击+真诚度三分位平均）< 0.5
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
),
ranked_by_tier AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY tier ORDER BY gpm DESC) AS rn_in_tier
  FROM note_filtered
  WHERE tier IN ('爆款','优秀','黑马')
),
note_content AS (
  SELECT note_id, title, content, video_asr_text,
    SUBSTR(merge_content_v2, 1, 500) AS merge_content_v2,
    note_type, image_num, brand_account_name
  FROM redcdm.dwd_con_note_info_all_df
  WHERE dtm = '20260614'
),
note_ext AS (
  SELECT note_id, taxonomy1, taxonomy2, taxonomy3, duration, is_multi_goods_note, goods_num
  FROM redcdm.dim_ecm_note_extend_df
  WHERE dtm = '20260614'
),
goods_info AS (
  SELECT goods_id, goods_name, goods_price, brand_name, third_category_name
  FROM redcdm.dim_goods_base_df
  WHERE dtm = '20260614'
),
comments_agg AS (
  SELECT discovery_id AS note_id,
    CONCAT_WS(' || ', COLLECT_LIST(content)) AS top_cmts
  FROM (
    SELECT discovery_id, content,
      ROW_NUMBER() OVER (PARTITION BY discovery_id ORDER BY like_num DESC) AS rn
    FROM reddw.dw_soc_discovery_comment_detail_day
    WHERE dtm BETWEEN '20260516' AND '20260614'
  ) t WHERE rn <= 5
  GROUP BY discovery_id
)
SELECT
  rt.tier,
  rt.note_id,
  rt.seller_name,
  rt.bridge_type,
  rt.total_dgmv,
  rt.total_imp,
  rt.total_clk,
  rt.total_gv,
  rt.total_buy,
  rt.gpm,
  rt.ctr1_pct,
  nc.note_type,
  nc.title,
  SUBSTR(nc.content, 1, 500) AS content_snip,
  nc.merge_content_v2,
  SUBSTR(COALESCE(nc.video_asr_text,''), 1, 800) AS asr_snip,
  nc.image_num,
  ne.taxonomy1, ne.taxonomy2, ne.taxonomy3, ne.duration, ne.is_multi_goods_note,
  gi.goods_name, gi.goods_price, gi.brand_name, gi.third_category_name AS goods_cat3,
  rt.cover_url,
  rt.good_click_quality_score,
  rt.low_bad_market_score,
  rt.model_sincerity_score,
  rt.model_sincerity_level,
  rt.creation_level,
  rt.aigc_score,
  rt.first_img_aesthetic_level,
  rt.first_img_beauty_level,
  rt.first_img_quality_level,
  rt.first_img_definition_level,
  rt.note_unfriendly_score,
  rt.neg_emotion_score,
  rt.note_quality_level,
  rt.purchase_intent_score,
  rt.ces_score_td,
  rt.fans_num,
  rt.tob_b_level_30d,
  rt.tob_seller_period_level,
  rt.rk_low_bad,
  rt.rk_good_click,
  rt.rk_sincerity,
  rt.algo_quality_rank,
  rt.rn_in_tier,
  SUBSTR(COALESCE(ca.top_cmts,''), 1, 600) AS top5_cmts
FROM ranked_by_tier rt
LEFT JOIN note_content nc ON nc.note_id = rt.note_id
LEFT JOIN note_ext ne ON ne.note_id = rt.note_id
LEFT JOIN goods_info gi ON gi.goods_id = rt.goods_id
LEFT JOIN comments_agg ca ON ca.note_id = rt.note_id
WHERE rt.rn_in_tier <= 400
ORDER BY rt.tier, rt.gpm DESC
;
