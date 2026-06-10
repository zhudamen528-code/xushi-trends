#!/usr/bin/env python3
"""
Layout V7: 左右分栏布局
- 左侧 220px 固定侧边栏：品类筛选 + 分区跳转
- 右侧主内容区，间距充裕
- Tab1 品类风向文字大幅精简（只留最强公式1句话）
- Tab 导航改为顶部全宽横条（紧贴 hero 下）
"""

content = open('index.html').read()

# ══════════════════════════════════════════════════════════════
# 1. 把 container 里的 tab-nav 和 tab-panels 重构为侧边栏布局
#    原结构: <div class="container">  <div class="tab-nav"> ...  <div id="tab-trends"> ...
#    新结构: tab-nav 移到 hero 下独立全宽；container 内变为 sidebar + main
# ══════════════════════════════════════════════════════════════

# 找 container 开始和 tab-nav
container_start = content.find('<div class="container">')
tabnav_start = content.find('<div class="tab-nav">', container_start)
tabnav_end = content.find('</div>', tabnav_start) + 6  # 闭合 tab-nav div

# 找 tab-trends panel 开始
trends_start = content.find('<div class="tab-panel', tabnav_end)

# 找最后一个 tab-panel 结束（在 script 前）
script_start = content.rfind('<script async src="//busuanzi')
# 找 footer div（在 script_start 前）
footer_start = content.rfind('<div style="text-align:center', 0, script_start)
# 所有 tab-panels 到 footer_start 之间
panels_block = content[trends_start:footer_start]

# tab-nav HTML
tabnav_html = content[tabnav_start:tabnav_end]

print(f'container_start={container_start}, tabnav={tabnav_start}~{tabnav_end}')
print(f'trends_start={trends_start}, footer_start={footer_start}')
print(f'panels_block len={len(panels_block)}')

# ══════════════════════════════════════════════════════════════
# 2. 精简 Tab1 品类风向卡（5列 → 压缩每列文字）
#    trend-dirs 里每条 trend-dir 只保留前60字+数据
#    实际：直接在 panels_block 里替换 trend-dirs 区块
# ══════════════════════════════════════════════════════════════

# 用精简版替换 5列 trend-grid 里的 trend-dirs 内容
# 策略：每个 trend-dir 的 <span> 内容截取到第一个"；"或"，"后约50字，
#       保留数据标签。用 regex 处理

import re

def shorten_trend_dir(match):
    """把 trend-dir 内的长 span 文字缩短到约60字"""
    full = match.group(0)
    # 找 <span> 内容（第二个span，也就是文字部分）
    spans = re.findall(r'<span>(.*?)</span>', full, re.DOTALL)
    if len(spans) >= 2:
        text = spans[1]
        # 截断：找第一个"；"或"，"在50字后
        short = text
        for sep in ['；', '，', '，']:
            idx = text.find(sep, 30)
            if 30 < idx < 80:
                short = text[:idx]
                break
        else:
            short = text[:70] + ('…' if len(text) > 70 else '')
        full = full.replace(f'<span>{text}</span>', f'<span>{short}</span>')
    return full

panels_block_new = re.sub(
    r'<div class="trend-dir">.*?</div>',
    shorten_trend_dir,
    panels_block,
    flags=re.DOTALL
)
print(f'panels_block after shorten: {len(panels_block_new)} bytes')

# ══════════════════════════════════════════════════════════════
# 3. 拼接新结构
# ══════════════════════════════════════════════════════════════

