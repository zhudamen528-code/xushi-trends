#!/usr/bin/env python3
"""
注入 V3 UI 设计系统到 index.html
风格参考 Uno：浅灰底 + 大圆角卡 + 彩色色块 + SF Pro 字体体系 + 活泼但克制
"""

content = open('index.html').read()

# ── 1. 注入 Google Font（Inter）+ V3 design token ──
HEAD_INJECT = """  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
"""

# 插到 <style> 前面
content = content.replace('  <style>\n', HEAD_INJECT + '  <style>\n', 1)

# ── 2. 替换 V3 design token（覆盖 LIGHT_CSS 里的 :root）──
OLD_ROOT = """  :root {
    --bg:        #f8f9fa;
    --card-bg:   #ffffff;
    --border:    #e5e7eb;
    --text:      #111827;
    --text-sub:  #6b7280;
    --primary:   #e63950;
    --accent:    #f97316;
    --green:     #059669;
  }
  body { background: #f8f9fa; color: #111827; }"""

NEW_ROOT = """  /* ── V3 Design Token (Uno-inspired) ── */
  :root {
    --bg:        #F2F2F7;
    --card-bg:   #FFFFFF;
    --border:    #E8E8ED;
    --text:      #1C1C1E;
    --text-sub:  #8E8E93;
    --text-ter:  #AEAEB2;
    --primary:   #FF3B4E;
    --accent:    #FF9500;
    --green:     #34C759;
    --blue:      #007AFF;
    --purple:    #AF52DE;
    --r8:        8px;
    --r12:       12px;
    --r16:       16px;
    --r20:       20px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
    font-size: 15px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }"""

assert OLD_ROOT in content, '找不到 ROOT'
content = content.replace(OLD_ROOT, NEW_ROOT)

# ── 3. 彻底重写 header ──
OLD_HEADER_CSS = ".header        { background: #fff; border-bottom: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,.04); }"
NEW_HEADER_CSS = """.header {
    background: #FFFFFF;
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
  }
  .header-left { display: flex; align-items: center; gap: 14px; }
  .header-icon { font-size: 28px; line-height: 1; }
  .header-title { font-size: 17px; font-weight: 800; color: var(--text); letter-spacing: -0.4px; }
  .header-sub { font-size: 12px; color: var(--text-sub); font-weight: 400; margin-top: 1px; }
  .header-week { font-size: 22px; font-weight: 900; letter-spacing: -1px; }
  .header-date { font-size: 11px; font-weight: 500; margin-top: 1px; }"""
content = content.replace(OLD_HEADER_CSS, NEW_HEADER_CSS)

# ── 4. Tab nav 重写 ──
OLD_TABNAV = ".tab-nav  { background: #f3f4f6; border-radius: 10px; }"
NEW_TABNAV = """.tab-nav {
    background: transparent;
    display: flex; gap: 4px;
    padding: 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .tab-nav::-webkit-scrollbar { display: none; }"""
content = content.replace(OLD_TABNAV, NEW_TABNAV)

OLD_TABBTN = ".tab-btn  { color: #6b7280; background: transparent; }"
NEW_TABBTN = """.tab-btn {
    padding: 10px 16px;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    background: transparent;
    color: var(--text-sub);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: color .15s, border-color .15s;
    margin-bottom: -1px;
  }"""
content = content.replace(OLD_TABBTN, NEW_TABBTN)

OLD_TABBTN_HOVER = ".tab-btn:hover  { color: #e63950; background: rgba(230,57,80,.06); }"
NEW_TABBTN_HOVER = ".tab-btn:hover  { color: var(--text); background: transparent; }"
content = content.replace(OLD_TABBTN_HOVER, NEW_TABBTN_HOVER)

OLD_TABBTN_ACTIVE = ".tab-btn.active { color: #e63950; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.08); }"
NEW_TABBTN_ACTIVE = """.tab-btn.active {
    color: var(--primary);
    background: transparent;
    border-bottom-color: var(--primary);
  }"""
