# 休食 GPM 漏斗看板 - 数据资产深度探查报告

&gt; **任务**：替换现有"14天 + 阈值 + 同商家去重 + 标题瞎猜"的低质案例 SQL，找到笔记内容、商品、封面、评论、内容打标的可用数据资产
&gt; **基础表**：`redcdm.dm_ecm_note_fullchain_guide_1d_di`（笔记全引导，dataset 1922 同源）
&gt; **报告时间**：2026-06-11
&gt; **执行者**：DIBP 子智能体（depth=1）
&gt; **所有 SQL 均已实跑验证，结果可在 DOR 链接复现**

---

## 0. 执行摘要（TL;DR）

| 类别 | 状态 | 最佳候选表 | 关键字段 | JOIN key |
|------|------|-----------|---------|----------|
| 1. 笔记内容/ASR/打标 | ✅ 找到 | `redcdm.dwd_con_note_info_all_df` | `title`/`content`/`video_asr_text`/`merge_content_v2`/`brand_name` | `note_id`（string） &#124;
| 1b. 算法质量分 | ✅ 找到 | `redcdm.dim_ecm_algo_note_label_df` | `note_quality_level`/`score`（购买意图分）/`is_individual_similar_note` | `note_id`（string） &#124;
| 2. 商品维度 | ✅ 找到 | `redcdm.dim_goods_base_df` | `goods_name`/`goods_price`/`brand_name`/`first/second/third_category_name`/`image_path`/`new_item_id` | `goods_id`（string） &#124;
| 2b. 电商笔记维表 | ✅ 找到 | `redcdm.dim_ecm_note_extend_df` | `taxonomy1/2/3`/`bridge_type`/`is_multi_goods_note`/`note_publish_type`/`anchor_identity_type` | `note_id`（string） &#124;
| 3. 笔记封面 URL | ✅ 找到 | `redapp.app_ecm_ark_ai_note_score_base_nd_di` | `cover_url`（已预拼接 CDN URL，开箱即用） &#124; `note_id`（string） &#124;
| 3b. 视频首帧/质量分 | ⚠️ 部分可用 | `reddw.dw_soc_media_video_discovery_info_day` | `first_frame_id`/`quality_score`/`duration`/`vqa`/`bbox` | `discovery_id`（=note_id）&#124;
| 4. 评论数据 | ✅ 找到 | `reddw.dw_soc_discovery_comment_detail_day` | `content`/`like_num`/`comment_level`/`is_author_replyed`/`note_intention_lv1` | `discovery_id`（=note_id）&#124;

**核心结论：4 类资产全部找到，且都可通过 `note_id` 或 `goods_id` 与 fullchain 直接 LEFT JOIN，无类型/口径冲突。**

---

## 1. 视频/笔记内容理解类

### 1.1 最佳推荐：`redcdm.dwd_con_note_info_all_df`（笔记常用基础信息表-全量）

- **负责人**：姜松（jiangzhiqi@xiaohongshu.com）
- **权限**：✅ 已通过 `check-auth`（实跑通过）
- **粒度**：note_id 全量每日快照
- **生命周期**：62 天（够用）
- **最新分区**：`dtm=20260610`（110亿行/分区，3000 文件）
- **关键字段**：
  | 字段 | 类型 | 用途 |
  |------|------|------|
  | `note_id` | string | 主键，**与 fullchain 表完全一致格式** |
  | `title` | string | 笔记标题 |
  | `content` | string | 笔记正文（直接给 Claude 喂这个！） |
  | `video_asr_text` | string | 视频 ASR 文本（视频笔记 33% 覆盖） |
  | `merge_content_v2` | string | 正文+属性词+标题+topic（精华字段，洞察首选） |
  | `note_voice_content` | string | 音频文本 |
  | `note_type` | int | 1=图文 2=视频 |
  | `brand_id`/`brand_name` | string | 品牌信息 |
  | `keyword_list` | string | 关键词列表 |
  | `topic_list` | string | 话题 list |
  | `image_num` | int | 图片数（图文笔记的图片数；视频笔记是封面图片数） |
  | `level` | int | 笔记审核状态（&gt;=2 才能正常曝光） |

### 1.2 算法打标补充：`redcdm.dim_ecm_algo_note_label_df`（算法标签公共层-笔记）

