import json, os
from collections import defaultdict

POOLS = ['ctr1_pic','ctr1_vid','ctr2_pic','ctr2_vid','cvr_pic','cvr_vid','price_pic','price_vid']
POOL_LABEL = {
    'ctr1_pic':'📸 CTR1·图文 (封面+标题强钩子)',
    'ctr1_vid':'🎥 CTR1·视频 (首帧+标题强钩子)',
    'ctr2_pic':'🛒 CTR2·图文 (正文+商品卡强吸引)',
    'ctr2_vid':'🎬 CTR2·视频 (脚本+商品卡强引导)',
    'cvr_pic':'🛍️ CVR·图文 (商品+评论强转化)',
    'cvr_vid':'📦 CVR·视频 (脚本+商品强转化)',
    'price_pic':'💰 件单价·图文 (高客单SKU带高单)',
    'price_vid':'💎 件单价·视频 (高客单SKU带高单)',
}

clusters = {}
for p in POOLS:
    path = f'data/v9_clusters_v3/{p}.cluster.json'
    if os.path.exists(path):
        clusters[p] = json.load(open(path))

# 收集所有方法（带池标签）
all_methods = []
for p in POOLS:
    c = clusters.get(p, {})
    for m in c.get('methods',[]):
        m['_pool'] = p
        m['_pool_label'] = POOL_LABEL[p]
        all_methods.append(m)

# 收集反直觉发现
all_insights = []
for p in POOLS:
    c = clusters.get(p, {})
    for ins in c.get('key_insights',[]):
        all_insights.append({'pool':p,'pool_label':POOL_LABEL[p],'insight':ins})

# 生成 markdown
md = []
md.append('# 🍿 休食商笔 V9 方法论库 · 8池40方法 + 反直觉发现')
md.append('')
md.append('## 📊 池子全景')
md.append('')
md.append('| 池 | 指标维度 | 方法数 | 主导品类 | 平均真诚度 |')
md.append('|---|---|---|---|---|')
for p in POOLS:
    c = clusters.get(p,{})
    methods = c.get('methods',[])
    # 算平均真诚度
    sins = []
    for m in methods:
        ap = m.get('algo_profile',{})
        s = ap.get('sincerity_avg')
        if s is not None: sins.append(float(s))
    avg_sin = round(sum(sins)/len(sins),1) if sins else '—'
    # top 类目
    cat_count = defaultdict(int)
    for m in methods:
        for cat,cnt in m.get('top_categories',[])[:3]:
            cat_count[cat] += cnt
    top_cats = sorted(cat_count.items(), key=lambda x:-x[1])[:3]
    cat_str = ' / '.join([f'{c}({n})' for c,n in top_cats])
    md.append(f'| {POOL_LABEL[p]} | — | {len(methods)} | {cat_str} | {avg_sin} |')
md.append('')
md.append('---')
md.append('')

# 分池详细方法
for p in POOLS:
    c = clusters.get(p,{})
    methods = c.get('methods',[])
    md.append(f'## {POOL_LABEL[p]}')
    md.append('')
    md.append(f'**方法数**：{len(methods)}')
    md.append('')
    md.append('| # | 方法名 | 笔记数 | 真诚度Δ | 主要类目 | 核心做法 |')
    md.append('|---|---|---|---|---|---|')
    for i,m in enumerate(methods,1):
        name = m.get('method_name','—')
        n = m.get('note_count','—')
        ap = m.get('algo_profile',{})
        sin_d = ap.get('sincerity_vs_pool','—') or '—'
        cats = m.get('top_categories',[])[:3]
        cat_str = ' / '.join([f'{c}({n2})' for c,n2 in cats]) or '—'
        summary = m.get('method_summary','—')
        md.append(f'| {i} | {name} | {n} | {sin_d} | {cat_str} | {summary} |')
    md.append('')
    # why_it_works 详情
    md.append('### 📖 方法详情')
    for i,m in enumerate(methods,1):
        name = m.get('method_name','—')
        why = m.get('why_it_works','—')
        cases = m.get('case_notes',[])[:3]
        md.append(f'**{i}. {name}**')
        md.append('')
        md.append(f'> {why}')
        md.append('')
        if cases:
            md.append('代表案例：')
            for cn in cases[:3]:
                title = cn.get('title','—')
                goods = cn.get('goods_name','—')
                gpm = cn.get('gpm','—')
                dgmv = cn.get('dgmv','—')
                md.append(f'- 《{title}》→ {goods} · GPM={gpm} · DGMV=¥{dgmv}')
        md.append('')
    # 反直觉
    insights = c.get('key_insights',[])
    if insights:
        md.append('### 🔁 反直觉发现')
        for ins in insights:
            md.append(f'- {ins}')
        md.append('')
    md.append('---')
    md.append('')

