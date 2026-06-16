#!/usr/bin/env python3
"""
V9 build: 在 V8 build 之上覆盖 4 个指标 Tab 的方法卡数据。
- 保留 V8 funnel_tab 外壳 / KPI 卡 / 其他 Tab（GMV / 卖点 / 违规 / 我的参考）
- 用 V9 cluster JSON + pool JSON 替换 CTR1/CTR2/CVR/PRICE 8 个 *_METHODS_T/V 字符串
- 顶部加 "两套武器" 框架卡片 + 反直觉发现横幅
"""
import json
import os
import sys
import importlib.util

WORKDIR = os.path.dirname(os.path.abspath(__file__))
CLUSTER_DIR = os.path.join(WORKDIR, 'data', 'v9_clusters_v3')
POOL_DIR = os.path.join(WORKDIR, 'data', 'v9_pools_v3')

POOLS_BY_TAB = {
    'ctr1': ('ctr1_pic', 'ctr1_vid'),
    'ctr2': ('ctr2_pic', 'ctr2_vid'),
    'cvr':  ('cvr_pic',  'cvr_vid'),
    'price':('price_pic','price_vid'),
}

# ============ 工具 ============
def escape(s):
    if s is None: return ''
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def num_str(v, suffix='', decimals=1):
    if v is None or v == '' or v == '—': return '—'
    try:
        return f'{float(v):.{decimals}f}{suffix}'
    except: return str(v)

def delta_str(v, pool_avg, suffix='', decimals=1):
    """生成 +X.X / -X.X 的差值字符串"""
    if v is None or pool_avg is None: return ''
    try:
        d = float(v) - float(pool_avg)
        if abs(d) < 0.05: return ''
        sign = '+' if d > 0 else ''
        return f'{sign}{d:.{decimals}f}{suffix}'
    except: return ''

def get(d, *keys, default=None):
    """从字典里按顺序拿第一个非空值"""
    for k in keys:
        v = d.get(k)
        if v not in (None, '', [], {}): return v
    return default

# ============ 读 V9 数据 ============
clusters = {}
pool_notes = {}  # pool_id -> {note_id: note_data}
for p_id in ['ctr1_pic','ctr1_vid','ctr2_pic','ctr2_vid','cvr_pic','cvr_vid','price_pic','price_vid']:
    cpath = os.path.join(CLUSTER_DIR, f'{p_id}.cluster.json')
    if os.path.exists(cpath):
        clusters[p_id] = json.load(open(cpath))
    ppath = os.path.join(POOL_DIR, f'{p_id}.json')
    if os.path.exists(ppath):
        pd = json.load(open(ppath))
        pool_notes[p_id] = {n['note_id']: n for n in pd.get('notes', [])}

# ============ 计算每池整体 algo profile ============
pool_algo = {}
for p_id, notes in pool_notes.items():
    sins, lbs, gcs = [], [], []
    for nid, n in notes.items():
        s = n.get('model_sincerity_score')
        if s is not None and s != '': sins.append(float(s))
        lb = n.get('low_bad_market_score')
        if lb is not None and lb != '': lbs.append(float(lb))
        gc = n.get('good_click_quality_score')
        if gc is not None and gc != '': gcs.append(float(gc))
    pool_algo[p_id] = {
        'sincerity_avg': round(sum(sins)/len(sins), 1) if sins else None,
        'low_bad_avg': round(sum(lbs)/len(lbs), 3) if lbs else None,
        'good_click_avg': round(sum(gcs)/len(gcs), 3) if gcs else None,
    }

