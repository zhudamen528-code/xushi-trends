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

# 加载 V10 差分聚类结果
V10_DIFF = {}
for m in ['ctr1', 'ctr2', 'cvr', 'price']:
    V10_DIFF[m] = json.load(open(os.path.join(WORKDIR, f'data/v10_clusters/{m}.diff.json'), encoding='utf-8'))

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
    
    ex_html = ''.join(f'<li>{escape(e)}</li>' for e in examples[:4])
    co_html = ''.join(f'<li>{escape(e)}</li>' for e in contrast[:2])
    
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
    
    ex_html = ''.join(f'<li>{escape(e)}</li>' for e in examples[:4])
    co_html = ''.join(f'<li>{escape(e)}</li>' for e in contrast[:2])
    
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

def render_v10_section(metric_key, metric_label):
    diff = V10_DIFF.get(metric_key, {})
    high_patterns = diff.get('high_only_patterns', [])
    low_patterns = diff.get('low_only_patterns', [])
    mechanism = diff.get('key_mechanism', '')
    
    high_html = ''.join(render_high_card(p, i) for i, p in enumerate(high_patterns))
    low_html = ''.join(render_low_card(p, i) for i, p in enumerate(low_patterns))
    
    return f'''<div class="v10-section">
  <div class="v10-banner">
    <div class="v10-banner-title">🔬 {escape(metric_label)} 高 vs 低对照差分聚类（V10 新增）</div>
    <div class="v10-banner-sub">按类目内 P75 vs P25 严格切高低对照组，找出"高组独有 / 低组陷阱"写法。<b>这是相关性证据，不是因果，但样本量足够、类目变量已控住</b>。</div>
  </div>
  
  {f'<div class="v10-mechanism">💎 <b>核心机制</b>：{escape(mechanism)}</div>' if mechanism else ''}
  
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

for metric_key in ['ctr1', 'ctr2', 'cvr', 'price']:
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