content = content.replace(OLD_TABBTN_ACTIVE, NEW_TABBTN_ACTIVE)

# ── 5. 卡片系统重写 ──
OLD_CARD = ".card          { background: #fff; border-color: var(--border); box-shadow: 0 1px 4px rgba(0,0,0,.06); }"
NEW_CARD = """.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: var(--r16);
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
  }"""
content = content.replace(OLD_CARD, NEW_CARD)

# trend-card 重写
content = content.replace(
    '.trend-card { background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb;',
    '.trend-card { background: #FFFFFF; border-radius: var(--r16); overflow: hidden; border: 1px solid var(--border);'
)
content = content.replace(
    '.trend-card:hover { border-color: #d1d5db; box-shadow: 0 4px 16px rgba(0,0,0,.06); }',
    '.trend-card:hover { border-color: #C7C7CC; box-shadow: 0 4px 20px rgba(0,0,0,.08); transform: translateY(-1px); transition: all .2s; }'
)

# trend-head 更圆润
content = content.replace(
    '.trend-head { padding: 12px 14px; font-size: 13px; font-weight: 700; color: #111827;',
    '.trend-head { padding: 14px 16px; font-size: 13px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.2px;'
)

# trend-item 行
content = content.replace(
    '.trend-item { padding: 10px 12px; line-height: 1.55; }',
    '.trend-item { padding: 11px 16px; line-height: 1.6; }'
)
content = content.replace(
    '.trend-item { padding: 10px 14px; border-bottom: 1px solid #f3f4f6; display: flex; gap: 10px; align-items: flex-start; }',
    '.trend-item { padding: 11px 16px; border-bottom: 1px solid #F2F2F7; display: flex; gap: 10px; align-items: flex-start; }'
)
content = content.replace(
    '.trend-num { flex-shrink: 0; width: 20px; height: 20px; border-radius: 50%; background: #f3f4f6; color: #9ca3af;',
    '.trend-num { flex-shrink: 0; width: 22px; height: 22px; border-radius: 50%; background: rgba(0,0,0,.06); color: var(--text-sub);'
)
content = content.replace(
    '.trend-text { font-size: 12px; color: #374151; line-height: 1.5; }',
    '.trend-text { font-size: 13px; color: var(--text); line-height: 1.6; }'
)

# ── 6. section-label 升级 ──
content = content.replace(
    '.section-label { font-size: 13px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1.5px; display: flex; align-items: center; gap: 8px; margin-bottom: 14px; padding-bottom: 10px;',
    '.section-label { font-size: 11px; font-weight: 700; color: var(--text-ter); text-transform: uppercase; letter-spacing: 2px; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; padding-bottom: 12px;'
)
content = content.replace(
    ".tag           { background: #f3f4f6; color: #6b7280; border: none; }",
    ".tag           { background: rgba(0,0,0,.05); color: var(--text-sub); border-radius: 20px; padding: 2px 10px; font-size: 11px; font-weight: 600; }"
)

