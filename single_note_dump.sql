-- 单条 note_id 在 6 张表的完整数据档案
-- target: 69e3b7060000000021013a5c

-- 1. fullchain 60 天聚合
SELECT '1.fullchain聚合' AS section, * FROM (
  SELECT note_id, seller_name, seller_industry, bridge_type, goods_id,
    SUM(note_imp_num) AS total_imp, SUM(note_click_num) AS total_clk,
    SUM(goods_view_num) AS total_gv, SUM(buy_num) AS total_buy,
    SUM(dgmv) AS total_dgmv,
    1000.0 * SUM(dgmv) / NULLIF(SUM(note_imp_num),0) AS gpm,
    100.0 * SUM(note_click_num) / NULLIF(SUM(note_imp_num),0) AS ctr1_pct
  FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
  WHERE dtm BETWEEN '20260413' AND '20260611'
    AND note_id = '69e3b7060000000021013a5c'
  GROUP BY note_id, seller_name, seller_industry, bridge_type, goods_id
) t

UNION ALL

-- 2. dwd 笔记内容
SELECT '2.dwd_note_info' AS section,
  note_id, title, content, video_asr_text, merge_content_v2,
  brand_name, note_type, publish_time, NULL, NULL, NULL, NULL, NULL, NULL
FROM redcdm.dwd_con_note_info_all_df
WHERE dt = '20260611' AND note_id = '69e3b7060000000021013a5c'

UNION ALL

-- 3. 算法打标
SELECT '3.algo_label' AS section,
  note_id, note_quality_level,
  CAST(score AS STRING),
  CAST(is_individual_similar_note AS STRING),
  NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
FROM redcdm.dim_ecm_algo_note_label_df
WHERE dt = '20260611' AND note_id = '69e3b7060000000021013a5c'
;