SIDEBAR_HTML = '''<div class="sidebar">
  <div class="sidebar-section">
    <div class="sidebar-label">品类筛选</div>
    <div class="sidebar-cats">
      <button class="sidebar-cat active" onclick="filterCat('all',this)">🍱 全部</button>
      <button class="sidebar-cat" onclick="filterCat('snack',this)">🍿 零食</button>
      <button class="sidebar-cat" onclick="filterCat('fast',this)">🍜 速食</button>
      <button class="sidebar-cat" onclick="filterCat('drink',this)">🧋 饮品</button>
      <button class="sidebar-cat" onclick="filterCat('liquor',this)">🍵 茶/酒</button>
      <button class="sidebar-cat" onclick="filterCat('herb',this)">🌿 滋补</button>
    </div>
  </div>
  <div class="sidebar-section">
    <div class="sidebar-label">快速跳转</div>
    <div class="sidebar-navs">
      <a class="sidebar-nav" href="#sec-trends">🧭 本周风向</a>
      <a class="sidebar-nav" href="#sec-formula">✍️ 标题公式</a>
      <a class="sidebar-nav" href="#sec-topics">🔥 热点话题</a>
      <a class="sidebar-nav" href="#sec-cats">📦 品类动向</a>
      <a class="sidebar-nav" href="#sec-top">🏆 TOP 笔记</a>
    </div>
  </div>
  <div class="sidebar-section">
    <div class="sidebar-label">本周数据</div>
    <div class="sidebar-kpi">
      <div class="sidebar-kpi-row"><span>最高封面CTR</span><strong>39%</strong></div>
      <div class="sidebar-kpi-row"><span>最高商卡CTR</span><strong>88.6%</strong></div>
      <div class="sidebar-kpi-row"><span>最高单篇曝光</span><strong>83万+</strong></div>
    </div>
  </div>
</div>'''

# 重组 container 内部
NEW_CONTAINER_INNER = f'''
  {tabnav_html}

  <div class="main-layout">
    {SIDEBAR_HTML}
    <div class="main-content">
      {panels_block_new}
    </div>
  </div>

'''

# 重建完整 content
before_container = content[:container_start]
after_panels = content[footer_start:]

new_content = (
    before_container
    + '<div class="container">\n'
    + NEW_CONTAINER_INNER
    + after_panels
)

print(f'new_content len={len(new_content)}')

# ══════════════════════════════════════════════════════════════
# 4. 注入 CSS（sidebar 布局 + 精简版 trend-card）
# ══════════════════════════════════════════════════════════════

SIDEBAR_CSS = '''
/* ── SIDEBAR LAYOUT ── */
.main-layout {
  display: flex;
  gap: 28px;
  align-items: flex-start;
  margin-top: 24px;
}
.sidebar {
  width: 200px;
  flex-shrink: 0;
  position: sticky;
  top: 120px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.main-content { flex: 1; min-width: 0; }

.sidebar-section {}
.sidebar-label {
  font-size: 10px;
  font-weight: 800;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 8px;
}
.sidebar-cats {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sidebar-cat {
  display: flex;
  align-items: center;
  padding: 9px 12px;
  border-radius: var(--r10);
  border: 1.5px solid var(--border);
  background: var(--card);
  color: var(--text2);
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: all .15s;
  gap: 6px;
}
.sidebar-cat:hover { background: var(--red-soft); color: var(--red); border-color: var(--red-mid); }
.sidebar-cat.active { background: var(--red); color: #fff; border-color: var(--red); }

.sidebar-navs {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sidebar-nav {
  display: block;
  padding: 8px 10px;
  border-radius: var(--r6);
  font-size: 12px;
  font-weight: 500;
  color: var(--text2);
  text-decoration: none;
  transition: background .12s, color .12s;
}
.sidebar-nav:hover { background: var(--bg); color: var(--red); }

.sidebar-kpi { display: flex; flex-direction: column; gap: 6px; }
.sidebar-kpi-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 7px 10px;
  border-radius: var(--r6);
  background: var(--bg);
  font-size: 12px;
}
.sidebar-kpi-row span { color: var(--text2); }
.sidebar-kpi-row strong { color: var(--red); font-weight: 800; font-size: 13px; }

/* ── trend-card 精简版 ── */
.trend-dirs { display: flex; flex-direction: column; }
.trend-dir {
  display: flex;
  gap: 8px;
  padding: 9px 14px;
  border-bottom: 1px solid var(--border2);
  font-size: 12px;
  line-height: 1.5;
  color: var(--text);
  align-items: flex-start;
}
.trend-dir:last-child { border-bottom: none; }
.trend-dir .trend-num { flex-shrink: 0; }
.trend-dir > span:last-child { flex: 1; }

/* section anchors */
#sec-trends, #sec-formula, #sec-topics, #sec-cats, #sec-top {
  scroll-margin-top: 120px;
}

/* mobile: 隐藏 sidebar */
@media (max-width: 900px) {
  .main-layout { flex-direction: column; }
  .sidebar { width: 100%; position: static; flex-direction: row; flex-wrap: wrap; gap: 10px; }
  .sidebar-section { flex: 1; min-width: 140px; }
  .sidebar-cats { flex-direction: row; flex-wrap: wrap; }
  .sidebar-cat { padding: 7px 10px; font-size: 12px; }
}
'''

