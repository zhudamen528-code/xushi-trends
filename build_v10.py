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
    return f'<span class="conf-badge {color}">信心 {escape(c)}</span>'

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
    if diff: diff_str = f'<span class="diff-pp">高组 +{diff}pp</span>'
    if ratio and ratio != diff_str:
        diff_str += f' <span class="diff-ratio">{escape(ratio)}</span>'
    
    examples = p.get('high_examples', [])
    contrast = p.get('low_contrast_examples', [])
    
    ex_html = ''.join(example_li(e) for e in examples[:4])
    co_html = ''.join(example_li(e) for e in contrast[:2])
    
    return f'''<div class="v10-card v10-card-high">
  <div class="v10-card-head">
    <span class="v10-card-num">#{idx+1}</span>
    <span class="v10-card-name">{name}</span>
    {confidence_badge(conf)}
  </div>
  <div class="v10-card-meta">
    <span class="v10-stat">高组命中 {high_n} 条 vs 低组 {low_n} 条</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 类目分布：{cat}</div>
  <div class="v10-card-advice">💡 <b>商家建议</b>：{advice}</div>
  <details class="v10-card-examples">
    <summary>📌 高组案例（{len(examples)}）+ 低组反例（{len(contrast)}）</summary>
    <div class="v10-ex-block">
      <div class="v10-ex-label">🟢 高组写法</div>
      <ul class="v10-ex-list">{ex_html}</ul>
    </div>
    {f'<div class="v10-ex-block"><div class="v10-ex-label v10-ex-label-red">🔴 低组反例</div><ul class="v10-ex-list">{co_html}</ul></div>' if co_html else ''}
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
    if diff: diff_str = f'<span class="diff-pp diff-pp-red">低组 +{abs(diff) if isinstance(diff, (int, float)) else diff}pp</span>'
    if ratio: diff_str += f' <span class="diff-ratio">{escape(ratio)}</span>'
    
    # 陷阱卡只看 low_examples（即 high_examples 字段在 low_only_patterns 里可能是 low 的案例）
    # 兼容 schema：subagent 输出的 low_only_patterns 里 high_examples 通常指代低组案例
    examples = p.get('high_examples', []) or p.get('low_examples', [])
    contrast = p.get('low_contrast_examples', []) or p.get('high_contrast_examples', [])
    
    ex_html = ''.join(example_li(e) for e in examples[:4])
    co_html = ''.join(example_li(e) for e in contrast[:2])
    
    return f'''<div class="v10-card v10-card-low">
  <div class="v10-card-head">
    <span class="v10-card-num v10-card-num-red">⚠️ #{idx+1}</span>
    <span class="v10-card-name">{name}</span>
    {confidence_badge(conf)}
  </div>
  <div class="v10-card-meta">
    <span class="v10-stat">低组命中 {low_n} 条 vs 高组 {high_n} 条</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 类目分布：{cat}</div>
  <div class="v10-card-advice v10-card-advice-red">🚫 <b>避坑建议</b>：{advice}</div>
  {f'<details class="v10-card-examples"><summary>📌 反例（{len(examples)}）</summary><ul class="v10-ex-list">{ex_html}</ul></details>' if examples else ''}
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
    <div class="v10-banner-title">💎 件单价拉升 · 4 大固定机制（V10 改版）</div>
    <div class="v10-banner-sub">件单价受商品定价/促销/库存/人群消费力影响太大，<b>笔记内容只能影响临门一脚</b>。这里不做差分聚类（会被"贵商品天然贵"污染），改成 4 个可直接照抄的运营机制，配本周池里真实案例。</div>
  </div>
  
  <div class="v10-mechanism v10-mech-hero">
    💎 <b>核心心智</b>：件单价 = 商品定价 × 平均购买件数。商品定价改不了，但「平均购买件数」可以通过笔记话术拉高（凑单/赠品/囤货/任选）。
  </div>
  
  <div class="price-mech-grid">{''.join(cards)}</div>