# ── 7. 方法论卡片升级 ──
content = content.replace(
    ".method-card  { background: #fff; border-color: var(--border); }",
    ".method-card  { background: #FFFFFF; border-color: var(--border); border-radius: var(--r16) !important; transition: box-shadow .2s, transform .2s; }"
)
content = content.replace(
    ".method-card:hover { border-color: rgba(37,99,235,.3); }",
    ".method-card:hover { border-color: #C7C7CC; box-shadow: 0 4px 20px rgba(0,0,0,.08); transform: translateY(-1px); }"
)
content = content.replace(
    ".method-card.open  { border-color: rgba(37,99,235,.4); }",
    ".method-card.open  { border-color: var(--primary); box-shadow: 0 4px 20px rgba(255,59,78,.1); }"
)
content = content.replace(
    ".method-num   { background: rgba(37,99,235,.1); color: var(--primary); }",
    ".method-num   { background: var(--primary); color: #FFFFFF; }"
)
content = content.replace(
    ".method-title { color: var(--text); }",
    ".method-title { color: var(--text); font-size: 15px; font-weight: 700; letter-spacing: -0.2px; }"
)
content = content.replace(
    ".method-badge { background: rgba(37,99,235,.07); color: var(--primary); }",
    ".method-badge { background: rgba(255,59,78,.08); color: var(--primary); font-weight: 700; }"
)
content = content.replace(
    ".method-head:hover { background: rgba(37,99,235,.04); }",
    ".method-head:hover { background: rgba(0,0,0,.02); }"
)
content = content.replace(
    ".method-why-text { font-size:13px; line-height:1.6; padding:10px 14px; border-radius:8px; border-left:3px solid rgba(255,36,66,.35); background:rgba(255,36,66,.03); }",
    ".method-why-text { font-size:13px; line-height:1.7; padding:12px 14px; border-radius:var(--r8); border-left:3px solid var(--primary); background:rgba(255,59,78,.04); color:var(--text); }"
)
content = content.replace(
    ".method-case  { background: #f8f9fc; border-color: var(--border); }",
    ".method-case  { background: #F2F2F7; border-color: transparent; border-radius:var(--r8) !important; }"
)
content = content.replace(
    ".method-case-text  { color: var(--text); }",
    ".method-case-text  { color: var(--text); font-size:13px; line-height:1.7; }"
)

# ── 8. 按钮系统升级 ──
content = content.replace(
    ".btn-gen-main { background: #e63950; }",
    ".btn-gen-main { background: var(--primary); color:#fff; border:none; border-radius:var(--r12); padding:14px 28px; font-size:15px; font-weight:700; cursor:pointer; width:100%; margin-top:18px; letter-spacing:-0.2px; transition: opacity .15s, transform .1s; }"
)
content = content.replace(
    ".btn-gen-main:disabled { opacity: .5; cursor: not-allowed; }",
    ".btn-gen-main:hover { opacity:.9; } .btn-gen-main:active { transform:scale(.99); } .btn-gen-main:disabled { opacity:.4; cursor:not-allowed; }"
)
content = content.replace(
    ".btn-gen       { background: #e63950; }",
    ".btn-gen { padding:12px 22px; background:var(--primary); color:#fff; border:none; border-radius:var(--r12); font-size:14px; font-weight:700; cursor:pointer; font-family:inherit; transition:opacity .15s; }"
)
content = content.replace(
    ".btn-gen.btn-doubao { background: #374151; }",
    ".btn-gen.btn-doubao { background: var(--text); }"
)
content = content.replace(
    ".btn-copy { padding: 12px 20px; background: #f9fafb; color: #374151; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: inherit; transition: all .15s; }",
    ".btn-copy { padding:12px 20px; background:#F2F2F7; color:var(--text-sub); border:none; border-radius:var(--r12); font-size:14px; font-weight:600; cursor:pointer; font-family:inherit; transition:background .15s; }"
)

# ── 9. 表单升级 ──
content = content.replace(
    ".form-input { width: 100%; padding: 10px 14px; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 14px; font-family: inherit; outline: none; transition: border-color 0.2s, box-shadow 0.2s; background: #fff; color: #111827; }",
    ".form-input { width:100%; padding:12px 14px; border:1.5px solid var(--border); border-radius:var(--r12); font-size:14px; font-family:inherit; outline:none; background:#fff; color:var(--text); transition:border-color .15s, box-shadow .15s; }"
)
content = content.replace(
    ".form-input:focus { border-color: #e63950; box-shadow: 0 0 0 3px rgba(230,57,80,.08); }",
    ".form-input:focus { border-color:var(--primary); box-shadow:0 0 0 3px rgba(255,59,78,.08); }"
)
content = content.replace(
    ".form-label { font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; display: block; }",
    ".form-label { font-size:13px; font-weight:600; color:var(--text-sub); margin-bottom:8px; display:block; }"
)
content = content.replace(
    ".cat-radio span { padding: 6px 14px; border-radius: 20px; border: 1px solid #e5e7eb; font-size: 13px; color: #6b7280; cursor: pointer; display: inline-block; transition: all 0.15s; background: #fff; }",
    ".cat-radio span { padding:7px 14px; border-radius:20px; border:1.5px solid var(--border); font-size:13px; color:var(--text-sub); cursor:pointer; display:inline-block; transition:all .15s; background:#fff; font-weight:500; }"
)
content = content.replace(
    ".cat-radio input:checked + span { background: #fef2f3; border-color: #e63950; color: #e63950; }",
    ".cat-radio input:checked + span { background:rgba(255,59,78,.08); border-color:var(--primary); color:var(--primary); font-weight:700; }"
)