# ============ method profile 提取（兼容 subagent schema 差异）============
def extract_algo(method, pool_id):
    ap = method.get('algo_profile', {})
    pool = pool_algo.get(pool_id, {})
    # sincerity
    sav = ap.get('sincerity_avg') or ap.get('sin_avg') or ap.get('avg_sincerity')
    if sav is None and ('sin_delta' in ap) and pool.get('sincerity_avg') is not None:
        sav = pool['sincerity_avg'] + ap['sin_delta']
    # low_bad
    lbv = ap.get('low_bad_avg') or ap.get('lb_avg') or ap.get('avg_low_bad')
    if lbv is None and ('lb_delta' in ap) and pool.get('low_bad_avg') is not None:
        lbv = pool['low_bad_avg'] + ap['lb_delta']
    # good_click
    gcv = ap.get('good_click_avg') or ap.get('gc_avg') or ap.get('avg_good_click')
    if gcv is None and ('gc_delta' in ap) and pool.get('good_click_avg') is not None:
        gcv = pool['good_click_avg'] + ap['gc_delta']
    return {
        'sincerity': float(sav) if sav is not None else None,
        'low_bad': float(lbv) if lbv is not None else None,
        'good_click': float(gcv) if gcv is not None else None,
    }

def get_cases(method, pool_id):
    """优先用 case_notes，没有就用 note_ids 反查 pool"""
    cases = method.get('case_notes', [])
    if cases:
        return cases[:3]
    nids = method.get('note_ids', [])[:3]
    pool = pool_notes.get(pool_id, {})
    out = []
    for nid in nids:
        n = pool.get(nid, {})
        if n:
            out.append({
                'note_id': nid,
                'title': n.get('title', '—') or '—',
                'goods_name': n.get('goods_name', '—') or '—',
                'goods_price': n.get('goods_price'),
                'gpm': n.get('_gpm') or n.get('gpm'),
                'dgmv': n.get('_dgmv') or n.get('total_dgmv'),
                'seller_name': n.get('seller_name', '—'),
                'imp': n.get('total_imp') or n.get('imp_num'),
            })
    return out

# ============ 渲染单方法卡 ============
def render_method_card(method, pool_id, metric_type):
    """渲染一个方法卡 HTML (匹配 V8 .method-card-v2 结构)"""
    name = get(method, 'method_name', default='—')
    summary = get(method, 'method_summary', 'essence', 'description', default='—')
    why = get(method, 'why_it_works', 'why_works', default='')
    note_count = get(method, 'note_count', default=len(method.get('note_ids', [])))
    cats = get(method, 'top_categories', 'applicable_category', default=[])
    signals = method.get('signals', [])

    # 类目字符串
    cat_strs = []
    for entry in cats[:3]:
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            cat_strs.append(f'{entry[0]}({entry[1]})')
        elif isinstance(entry, dict):
            cat_strs.append(f"{entry.get('name','—')}({entry.get('count','')})")
        elif isinstance(entry, str):
            cat_strs.append(entry)
    cat_str = ' / '.join(cat_strs) if cat_strs else '—'

    # 算法画像（商家化语言）
    algo = extract_algo(method, pool_id)
    pool_av = pool_algo.get(pool_id, {})

    # 翻译算法分到商家语言（避免出现"真诚度/算法分"等内部术语）
    algo_tags = []
    if algo['sincerity'] is not None and pool_av.get('sincerity_avg') is not None:
        d = algo['sincerity'] - pool_av['sincerity_avg']
        if d >= 3:
            algo_tags.append('<span class="algo-tag algo-good">🚀 系统判"像真心分享"·推流加成</span>')
        elif d <= -3:
            algo_tags.append('<span class="algo-tag algo-warn">⚡ 系统判"商业味重"·短期收割型</span>')
    if algo['good_click'] is not None and pool_av.get('good_click_avg') is not None:
        d = algo['good_click'] - pool_av['good_click_avg']
        if d >= 0.01:
            algo_tags.append('<span class="algo-tag algo-good">👁 点进来的人会认真看完</span>')
    if algo['low_bad'] is not None and pool_av.get('low_bad_avg') is not None:
        d = algo['low_bad'] - pool_av['low_bad_avg']
        if d >= 0.01:
            algo_tags.append('<span class="algo-tag algo-good">🛡 避开"营销味太重"扣分</span>')
        elif d <= -0.02:
            algo_tags.append('<span class="algo-tag algo-warn">⚠️ 营销味偏重·容易被压流量</span>')

    algo_tags_html = ' '.join(algo_tags) if algo_tags else ''

    # 案例
    cases = get_cases(method, pool_id)
    case_htmls = []
    for c in cases:
        nid = c.get('note_id', '')
        url = f'https://www.xiaohongshu.com/explore/{nid}' if nid else '#'
        # 主指标
        if metric_type == 'price':
            dgmv = c.get('dgmv')
            try: metric_val = f'¥{float(dgmv):.0f}'
            except: metric_val = '—'
        else:
            gpm = c.get('gpm')
            try: metric_val = f'GPM {float(gpm):.0f}'
            except: metric_val = '—'
        title = escape(c.get('title','—') or '—')[:32]
        goods = escape(c.get('goods_name','—') or '—')[:24]
        seller = escape(c.get('seller_name','—') or '—')[:12]
        imp = c.get('imp')
        try: imp_s = f'曝光 {int(imp):,}'
        except: imp_s = ''
        meta_row = f'{seller} · {imp_s}' if imp_s else seller
        case_htmls.append(
            f'<a class="inline-case inline-case-row" href="{url}" target="_blank">'
            f'<span class="ic-metric">{metric_val}</span>'
            f'<span class="ic-title">{title}</span>'
            f'<span class="ic-hl">🛒 {goods}</span>'
            f'<span class="ic-meta-row">{meta_row}</span>'
            f'</a>'
        )
    cases_html = ''.join(case_htmls)

    # 识别信号 tips
    tips_html = ''
    if signals:
        sig_list = signals[:3] if isinstance(signals, list) else [str(signals)]
        sig_str = ' · '.join(escape(str(s)) for s in sig_list)
        tips_html = f'<div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">🔑 识别信号</span>{sig_str}</div></div>'

    return f'''<div class="method-card-v2">
  <div class="method-title">{escape(name)} <span class="method-count">· {note_count} 条</span></div>
  <div class="method-desc">{escape(summary)}</div>
  {tips_html}
  <div class="method-why">💡 <strong>为什么奏效</strong>：{escape(why)[:200]}</div>
  <div class="method-meta">
    <span class="method-cats">🏷️ 主要类目：{cat_str}</span>
    {('<div class="algo-tags">' + algo_tags_html + '</div>') if algo_tags_html else ''}
  </div>
  <div class="method-cases">{cases_html}</div>
  <div class="method-source">数据来源：V9 算法分相对分位筛后池（{note_count} 条真实笔记聚类）</div>
</div>'''

