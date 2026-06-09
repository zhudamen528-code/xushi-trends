#!/usr/bin/env python3
"""
Design V5: 小红书电商风格 · 内容创作工作台
- 主色：小红书品牌红 #FE2C55
- 底色：暖灰 #F7F7F8，卡片纯白
- 字体：Inter + PingFang SC
- 动效：选中弹性、按钮 hover、结果 fadeInUp
- 保留品类色块识别色（橙/黄/蓝/绿/青）
"""

content = open('index.html').read()

# 定位两个 style 块
e1 = content.find('</style>') + 8
s2 = content.find('<style>', e1)
e2 = content.find('</style>', s2) + 8
s1 = content.find('<style>')

NEW_CSS1 = """<style>
/* ═══════════════════════════════════════════════
   Design V5 — 小红书电商风格内容创作工作台
   主色：#FE2C55  底色：#F7F7F8  字体：Inter
   ═══════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Design Tokens ── */
:root {
  --red:      #FE2C55;
  --red-soft: rgba(254,44,85,.08);
  --red-mid:  rgba(254,44,85,.15);
  --orange:   #FF6B35;
  --yellow:   #FFB020;
  --blue:     #0BA5EC;
  --teal:     #0D9488;
  --green:    #17B26A;
  --purple:   #7C3AED;

  --bg:       #F7F7F8;
  --card:     #FFFFFF;
  --border:   #EBEBEB;
  --border2:  #F0F0F0;

  --text:     #1A1A1A;
  --text2:    #666666;
  --text3:    #AAAAAA;

  --r6:  6px;
  --r10: 10px;
  --r14: 14px;
  --r18: 18px;
  --r24: 24px;

  --shadow-sm: 0 1px 4px rgba(0,0,0,.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,.09);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.12);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'Inter', -apple-system, 'PingFang SC', 'Helvetica Neue', sans-serif;
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

/* ── TAB 显隐（核心，不可删）── */
.tab-panel { display: block; }
.tab-panel.hidden { display: none !important; }
.hidden { display: none !important; }

/* ── HEADER ── */
.header {
  background: #FFFFFF;
  border-bottom: 1px solid var(--border);
  padding: 0 36px;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 200;
  backdrop-filter: saturate(180%) blur(16px);
  -webkit-backdrop-filter: saturate(180%) blur(16px);
}
.header-left  { display: flex; align-items: center; gap: 10px; }
.header-icon  { font-size: 24px; line-height: 1; }
.header-title { font-size: 16px; font-weight: 800; letter-spacing: -.3px; color: var(--text); }
.header-sub   { font-size: 11px; color: var(--text3); margin-top: 1px; }
.header-right { display: flex; align-items: flex-end; gap: 6px; flex-direction: column; text-align: right; }
.header-week  {
  font-size: 30px;
  font-weight: 900;
  letter-spacing: -2px;
  color: var(--red);
  line-height: 1;
}
.header-date  { font-size: 11px; color: var(--text3); line-height: 1; }

/* ── TAB NAV ── */
.tab-nav {
  display: flex;
  background: #FFFFFF;
  border-bottom: 1px solid var(--border);
  padding: 0 36px;
  overflow-x: auto;
  scrollbar-width: none;
  position: sticky;
  top: 62px;
  z-index: 100;
}
.tab-nav::-webkit-scrollbar { display: none; }

.tab-btn {
  padding: 14px 18px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--text2);
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: color .15s, border-color .15s, background .15s;
  margin-bottom: -1px;
  border-radius: 0;
}
.tab-btn:hover  {
  color: var(--text);
  background: var(--red-soft);
}
.tab-btn.active {
  color: var(--red);
  border-bottom-color: var(--red);
  background: rgba(254,44,85,.04);
}

/* ── CONTAINER ── */
.container { max-width: 1100px; margin: 0 auto; padding: 28px 36px 100px; }

/* ── SECTION LABEL ── */
.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 18px;
  margin-top: 36px;
}
.section-label:first-child,
.tab-panel > .section-label:first-child { margin-top: 0; }
.section-label .icon { font-size: 14px; }
.section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ── CARD BASE ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  box-shadow: var(--shadow-sm);
}

/* ── TREND GRID (品类风向) ── */
.trend-grid  { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.top-grid    { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.bench-grid  { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.note-grid   { display: grid; grid-template-columns: 1fr; gap: 8px; }
.ref-grid    { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.check-grid  { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.lingxi-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.method-grid { display: grid; gap: 10px; }

/* ── TREND CARD ── */
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
  padding: 13px 15px;
  font-size: 13px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -.2px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.trend-head.snack  { background: linear-gradient(135deg, #FF6B35, #FF8E53); }
.trend-head.fast   { background: linear-gradient(135deg, #FFB020, #FFC94D); }
.trend-head.drink  { background: linear-gradient(135deg, #0BA5EC, #38BDF8); }
.trend-head.liquor { background: linear-gradient(135deg, #0D9488, #2DD4BF); }
.trend-head.herb   { background: linear-gradient(135deg, #17B26A, #4ADE80); }
.trend-body { padding: 4px 0; }
.trend-item {
  padding: 10px 15px;
  border-bottom: 1px solid var(--border2);
  font-size: 12px;
  color: var(--text);
  line-height: 1.6;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}
.trend-item:last-child { border-bottom: none; }
.trend-num {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--bg);
  color: var(--text3);
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}
.trend-text { flex: 1; font-size: 12px; line-height: 1.6; }

/* TOP 笔记卡 */
.top-card {
  background: var(--card);
  border-radius: var(--r18);
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.top-head {
  background: var(--text);
  color: #fff;
  padding: 12px 15px;
  font-size: 13px;
  font-weight: 800;
}
.top-item {
  padding: 11px 15px;
  border-bottom: 1px solid var(--border2);
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.top-item:last-child { border-bottom: none; }
.top-num {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  color: var(--text2);
  margin-top: 1px;
}
.top-num.gold   { background: #FFB020; color: #fff; }
.top-num.silver { background: #8E8E93; color: #fff; }
.top-num.bronze { background: #C47B3A; color: #fff; }
.top-text { font-size: 12px; color: var(--text); line-height: 1.55; }
.top-meta { font-size: 11px; color: var(--text3); margin-top: 2px; }

/* BENCH CARD */
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
  background: var(--red);
}
.bench-card.avg::before { background: var(--blue); }
.bench-card-label { font-size: 10px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
.bench-card-val   { font-size: 26px; font-weight: 900; color: var(--text); letter-spacing: -1px; line-height: 1; }
.bench-card-sub   { font-size: 12px; color: var(--text2); margin-top: 6px; }

/* HOT TAGS */
.hot-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin: 3px;
  background: var(--bg);
  color: var(--text2);
  border: 1px solid var(--border);
  white-space: nowrap;
}

/* NOTE CARD */
.note-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  padding: 12px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  transition: box-shadow .15s, border-color .15s;
  cursor: pointer;
}
.note-card:hover {
  box-shadow: var(--shadow-md);
  border-color: #D0D0D0;
}
.note-rank  { flex-shrink: 0; font-size: 13px; font-weight: 900; color: var(--text3); width: 22px; text-align: right; }
.note-content { flex: 1; }
.note-title { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.45; }
.note-meta  { font-size: 11px; color: var(--text3); margin-top: 4px; }

/* FORMULA CARD */
.formula-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  padding: 18px;
  box-shadow: var(--shadow-sm);
}
.formula-title { font-size: 13px; font-weight: 800; color: var(--text); margin-bottom: 12px; }
.formula-body  { font-size: 13px; color: var(--text2); line-height: 1.7; }

/* ── 标题公式行 ── */
.formula-row { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border2); }
.formula-row:last-child { border-bottom: none; }
.formula-rank { flex-shrink: 0; width: 24px; height: 24px; border-radius: 6px; background: var(--red); color: #fff; font-size: 11px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.formula-pills { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; flex: 1; }
.formula-pill  { padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; background: var(--bg); color: var(--text2); border: 1px solid var(--border); }
.formula-pill.hot { background: var(--red-soft); color: var(--red); border-color: var(--red-mid); }
.formula-plus  { font-size: 14px; color: var(--text3); font-weight: 700; }
.formula-example { font-size: 11px; color: var(--text3); margin-top: 4px; line-height: 1.5; }

/* ── TOPIC TAGS ── */
.topic-tag { display: inline-block; margin: 3px; }
.topic-tag span, .topic-tag-inner {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg);
  color: var(--text2);
  border: 1px solid var(--border);
  white-space: nowrap;
}
.topic-tag.hot     span { background: var(--red-soft); color: var(--red); border-color: var(--red-mid); }
.topic-tag.seasonal span { background: rgba(255,176,32,.1); color: #996600; border-color: rgba(255,176,32,.3); }
.topic-tag.evergreen span { background: rgba(23,178,106,.1); color: #0D7A47; border-color: rgba(23,178,106,.3); }

/* ── TAG (通用) ── */
.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  background: var(--bg);
  color: var(--text3);
  border: 1px solid var(--border);
}

/* ── METHOD CARD ── */
.method-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow .2s, border-color .2s;
}
.method-card:hover  { box-shadow: var(--shadow-md); }
.method-card.open   { border-color: var(--red); box-shadow: 0 0 0 3px rgba(254,44,85,.08); }
.method-head {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  user-select: none;
  transition: background .15s;
}
.method-head:hover { background: var(--red-soft); }
.method-num {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--text);
  color: #fff;
  font-size: 13px;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
}
.method-card.open .method-num { background: var(--red); }
.method-info    { flex: 1; }
.method-title   { font-size: 14px; font-weight: 700; color: var(--text); letter-spacing: -.2px; }
.method-badge   { display: inline-block; margin-top: 3px; padding: 1px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; background: var(--red-soft); color: var(--red); }
.method-arrow   { font-size: 16px; color: var(--text3); transition: transform .2s; }
.method-card.open .method-arrow { transform: rotate(90deg); color: var(--red); }
.method-body    { display: none; border-top: 1px solid var(--border); padding: 18px 20px; }
.method-card.open .method-body { display: block; }
.method-why-text {
  font-size: 13px;
  line-height: 1.7;
  padding: 12px 16px;
  border-radius: var(--r10);
  border-left: 3px solid var(--red);
  background: var(--red-soft);
  color: var(--text);
  margin-bottom: 12px;
}
.method-case {
  background: var(--bg);
  border-radius: var(--r10);
  padding: 12px 14px;
  margin-top: 10px;
}
.method-case-label { font-size: 10px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; }
.method-case-text  { font-size: 13px; color: var(--text); line-height: 1.7; }

/* SGLD CARD */
.sgld-card  { background: var(--bg); border-radius: var(--r18); padding: 22px; margin-top: 20px; }
.sgld-title { font-size: 15px; font-weight: 800; color: var(--text); margin-bottom: 10px; }
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
  transition: opacity .15s;
  text-decoration: none;
}
.sgld-btn:hover { opacity: .85; }

/* ── FORM SYSTEM ── */
.ref-intro {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 3px solid var(--red);
  border-radius: var(--r14);
  padding: 14px 18px;
  font-size: 14px;
  color: var(--text2);
  line-height: 1.7;
  margin-bottom: 20px;
}
.ref-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.ref-form-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 20px;
  letter-spacing: -.3px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}
.form-row   { display: flex; flex-direction: column; gap: 6px; margin-bottom: 4px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--text2); }
.required   { color: var(--red); }

.form-input {
  width: 100%;
  padding: 11px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--r10);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  background: #FAFAFA;
  color: var(--text);
  transition: border-color .15s, box-shadow .15s, background .15s;
}
.form-input:focus {
  border-color: var(--red);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(254,44,85,.1);
}
.form-input::placeholder { color: var(--text3); }

/* 选项按钮统一样式 */
.cat-l1-btn, .cat-l2-btn, .price-btn, .aud-btn {
  padding: 8px 16px;
  border-radius: 24px;
  border: 1.5px solid var(--border);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  background: #FAFAFA;
  color: var(--text2);
  transition: all .15s;
  white-space: nowrap;
}
.cat-l1-btn:hover, .cat-l2-btn:hover,
.price-btn:hover, .aud-btn:hover {
  border-color: var(--red);
  color: var(--red);
  background: var(--red-soft);
}
.cat-l1-btn.active, .price-btn.active {
  background: var(--red);
  color: #fff;
  border-color: var(--red);
  transform: scale(1.03);
  box-shadow: 0 2px 8px rgba(254,44,85,.3);
}
.cat-l2-btn.active {
  background: var(--text);
  color: #fff;
  border-color: var(--text);
}
.aud-btn.active {
  background: var(--red-soft);
  color: var(--red);
  border-color: var(--red);
  font-weight: 700;
}

/* cat-radio (Tab4) */
.cat-radio { cursor: pointer; }
.cat-radio input { display: none; }
.cat-radio span {
  display: inline-block;
  padding: 7px 14px;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 600;
  background: #FAFAFA;
  color: var(--text2);
  border: 1.5px solid var(--border);
  transition: all .15s;
  cursor: pointer;
}
.cat-radio input:checked + span {
  background: var(--red);
  color: #fff;
  border-color: var(--red);
}

/* ── MAIN CTA BUTTON ── */
.btn-gen-main {
  display: block;
  width: 100%;
  margin-top: 22px;
  padding: 16px;
  background: linear-gradient(135deg, #FE2C55, #FF5070);
  color: #fff;
  border: none;
  border-radius: 28px;
  font-size: 15px;
  font-weight: 800;
  font-family: inherit;
  cursor: pointer;
  letter-spacing: -.2px;
  box-shadow: 0 4px 16px rgba(254,44,85,.35);
  transition: opacity .15s, transform .12s, box-shadow .15s;
}
.btn-gen-main:hover {
  opacity: .92;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(254,44,85,.4);
}
.btn-gen-main:active  { transform: scale(.99); }
.btn-gen-main:disabled { opacity: .45; cursor: not-allowed; transform: none; box-shadow: none; }

/* ── ACTION BUTTONS ── */
.btn-gen {
  padding: 11px 22px;
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
  padding: 11px 20px;
  background: var(--bg);
  color: var(--text2);
  border: 1.5px solid var(--border);
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background .15s;
}
.btn-copy:hover { background: #EBEBEB; }

.btn-refresh {
  flex: 1;
  padding: 11px;
  border-radius: var(--r10);
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text2);
  transition: background .15s;
}
.btn-refresh:hover { background: #EBEBEB; }

.btn-copy-all {
  flex: 1;
  padding: 11px;
  border-radius: var(--r10);
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  background: var(--red-soft);
  border: 1.5px solid var(--red-mid);
  color: var(--red);
  transition: background .15s;
}
.btn-copy-all:hover { background: var(--red-mid); }

.copy-success {
  background: rgba(23,178,106,.1) !important;
  color: var(--green) !important;
  border-color: rgba(23,178,106,.3) !important;
}

/* ── REF RESULT CARDS ── */
.ref-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
}
.ref-card-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.ref-tag {
  display: inline-block;
  margin: 3px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  background: var(--red-soft);
  color: var(--red);
  border: 1px solid var(--red-mid);
}
.ref-template {
  border-radius: var(--r10);
  padding: 11px 14px;
  margin: 6px 0;
  font-size: 13px;
  line-height: 1.65;
  background: var(--bg);
  border-left: 3px solid var(--text);
}
.ref-template .example { font-size: 11px; color: var(--text3); margin-top: 4px; }
.ref-case {
  border: 1px solid var(--border);
  border-radius: var(--r10);
  padding: 12px 14px;
  margin: 6px 0;
  background: var(--bg);
}
.ref-actions { display: flex; gap: 10px; margin-top: 16px; }

/* REF INTRO */
.ref-intro { border-left: 3px solid var(--red); }

/* ── PLANNER CARD (Tab4) ── */
.planner-card {
  background: var(--card);
  border-radius: var(--r24);
  border: 1px solid var(--border);
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: var(--shadow-sm);
}
.planner-intro {
  background: var(--bg);
  padding: 14px 22px;
  font-size: 13px;
  color: var(--text2);
  border-bottom: 1px solid var(--border);
  line-height: 1.65;
}
.planner-form { padding: 22px; display: flex; flex-direction: column; gap: 14px; }
.planner-actions { padding: 0 22px 20px; display: flex; gap: 10px; flex-wrap: wrap; }

.prompt-preview {
  margin: 0 22px 22px;
  background: var(--bg);
  border-radius: var(--r14);
  overflow: hidden;
  border: 1px solid var(--border);
}
.prompt-label {
  padding: 7px 14px;
  font-size: 10px;
  font-weight: 700;
  color: var(--text3);
  background: var(--border2);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.prompt-text {
  padding: 14px;
  font-size: 12px;
  color: var(--text2);
  line-height: 1.7;
  white-space: pre-wrap;
  max-height: 260px;
  overflow-y: auto;
}

/* ── LINGXI CARDS ── */
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
  border-color: var(--red);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}
.lingxi-icon { font-size: 26px; }
.lingxi-info .name { font-size: 14px; font-weight: 700; color: var(--text); }
.lingxi-info .desc { font-size: 12px; color: var(--text2); margin-top: 2px; }
.lingxi-arrow { margin-left: auto; font-size: 16px; color: var(--text3); }

/* ── CHECK (Tab5) ── */
.check-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r24);
  padding: 22px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}
.check-module {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r18);
  padding: 18px 20px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-sm);
}
.check-module-title {
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
  margin-bottom: 12px;
}
.check-score {
  text-align: center;
  padding: 22px;
  border-radius: var(--r14);
  margin-bottom: 12px;
  background: var(--bg);
}
.check-score-num   { font-size: 42px; font-weight: 900; color: var(--red); letter-spacing: -2px; }
.check-score-label { font-size: 13px; color: var(--text2); margin-top: 6px; }
.check-top-tip {
  border-radius: var(--r10);
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.65;
  margin-top: 12px;
  background: rgba(255,176,32,.08);
  color: #996600;
  font-weight: 500;
  border-left: 3px solid var(--yellow);
}

/* ── RESULT ANIMATION ── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
#ref-result-content { animation: fadeInUp .3s ease; }
.tool-result-area.show { animation: fadeInUp .25s ease; }

/* ── LOADING DOTS ── */
@keyframes dot-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: .4; }
  40%            { transform: translateY(-6px); opacity: 1; }
}
.loading-dots { display: inline-flex; gap: 4px; }
.loading-dots span {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--red);
  display: inline-block;
  animation: dot-bounce 1.2s infinite;
}
.loading-dots span:nth-child(2) { animation-delay: .15s; }
.loading-dots span:nth-child(3) { animation-delay: .3s; }

/* ── TOOL RESULT ── */
.tool-result-area { margin-top: 14px; }
.tool-result-text { font-size: 13px; line-height: 1.8; white-space: pre-wrap; color: var(--text); }
.title-item {
  padding: 10px 14px;
  border-radius: var(--r10);
  margin: 6px 0;
  background: var(--bg);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: border-color .15s, background .15s;
}
.title-item:hover { border-color: var(--red); background: var(--red-soft); }
.title-item-text   { font-size: 14px; color: var(--text); font-weight: 600; }
.title-item-method { font-size: 11px; color: var(--text3); margin-top: 4px; }

/* ── FOOTER ── */
.footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: var(--text3);
  border-top: 1px solid var(--border);
  margin-top: 40px;
}

/* ── MOBILE ── */
@media (max-width: 768px) {
  .container   { padding: 18px 16px 80px; }
  .header      { padding: 0 16px; }
  .tab-nav     { padding: 0 8px; }
  .tab-btn     { padding: 12px 12px; font-size: 13px; }
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
  .trend-grid { grid-template-columns: 1fr; }
  .bench-grid { grid-template-columns: 1fr; }
}

/* ── LEGACY COMPAT ── */
.card            { background: var(--card); border: 1px solid var(--border); border-radius: var(--r14); box-shadow: var(--shadow-sm); }
.topic-section   { margin-bottom: 28px; }
.bench-section   { margin-bottom: 32px; }
.check-result    { display: none; }
.check-result.show { display: block; }
.ref-result      { display: none; }
.ref-result.show { display: block; }
.show            { display: block !important; }
</style>"""