# 注入到第二个 </style> 前
second_style_end = new_content.rfind('</style>')
new_content = new_content[:second_style_end] + SIDEBAR_CSS + '\n' + new_content[second_style_end:]
print('✅ Sidebar CSS 注入')

# ══════════════════════════════════════════════════════════════
# 5. 给 Tab1 各 section 加锚点 id
# ══════════════════════════════════════════════════════════════
new_content = new_content.replace(
    '<span class="icon">🧭</span> 本周内容风向',
    '<span class="icon">🧭</span> <span id="sec-trends">本周内容风向</span>'
, 1)
new_content = new_content.replace(
    '<span class="icon">✍️</span> 本周标题公式',
    '<span class="icon">✍️</span> <span id="sec-formula">本周标题公式</span>'
, 1)
new_content = new_content.replace(
    '<span class="icon">🔥</span> 本周热点话题',
    '<span class="icon">🔥</span> <span id="sec-topics">本周热点话题</span>'
, 1)
new_content = new_content.replace(
    '<span class="icon">📦</span> 品类重点动向',
    '<span class="icon">📦</span> <span id="sec-cats">品类重点动向</span>'
, 1)
new_content = new_content.replace(
    '<span class="icon">🏆</span> 本周新发高表现笔记',
    '<span class="icon">🏆</span> <span id="sec-top">本周新发高表现笔记</span>'
, 1)
print('✅ 锚点注入')

# ══════════════════════════════════════════════════════════════
# 6. 注入品类筛选 JS
# ══════════════════════════════════════════════════════════════
FILTER_JS = '''
function filterCat(cat, btn) {
  document.querySelectorAll('.sidebar-cat').forEach(function(b){ b.classList.remove('active'); });
  btn.classList.add('active');
  var cards = document.querySelectorAll('.trend-card');
  cards.forEach(function(card) {
    var head = card.querySelector('.trend-head');
    if (cat === 'all') {
      card.style.opacity = '1';
      card.style.transform = 'none';
    } else if (head && head.classList.contains(cat)) {
      card.style.opacity = '1';
      card.style.transform = 'none';
    } else {
      card.style.opacity = '0.25';
      card.style.transform = 'scale(0.97)';
    }
  });
  var accItems = document.querySelectorAll('.acc-item');
  accItems.forEach(function(item) {
    var badge = item.querySelector('.acc-badge');
    if (cat === 'all') {
      item.style.opacity = '1';
    } else if (badge && badge.classList.contains(cat)) {
      item.style.opacity = '1';
    } else {
      item.style.opacity = '0.3';
    }
  });
}
'''

last_script_end = new_content.rfind('</script>')
new_content = new_content[:last_script_end] + FILTER_JS + new_content[last_script_end:]
print('✅ filterCat JS 注入')

# ══════════════════════════════════════════════════════════════
# 7. 校验
# ══════════════════════════════════════════════════════════════
opens  = new_content.count('<style>')
closes = new_content.count('</style>')
print(f'style tags: {opens} ↔ {closes}')
assert opens == closes, 'style 不平衡'

open('index.html', 'w').write(new_content)
print(f'✅ 写入 {len(new_content)} bytes')