# ── 10. Tab3 表单按钮升级 ──
content = content.replace(
    ".cat-l1-btn { padding:10px 18px; border-radius:10px; border:1px solid; cursor:pointer; font-size:14px; font-weight:600; transition:all .2s; }",
    ".cat-l1-btn { padding:10px 18px; border-radius:var(--r12); border:1.5px solid var(--border); cursor:pointer; font-size:14px; font-weight:600; transition:all .15s; background:#fff; color:var(--text); }"
)
content = content.replace(
    ".cat-l1-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }",
    ".cat-l1-btn.active { border-color:var(--primary); color:var(--primary); background:rgba(255,59,78,.07); }"
)
content = content.replace(
    ".cat-l2-btn { border-color: var(--border); color: var(--text-sub); }",
    ".cat-l2-btn { padding:7px 14px; border-radius:20px; border:1.5px solid var(--border); cursor:pointer; font-size:13px; color:var(--text-sub); background:#fff; font-weight:500; transition:all .15s; }"
)
content = content.replace(
    ".cat-l2-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }",
    ".cat-l2-btn.active { border-color:var(--primary); color:var(--primary); background:rgba(255,59,78,.07); font-weight:700; }"
)
content = content.replace(
    ".price-btn  { border-color: var(--border); color: var(--text-sub); }",
    ".price-btn  { padding:8px 16px; border-radius:20px; border:1.5px solid var(--border); cursor:pointer; font-size:13px; color:var(--text-sub); background:#fff; font-weight:500; transition:all .15s; }"
)
content = content.replace(
    ".price-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }",
    ".price-btn.active { border-color:var(--primary); color:var(--primary); background:rgba(255,59,78,.07); font-weight:700; }"
)
content = content.replace(
    ".aud-btn    { border-color: var(--border); color: var(--text-sub); }",
    ".aud-btn    { padding:6px 13px; border-radius:20px; border:1.5px solid var(--border); cursor:pointer; font-size:12px; color:var(--text-sub); background:#fff; font-weight:500; transition:all .15s; }"
)
content = content.replace(
    ".aud-btn.active { border-color: rgba(124,58,237,.4); color: var(--accent); background: rgba(124,58,237,.07); }",
    ".aud-btn.active { border-color:var(--purple); color:var(--purple); background:rgba(175,82,222,.08); font-weight:700; }"
)