# ============ 池 → 方法字符串 ============
def render_pool_methods(pool_id, metric_type):
    c = clusters.get(pool_id, {})
    methods = c.get('methods', [])
    if not methods:
        return f'<div class="empty-pool">本周该池数据不足，暂无方法</div>'
    return ''.join(render_method_card(m, pool_id, metric_type) for m in methods)

# ============ 反直觉横幅 ============
POOL_LABEL_SHORT = {
    'ctr1_pic':'图文 CTR1','ctr1_vid':'视频 CTR1',
    'ctr2_pic':'图文 CTR2','ctr2_vid':'视频 CTR2',
    'cvr_pic':'图文 CVR','cvr_vid':'视频 CVR',
    'price_pic':'图文 件单价','price_vid':'视频 件单价',
}

def fallback_insight_from_methods(pool_id):
    """池里 key_insights 为空时，从 methods 里找算法分最对立的方法生成兜底洞察"""
    c = clusters.get(pool_id, {})
    methods = c.get('methods', [])
    if not methods: return None
    pool_av = pool_algo.get(pool_id, {})
    if not pool_av.get('sincerity_avg'): return None
    # 找真诚度比池均低 ≥3 分但仍上榜（=算法压但用户买）
    weakest = None
    weakest_d = 0
    for m in methods:
        algo = extract_algo(m, pool_id)
        if algo['sincerity'] is None: continue
        d = algo['sincerity'] - pool_av['sincerity_avg']
        if d < weakest_d:
            weakest_d = d
            weakest = m
    if weakest is None or weakest_d > -3: return None
    name = get(weakest, 'method_name', default='—')
    n = get(weakest, 'note_count', default=len(weakest.get('note_ids',[])))
    return f'⚡ <b>{escape(name)}</b>：算法真诚度比池均低 {abs(weakest_d):.1f} 分（系统判商业感强），但 {n} 条笔记仍跑进强信号池。说明用户买这套但算法不爱——适合短期收割，不适合长线人设。'

