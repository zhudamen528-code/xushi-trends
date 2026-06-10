#!/usr/bin/env python3
"""V8 GPM 漏斗工具 - 完整构建脚本"""
import json, os, re, sys
from datetime import datetime

WORKDIR = os.path.dirname(os.path.abspath(__file__))
V7_PATH = os.path.join(WORKDIR, 'index_v7_backup.html')
OUT_PATH = os.path.join(WORKDIR, 'index.html')
DATA_PATH = os.path.join(WORKDIR, 'data.json')

# ============ 工具函数 ============
def fmt_pct(v, decimals=1):
    if v is None: return '—'
    return f"{v*100:.{decimals}f}%"

def fmt_money(v):
    if v is None: return '—'
    return f"¥{v:.0f}"

def escape(s):
    if s is None: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

# ============ 读数据 ============
with open(DATA_PATH) as f:
    data = json.load(f)
xushi_t = data['p75'].get('休食', {}).get('图文', {})
xushi_v = data['p75'].get('休食', {}).get('视频', {})
ka_t = data['p75'].get('ka_avg', {}).get('图文', {})
ka_v = data['p75'].get('ka_avg', {}).get('视频', {})
cases = data.get('top_cases', {})

with open(V7_PATH) as f:
    v7 = f.read()

# ============ Tab nav HTML ============
NEW_NAV = '''<div class="tab-nav">
    <button class="tab-btn active" onclick="switchTab(event,'gpm')">📊 GPM 总览</button>
    <button class="tab-btn" onclick="switchTab(event,'ctr1')">👆 CTR1 封面</button>
    <button class="tab-btn" onclick="switchTab(event,'ctr2')">🔗 CTR2 商品卡</button>
    <button class="tab-btn" onclick="switchTab(event,'cvr')">💰 CVR 转化</button>
    <button class="tab-btn" onclick="switchTab(event,'price')">💎 件单价</button>
    <button class="tab-btn" onclick="switchTab(event,'audit')">🚦 违规预审</button>
    <button class="tab-btn" onclick="switchTab(event,'tools')">🛠️ 我的参考</button>
  </div>'''

# ============ KPI 卡片 ============
def kpi_card(title, p50, p75, ka_p75=None, pct=True):
    fmt = fmt_pct if pct else fmt_money
    ka_html = f'<div class="kpi-ka">KA 大盘 P75：{fmt(ka_p75)}</div>' if ka_p75 is not None else ''
    return f'''<div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{fmt(p75)}</div>
      <div class="kpi-sub">优秀线 P75 · 中位 P50 {fmt(p50)}</div>
      {ka_html}
    </div>'''

# ============ Tab1 GPM 总览 ============
TAB1 = f'''<div class="tab-panel" id="tab-gpm">
  <div class="hero">
    <h2>📊 GPM 漏斗 · 本周大盘</h2>
    <p class="meta">数据窗口：{data['window'][0]} 至 {data['window'][1]} · 更新 {data['updated_at']}</p>
    <div class="funnel-formula">
      <strong>GPM = CTR1 × CTR2 × CVR × 件单价</strong><br>
      笔记曝光 → <span class="step ctr1">👆 封面点击</span> → <span class="step ctr2">🔗 商品卡点击</span> → <span class="step cvr">💰 下单</span> → <span class="step price">💎 客单价</span>
    </div>
  </div>

  <div class="section-label">📈 休食 · 图文</div>
  <div class="kpi-grid">
    {kpi_card("CTR1 封面点击率", xushi_t.get('ctr1_p50'), xushi_t.get('ctr1_p75'), ka_t.get('ctr1_p75'))}
    {kpi_card("CTR2 商品卡点击率", xushi_t.get('ctr2_p50'), xushi_t.get('ctr2_p75'), ka_t.get('ctr2_p75'))}
    {kpi_card("CVR 转化率", xushi_t.get('cvr_p50'), xushi_t.get('cvr_p75'), ka_t.get('cvr_p75'))}
    {kpi_card("件单价", xushi_t.get('price_p50'), xushi_t.get('price_p75'), ka_t.get('price_p75'), pct=False)}
  </div>

  <div class="section-label">🎬 休食 · 视频</div>
  <div class="kpi-grid">
    {kpi_card("CTR1 封面点击率", xushi_v.get('ctr1_p50'), xushi_v.get('ctr1_p75'), ka_v.get('ctr1_p75'))}
    {kpi_card("CTR2 商品卡点击率", xushi_v.get('ctr2_p50'), xushi_v.get('ctr2_p75'), ka_v.get('ctr2_p75'))}
    {kpi_card("CVR 转化率", xushi_v.get('cvr_p50'), xushi_v.get('cvr_p75'), ka_v.get('cvr_p75'))}
    {kpi_card("件单价", xushi_v.get('price_p50'), xushi_v.get('price_p75'), ka_v.get('price_p75'), pct=False)}
  </div>

  <div class="tips-box">
    <strong>💡 怎么看：</strong> P50 = 行业中位（一半笔记达到），P75 = 优秀线（前 25% 笔记）。比对自己笔记的数据，<strong>落后哪一环就先优化哪一环</strong>。点击上方 Tab 看每环节方法论 + 本周休食 TOP 案例。<br><br>
    <strong>KA 快消大盘</strong>包括：休食 + 大健康 + 生鲜 + 亲子生活 + 宠物 + 家用 共 6 个一级品类。
  </div>
</div>'''

