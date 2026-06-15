-- ============================================================
-- 休食 GPM 漏斗看板 V2 案例 SQL
-- 输入参数：start_dtm（60 天前）、end_dtm（昨天）、target_dtm（取维表的快照分区，=end_dtm）
-- 输出：每条笔记一行，含 dgmv/imp/gpm + 内容 + 商品 + 封面 + 打标 + 评论统计
-- ============================================================

WITH
-- Step 1: 60 天 fullchain 聚合到 note × goods 粒度
note_metric AS (
  SELECT
    note_id,
    MAX(goods_id) AS goods_id,                    -- 主推商品（如有多个取最大）
    MAX(seller_name) AS seller_name,
    MAX(anchor_identity_type) AS anchor_type,
    MAX(bridge_type) AS bridge_type,
    SUM(note_imp_num) AS total_imp,
    SUM(note_click_num) AS total_clk,
    SUM(dgmv) AS total_dgmv,
    SUM(goods_view_num) AS total_gv,
    SUM(buy_num) AS total_buy,
    SUM(goods_total) AS total_qty,
    -- GPM = 千次曝光带来的 GMV
    1000.0 * SUM(dgmv) / NULLIF(SUM(note_imp_num),0) AS gpm,
    -- CTR
    SUM(note_click_num) / NULLIF(SUM(note_imp_num),0) AS ctr
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm BETWEEN '20260413' AND '20260611'
    AND bridge_type IN ('goods_v2','goods_seller')   -- 仅商品笔记
    AND seller_industry = '休食'                       -- 限休食
  GROUP BY note_id
  HAVING SUM(note_imp_num) >= 500                    -- 最低曝光门槛
     AND SUM(dgmv) >= 100                            -- 最低 dgmv 门槛
),

-- Step 2: 三层分类
tiered AS (
  SELECT
    *,
    CASE
      WHEN total_dgmv >= 50000 THEN '爆款'
      WHEN total_dgmv BETWEEN 10000 AND 49999.99 THEN '优秀'
      WHEN total_imp < 10000 AND gpm > 100 THEN '黑马'   -- 固定阈值 GPM>100
      ELSE NULL
    END AS tier
  FROM note_metric
),

-- Step 3: 每层 TopN（按 GPM 降序，每层 200 条）
ranked AS (
  SELECT *
  FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY tier ORDER BY gpm DESC) AS rk
    FROM tiered
    WHERE tier IS NOT NULL
  ) t
  WHERE rk <= 200
),

-- Step 4: 评论聚合（用 end_dtm 当天分区即可，含近一年评论）
cmt AS (
  SELECT discovery_id AS note_id,
         COUNT(*) AS cmt_cnt,
         SUM(like_num) AS cmt_total_like,
         SUM(CASE WHEN is_author_replyed=1 THEN 1 ELSE 0 END) AS author_reply_cnt,
         -- 拼前 5 条高赞评论作为"用户声音"
         CONCAT_WS(' || ',
           COLLECT_LIST(
             CASE WHEN rk_cmt <= 5 THEN SUBSTR(content, 1, 60) ELSE NULL END
           )
         ) AS top5_cmts
  FROM (
    SELECT discovery_id, content, like_num, is_author_replyed,
           ROW_NUMBER() OVER (PARTITION BY discovery_id ORDER BY like_num DESC) AS rk_cmt
    FROM reddw.dw_soc_discovery_comment_detail_day
    WHERE dtm='20260611'
      AND enabled=true
      AND status >= 0
  ) c
  WHERE rk_cmt <= 50           -- 每个笔记只看前 50 条评论
  GROUP BY discovery_id
)

-- Step 5: 一把梭 JOIN
SELECT
  r.tier,
  r.note_id,
  r.seller_name,
  r.bridge_type,
  r.total_dgmv,
  r.total_imp,
  r.total_clk,
  r.total_gv,
  r.total_buy,
  ROUND(r.gpm, 2) AS gpm,
  ROUND(r.ctr * 100, 2) AS ctr_pct,

  -- 笔记内容
  n.note_type,
  n.title,
  SUBSTR(n.content, 1, 200) AS content_snip,
  n.merge_content_v2,
  CASE WHEN n.video_asr_text IS NOT NULL
       THEN SUBSTR(n.video_asr_text, 1, 200) END AS asr_snip,
  n.image_num,
  n.topic_list,

  -- 算法打标
  l.note_quality_level,
  l.score AS purchase_intent_score,
  l.is_individual_similar_note,
  l.is_group_similar_note,

  -- 电商笔记维表
  e.taxonomy1 AS note_taxonomy1,
  e.first_category_name AS ecm_cat1,
  e.second_category_name AS ecm_cat2,
  e.is_multi_goods_note,
  e.note_publish_type,

  -- 商品维度
  g.goods_name,
  g.spu_name,
  g.goods_price,
  g.brand_name,
  g.first_category_name AS goods_cat1,
  g.third_category_name AS goods_cat3,
  g.ipq_num AS goods_pack_qty,
  g.is_seven_day_no_reason,

  -- 封面（开箱即用！）
  cv.cover_url,

  -- 视频质量分（可能 NULL）
  v.first_frame_id,
  v.quality_score AS video_quality_score,
  v.duration AS video_duration_ms,

  -- 评论
  COALESCE(cm.cmt_cnt, 0) AS cmt_cnt,
  COALESCE(cm.cmt_total_like, 0) AS cmt_total_like,
  COALESCE(cm.author_reply_cnt, 0) AS author_reply_cnt,
  cm.top5_cmts
FROM ranked r
LEFT JOIN redcdm.dwd_con_note_info_all_df n
  ON r.note_id = n.note_id AND n.dtm = '20260611'
LEFT JOIN redcdm.dim_ecm_algo_note_label_df l
  ON r.note_id = l.note_id AND l.dtm = '20260611'
LEFT JOIN redcdm.dim_ecm_note_extend_df e
  ON r.note_id = e.note_id AND e.dtm = '20260611'
LEFT JOIN redcdm.dim_goods_base_df g
  ON r.goods_id = g.goods_id AND g.dtm = '20260611'
LEFT JOIN redapp.app_ecm_ark_ai_note_score_base_nd_di cv
  ON r.note_id = cv.note_id AND cv.dtm = '20260611'
LEFT JOIN (
  -- 同一笔记可能有多 video，取首条
  SELECT discovery_id, MAX(first_frame_id) AS first_frame_id,
         MAX(quality_score) AS quality_score, MAX(duration) AS duration
  FROM reddw.dw_soc_media_video_discovery_info_day
  WHERE dtm = '20260611' AND discovery_id IS NOT NULL
  GROUP BY discovery_id
) v ON r.note_id = v.discovery_id
LEFT JOIN cmt cm ON r.note_id = cm.note_id
ORDER BY r.tier, r.gpm DESC
;