#!/usr/bin/env python3
# 构建 V2 index.html — 干净版（无拼接 bug）
import sys, json

lines = open('index_v1_backup.html').readlines()

def get(s, e):  # 1-indexed, inclusive
    return ''.join(lines[s-1:e])

css1        = get(16, 599)    # 主 CSS（不含 </style>）
css2        = get(1080, 1209) # tools CSS（含 <style>...</style> 包装）
trends_body = get(698, 893)   # 风向卡片~TOP笔记格
tools_html  = get(895, 1039)  # 创作工具 HTML
top_notes   = get(1213, 1235) # TOP_NOTES 数组定义
build_prompt= get(1354, 1435) # buildPrompt()
update_prev = get(1437, 1497) # updatePreview + 事件绑定（不含 switchTab）
build_cover = get(1507, 1598) # buildCoverPrompt()
api_keys    = get(1599, 1601) # _ak / _enc / _key
run_audit   = get(1609, 1690) # runAudit() V1

# 验证括号
for name, s in [('build_prompt', build_prompt), ('update_prev', update_prev),
                ('build_cover', build_cover), ('run_audit', run_audit)]:
    ob, cb = s.count('{'), s.count('}')
    if ob != cb:
        print(f'WARN {name}: open={ob} close={cb}', file=sys.stderr)

# ── 浅色调设计 token ──
LIGHT_CSS = """
  :root {
    --bg:        #f5f6fa;
    --card-bg:   #ffffff;
    --border:    #e2e5ef;
    --text:      #1a1d2e;
    --text-sub:  #6b7280;
    --primary:   #2563eb;
    --accent:    #7c3aed;
    --green:     #059669;
  }
  body { background: var(--bg); color: var(--text); }

  /* 覆盖 V1 深色 token */
  .header        { background: #fff; border-bottom: 1px solid var(--border); box-shadow: 0 1px 6px rgba(0,0,0,.06); }
  .header-title  { color: var(--text); }
  .header-sub    { color: var(--text-sub); }
  .header-week   { color: var(--primary) !important; text-shadow: none !important; }
  .header-date   { color: var(--text-sub) !important; }
  .container     { background: var(--bg); }
  .card          { background: #fff; border-color: var(--border); box-shadow: 0 1px 4px rgba(0,0,0,.06); }
  .section-label { color: var(--text); border-color: var(--border); }
  .tag           { background: rgba(37,99,235,.08); color: var(--primary); }
  .trend-item    { background: #fff; border-color: var(--border); }
  .trend-num     { background: rgba(37,99,235,.1); color: var(--primary); }
  .hot-tag       { background: rgba(37,99,235,.08); color: var(--primary); border-color: rgba(37,99,235,.15); }
  .note-card     { background: #fff; border-color: var(--border); }
  .note-title    { color: var(--text); }
  .note-meta     { color: var(--text-sub); }
  .note-tag      { background: rgba(37,99,235,.07); color: var(--primary); border-color: rgba(37,99,235,.12); }
  .planner-card  { background: #fff; border-color: var(--border); }
  .planner-intro { color: var(--text-sub); }
  .form-label    { color: var(--text-sub); }
  .form-input    { background: #f8f9fc; border-color: var(--border); color: var(--text); }
  .form-input:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }
  .cat-radio span { color: var(--text-sub); }
  .cat-radio input:checked + span { color: var(--primary); }
  .btn-gen       { background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); }
  .btn-doubao    { background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%); }
  .btn-copy      { background: #f1f5f9; color: var(--text-sub); border-color: var(--border); }
  .btn-copy:hover{ background: #e2e8f0; }
  .prompt-preview{ background: #f8f9fc; border-color: var(--border); }
  .prompt-label  { color: var(--text-sub); }
  .prompt-text   { color: var(--text); }
  .audit-result  { background: #f8f9fc; border-color: var(--border); }

  /* Tab nav */
  .tab-nav  { background: #eef0f8; }
  .tab-btn  { color: var(--text-sub); }
  .tab-btn:hover  { color: var(--primary); background: rgba(37,99,235,.06); }
  .tab-btn.active { color: var(--primary); background: #fff;
                    box-shadow: 0 1px 6px rgba(37,99,235,.12); }

  /* 方法论 */
  .method-card  { background: #fff; border-color: var(--border); }
  .method-card:hover { border-color: rgba(37,99,235,.3); }
  .method-card.open  { border-color: rgba(37,99,235,.4); }
  .method-num   { background: rgba(37,99,235,.1); color: var(--primary); }
  .method-title { color: var(--text); }
  .method-badge { background: rgba(37,99,235,.07); color: var(--primary); }
  .method-arrow { color: var(--text-sub); }
  .method-body  { border-color: var(--border); }
  .method-why-text { background: rgba(37,99,235,.04); border-color: rgba(37,99,235,.2);
                     color: var(--text-sub); }
  .method-how-list li { color: var(--text-sub); }
  .method-how-list li::before { color: var(--accent); }
  .method-case  { background: #f8f9fc; border-color: var(--border); }
  .method-case-label { color: var(--text-sub); }
  .method-case-text  { color: var(--text); }

  /* 三感六度 */
  .sgld-card  { background: #fff; border-color: var(--border); }
  .sgld-title { color: var(--text); }
  .sgld-desc  { color: var(--text-sub); }
  .sgld-dim   { background: rgba(5,150,105,.07); color: var(--green);
                border-color: rgba(5,150,105,.18); }
  .sgld-btn   { background: rgba(5,150,105,.1); color: var(--green);
                border-color: rgba(5,150,105,.25); }

  /* Tab3 我的内容参考 */
  .ref-intro  { background: rgba(37,99,235,.04); border-color: rgba(37,99,235,.2);
                color: var(--text-sub); }
  .cat-l1-btn { background: #fff; border-color: var(--border); color: var(--text-sub); }
  .cat-l1-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }
  .cat-l2-btn { border-color: var(--border); color: var(--text-sub); }
  .cat-l2-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }
  .ref-form   { background: #fff; border-color: var(--border); }
  .price-btn  { border-color: var(--border); color: var(--text-sub); }
  .price-btn.active { border-color: rgba(37,99,235,.4); color: var(--primary); background: rgba(37,99,235,.07); }
  .aud-btn    { border-color: var(--border); color: var(--text-sub); }
  .aud-btn.active { border-color: rgba(124,58,237,.4); color: var(--accent); background: rgba(124,58,237,.07); }
  .btn-gen-main { background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); }
  .ref-card   { background: #fff; border-color: var(--border); }
  .ref-card-title { color: var(--text-sub); }
  .ref-tag    { background: rgba(37,99,235,.07); border-color: rgba(37,99,235,.12); color: var(--primary); }
  .ref-template { background: #f8f9fc; color: var(--text); }
  .ref-template .example { color: var(--text-sub); }
  .ref-case   { border-color: var(--border); }
  .ref-case-title { color: var(--text); }
  .ref-case-meta  { color: var(--text-sub); }
  .ref-case-note  { color: var(--primary); }
  .btn-refresh  { border-color: var(--border); color: var(--text-sub); }
  .btn-copy-all { background: rgba(37,99,235,.08); border-color: rgba(37,99,235,.15); color: var(--primary); }

  /* Tab5 体检 */
  .check-form  { background: #fff; border-color: var(--border); }
  .check-module { background: #fff; border-color: var(--border); }
  .check-module-title { color: var(--text-sub); }
  .check-comment { color: var(--text-sub); }
  .check-score { background: rgba(37,99,235,.05); }
  .check-score-num { color: var(--primary); }
  .check-top-tip { background: rgba(124,58,237,.06); border-color: rgba(124,58,237,.15); color: var(--accent); }
  .bench-label-sm { color: var(--text-sub); }
  .bench-val-sm .num { color: var(--text); }
  .bench-val-sm .lab { color: var(--text-sub); }

  /* 创作工具升级 */
  .tool-result-area { background: rgba(37,99,235,.04); border-color: rgba(37,99,235,.1); }
  .tool-result-text { color: var(--text); }
  .title-item { background: #f8f9fc; }
  .title-item:hover { background: rgba(37,99,235,.06); }
  .title-item-text   { color: var(--text); }
  .title-item-method { color: rgba(37,99,235,.6); }
  .lingxi-card { background: #fff; border-color: var(--border); }
  .lingxi-card:hover { border-color: rgba(37,99,235,.3); }
  .lingxi-info .name { color: var(--text); }
  .lingxi-info .desc { color: var(--text-sub); }

  /* ── PC 端布局优化 ── */
  .container { max-width: 1280px !important; padding: 28px 32px 80px !important; }

  /* 方法论：PC 端 2 列 */
  @media (min-width: 900px) {
    .method-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  }

  /* Tab3 卡片：PC 端 3 列（人群/买点单列，标题/案例横跨） */
  @media (min-width: 900px) {
    .ref-cards { grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
    .ref-cards .ref-card:nth-child(3),
    .ref-cards .ref-card:nth-child(4) { grid-column: 1 / -1; }
  }

  /* 灵犀：PC 端 4 列 */
  @media (min-width: 768px) {
    .lingxi-grid { grid-template-columns: repeat(4, 1fr); }
  }

  /* Tab5 体检模块：PC 端 2 列 */
  @media (min-width: 900px) {
    .check-result {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      align-items: start;
    }
    .check-result .check-module:first-child { grid-column: 1 / -1; }
  }

  /* Tab4 创作工具：PC 端 2 列布局 */
  @media (min-width: 900px) {
    #tab-tools .planner-card { max-width: 100%; }
    #tab-tools .section-label { margin-top: 24px; }
  }

  /* Tab nav PC 端 */
  @media (min-width: 768px) {
    .tab-nav { max-width: fit-content; }
    .tab-btn { font-size: 14px; padding: 10px 20px; }
  }

  /* 风向卡更通透 */
  .trend-item { padding: 10px 12px; line-height: 1.55; }
"""