def render_insights_banner(pool_t, pool_v):
    """从两个池抓 key_insights 拼成横幅，没有就 fallback"""
    insights = []
    for pid in (pool_t, pool_v):
        c = clusters.get(pid, {})
        kis = c.get('key_insights', [])
        if kis:
            ins = kis[0]
        else:
            ins = fallback_insight_from_methods(pid)
        if not ins: continue
        label = POOL_LABEL_SHORT.get(pid, pid)
        insights.append(f'<div class="insight-card"><span class="insight-pool">{label} 池</span><div class="insight-text">{escape(str(ins))[:300]}</div></div>')
    if not insights:
        return ''
    return f'''<div class="insights-banner">
  <div class="insights-title">🔁 本周反直觉发现</div>
  <div class="insights-list">{''.join(insights)}</div>
</div>'''

# ============ 生成 8 个 _METHODS_T/V 字符串 ============
new_methods = {}
for tab_key, (pic_pool, vid_pool) in POOLS_BY_TAB.items():
    metric_type = tab_key  # ctr1/ctr2/cvr/price
    new_methods[f'{tab_key.upper()}_METHODS_T'] = render_pool_methods(pic_pool, metric_type)
    new_methods[f'{tab_key.upper()}_METHODS_V'] = render_pool_methods(vid_pool, metric_type)

# ============ 每个 Tab 自己池的"两套武器"框架卡 ============
def render_two_weapons_for_tab(tab_key, pic_pool, vid_pool):
    """根据池内方法的算法分，分长线/短线两组"""
    metric_label = {
        'ctr1': 'CTR1（封面+标题）',
        'ctr2': 'CTR2（商品卡点击）',
        'cvr': 'CVR（转化下单）',
        'price': '件单价（高客单）',
    }.get(tab_key, tab_key.upper())

    long_methods = []   # 长线（真诚度 ≥ +3）
    short_methods = []  # 短线（真诚度 ≤ -3）
    for pid in (pic_pool, vid_pool):
        c = clusters.get(pid, {})
        pool_av = pool_algo.get(pid, {})
        if not pool_av.get('sincerity_avg'): continue
        form_label = '图文' if pid.endswith('_pic') else '视频'
        for m in c.get('methods', []):
            algo = extract_algo(m, pid)
            if algo['sincerity'] is None: continue
            d = algo['sincerity'] - pool_av['sincerity_avg']
            name = get(m, 'method_name', default='—')
            note_count = get(m, 'note_count', default=len(m.get('note_ids',[])))
            entry = (d, name, form_label, note_count)
            if d >= 3:
                long_methods.append(entry)
            elif d <= -3:
                short_methods.append(entry)

    # 排序：长线按 sincerity_d desc，短线按 sincerity_d asc（最对立的在前）
    long_methods.sort(key=lambda x: -x[0])
    short_methods.sort(key=lambda x: x[0])

    def render_list(methods, max_n=6, kind='long'):
        if not methods:
            return '<li class="tw-empty">本指标池里暂无该类方法</li>'
        items = []
        for d, name, form, n in methods[:max_n]:
            tag = '🚀 推流加成' if kind == 'long' else '⚡ 算法不爱但用户买'
            items.append(f'<li>{escape(name)} <span class="tw-meta">·{form}·{n}条·{tag}</span></li>')
        return ''.join(items)

    long_html = render_list(long_methods, kind='long')
    short_html = render_list(short_methods, kind='short')

    # 兜底
    long_foot = '→ 算法长期给流量，做老客承接 / 品牌人设' if long_methods else '→ 本指标池里这类方法少见'
    short_foot = '→ 大促 / 库存清 / 季节末班车专用，别天天发' if short_methods else '→ 本指标池里没有"算法不爱但用户买"的方法'

    total_methods = len(clusters.get(pic_pool, {}).get('methods', [])) + len(clusters.get(vid_pool, {}).get('methods', []))
    return f'''<div class="two-weapons-banner">
  <div class="tw-title">🎯 {escape(metric_label)} 表现好的笔记里，有 2 种不同算法画像（共 {total_methods} 个方法）</div>
  <div class="tw-grid">
    <div class="tw-card tw-long">
      <div class="tw-head">🏛️ 可持续打法</div>
      <div class="tw-desc">读起来像真心分享，系统愿意持续给流量、不容易被压</div>
      <ul>{long_html}</ul>
      <div class="tw-foot">{long_foot}</div>
    </div>
    <div class="tw-card tw-short">
      <div class="tw-head">⚡ 短期收割打法</div>
      <div class="tw-desc">系统会判定"商业味重"，但用户的购买决策会被强力推一把</div>
      <ul>{short_html}</ul>
      <div class="tw-foot">{short_foot}</div>
    </div>
  </div>
  <div class="tw-tips">💡 <b>可持续打法</b>适合做长期人设和复购；<b>短期收割打法</b>适合大促/库存清/季节末班车，<b>但别天天用</b>——系统看到你模板化会压你的流量。两套打法都要会，分场景用。</div>
</div>'''

