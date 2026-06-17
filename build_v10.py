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
    <span class="v10-stat">表现好的笔记里 <b>{high_n} 篇</b>用了这招 · 表现差的笔记里只 <b>{low_n} 篇</b>用</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 类目分布：{cat}</div>
  <div class="v10-card-advice">💡 <b>商家建议</b>：{advice}</div>
  <details class="v10-card-examples">
    <summary>📌 看真实案例（{len(examples)} 篇好笔记 + {len(contrast)} 篇反例）</summary>
    <div class="v10-ex-block">
      <div class="v10-ex-label">🟢 表现好的笔记是这么写的</div>
      <ul class="v10-ex-list">{ex_html}</ul>
    </div>
    {f'<div class="v10-ex-block"><div class="v10-ex-label v10-ex-label-red">🔴 表现差的笔记反例</div><ul class="v10-ex-list">{co_html}</ul></div>' if co_html else ''}
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
    <span class="v10-stat">表现差的笔记里 <b>{low_n} 篇</b>踩了这坑 · 表现好的笔记里只 <b>{high_n} 篇</b>这么写</span>
    {diff_str}
  </div>
  <div class="v10-card-cat">📊 类目分布：{cat}</div>
  <div class="v10-card-advice v10-card-advice-red">🚫 <b>避坑建议</b>：{advice}</div>
  {f'<details class="v10-card-examples"><summary>📌 看真实反例（{len(examples)} 篇）</summary><ul class="v10-ex-list">{ex_html}</ul></details>' if examples else ''}
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
    ladder = [
        {'feat': '真诚分享',   'q1_dgmv': 1138,  'q4_dgmv': 3014,  'dgmv_x': 2.6,  'imp_x': 2.4,  'positive': True},
        {'feat': '营销味淡',   'q1_dgmv': 1335,  'q4_dgmv': 3679,  'dgmv_x': 2.8,  'imp_x': 2.4,  'positive': True},
        {'feat': '综合算法分', 'q1_dgmv': 1503,  'q4_dgmv': 3474,  'dgmv_x': 2.3,  'imp_x': 2.2,  'positive': True},
        {'feat': '笔记质量分', 'q1_dgmv': 702,   'q4_dgmv': 13110, 'dgmv_x': 18.7, 'imp_x': 170,  'positive': True, 'star': True},
        {'feat': '好点击留人', 'q1_dgmv': 2688,  'q4_dgmv': 1222,  'dgmv_x': 0.5,  'imp_x': 0.4,  'positive': False},
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
  <div class="mac-title">🤖 平台算法分 × <abbr title="DGMV = 笔记带来的直接成交金额（小红书后台同口径）">DGMV</abbr> 真实阶梯（n=1199 篇笔记）</div>
  <div class="mac-sub">把池里 1199 篇笔记<b>按算法打分从低到高排队</b>，分成 4 段，看每段笔记<b>典型 DGMV 和曝光</b>是多少。<b>这是实测产出，不是统计模型</b>。</div>
  <table class="mac-table mac-ladder">
    <thead><tr>
      <th>平台给的算法分</th>
      <th><abbr title="把所有笔记按算法分从高到低排队，分数最低的 25%">算法分倒数 25%</abbr><br><span class="mac-th-sub">这批笔记典型 DGMV</span></th>
      <th><abbr title="把所有笔记按算法分从高到低排队，分数最高的 25%">算法分 Top 25%</abbr><br><span class="mac-th-sub">这批笔记典型 DGMV</span></th>
      <th>多卖多少倍</th>
      <th>多拿多少倍曝光</th>
      <th></th>
    </tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="mac-key">💎 <b>关键洞察</b>：算法分高的笔记 DGMV 是算法分低的 <b>2-19 倍</b>，曝光最多大 <b>170 倍</b>。追"<b>真诚分享 / 营销味淡 / 笔记质量分</b>"非常有用；但要警惕"<b>好点击留人</b>"分高的笔记反而少卖货——可能是标题党骗到了点击但卖不动。</div>
  <div class="mac-warn">📌 注：之前用统计相关系数（皮尔逊）拟合点击率类指标，数值小且方向容易误导，已改成上面的"按算法分排队分 4 段看典型产出"。</div>
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
.mac-warn { font-size: 11px; color: #999; margin-top: 8px; padding: 8px 12px; background: #f8f9fa; border-radius: 4px; border-left: 2px solid #ccc; }
/* Ladder 表 */
.mac-ladder td, .mac-ladder th { padding: 8px 10px; text-align: center; font-size: 13px; }
.mac-ladder th:first-child, .mac-ladder td:first-child { text-align: left; }
.ladder-feat { font-weight: 600; color: #333; }
.ladder-q1 { color: #888; }
.ladder-q4 { color: #1a7a3f; font-weight: 600; }
.ladder-mult { font-weight: 600; }
.ladder-x { color: #1a7a3f; background: #e8f5ee; padding: 2px 8px; border-radius: 10px; }
.ladder-x-neg { color: #c0392b; background: #fde8e8; padding: 2px 8px; border-radius: 10px; }
.ladder-neg { background: #fffafa; }
.ladder-warn { color: #c0392b; font-size: 11px; font-weight: 600; }

/* V9 老内容折叠样式 */
.v9-legacy-fold { background: #fafbfc; border: 1px solid #e5e7eb; border-radius: 10px; margin: 24px 0 16px; padding: 0; }
.v9-legacy-summary { cursor: pointer; padding: 14px 18px; font-size: 13px; font-weight: 600; color: #666; list-style: none; display: flex; align-items: center; gap: 8px; user-select: none; }
.v9-legacy-summary::-webkit-details-marker { display: none; }
.v9-legacy-summary::before { content: '▶'; transition: transform 0.2s; color: #999; font-size: 10px; }
.v9-legacy-fold[open] .v9-legacy-summary::before { transform: rotate(90deg); }
.v9-legacy-summary:hover { color: #d92f5e; }
.v9-legacy-body { padding: 16px 18px 4px; border-top: 1px solid #e5e7eb; }

/* 业务术语 hover */
.term-abbr { text-decoration: none; border-bottom: 1px dotted #aaa; cursor: help; }
.term-abbr:hover { background: #fff5d6; }
.mac-th-sub { display: block; font-size: 10px; color: #888; font-weight: 400; margin-top: 2px; }
abbr.conf-badge { text-decoration: none; cursor: help; }
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
    'CTR1': '封面点击率：曝光 → 点开笔记的比例（你后台叫"封面点击率/CTR"）',
    'CTR2': '商品卡点击率：看了笔记 → 点开商品卡的比例',
    'CVR':  '下单转化率：看了商品卡 → 实际下单的比例',
    'GPM':  'GMV per Mille：每 1000 次曝光带来的 GMV，等于 CTR1 × CTR2 × CVR × 件单价 × 1000',
    'DGMV': '笔记直接带来的 GMV（小红书后台同口径，不含间接成交）',
    'GMV':  '商品成交金额（销售额）',
    '件单价': '单笔订单平均成交金额 = DGMV / 下单数',
}
# 只替换文本节点中第一次出现的（避免重复嵌套）
import html as _html
already_wrapped = set()
def wrap_terms_in_text(html_text):
    """对 HTML 文本（非 attribute/tag）替换术语"""
    # 简单做法：先 split 成 tag/text segments
    parts = re.split(r'(<[^>]+>)', html_text)
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            # 是 tag，不动
            out.append(p)
            continue
        # 文本段，对每个术语只替换首次（避免无限嵌套）
        for term, tip in TERM_TOOLTIPS.items():
            # 已被 abbr 包过的就跳过
            if f'>{term}<' in p or f'"{tip}"' in p: continue
            # 用边界匹配避免误替换（如 "ictr1" 不替换）
            pattern = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(term) + r'(?![A-Za-z0-9_])')
            # 替换前两次（防止整页太多 abbr）
            p, n = pattern.subn(f'<abbr class="term-abbr" title="{_html.escape(tip)}">{term}</abbr>', p, count=2)
        out.append(p)
    return ''.join(out)

html = wrap_terms_in_text(html)
print(f'✅ 业务术语已加 hover tooltip')

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
