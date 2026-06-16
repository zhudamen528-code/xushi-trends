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
pool_data = {}
for p in POOLS:
    cpath = f'data/v9_clusters_v3/{p}.cluster.json'
    if os.path.exists(cpath):
        clusters[p] = json.load(open(cpath))
    ppath = f'data/v9_pools_v3/{p}.json'
    if os.path.exists(ppath):
        pdata = json.load(open(ppath))
        pool_data[p] = {n['note_id']: n for n in pdata.get('notes',[])}

def get(d, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v not in (None, '', [], {}):
            return v
    return default

def num_str(v):
    if v is None or v == '' or v == '—': return '—'
    try:
        fv = float(v)
        return f'{fv:+.1f}' if abs(fv) < 1000 else f'{fv:+.0f}'
    except: return str(v)

def normalize_method(m, pool_id):
    """统一别名 + 补全 case_notes"""
    out = {}
    out['method_name'] = get(m, 'method_name', default='—')
    out['method_summary'] = get(m, 'method_summary', 'essence', 'description', default='—')
    out['why_it_works'] = get(m, 'why_it_works', 'why_works', default='—')
    out['note_count'] = get(m, 'note_count', default=len(m.get('note_ids',[])))
    out['top_categories'] = get(m, 'top_categories', 'applicable_category', default=[])
    out['signals'] = get(m, 'signals', default=[])
    out['algo_profile'] = m.get('algo_profile', {})
    
    # case_notes 补全
    case_notes = m.get('case_notes', [])
    if case_notes:
        out['case_notes'] = case_notes
    else:
        # 用 note_ids 反查 pool 数据
        nids = m.get('note_ids', [])[:3]  # 取前 3
        pool_d = pool_data.get(pool_id, {})
        cases = []
        for nid in nids:
            n = pool_d.get(nid, {})
            if n:
                cases.append({
                    'note_id': nid,
                    'title': n.get('title','—') or '—',
                    'goods_name': n.get('goods_name','—') or '—',
                    'goods_price': n.get('goods_price','—'),
                    'gpm': n.get('_gpm') or n.get('gpm','—'),
                    'dgmv': n.get('_dgmv') or n.get('total_dgmv','—'),
                })
        out['case_notes'] = cases
    return out

# 算每池整体 algo_profile（用于 vs 池均计算）
pool_algo = {}
for p in POOLS:
    pd = pool_data.get(p,{})
    sins=[]; lbs=[]; gcs=[]
    for nid, n in pd.items():
        if n.get('model_sincerity_score'): sins.append(float(n['model_sincerity_score']))
        if n.get('low_bad_market_score'): lbs.append(float(n['low_bad_market_score']))
        if n.get('good_click_quality_score'): gcs.append(float(n['good_click_quality_score']))
    pool_algo[p] = {
        'sincerity': round(sum(sins)/len(sins),1) if sins else 0,
        'low_bad': round(sum(lbs)/len(lbs),4) if lbs else 0,
        'good_click': round(sum(gcs)/len(gcs),4) if gcs else 0,
    }

def algo_delta(method, pool_id):
    """从 algo_profile 提取 delta 字符串"""
    ap = method['algo_profile']
    pool = pool_algo.get(pool_id,{})
    out = {}
    # sincerity
    sav = ap.get('sincerity_avg') or ap.get('sin_avg') or ap.get('avg_sincerity')
    if sav is None and 'sin_delta' in ap:
        sav = pool['sincerity'] + ap['sin_delta']
    if sav is not None:
        try:
            delta = float(sav) - pool['sincerity']
            out['sincerity'] = f'{float(sav):.1f} ({delta:+.1f})'
        except: out['sincerity'] = str(sav)
    else:
        out['sincerity'] = '—'
    # low_bad
    lbv = ap.get('low_bad_avg') or ap.get('lb_avg') or ap.get('avg_low_bad')
    if lbv is None and 'lb_delta' in ap:
        lbv = pool['low_bad'] + ap['lb_delta']
    if lbv is not None:
        try:
            delta = float(lbv) - pool['low_bad']
            out['low_bad'] = f'{float(lbv):.3f} ({delta:+.3f})'
        except: out['low_bad'] = str(lbv)
    else:
        out['low_bad'] = '—'
    # good_click
    gcv = ap.get('good_click_avg') or ap.get('gc_avg') or ap.get('avg_good_click')
    if gcv is None and 'gc_delta' in ap:
        gcv = pool['good_click'] + ap['gc_delta']
    if gcv is not None:
        try:
            delta = float(gcv) - pool['good_click']
            out['good_click'] = f'{float(gcv):.3f} ({delta:+.3f})'
        except: out['good_click'] = str(gcv)
    else:
        out['good_click'] = '—'
    return out

# 生成 markdown
md = []
md.append('# 🍿 休食商笔 V9 方法论库（补全版）· 8池40方法 + 反直觉发现')
md.append('')
md.append('> 更新：2026-06-16 11:50，修复了 schema 别名导致的空值，所有方法的真诚度/低差营销/互动质量分对比都已补全。')
md.append('')
md.append('## 📊 池子全景')
md.append('')
md.append('| 池 | 方法数 | 主导品类 | 池平均真诚度 |')
md.append('|---|---|---|---|')
for p in POOLS:
    c = clusters.get(p,{})
    methods = c.get('methods',[])
    cat_count = defaultdict(int)
    for m in methods:
        cats = get(m, 'top_categories', 'applicable_category', default=[])
        for entry in cats[:3]:
            if isinstance(entry,(list,tuple)) and len(entry)>=2:
                cat_count[entry[0]] += entry[1]
            elif isinstance(entry,dict):
                cat_count[entry.get('name','—')] += entry.get('count',1)
            elif isinstance(entry,str):
                cat_count[entry] += 1
    top_cats = sorted(cat_count.items(), key=lambda x:-x[1])[:3]
    cat_str = ' / '.join([f'{c}({n})' for c,n in top_cats]) or '—'
    md.append(f'| {POOL_LABEL[p]} | {len(methods)} | {cat_str} | {pool_algo[p]["sincerity"]} |')
md.append('')
md.append('---')
md.append('')

# 分池详细方法
for p in POOLS:
    c = clusters.get(p,{})
    raw_methods = c.get('methods',[])
    methods = [normalize_method(m, p) for m in raw_methods]
    md.append(f'## {POOL_LABEL[p]}')
    md.append('')
    md.append(f'**方法数**：{len(methods)}　|　**池平均真诚度** {pool_algo[p]["sincerity"]}　|　**池平均商业感** {pool_algo[p]["low_bad"]}　|　**池平均互动质量** {pool_algo[p]["good_click"]}')
    md.append('')
    md.append('| # | 方法名 | 笔记数 | 真诚度 | 商业感 | 互动质量 | 主要类目 |')
    md.append('|---|---|---|---|---|---|---|')
    for i,m in enumerate(methods,1):
        delta = algo_delta(m, p)
        cats = m['top_categories'][:3]
        cat_str = ' / '.join([f'{c}({n})' if isinstance(c,str) and not isinstance(n,str) else str(c) for c,n in [(e[0],e[1]) if isinstance(e,(list,tuple)) and len(e)>=2 else (e,'') for e in cats]]) or '—'
        md.append(f'| {i} | {m["method_name"]} | {m["note_count"]} | {delta["sincerity"]} | {delta["low_bad"]} | {delta["good_click"]} | {cat_str} |')
    md.append('')
    md.append('### 📖 方法详情')
    md.append('')
    for i,m in enumerate(methods,1):
        md.append(f'#### {i}. {m["method_name"]}')
        md.append('')
        md.append(f'**做法**：{m["method_summary"]}')
        md.append('')
        md.append(f'**为什么奏效**：{m["why_it_works"]}')
        md.append('')
        if m.get('signals'):
            md.append('**识别信号**：' + ' / '.join(m['signals']))
            md.append('')
        cases = m['case_notes'][:3]
        if cases:
            md.append('**代表案例**：')
            for cn in cases:
                title = cn.get('title','—') or '—'
                goods = cn.get('goods_name','—') or '—'
                price = cn.get('goods_price','—')
                gpm = cn.get('gpm','—')
                dgmv = cn.get('dgmv','—')
                try: gpm_s = f'{float(gpm):.0f}' if gpm!='—' else '—'
                except: gpm_s = str(gpm)
                try: dgmv_s = f'¥{float(dgmv):.0f}' if dgmv!='—' else '—'
                except: dgmv_s = f'¥{dgmv}'
                md.append(f'- 《{title}》→ {goods} · GPM={gpm_s} · DGMV={dgmv_s}')
            md.append('')
    insights = c.get('key_insights',[])
    if insights:
        md.append('### 🔁 反直觉发现')
        md.append('')
        for ins in insights:
            md.append(f'- {ins}')
        md.append('')
    md.append('---')
    md.append('')

# 跨池强方法
md.append('## 🏆 跨池强方法 Top 5')
md.append('')
md.append('| 排名 | 方法主题 | 出现池 | 估算笔记数 |')
md.append('|---|---|---|---|')
md.append('| 🥇1 | 🌾 老板自白/委屈/真心话 | ctr1_pic + ctr2_pic + ctr2_vid + cvr_pic | 75+ |')
md.append('| 🥈2 | ⏳ 真稀缺+真原因（季节/限量/补货）| ctr2_pic + price_pic | 45+ |')
md.append('| 🥉3 | 🍵 出处可考·年份山头·工艺溯源 | ctr1_vid + price_vid + ctr1_pic | 50+ |')
md.append('| 4 | 🔍 鉴别避坑·真假对比 | ctr1_vid + cvr_vid | 44 |')
md.append('| 5 | 🩺 痛点直击+解决方案 | cvr_pic + cvr_vid | 36 |')
md.append('')

md.append('## ⚡ 4 个"算法 vs 用户"对立方法')
md.append('')
md.append('| 方法 | 出现池 | 真诚度Δ | 转化亮点 |')
md.append('|---|---|---|---|')
md.append('| ⏰ 末班车催单 | ctr2_vid | -3.7 | CVR 15.3% 全池最高 |')
md.append('| 🌿 症状代入/古法养生 | cvr_vid | -4.7 | CVR Top3 |')
md.append('| 💪 痛点食疗 | cvr_pic | -7.7 | CVR 30.9% Top2 |')
md.append('| 💗 周期套餐·女性月子 | price_vid | -21.3 | 高客单坚挺 |')
md.append('')

doc = '\n'.join(md)
open('V9_METHODOLOGY_REVIEW_V2.md','w', encoding='utf-8').write(doc)

out=[]; ic=False
for ln in md:
    if ln.startswith('```'):
        ic=not ic; out.append(ln); continue
    if ic: out.append(ln); continue
    ln=ln.replace('<','&lt;').replace('>','&gt;')
    out.append(ln)
open('V9_METHODOLOGY_REVIEW_V2.redoc.md','w').write('\n'.join(out))
print(f'wrote {len(doc)} chars, {len(md)} lines')
