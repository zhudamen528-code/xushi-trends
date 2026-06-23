#!/usr/bin/env python3
"""V10 build：在 V8 funnel_tab 框架不动的前提下，把 4 指标 Tab 内部的方法卡换成 V10 高低对照差分聚类结果。

策略：
- 保留 V8/V9 的 funnel_tab 外壳（hero + 行业参考值 + 卖点助手 等）
- 保留 V9 的"图文/视频路径方法卡"作为多样化参考（subagent 已聚类的 40 方法）
- 新增 V10 核心模块：每个 Tab 顶部加"🔍 高 vs 低对照差分聚类"，包含：
  - 高组独有写法簇（绿卡）：簇名 / 高 N vs 低 N / 差距 pp / 类目 / 信心 / 案例 / 反例 / 商家建议
  - 低组陷阱簇（红卡）：陷阱名 / 命中数 / 类目 / 案例 / 避坑建议
  - 核心机制总结（金句）
"""
import json, os, re, sys, importlib.util

WORKDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKDIR)

# 加载 V10 差分聚类结果（ctr1/ctr2/cvr 跑差分；price 改固定 playbook）
V10_DIFF = {}
for m in ['ctr1', 'ctr2', 'cvr']:
    V10_DIFF[m] = json.load(open(os.path.join(WORKDIR, f'data/v10_clusters/{m}.diff.json'), encoding='utf-8'))

# 件单价不做差分聚类（笔记内容只能影响临门一脚，影响因子太多控不住）
# 改成固定 4 机制运营手册
V10_PRICE_PLAYBOOK = json.load(open(os.path.join(WORKDIR, 'data/v10_price_playbook.json'), encoding='utf-8'))

# 指标与算法 feature 相关性（皮尔逊）
V10_METRIC_CORR = json.load(open(os.path.join(WORKDIR, 'data/v10_metric_algo_corr.json'), encoding='utf-8'))

# 加载 title → note_id 索引（用于案例跳转）
TITLE_IDX = {}
try:
    TITLE_IDX = json.load(open(os.path.join(WORKDIR, 'data/v10_clusters/title_to_noteid.json'), encoding='utf-8'))
except FileNotFoundError:
    print('⚠️ title_to_noteid.json 不存在，案例无跳转链')

def _norm(s): return re.sub(r'[\s\u3000【】「」\[\]<>《》（）()]+','', s or '')
NORM_IDX = {_norm(k): v for k, v in TITLE_IDX.items() if len(_norm(k)) >= 6}

def _example_candidates(ex):
    s = ex.strip()
    s = re.sub(r'^[\[【][^\]】]+[\]】]\s*', '', s)
    cands = [s]
    m = re.match(r'^《([^》]+)》', s)
    if m: cands.append(m.group(1).strip())
    for seg in re.split(r'[|｜]', s):
        seg = seg.strip()
        if len(seg) >= 4: cands.append(seg)
    out = []
    for c in cands:
        out.append(c)
        for L in [25,20,15,12,10,8]:
            out.append(c[:L])
    return out

def lookup_note_id(ex):
    for c in _example_candidates(ex):
        if c in TITLE_IDX: return TITLE_IDX[c]
        nc = _norm(c)
        if nc in NORM_IDX: return NORM_IDX[nc]
    return None

def example_li(ex):
    nid = lookup_note_id(ex)
    text = escape(ex)
    if nid:
        # 小红书笔记跳转链
        return f'<li><a href="https://www.xiaohongshu.com/explore/{escape(nid)}" target="_blank" rel="noopener" class="v10-note-link">🔗 {text}</a></li>'
    return f'<li>{text}</li>'

# ============ HTML 工具 ============
def escape(s):
    if s is None: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def confidence_badge(c):
    if not c: return ''
    color = {'高': 'cb-high', '中': 'cb-mid', '低': 'cb-low'}.get(c, 'cb-mid')
    label = {'高': '证据强', '中': '证据中', '低': '证据弱'}.get(c, '证据中')
    tooltip = {'高': '差距大 + 跨多个类目 + 样本量足', '中': '差距中等或样本偏小，可参考但需结合自身判断', '低': '可能是品类特性或样本噪声，仅供参考'}.get(c, '')
    return f'<abbr class="conf-badge {color}" title="{tooltip}">{label}</abbr>'


def pick_balanced_examples(examples, max_per_cat=2, max_total=4):
    """类目均衡选案例，优先确保 零食/速食/茶酒/滋补 4 大组都有覆盖
    
    examples 元素结构（来自 subagent）：
      "[养生食疗] 标题文字"  或  dict {category, title, ...}
    """
    if not examples:
        return []
    # 提取类目和原始项
    items = []
    for e in examples:
        if isinstance(e, str):
            # 从 "[类目] 标题" 提取
            m = re.match(r'^\[([^\]]+)\]', e)
            cat = m.group(1) if m else '其他'
            items.append((cat, e))
        elif isinstance(e, dict):
            cat = e.get('category') or e.get('cat') or '其他'
            items.append((cat, e))
        else:
            items.append(('其他', e))
    
    # 类目桶
    buckets = {}
    for cat, item in items:
        buckets.setdefault(cat, []).append(item)
    
    # 优先级：零食组 > 速食/咖啡组 > 滋补组 > 茶酒组 > 其他
    PRI = {
        '美食测评': 1, '美食展示': 1, '美食教程': 1, '美食其他': 1,
        '坚果': 1, '糕点': 1, '肉干': 1, '速食': 1,
        '科学科普': 2,
        '养生食疗': 3, '滋补': 3, '药食同源': 3,
        '花草茶': 4, '葡萄酒': 4, '洋酒': 4, '酒类': 4,
    }
    cats_sorted = sorted(buckets.keys(), key=lambda c: (PRI.get(c, 5), -len(buckets[c])))
    
    # 轮询取，每类目最多 max_per_cat
    picked = []
    idx_per_cat = {c: 0 for c in cats_sorted}
    while len(picked) < max_total:
        before = len(picked)
        for cat in cats_sorted:
            if len(picked) >= max_total: break
            i = idx_per_cat[cat]
            if i < min(max_per_cat, len(buckets[cat])):
                picked.append(buckets[cat][i])
                idx_per_cat[cat] = i + 1
        if len(picked) == before:
            break  # 没新加 = 全用完
    return picked

