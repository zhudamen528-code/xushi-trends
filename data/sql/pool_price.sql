-- V9 池：CTR1（图文+视频），60 天，三层分类
-- 输出：每条笔记一行，含全字段
WITH note_agg AS (
  SELECT
    note_id,
    MAX(title)            AS title,
    MAX(seller_id)        AS seller_id,
    MAX(seller_name)      AS seller_name,
    MAX(goods_id)         AS goods_id,
    MAX(publish_time)     AS publish_time,
    MAX(type)             AS note_form_raw,
    SUM(note_imp_num)     AS imp,
    SUM(note_click_num)   AS click,
    SUM(tag_imp_num)      AS tag_imp,
    SUM(tag_click_num)    AS tag_click,
    SUM(buy_num)          AS buy,
    SUM(dgmv)             AS dgmv
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm >= '20260412' AND dtm <= '20260610'
    AND seller_industry = '休食'
    AND type IN ('1','2')
    AND bridge_type IN ('goods_v2','goods_seller')
    AND note_imp_num > 0
  GROUP BY note_id
),
note_metric AS (
  SELECT
    note_id, title, seller_id, seller_name, goods_id, publish_time,
    CASE WHEN note_form_raw='1' THEN 1 ELSE 2 END AS note_form,
    imp, click, tag_imp, tag_click, buy, dgmv,
    1000.0 * dgmv / NULLIF(imp,0) AS gpm,
    click * 1.0 / NULLIF(imp,0)        AS ctr1,
    tag_click * 1.0 / NULLIF(tag_imp,0) AS ctr2,
    buy * 1.0 / NULLIF(tag_click,0)     AS cvr,
    dgmv * 1.0 / NULLIF(buy,0)          AS price_unit
  FROM note_agg
  WHERE imp >= 5000 AND buy >= 10
),
p75_thresh AS (
  SELECT note_form, percentile_approx(price_unit, 0.75) AS p75_price_unit
  FROM note_metric GROUP BY note_form
),
tiered AS (
  SELECT m.*,
    CASE
      WHEN m.gpm >= 500 THEN '爆款'
      WHEN m.gpm >= 200 THEN '优秀'
      WHEN m.gpm < 200 AND m.price_unit > t.p75_price_unit THEN '黑马'
      ELSE NULL
    END AS tier
  FROM note_metric m
  LEFT JOIN p75_thresh t ON m.note_form = t.note_form
),
ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY note_form, tier ORDER BY price_unit DESC) AS rk
  FROM tiered
  WHERE tier IS NOT NULL
),
top_pool AS (
  SELECT * FROM ranked WHERE rk <= 40   -- 每形态每层 40 条 = 240 条候选，去重后预计 200+
),
cmt AS (
  SELECT discovery_id AS note_id,
         COUNT(*) AS cmt_cnt,
         CONCAT_WS(' || ',
           COLLECT_LIST(
             CASE WHEN rk_cmt <= 3 THEN SUBSTR(content,1,80) ELSE NULL END
           )
         ) AS comments_top3
  FROM (
    SELECT discovery_id, content, like_num,
           ROW_NUMBER() OVER (PARTITION BY discovery_id ORDER BY like_num DESC) AS rk_cmt
    FROM reddw.dw_soc_discovery_comment_detail_day
    WHERE dtm = '20260610' AND enabled = true AND status >= 0
  ) c
  WHERE rk_cmt <= 20
  GROUP BY discovery_id
)
SELECT
  r.note_form, r.tier, r.note_id, r.seller_name,
  ROUND(r.ctr1,4) AS ctr1, ROUND(r.ctr2,4) AS ctr2, ROUND(r.cvr,4) AS cvr,
  ROUND(r.price_unit,2) AS price, ROUND(r.gpm,2) AS gpm,
  r.imp, r.tag_click, r.buy, ROUND(r.dgmv,2) AS dgmv,
  -- 内容
  n.title AS n_title,
  SUBSTR(n.content,1,300) AS content_snip,
  CASE WHEN n.video_asr_text IS NOT NULL THEN SUBSTR(n.video_asr_text,1,400) END AS asr_snip,
  -- 算法打标
  l.note_quality_level AS npl_quality_level,
  -- 维表
  e.taxonomy3,
  -- 商品
  g.goods_name, g.goods_price, g.brand_name, g.third_category_name,
  -- 封面
  cv.cover_url,
  -- 评论
  COALESCE(cm.cmt_cnt,0) AS cmt_cnt,
  cm.comments_top3
FROM top_pool r
LEFT JOIN redcdm.dwd_con_note_info_all_df n
  ON r.note_id = n.note_id AND n.dtm = '20260610'
LEFT JOIN redcdm.dim_ecm_algo_note_label_df l
  ON r.note_id = l.note_id AND l.dtm = '20260610'
LEFT JOIN redcdm.dim_ecm_note_extend_df e
  ON r.note_id = e.note_id AND e.dtm = '20260610'
LEFT JOIN redcdm.dim_goods_base_df g
  ON r.goods_id = g.goods_id AND g.dtm = '20260610'
LEFT JOIN redapp.app_ecm_ark_ai_note_score_base_nd_di cv
  ON r.note_id = cv.note_id AND cv.dtm = '20260610'
LEFT JOIN cmt cm ON r.note_id = cm.note_id
ORDER BY r.note_form, r.tier, r.price_unit DESC
