# V8 GPM 漏斗工具规划

## 新 7-Tab 结构（按漏斗顺序）

| Tab | id | 内容 | 来源 |
|---|---|---|---|
| 1 | gpm | 📊 GPM 总览（本周大盘 P50/P75 + 漏斗示意图 + KA vs 休食对比） | 全新 |
| 2 | ctr1 | 👆 提升 CTR1（封面） | 新+方法论 |
| 3 | ctr2 | 🔗 提升 CTR2（商品卡） | 新+方法论 |
| 4 | cvr | 💰 提升 CVR（转化） | 新+方法论 |
| 5 | price | 💎 提升件单价 | 新+方法论 |
| 6 | audit | 🚦 违规预审 | V7 Tab5 迁过来 |
| 7 | tools | 🛠️ 我的内容参考（标题生成等） | V7 Tab4 迁过来 |

## Tab1-5 通用骨架

每个漏斗 Tab（2-5）固定 4 个区块：

1. **本周大盘数字（KPI 卡片）** — 我所在品类 P50/P75 + 我所在的位置
2. **TOP 案例（数据驱动）** — 本周该指标 TOP10 笔记，标题+数据+Claude 亮点解析+跳转
3. **多路径方法论参考** — 从 insight-v20 + creation-guide-v9 提炼的多条路径
4. **行动 checklist** — 商家自检清单

## 数据接入

- 每周一 09:00 cron 跑 fetch_data.py
- 输出 data.json，HTML 启动时 fetch 加载
- data.json 结构：
```json
{
  "updated_at": "2026-06-10",
  "window": ["2026-05-14", "2026-06-09"],
  "p75": {
    "休食": {"图文": {"ctr1_p50": 0.068, "ctr1_p75": 0.10, ...}, "视频": {...}},
    "大健康": {...}, ...,
    "ka_avg": {"图文": {...}, "视频": {...}}
  },
  "top_cases": {
    "ctr1": {
      "图文": [{"note_id": "...", "title": "...", "value": 0.25, "seller_name": "...", "highlight": "封面..."}, ...],
      "视频": [...]
    },
    "ctr2": {...}, "cvr": {...}, "price": {...}
  }
}
```

## 实施步骤

1. ✅ 写 fetch_p75.sql + fetch_data.py 骨架
2. ⏳ 等 subagent 给出 TOP 案例 SQL → 合并到 fetch_data.py
3. ⏳ 写 build_v8_gpm.py 重写 Tab1-5 HTML，Tab6/7 保留
4. ⏳ cron 配置 + 首次跑 + push
5. ⏳ 浏览器截图验收

## 兼容性约束

- 必保留：`.tab-panel { display:block }` + `.tab-panel.hidden { display:none !important }` + `.hidden { display:none !important }`
- push 前必 node --check + style 标签平衡
- 链接不变：https://zhudamen528-code.github.io/xushi-trends/