def render_high_card(p, idx):
    name = escape(p.get('cluster_name', '?'))
    high_n = p.get('high_n', '?')
    low_n = p.get('low_n', '?')
    diff = p.get('diff_pp', '')
    ratio = p.get('ratio', '')
    cat = escape(p.get('category_dist', '—'))
    conf = p.get('confidence', '中')
    advice = escape(p.get('merchant_advice', '—'))
    
    diff_str = ''
    if diff: diff_str = f'<span class="diff-pp">表现好的多 {diff}%</span>'
    if ratio and ratio != diff_str:
        diff_str += f' <span class="diff-ratio">{escape(ratio)}</span>'
    
    examples = p.get('high_examples', [])
    # 砍掉"反例案例"：商家工具不展示低组具体笔记（容易踩到自己/同行笔记，徒增尴尬）
    
    # 类目均衡选案例：每类目最多 2 条，零食/速食/茶酒/滋补尽量都有
    examples = pick_balanced_examples(examples, max_per_cat=2, max_total=4)
    ex_html = ''.join(example_li(e) for e in examples)
    
    return f'''<div class="v10-card v10-card-high">
  <div class="v10-card-head">
    <span class="v10-card-num">{idx+1}</span>
    <span class="v10-card-name">{name}</span>
    {confidence_badge(conf)}
  </div>
  <div class="v10-card-stat-row">
    <span class="v10-stat-good">✅ 表现好 <b>{high_n}</b> 篇</span>
    <span class="v10-stat-sep">vs</span>
    <span class="v10-stat-bad">表现差仅 <b>{low_n}</b> 篇</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 {cat}</div>
  <div class="v10-card-advice">💡 {advice}</div>
  <details class="v10-card-examples">
    <summary>看 {len(examples)} 篇真实案例</summary>
    <div class="v10-ex-block">
      <div class="v10-ex-label">🟢 表现好的笔记是这么写的</div>
      <ul class="v10-ex-list">{ex_html}</ul>
    </div>
  </details>
</div>'''

def render_low_card(p, idx):
    name = escape(p.get('cluster_name', '?'))
    high_n = p.get('high_n', '?')
    low_n = p.get('low_n', '?')
    diff = p.get('diff_pp', '')
    ratio = p.get('ratio', '')
    cat = escape(p.get('category_dist', '—'))
    conf = p.get('confidence', '中')
    advice = escape(p.get('merchant_advice', '—'))
    
    diff_str = ''
    if diff: diff_str = f'<span class="diff-pp diff-pp-red">表现差的多 {abs(diff) if isinstance(diff, (int, float)) else diff}%</span>'
    if ratio: diff_str += f' <span class="diff-ratio">{escape(ratio)}</span>'
    
    # 陷阱卡：完全不展示具体笔记案例（不点名任何商家），只展示写法描述
    return f'''<div class="v10-card v10-card-low">
  <div class="v10-card-head">
    <span class="v10-card-num v10-card-num-red">{idx+1}</span>
    <span class="v10-card-name">{name}</span>
    {confidence_badge(conf)}
  </div>
  <div class="v10-card-stat-row">
    <span class="v10-stat-bad">🔴 表现差 <b>{low_n}</b> 篇踩坑</span>
    <span class="v10-stat-sep">vs</span>
    <span class="v10-stat-good">表现好仅 <b>{high_n}</b> 篇</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 {cat}</div>
  <div class="v10-card-advice v10-card-advice-red">🚫 {advice}</div>
</div>'''

def render_price_playbook():
    """件单价 Tab 改：4 大拉升机制固定运营手册（不做差分聚类）"""
    mechs = V10_PRICE_PLAYBOOK.get('mechanisms', {})
    cards = []
    for mk, m in mechs.items():
        cases_html = ''
        for c in m['cases']:
            nid = c['note_id']
            tax = escape(c.get('taxonomy','?'))
            buy = c['buy_n']
            ppi = c['ppi']
            title = escape(c['title'][:38])
            kws = '·'.join(c['hit_kws'][:2])
            cases_html += f'''<li><a href="https://www.xiaohongshu.com/explore/{escape(nid)}" target="_blank" rel="noopener" class="v10-note-link">🔗 [{tax}] {title}</a> <span class="case-meta">件数 {buy} · 件单价 ¥{ppi} · 关键词「{escape(kws)}」</span></li>'''
        if not cases_html:
            cases_html = '<li class="case-empty">本周池里暂无对应案例</li>'
        
        cards.append(f'''<div class="price-mech-card">
  <div class="price-mech-head">
    <span class="price-mech-name">{escape(m['name'])}</span>
  </div>
  <div class="price-mech-desc">{escape(m['desc'])}</div>
  <div class="price-mech-sop">💡 <b>怎么做</b>：{escape(m['sop'])}</div>
  <div class="price-mech-pitfall">⚠️ <b>避坑</b>：{escape(m['pitfall'])}</div>
  <details class="price-mech-cases">
    <summary>📌 本周池里命中的真实案例（{len(m['cases'])}）</summary>
    <ul class="v10-ex-list">{cases_html}</ul>
  </details>
</div>''')
    
    return f'''<div class="v10-section price-playbook-section">
  <div class="v10-banner price-banner">
    <div class="v10-banner-title">💎 件单价怎么拉？· 4 个能直接抄的玩法</div>
    <div class="v10-banner-sub">件单价受商品定价、促销、库存、人群消费力影响，<b>笔记内容能改的是"临门一脚的引导"</b>。这里给 4 个能直接抄的玩法，配本周真实案例。</div>
  </div>
  
  <div class="v10-mechanism v10-mech-hero">
    💎 <b>关键心智</b>：件单价 = 商品标价 × 平均买几件。商品标价改不了，但<b>平均买几件</b>可以通过笔记话术拉高（凑单 / 赠品 / 囤货 / 任选）。
  </div>
  
  <div class="price-mech-grid">{''.join(cards)}</div>
</div>'''