# ── V2 新增组件 CSS ──
V2_COMPONENT_CSS = """
  .tab-nav { display:flex; gap:6px; margin-bottom:28px; padding:4px; border-radius:12px; flex-wrap:wrap; }
  .tab-btn { font-size:13px; padding:9px 16px; border-radius:8px; border:none; cursor:pointer; font-weight:600; transition:all .2s; white-space:nowrap; }
  .tab-panel.hidden { display:none !important; }

  .method-cards { display:flex; flex-direction:column; gap:16px; }
  .method-card  { border-radius:14px; border:1px solid; overflow:hidden; cursor:pointer; transition:border-color .2s; }
  .method-head  { display:flex; align-items:center; gap:12px; padding:18px 20px; }
  .method-num   { width:28px; height:28px; border-radius:50%; font-size:13px; font-weight:700; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
  .method-title { font-size:15px; font-weight:700; flex:1; }
  .method-badge { font-size:11px; padding:2px 8px; border-radius:20px; }
  .method-arrow { font-size:14px; transition:transform .2s; }
  .method-card.open .method-arrow { transform:rotate(90deg); }
  .method-body  { display:none; padding:0 20px 20px; border-top:1px solid; }
  .method-card.open .method-body { display:block; }
  .method-why   { margin-top:14px; }
  .method-why-label,.method-how-label { font-size:11px; font-weight:700; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px; }
  .method-why-label { color:rgba(37,99,235,.5); }
  .method-how-label { color:rgba(124,58,237,.5); }
  .method-why-text { font-size:13px; line-height:1.6; padding:10px 14px; border-radius:8px; border-left:2px solid; }
  .method-how { margin-top:14px; }
  .method-how-list { list-style:none; padding:0; }
  .method-how-list li { font-size:13px; padding:4px 0 4px 16px; position:relative; }
  .method-how-list li::before { content:"·"; position:absolute; left:0; }
  .method-case { margin-top:14px; border-radius:8px; padding:12px 14px; border:1px solid; }
  .method-case-label { font-size:11px; font-weight:700; margin-bottom:6px; }
  .method-case-text  { font-size:13px; line-height:1.6; }

  .sgld-card  { border-radius:14px; border:1px solid; padding:22px; margin-top:16px; }
  .sgld-title { font-size:14px; font-weight:700; margin-bottom:8px; }
  .sgld-desc  { font-size:13px; margin-bottom:14px; line-height:1.6; }
  .sgld-dims  { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:16px; }
  .sgld-dim   { font-size:12px; padding:4px 10px; border-radius:20px; border:1px solid; }
  .sgld-btn   { border:1px solid; border-radius:8px; padding:8px 16px; font-size:13px; font-weight:600; cursor:pointer; }

  .ref-intro  { font-size:14px; line-height:1.7; margin-bottom:24px; padding:14px 18px; border-radius:10px; border-left:3px solid; }
  .cat-l1-grid { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:20px; }
  .cat-l1-btn { padding:10px 18px; border-radius:10px; border:1px solid; cursor:pointer; font-size:14px; font-weight:600; transition:all .2s; }
  .cat-l2-area { display:none; margin-bottom:20px; }
  .cat-l2-area.show { display:block; }
  .cat-l2-grid { display:flex; gap:8px; flex-wrap:wrap; }
  .cat-l2-btn { padding:7px 14px; border-radius:20px; border:1px solid; cursor:pointer; font-size:13px; transition:all .2s; }
  .cat-l2-btn.disabled { opacity:.4; cursor:not-allowed; }
  .ref-form   { border-radius:14px; border:1px solid; padding:20px; margin-bottom:20px; }
  .price-btns { display:flex; gap:8px; flex-wrap:wrap; }
  .price-btn  { padding:7px 14px; border-radius:20px; border:1px solid; cursor:pointer; font-size:13px; transition:all .2s; }
  .audience-grid { display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }
  .aud-btn    { padding:6px 12px; border-radius:16px; border:1px solid; cursor:pointer; font-size:12px; transition:all .2s; }
  .btn-gen-main { color:#fff; border:none; border-radius:10px; padding:12px 28px; font-size:14px; font-weight:700; cursor:pointer; width:100%; margin-top:16px; }
  .btn-gen-main:disabled { opacity:.5; cursor:not-allowed; }
  .ref-result { display:none; }
  .ref-result.show { display:block; }
  .ref-cards  { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  @media(max-width:600px){ .ref-cards { grid-template-columns:1fr; } }
  .ref-card   { border-radius:12px; border:1px solid; padding:16px; }
  .ref-card-title { font-size:12px; font-weight:700; margin-bottom:10px; text-transform:uppercase; letter-spacing:1px; display:flex; align-items:center; gap:6px; }
  .ref-tag    { display:inline-block; margin:3px; padding:4px 10px; border-radius:14px; border:1px solid; font-size:12px; }
  .ref-template { border-radius:8px; padding:10px 12px; margin:6px 0; font-size:12px; line-height:1.6; }
  .ref-template .example { font-size:11px; margin-top:4px; }
  .ref-case   { border:1px solid; border-radius:8px; padding:10px 12px; margin:6px 0; }
  .ref-case-title { font-size:12px; font-weight:600; margin-bottom:4px; }
  .ref-case-meta  { font-size:11px; }
  .ref-case-note  { font-size:11px; margin-top:4px; }
  .ref-actions { display:flex; gap:8px; margin-top:16px; }
  .btn-refresh  { flex:1; border-radius:8px; padding:10px; font-size:13px; cursor:pointer; }
  .btn-copy-all { flex:1; border-radius:8px; padding:10px; font-size:13px; cursor:pointer; }

  .check-form   { border-radius:14px; border:1px solid; padding:20px; margin-bottom:20px; }
  .check-result { display:none; }
  .check-result.show { display:block; }
  .check-module { border-radius:12px; border:1px solid; padding:18px; margin-bottom:14px; }
  .check-module-title { font-size:13px; font-weight:700; margin-bottom:14px; text-transform:uppercase; letter-spacing:1px; }
  .check-item   { display:flex; align-items:flex-start; gap:10px; padding:8px 0; border-bottom:1px solid rgba(0,0,0,.05); }
  .check-item:last-child { border-bottom:none; }
  .check-icon   { font-size:16px; flex-shrink:0; margin-top:1px; }
  .check-label  { font-size:13px; font-weight:600; flex:0 0 110px; }
  .check-comment { font-size:13px; flex:1; line-height:1.5; }
  .check-score  { text-align:center; padding:16px; border-radius:10px; margin-bottom:12px; }
  .check-score-num   { font-size:36px; font-weight:800; }
  .check-score-label { font-size:12px; margin-top:4px; }
  .check-top-tip { border:1px solid; border-radius:8px; padding:10px 14px; font-size:13px; line-height:1.6; margin-top:10px; }
  .bench-row-small { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(0,0,0,.05); }
  .bench-row-small:last-child { border-bottom:none; }
  .bench-vals  { display:flex; gap:20px; }
  .bench-val-sm .num { font-size:14px; font-weight:700; }
  .bench-val-sm .lab { font-size:10px; }

  .tool-section  { margin-bottom:28px; }
  .tool-result-area { display:none; margin-top:14px; border-radius:10px; border:1px solid; padding:14px; }
  .tool-result-area.show { display:block; }
  .tool-result-text { font-size:13px; line-height:1.8; white-space:pre-wrap; }
  .title-item   { border-radius:8px; padding:10px 14px; margin:6px 0; cursor:pointer; transition:background .2s; }
  .title-item-text   { font-size:13px; }
  .title-item-method { font-size:11px; margin-top:4px; }
  .lingxi-grid  { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:4px; }
  @media(max-width:500px){ .lingxi-grid { grid-template-columns:1fr; } }
  .lingxi-card  { border-radius:10px; border:1px solid; padding:14px; display:flex; align-items:center; gap:10px; cursor:pointer; transition:border-color .2s; }
  .lingxi-icon  { font-size:22px; }
  .lingxi-info .name { font-size:13px; font-weight:600; }
  .lingxi-info .desc { font-size:12px; margin-top:2px; }

  @media(max-width:600px){
    .tab-btn { font-size:12px; padding:8px 10px; }
  }
"""