# 跨池强方法
md.append('## 🏆 跨池强方法 Top 5（算法+用户双优）')
md.append('')
md.append('| 排名 | 方法主题 | 出现池 | 估算笔记数 | 核心模式 |')
md.append('|---|---|---|---|---|')
md.append('| 🥇1 | 🌾 老板自白/委屈/真心话 | ctr1_pic + ctr2_pic + ctr2_vid + cvr_pic | 75+ | 第一人称真诚叙事 |')
md.append('| 🥈2 | ⏳ 真稀缺+真原因（季节/限量/补货）| ctr2_pic + price_pic | 45+ | 时间+原因落到具体 |')
md.append('| 🥉3 | 🍵 出处可考·年份山头·工艺溯源 | ctr1_vid + price_vid + ctr1_pic | 50+ | 专业身份+可验证 |')
md.append('| 4 | 🔍 鉴别避坑·真假对比 | ctr1_vid + cvr_vid | 44 | 信任建立+决策辅助 |')
md.append('| 5 | 🩺 痛点直击+解决方案 | cvr_pic + cvr_vid | 36 | 算法压但用户买 |')
md.append('')

# 4 大算法 vs 用户对立
md.append('## ⚡ 4 个"算法 vs 用户"对立方法（短期收割武器）')
md.append('')
md.append('| 方法 | 出现池 | 真诚度Δ | 转化亮点 | 适用场景 |')
md.append('|---|---|---|---|---|')
md.append('| ⏰ 末班车催单 | ctr2_vid | -3.7 | CVR 15.3% 全池最高 | 季节末班/库存清 |')
md.append('| 🌿 症状代入/古法养生 | cvr_vid | -4.7 | CVR Top3 | 药食同源/养生品 |')
md.append('| 💪 痛点食疗 | cvr_pic | -7.7 | CVR 30.9% Top2 | 女性健康/功效品 |')
md.append('| 💗 周期套餐·女性月子 | price_vid | -21.3 | 高客单坚挺 | 月子调理/抗衰套餐 |')
md.append('')
md.append('> 💡 商家含义：这 4 类**算法不爱但用户买**。适合大促/库存清/季节末班车，**不适合做长线人设**——一旦模板化会被持续降权。')
md.append('')

# 总体方法论结论
md.append('## 💡 V9 方法论结构总结')
md.append('')
md.append('### 商家应该建立的"两套武器"')
md.append('')
md.append('| 武器 | 算法友好 | 用户买单 | 用法 |')
md.append('|---|---|---|---|')
md.append('| 长线人设（追算法）| ✅ | ✅ | 老板自白 / 真稀缺 / 出处可考 / 鉴别避坑 |')
md.append('| 短期收割（追用户）| ❌ | ✅ | 末班车 / 痛点食疗 / 症状代入 / 周期套餐 |')
md.append('')
md.append('### 8 大类目"算法最爱"的方法配对')
md.append('')
md.append('- **葡萄酒/洋酒**：老茶有谱型 / 名庄风土 / 工艺品鉴')
md.append('- **燕窝/滋补品**：硬货实拍·规格透明 / 真假鉴别')
md.append('- **药食同源/养生**：症状代入·古法养生（短期）/ 老客证言（长期）')
md.append('- **零食/坚果/卤味**：感官冲击·馋住种草 / 老板自白')
md.append('- **代用茶/花草茶**：吃法搭子·场景植入 / 老茶有谱')
md.append('- **方便速食**：老板自白·真材实料溯源')
md.append('- **礼盒/季节品**：节日+对象+礼盒一句话锁定 / 倒计时·限量稀缺')
md.append('- **米面/谷物**：原料溯源·硬刚同行（短期吸睛）')
md.append('')

md.append('## 🙋‍♂️ 等大门定的事')
md.append('')
md.append('1. **方法名要不要调**？某些方法名"商业感重"（"对手句式"等），可以换更商家友好的')
md.append('2. **王炸名单**？每池选 1 个做完整 5 件套 SOP，建议（按笔记数 × 算法友好度）：')
md.append('   - CTR1 图文 → 🏛 故事工艺·专业讲究（16条/真诚度+7.3）')
md.append('   - CTR1 视频 → 🔍 鉴别避坑+真假对比（25条/双优算法）')
md.append('   - CTR2 图文 → 🌾 老板自白×真材实料溯源（35条/真诚度+5）')
md.append('   - CTR2 视频 → 😭 老板亲自下场委屈体（12条/真诚度+9.3）')
md.append('   - CVR 图文 → 💪 痛点食疗（反直觉冠军，CVR 30.9%）')
md.append('   - CVR 视频 → 🌿 症状代入·古法养生（22条/养生赛道金矿）')
md.append('   - 件单价 图文 → ⏳ 倒计时·限量稀缺（39条/酒类主流）')
md.append('   - 件单价 视频 → 🍵 老茶有谱·年份山头（27条/双优算法）')
md.append('3. **是否要呈现"两套武器"框架**给商家？（建议：要，帮 AM 教学）')
md.append('')

doc = '\n'.join(md)
open('V9_METHODOLOGY_REVIEW.md','w', encoding='utf-8').write(doc)
print('wrote', len(doc), 'chars,', len(md), 'lines')

# REDoc 转义版
out=[]; ic=False
for ln in md:
    if ln.startswith('```'):
        ic=not ic; out.append(ln); continue
    if ic: out.append(ln); continue
    ln=ln.replace('<','&lt;').replace('>','&gt;')
    out.append(ln)
open('V9_METHODOLOGY_REVIEW.redoc.md','w').write('\n'.join(out))
print('redoc wrote', sum(len(l) for l in out))