def render_metric_algo_corr_table():
    """Tab1 GMV 公式旁渲染：算法分 Q1→Q4 商业产出阶梯（不是皮尔逊拟合，是真实 DGMV/曝光 中位数）"""
    # 阶梯数据（从分箱算的，不是 pearson 拟合）
    # ⚠️ 注：'好点击留人' 行（dgmv 0.5x）已删除，因为它会误导商家："留人率高=GMV 低=别让用户停留" 是错误推论。
    # 真相：留人率高的多是干货/科普长文，用户读完后去其他渠道下单，DGMV 只算小红书原地成交。这是衡量口径偏差，不是策略指南。
    ladder = [
        {'feat': '真诚分享',   'q1_dgmv': 1138,  'q4_dgmv': 3014,  'dgmv_x': 2.6,  'imp_x': 2.4,  'positive': True},
        {'feat': '营销味淡',   'q1_dgmv': 1335,  'q4_dgmv': 3679,  'dgmv_x': 2.8,  'imp_x': 2.4,  'positive': True},
        {'feat': '平台综合打分', 'q1_dgmv': 1503,  'q4_dgmv': 3474,  'dgmv_x': 2.3,  'imp_x': 2.2,  'positive': True},
        {'feat': '内容质量分',   'q1_dgmv': 702,   'q4_dgmv': 13110, 'dgmv_x': 18.7, 'imp_x': 170,  'positive': True, 'star': True},
    ]
    rows = []
    for r in ladder:
        cls = 'ladder-pos' if r['positive'] else 'ladder-neg'
        star = ' 🔥' if r.get('star') else ''
        warn = '<span class="ladder-warn">⚠️ 反例</span>' if not r['positive'] else ''
        dgmv_x_str = f'<b class="ladder-x">{r["dgmv_x"]}x</b>' if r['positive'] else f'<b class="ladder-x-neg">{r["dgmv_x"]}x</b>'
        imp_x_str = f'{r["imp_x"]}x' if r['imp_x'] < 100 else f'<b>{r["imp_x"]}x</b>'
        rows.append(f'''<tr class="{cls}">
  <td class="ladder-feat">{escape(r["feat"])}{star}</td>
  <td class="ladder-q1">¥{r["q1_dgmv"]:,}</td>
  <td class="ladder-q4">¥{r["q4_dgmv"]:,}</td>
  <td class="ladder-mult">{dgmv_x_str}</td>
  <td class="ladder-mult">{imp_x_str}</td>
  <td>{warn}</td>
</tr>''')
    
    return f'''<div class="metric-algo-corr">
  <div class="mac-title">🤖 平台给你的分 × 实际销售额 真实对比（n=1199 篇笔记）</div>
  <div class="mac-sub">把池里 1199 篇笔记<b>按算法打分从低到高排队</b>，分成 4 段，看每段笔记<b>典型 DGMV 和曝光</b>是多少。<b>这是实测产出，不是统计模型</b>。</div>
  <table class="mac-table mac-ladder">
    <thead><tr>
      <th>平台打分维度</th>
      <th><abbr title="把所有笔记按算法分从高到低排队，分数最低的 25%">评分垫底 25%</abbr><br><span class="mac-th-sub">这批笔记典型销售额</span></th>
      <th><abbr title="把所有笔记按算法分从高到低排队，分数最高的 25%">评分领先 25%</abbr><br><span class="mac-th-sub">这批笔记典型销售额</span></th>
      <th>多卖多少倍</th>
      <th>多拿多少倍曝光</th>
      <th></th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="mac-key">💎 <b>关键洞察</b>：算法分高的笔记 DGMV 是算法分低的 <b>2-19 倍</b>，曝光最多大 <b>170 倍</b>。重点追"<b>内容质量分 / 真诚分享 / 营销味淡 / 平台综合打分</b>"这 4 个分。</div>
  <div class="mac-warn">📌 注：这是把 1199 篇笔记按平台打分排队分 4 段，看销售额和曝光的真实差距，不是统计模型。分数由平台计算，商家不能直接改，但能通过"内容写法"间接影响——具体见下面 4 个指标 Tab。</div>
</div>'''

CTR2_PRIORITY_NOTE = '''<div class="ctr2-priority-note">
  <div class="cpn-title">📐 CTR2 三层优先级 · 字数本身不是因，「信息密度」才是</div>
  <div class="cpn-tier cpn-tier-1"><b>🔴 首要 · 商品卡里的商品名做减法</b>（差距最大 +14.5 个百分点）<br>≤ 25 字内只放「品类 + 1 个硬指标」。例：✅「韩要强夏威夷果 250g 中大半粒」/ ❌「韩要强 0号特大现烤夏威夷果仁没有额外添加剂250克 1罐*250克【中大半粒】」</div>
  <div class="cpn-tier cpn-tier-2"><b>🟡 次要 · 笔记正文前 200 字做减法</b>（< 100 字 +14.5 个百分点）<br>一句卖点 + 一句证据，不要把商详顶部写成产品说明书。</div>
  <div class="cpn-tier cpn-tier-3"><b>🟢 辅助 · 笔记标题做减法</b>（≤ 15 字 +8.3 个百分点）<br>≤ 15 字 + 规格量化数字，让用户在信息流 0.5 秒看懂「是什么 + 多少」。</div>
  <div class="cpn-key">💡 <b>判断依据</b>：不是死磕字数，是看「单位字数的信息密度」——25 字商品名讲清 1 件事 > 50 字商品名塞 7 件事每件都没讲透。</div>
</div>'''

def render_v10_section(metric_key, metric_label):
    diff = V10_DIFF.get(metric_key, {})
    high_patterns = diff.get('high_only_patterns', [])
    low_patterns = diff.get('low_only_patterns', [])
    mechanism = diff.get('key_mechanism', '')
    
    high_html = ''.join(render_high_card(p, i) for i, p in enumerate(high_patterns))
    low_html = ''.join(render_low_card(p, i) for i, p in enumerate(low_patterns))
    
    # CTR2 加三层优先级前置说明
    ctr2_priority = CTR2_PRIORITY_NOTE if metric_key == 'ctr2' else ''
    
    return f'''<div class="v10-section">
  <div class="v10-banner">
    <div class="v10-banner-title">🔬 {escape(metric_label)} 高低对照 · 学好的，避坑的</div>
    <div class="v10-banner-sub">把同类目里"<b>{escape(metric_label)} 排前 25%</b>"和"<b>排后 25%</b>"的笔记拉出来比，找出"好笔记常用、坏笔记踩坑"的写法。<b>这是从已发笔记里归纳的规律，是参考不是保证</b>。</div>
  </div>
  
  {f'<div class="v10-mechanism v10-mech-hero">💎 <b>核心规律</b>：{escape(mechanism)}</div>' if mechanism else ''}
  
  {ctr2_priority}
  
  <div class="v10-subhead v10-subhead-green">✅ 表现好的笔记常用的 {len(high_patterns)} 招 → 抄</div>
  <div class="v10-cards-grid">{high_html}</div>
  
  <div class="v10-subhead v10-subhead-red">🚫 表现差的笔记常踩的 {len(low_patterns)} 个坑 → 避</div>
  <div class="v10-cards-grid">{low_html}</div>
</div>'''

