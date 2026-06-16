-- V9 Step B: 基于 Step A 1200 note_id 列表，去 JOIN 4 张内容表
-- 占位变量：NOTE_ID_LIST 需脚本注入（CSV 上传后从 Step A 结果生成）
WITH base_notes AS (
  SELECT note_id FROM (VALUES NOTE_ID_LIST AS t(note_id))
)
SELECT
  bn.note_id,
  nc.title,
  SUBSTR(nc.content, 1, 500) AS content_snip,
  SUBSTR(nc.merge_content_v2, 1, 500) AS merge_content_v2,
  SUBSTR(COALESCE(nc.video_asr_text,''), 1, 800) AS asr_snip,
  nc.note_type, nc.image_num, nc.brand_account_name,
  ne.taxonomy1, ne.taxonomy2, ne.taxonomy3, ne.duration, ne.is_multi_goods_note,
  gi.goods_name, gi.goods_price, gi.brand_name, gi.third_category_name AS goods_cat3,
  ca.top_cmts
FROM base_notes bn
LEFT JOIN (
  SELECT note_id, title, content, merge_content_v2, video_asr_text, note_type, image_num, brand_account_name
  FROM redcdm.dwd_con_note_info_all_df WHERE dtm = '20260614'
) nc ON nc.note_id = bn.note_id
LEFT JOIN (
  SELECT note_id, taxonomy1, taxonomy2, taxonomy3, duration, is_multi_goods_note, goods_num
  FROM redcdm.dim_ecm_note_extend_df WHERE dtm = '20260614'
) ne ON ne.note_id = bn.note_id
LEFT JOIN (
  SELECT goods_id, goods_name, goods_price, brand_name, third_category_name
  FROM redcdm.dim_goods_base_df WHERE dtm = '20260614'
) gi ON gi.goods_id = (SELECT goods_id FROM <STEP_A_TEMP_TABLE> WHERE note_id = bn.note_id)
LEFT JOIN (
  SELECT discovery_id AS note_id, CONCAT_WS(' || ', COLLECT_LIST(content)) AS top_cmts
  FROM (
    SELECT discovery_id, content,
      ROW_NUMBER() OVER (PARTITION BY discovery_id ORDER BY like_num DESC) AS rn
    FROM reddw.dw_soc_discovery_comment_detail_day
    WHERE dtm BETWEEN '20260516' AND '20260614'
  ) t WHERE rn <= 5
  GROUP BY discovery_id
) ca ON ca.note_id = bn.note_id