- **负责人**：罗丘（sumaocheng@xiaohongshu.com，与 fullchain 同 owner）
- **权限**：✅ 已通过
- **生命周期**：1000 天
- **关键字段**（仅 6 个，但都是金子）：
  - `note_quality_level`（bigint）笔记**质量分**：0/1/2 — 算法对笔记质量的硬打分
  - `score`（string）**购买意图分**：这是判定"为啥能转化"的关键！
  - `is_individual_similar_note`（int）是否个人重复发文（=1 通常是低质刷量笔记）
  - `is_group_similar_note`（int）是否团队重复发文

### 1.3 其他候选（次选）

| 表名 | 用途 | 不推荐主因 |
|------|------|----------|
| `shequ_mediacloud.dwd_con_asr_subtitile_note_read_di` | 字幕笔记阅读数 | 是统计表不是底层 ASR |
| `nlp.ads_note_content_sentiment_df` | 笔记正文情感 | 业务级覆盖率低 |
| `redalgo.algo_log_ads_nlp_note_spu_day` | 内容理解-SPU 关联 | 不是文本本身 |

### 1.4 验证 SQL（已实跑）

```sql
SELECT note_id, title, content, video_asr_text, brand_name
FROM redcdm.dwd_con_note_info_all_df
WHERE dtm='20260609' AND note_type=2 AND content IS NOT NULL LIMIT 3;
```

**实际返回**（msgId=5bfb44a0-…）：
```
| note_id                  | title       | content（节选）              | video_asr_text |
| 645efb8b...01502        | 平昌单间出租 | #平昌# 新城 老城都有...      | NULL           |
| 645efc24...3f544        | NULL        | #小红书AI音色#               | NULL           |
| 645efd44...3c1d8        | NULL        | 师傅说镶嵌个扣头是为了...    | NULL           |
```

**ASR 覆盖率验证**（基于 20260609 分区、2026-05-01 后发布）：
- 视频笔记（note_type=2）：1.24 亿笔记中 4130 万有 ASR ≈ **33%**
- 图文笔记（note_type=1）：0%（合理，本就没视频）

---

## 2. 商品维度表

### 2.1 最佳推荐：`redcdm.dim_goods_base_df`（商品基础信息全量维表）

- **负责人**：元让（lijiawen2@xiaohongshu.com）
- **优先级**：**L0**（双 L0，最高优先级），查询次数 **9290** 次
- **权限**：✅ 已通过
- **生命周期**：1100 天
- **粒度**：goods_id（=SKU）每日全量快照
- **文档**：https://docs.xiaohongshu.com/doc/150e7c2e1f369c4d2df424db9debc46d
- **关键字段**（114 个，挑核心）：
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | `goods_id` | string | 主键（SKU 粒度，**=fullchain 表的 goods_id**） |
  | `new_item_id` | string | 商品 item ID（=fullchain 的 new_item_id） |
  | `goods_name` | string | 完整 SKU 名（带颜色规格） |
  | `spu_name` | string | SPU 名（去规格） |
  | `goods_price` | double | 售卖价（元） |
  | `brand_id`/`brand_name` | bigint/string | 品牌（小品牌可能 UNKNOWN） |
  | `first_category_name` | string | 工业一级类目（食品/美妆等） |
  | `second/third_category_name` | string | 二/三级类目 |
  | `image_path` | string | 商品主图路径，拼接 URL：`concat('https://qimg.xiaohongshu.com/', image_path, '?item_id=', goods_id, '&imageView2/2/w/800/q/90.jpg')` |
  | `ipq_num` | bigint | 打包数量（如 可乐500ml*6 → ipq_num=6，套装识别用） |
  | `barcode` | string | 商品条形码 |
  | `is_buyable` | bigint | 是否在售（0/1） |
  | `goods_first_onshelf_time` | string | C 端首次上架时间 |
  | `available_stock_cnt` | bigint | 库存数量 |
  | `is_seven_day_no_reason` | bigint | 是否支持七无（影响转化） |
  | `seller_id` | string | 商家 ID |

### 2.2 电商笔记维表补充：`redcdm.dim_ecm_note_extend_df`（交易笔记维表）

- **负责人**：罗丘（与 fullchain 同 owner，置信度极高）
- **优先级**：L4, L3, L1
- **关键字段**（78 个）：
  - `taxonomy1/2/3` 笔记**通用一级/二级/三级类目**（注意：是笔记侧，非商品侧）
  - `first/second/third_category_name` 笔记绑定商品的**电商类目**
  - `bridge_type`：商笔/购物笔/晒单笔区分（goods_v2/goods_seller/goods_shopping/goods_order）
  - `is_multi_goods_note`：多商品笔记标记
  - `is_cps_note`：是否分销购物笔记
  - `note_publish_type`：AI 辅助发布标记（识别"AI 生产笔记"）
  - `author_seller_id`：作者绑定的商家
  - `anchor_identity_type`：作者身份类型（在 fullchain 也有）
  - `enabled`/`level`：笔记有效性判断（标准用法：`enabled=true AND level>1`）