</div>'''


def render_metric_algo_corr_table():
    """Tab1 GMV 公式旁渲染：每指标与 Top 3 算法 feature 相关性"""
    metric_labels = {
        'ctr1': '👆 CTR1（封面+标题点击）',
        'ctr2': '🔗 CTR2（商品卡点击）',
        'cvr': '💵 CVR（下单转化）',
        'price': '💎 件单价（单笔客单）',
    }
    rows = []
    for mk, label in metric_labels.items():
        top = V10_METRIC_CORR.get(mk, [])[:3]
        if not top: continue
        feats = []
        for t in top:
            arrow = '↑' if t['pearson'] > 0 else '↓'
            color_cls = 'corr-pos' if t['pearson'] > 0 else 'corr-neg'
            feats.append(f'<span class="{color_cls}">{escape(t["label"])}{arrow}{abs(t["pearson"]):.2f}</span>')
        rows.append(f'<tr><td class="mac-metric">{escape(label)}</td><td class="mac-feats">{" · ".join(feats)}</td></tr>')
    return f'''<div class="metric-algo-corr">
  <div class="mac-title">🤖 4 指标 ↔ 算法 Top 3 相关 feature</div>
  <div class="mac-sub">皮尔逊系数（n=1199）。<b>↑ 表示算法该指标高的笔记，对应业务指标也越高</b>；↓ 表示反向关系。系数 0.05-0.15 属弱-中等相关，但方向已稳定。</div>
  <table class="mac-table">
    <thead><tr><th>业务指标</th><th>算法 feature Top 3</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="mac-key">💎 <b>关键洞察</b>：CVR 与「真诚分享」呈<b>负相关</b>（-0.11）——真诚分享是算法的"长期人设"奖励，但买家下单更买"具体使用方案 + 人群定位"，<b>追算法 ≠ 卖货好，两条线要分场景</b>。</div>
</div>'''

CTR2_PRIORITY_NOTE = '''<div class="ctr2-priority-note">
  <div class="cpn-title">📐 CTR2 三层优先级 · 字数本身不是因，「信息密度」才是</div>
  <div class="cpn-tier cpn-tier-1"><b>🔴 首要 · 商品名做减法</b>（差距最大 +14.5pp）<br>≤ 25 字内只放「品类 + 1 个硬指标」。例：✅「韩要强夏威夷果 250g 中大半粒」/ ❌「韩要强 0号特大现烤夏威夷果仁没有额外添加剂250克 1罐*250克【中大半粒】」</div>
  <div class="cpn-tier cpn-tier-2"><b>🟡 次要 · 正文前 200 字做减法</b>（< 100 字 +14.5pp）<br>一句卖点 + 一句证据，不要把商详顶部写成产品说明书。</div>
  <div class="cpn-tier cpn-tier-3"><b>🟢 辅助 · 标题做减法</b>（≤ 15 字 +8.3pp）<br>≤ 15 字 + 规格量化数字，让用户在信息流 0.5 秒看懂「是什么 + 多少」。</div>
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
    <div class="v10-banner-title">🔬 {escape(metric_label)} 高 vs 低对照差分聚类（V10 新增）</div>
    <div class="v10-banner-sub">按类目内 P75 vs P25 严格切高低对照组，找出"高组独有 / 低组陷阱"写法。<b>这是相关性证据，不是因果，但样本量足够、类目变量已控住</b>。</div>
  </div>
  
  {f'<div class="v10-mechanism v10-mech-hero">💎 <b>核心机制</b>：{escape(mechanism)}</div>' if mechanism else ''}
  
  {ctr2_priority}
  
  <div class="v10-subhead v10-subhead-green">✅ {len(high_patterns)} 个高组独有写法 → 抄</div>
  <div class="v10-cards-grid">{high_html}</div>
  
  <div class="v10-subhead v10-subhead-red">🚫 {len(low_patterns)} 个低组陷阱 → 避</div>
  <div class="v10-cards-grid">{low_html}</div>
