#!/usr/bin/env python3
"""V4: 彻底替换全部 CSS，对齐 Uno 风格：纯白底 + 大间距 + 黑色系 + 彩色品类色块"""

content = open('index.html').read()

# ── 找两个 style 块的边界 ──
e1 = content.find('</style>') + 8
s2 = content.find('<style>', e1)
e2 = content.find('</style>', s2) + 8
s1 = content.find('<style>')

print(f"style1: {s1}~{e1}")
print(f"style2: {s2}~{e2}")

# ── 新 CSS style1 (主 CSS) ──
NEW_CSS1 = """<style>
/* ════════════════════════════════════════
   V4 Design System — Uno-inspired
   纯白底 / 大间距 / 粗字体 / 彩色色块
   ════════════════════════════════════════ */

/* Google Fonts: Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;0,14..32,900&display=swap');

:root {
  /* 品牌色 */
  --red:     #FF3B30;
  --orange:  #FF9500;
  --green:   #34C759;
  --blue:    #007AFF;
  --purple:  #AF52DE;
  --teal:    #30B0C7;

  /* 页面色 */
  --bg:      #FFFFFF;
  --bg2:     #F5F5F7;
  --card:    #FFFFFF;
  --border:  #E6E6EB;
  --text:    #1D1D1F;
  --text2:   #6E6E73;
  --text3:   #AEAEB2;

  /* 圆角 */
  --r6:  6px;
  --r10: 10px;
  --r14: 14px;
  --r18: 18px;
  --r24: 24px;

  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,.08);
  --shadow-lg: 0 8px 30px rgba(0,0,0,.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── HEADER ── */
.header {
  background: rgba(255,255,255,.92);
  border-bottom: 1px solid var(--border);
  padding: 0 32px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 200;
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
}
.header-left  { display: flex; align-items: center; gap: 12px; }
.header-icon  { font-size: 26px; line-height: 1; }
.header-title { font-size: 16px; font-weight: 800; letter-spacing: -.4px; color: var(--text); }
.header-sub   { font-size: 11px; color: var(--text2); margin-top: 1px; }
.header-right { display: flex; align-items: center; gap: 12px; }
.header-week  { font-size: 28px; font-weight: 900; letter-spacing: -2px; color: var(--red); }
.header-date  { font-size: 11px; color: var(--text2); text-align: right; }

/* ── TAB NAV ── */
.tab-nav {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border);
  padding: 0 0 0 0;
  margin-bottom: 32px;
  overflow-x: auto;
  scrollbar-width: none;
  background: var(--bg);
  position: sticky;
  top: 60px;
  z-index: 100;
}
.tab-nav::-webkit-scrollbar { display: none; }

.tab-btn {
  padding: 14px 20px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--text2);
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: color .15s, border-color .15s;
  margin-bottom: -1px;
  letter-spacing: -.2px;
}
.tab-btn:hover  { color: var(--text); }
.tab-btn.active { color: var(--text); border-bottom-color: var(--text); }

/* ── CONTAINER ── */
.container { max-width: 1120px; margin: 0 auto; padding: 32px 32px 100px; }

/* ── SECTION LABEL ── */
.section-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 2px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── TAGS ── */
.tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg2);
  color: var(--text2);
}

/* ── GRID ── */
.trend-grid   { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.top-grid     { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.bench-grid   { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.method-grid  { display: grid; gap: 12px; }
.ref-grid     { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.note-grid    { display: grid; grid-template-columns: 1fr; gap: 10px; }
.lingxi-grid  { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.check-grid   { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }

/* ── TREND CARD (品类) ── */
.trend-card {
  background: var(--card);
  border-radius: var(--r18);
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s, transform .2s;
}
.trend-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.trend-head {
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -.2px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.trend-head.snack  { background: #FF6B35; }
.trend-head.fast   { background: #FFB020; }
.trend-head.drink  { background: #0BA5EC; }
.trend-head.liquor { background: #0D9488; }
.trend-head.herb   { background: #17B26A; }
.trend-body { padding: 4px 0; }
.trend-item {
  padding: 10px 16px;
  border-bottom: 1px solid var(--bg2);
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.trend-item:last-child { border-bottom: none; }
.trend-num {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--bg2);
  color: var(--text3);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}
.trend-text { font-size: 12px; color: var(--text); line-height: 1.55; }

/* TOP 笔记专用卡 */
.top-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--bg2);
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.top-item:last-child { border-bottom: none; }
.top-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--text);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}
.top-num.gold   { background: #FFB020; }
.top-num.silver { background: #8E8E93; }
.top-num.bronze { background: #C47B3A; }
.top-text { font-size: 12px; color: var(--text); line-height: 1.55; }
.top-meta { font-size: 11px; color: var(--text2); margin-top: 3px; }

/* ── TOP-HEAD 标题卡 ── */
.top-head {
  background: var(--text);
  color: #fff;
  border-radius: var(--r18) var(--r18) 0 0;
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: -.2px;
}
.top-card {
  background: var(--card);
  border-radius: var(--r18);
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.top-card:hover { box-shadow: var(--shadow-md); }

/* ── BENCH CARD (行业均值) ── */
.bench-card {
  background: var(--card);
  border-radius: var(--r18);
  border: 1px solid var(--border);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}
.bench-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--text);
}
.bench-card.avg::before { background: var(--blue); }
.bench-card-label { font-size: 11px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.bench-card-val   { font-size: 28px; font-weight: 900; color: var(--text); letter-spacing: -1.5px; line-height: 1; }
.bench-card-sub   { font-size: 12px; color: var(--text2); margin-top: 6px; }

/* ── HOT TAGS ── */
.hot-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin: 3px;
  background: var(--bg2);
  color: var(--text);
  border: none;
  cursor: default;
  white-space: nowrap;
}

/* ── NOTE CARD ── */
.note-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  transition: box-shadow .2s, transform .15s;
  text-decoration: none;
  cursor: pointer;
}
.note-card:hover { box-shadow: var(--shadow-md); transform: translateX(2px); }
.note-rank {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 900;
  color: var(--text3);
  width: 24px;
  text-align: right;
}
.note-content { flex: 1; }
.note-title   { font-size: 14px; font-weight: 600; color: var(--text); line-height: 1.45; }
.note-meta    { font-size: 12px; color: var(--text2); margin-top: 5px; }
.note-link    { font-size: 11px; color: var(--blue); margin-top: 4px; }

/* ── METHOD CARD ── */
.method-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s, transform .2s;
}
.method-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.method-card.open  { border-color: var(--red); box-shadow: 0 0 0 3px rgba(255,59,48,.1); }
.method-head {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  user-select: none;
}
.method-num {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: var(--text);
  color: #fff;
  font-size: 14px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}
.method-info    { flex: 1; }
.method-title   { font-size: 15px; font-weight: 700; color: var(--text); letter-spacing: -.2px; }
.method-badge   { display: inline-block; margin-top: 4px; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; background: rgba(255,59,48,.09); color: var(--red); }
.method-arrow   { font-size: 18px; color: var(--text3); transition: transform .2s; }
.method-card.open .method-arrow { transform: rotate(90deg); }
.method-body    { display: none; border-top: 1px solid var(--border); padding: 20px; }
.method-card.open .method-body { display: block; }
.method-why-text {
  font-size: 13px;
  line-height: 1.7;
  padding: 12px 16px;
  border-radius: var(--r10);
  border-left: 3px solid var(--red);
  background: rgba(255,59,48,.04);
  color: var(--text);
  margin-bottom: 14px;
}
.method-case {
  border: 1px solid var(--border);
  border-radius: var(--r10);
  padding: 14px;
  margin-top: 10px;
  background: var(--bg2);
}
.method-case-label { font-size: 10px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.method-case-text  { font-size: 13px; color: var(--text); line-height: 1.7; }

/* ── SGLD CARD ── */
.sgld-card {
  background: var(--bg2);
  border-radius: var(--r18);
  padding: 24px;
  margin-top: 24px;
}
.sgld-title { font-size: 15px; font-weight: 800; color: var(--text); margin-bottom: 12px; }
.sgld-desc  { font-size: 13px; color: var(--text2); line-height: 1.7; margin-bottom: 16px; }
.sgld-btn {
  display: inline-block;
  padding: 10px 20px;
  background: var(--text);
  color: #fff;
  border: none;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  text-decoration: none;
  transition: opacity .15s;
}
.sgld-btn:hover { opacity: .85; }

/* ── TAB3: REF ── */
.ref-intro {
  background: var(--bg2);
  border-radius: var(--r14);
  padding: 16px 20px;
  font-size: 14px;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 24px;
}
.ref-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.ref-form-title { font-size: 16px; font-weight: 800; color: var(--text); margin-bottom: 20px; letter-spacing: -.3px; }
.form-row   { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--text2); }
.required   { color: var(--red); }
.form-input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--r10);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  background: var(--bg);
  color: var(--text);
  transition: border-color .15s, box-shadow .15s;
}
.form-input:focus { border-color: var(--text); box-shadow: 0 0 0 3px rgba(29,29,31,.06); }
.form-input::placeholder { color: var(--text3); }
.cat-select-group { display: flex; flex-wrap: wrap; gap: 8px; }
.cat-radio { cursor: pointer; }
.cat-radio input { display: none; }
.cat-radio span {
  display: inline-block;
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: var(--bg2);
  color: var(--text2);
  border: 1.5px solid transparent;
  transition: all .15s;
  cursor: pointer;
}
.cat-radio input:checked + span {
  background: var(--text);
  color: #fff;
  border-color: var(--text);
}

/* Cat L1/L2/price/audience btn */
.cat-l1-btn, .cat-l2-btn, .price-btn, .aud-btn {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  background: var(--bg);
  color: var(--text2);
  transition: all .15s;
}
.cat-l1-btn.active, .cat-l2-btn.active, .price-btn.active {
  background: var(--text);
  color: #fff;
  border-color: var(--text);
}
.aud-btn.active {
  background: var(--purple);
  color: #fff;
  border-color: var(--purple);
}

/* ref-card: 结果卡片 */
.ref-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 20px;
  box-shadow: var(--shadow-sm);
}
.ref-card-title { font-size: 11px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 14px; }
.ref-tag {
  display: inline-block;
  margin: 3px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255,59,48,.08);
  color: var(--red);
}
.ref-template {
  border-radius: var(--r10);
  padding: 12px 16px;
  margin: 8px 0;
  font-size: 13px;
  line-height: 1.65;
  background: var(--bg2);
  color: var(--text);
  border-left: 3px solid var(--text);
}
.ref-template .title { font-weight: 700; font-size: 13px; color: var(--text); margin-bottom: 4px; }
.ref-template .example { font-size: 12px; color: var(--text2); margin-top: 4px; }
.ref-case {
  border: 1px solid var(--border);
  border-radius: var(--r10);
  padding: 12px 16px;
  margin: 8px 0;
  background: var(--bg2);
}
.ref-actions { display: flex; gap: 10px; margin-top: 16px; }
.btn-refresh {
  flex: 1;
  border-radius: var(--r10);
  padding: 11px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: var(--bg2);
  border: 1.5px solid var(--border);
  color: var(--text2);
  transition: background .15s;
}
.btn-refresh:hover { background: #E6E6EB; }
.btn-copy-all {
  flex: 1;
  border-radius: var(--r10);
  padding: 11px;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: var(--text);
  border: none;
  color: #fff;
  transition: opacity .15s;
}
.btn-copy-all:hover { opacity: .85; }
.btn-gen-main {
  display: block;
  width: 100%;
  margin-top: 20px;
  padding: 16px;
  background: var(--text);
  color: #fff;
  border: none;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 800;
  font-family: inherit;
  cursor: pointer;
  letter-spacing: -.3px;
  transition: opacity .15s, transform .1s;
}
.btn-gen-main:hover { opacity: .88; }
.btn-gen-main:active { transform: scale(.99); }
.btn-gen-main:disabled { opacity: .4; cursor: not-allowed; }

/* lingxi cards */
.lingxi-card {
  border-radius: var(--r14);
  border: 1.5px solid var(--border);
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  background: var(--card);
  transition: all .2s;
}
.lingxi-card:hover {
  border-color: var(--text);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.lingxi-icon { font-size: 28px; }
.lingxi-info .name { font-size: 14px; font-weight: 700; color: var(--text); }
.lingxi-info .desc { font-size: 12px; color: var(--text2); margin-top: 3px; }
.lingxi-arrow { margin-left: auto; font-size: 16px; color: var(--text3); }

/* ── TAB4: 创作工具 ── */
.planner-card {
  background: var(--card);
  border-radius: var(--r24);
  border: 1px solid var(--border);
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}
.planner-intro {
  background: var(--bg2);
  padding: 16px 24px;
  font-size: 13px;
  color: var(--text2);
  border-bottom: 1px solid var(--border);
  line-height: 1.6;
}
.planner-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.planner-actions {
  padding: 0 24px 24px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.btn-gen {
  padding: 12px 24px;
  background: var(--text);
  color: #fff;
  border: none;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: opacity .15s;
}
.btn-gen:hover { opacity: .85; }
.btn-gen.btn-doubao { background: #4F4F4F; }
.btn-copy {
  padding: 12px 20px;
  background: var(--bg2);
  color: var(--text2);
  border: 1.5px solid var(--border);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background .15s;
}
.btn-copy:hover { background: #E6E6EB; }
.prompt-preview {
  margin: 0 24px 24px;
  background: var(--bg2);
  border-radius: var(--r14);
  overflow: hidden;
}
.prompt-label {
  padding: 8px 14px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text3);
  background: var(--border);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.prompt-text {
  padding: 14px;
  font-size: 13px;
  color: var(--text2);
  line-height: 1.7;
  white-space: pre-wrap;
  max-height: 280px;
  overflow-y: auto;
}
.copy-success {
  background: rgba(52,199,89,.1) !important;
  color: var(--green) !important;
  border-color: rgba(52,199,89,.3) !important;
}

/* ── TAB5: 体检 ── */
.check-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r24);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.check-module {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 20px;
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}
.check-module-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.check-score {
  text-align: center;
  padding: 24px;
  border-radius: var(--r14);
  margin-bottom: 14px;
  background: var(--bg2);
}
.check-score-num { font-size: 44px; font-weight: 900; color: var(--text); letter-spacing: -3px; }
.check-score-label { font-size: 13px; color: var(--text2); margin-top: 6px; }
.check-top-tip {
  border-radius: var(--r10);
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.65;
  margin-top: 12px;
  background: rgba(255,149,0,.08);
  color: #CC7A00;
  font-weight: 500;
}
.check-result-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text);
}
.check-result-item:last-child { border-bottom: none; }
.check-result-item.pass { color: var(--green); }
.check-result-item.fail { color: var(--red); }
.check-result-icon { margin-right: 6px; }

/* ── FORMULA CARD ── */
.formula-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  padding: 18px;
  box-shadow: var(--shadow-sm);
}
.formula-title { font-size: 13px; font-weight: 800; color: var(--text); margin-bottom: 10px; }
.formula-body  { font-size: 13px; color: var(--text2); line-height: 1.7; }

/* ── MOBILE ── */
@media (max-width: 768px) {
  .container { padding: 20px 16px 80px; }
  .header { padding: 0 16px; }
  .tab-btn { padding: 12px 14px; font-size: 13px; }
  .trend-grid  { grid-template-columns: 1fr 1fr; gap: 10px; }
  .top-grid    { grid-template-columns: 1fr; }
  .bench-grid  { grid-template-columns: 1fr 1fr; }
  .ref-grid    { grid-template-columns: 1fr; }
  .check-grid  { grid-template-columns: 1fr; }
  .lingxi-grid { grid-template-columns: 1fr; }
  .section-label::after { display: none; }
  .header-week { font-size: 22px; }
}
@media (max-width: 480px) {
  .trend-grid  { grid-template-columns: 1fr; }
  .bench-grid  { grid-template-columns: 1fr; }
}

/* ── TOPIC TAGS AREA ── */
.topic-tag { display: inline-block; margin: 3px; }
.topic-tag span, .topic-tag-inner {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg2);
  color: var(--text);
  white-space: nowrap;
}
.topic-tag.seasonal span   { background: rgba(255,149,0,.1); color: #CC7A00; }
.topic-tag.evergreen span  { background: rgba(52,199,89,.1);  color: #1A8C3E; }
.topic-tag.trending span   { background: rgba(255,59,48,.1);  color: var(--red); }

/* ── UTIL ── */
.text-muted { color: var(--text2); }
.text-sm    { font-size: 13px; }
.text-xs    { font-size: 12px; }
.mb8  { margin-bottom: 8px; }
.mb12 { margin-bottom: 12px; }
.mb16 { margin-bottom: 16px; }
.mb24 { margin-bottom: 24px; }
.mt16 { margin-top: 16px; }
.mt24 { margin-top: 24px; }
.p16  { padding: 16px; }
.gap8 { gap: 8px; }
.gap12 { gap: 12px; }
.flex { display: flex; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }

/* ── LOADING ── */
.loading { color: var(--text2); font-size: 13px; padding: 20px; text-align: center; }
.spin { display: inline-block; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── FOOTER ── */
.footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text3);
  border-top: 1px solid var(--border);
  margin-top: 40px;
}

/* ── 旧类名兼容（避免 JS 里的 class 对不上） ── */
.card { background: var(--card); border: 1px solid var(--border); border-radius: var(--r14); box-shadow: var(--shadow-sm); }
.topic-section { margin-bottom: 28px; }
.top-notes-section { margin-bottom: 32px; }
.bench-section { margin-bottom: 32px; }
</style>"""

# ── 新 CSS style2 (创作工具，覆盖掉 V1 深色) ──
NEW_CSS2 = """<style>
/* ── Tab4 创作工具（V4 override，确保覆盖 V1 深色残留） ── */
.planner-card * { color: inherit; }
.planner-intro  { line-height: 1.7; }
.cat-radio span, .cat-radio input:checked + span { font-family: inherit; }
</style>"""

# ── 替换 ──
new_content = content[:s1] + NEW_CSS1 + content[e1:s2] + NEW_CSS2 + content[e2:]

# 验证
opens  = new_content.count('<style>')
closes = new_content.count('</style>')
print(f"style OK: {opens} ↔ {closes}")

open('index.html', 'w').write(new_content)
print(f"写入: {len(new_content)} bytes")