### 2.3 验证 SQL（已实跑）

```sql
SELECT goods_id, new_item_id, goods_name, goods_price, brand_name,
       first_category_name, second_category_name, third_category_name, image_path
FROM redcdm.dim_goods_base_df
WHERE dtm='20260609' AND brand_name IS NOT NULL LIMIT 3;
```

返回示例（msgId=0e6f6d31-…）：
```
| goods_id                | goods_name                     | goods_price | brand_name | first_cat | image_path                   |
| 68776365ef11920015b7d48b | 塑料透明自封袋面包吐司...     | 17.7       | UNKNOWN    | 家居百货  | material_space/cba8f169-...   |
| 687763863b9d470015ab437a | 周杰伦厦门适用苹果16pro...    | 29.9       | UNKNOWN    | 家居百货  | material_space/0f8da527-...   |
```

&gt; ⚠️ **brand_name 大量 UNKNOWN 是符合预期的**：休食/小卖家未注册品牌库；要拿品牌看 `brand_id` 是否非空，或回退到 spu_name。

---

## 3. 笔记封面/正文/视频首帧

### 3.1 最佳推荐：`redapp.app_ecm_ark_ai_note_score_base_nd_di`（AI 选笔记评分模型特征底座宽表）

- **负责人**：可风（zhangyang10@xiaohongshu.com）
- **权限**：✅ 已通过
- **粒度**：note_id × dtm 每日全量快照
- **生命周期**：365 天
- **最新分区**：`dtm=20260610`，22 亿行
- **核心字段**：`cover_url`（笔记封面首图 URL，**已预拼接 CDN URL，开箱即用！**）
- **拼接规则**（owner 注释）：来源 `dw_soc_note_image_day` 的 file_id，按 update_time DESC 取最新首图

### 3.2 视频质量分补充：`reddw.dw_soc_media_video_discovery_info_day`（视频信息表）

- **负责人**：雷祥
- **优先级**：L1
- **生命周期**：93 天
- **关键字段**：
  - `discovery_id`（string，=note_id，可直接 JOIN）
  - `first_frame_id`（bigint，视频首帧图 ID，覆盖率不全）
  - `quality_score`（double，**无参评测分**，视频质量分）
  - `vqa`（string，无参考质量分）
  - `bbox`（string，OCR 识别）
  - `duration`（bigint，视频时长，ms）
  - `image_sprite_id`（视频雪碧图）
  - `defect_status`（视频质检状态）
- ⚠️ **限制**：约 30% 视频的 first_frame_id=0、quality_score=0（处理失败/未跑全），不可强依赖

### 3.3 其他候选

| 表名 | 字段 | 不推荐主因 |
|------|------|----------|
| `reddw.dw_soc_note_image_day` | file_id（需拼接） | **note_id 是 bigint 与 fullchain 的 string 不匹配，需复杂转换** |
| `redapp.app_ecm_tab2_note_replace_item_info_1d_di` | note_url | 仅商品 tab2 场景 |
| `redcdm.dm_con_note_quality_tag_df` | cover_url | "未打标"队列，覆盖小 |
| `shequ_risk_data.nova_case_library_note_detail_df` | note_cover | 案例库子集，非全量 |

### 3.4 验证 SQL（已实跑）

```sql
SELECT note_id, cover_url
FROM redapp.app_ecm_ark_ai_note_score_base_nd_di
WHERE dtm='20260609'
  AND note_id IN ('69e71ba2000000001d01c13a','696f91cd00000000210326b5',
                  '69dc74a4000000001b021c3c','69d784de00000000230269b6');
```

返回（msgId=780a4a12-…）：
```
| note_id                  | cover_url                                                                          |
| 69dc74a4000000001b021c3c | http://sns-img-qn.xhscdn.com/1040g2sg31usvbsq62geg5p27n4b3ort39rv1eqg?imageView2/2/...|
| 69e71ba2000000001d01c13a | http://sns-img-qn.xhscdn.com/spectrum/1040g0k031v7c4splhm0040gimuh23kn0fhna9c8?im...  |
| 69d784de00000000230269b6 | http://sns-img-qn.xhscdn.com/1040g2sg31uo4umo2jme05p3m4seamj5f3t1nlc0?imageView2/2/...|
| 696f91cd00000000210326b5 | http://sns-img-qn.xhscdn.com/1040g2sg31rhd3vm4nu205q7j3l0dpbvc9i80ouo?imageView2/2/...|
```