# ============ V10 CSS ============
V10_CSS = '''
/* ============ V10.2 Design Tokens（4 色系统）============ */
:root {
  /* 主色 4 个：深=结论 / 黄=提示 / 绿=可抄 / 红=避坑 */
  --c-deep: #1f2937;       /* 深色（标题/结论 hero）*/
  --c-deep-2: #374151;     /* 深色辅助 */
  --c-deep-3: #6b7280;     /* 深色中度（次要文本）*/
  --c-warn: #f59e0b;       /* 黄色（重要提示/平台心智）*/
  --c-warn-bg: #fffbeb;    /* 黄色背景 */
  --c-warn-bg-2: #fef3c7;  /* 黄色背景加深 */
  --c-good: #10b981;       /* 绿色（可抄/正面）*/
  --c-good-bg: #ecfdf5;    /* 绿色背景 */
  --c-good-bg-2: #d1fae5;  /* 绿色背景加深 */
  --c-bad: #ef4444;        /* 红色（避坑/反例）*/
  --c-bad-bg: #fef2f2;     /* 红色背景 */
  --c-bad-bg-2: #fee2e2;   /* 红色背景加深 */
  /* 中性灰阶 */
  --c-text: #111827;       /* 主文本 */
  --c-text-2: #374151;     /* 次要文本 */
  --c-text-3: #6b7280;     /* 弱化文本 */
  --c-text-4: #9ca3af;     /* 极弱文本/标签 */
  --c-bg: #ffffff;         /* 背景 */
  --c-bg-2: #f9fafb;       /* 卡片背景 */
  --c-bg-3: #f3f4f6;       /* 区块背景 */
  --c-border: #e5e7eb;     /* 边框 */
  --c-border-strong: #d1d5db; /* 强边框 */
  /* 字号 5 级 */
  --fs-xs: 11px;
  --fs-sm: 12px;
  --fs-base: 14px;
  --fs-md: 16px;
  --fs-lg: 20px;
  --fs-xl: 28px;
  /* 间距 4 级 */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 14px;
  --sp-4: 20px;
  --sp-5: 28px;
  /* 圆角 */
  --r-sm: 6px;
  --r: 10px;
  --r-lg: 14px;
}
/* 全站轻量重置 */
body { color: var(--c-text); }

.v10-section { margin: 20px 0; }
.v10-banner { background: linear-gradient(135deg, var(--c-warn-bg), var(--c-warn-bg-2)); border-left: 4px solid var(--c-warn); border-radius: 10px; padding: 14px 18px; margin-bottom: 18px; }
.v10-banner-title { font-size: 16px; font-weight: 700; color: var(--c-text); margin-bottom: 6px; }
.v10-banner-sub { font-size: 12px; color: var(--c-text-3); line-height: 1.6; }
.v10-mechanism { background: #f4f8ff; border-left: 3px solid var(--c-deep); border-radius: 6px; padding: 12px 16px; margin: 14px 0; font-size: 13px; color: var(--c-text); line-height: 1.7; }
/* 核心机制 hero 样式：深色背景、大字、高亮 */
.v10-mech-hero { background: linear-gradient(135deg, var(--c-deep) 0%, var(--c-deep-2) 100%) !important; color: #fff !important; border-left: 4px solid var(--c-warn) !important; padding: 16px 20px !important; font-size: 15px !important; line-height: 1.8 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin: 16px 0 20px !important; border-radius: 8px !important; }
.v10-mech-hero b { color: var(--c-warn) !important; font-size: 16px; }

/* CTR2 三层优先级前置说明 */
.ctr2-priority-note { background: #fff; border: 1px solid #e8eaed; border-radius: 10px; padding: 16px 18px; margin: 14px 0 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.cpn-title { font-size: 14px; font-weight: 700; color: #d92f5e; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #f0d4dd; }
.cpn-tier { padding: 8px 12px; margin: 6px 0; border-radius: 6px; font-size: 12px; line-height: 1.7; color: var(--c-text); }
.cpn-tier-1 { background: #fff0f0; border-left: 3px solid #d92f5e; }
.cpn-tier-2 { background: #fffaeb; border-left: 3px solid var(--c-warn); }
.cpn-tier-3 { background: #f0fff4; border-left: 3px solid var(--c-good); }
.cpn-tier b { color: var(--c-deep); font-size: 13px; }
.cpn-key { background: var(--c-deep); color: #fff; border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 12px; line-height: 1.7; }
.cpn-key b { color: var(--c-warn); }

/* 指标↔算法相关性表（已移除，CSS 保留备用）*/

/* V9 老内容折叠样式 */
.v9-legacy-fold { background: #fafbfc; border: 1px solid #e5e7eb; border-radius: 10px; margin: 24px 0 16px; padding: 0; }
.v9-legacy-summary { cursor: pointer; padding: 14px 18px; font-size: 13px; font-weight: 600; color: var(--c-text-3); list-style: none; display: flex; align-items: center; gap: 8px; user-select: none; }
.v9-legacy-summary::-webkit-details-marker { display: none; }
.v9-legacy-summary::before { content: '▶'; transition: transform 0.2s; color: var(--c-text-4); font-size: 10px; }
.v9-legacy-fold[open] .v9-legacy-summary::before { transform: rotate(90deg); }
.v9-legacy-summary:hover { color: #d92f5e; }
.v9-legacy-body { padding: 16px 18px 4px; border-top: 1px solid var(--c-border); }

/* 业务术语 hover：自实现 tooltip，桌面 hover + 移动 tap 都支持 */
.term-abbr { 
  text-decoration: none; 
  border-bottom: 1px dotted var(--c-text-4); 
  cursor: help; 
  position: relative;
  background: var(--c-warn-bg);
  padding: 0 2px;
  border-radius: 3px;
}
.term-abbr:hover, .term-abbr.tip-open { background: var(--c-warn-bg-2); }
.term-abbr::after {
  content: attr(data-tip);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%) translateY(4px);
  background: var(--c-deep);
  color: #fff;
  font-size: var(--fs-xs);
  font-weight: 400;
  line-height: 1.6;
  padding: 8px 12px;
  border-radius: 6px;
  white-space: normal;
  width: max-content;
  max-width: 240px;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.15s, transform 0.15s, visibility 0.15s;
  z-index: 999;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  text-align: left;
}
.term-abbr::before {
  content: '';
  position: absolute;
  bottom: calc(100% + 0px);
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: var(--c-deep);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.15s, visibility 0.15s;
  pointer-events: none;
  z-index: 999;
}
.term-abbr:hover::after, .term-abbr:hover::before,
.term-abbr.tip-open::after, .term-abbr.tip-open::before {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}
.term-abbr:hover::before, .term-abbr.tip-open::before {
  transform: translateX(-50%);
}
@media (max-width: 640px) {
  .term-abbr::after { max-width: 220px; font-size: 11px; }
}
.mac-th-sub { display: block; font-size: 10px; color: var(--c-text-3); font-weight: 400; margin-top: 2px; }
abbr.conf-badge { text-decoration: none; cursor: help; }

/* ============ V10.2 UI 大改：卡片紧凑 + 双栏对比 + sticky 锚 ============ */
.v10-card { transition: box-shadow 0.15s; }
.v10-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.v10-card-head { display: flex; align-items: center; gap: 8px; margin-bottom: var(--sp-2); flex-wrap: wrap; }
.v10-card-num { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: var(--c-good); color: #fff; font-size: var(--fs-xs); font-weight: 700; flex-shrink: 0; }
.v10-card-num-red { background: var(--c-bad); }
.v10-card-name { font-size: var(--fs-base); font-weight: 700; color: var(--c-text); flex: 1; line-height: 1.4; min-width: 200px; }
.v10-card-stat-row { display: flex; align-items: center; gap: 8px; margin-bottom: var(--sp-2); font-size: var(--fs-sm); color: var(--c-text-3); flex-wrap: wrap; }
.v10-stat-good { color: var(--c-good); }
.v10-stat-good b { color: var(--c-good); font-size: var(--fs-base); }
.v10-stat-bad { color: var(--c-bad); }
.v10-stat-bad b { color: var(--c-bad); font-size: var(--fs-base); }
.v10-stat-sep { color: var(--c-text-4); font-size: 10px; font-weight: 400; }
.v10-card-cat { font-size: var(--fs-xs); color: var(--c-text-3); margin-bottom: var(--sp-2); }

/* Tab 内 sticky 小目录（仅 GMV 总览 Tab）*/
.tab-anchor-nav { position: sticky; top: 56px; z-index: 8; background: rgba(255,255,255,0.97); backdrop-filter: blur(8px); border-bottom: 1px solid var(--c-border); margin: -8px -8px var(--sp-3); padding: 8px 8px; display: flex; gap: 6px; overflow-x: auto; font-size: var(--fs-xs); }
.tab-anchor-nav a { color: var(--c-text-3); text-decoration: none; white-space: nowrap; padding: 4px 10px; border-radius: 6px; border: 1px solid transparent; transition: all 0.15s; }
.tab-anchor-nav a:hover { background: var(--c-bg-3); color: var(--c-text); border-color: var(--c-border); }

/* 区块视觉锚（数字标 + 块标题）*/
.section-block { margin: var(--sp-5) 0 var(--sp-4); }
.section-block-head { display: flex; align-items: center; gap: 10px; margin-bottom: var(--sp-3); padding-bottom: var(--sp-2); border-bottom: 2px solid var(--c-deep); }
.section-block-num { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; background: var(--c-deep); color: #fff; border-radius: 6px; font-weight: 700; font-size: var(--fs-sm); flex-shrink: 0; }
.section-block-title { font-size: var(--fs-md); font-weight: 700; color: var(--c-text); }
.section-block-sub { font-size: var(--fs-xs); color: var(--c-text-3); margin-left: auto; }

/* 行业 KPI 双栏对照表 */
.industry-kpi-dual { background: var(--c-bg); border: 1px solid var(--c-border); border-radius: var(--r); padding: var(--sp-4); }
.industry-kpi-dual-table { width: 100%; border-collapse: collapse; font-size: var(--fs-sm); }
.industry-kpi-dual-table th { text-align: left; padding: 10px 12px; color: var(--c-text-2); font-weight: 600; border-bottom: 2px solid var(--c-border); font-size: var(--fs-xs); }
.industry-kpi-dual-table th.pic-col { color: var(--c-good); }
.industry-kpi-dual-table th.vid-col { color: var(--c-deep-2); }
.industry-kpi-dual-table td { padding: 12px; border-bottom: 1px solid var(--c-border); }
.industry-kpi-dual-table td.kpi-name { color: var(--c-text-2); font-weight: 500; }
.industry-kpi-dual-table td.kpi-val-pic { font-weight: 700; color: var(--c-good); font-size: var(--fs-base); }
.industry-kpi-dual-table td.kpi-val-vid { font-weight: 700; color: var(--c-deep); font-size: var(--fs-base); }
.industry-kpi-dual-table tr:hover { background: var(--c-bg-2); }
.industry-kpi-note { font-size: var(--fs-xs); color: var(--c-text-3); margin-top: 12px; padding: 8px 12px; background: var(--c-bg-2); border-radius: var(--r-sm); }
.v10-subhead { font-size: 14px; font-weight: 700; margin: 18px 0 10px; padding: 6px 10px; border-radius: 4px; }
.v10-subhead-green { color: var(--c-good); background: #e8f5ee; }
.v10-subhead-red { color: var(--c-bad); background: #fde8e8; }
.v10-cards-grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin-bottom: 18px; }
.v10-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.v10-card-high { border-left: 4px solid var(--c-good); }
.v10-card-low { border-left: 4px solid var(--c-bad); background: #fffafa; }
.v10-card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.v10-card-num { background: var(--c-good); color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.v10-card-num-red { background: var(--c-bad); }
.v10-card-name { font-size: 14px; font-weight: 700; color: var(--c-deep); flex: 1; }
.conf-badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.cb-high { background: #d4edda; color: var(--c-good); }
.cb-mid { background: #fff3cd; color: var(--c-text-2); }
.cb-low { background: #f8d7da; color: var(--c-bad); }
.v10-card-meta { font-size: 12px; color: var(--c-text-2); margin-bottom: 6px; }
.v10-stat { color: var(--c-text-3); }
.diff-pp { color: var(--c-good); font-weight: 600; margin-left: 8px; }
.diff-pp-red { color: var(--c-bad); }
.diff-ratio { background: #fff8d6; padding: 1px 6px; border-radius: 4px; font-size: 11px; color: var(--c-text-2); margin-left: 4px; }
.v10-card-cat { font-size: 11px; color: var(--c-text-3); margin-bottom: 8px; line-height: 1.5; }
.v10-card-advice { background: #f0f8ff; border-radius: 6px; padding: 8px 12px; font-size: 13px; color: var(--c-text); line-height: 1.6; }
.v10-card-advice-red { background: #fff5f5; color: var(--c-text); }
.v10-card-examples { margin-top: 10px; font-size: 12px; color: var(--c-text-2); }
.v10-card-examples summary { cursor: pointer; color: var(--c-deep); padding: 4px 0; font-weight: 500; }
.v10-card-examples summary:hover { color: var(--c-deep); }
.v10-ex-block { margin: 8px 0; }
.v10-ex-label { font-size: 11px; color: var(--c-text-3); font-weight: 600; margin-bottom: 4px; }
.v10-ex-label-red { color: var(--c-bad); }
.v10-ex-list { margin: 4px 0 0 18px; padding: 0; line-height: 1.7; color: var(--c-text-2); font-size: 12px; }
.v10-ex-list li { margin-bottom: 3px; }
.v10-note-link { color: var(--c-deep); text-decoration: none; }
.v10-note-link:hover { color: #d92f5e; text-decoration: underline; }

/* 件单价 4 机制 playbook */
.price-playbook-section { margin: 20px 0; }
.price-banner { background: linear-gradient(135deg, #ffe9f0, #ffd5e3) !important; border-left-color: #d92f5e !important; }
.v10-mech-hero { background: linear-gradient(135deg, var(--c-deep), var(--c-deep-2)); color: #f0f0f0; border-left: 4px solid var(--c-warn); font-size: 14px; padding: 14px 18px; }
.v10-mech-hero b { color: #fff; }
.price-mech-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
.price-mech-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-top: 3px solid #d92f5e; }
.price-mech-head { margin-bottom: 8px; }
.price-mech-name { font-size: 15px; font-weight: 700; color: var(--c-deep); }
.price-mech-desc { font-size: 12px; color: var(--c-text-3); margin-bottom: 10px; line-height: 1.6; }
.price-mech-sop { background: #f0f8ff; border-radius: 6px; padding: 8px 12px; font-size: 13px; color: var(--c-text); line-height: 1.6; margin-bottom: 8px; }
.price-mech-pitfall { background: #fff5e6; border-radius: 6px; padding: 8px 12px; font-size: 12px; color: var(--c-text-2); line-height: 1.6; margin-bottom: 10px; }
.price-mech-cases summary { cursor: pointer; color: var(--c-deep); padding: 4px 0; font-weight: 500; font-size: 12px; }
.price-mech-cases summary:hover { color: #d92f5e; }
.case-meta { color: var(--c-text-3); font-size: 11px; }
.case-empty { color: var(--c-text-4); font-style: italic; }
@media (max-width: 768px) {
  .price-mech-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .v10-banner { padding: 10px 12px; }
  .v10-banner-title { font-size: 14px; }
  .v10-card { padding: 10px 12px; }
  .v10-card-name { font-size: 13px; }
}

/* === V10.3 按钮可见性修复 === */
/* btn-gen 文字强制白色（V10 body color 全局 override 可能影响） */
.btn-gen { color: #fff !important; }
/* Kimi 按钮用绿色区分（更易识别） */
button.btn-gen:first-child,
.planner-actions .btn-gen:first-of-type { background: #00b96b !important; }
/* CTR2 优先级卡 +pp 改成中文描述，不挂术语 */
'''