</div>'''

# ============ V10 CSS ============
V10_CSS = '''
.v10-section { margin: 20px 0; }
.v10-banner { background: linear-gradient(135deg, #fff9e6, #fff3d3); border-left: 4px solid #f5b400; border-radius: 10px; padding: 14px 18px; margin-bottom: 18px; }
.v10-banner-title { font-size: 16px; font-weight: 700; color: #333; margin-bottom: 6px; }
.v10-banner-sub { font-size: 12px; color: #666; line-height: 1.6; }
.v10-mechanism { background: #f4f8ff; border-left: 3px solid #4a90e2; border-radius: 6px; padding: 12px 16px; margin: 14px 0; font-size: 13px; color: #333; line-height: 1.7; }
/* 核心机制 hero 样式：深色背景、大字、高亮 */
.v10-mech-hero { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important; color: #fff !important; border-left: 4px solid #f5b400 !important; padding: 16px 20px !important; font-size: 15px !important; line-height: 1.8 !important; box-shadow: 0 2px 8px rgba(0,0,0,0.15); margin: 16px 0 20px !important; border-radius: 8px !important; }
.v10-mech-hero b { color: #f5b400 !important; font-size: 16px; }

/* CTR2 三层优先级前置说明 */
.ctr2-priority-note { background: #fff; border: 1px solid #e8eaed; border-radius: 10px; padding: 16px 18px; margin: 14px 0 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.cpn-title { font-size: 14px; font-weight: 700; color: #d92f5e; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px dashed #f0d4dd; }
.cpn-tier { padding: 8px 12px; margin: 6px 0; border-radius: 6px; font-size: 12px; line-height: 1.7; color: #333; }
.cpn-tier-1 { background: #fff0f0; border-left: 3px solid #d92f5e; }
.cpn-tier-2 { background: #fffaeb; border-left: 3px solid #f5b400; }
.cpn-tier-3 { background: #f0fff4; border-left: 3px solid #34c759; }
.cpn-tier b { color: #222; font-size: 13px; }
.cpn-key { background: #2c3e50; color: #fff; border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 12px; line-height: 1.7; }
.cpn-key b { color: #f5b400; }

/* 指标↔算法相关性表 */
.metric-algo-corr { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 18px; margin: 16px 0 0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.mac-title { font-size: 14px; font-weight: 700; color: #2c3e50; margin-bottom: 6px; }
.mac-sub { font-size: 11px; color: #888; margin-bottom: 12px; line-height: 1.6; }
.mac-table { width: 100%; border-collapse: collapse; }
.mac-table th { font-size: 12px; color: #666; text-align: left; padding: 6px 10px; background: #f8f9fa; border-bottom: 1px solid #e5e7eb; }
.mac-table td { padding: 8px 10px; font-size: 13px; border-bottom: 1px solid #f0f0f0; }
.mac-metric { font-weight: 600; color: #333; white-space: nowrap; }
.mac-feats { color: #555; }
.corr-pos { color: #1a7a3f; background: #e8f5ee; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-right: 4px; display: inline-block; margin-bottom: 4px; }
.corr-neg { color: #c0392b; background: #fde8e8; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-right: 4px; display: inline-block; margin-bottom: 4px; }
.mac-key { background: #2c3e50; color: #fff; border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 12px; line-height: 1.7; }
.mac-key b { color: #f5b400; }

/* V9 老内容折叠样式 */
.v9-legacy-fold { background: #fafbfc; border: 1px solid #e5e7eb; border-radius: 10px; margin: 24px 0 16px; padding: 0; }
.v9-legacy-summary { cursor: pointer; padding: 14px 18px; font-size: 13px; font-weight: 600; color: #666; list-style: none; display: flex; align-items: center; gap: 8px; user-select: none; }
.v9-legacy-summary::-webkit-details-marker { display: none; }
.v9-legacy-summary::before { content: '▶'; transition: transform 0.2s; color: #999; font-size: 10px; }
.v9-legacy-fold[open] .v9-legacy-summary::before { transform: rotate(90deg); }
.v9-legacy-summary:hover { color: #d92f5e; }
.v9-legacy-body { padding: 16px 18px 4px; border-top: 1px solid #e5e7eb; }
.v10-subhead { font-size: 14px; font-weight: 700; margin: 18px 0 10px; padding: 6px 10px; border-radius: 4px; }
.v10-subhead-green { color: #1a7a3f; background: #e8f5ee; }
.v10-subhead-red { color: #b32a2a; background: #fde8e8; }
.v10-cards-grid { display: grid; grid-template-columns: 1fr; gap: 12px; margin-bottom: 18px; }
.v10-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.v10-card-high { border-left: 4px solid #1a7a3f; }
.v10-card-low { border-left: 4px solid #c0392b; background: #fffafa; }
.v10-card-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.v10-card-num { background: #1a7a3f; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.v10-card-num-red { background: #c0392b; }
.v10-card-name { font-size: 14px; font-weight: 700; color: #222; flex: 1; }
.conf-badge { font-size: 10px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.cb-high { background: #d4edda; color: #155724; }
.cb-mid { background: #fff3cd; color: #856404; }
.cb-low { background: #f8d7da; color: #721c24; }
.v10-card-meta { font-size: 12px; color: #555; margin-bottom: 6px; }
.v10-stat { color: #666; }
.diff-pp { color: #1a7a3f; font-weight: 600; margin-left: 8px; }
.diff-pp-red { color: #c0392b; }
.diff-ratio { background: #fff8d6; padding: 1px 6px; border-radius: 4px; font-size: 11px; color: #8b6914; margin-left: 4px; }
.v10-card-cat { font-size: 11px; color: #888; margin-bottom: 8px; line-height: 1.5; }
.v10-card-advice { background: #f0f8ff; border-radius: 6px; padding: 8px 12px; font-size: 13px; color: #333; line-height: 1.6; }
.v10-card-advice-red { background: #fff5f5; color: #2c2c2c; }
.v10-card-examples { margin-top: 10px; font-size: 12px; color: #555; }
.v10-card-examples summary { cursor: pointer; color: #4a90e2; padding: 4px 0; font-weight: 500; }
.v10-card-examples summary:hover { color: #2c5fa5; }
.v10-ex-block { margin: 8px 0; }
.v10-ex-label { font-size: 11px; color: #888; font-weight: 600; margin-bottom: 4px; }
.v10-ex-label-red { color: #c0392b; }
.v10-ex-list { margin: 4px 0 0 18px; padding: 0; line-height: 1.7; color: #444; font-size: 12px; }
.v10-ex-list li { margin-bottom: 3px; }
.v10-note-link { color: #1a73e8; text-decoration: none; }
.v10-note-link:hover { color: #d92f5e; text-decoration: underline; }

/* 件单价 4 机制 playbook */
.price-playbook-section { margin: 20px 0; }
.price-banner { background: linear-gradient(135deg, #ffe9f0, #ffd5e3) !important; border-left-color: #d92f5e !important; }
.v10-mech-hero { background: linear-gradient(135deg, #2c3e50, #34495e); color: #f0f0f0; border-left: 4px solid #f5b400; font-size: 14px; padding: 14px 18px; }
.v10-mech-hero b { color: #fff; }
.price-mech-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 14px; }
.price-mech-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-top: 3px solid #d92f5e; }
.price-mech-head { margin-bottom: 8px; }
.price-mech-name { font-size: 15px; font-weight: 700; color: #222; }
.price-mech-desc { font-size: 12px; color: #666; margin-bottom: 10px; line-height: 1.6; }
.price-mech-sop { background: #f0f8ff; border-radius: 6px; padding: 8px 12px; font-size: 13px; color: #333; line-height: 1.6; margin-bottom: 8px; }
.price-mech-pitfall { background: #fff5e6; border-radius: 6px; padding: 8px 12px; font-size: 12px; color: #5d4a1f; line-height: 1.6; margin-bottom: 10px; }
.price-mech-cases summary { cursor: pointer; color: #4a90e2; padding: 4px 0; font-weight: 500; font-size: 12px; }
.price-mech-cases summary:hover { color: #d92f5e; }
.case-meta { color: #888; font-size: 11px; }
.case-empty { color: #aaa; font-style: italic; }
@media (max-width: 768px) {
  .price-mech-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .v10-banner { padding: 10px 12px; }
  .v10-banner-title { font-size: 14px; }
  .v10-card { padding: 10px 12px; }
  .v10-card-name { font-size: 13px; }
}
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

# 在每个 Tab 里 "🎯 行业参考值" 标签之前注入 V10 section
metric_labels = {
    'ctr1': 'CTR1（封面+标题点击）',
    'ctr2': 'CTR2（商品卡点击）',
    'cvr':  'CVR（下单转化）',
    'price':'件单价（单笔客单）',
}

# tab-panel 顺序：gpm, ctr1, ctr2, cvr, price, cat, audit, tools
# 在 tab-ctr1/ctr2/cvr/price 内部的"行业参考值" 前面注入

# Tab1 注入"指标 ↔ 算法相关性"表
mac_html = render_metric_algo_corr_table()
mac_pattern = r'(<div class="formula-tip">.*?</div>)\s*(</div>\s*</div>\s*<div class="section-label">)'
m = re.search(mac_pattern, html, re.DOTALL)
if m:
    html = html[:m.end(1)] + '\n' + mac_html + html[m.end(1):]
    print('✅ Tab1 注入 metric-algo-corr 表')
else:
    print('⚠️ Tab1 metric-algo-corr 注入点未找到，尝试 fallback')
    # fallback：找 funnel-formula div 末尾
    fb_pat = r'(<div class="funnel-formula">.*?<div class="formula-tip">.*?</div>)\s*(</div>)'
    m2 = re.search(fb_pat, html, re.DOTALL)
    if m2:
        html = html[:m2.end(1)] + '\n' + mac_html + html[m2.end(1):]
        print('✅ Tab1 fallback 注入 metric-algo-corr 表')

for metric_key in ['ctr1', 'ctr2', 'cvr', 'price']:
    if metric_key == 'price':
        section_html = render_price_playbook()
    else:
        section_html = render_v10_section(metric_key, metric_labels[metric_key])
    
    # 找到这个 tab 的 panel
    pattern = rf'(<div class="tab-panel hidden" id="tab-{metric_key}">.*?)(<div class="section-label">🎯 行业参考值)'
    m = re.search(pattern, html, re.DOTALL)
    if m:
        # 在"行业参考值"之前插 V10 section
        html = html[:m.end(1)] + section_html + html[m.end(1):]
        print(f'✅ {metric_key} Tab 注入 V10 section')
    else:
        # fallback：直接找 tab-{key} 第一次出现
        idx = html.find(f'<div class="tab-panel hidden" id="tab-{metric_key}">')
        if idx >= 0:
            # 找到 hero 块之后插
            hero_end = html.find('</div>', html.find('<div class="hero', idx))
            if hero_end > 0:
                ins_pos = hero_end + len('</div>')
                html = html[:ins_pos] + '\n' + section_html + html[ins_pos:]
                print(f'⚠️ {metric_key} Tab fallback 注入 V10 section')
        else:
            print(f'❌ {metric_key} Tab 未找到')

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
  <summary class="v9-legacy-summary">📚 V9 老方法 · 两套武器框架 + 40 方法卡 + 反直觉发现（点开看更多角度参考）</summary>
  <div class="v9-legacy-body">{html[tw_start:panel_end]}</div>
</details>'''
    html = html[:tw_start] + wrapped + html[panel_end:]
    print(f'✅ {metric_key} Tab V9 老内容已折叠')

# 注入 V10 CSS（接在 V9 CSS 之后）
html = html.replace('</style>', V10_CSS + '\n</style>', 1)

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