# ── 知识包 JS (不用 f-string，直接写) ──
KNOWLEDGE_JS = r"""
  const KNOWLEDGE = {
    "candy_chocolate": {
      name: "糖果巧克力", l1: "零食",
      audiences: [
        {id:"gift",   label:"节日送礼",       price_bands:["80-200",">200"], keywords:["伴手礼","礼盒","送人","节日"]},
        {id:"daily",  label:"自己吃/日常解馋", price_bands:["<30","30-80"],   keywords:["日常","解馋","囤货","零食"]},
        {id:"kids",   label:"给孩子/宝妈",     price_bands:["30-80","80-200"],keywords:["儿童","宝宝","无添加","孩子"]},
        {id:"office", label:"办公室零食",       price_bands:["<30","30-80"],   keywords:["办公室","下午茶","同事","茶歇"]},
        {id:"diet",   label:"减脂期/低卡",     price_bands:["30-80","80-200"],keywords:["低卡","低糖","代糖","减脂","控糖"]}
      ],
      selling_points_by_band: {
        "<30":    ["散装实惠","量大管饱","性价比高","日常囤货首选","同款超市要贵3倍"],
        "30-80":  ["0蔗糖添加","精选可可脂","进口原料","网红同款","颜值超高"],
        "80-200": ["比利时进口巧克力","手工制作限量","联名限定礼盒","品牌旗舰","送人倍有面"],
        ">200":   ["顶级原料可可脂","手工定制礼盒","明星同款","奢华包装","企业伴手礼首选"]
      },
      title_templates: [
        {t:"「{产品}让我的{节日}送礼不再为难」",            fit:["gift"],             example:"「费列罗让我的生日送礼不再为难」"},
        {t:"「宿舍/办公室{场景}，这款{产品}藏不住了」",     fit:["office","daily"],   example:"「宿舍深夜解馋，这款松露巧克力藏不住了」"},
        {t:"「{人群}必囤！{产品}{卖点}还不到{价格}」",      fit:["daily","diet"],     example:"「减脂人必囤！这款0蔗糖巧克力还不到30元」"},
        {t:"「妈呀！{产品}真的{效果描述}」",                fit:["daily","gift","kids"],example:"「妈呀！这款草莓夹心巧克力真的太治愈了」"},
        {t:"「收到{产品}当时就{情绪反应}了...」",           fit:["gift"],             example:"「收到这盒手工巧克力当时就哭了...」"},
        {t:"「不允许你们不知道！{产品}{卖点}」",            fit:["daily","office"],   example:"「不允许你们不知道！这款0卡糖比正装便宜一半」"},
        {t:"「{价格}买到{同类贵价产品}同款品质」",          fit:["daily"],            example:"「30块买到百元同款巧克力品质，我哭了」"},
        {t:"「联名上新！{品牌A}×{品牌B}这次真的{卖点}」",  fit:["gift"],             example:"「联名上新！彩虹糖×心动小镇这次真的绝了」"},
        {t:"「{人群特征}的姐妹注意！{产品}让你{改变}」",   fit:["diet","kids"],      example:"「想控糖的姐妹注意！这款低GI巧克力让你解馋不怕胖」"},
        {t:"「{时间/情境}只想吃{产品}，{原因}」",           fit:["daily","office"],   example:"「加班到10点只想吃这款黑巧，苦到刚好」"}
      ],
      cases: [
        {title:"「彩虹糖×心动小镇联名糖果礼盒联动开启！」", ctr:31.3, tagCtr:88.6, note:"联名+节日礼盒，商卡CTR 88.6%，行业历史最高"},
        {title:"「宠粉福利🎁巧克力花生酱免费尝❗」",         ctr:25.1, tagCtr:16.6, note:"免费试吃钩子，低门槛引流再转化"},
        {title:"「不允许你们买贵 老天奶饼干」",              ctr:20.6, tagCtr:19.9, note:"价格对比+强推句式，商卡转化19.9%，曝光3.4万"}
      ]
    },
    "baked_goods": {
      name: "烘焙糕点", l1: "零食",
      audiences: [
        {id:"gift",   label:"节日送礼/伴手礼", price_bands:["80-200",">200"], keywords:["伴手礼","礼盒","茶歇","送人"]},
        {id:"daily",  label:"自己吃/下午茶",   price_bands:["<30","30-80"],   keywords:["下午茶","解馋","自己吃"]},
        {id:"kids",   label:"给孩子",           price_bands:["30-80","80-200"],keywords:["儿童","宝宝","无添加","放心"]},
        {id:"office", label:"办公室茶歇",       price_bands:["30-80","80-200"],keywords:["办公室","茶歇","同事","部门"]}
      ],
      selling_points_by_band: {
        "<30":    ["现烤现发","不添加防腐剂","比面包店实惠","量大新鲜"],
        "30-80":  ["低糖低脂","网红同款","法式工艺","无添加健康"],
        "80-200": ["手工制作","法式西点大师配方","进口黄油","精致礼盒包装"],
        ">200":   ["定制礼盒","明星下午茶同款","高端伴手礼","企业团购"]
      },
      title_templates: [
        {t:"「{节日/场景}茶歇选{产品}，{理由}」",           fit:["office","gift"], example:"「部门茶歇选这款马卡龙，同事都问哪买的」"},
        {t:"「{情绪感叹}！{产品}居然{出乎意料}」",           fit:["daily","kids"],  example:"「妈呀！这款无糖磅蛋糕居然比普通的还好吃」"},
        {t:"「实在忍不住发布（{原因}）{产品}真的太{描述}了」",fit:["daily","gift"], example:"「实在忍不住发布（客返图拍的太美了）这款曲奇真的太好看了」"},
        {t:"「破防了，{频率}买{产品}」",                    fit:["daily"],         example:"「破防了，每周必买这款布丁」"},
        {t:"「{人群}的第一款{产品}，选{特点}就够了」",       fit:["kids","diet"],   example:"「宝宝的第一款饼干，选无蔗糖就够了」"},
        {t:"「{产品}让我的{活动}，{解决问题}」",             fit:["gift","office"], example:"「这款曲奇让我的年会伴手礼，再也不用发愁了」"},
        {t:"「裸寄收到{产品}，{情绪反应}」",                fit:["gift"],          example:"「裸寄收到这盒泡芙，当时就崩溃了...」"},
        {t:"「{具体时间/场景}只想吃{产品}」",               fit:["daily","office"],example:"「下午三点困到不行，只想吃这款抹茶千层」"}
      ],
      cases: [
        {title:"「实在是忍不住发布（客返图）拍的实在美丽！」",ctr:26.0, tagCtr:16.0, note:"买家秀视角，真实感强，CTR 26% 曝光4.3万"},
        {title:"「🫠遇到裸寄的了😰」",                        ctr:25.4, tagCtr:8.2,  note:"负面情绪引流，裸寄话题爆量，曝光11.6万"},
        {title:"「星愿薯饼——星星脸暴击治愈力」",              ctr:24.6, tagCtr:6.6,  note:"IP/颜值叙事，情感价值驱动点击，曝光2.8万"}
      ]
    }
  };

  const CAT_L2 = {
    snack:   [{id:"candy_chocolate",name:"糖果巧克力",has_data:true},{id:"puffed_cookie",name:"膨化饼干",has_data:false},{id:"baked_goods",name:"烘焙糕点",has_data:true},{id:"nuts",name:"坚果炒货",has_data:false},{id:"marinated_meat",name:"卤味肉干",has_data:false},{id:"dried_fruit",name:"蜜饯果干",has_data:false}],
    instant: [{id:"noodle_instant",name:"干面方便食品",has_data:false},{id:"frozen_dim",name:"冷冻冷藏面点",has_data:false},{id:"self_heating",name:"自热即食",has_data:false},{id:"sauce",name:"调味料酱料",has_data:false}],
    drink:   [{id:"tea_drink",name:"茶饮",has_data:false},{id:"coffee",name:"咖啡",has_data:false},{id:"dairy",name:"乳品",has_data:false},{id:"functional",name:"功能饮料软饮",has_data:false}],
    liquor:  [{id:"baijiu",name:"白酒",has_data:false},{id:"wine",name:"葡萄酒",has_data:false},{id:"beer_craft",name:"啤酒精酿",has_data:false},{id:"spirits",name:"洋酒利口酒",has_data:false}],
    herb:    [{id:"herb_tea",name:"滋补茶饮",has_data:false},{id:"paste_pill",name:"膏方丸剂",has_data:false},{id:"tonic_food",name:"滋补食材",has_data:false},{id:"functional_health",name:"功能保健品",has_data:false}]
  };
"""

