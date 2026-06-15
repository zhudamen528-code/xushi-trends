"""
8 池聚类：给每池 60 条笔记，让 Claude 归纳 4-5 个方法
"""
import json, sys

METRIC_DESC = {
    'ctr1': ('封面+标题点击率', '商家自己 100% 可控：封面图、标题文字'),
    'ctr2': ('笔记→商品卡点击率', '看正文叙事是否种草、商品卡何时挂、用户是否被钩到去看商品'),
    'cvr':  ('商品卡→下单转化率', '看商品本身（价/卖点/SKU）、笔记内信任建立、评论区氛围'),
    'price':('件单价', '看商品 SKU 结构、套装/组合策略、价格段定位'),
}
FORM_DESC = {
    'pic': '图文笔记（CTR1 看封面+标题；正文文字承载信息）',
    'vid': '视频笔记（CTR1 看封面+前 3 秒+标题；ASR 文本承载脚本节奏）',
}

def build_prompt(pool_key, items):
    metric_key = pool_key.split('_')[0]
    form_key = pool_key.split('_')[1]
    metric_name, metric_what = METRIC_DESC[metric_key]
    form_name = FORM_DESC[form_key]
    
    lines = [f"# 任务：归纳「休食 · {form_name} · {metric_name}」的内容方法\n"]
    lines.append(f"## 背景")
    lines.append(f"- 你拿到 {len(items)} 条休食类目下「{metric_name}」表现优秀的笔记")
    lines.append(f"- 该指标核心是看：{metric_what}")
    lines.append(f"- 数据来源：近 60 天 fullchain，按该指标降序排序")
    lines.append("")
    lines.append("## 你的任务")
    lines.append(f"1. 把这 {len(items)} 条笔记按「内容方法」聚类（不是按品类/品牌聚）")
    lines.append("2. 归纳出 **4-5 个独立的方法**（必须有显著差异，不能重复）")
    lines.append("3. 每个方法必须包含：")
    lines.append("   - `method_name`: 12 字内方法名（emoji 开头）")
    lines.append("   - `essence`: 30 字内核心定义（这个方法是什么）")
    lines.append("   - `why_works`: 50 字内为什么这个方法能拉高该指标（数据驱动归纳，不是套路话）")
    lines.append("   - `signals`: 3-5 条可执行的内容信号（如\"封面用 X 元素\"\"标题含 Y 句式\"\"商品卡挂 Z 数量\"），具体可抄")
    lines.append("   - `applicable_category`: 适合品类清单（基于这批笔记的真实商品类目分布给）")
    lines.append("   - `note_ids`: 归到该方法的笔记 ID 列表（≥5 条，按指标排序）")
    lines.append("4. 最后给出 `cluster_rationale`: 100 字内说\"为什么这样聚类，依据是什么\"")
    lines.append("")
    lines.append("## 输出格式")
    lines.append("严格 JSON：")
    lines.append("```json")
    lines.append("{")
    lines.append('  "methods": [')
    lines.append('    {"method_name": "...", "essence": "...", "why_works": "...", "signals": ["...","..."], "applicable_category": ["..."], "note_ids": ["...","..."]}')
    lines.append("  ],")
    lines.append('  "cluster_rationale": "..."')
    lines.append("}")
    lines.append("```")
    lines.append("")
    lines.append("## 红线")
    lines.append("- 不许编标题/亮点：所有方法依据必须能从下面笔记里找到证据")
    lines.append("- 不许预设方法（不要套\"封面钩子/数字反差/痛点共鸣\"这种现成标签）")
    lines.append("- 必须从数据归纳：先看完 60 条找规律，再定方法名")
    lines.append("- 至少 1 个方法要包含\"反直觉发现\"（如某种商品类型的特殊玩法）")
    lines.append("- 视频池要关注 ASR 文本里的开头话术/节奏；图文池要关注正文段落结构")
    lines.append("")
    lines.append(f"## 候选笔记池（{len(items)} 条）")
    lines.append("")
    
    for i, x in enumerate(items, 1):
        lines.append(f"### [{i}] note_id={x['note_id']} | gpm={x['gpm']} | {metric_name}={x.get(metric_key+'_pct') or x.get('price_yuan')}{'%' if metric_key!='price' else '元'} | imp={x['imp']}")
        lines.append(f"- 商家: {x['seller']} | 商品: {x['goods_name']} | 价格: ¥{x['goods_price']} | 品类3: {x.get('goods_cat3','')}")
        lines.append(f"- 标题: {x['title']}")
        if x.get('content'):
            lines.append(f"- 正文(前200): {x['content'][:200]}")
        if x.get('asr'):
            lines.append(f"- ASR(前300): {x['asr'][:300]}")
        if x.get('top_cmts'):
            lines.append(f"- Top评论: {x['top_cmts'][:200]}")
        lines.append("")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    pool_key = sys.argv[1]
    items = json.load(open(f'data/v9_pools/{pool_key}.json'))
    prompt = build_prompt(pool_key, items)
    open(f'data/v9_clusters/{pool_key}.prompt.md','w').write(prompt)
    print(f'{pool_key}: prompt {len(prompt)} chars, {len(items)} items')
