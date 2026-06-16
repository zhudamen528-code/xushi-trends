-- V9 PoolV2 完整池 SQL · 30 天 + 算法分参与
-- 输出每条笔记：行为指标 + 算法分 + 笔记内容 + 商品 + 评论
-- 全量数据用 DOWNLOAD 模式拉，预计 800-1200 条

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
),
note_filtered AS (
  SELECT *,
    CASE
      WHEN total_dgmv >= 50000 THEN '爆款'
      WHEN total_dgmv >= 10000 THEN '优秀'
      WHEN total_imp < 10000 AND gpm > 100 THEN '黑马'
      ELSE '常规'
    END AS tier
  FROM note_with_algo
  WHERE COALESCE(good_click_quality_score, 0) > 0.7
    AND COALESCE(low_bad_market_score, 0) < 0.5
    AND COALESCE(creation_level, 'X') IN ('E','S','A','B')
    AND COALESCE(model_sincerity_score, 0) > 10
    AND COALESCE(spam_level, '正常') = '正常'
    AND COALESCE(audit_level, 2) IN (2,3,4)
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
  WHERE dt = '20260614'
),
comments_agg AS (
  SELECT discovery_id AS note_id,
    CONCAT_WS(' || ', COLLECT_LIST(content)) AS top_cmts
  FROM (
    SELECT discovery_id, content,
      ROW_NUMBER() OVER (PARTITION BY discovery_id ORDER BY like_num DESC) AS rn
    FROM reddw.dw_soc_discovery_comment_detail_day
    WHERE dt BETWEEN '20260516' AND '20260614'
  ) t WHERE rn <= 5
  GROUP BY discovery_id
)
SELECT
  nf.tier,
  nf.note_id,
  nf.seller_name,
  nf.bridge_type,
  nf.total_dgmv,
  nf.total_imp,
  nf.total_clk,
  nf.total_gv,
  nf.total_buy,
  nf.gpm,
  nf.ctr1_pct,
  nc.note_type,
  nc.title,
  SUBSTR(nc.content, 1, 500) AS content_snip,
  nc.merge_content_v2,
  SUBSTR(COALESCE(nc.video_asr_text,''), 1, 800) AS asr_snip,
  nc.image_num,
  ne.taxonomy1, ne.taxonomy2, ne.taxonomy3, ne.duration, ne.is_multi_goods_note,
  gi.goods_name, gi.goods_price, gi.brand_name, gi.third_category_name AS goods_cat3,
  nf.cover_url,
  -- 算法分（V9 核心）
  nf.good_click_quality_score,
  nf.low_bad_market_score,
  nf.model_sincerity_score,
  nf.model_sincerity_level,
  nf.creation_level,
  nf.aigc_score,
  nf.first_img_aesthetic_level,
  nf.first_img_beauty_level,
  nf.first_img_quality_level,
  nf.first_img_definition_level,
  nf.note_unfriendly_score,
  nf.neg_emotion_score,
  nf.note_quality_level,
  nf.purchase_intent_score,
  nf.ces_score_td,
  nf.fans_num,
  nf.tob_b_level_30d,
  nf.tob_seller_period_level,
  SUBSTR(COALESCE(ca.top_cmts,''), 1, 600) AS top5_cmts
FROM note_filtered nf
LEFT JOIN note_content nc ON nc.note_id = nf.note_id
LEFT JOIN note_ext ne ON ne.note_id = nf.note_id
LEFT JOIN goods_info gi ON gi.goods_id = nf.goods_id
LEFT JOIN comments_agg ca ON ca.note_id = nf.note_id
;