# ── V2 主 JS（干净，不用 f-string 插值） ──
MAIN_JS = r"""
  // ── Tab 3 状态 ──
  let currentCatId = null;
  let selectedPrice = null;
  let selectedAudiences = [];

  function selectL1(btn) {
    document.querySelectorAll('.cat-l1-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const cat = btn.dataset.cat;
    const l2Grid = document.getElementById('catL2Grid');
    document.getElementById('catL2Area').classList.add('show');
    l2Grid.innerHTML = CAT_L2[cat].map(c =>
      '<button class="cat-l2-btn' + (c.has_data ? '' : ' disabled') + '" data-id="' + c.id + '" onclick="' + (c.has_data ? 'selectL2(this)' : 'showNoData()') + '">' + c.name + (c.has_data ? ' ✦' : '') + '</button>'
    ).join('');
    document.getElementById('refForm').style.display = 'none';
    document.getElementById('refResult').classList.remove('show');
    currentCatId = null;
    gtag('event','ref_cat_l1',{cat_name: btn.textContent.trim()});
  }

  function selectL2(btn) {
    document.querySelectorAll('.cat-l2-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentCatId = btn.dataset.id;
    document.getElementById('refForm').style.display = 'block';
    document.getElementById('refResult').classList.remove('show');
    gtag('event','ref_cat_l2',{cat_id: currentCatId});
  }

  function showNoData() {
    alert('该品类数据正在整理中，敬请期待 ✦\n目前已有数据的品类：糖果巧克力 / 烘焙糕点');
  }

  function selectPrice(btn) {
    document.querySelectorAll('.price-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedPrice = btn.dataset.price;
  }

  function toggleAudience(btn) {
    btn.classList.toggle('active');
    selectedAudiences = Array.from(document.querySelectorAll('.aud-btn.active')).map(b => b.dataset.aud);
  }

  function generateRef() {
    if (!currentCatId) { alert('请先选择品类'); return; }
    if (!selectedPrice) { alert('请选择价格带'); return; }
    const kw = document.getElementById('refKeywords').value.trim();
    if (!kw) { alert('请填写核心卖点'); return; }
    const pkg = KNOWLEDGE[currentCatId];
    if (!pkg) { showNoData(); return; }
    const keywords = kw.split(/[，,、\s]+/).filter(Boolean);
    const matchedAud = pkg.audiences.filter(a =>
      a.price_bands.some(pb => pb === selectedPrice) ||
      a.keywords.some(k => keywords.some(kw2 => kw2.includes(k) || k.includes(kw2)))
    );
    const extraAud = pkg.audiences.filter(a => !matchedAud.includes(a) && selectedAudiences.includes(a.id));
    const finalAud = [...new Set([...matchedAud, ...extraAud])].slice(0,5);
    const spKey = pkg.selling_points_by_band[selectedPrice] ? selectedPrice : Object.keys(pkg.selling_points_by_band)[0];
    const sps = pkg.selling_points_by_band[spKey] || [];
    const audIds = [...new Set([...finalAud.map(a => a.id), ...selectedAudiences])];
    const matched  = pkg.title_templates.filter(t => t.fit.some(f => audIds.includes(f)));
    const rest     = pkg.title_templates.filter(t => !matched.includes(t));
    const templates = [...matched, ...rest].slice(0,8);
    renderRefResult(finalAud, sps, templates, pkg.cases);
    document.getElementById('refResult').classList.add('show');
    gtag('event','ref_generated',{cat_id: currentCatId});
  }

  function renderRefResult(audiences, sps, templates, cases) {
    const cards = document.getElementById('refCards');
    cards.innerHTML =
      '<div class="ref-card">' +
        '<div class="ref-card-title"><span>🧑‍🤝‍🧑</span> 高潜人群</div>' +
        (audiences.length ? audiences.map(a => '<span class="ref-tag">' + a.label + '</span>').join('') : '<span style="font-size:12px">请完善筛选条件</span>') +
        (audiences.length ? '<div style="margin-top:8px;font-size:11px">这些人群与你的价格带/卖点匹配度最高</div>' : '') +
      '</div>' +
      '<div class="ref-card">' +
        '<div class="ref-card-title"><span>💡</span> 买点包装</div>' +
        sps.map(sp => '<span class="ref-tag">' + sp + '</span>').join('') +
        '<div style="margin-top:8px;font-size:11px">同价格带商家常用的卖点表达</div>' +
      '</div>' +
      '<div class="ref-card" style="grid-column:1/-1">' +
        '<div class="ref-card-title"><span>✍️</span> 标题模板</div>' +
        templates.map(t => '<div class="ref-template">' + t.t + '<div class="example">示例：' + t.example + '</div></div>').join('') +
      '</div>' +
      '<div class="ref-card" style="grid-column:1/-1">' +
        '<div class="ref-card-title"><span>🔥</span> 同类爆款案例</div>' +
        cases.map(c => '<div class="ref-case"><div class="ref-case-title">' + c.title + '</div><div class="ref-case-meta">封面CTR ' + c.ctr + '% · 商卡转化 ' + c.tagCtr + '%</div><div class="ref-case-note">' + c.note + '</div></div>').join('') +
      '</div>';
  }

  function copyRefAll() {
    const el = document.getElementById('refCards');
    navigator.clipboard.writeText(el.innerText).then(() => {
      const btn = document.querySelector('.btn-copy-all');
      btn.textContent = '✅ 已复制';
      setTimeout(() => btn.textContent = '📋 复制全部', 2000);
    });
  }

  function showLingxiTip() {
    const t = document.getElementById('lingxiTip');
    t.style.display = t.style.display === 'none' ? 'block' : 'none';
  }

  // ── API 调用（创作工具） ──
  function _dec(enc, key) {
    const data = Uint8Array.from(atob(enc), c => c.charCodeAt(0));
    const res  = data.map((b, i) => b ^ key.charCodeAt(i % key.length));
    return new TextDecoder().decode(res);
  }

  async function callDoubao(systemPrompt, userMsg, btnId, loadingText, origText) {
    const btn = btnId ? document.getElementById(btnId) : null;
    if (btn) { btn.disabled = true; btn.textContent = loadingText || '⏳ 生成中…'; }
    try {
      const resp = await fetch('https://ark.cn-beijing.volces.com/api/v3/chat/completions', {
        method: 'POST',
        headers: {'Content-Type':'application/json','Authorization':'Bearer ' + _ak},
        body: JSON.stringify({
          model: 'doubao-seed-2-0-lite-260215',
          messages: [{role:'system',content:systemPrompt},{role:'user',content:userMsg}],
          max_tokens: 1200, temperature: 0.7
        })
      });
      const data = await resp.json();
      if (!data.choices) throw new Error(data.error ? data.error.message : '请求失败');
      return data.choices[0].message.content.trim();
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = origText || '生成'; }
    }
  }

  // 标题生成
  async function genTitles() {
    const name = document.getElementById('product-name').value.trim();
    if (!name) { alert('请填写产品名称'); return; }
    const feature  = document.getElementById('product-feature').value.trim();
    const audience = document.getElementById('product-audience').value.trim();
    const cat = (document.querySelector('input[name="cat"]:checked') || {value:'零食'}).value;
    const area = document.getElementById('titleResultArea');
    area.innerHTML = '⏳ 生成中…';
    area.classList.add('show');
    const sys = '你是小红书商品笔记标题专家，精通休食行业。请生成5条高CTR标题，每条标注"方法"（从以下选：卖点前置/人群锚定/具体场景/情绪共鸣/价格对比）。要求：每条标题25字以内，符合小红书调性，有差异化。格式：数字+标题+（方法：xxx）';
    const usr = '产品：' + name + (feature ? ' 卖点：' + feature : '') + (audience ? ' 人群：' + audience : '') + ' 品类：' + cat;
    try {
      const result = await callDoubao(sys, usr, 'title-gen-btn', '⏳ 生成中…', '✨ 生成5条标题');
      area.innerHTML = result.split('\n').filter(l => l.trim()).map(l => {
        const m = l.match(/（方法：(.+?)）/);
        const method = m ? m[1] : '';
        return '<div class="title-item" onclick="navigator.clipboard.writeText(this.querySelector(\'.title-item-text\').textContent)"><div class="title-item-text">' + l + '</div>' + (method ? '<div class="title-item-method">方法：' + method + ' · 点击复制</div>' : '') + '</div>';
      }).join('');
      gtag('event','tool_title_gen');
    } catch(e) {
      area.innerHTML = '<span style="color:#dc2626;font-size:13px">❌ 生成失败：' + e.message + '</span>';
    }
  }

  // 评论区话术
  async function genComments() {
    const topic = document.getElementById('comment-topic').value.trim();
    if (!topic) { alert('请填写笔记主题'); return; }
    const goal = (document.querySelector('input[name="comment-goal"]:checked') || {value:'引导商卡点击'}).value;
    const area = document.getElementById('commentResultArea');
    area.innerHTML = '⏳ 生成中…';
    area.classList.add('show');
    const sys = '你是小红书商品笔记运营专家。请直接输出：【置顶评论】3条（简洁有力，带行动引导，每条20字以内）和【互动话术】3条（回复评论区引发互动，轻松活泼）。';
    const usr = '产品/笔记主题：' + topic + '，目标诉求：' + goal;
    try {
      const result = await callDoubao(sys, usr, 'comment-gen-btn', '⏳ 生成中…', '💬 生成评论区话术');
      area.innerHTML = '<div class="tool-result-text">' + result.replace(/</g,'&lt;') + '</div>';
      gtag('event','tool_comment_gen');
    } catch(e) {
      area.innerHTML = '<span style="color:#dc2626;font-size:13px">❌ 失败：' + e.message + '</span>';
    }
  }

  // 封面生成
  async function genCover() {
    const name = document.getElementById('cover-name').value.trim();
    if (!name) { alert('请填写产品名称'); return; }
    const feature  = document.getElementById('cover-feature').value.trim();
    const audience = document.getElementById('cover-audience').value.trim();
    const area = document.getElementById('coverResultArea');
    area.innerHTML = '⏳ 生成中…';
    area.classList.add('show');
    const sys = '你是小红书商品笔记封面策划专家。请生成3个不同风格的封面文案方向，每个方向包含：风格名称/核心视觉画面/封面主文案/封面副文案/适用场景。格式清晰简洁。';
    const usr = '产品：' + name + (feature ? ' 卖点：' + feature : '') + (audience ? ' 人群：' + audience : '');
    try {
      const result = await callDoubao(sys, usr, 'cover-gen-btn', '⏳ 生成中…', '🤖 生成3个封面方向');
      area.innerHTML = '<div class="tool-result-text">' + result.replace(/</g,'&lt;') + '</div>';
      gtag('event','tool_cover_gen');
    } catch(e) {
      area.innerHTML = '<span style="color:#dc2626;font-size:13px">❌ 失败：' + e.message + '</span>';
    }
  }

  // ── Tab 5 笔记体检 ──
  async function runAuditV2() {
    const title = document.getElementById('audit-title').value.trim();
    const body  = document.getElementById('audit-body').value.trim();
    if (!body && !title) { alert('请先填写标题或正文'); return; }
    gtag('event','check_note');
    const btn = document.getElementById('audit-btn');
    btn.disabled = true; btn.textContent = '⏳ 体检中…';
    document.getElementById('checkResult').classList.add('show');
    document.getElementById('auditResultContent').textContent = '正在分析违规风险…';
    document.getElementById('methodCheckItems').innerHTML = '';
    document.getElementById('methodScore').textContent = '-';
    document.getElementById('topTip').style.display = 'none';
    const userMsg = '请审核以下笔记：\n标题：' + (title || '（无标题）') + '\n正文：\n' + body;

    // 模块1: 违规预审
    try {
      const systemPrompt = _dec(_enc, _key);
      const resp = await fetch('https://ark.cn-beijing.volces.com/api/v3/chat/completions', {
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer ' + _ak},
        body: JSON.stringify({model:'doubao-seed-2-0-lite-260215',messages:[{role:'system',content:systemPrompt},{role:'user',content:userMsg}],max_tokens:1500,temperature:0.1})
      });
      const data = await resp.json();
      if (data.choices) {
        const raw = data.choices[0].message.content.trim();
        const match = raw.match(/\{[\s\S]*\}/);
        if (match) {
          try {
            const result = JSON.parse(match[0]);
            const riskEmoji = {'高风险':'🔴','中风险':'🟡','低风险':'🟢','无风险':'✅'};
            let output = (riskEmoji[result.risk_level] || '⚠️') + ' ' + result.risk_level + '\n\n' + result.summary + '\n';
            if (result.issues && result.issues.length) {
              output += '\n━━ 问题详情 ━━\n';
              result.issues.forEach((issue, i) => {
                const sev = {'高':'🔴','中':'🟡','低':'🟢'};
                output += '\n' + (i+1) + '. [' + (sev[issue.severity]||'') + ' ' + issue.dimension + ']\n';
                output += '   问题：「' + issue.quote + '」\n';
                output += '   建议：' + issue.suggestion + '\n';
              });
            }
            if (result.revised_title && result.revised_title !== title) {
              output += '\n━━ 标题修改建议 ━━\n' + result.revised_title;
            }
            document.getElementById('auditResultContent').textContent = output;
          } catch(e2) {
            document.getElementById('auditResultContent').textContent = raw;
          }
        } else {
          document.getElementById('auditResultContent').textContent = raw;
        }
      }
    } catch(e) {
      document.getElementById('auditResultContent').textContent = '❌ 违规预审失败：' + e.message;
    }

    // 模块2: 方法论体检
    try {
      document.getElementById('methodCheckItems').innerHTML = '<div style="font-size:13px;padding:8px 0">正在核查 5 条方法论…</div>';
      const methodPrompt = '你是小红书商品笔记分析专家。请分析这篇笔记是否命中以下5条方法（每条只看明显命中或明显未命中）：\nD2-卖点前置：标题/封面前8字是否有核心卖点\nD5-人群场景：是否有具体人群描述（谁）+ 具体场景（在哪/什么时候）\nD8-使用场景：是否有具体生活化使用场景描述（非功效堆砌）\nD4-评论引导：正文是否有引导评论/互动/点击商卡的钩子\nD9-内容饱满：是否视频或图文内容丰富（正文字数>200字视为图文饱满）\n返回严格JSON，不要多余文字：\n{"d2":{"pass":true,"comment":"说明"},"d5":{"pass":true,"comment":""},"d8":{"pass":true,"comment":""},"d4":{"pass":true,"comment":""},"d9":{"pass":true,"comment":""},"score":0,"top_suggestion":"最重要的一条改进建议"}';
      const resp2 = await fetch('https://ark.cn-beijing.volces.com/api/v3/chat/completions', {
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer ' + _ak},
        body: JSON.stringify({model:'doubao-seed-2-0-lite-260215',messages:[{role:'system',content:methodPrompt},{role:'user',content:userMsg}],max_tokens:600,temperature:0.1})
      });
      const data2 = await resp2.json();
      if (data2.choices) {
        const raw2 = data2.choices[0].message.content.trim();
        const match2 = raw2.match(/\{[\s\S]*\}/);
        if (match2) {
          const r = JSON.parse(match2[0]);
          document.getElementById('methodScore').textContent = r.score != null ? r.score : '-';
          const dims = [
            {key:'d2',label:'卖点前置'},{key:'d5',label:'人群×场景'},
            {key:'d8',label:'具体场景'},{key:'d4',label:'评论引导'},{key:'d9',label:'内容饱满'}
          ];
          document.getElementById('methodCheckItems').innerHTML = dims.map(d => {
            const item = r[d.key] || {};
            return '<div class="check-item"><div class="check-icon">' + (item.pass ? '✅' : '❌') + '</div><div class="check-label">' + d.label + '</div><div class="check-comment">' + (item.comment || '') + '</div></div>';
          }).join('');
          if (r.top_suggestion) {
            const tip = document.getElementById('topTip');
            tip.style.display = 'block';
            tip.textContent = '💡 最重要的改进：' + r.top_suggestion;
          }
        }
      }
    } catch(e) {
      document.getElementById('methodCheckItems').innerHTML = '<div style="color:#dc2626;font-size:13px">❌ 方法论核查失败：' + e.message + '</div>';
    }

    // 模块3: benchmark
    const catId = document.getElementById('check-cat').value;
    const benchData = {
      candy_chocolate: {ctrs:'18~25', topCtr:'25%+', cvr:'8~12',  topCvr:'12%+'},
      baked_goods:     {ctrs:'16~22', topCtr:'22%+', cvr:'7~11',  topCvr:'11%+'},
      other:           {ctrs:'13~18', topCtr:'20%+', cvr:'5~9',   topCvr:'10%+'},
      '':              {ctrs:'13~20', topCtr:'20%+', cvr:'5~10',  topCvr:'10%+'}
    };
    const bench = benchData[catId] || benchData[''];
    document.getElementById('benchContent').innerHTML =
      '<div class="bench-row-small"><span class="bench-label-sm">商笔 CTR（封面点击率）</span><div class="bench-vals"><div class="bench-val-sm"><div class="num">' + bench.ctrs + '%</div><div class="lab">行业区间</div></div><div class="bench-val-sm"><div class="num">' + bench.topCtr + '</div><div class="lab">TOP20%</div></div></div></div>' +
      '<div class="bench-row-small"><span class="bench-label-sm">商品转化率（商卡→支付）</span><div class="bench-vals"><div class="bench-val-sm"><div class="num">' + bench.cvr + '%</div><div class="lab">行业区间</div></div><div class="bench-val-sm"><div class="num">' + bench.topCvr + '</div><div class="lab">TOP20%</div></div></div></div>' +
      '<div style="margin-top:8px;font-size:12px">达到行业均值即为合格，进入 TOP20% 区间说明内容创作已较为高效</div>';

    btn.disabled = false; btn.textContent = '🔍 开始体检';
  }

  // ── 方法论卡片折叠 ──
  function toggleMethod(card) {
    const isOpen = card.classList.contains('open');
    document.querySelectorAll('.method-card').forEach(c => c.classList.remove('open'));
    if (!isOpen) card.classList.add('open');
  }

  // ── Tab 切换 ──
  function switchTab(event, name) {
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.remove('hidden');
    if (event && event.currentTarget) event.currentTarget.classList.add('active');
    gtag('event','tab_switch',{tab_name: name});
  }

  function switchTabByName(name) {
    const idx = {trends:0, method:1, ref:2, tools:3, check:4};
    const i = idx[name] != null ? idx[name] : 0;
    const btns = document.querySelectorAll('.tab-btn');
    if (btns[i]) btns[i].click();
  }
"""

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>休食商笔风向看板 · 小红书电商</title>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VJ5TN7HBY1"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-VJ5TN7HBY1');
  </script>
  <style>