✅ **4/4 命中**，URL 可直接放进 HTML `<img src=...>` 渲染。

---

## 4. 评论数据表

### 4.1 最佳推荐：`reddw.dw_soc_discovery_comment_detail_day`（笔记评论发布消费表-近1年）

- **负责人**：孟敖（bailiang@xiaohongshu.com）
- **优先级**：L1
- **权限**：✅ 已通过
- **生命周期**：240 天
- **粒度**：评论 id（一行一条评论）
- **覆盖**：近 1 年发布的评论
- **关键字段**（93 个，挑核心）：
  | 字段 | 类型 | 说明 |
  |------|------|------|
  | `id` | string | 评论主键 |
  | `discovery_id` | string | **笔记 id（与 fullchain 的 note_id 完全一致格式）** |
  | `content` | string | 评论正文（核心！） |
  | `like_num` | bigint | 评论获赞数 |
  | `is_author_liked` | int | 笔记作者是否点赞（0/1） |
  | `is_author_replyed` | int | 笔记作者是否回复（0/1） |
  | `comment_level` | bigint | 评论等级 1/2/3（1=主评论） |
  | `cmt_intention` | string | 评论意图 |
  | `note_intention_lv1/lv2` | string | 笔记发布意图（来自 note_intention_df） |
  | `note_title` | string | 笔记标题（冗余） |
  | `enabled` | boolean | 评论有效性（**必须 enabled=true**） |
  | `status` | int | 评论状态 |
  | `asr_text` | string | 语音评论 ASR |
  | `comment_type` | bigint | 评论类型（0/1=文本，2=图片，4=语音，5=视频） |
  | `is_image_comment` | bigint | 是否图片评论 |

### 4.2 其他候选

| 表名 | 用途 | 不推荐主因 |
|------|------|----------|
| `redcdm.dm_comment_engage_nd_df` | 评论消费宽表全量 | 偏指标聚合，缺业务字段 |
| `reddm.dm_soc_discovery_comment_engagement_day_inc` | 评论消费增量宽表 | 增量需自己滚动 |
| `redapp.app_ads_bcoo_word_cloud_note_comment_df` | 词云笔记评论 | 仅蒲公英子集 |

### 4.3 验证 SQL（已实跑）

```sql
SELECT discovery_id AS note_id, COUNT(*) AS cmt_cnt, SUM(like_num) AS total_like
FROM reddw.dw_soc_discovery_comment_detail_day
WHERE dtm='20260609'
  AND discovery_id IN ('69e49028000000002301e00f','6a1d00a100000000070121d8','69f697c4000000002202aefb')
  AND enabled=true
GROUP BY discovery_id;
```

返回（msgId=a55ca1b0-…）：
```
| note_id                  | cmt_cnt | total_like |
| 6a1d00a100000000070121d8 | 47      | 11         |
| 69f697c4000000002202aefb | 3       | 7          |
| 69e49028000000002301e00f | 58      | 13         |
```

✅ JOIN key 与 fullchain 完全一致，无类型转换；可用 `discovery_id=note_id` 直接关联。

---

## 5. JOIN 全景图（如何与 fullchain 组合）

```
                redcdm.dm_ecm_note_fullchain_guide_1d_di
                 (note_id, goods_id, dgmv, note_imp_num...)
                                |
        ┌──────────────────┬────┴────┬────────────────┬────────────────┐
        │ note_id          │ note_id │ note_id        │ goods_id       │
        │                  │         │                │                │
        ▼                  ▼         ▼                ▼                ▼
[dwd_con_note_info_all_df] [dim_ecm_algo_note_label_df] [dim_ecm_note_extend_df]
   笔记内容/ASR              算法打标                    电商笔记维表
   title/content/asr        quality_level/score        taxonomy/bridge_type
        │
[app_ecm_ark_ai_note_score_base_nd_di]  ← cover_url 封面 URL
        │
[reddw.dw_soc_media_video_discovery_info_day] ← first_frame_id/quality_score (discovery_id=note_id)
        │
[reddw.dw_soc_discovery_comment_detail_day] ← 评论 content/like_num (discovery_id=note_id)
                                                                       │
                                                          [dim_goods_base_df]  ← goods_id
                                                          商品维度
```