# ref-card 升级
content = content.replace(
    ".ref-card   { background: #fff; border-color: var(--border); }",
    ".ref-card   { background: #FFFFFF; border:1px solid var(--border); border-radius:var(--r16); padding:18px; }"
)
content = content.replace(
    ".ref-card-title { color: var(--text-sub); }",
    ".ref-card-title { color: var(--text-sub); font-size:11px; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:12px; }"
)
content = content.replace(
    ".ref-tag    { background: rgba(37,99,235,.07); border-color: rgba(37,99,235,.12); color: var(--primary); }",
    ".ref-tag    { display:inline-block; margin:3px; padding:5px 12px; border-radius:20px; border:none; font-size:12px; background:rgba(255,59,78,.08); color:var(--primary); font-weight:600; }"
)
content = content.replace(
    ".ref-template { border-radius:8px; padding:10px 12px; margin:6px 0; font-size:12px; line-height:1.6; }",
    ".ref-template { border-radius:var(--r8); padding:12px 14px; margin:6px 0; font-size:13px; line-height:1.6; background:#F2F2F7; color:var(--text); }"
)
content = content.replace(
    ".ref-template .example { font-size:11px; margin-top:4px; }",
    ".ref-template .example { font-size:12px; margin-top:6px; color:var(--text-sub); }"
)
content = content.replace(
    ".ref-case   { border:1px solid; border-radius:8px; padding:10px 12px; margin:6px 0; }",
    ".ref-case   { border:1px solid var(--border); border-radius:var(--r12); padding:12px 14px; margin:6px 0; }"
)
content = content.replace(
    ".btn-refresh  { flex:1; border-radius:8px; padding:10px; font-size:13px; cursor:pointer; }",
    ".btn-refresh  { flex:1; border-radius:var(--r12); padding:11px; font-size:13px; cursor:pointer; background:#F2F2F7; border:none; color:var(--text-sub); font-weight:600; }"
)
content = content.replace(
    ".btn-copy-all { flex:1; border-radius:8px; padding:10px; font-size:13px; cursor:pointer; }",
    ".btn-copy-all { flex:1; border-radius:var(--r12); padding:11px; font-size:13px; cursor:pointer; background:rgba(255,59,78,.08); border:none; color:var(--primary); font-weight:700; }"
)

# ── 11. 创作工具卡片升级 ──
content = content.replace(
    ".planner-card { background: #ffffff; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; }",
    ".planner-card { background: #FFFFFF; border-radius: var(--r20); border: 1px solid var(--border); overflow: hidden; margin-bottom: 16px; }"
)
content = content.replace(
    ".planner-intro { background: #f9fafb;",
    ".planner-intro { background: #F2F2F7;"
)
content = content.replace(
    ".prompt-preview { margin: 0 24px 24px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; }",
    ".prompt-preview { margin: 0 24px 24px; background: #F2F2F7; border: none; border-radius: var(--r12); padding: 14px; }"
)

# lingxi-card
content = content.replace(
    ".lingxi-card  { border-radius:10px; border:1px solid; padding:14px; display:flex; align-items:center; gap:10px; cursor:pointer; transition:border-color .2s; }",
    ".lingxi-card  { border-radius:var(--r16); border:1.5px solid var(--border); padding:16px; display:flex; align-items:center; gap:12px; cursor:pointer; transition:all .2s; background:#fff; }"
)
content = content.replace(
    ".lingxi-card:hover { border-color: rgba(37,99,235,.3); }",
    ".lingxi-card:hover { border-color:var(--primary); background:rgba(255,59,78,.03); transform:translateY(-1px); box-shadow:0 4px 16px rgba(0,0,0,.06); }"
)
content = content.replace(
    ".lingxi-info .name { font-size:13px; font-weight:600; }",
    ".lingxi-info .name { font-size:14px; font-weight:700; color:var(--text); }"
)
content = content.replace(
    ".lingxi-info .desc { font-size:12px; margin-top:2px; }",
    ".lingxi-info .desc { font-size:12px; margin-top:3px; color:var(--text-sub); }"
)

# ── 12. 体检模块升级 ──
content = content.replace(
    ".check-module { border-radius:12px; border:1px solid; padding:18px; margin-bottom:14px; }",
    ".check-module { border-radius:var(--r16); border:1px solid var(--border); padding:20px; margin-bottom:14px; background:#fff; }"
)
content = content.replace(
    ".check-form   { border-radius:14px; border:1px solid; padding:20px; margin-bottom:20px; }",
    ".check-form   { border-radius:var(--r20); border:1px solid var(--border); padding:22px; margin-bottom:20px; background:#fff; }"
)
content = content.replace(
    ".check-score  { text-align:center; padding:16px; border-radius:10px; margin-bottom:12px; background:rgba(255,36,66,.04); }",
    ".check-score  { text-align:center; padding:20px; border-radius:var(--r12); margin-bottom:12px; background:#F2F2F7; }"
)
content = content.replace(
    ".check-score-num { font-size:36px; font-weight:800; color:var(--primary); }",
    ".check-score-num { font-size:40px; font-weight:900; color:var(--primary); letter-spacing:-2px; }"
)
content = content.replace(
    ".check-top-tip { border:1px solid; border-radius:8px; padding:10px 14px; font-size:13px; line-height:1.6; margin-top:10px; }",
    ".check-top-tip { border:none; border-radius:var(--r12); padding:12px 16px; font-size:13px; line-height:1.6; margin-top:12px; background:rgba(255,149,0,.1); color:var(--accent); font-weight:500; }"
)