""" + css1 + LIGHT_CSS + V2_COMPONENT_CSS + """
  </style>
""" + css2 + """
</head>
<body>

<header class="header">
  <div class="header-left">
    <div class="header-icon">🍿</div>
    <div>
      <div class="header-title">休食商笔风向看板</div>
      <div class="header-sub">小红书电商 · 商家内容创作参考 · 每周更新</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-week" style="color:#2563eb">W21</div>
    <div class="header-date" style="color:#6b7280">2026.05.18 — 05.24</div>
  </div>
</header>

<div class="container">

  <div class="tab-nav">
    <button class="tab-btn active" onclick="switchTab(event,'trends')">📊 行业趋势</button>
    <button class="tab-btn" onclick="switchTab(event,'method')">📚 方法论</button>
    <button class="tab-btn" onclick="switchTab(event,'ref')">🎯 我的内容参考</button>
    <button class="tab-btn" onclick="switchTab(event,'tools')">🛠️ 创作工具</button>
    <button class="tab-btn" onclick="switchTab(event,'check')">🔍 笔记体检</button>
  </div>

  <!-- Tab 1: 行业趋势 -->
  <div class="tab-panel" id="tab-trends">
""" + trends_body + """
    <div class="section-label">
      <span class="icon">🏆</span> 本周新发高表现笔记
      <span class="tag">W21 · 05.18—05.24 · 封面CTR × 商卡CTR 综合排名 TOP20</span>
    </div>
    <div class="top-notes-grid" id="topNotesGrid"></div>
  </div>

  <!-- Tab 2: 方法论 -->
  <div class="tab-panel hidden" id="tab-method">
    <div class="section-label"><span class="icon">📚</span> 5 条核心方法 <span class="tag">基于 25 年休食真实笔记数据验证</span></div>
    <div class="method-cards" id="methodCards">

      <div class="method-card" onclick="toggleMethod(this)">
        <div class="method-head"><div class="method-num">1</div><div class="method-title">卖点前置 · 3秒亮出核心利益点</div><div class="method-badge">D2</div><div class="method-arrow">›</div></div>
        <div class="method-body">
          <div class="method-why"><div class="method-why-label">为什么有效</div><div class="method-why-text">25年休食数据：高CTR笔记中 78% 在封面首位展示核心利益点，比未前置的笔记 CTR 平均高出 1.5 倍。</div></div>
          <div class="method-how"><div class="method-how-label">怎么做</div><ul class="method-how-list"><li>卖点 → 品牌名 → 产品名的优先级排封面</li><li>标题前 8 字必须有利益点（"0添加蜂蜜""古法九蒸黑芝麻"）</li><li>❌ 不要前置成分说明、配料表、功效列表</li><li>❌ 不要用"我们家的"开头，没人关心"我们家"</li></ul></div>
          <div class="method-case"><div class="method-case-label">爆款案例</div><div class="method-case-text">「古法九蒸九晒·黑芝麻丸，坚持吃了3个月变化」—— 封面第一行是核心卖点，CTR 28%+；对比"我家黑芝麻丸"，同款产品 CTR 不足 12%</div></div>
        </div>
      </div>

      <div class="method-card" onclick="toggleMethod(this)">
        <div class="method-head"><div class="method-num">2</div><div class="method-title">锁定人群×场景 · 让对的人觉得"这就是我"</div><div class="method-badge">D5</div><div class="method-arrow">›</div></div>
        <div class="method-body">
          <div class="method-why"><div class="method-why-label">为什么有效</div><div class="method-why-text">9维数据验证：CVR池中 D5 命中率比 GPM池高出 27pp。笔记里同时出现"谁"和"在什么情况下"，转化率显著更高。</div></div>
          <div class="method-how"><div class="method-how-label">怎么做</div><ul class="method-how-list"><li>标题开头锁人群（"备孕姐妹""减脂期姐妹""宝妈专属"）</li><li>正文第一段描述具体场景（"哄娃失败躺平" "婆婆来了不知道送啥"）</li><li>❌ 不要写"大家都爱"——没有人群，没人觉得是在说自己</li></ul></div>
          <div class="method-case"><div class="method-case-label">爆款案例</div><div class="method-case-text">「这种肚子的女生一定注意，再节食也没用」—— 精准锁定体型焦虑人群，CTR 20.7%，曝光 17.9 万</div></div>
        </div>
      </div>

      <div class="method-card" onclick="toggleMethod(this)">
        <div class="method-head"><div class="method-num">3</div><div class="method-title">具体使用场景 · 不说"好喝"说"加班第三杯"</div><div class="method-badge">D8</div><div class="method-arrow">›</div></div>
        <div class="method-body">
          <div class="method-why"><div class="method-why-label">为什么有效</div><div class="method-why-text">D8 是最强单维度信号：CVR池中命中率 51.2%，比 GPM池高出 36.8pp。把产品放进具体生活画面，比功效描述有效 10 倍。</div></div>
          <div class="method-how"><div class="method-how-label">怎么做</div><ul class="method-how-list"><li>描述"在哪里吃/喝/用"（地点 + 时间 + 状态）</li><li>带入情绪（压力/放松/惊喜/治愈感）</li><li>❌ 不要堆功效词（"排毒养颜健脾胃滋补"连成串）</li></ul></div>
          <div class="method-case"><div class="method-case-label">爆款案例</div><div class="method-case-text">「婆婆又煮了一锅｜我手把手教你做七宝水✨」—— 把养生茶放进家庭生活场景，CTR 29.4%，曝光 6.3 万</div></div>
        </div>
      </div>

      <div class="method-card" onclick="toggleMethod(this)">
        <div class="method-head"><div class="method-num">4</div><div class="method-title">评论区运营 · 评论区是第二个销售场</div><div class="method-badge">D4</div><div class="method-arrow">›</div></div>
        <div class="method-body">
          <div class="method-why"><div class="method-why-label">为什么有效</div><div class="method-why-text">DGMV池中 D4 命中率 78.8%，比 GPM池高出 52.1pp——这是所有维度中对GMV影响最大的。评论区做得好，转化率额外提升 30%+。</div></div>
          <div class="method-how"><div class="method-how-label">怎么做</div><ul class="method-how-list"><li>置顶评论引导行动（"想要的姐妹扣1""点击上方商品卡查价格"）</li><li>置顶评论提前挖掘顾客担忧并解答（"看到很多问发货问题的…"）</li><li>评论区互动保持自然，不要一眼刷出来的感觉</li></ul></div>
          <div class="method-case"><div class="method-case-label">爆款案例</div><div class="method-case-text">置顶评论写"想买的扣1"的笔记，相比不引导的笔记，商卡点击率平均高 2~3 倍；DGMV 贡献提升 40% 以上</div></div>
        </div>
      </div>

      <div class="method-card" onclick="toggleMethod(this)">
        <div class="method-head"><div class="method-num">5</div><div class="method-title">视频化 / 图文饱满 · 形态决定上限</div><div class="method-badge">D9</div><div class="method-arrow">›</div></div>
        <div class="method-body">
          <div class="method-why"><div class="method-why-label">为什么有效</div><div class="method-why-text">2026年数据首次出现视频笔记单篇产出（¥98）超过图文（¥82），且差距持续扩大。形态的选择，影响流量天花板。</div></div>
          <div class="method-how"><div class="method-how-label">怎么做</div><ul class="method-how-list"><li>有口播能力：优先做视频（15~60秒），前3秒放最亮眼画面/文字</li><li>做图文：至少8张（封面+场景+细节+评论截图+收货+买家秀）</li><li>视频开头第1句话就要抓人，不要用"大家好"之类的开场白</li></ul></div>
          <div class="method-case"><div class="method-case-label">数据佐证</div><div class="method-case-text">休食五组 2025 年数据：从图文切换为视频的商家，CTR 平均提升 35%，CVR 提升 20%；建议产品有可视化卖点的优先视频化</div></div>
        </div>
      </div>

    </div>
    <div class="sgld-card">
      <div class="sgld-title">🏅 平台官方好内容评分标准 · 三感六度</div>
      <div class="sgld-desc">小红书官方用 7 个维度评判一篇笔记好不好。自查用：未命中任一硬伤 + 七维≥4个达标 = GOOD内容。</div>
      <div class="sgld-dims"><span class="sgld-dim">受众精准度</span><span class="sgld-dim">兴趣激发度</span><span class="sgld-dim">场景融入度</span><span class="sgld-dim">情绪共鸣度</span><span class="sgld-dim">需求满足度</span><span class="sgld-dim">封面&标题自然呈现</span><span class="sgld-dim">正文自然呈现度</span></div>
      <button class="sgld-btn" onclick="switchTabByName('check')">→ 去 Tab5 给我的笔记体检</button>
    </div>
  </div>

  <!-- Tab 3: 我的内容参考 -->
  <div class="tab-panel hidden" id="tab-ref">
    <div class="section-label"><span class="icon">🎯</span> 我的内容参考 <span class="tag">输入你的产品信息 · 获取个性化内容建议</span></div>
    <div class="ref-intro">不同品类、不同价格带、不同卖点的商品，适合完全不同的内容打法。<br>选择你的品类和产品定位，看板帮你从本周行业数据中，挑出最贴近你的人群洞察、买点包装和标题模板。</div>
    <div class="form-row" style="margin-bottom:12px">
      <label class="form-label">第一步 · 选择品类</label>
      <div class="cat-l1-grid" id="catL1Grid">
        <button class="cat-l1-btn" data-cat="snack"   onclick="selectL1(this)">🍿 零食</button>
        <button class="cat-l1-btn" data-cat="instant" onclick="selectL1(this)">🍜 速食</button>
        <button class="cat-l1-btn" data-cat="drink"   onclick="selectL1(this)">🧋 饮品</button>
        <button class="cat-l1-btn" data-cat="liquor"  onclick="selectL1(this)">🍷 酒类</button>
        <button class="cat-l1-btn" data-cat="herb"    onclick="selectL1(this)">🌿 中式滋补</button>
      </div>
    </div>
    <div class="cat-l2-area" id="catL2Area">
      <label class="form-label">选择细分品类</label>
      <div class="cat-l2-grid" id="catL2Grid"></div>
    </div>
    <div class="ref-form" id="refForm" style="display:none">
      <div class="form-row">
        <label class="form-label">价格带 <span class="required">*</span></label>
        <div class="price-btns" id="priceBtns">
          <button class="price-btn" data-price="<30"    onclick="selectPrice(this)">¥30以下</button>
          <button class="price-btn" data-price="30-80"  onclick="selectPrice(this)">¥30-80</button>
          <button class="price-btn" data-price="80-200" onclick="selectPrice(this)">¥80-200</button>
          <button class="price-btn" data-price=">200"   onclick="selectPrice(this)">¥200以上</button>
        </div>
      </div>
      <div class="form-row" style="margin-top:14px">
        <label class="form-label">核心卖点 <span class="required">*</span></label>
        <input class="form-input" id="refKeywords" type="text" placeholder="例：古法工艺、0添加、伴手礼、产地直发（逗号分隔，最多3个）">
      </div>
      <div class="form-row" style="margin-top:14px">
        <label class="form-label">目标人群（可多选）</label>
        <div class="audience-grid" id="audienceGrid">
          <button class="aud-btn" data-aud="gift"   onclick="toggleAudience(this)">送礼</button>
          <button class="aud-btn" data-aud="daily"  onclick="toggleAudience(this)">日常/自己吃</button>
          <button class="aud-btn" data-aud="kids"   onclick="toggleAudience(this)">给孩子/宝妈</button>
          <button class="aud-btn" data-aud="elder"  onclick="toggleAudience(this)">送长辈</button>
          <button class="aud-btn" data-aud="office" onclick="toggleAudience(this)">办公室零食</button>
          <button class="aud-btn" data-aud="diet"   onclick="toggleAudience(this)">减脂/健身</button>
        </div>
      </div>
      <button class="btn-gen-main" onclick="generateRef()" id="genRefBtn">🎯 生成我的内容参考</button>
    </div>
    <div class="ref-result" id="refResult">
      <div class="ref-cards" id="refCards"></div>
      <div class="ref-actions">
        <button class="btn-refresh" onclick="generateRef()">↻ 换一份参考</button>
        <button class="btn-copy-all" onclick="copyRefAll()">📋 复制全部</button>
      </div>
    </div>
  </div>

  <!-- Tab 4: 创作工具 -->
  <div class="tab-panel hidden" id="tab-tools">
    <div class="section-label"><span class="icon">✨</span> 标题生成器 <span class="tag">输入产品 · 直接生成5条候选</span></div>
    <div class="planner-card tool-section">