# ============ 漏斗 Tab 内容（CTR1/CTR2/CVR/Price 通用模板） ============
def case_card(c, metric_type):
    """单个 TOP 案例卡片"""
    if metric_type == 'price':
        value_str = fmt_money(c['value'])
    else:
        value_str = fmt_pct(c['value'])
    highlight = c.get('highlight') or '—'
    return f'''<div class="case-card">
      <div class="case-rank">#{c['rank']}</div>
      <div class="case-body">
        <div class="case-title">{escape(c['title'])}</div>
        <div class="case-meta">
          <span class="case-metric">{value_str}</span>
          <span class="case-seller">{escape(c['seller_name'])}</span>
        </div>
        <div class="case-stats">曝光 {c['imp']:,} · 点击 {c['click']:,} · 下单 {c['buy']} · GMV ¥{c['dgmv']:.0f}</div>
        <div class="case-highlight">💡 {escape(highlight)}</div>
        <a class="case-link" href="{c['note_url']}" target="_blank">→ 看原文</a>
      </div>
    </div>'''

def funnel_tab(tab_id, icon, title, metric_key, methods_html, is_price=False):
    """生成一个漏斗 Tab 的完整 HTML"""
    pct = not is_price
    xushi_p50_t = xushi_t.get(f'{metric_key}_p50')
    xushi_p75_t = xushi_t.get(f'{metric_key}_p75')
    xushi_p50_v = xushi_v.get(f'{metric_key}_p50')
    xushi_p75_v = xushi_v.get(f'{metric_key}_p75')
    ka_p75_t = ka_t.get(f'{metric_key}_p75')
    ka_p75_v = ka_v.get(f'{metric_key}_p75')

    cases_t = cases.get(metric_key, {}).get('图文', [])
    cases_v = cases.get(metric_key, {}).get('视频', [])
    cases_t_html = ''.join(case_card(c, metric_key) for c in cases_t)
    cases_v_html = ''.join(case_card(c, metric_key) for c in cases_v)

    return f'''<div class="tab-panel hidden" id="tab-{tab_id}">
  <div class="hero hero-sub hero-{tab_id}">
    <h2>{icon} {title}</h2>
    <p class="meta">休食本周 · 优秀线 P75 + 本周 TOP 案例 + 多路径方法论</p>
  </div>

  <div class="section-label">🎯 本周大盘优秀线</div>
  <div class="kpi-grid kpi-grid-2col">
    <div class="kpi-card">
      <div class="kpi-title">📈 图文</div>
      <div class="kpi-value">{fmt_pct(xushi_p75_t) if pct else fmt_money(xushi_p75_t)}</div>
      <div class="kpi-sub">P75 优秀 · 中位 {fmt_pct(xushi_p50_t) if pct else fmt_money(xushi_p50_t)}</div>
      <div class="kpi-ka">KA 大盘 P75：{fmt_pct(ka_p75_t) if pct else fmt_money(ka_p75_t)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🎬 视频</div>
      <div class="kpi-value">{fmt_pct(xushi_p75_v) if pct else fmt_money(xushi_p75_v)}</div>
      <div class="kpi-sub">P75 优秀 · 中位 {fmt_pct(xushi_p50_v) if pct else fmt_money(xushi_p50_v)}</div>
      <div class="kpi-ka">KA 大盘 P75：{fmt_pct(ka_p75_v) if pct else fmt_money(ka_p75_v)}</div>
    </div>
  </div>

  <div class="section-label">📚 多路径方法论（不是唯一答案）</div>
  <div class="methods-grid">
    {methods_html}
  </div>

  <div class="section-label">🔥 本周休食 TOP 10 · 图文</div>
  <div class="case-grid">{cases_t_html}</div>

  <div class="section-label">🎥 本周休食 TOP 10 · 视频</div>
  <div class="case-grid">{cases_v_html}</div>

  <div class="tips-box">
    <strong>💡 怎么用：</strong> 看 TOP 案例的标题套路 + AI 亮点解析 → 找到适合你品类的 2-3 条路径 → 自己仿写。每周一更新 TOP 案例，多积累灵感库。
  </div>
</div>'''