# ── 13. NOTE CARD (TOP 笔记) 升级 ──
content = content.replace(
    ".note-card { background: #ffffff; border: 1px solid #e5e7eb;",
    ".note-card { background: #FFFFFF; border: 1px solid var(--border);"
)
content = content.replace(
    ".note-card:hover { border-color: #d1d5db; box-shadow: 0 4px 12px rgba(0,0,0,.08); }",
    ".note-card:hover { border-color: #C7C7CC; box-shadow: 0 6px 24px rgba(0,0,0,.1); transform: translateY(-2px); transition: all .2s; }"
)

# ── 14. sgld-card (三感六度) ──
content = content.replace(
    ".sgld-card  { background: #fff; border-color: var(--border); }",
    ".sgld-card  { background: #FFFFFF; border: 1px solid var(--border); border-radius: var(--r20); padding: 24px; margin-top: 20px; }"
)
content = content.replace(
    ".sgld-btn   { background: rgba(5,150,105,.1); color: var(--green); border-color: rgba(5,150,105,.25); }",
    ".sgld-btn   { background: rgba(52,199,89,.12); color: var(--green); border: none; border-radius: var(--r12); padding: 10px 18px; font-size: 13px; font-weight: 700; cursor: pointer; transition: background .15s; }"
)

# ── 15. 容器宽度 ──
content = content.replace(
    ".container { max-width: 1100px !important; padding: 28px 28px 80px !important; }",
    ".container { max-width: 1080px !important; padding: 24px 24px 80px !important; }"
)

# ── 16. header week/date 颜色更新 ──
content = content.replace(
    'style="color:#e63950"',
    'style="color:var(--primary)"'
)
content = content.replace(
    'style="color:#6b7280"',
    'style="color:var(--text-sub)"'
)

# ── 17. ref-form + ref-intro 背景 ──
content = content.replace(
    ".ref-form   { background: #fff; border-color: var(--border); }",
    ".ref-form   { background: #FFFFFF; border: 1px solid var(--border); border-radius: var(--r20); padding: 22px; margin-bottom: 20px; }"
)
content = content.replace(
    ".ref-intro  { background: rgba(37,99,235,.04); border-color: rgba(37,99,235,.2); color: var(--text-sub); }",
    ".ref-intro  { background: #F2F2F7; border: none; border-radius: var(--r12); color: var(--text-sub); line-height: 1.7; margin-bottom: 24px; padding: 14px 18px; font-size: 14px; }"
)

# ── 18. 热门话题标签统一 ──
content = content.replace(
    ".hot-tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; margin: 2px; border: 1px solid; background: #f9fafb !important; color: #374151 !important; border-color: #e5e7eb !important; }",
    ".hot-tag { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin: 3px; border: none; background: rgba(0,0,0,.06); color: var(--text); }"
)

# ── 19. formula-card 升级 ──
content = content.replace(
    ".formula-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; }",
    ".formula-card { background: #FFFFFF; border: 1px solid var(--border); border-radius: var(--r16); padding: 18px; }"
)

open('index.html', 'w').write(content)

import re
opens = content.count('<style>')
closes = content.count('</style>')
print(f'style: {opens} ↔ {closes}')
print(f'写入: {len(content)} bytes')