# ============ V9 额外 CSS（追加到 V8 之后）============
V9_EXTRA_CSS = '''
.method-card-v2 .method-count { color:#999; font-weight:400; font-size:12px; }
.method-card-v2 .method-why { background:#fff5f0; border-left:3px solid #ff6b35; padding:8px 12px; font-size:12px; color:#5a3220; line-height:1.6; margin-bottom:8px; border-radius:0 4px 4px 0; }
.method-card-v2 .method-meta { display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px; font-size:11px; color:#888; }
.method-cats { font-size:11px; color:#888; }
.algo-tags { display:flex; flex-wrap:wrap; gap:4px; }
.algo-tag { display:inline-block; padding:2px 6px; border-radius:3px; font-size:11px; font-weight:500; }
.algo-good { background:#e8f5e9; color:#2e7d32; }
.algo-warn { background:#fff3e0; color:#e65100; }
.inline-case-row .ic-hl { color:#666; font-style:normal; }

.two-weapons-banner { background:linear-gradient(135deg,#fff9f5,#f5f9ff); border:1px solid #ffd8c0; border-radius:12px; padding:18px 20px; margin:14px 0 22px; }
.tw-title { font-size:15px; font-weight:700; color:#d84315; margin-bottom:14px; }
.tw-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.tw-card { background:white; border-radius:10px; padding:14px; border:1px solid #f0f0f0; }
.tw-card.tw-long { border-top:3px solid #16a34a; }
.tw-card.tw-short { border-top:3px solid #ff6b35; }
.tw-head { font-weight:700; font-size:14px; margin-bottom:4px; color:#222; }
.tw-desc { font-size:12px; color:#777; margin-bottom:8px; }
.tw-card ul { list-style:none; padding:0; margin:0 0 8px; }
.tw-card li { font-size:13px; color:#333; padding:3px 0; }
.tw-card li .tw-meta { font-size:11px; color:#999; margin-left:4px; }
.tw-card li.tw-empty { color:#bbb; font-style:italic; font-size:12px; }
.tw-foot { font-size:11px; color:#888; padding-top:8px; border-top:1px dashed #eee; }
.tw-tips { margin-top:12px; padding:10px 12px; background:#fffbf0; border-left:3px solid #f5b800; border-radius:0 4px 4px 0; font-size:12px; color:#5d4a1f; line-height:1.5; }
@media (max-width:768px) { .tw-grid { grid-template-columns:1fr; } }

.insights-banner { background:#fffbf0; border:1px solid #ffe9b3; border-radius:10px; padding:14px 16px; margin:14px 0 18px; }
.insights-title { font-size:14px; font-weight:700; color:#b8860b; margin-bottom:10px; }
.insights-list { display:flex; flex-direction:column; gap:8px; }
.insight-card { background:white; border-radius:6px; padding:10px 12px; border:1px solid #f5e5b0; display:flex; flex-direction:column; gap:4px; }
.insight-pool { font-size:11px; color:#999; font-weight:600; }
.insight-text { font-size:12px; color:#444; line-height:1.6; }

.empty-pool { padding:24px; text-align:center; color:#999; font-size:13px; background:#fafafa; border-radius:8px; }
'''