# ============ 各 Tab 方法论卡片（多路径，引用 insight-v20） ============
def method_card(title, desc, source):
    return f'''<div class="method-card">
      <div class="method-title">{title}</div>
      <div class="method-desc">{desc}</div>
      <div class="method-source">来源：{source}</div>
    </div>'''

CTR1_METHODS = ''.join([
    method_card("📸 单主体+特写", "封面只放一个主体（产品/手部动作），剔除杂乱背景，CTR1 平均提升 30%", "诺亚漏斗洞察 insight-v20"),
    method_card("🔥 数字+反差词", '标题用"3个月"/"99%人都不知道"/"踩雷"等强钩子词，吸引点击', "creation-guide-v9 D2"),
    method_card("✋ 手部动作+使用场景", "封面有人手在拿/用产品，比纯产品图 CTR 高 2x（适合食品/护肤）", "诺亚漏斗洞察 insight-v20"),
    method_card("💬 痛点共鸣开头", '"打工人续命水" / "懒人福音" 类标题，精准触达需求', "creation-guide-v9 D5"),
    method_card("👀 信息量大的封面", "封面贴文字标签（价格/卖点/对比），用户秒懂内容价值", "诺亚漏斗洞察 insight-v20"),
])

CTR2_METHODS = ''.join([
    method_card("🏷️ 商品卡价格诱惑", '挂车价格<心理预期价位 → CTR2 显著高（如标"9.9 包邮"）', "creation-guide-v9 D8"),
    method_card("⏰ 限时限量氛围", "正文/评论区强调限时、库存紧张，激发紧迫感", "诺亚漏斗洞察 insight-v20"),
    method_card("📊 评测对比", '"vs 某大牌" 对比类内容，商品卡点击率高（用户已被种草）', "三感六度"),
    method_card("👥 KOL/达人背书", "标题/正文带「XX 同款」/「测评推荐」，商品卡承接好", "creation-guide-v9 D4"),
    method_card("🎁 套装/赠品", '"买一送一" / "套装更划算" 提高商品卡点击意愿', "creation-guide-v9 D9"),
])

CVR_METHODS = ''.join([
    method_card("🎯 精准人群定位", "标题里直接写人群（如「备孕」「减脂」「小学生」），过滤无效流量，转化更高", "creation-guide-v9 D5"),
    method_card("✅ 解决方案明确", "笔记给出明确「解决什么问题 → 产品就是答案」路径，CVR 翻倍", "诺亚漏斗洞察"),
    method_card("💬 评论区氛围", '"求链接""我也买了" 评论增强信任，置顶好评', "creation-guide-v9 D4"),
    method_card("🎬 视频强口播", '视频结尾明确说「链接在评论区/购物车」，引导下单', "creation-guide-v9 D9"),
    method_card("🏆 复购/老客背书", '"回购第N次" 类标题/正文，建立长期价值预期', "三感六度"),
])