""" + tools_html + """
      <div class="tool-result-area" id="titleResultArea"></div>
    </div>

    <div class="section-label" style="margin-top:4px"><span class="icon">💬</span> 评论区话术 <span class="tag">对应方法论第4条 · 直接生成</span></div>
    <div class="planner-card tool-section">
      <div class="planner-intro">生成置顶评论 + 互动引导话术，评论区做好转化率能额外提升 30%+</div>
      <div class="planner-form">
        <div class="form-row">
          <label class="form-label">笔记主题 <span class="required">*</span></label>
          <input class="form-input" id="comment-topic" type="text" placeholder="例：卖手工黑芝麻丸、推广有机燕麦奶">
        </div>
        <div class="form-row">
          <label class="form-label">目标诉求</label>
          <div class="cat-select-group">
            <label class="cat-radio"><input type="radio" name="comment-goal" value="引导商卡点击" checked><span>引导点击</span></label>
            <label class="cat-radio"><input type="radio" name="comment-goal" value="解答顾虑"><span>解答顾虑</span></label>
            <label class="cat-radio"><input type="radio" name="comment-goal" value="引导关注"><span>引导关注</span></label>
            <label class="cat-radio"><input type="radio" name="comment-goal" value="引导复购"><span>引导复购</span></label>
          </div>
        </div>
      </div>
      <div class="planner-actions">
        <button class="btn-gen" id="comment-gen-btn" onclick="genComments()">💬 生成评论区话术</button>
      </div>
      <div class="tool-result-area" id="commentResultArea"></div>
    </div>

    <div class="section-label" style="margin-top:4px"><span class="icon">🖼️</span> 封面策划助手 <span class="tag">输入卖点 · 直接生成3个封面方向</span></div>
    <div class="planner-card tool-section">
      <div class="planner-form">
        <div class="form-row"><label class="form-label">产品名称 <span class="required">*</span></label><input class="form-input" id="cover-name" type="text" placeholder="例：手工黑芝麻丸、鲜萃冷泡茶"></div>
        <div class="form-row" style="margin-top:10px"><label class="form-label">核心卖点（选填）</label><input class="form-input" id="cover-feature" type="text" placeholder="例：古法九蒸九晒、0添加、外婆配方"></div>
        <div class="form-row" style="margin-top:10px"><label class="form-label">目标人群（选填）</label><input class="form-input" id="cover-audience" type="text" placeholder="例：备考学生、减脂女生、宝妈"></div>
      </div>
      <div class="planner-actions">
        <button class="btn-gen btn-doubao" id="cover-gen-btn" onclick="genCover()">🤖 生成3个封面方向</button>
        <button class="btn-copy" onclick="copyCoverPrompt()">📋 复制提示词</button>
      </div>
      <div class="tool-result-area" id="coverResultArea"></div>
      <div class="prompt-preview" id="cover-prompt-preview"><div class="prompt-label">封面策划提示词预览</div><div class="prompt-text" id="cover-prompt-text">填写产品信息后，这里会显示封面策划提示词…</div></div>
    </div>

    <div class="section-label" style="margin-top:4px"><span class="icon">🔗</span> 灵犀工具 <span class="tag">小红书商家后台 · 数据化选词/选品/选人群</span></div>
    <div class="lingxi-grid">
      <div class="lingxi-card" onclick="showLingxiTip()"><div class="lingxi-icon">🔍</div><div class="lingxi-info"><div class="name">灵犀选词</div><div class="desc">找高 CTR 标题关键词</div></div></div>
      <div class="lingxi-card" onclick="showLingxiTip()"><div class="lingxi-icon">📦</div><div class="lingxi-info"><div class="name">灵犀选品</div><div class="desc">发现行业热销 SPU</div></div></div>
      <div class="lingxi-card" onclick="showLingxiTip()"><div class="lingxi-icon">👥</div><div class="lingxi-info"><div class="name">灵犀人群洞察</div><div class="desc">了解你的目标用户</div></div></div>
      <div class="lingxi-card" onclick="showLingxiTip()"><div class="lingxi-icon">📊</div><div class="lingxi-info"><div class="name">灵犀内容诊断</div><div class="desc">分析笔记流量来源</div></div></div>
    </div>
    <div id="lingxiTip" style="display:none;margin-top:12px;padding:12px 16px;background:rgba(124,58,237,.06);border:1px solid rgba(124,58,237,.15);border-radius:10px;font-size:13px;color:#7c3aed">💡 灵犀工具请在小红书商家后台 → 数据中心 → 灵犀分析 中使用</div>
  </div>

  <!-- Tab 5: 笔记体检 -->
  <div class="tab-panel hidden" id="tab-check">
    <div class="section-label"><span class="icon">🔍</span> 笔记体检 <span class="tag">贴入文案 · AI 自动体检 + 行业对标</span></div>
    <div class="check-form">
      <div class="planner-intro" style="padding:0;margin-bottom:16px;font-size:13px;line-height:1.6">粘贴你的笔记，一键体检：① 违规风险 ② 5条方法论核查 ③ 行业 benchmark 对标</div>
      <div class="form-row"><label class="form-label">笔记标题（选填）</label><input class="form-input" id="audit-title" type="text" placeholder="例：7天瘦10斤！这个方法太有效了"></div>
      <div class="form-row" style="margin-top:12px"><label class="form-label">笔记正文 <span class="required">*</span></label><textarea class="form-input" id="audit-body" rows="5" placeholder="把你的笔记正文粘贴到这里…" style="resize:vertical;line-height:1.6"></textarea></div>
      <div class="form-row" style="margin-top:12px">
        <label class="form-label">品类（选填）</label>
        <select class="form-input" id="check-cat"><option value="">-- 不限品类 --</option><option value="candy_chocolate">糖果巧克力</option><option value="baked_goods">烘焙糕点</option><option value="other">其他休食品类</option></select>
      </div>
      <div class="planner-actions" style="margin-top:14px"><button class="btn-gen" id="audit-btn" onclick="runAuditV2()">🔍 开始体检</button></div>
    </div>
    <div class="check-result" id="checkResult">
      <div class="check-module"><div class="check-module-title">① 违规风险预审</div><div id="auditResultContent" style="font-size:13px;white-space:pre-wrap;line-height:1.8"></div></div>
      <div class="check-module"><div class="check-module-title">② 5条方法论核查</div><div class="check-score"><div class="check-score-num" id="methodScore">-</div><div class="check-score-label">/ 5 条方法命中</div></div><div id="methodCheckItems"></div><div id="topTip" class="check-top-tip" style="display:none"></div></div>
      <div class="check-module"><div class="check-module-title">③ 行业参考 benchmark</div><div id="benchContent"></div><div style="margin-top:12px;font-size:12px">👉 想提升内容质量？<button onclick="switchTabByName('ref')" style="background:none;border:none;color:#2563eb;cursor:pointer;font-size:12px;text-decoration:underline">去 Tab3 获取个性化内容参考</button></div></div>
    </div>
  </div>