# ============ Monkey-patch build_v8_gpm 并执行 ============
spec = importlib.util.spec_from_file_location('build_v8_gpm', os.path.join(WORKDIR, 'build_v8_gpm.py'))
mod = importlib.util.module_from_spec(spec)

# 在执行前预先注入 V9 方法字符串和 CSS
# build_v8_gpm 是 top-level script，import 后会直接执行
# 我们用变通做法：先读源码，把 8 个 _METHODS_T/V 变量重写
src = open(os.path.join(WORKDIR, 'build_v8_gpm.py'), encoding='utf-8').read()

# 替换 8 个方法字符串变量
for var_name, html in new_methods.items():
    # 找到 CTR1_METHODS_T = '...' 这种行
    import re
    pattern = rf"^{var_name}\s*=\s*'.*?'$"
    # 用 repr 输出安全的 python 字符串字面量（处理换行/引号）
    safe_literal = repr(html)
    replacement_text = f"{var_name} = {safe_literal}"
    # 用 lambda 避开 re 替换字符串的 \1/\g/\u 解释
    new_src, n = re.subn(pattern, lambda m: replacement_text, src, flags=re.MULTILINE)
    if n != 1:
        # 兜底：用更宽松的匹配（首行+尾行）
        # 处理跨行字符串（单引号 + 内容到下一个 NAME = '）
        pattern2 = rf"({var_name}\s*=\s*')(.*?)('\s*\n)"
        new_src, n = re.subn(pattern2, lambda m: f'{var_name} = {safe_literal}\n', src, count=1, flags=re.DOTALL)
        if n != 1:
            print(f'❌ 未能替换 {var_name}（n={n}）')
            sys.exit(1)
    src = new_src
    print(f'✅ 替换 {var_name}（{len(html)} chars）')

# 在 funnel_tab 函数定义里，把 hero-sub 改成包含 placeholders + insights
# 找到 'methods-grid' 之前注入
old_hero_block = '''  <div class="section-label">🎯 行业参考值（对照你的笔记后台数据）</div>'''
new_hero_block_template = '''  __V9_TWO_WEAPONS_PLACEHOLDER__
  __V9_INSIGHTS_PLACEHOLDER__
  <div class="section-label">🎯 行业参考值（对照你的笔记后台数据）</div>'''

# 简单做法：直接 patch funnel_tab 函数体
src = src.replace(old_hero_block, new_hero_block_template)

# === P0：话术降级 - 把"提升 X" 改成"X 表现好的笔记长什么样" + 加诚实标注 ===
tab_title_rewrites = [
    ("funnel_tab('ctr1', '👆', '提升 CTR1：封面+标题钩子'",
     "funnel_tab('ctr1', '📈', 'CTR1（封面+标题点击）表现好的笔记长什么样'"),
    ("funnel_tab('ctr2', '🔗', '提升 CTR2：商品卡点击'",
     "funnel_tab('ctr2', '📈', 'CTR2（商品卡点击）表现好的笔记长什么样'"),
    ("funnel_tab('cvr',  '💰', '提升 CVR：转化下单'",
     "funnel_tab('cvr',  '📈', 'CVR（下单转化）表现好的笔记长什么样'"),
    ("funnel_tab('price','💎', '提升件单价：客单优化'",
     "funnel_tab('price','📈', '件单价表现好的笔记长什么样'"),
]
for old, new in tab_title_rewrites:
    if old in src:
        src = src.replace(old, new)
        print(f'✅ 重写 Tab 标题: {old[18:40]}...')
    else:
        print(f'⚠️ 未命中标题改写：{old[:30]}')