PRICE_METHODS = ''.join([
    method_card("🎁 礼盒/套装", '"过节送礼" / "情人节套装" 等场景拉高客单', "creation-guide-v9 D8"),
    method_card("🍷 高端品类发力", "酒水/茶叶/滋补品本身高客单，匹配的标题强调品质/产地/年份", "诺亚漏斗洞察"),
    method_card("📦 大份装/家庭装", '"全家装" / "囤货价" 推高单笔购买量', "creation-guide-v9 D9"),
    method_card("💎 稀缺/限量", "限定款、联名款、年份产品 → 用户愿意为稀缺付溢价", "三感六度"),
    method_card("👨‍👩‍👧 送礼/孝心场景", '"送爸妈" / "送领导" 场景默认接受高客单价', "creation-guide-v9 D5"),
])

# 生成 4 个漏斗 Tab
TAB_CTR1 = funnel_tab('ctr1', '👆', '提升 CTR1：封面+标题钩子', 'ctr1', CTR1_METHODS)
TAB_CTR2 = funnel_tab('ctr2', '🔗', '提升 CTR2：商品卡点击', 'ctr2', CTR2_METHODS)
TAB_CVR = funnel_tab('cvr', '💰', '提升 CVR：转化下单', 'cvr', CVR_METHODS)
TAB_PRICE = funnel_tab('price', '💎', '提升件单价：客单优化', 'price', PRICE_METHODS, is_price=True)

# ============ 提取 V7 的 Tab4(tools)/Tab5(check) 内容 ============
def extract_panel(html, panel_id):
    """从原 HTML 提取整个 tab-panel div（含内部嵌套 div 平衡）"""
    pat = rf'<div class="tab-panel[^"]*" id="tab-{panel_id}">'
    m = re.search(pat, html)
    if not m:
        return ''
    start = m.start()
    depth = 0
    i = start
    n = len(html)
    while i < n:
        if html.startswith('<div', i) and (i+4 < n and html[i+4] in ' >'):
            depth += 1
            close = html.find('>', i)
            i = close + 1 if close != -1 else i + 1
        elif html.startswith('</div>', i):
            depth -= 1
            i += 6
            if depth == 0:
                return html[start:i]
        else:
            i += 1
    return ''

tools_panel = extract_panel(v7, 'tools')
check_panel = extract_panel(v7, 'check')

# 把 check_panel 重命名为 audit
TAB_AUDIT = check_panel.replace('id="tab-check"', 'id="tab-audit"', 1)
TAB_TOOLS = tools_panel  # 保留 id="tab-tools"

# ============ 装配新 HTML ============
# 0. 清理 V7 残留（用 CSS 隐藏，不动 DOM）：hero-section 摘要 + sidebar
# 这些会在末尾 CSS 注入时处理

# 1. 替换 nav
v8 = re.sub(r'<div class="tab-nav">.*?</div>', NEW_NAV, v7, count=1, flags=re.DOTALL)

# 2. 删除所有原 tab-panel（用 extract_panel 找到每个并删除）
for pid in ['trends','method','ref','tools','check']:
    panel_html = extract_panel(v8, pid)
    if panel_html:
        v8 = v8.replace(panel_html, '', 1)

# 3. 在 main-content 内插入新 panel
all_panels = '\n'.join([TAB1, TAB_CTR1, TAB_CTR2, TAB_CVR, TAB_PRICE, TAB_AUDIT, TAB_TOOLS])
if '<div class="main-content">' in v8:
    v8 = v8.replace('<div class="main-content">', '<div class="main-content">\n' + all_panels, 1)
elif '</main>' in v8:
    v8 = v8.replace('</main>', all_panels + '\n</main>', 1)
else:
    v8 = v8.replace('</body>', all_panels + '\n</body>', 1)