# ============ 调用 build_v9.py（它会再调 build_v8_gpm.py）============
import subprocess
print('=== 先跑 build_v9.py 生成基础 HTML ===')
result = subprocess.run([sys.executable, os.path.join(WORKDIR, 'build_v9.py')], capture_output=True, text=True, cwd=WORKDIR)
print(result.stdout[-1500:] if result.stdout else '')
if result.returncode != 0:
    print('❌ build_v9.py 失败')
    print(result.stderr[-2000:])
    sys.exit(1)

# 读 V9 生成的 HTML，注入 V10 section
out_path = os.path.join(WORKDIR, 'index.html')
html = open(out_path, encoding='utf-8').read()

# 安全检查：getFormData 函数是否存在（某些 V8/V9 build 路径会丢失它）
if 'function getFormData()' not in html:
    GET_FORM_DATA_JS = """function getFormData() {
    const name = document.getElementById('product-name').value.trim();
    const feature = document.getElementById('product-feature').value.trim();
    const audience = document.getElementById('product-audience').value.trim();
    const cat = document.querySelector('input[name="cat"]:checked').value;
    return { name, feature, audience, cat };
  }

  """
    html = html.replace('function buildPrompt()', GET_FORM_DATA_JS + 'function buildPrompt()', 1)
    print('✅ getFormData 函数已补注入（V8/V9 丢失兜底）')