</div>

<div style="text-align:center;padding:20px;font-size:12px;color:#9ca3af">
  <div>数据来源：小红书 BI · 休食五组 · 近7天</div>
  <div style="margin-top:4px">本站累计访问 <span id="busuanzi_value_site_pv">--</span> 次 · 访客数 <span id="busuanzi_value_site_uv">--</span> 人</div>
</div>

<script async src="//busuanzi.ibruce.info/busuanzi/2.3/busuanzi.pure.mini.js"></script>

<script>
""" + top_notes + """
  function renderTopNotes(notes) {
    const grid = document.getElementById('topNotesGrid');
    if (!grid) return;
    grid.innerHTML = notes.map(n => '<a class="note-card" href="' + n.url + '" target="_blank" rel="noopener"><div class="note-img-wrap"><img class="note-img" src="' + n.cover + '" loading="lazy" onerror="this.style.display=\\'none\\'" /></div><div class="note-body"><div class="note-title">' + n.title + '</div><div class="note-meta">封面CTR ' + n.ctr + '%</div></a>').join('');
  }
  if (typeof TOP_NOTES !== 'undefined') renderTopNotes(TOP_NOTES);

""" + KNOWLEDGE_JS + MAIN_JS + build_prompt + update_prev + build_cover + api_keys + """
</script>
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'写入完成: {len(html)} bytes, {html.count(chr(10))+1} 行')
PYEOF
