# 任务：对 {pool_name} 池做方法论聚类

## 输入
读取池数据文件：`/home/node/.openclaw/workspace/xushi-trends-cron/work/data/v9_pools_v3/{pool_name}.json`

文件结构：
- pool_name / metric / form / count
- algo_profile（算法画像：sincerity/low_bad/good_click 均值+创作等级分布）
- top10_categories / top10_sellers
- notes[] 100 条笔记，每条含：note_id / seller_name / title / content_snip / asr_snip / goods_name / goods_price / goods_cat3 / total_dgmv / gpm / model_sincerity_score / low_bad_market_score 等

## 任务
从这 100 条笔记里**归纳出 4-5 个方法**（必须从数据出发，禁止预设标签）。

每个方法输出 JSON 格式：
```json
{
  "method_name": "📚 行家开品讲故事型",
  "method_summary": "用专业身份+完整品鉴流程+口感细节描述",
  "algo_profile": {
    "sincerity_avg": 45.2,
    "sincerity_vs_pool": "+9.7 vs 池均",
    "low_bad_avg": 0.85,
    "low_bad_vs_pool": "-0.03 vs 池均（更轻商业感）",
    "creation_level_dominant": "B"
  },
  "note_count": 18,
  "top_categories": [["葡萄酒", 9], ["洋酒", 5], ["威士忌", 2]],
  "case_notes": [
    {"note_id":"...", "title":"...", "goods_name":"...", "goods_price":xx, "gpm":xx, "dgmv":xx},
    ...3-5 个代表
  ],
  "why_it_works": "用商家能听懂的话，2-3 句话，说明：①算法为什么喜欢这类（用 sincerity/low_bad 解释，但不出现这些英文术语），②商家为什么转化好"
}
```

## 强约束
- 数据归纳，禁止预设
- 4-5 个方法必须**有显著差异**（封面/正文/商品/评论任一维度不同）
- 算法画像必须**真实计算**该方法笔记子集的均值（不能猜）
- 笔记不够 5 条的方法不输出
- why_it_works 用商家可读语言，不出现 "sincerity / low_bad_market" 这种英文

## 输出
输出 1 个 JSON 到：`/home/node/.openclaw/workspace/xushi-trends-cron/work/data/v9_clusters_v3/{pool_name}.cluster.json`

格式：
```json
{
  "pool_name": "...",
  "methods": [ ... 4-5 个方法对象 ],
  "key_insights": ["反直觉发现 1", "反直觉发现 2"]
}
```