else:
    print('✅ getFormData 函数已存在，跳过补注入')

# 安全检查：CAT_TRENDS 数据是否存在（某些 build 路径会丢失）
if 'const CAT_TRENDS' not in html:
    import pathlib
    _backup = pathlib.Path(WORKDIR) / 'index_v1_backup.html'
    if _backup.exists():
        _bk = _backup.read_text(encoding='utf-8')
        _s = _bk.find('  const CAT_TRENDS = {')
        _tf_start = _bk.find('  const TITLE_FORMULAS = `', _s)
        _tf_end = _bk.find('`;\n', _tf_start) + 2
        _cat_block = _bk[_s:_tf_end].strip()
        html = html.replace('function getFormData()', _cat_block + '\n\n  function getFormData()', 1)
        print(f'✅ CAT_TRENDS + TITLE_FORMULAS 已从 backup 补注入（{len(_cat_block)} 字符）')
    else:
        print('⚠️ CAT_TRENDS 缺失且 backup 不存在，提示词预览将报错')
else:
    print('✅ CAT_TRENDS 已存在，跳过')

# 在每个 Tab 里 "🎯 行业参考值" 标签之前注入 V10 section
metric_labels = {
    'ctr1': 'CTR1（封面+标题点击）',
    'ctr2': 'CTR2（商品卡点击）',
    'cvr':  'CVR（下单转化）',
    'price':'件单价（单笔客单）',
}

# tab-panel 顺序：gpm, ctr1, ctr2, cvr, price, cat, audit, tools
# 在 tab-ctr1/ctr2/cvr/price 内部的"行业参考值" 前面注入

# Tab1 算法分阶梯表：已移除（商家理解成本过高，看不到分数也无行动抓手）
# mac_html = render_metric_algo_corr_table()  # 保留函数定义备用，但不注入

for metric_key in ['ctr1', 'ctr2', 'cvr', 'price']:
    if metric_key == 'price':
        section_html = render_price_playbook()
    else:
        section_html = render_v10_section(metric_key, metric_labels[metric_key])
    
    # 找到这个 tab 的 panel，插入位置 = hero block 之后、 two-weapons-banner 之前
    # 这样后续 V9 折叠（从 two-weapons-banner 开始包）才不会把 V10 section 吞进去
    tab_pat = rf'<div class="tab-panel hidden" id="tab-{metric_key}">'
    tab_start = html.find(tab_pat)
    if tab_start < 0:
        print(f'❌ {metric_key} Tab 未找到')
        continue
    # 找 hero block 闭合（hero block 是 panel 内第一个 <div class="hero...">...</div>）
    hero_open = html.find('<div class="hero', tab_start)
    if hero_open < 0:
        print(f'❌ {metric_key} 未找到 hero block')
        continue
    # hero block 可能嵌套，找匹配 </div>：用 depth 计数
    depth = 1
    i = hero_open + len('<div')
    while depth > 0 and i < len(html):
        nxt_open = html.find('<div', i)
        nxt_close = html.find('</div>', i)
        if nxt_close < 0: break
        if 0 <= nxt_open < nxt_close:
            depth += 1; i = nxt_open + len('<div')
        else:
            depth -= 1; i = nxt_close + len('</div>')
    if depth != 0:
        print(f'❌ {metric_key} hero block 闭合不匹配')
        continue
    ins_pos = i  # 紧跟在 hero 闭合 </div> 之后
    html = html[:ins_pos] + '\n' + section_html + '\n' + html[ins_pos:]
    print(f'✅ {metric_key} Tab 注入 V10 section（hero 后）')

# V10 UI 降噪：折叠 V9 老的"两套武器+反直觉+方法卡"为可展开模块
# 4 指标 Tab 内：把 two-weapons-banner 到结尾整体包一层 details
for metric_key in ['ctr1', 'ctr2', 'cvr', 'price']:
    # 找该 tab 的 panel 边界
    tab_start = html.find(f'<div class="tab-panel hidden" id="tab-{metric_key}">')
    if tab_start < 0: continue
    # 找该 tab 内 two-weapons-banner 位置
    tw_start = html.find('<div class="two-weapons-banner">', tab_start)
    if tw_start < 0: continue
    # 找下一个 tab-panel 开始 或 closing 边界
    next_tab = html.find('<div class="tab-panel hidden"', tab_start + 100)
    if next_tab < 0: next_tab = html.find('</body>')
    # tab panel 是否在边界内
    if tw_start > next_tab: continue
    # 找 panel 自身的 closing </div>（粗略：找到最后一个 </div> 紧贴下一个 tab 之前）
    panel_end = next_tab
    # 简化：从 two-weapons-banner 到 next_tab 之间的内容包 details
    legacy = html[tw_start:panel_end].rstrip()
    # 去掉末尾 </div>（保留给 panel 收尾）
    while legacy.endswith('</div>'):
        legacy = legacy[:-6].rstrip()
    legacy_back_close = (panel_end - len((html[tw_start:panel_end]).rstrip())) - tw_start  # 不用，直接简化
    wrapped = f'''<details class="v9-legacy-fold">
  <summary class="v9-legacy-summary">📚 看更多写法参考（点开：图文/视频路径详细方法卡 + 反直觉发现）</summary>
  <div class="v9-legacy-body">{html[tw_start:panel_end]}</div>
</details>'''
    html = html[:tw_start] + wrapped + html[panel_end:]
    print(f'✅ {metric_key} Tab V9 老内容已折叠')