# 把副标题"方法论 + 本周休食案例（数据驱动，非唯一答案）" 改诚实
old_meta = '<p class="meta">方法论 + 本周休食案例（数据驱动，非唯一答案）</p>'
new_meta = '<p class="meta">⚠️ 这是从高 GMV 笔记里聚类出的相关性画像，不是因果证明。仅作为内容方向参考，不保证按此改一定提升该指标</p>'
src = src.replace(old_meta, new_meta)

# 把 tips-box 那句"找到适合你品类的方向，仿写标题或封面策略"也降级
old_tips = '<strong>💡 怎么用：</strong> 每条方法下有 2 个本周真实案例。找到适合你品类的方向，仿写标题或封面策略。方法没有优先级，哪个适合你的产品就用哪个。'
new_tips = '<strong>💡 怎么用：</strong> 每条方法下有 2 个本周真实案例，是该指标表现好的笔记里聚类出的写法规律。<b>注意</b>：这是相关性，不是因果——同一批笔记同时高 GMV、高 CTR/CVR，方法论可能跨指标重叠。建议优先看你品类的案例，不要硬抄跨品类。'
src = src.replace(old_tips, new_tips)

# 写一个临时 build 脚本，先 import 改后的 v8 模块；用 exec 避免重复 IO
TMP_BUILD = os.path.join(WORKDIR, '_build_v8_patched_tmp.py')
open(TMP_BUILD, 'w', encoding='utf-8').write(src)

# 把 TWO_WEAPONS 和 insights 注入做成 placeholder 替换
# 我们用 monkey-patch funnel_tab 的 return 字符串
# 改为：在生成完整 HTML 后做后置替换

# 用 importlib + 修改源 + exec
ns = {'__file__': TMP_BUILD, '__name__': '__main__'}
exec(compile(src, TMP_BUILD, 'exec'), ns)

# 此时 ns 里已经生成了 index.html
# 但 placeholder 还在，我们直接读取生成的 index.html 做后置替换
out_path = os.path.join(WORKDIR, 'index.html')
with open(out_path, encoding='utf-8') as f:
    html = f.read()

# 按 tab 各自替换 two-weapons 和 insights placeholder
# funnel_tab 按 ctr1 → ctr2 → cvr → price 顺序生成 4 个 Tab，placeholder 依次出现
import re as _re
for tab_key, (pic_pool, vid_pool) in POOLS_BY_TAB.items():
    two_weapons_html = render_two_weapons_for_tab(tab_key, pic_pool, vid_pool)
    insights_html = render_insights_banner(pic_pool, vid_pool)
    # 替换第一个出现的占位符
    html = html.replace('__V9_TWO_WEAPONS_PLACEHOLDER__', two_weapons_html, 1)
    html = html.replace('__V9_INSIGHTS_PLACEHOLDER__', insights_html, 1)

# 追加 V9 额外 CSS
# 找 </style> 标签前注入
html = html.replace('</style>', V9_EXTRA_CSS + '\n</style>', 1)

# 写回
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 清理临时文件
os.remove(TMP_BUILD)

# ============ 自检 ============
import re as _re
n_panel = len(_re.findall(r'class="tab-panel', html))
n_method_v9 = len(_re.findall(r'class="method-card-v2"', html))
n_two_weapons = len(_re.findall(r'two-weapons-banner', html))
n_placeholder = len(_re.findall(r'__V9_', html))

print(f'\n=== V9 build 自检 ===')
print(f'tab-panel 数量：{n_panel}（预期 8）')
print(f'V9 method-card 数量：{n_method_v9}（预期 40，8 池 × 5 方法）')
print(f'two-weapons-banner 数量：{n_two_weapons}（预期 4）')
print(f'未替换的 V9 placeholder：{n_placeholder}（预期 0）')

if n_panel != 8:
    print('❌ tab-panel 数量异常'); sys.exit(1)
if n_method_v9 < 35:
    print(f'❌ V9 method-card 数量过低 ({n_method_v9})'); sys.exit(1)
if n_placeholder != 0:
    print(f'❌ 还有 {n_placeholder} 个未替换的 placeholder'); sys.exit(1)

print(f'\n✅ V9 build 完成，写入 {out_path} ({len(html):,} chars)')