NEW_CSS2 = """<style>
/* Tab4 创作工具补充样式 */
.planner-card * { color: inherit; }
</style>"""

# 替换
new_content = content[:s1] + NEW_CSS1 + content[e1:s2] + NEW_CSS2 + content[e2:]

# 同时更新 loading 文字为动效版本
new_content = new_content.replace(
    '<div id="ref-result-loading" style="text-align:center;padding:40px;font-size:14px;color:var(--text2)">\n        <div style="font-size:28px;margin-bottom:12px">🤖</div>\n        正在读取本周行业数据 + 推导你的产品卖点和人群…<br>\n        <span style="font-size:12px;color:var(--text3)">大约需要 15-25 秒</span>\n      </div>',
    '<div id="ref-result-loading" style="text-align:center;padding:48px;font-size:14px;color:var(--text2)">\n        <div style="font-size:32px;margin-bottom:16px">🤖</div>\n        <div style="margin-bottom:10px">正在读取本周行业数据，推导你的产品卖点和人群…</div>\n        <div class="loading-dots"><span></span><span></span><span></span></div>\n        <div style="font-size:12px;color:var(--text3);margin-top:10px">大约需要 15-25 秒</div>\n      </div>'
)

opens  = new_content.count('<style>')
closes = new_content.count('</style>')
print(f'style: {opens} ↔ {closes}')
assert opens == closes, 'style 不平衡'

open('index.html', 'w').write(new_content)
print(f'写入 {len(new_content)} bytes')