# V10.2 UI 改造：GMV 总览 Tab 内
# 1) 加 sticky 锚目录
# 2) 把图文/视频 8 张 KPI 卡合并成双栏对照表
import json as _json
def render_industry_kpi_dual_table():
    """读 data/industry_*.json，render 成图文 vs 视频双栏对照表"""
    # 尝试从已 build 的 HTML 抓数（避免依赖外部文件）
    pic = {}
    vid = {}
    # 用 regex 从原 HTML KPI 卡里抓值
    return None  # 留空：直接基于现有 KPI 数据 transform

# 用 BeautifulSoup-style regex 改造：把 KPI 8 卡片折成对照表
def transform_industry_kpi(html):
    """把 Tab1 内 2 个 '行业参考值' section + 8 张 kpi-card 合并成 1 张对照表"""
    # 找 Tab1 panel
    tab_start = html.find('<div class="tab-panel" id="tab-gpm">')
    tab_end = html.find('<div class="tab-panel hidden"', tab_start + 100)
    if tab_start < 0 or tab_end < 0:
        return html
    panel = html[tab_start:tab_end]
    
    # 抓 2 个 section-label + 后续 KPI 数据
    # 用 regex 匹配每个 kpi-card 的关键值
    # kpi-card 结构: <div class="kpi-card"><div class="kpi-label">CTR1 ...</div><div class="kpi-value">10.1%</div>...</div>
    kpi_pattern = re.compile(
        r'<div class="kpi-card">\s*<div class="kpi-title">([^<]+)</div>\s*<div class="kpi-value">([^<]+)</div>',
        re.DOTALL
    )
    matches = list(kpi_pattern.finditer(panel))
    if len(matches) < 8:
        print(f'⚠️ 行业 KPI 卡只找到 {len(matches)} 张，未做折叠')
        return html
    
    # 前 4 个=图文，后 4 个=视频
    pic_kpis = matches[:4]
    vid_kpis = matches[4:8]
    
    # 找 2 个 section-label 在 panel 内位置（相对）
    label_pat = re.compile(r'<div class="section-label">[^<]+</div>')
    labels = list(label_pat.finditer(panel))
    if len(labels) < 2:
        print('⚠️ 找不到 2 个 section-label')
        return html
    pic_label_start = labels[0].start()
    # 视频组结束位置：找第 4 个视频 kpi-card 之后的 </div>，简单点：第 8 张卡末尾后第一个 </div>
    vid_last_end = vid_kpis[3].end()
    # 找该位置之后的下一个 section-label（即 GPM 自查）或下一个 </div></div>
    next_section = panel.find('<div class="section-label">', vid_last_end)
    if next_section < 0:
        next_section = vid_last_end + 200
    
    # 构建对照表
    def kn(label):
        return re.sub(r'\s+', ' ', label).strip()
    
    rows = ''
    for i, k in enumerate(['CTR1 封面点击率', 'CTR2 商品卡点击率', 'CVR 转化率', '件单价']):
        p = pic_kpis[i]
        v = vid_kpis[i]
        rows += f'''<tr>
  <td class="kpi-name">{k}</td>
  <td class="kpi-val-pic">{p.group(2)}</td>
  <td class="kpi-val-vid">{v.group(2)}</td>
</tr>'''
    
    new_block = f'''<div class="section-block">
  <div class="section-block-head">
    <span class="section-block-num">4</span>
    <span class="section-block-title">行业参考值 · 图文 vs 视频对照</span>
    <span class="section-block-sub">把你后台数据对一下</span>
  </div>
  <div class="industry-kpi-dual">
    <table class="industry-kpi-dual-table">
      <thead>
        <tr>
          <th>指标</th>
          <th class="pic-col">📈 图文 P75</th>
          <th class="vid-col">🎬 视频 P75</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <div class="industry-kpi-note">📌 P75 = 把所有商家按这个指标从高到低排队，排在第 25% 位置的值；超过这个数就算行业前 25%</div>
  </div>
</div>'''
    
    # 替换：从 pic_label_start 到 next_section
    new_panel = panel[:pic_label_start] + new_block + panel[next_section:]
    html = html[:tab_start] + new_panel + html[tab_end:]
    print(f'✅ Tab1 行业 KPI 8 卡片合并为对照表')
    return html

html = transform_industry_kpi(html)

# Tab1 顶部加 sticky 锚目录
def add_tab1_anchor_nav(html):
    tab_start = html.find('<div class="tab-panel" id="tab-gpm">')
    if tab_start < 0: return html
    # 找 hero block 闭合位置
    hero_open = html.find('<div class="hero', tab_start)
    if hero_open < 0: return html
    depth = 1
    i = hero_open + len('<div')
    while depth > 0 and i < len(html):
        nxt_open = html.find('<div', i)
        nxt_close = html.find('</div>', i)
        if nxt_close < 0: break
        if 0 <= nxt_open < nxt_close: depth += 1; i = nxt_open + len('<div')
        else: depth -= 1; i = nxt_close + len('</div>')
    if depth != 0: return html
    
    nav = '''
<nav class="tab-anchor-nav">
  <a href="#anchor-formula">📐 公式</a>
  <a href="#anchor-industry">🎯 行业参考</a>
  <a href="#anchor-selfcheck">🧮 GPM 自查</a>
</nav>'''
    html = html[:i] + nav + html[i:]
    print('✅ Tab1 sticky 锚目录已添加')
    return html

html = add_tab1_anchor_nav(html)

# 给区块加 anchor id：公式 / 行业参考 / 自查（算法分阶梯已移除，anchor-algo 不再需要）
def add_block_anchors(html):
    # 1. funnel-formula → anchor-formula
    html = html.replace('<div class="funnel-formula">', '<div class="funnel-formula" id="anchor-formula">', 1)
    # 2. metric-algo-corr 已移除，跳过 anchor-algo
    # 3. section-block （行业参考表）→ anchor-industry
    html = html.replace('<div class="section-block">', '<div class="section-block" id="anchor-industry">', 1)
    # 4. GPM 自查 section-label → anchor-selfcheck
    html = re.sub(r'<div class="section-label">🧮', '<div class="section-label" id="anchor-selfcheck">🧮', html, count=1)
    print('✅ 区块 anchor id 已添加（公式/行业参考/自查）')
    return html