# 4. 注入 GPM 专用 CSS（追加到现有 <style> 内）
GPM_CSS = '''
/* === V8 隐藏 V7 残留 === */
.hero-section, .sidebar { display: none !important; }
.main-layout { display: block !important; flex-direction: column !important; }
.main-content { width: 100% !important; }

/* === V8 GPM 风格 === */
.hero { background: linear-gradient(135deg,#fff0f0,#fff9f5); padding: 24px; border-radius: 16px; margin-bottom: 24px; }
.hero h2 { margin: 0 0 8px; color: #ff2442; font-size: 22px; }
.hero .meta { margin: 0; color: #666; font-size: 13px; }
.hero-sub { padding: 20px; }
.hero-sub h2 { font-size: 20px; }
.funnel-formula { margin-top: 16px; padding: 16px; background: white; border-radius: 12px; font-size: 14px; color: #555; line-height: 1.8; }
.funnel-formula .step { display: inline-block; padding: 2px 8px; border-radius: 6px; margin: 0 2px; font-weight: 600; }
.funnel-formula .step.ctr1 { background: #ffe0d0; color: #d84315; }
.funnel-formula .step.ctr2 { background: #fff3e0; color: #ef6c00; }
.funnel-formula .step.cvr { background: #e8f5e9; color: #388e3c; }
.funnel-formula .step.price { background: #e3f2fd; color: #1976d2; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.kpi-grid-2col { grid-template-columns: repeat(2, 1fr); }
.kpi-card { background: white; border: 1px solid #eee; border-radius: 12px; padding: 16px; }
.kpi-title { font-size: 12px; color: #999; margin-bottom: 8px; }
.kpi-value { font-size: 26px; font-weight: bold; color: #ff2442; }
.kpi-sub { font-size: 11px; color: #666; margin-top: 4px; }
.kpi-ka { font-size: 11px; color: #888; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #eee; }
.tips-box { margin-top: 24px; padding: 14px; background: #fef9e7; border-radius: 8px; font-size: 13px; color: #7a5d00; line-height: 1.7; }
.methods-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-bottom: 24px; }
.method-card { background: white; border: 1px solid #eee; border-left: 3px solid #ff2442; border-radius: 8px; padding: 12px 14px; }
.method-title { font-weight: 600; color: #333; margin-bottom: 6px; font-size: 14px; }
.method-desc { font-size: 13px; color: #555; line-height: 1.6; }
.method-source { font-size: 11px; color: #999; margin-top: 6px; }
.case-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; margin-bottom: 24px; }
.case-card { display: flex; background: white; border: 1px solid #eee; border-radius: 8px; padding: 12px; gap: 12px; }
.case-rank { flex: 0 0 36px; height: 36px; background: linear-gradient(135deg,#ff2442,#ff7043); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; }
.case-body { flex: 1; min-width: 0; }
.case-title { font-weight: 600; color: #222; font-size: 14px; margin-bottom: 6px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.case-meta { display: flex; gap: 10px; align-items: center; font-size: 12px; margin-bottom: 4px; }
.case-metric { background: #ff2442; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.case-seller { color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.case-stats { font-size: 11px; color: #888; margin-bottom: 6px; }
.case-highlight { font-size: 12px; color: #555; background: #fafafa; padding: 6px 8px; border-radius: 6px; margin-bottom: 6px; line-height: 1.5; }
.case-link { font-size: 12px; color: #ff2442; text-decoration: none; }
.case-link:hover { text-decoration: underline; }
@media (max-width: 768px) {
  .kpi-grid-2col { grid-template-columns: 1fr; }
  .case-grid { grid-template-columns: 1fr; }
  .methods-grid { grid-template-columns: 1fr; }
  .hero { padding: 16px; }
  .hero h2 { font-size: 18px; }
}
'''
# 注入到第一个 </style> 之前
v8 = v8.replace('</style>', GPM_CSS + '\n</style>', 1)

# ============ 写出 ============
with open(OUT_PATH, 'w') as f:
    f.write(v8)

print(f"index.html written: {os.path.getsize(OUT_PATH):,} bytes")

# 自检：style 标签平衡 + tab-panel 数量
import re as _re
n_open = len(_re.findall(r'<style\b', v8))
n_close = len(_re.findall(r'</style>', v8))
print(f"<style> 平衡：{n_open}/{n_close}")
n_panel = len(_re.findall(r'class="tab-panel', v8))
print(f"tab-panel 数量：{n_panel}（预期 7）")
panel_ids = _re.findall(r'<div class="tab-panel[^"]*" id="tab-(\w+)"', v8)
print(f"panel ids: {panel_ids}")