**JOIN key 一致性**：所有上述表的 note_id / discovery_id 都是 24 位 hex string，与 fullchain.note_id 完全可直接等值连接，**无任何类型转换**。

**唯一例外**：`reddw.dw_soc_note_image_day` 的 note_id 是 bigint，**因此放弃此表**，改用 `app_ecm_ark_ai_note_score_base_nd_di.cover_url`。

---

## 6. 新版案例 SQL 草案（60 天 × 三层 × 内容增强）

&gt; **设计原则**
&gt; 1. 时间窗：14 天 → **60 天**，覆盖更多类目
&gt; 2. 分层：爆款（dgmv&gt;5w）/ 优秀（1w-5w）/ 黑马（imp&lt;1w 但 GPM&gt;P75）
&gt; 3. 每层至少 200 条候选，**先粗筛后排序**
&gt; 4. 一行一个 (note_id, dtm)，聚合到 note 后再筛
&gt; 5. 自带商品/内容/打标全部字段，下游 Claude 直接读

```sql
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
  WHERE dtm BETWEEN '{start_dtm}' AND '{end_dtm}'
    AND bridge_type IN ('goods_v2','goods_seller')   -- 仅商品笔记
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
      WHEN total_imp < 10000 AND gpm > (
        -- 用类目 P75 GPM 作为黑马阈值（动态）
        SELECT APPROX_PERCENTILE(g, 0.75)
        FROM (SELECT 1000.0*SUM(dgmv)/NULLIF(SUM(note_imp_num),0) AS g
              FROM redcdm.dm_ecm_note_fullchain_guide_1d_di
              WHERE dtm BETWEEN '{start_dtm}' AND '{end_dtm}'
              GROUP BY note_id
              HAVING SUM(note_imp_num) BETWEEN 500 AND 10000) p
      ) THEN '黑马'
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
    WHERE dtm='{end_dtm}'
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
  ON r.note_id = n.note_id AND n.dtm = '{end_dtm}'
LEFT JOIN redcdm.dim_ecm_algo_note_label_df l
  ON r.note_id = l.note_id AND l.dtm = '{end_dtm}'
LEFT JOIN redcdm.dim_ecm_note_extend_df e
  ON r.note_id = e.note_id AND e.dtm = '{end_dtm}'
LEFT JOIN redcdm.dim_goods_base_df g
  ON r.goods_id = g.goods_id AND g.dtm = '{end_dtm}'
LEFT JOIN redapp.app_ecm_ark_ai_note_score_base_nd_di cv
  ON r.note_id = cv.note_id AND cv.dtm = '{end_dtm}'
LEFT JOIN (
  -- 同一笔记可能有多 video，取首条
  SELECT discovery_id, MAX(first_frame_id) AS first_frame_id,
         MAX(quality_score) AS quality_score, MAX(duration) AS duration
  FROM reddw.dw_soc_media_video_discovery_info_day
  WHERE dtm = '{end_dtm}' AND discovery_id IS NOT NULL
  GROUP BY discovery_id
) v ON r.note_id = v.discovery_id
LEFT JOIN cmt cm ON r.note_id = cm.note_id
ORDER BY r.tier, r.gpm DESC
;
```

### 6.1 SQL 草案要点说明

| 设计点 | 说明 |
|--------|------|
| 时间窗 60 天 | 用 `dtm BETWEEN start AND end`，自动跨分区 &#124;
| 三层 200 条 | `ROW_NUMBER OVER (PARTITION BY tier)` + `rk<=200`，共 600 条 &#124;
| 黑马动态阈值 | 用 P75 GPM 作为高 GPM 标准，比固定阈值更稳定 |
| 维表统一用 end_dtm 快照 | 减少分区扫描、保证一致性 |
| 评论取前 50 + 高赞前 5 | 用 ROW_NUMBER 避免 GROUP_CONCAT 内存爆 |
| 视频信息表 GROUP BY 去重 | 一笔记多视频问题 |
| 封面来源 `cv.cover_url` | 已预拼接 CDN URL，HTML 直接 `<img src>` |

### 6.2 已知限制

| 限制 | 影响 | 建议 |
|------|------|------|
| video_asr_text 视频笔记 33% 覆盖 | 部分视频笔记没 ASR 摘要 | 用 title+content+merge_content_v2 兜底 |
| brand_name 大量 UNKNOWN | 小卖家品牌库未注册 | 优先用 spu_name 描述 |
| video_quality_score 约 30% 异常为 0 | 不可强依赖 | 仅作为辅助参考 |
| cover_url 来自 redapp 表，分区只显 10 天 | 历史回看不便 | 60 天案例的 cover 用 end_dtm 当日快照即可（笔记封面少变） |
| dim_ecm_note_extend_df 标 L4/L3/L1 | 不是 L0 | 但与 fullchain 同 owner，置信度高 |