html = add_block_anchors(html)

# V10 卖点助手 prompt 替换为 V10 方法论版本
V10_PROMPT_FN = open(os.path.join(WORKDIR, 'v10_prompt_template.js'), encoding='utf-8').read().strip()
old_prompt_pat = re.compile(r'function buildRefPromptText\(p\)\s*\{.*?return\s+`[^`]*`;\s*\}', re.DOTALL)
m_prompt = old_prompt_pat.search(html)
if m_prompt:
    html = html[:m_prompt.start()] + V10_PROMPT_FN + html[m_prompt.end():]
    print('✅ 卖点助手 prompt 已替换为 V10 版本')
else:
    print('⚠️ 老 buildRefPromptText 未找到，prompt 未更新')

# 注入 V10 CSS（接在 V9 CSS 之后）
html = html.replace('</style>', V10_CSS + '\n</style>', 1)

# 给 CTR1/CTR2/CVR/GPM/DGMV 等业务术语加 hover 解释（仅文本中的独立词，避 tag attribute）
TERM_TOOLTIPS = {
    # 注意 tooltip 文本必须不含 " 和不含本表其他术语，否则会 1) 撑爆 HTML attribute 2) 嵌套 wrap 撕裂
    'CTR1': '封面点击率，曝光后被点开笔记的比例（小红书后台叫封面点击率）',
    'CTR2': '商品卡点击率，看了笔记后点开商品卡的比例',
    'CVR':  '下单转化率，点开商品卡后实际下单的比例',
    'GPM':  '每千次曝光带来的销售额（GMV per Mille）',
    'DGMV': '笔记直接带来的销售额（不含间接成交，小红书后台同口径）',
    'GMV':  '商品成交金额，即销售额',
    '件单价': '单笔订单平均成交金额',
}
# 严格 segment 拆分：tag / text / 已有 abbr 三类，仅 text 类才扫描替换；
# 替换后用 sentinel 占位避免被后续术语再次匹配
import html as _html
import uuid as _uuid

def wrap_terms_in_text(html_text):
    """
    严格 wrap：避免 4 类 bug
      1) 嵌套 abbr（GPM tip 含 GMV 又被 GMV wrap）
      2) 在 tag 内替换（如 <div class="something CTR1 ...">）
      3) 在已有 abbr 内替换
      4) tip 文本含 " 把 attribute 撑爆
    新增：避免在 tab-btn / mech-hero / nav 类深色容器内挂 abbr（hover tooltip 被遮挡 / 深色背景看不清）
    实现：每次 wrap 完一个术语就把所有新 abbr 整段 stash 成 sentinel，下一术语只扫 sentinel 之外的文本。
    """
    placeholders = {}
    def _stash(m):
        k = f'@@A_{_uuid.uuid4().hex[:14]}@@'
        placeholders[k] = m.group(0)
        return k
    
    # 0) 先 stash 已存在的所有 abbr
    abbr_pat = re.compile(r'<abbr[^>]*>.*?</abbr>', re.DOTALL)
    html_text = abbr_pat.sub(_stash, html_text)
    
    # 新增 0.5) 把"不应挂 abbr 的深色容器/tab btn"先 stash，wrap 完再还原
    # 包括：tab-btn / v10-mech-hero / tab-anchor-nav 类整段
    EXCLUDE_PATTERNS = [
        # tab 按钮
        re.compile(r'<button class="tab-btn[^"]*"[^>]*>.*?</button>', re.DOTALL),
        # 核心机制 hero（深色卡）
        re.compile(r'<div class="v10-mechanism v10-mech-hero[^"]*">.*?</div>', re.DOTALL),
        # 算法表的关键洞察 hero（深色）
        re.compile(r'<div class="mac-key">.*?</div>', re.DOTALL),
        # tab sticky 锚 nav
        re.compile(r'<nav class="tab-anchor-nav">.*?</nav>', re.DOTALL),
    ]
    for ep in EXCLUDE_PATTERNS:
        html_text = ep.sub(_stash, html_text)
    
    PER_TERM_GLOBAL_CAP = 8
    counts = {t: 0 for t in TERM_TOOLTIPS}
    
    for term, tip in TERM_TOOLTIPS.items():
        if counts[term] >= PER_TERM_GLOBAL_CAP: continue
        parts = re.split(r'(<[^>]+>)', html_text)
        for i, p in enumerate(parts):
            if i % 2 == 1:
                continue
            if counts[term] >= PER_TERM_GLOBAL_CAP:
                continue
            pat = re.compile(r'(?<![A-Za-z0-9_\u4e00-\u9fa5])' + re.escape(term) + r'(?![A-Za-z0-9_])')
            def _rep(m):
                if counts[term] >= PER_TERM_GLOBAL_CAP:
                    return m.group(0)
                counts[term] += 1
                safe = _html.escape(tip, quote=True)
                return f'<abbr class="term-abbr" data-tip="{safe}">{term}</abbr>'
            parts[i] = pat.sub(_rep, p)
        html_text = ''.join(parts)
        # 立刻 stash 本轮生成的 abbr
        html_text = abbr_pat.sub(_stash, html_text)
    
    # 还原所有 sentinel
    for k, v in placeholders.items():
        html_text = html_text.replace(k, v)
    return html_text

html = wrap_terms_in_text(html)
print(f'✅ 业务术语已加 hover tooltip')

# 注入移动端 tap 触发 tooltip 的 JS（桌面 hover 仍由 CSS 处理）
TIP_JS = '''
<script>
// V10.2 移动端 tooltip tap 触发
(function(){
  let curOpen = null;
  document.addEventListener('click', function(e){
    const t = e.target.closest('.term-abbr');
    if (t) {
      e.preventDefault();
      if (curOpen && curOpen !== t) curOpen.classList.remove('tip-open');
      t.classList.toggle('tip-open');
      curOpen = t.classList.contains('tip-open') ? t : null;
    } else if (curOpen) {
      curOpen.classList.remove('tip-open');
      curOpen = null;
    }
  });
})();
</script>
'''
html = html.replace('</body>', TIP_JS + '</body>', 1)

# 写回
open(out_path, 'w', encoding='utf-8').write(html)

print()
print('=== V10 build 自检 ===')
print(f'tab-panel 数量：{html.count("tab-panel hidden")} + active={html.count("tab-panel active")}')
print(f'V10 section 数量：{html.count("v10-section")}（预期 4）')
print(f'V10 high card 数量：{html.count("v10-card-high")}')
print(f'V10 low card 数量：{html.count("v10-card-low")}')
print(f'V10 mechanism 数量：{html.count("v10-mechanism")}（预期 4）')
print()
print(f'✅ V10 build 完成，写入 {out_path} ({len(html):,} chars)')