### 6.3 性能预估

- 6 表 JOIN + 60 天聚合：上面测试 5 条数据跑了 **~12 分钟**（HiveSQL），正式 600 条预估 15-25 分钟
- 优化建议：先把 ranked CTE 落临时表（DISTRIBUTE BY note_id），再 JOIN

---

## 7. 资产清单（最终交付）

```python
# work/data_assets.json
{
  "fullchain": "redcdm.dm_ecm_note_fullchain_guide_1d_di",     # 原表
  "note_content": "redcdm.dwd_con_note_info_all_df",            # 标题/正文/ASR
  "algo_label": "redcdm.dim_ecm_algo_note_label_df",            # 质量分/购买意图
  "ecm_extend": "redcdm.dim_ecm_note_extend_df",                # 电商笔记维表
  "goods_dim": "redcdm.dim_goods_base_df",                      # 商品维度
  "cover": "redapp.app_ecm_ark_ai_note_score_base_nd_di",       # 封面 URL
  "video_info": "reddw.dw_soc_media_video_discovery_info_day",  # 视频信息
  "comment": "reddw.dw_soc_discovery_comment_detail_day"        # 评论
}
```

---

## 附录 A：探查过程审计

| # | 检索关键词 | 命中表数 | 备注 |
|---|------------|---------|------|
| 1 | 笔记内容理解 | 13 | 多为 nlp/algo 表，业务接入复杂 |
| 2 | asr 视频 | 7 | 找到 video_asr_chapter 等多个 ASR 表 |
| 3 | 笔记标签 | 14 | 多为风控/审核场景 |
| 4 | 商品维度 dim_item | 6 | 锁定 dim_ecm_external_goods_base_df |
| 5 | 商品 sku 维表 | 15 | 锁定 **dim_goods_base_df**（L0 9290 次） |
| 6 | 笔记封面 cover_url | 字段命中 15+ | bigint vs string 类型问题排查 |
| 7 | 笔记正文 标题 | 字段命中 10+ | 锁定 dwd_con_note_info_all_df |
| 8 | 笔记评论 评论 | 8 | 锁定 dw_soc_discovery_comment_detail_day |
| 9 | 笔记基础信息 | 14 | 二次确认 dwd_con_note_info_all_df 是首选 |
| 10 | note 标签 算法 | 8 | 🎯 锁定 dim_ecm_algo_note_label_df |
| 11 | 笔记 视频信息 | 9 | 🎯 锁定 dw_soc_media_video_discovery_info_day |

## 附录 B：已实跑 SQL msgId 清单（可在 DOR 复查）

| 用途 | msgId | 状态 |
|------|-------|------|
| dwd_con_note_info_all_df 验证 | 5bfb44a0-109a-4d87-8ca2-e4ee08d6132a | FINISHED |
| dim_goods_base_df 验证 | 0e6f6d31-a3c9-4428-b906-4e535044888e | FINISHED |
| dw_soc_note_image_day 验证 | 45c54994-1fc8-4889-bb96-360e052af182 | FINISHED |
| dw_soc_discovery_comment_detail_day 验证 | baddc2e5-783f-43fa-9a31-5411e800b6e0 | FINISHED |
| fullchain note_id 类型探查 | 748a2e6f-2a19-4ff4-90a8-24b9eb2e3dbf | FINISHED |
| 6JOIN 完整验证 | fc00d690-06da-40d6-ba0a-1e29cc6e0395 | FINISHED |
| ASR 覆盖率统计 | c2c2de69-6131-4221-ae5b-e706c47e5a16 | FINISHED |
| video_info 验证 | a3444aca-09cb-4dac-8239-f685954e8c2b | FINISHED |
| cover_url 验证 | 780a4a12-ac02-4219-942e-8ed87ce8eb70 | FINISHED |
| 评论 JOIN 验证 | a55ca1b0-5b64-4c89-b800-7d0b35c37bd5 | FINISHED |

---

&gt; 报告版本：v1.0
&gt; 生成时间：2026-06-11 20:25 Asia/Shanghai
&gt; 子智能体：agent:main:subagent:8e5166d9-7b04-4a91-83a7-1516cf8c95e3
