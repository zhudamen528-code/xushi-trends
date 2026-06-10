#!/usr/bin/env python3
"""V8b patch: Tab1脱敏 + Tab2-5 方法论+案例内联"""
import json, os, re

WORKDIR = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
DATA_PATH = os.path.join(WORKDIR, 'data.json')
BUILD_PATH = os.path.join(WORKDIR, 'build_v8_gpm.py')

with open(DATA_PATH) as f:
    data = json.load(f)
with open(BUILD_PATH) as f:
    src = f.read()

# ========= 1. Tab1 KPI 卡片改为脱敏版 =========
# 把 kpi_card 函数改成只显示方向感（高/中/低），不显示具体数值
OLD_KPI_CARD = '''def kpi_card(title, p50, p75, ka_p75=None, pct=True):
    fmt = fmt_pct if pct else fmt_money
    ka_html = f\'<div class="kpi-ka">KA 大盘 P75：{fmt(ka_p75)}</div>\' if ka_p75 is not None else \'\'
    return f\'\'\'<div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{fmt(p75)}</div>
      <div class="kpi-sub">优秀线 P75 · 中位 P50 {fmt(p50)}</div>
      {ka_html}
    </div>\'\'\''''

NEW_KPI_CARD = '''def kpi_card(title, p50, p75, ka_p75=None, pct=True):
    """Tab1 脱敏版：只展示方向感，不暴露绝对值"""
    def level(v, is_pct):
        if v is None: return '—'
        if is_pct:
            # CTR1: 图文>10%=高, 7-10%=中, <7%=低
            # CTR2: 图文>30%=高; CVR>6%=高
            if v >= 0.10: return '高'
            if v >= 0.06: return '中等'
            return '一般'
        else:
            if v >= 60: return '高'
            if v >= 30: return '中等'
            return '一般'
    p75_label = level(p75, pct)
    p50_label = level(p50, pct)
    color = '#ff2442' if p75_label == '高' else ('#ff7043' if p75_label == '中等' else '#888')
    ka_cmp = ''
    if ka_p75 is not None and p75 is not None:
        diff = p75 - ka_p75
        if abs(diff) < 0.005 if pct else abs(diff) < 3:
            ka_cmp = '与大盘持平'
        elif diff > 0:
            ka_cmp = '优于大盘'
        else:
            ka_cmp = '略低大盘'
    ka_html = f\'<div class="kpi-ka">{ka_cmp}</div>\' if ka_cmp else \'\'
    return f\'\'\'<div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value" style="color:{color}">{p75_label}</div>
      <div class="kpi-sub">优秀笔记水平 · 行业中位 {p50_label}</div>
      {ka_html}
    </div>\'\'\''''

src = src.replace(OLD_KPI_CARD, NEW_KPI_CARD, 1)
if OLD_KPI_CARD in src:
    print("[ERROR] kpi_card replacement failed - still found old string")
else:
    print("[OK] Tab1 kpi_card 脱敏完成")

# ========= 2. 改 funnel_tab：方法论+案例内联 =========
# 读 data 里的 cases，给每条方法匹配 2 个案例
# 匹配规则：关键词从 highlight 里找

def match_cases_to_method(cases_list, keywords, n=2):
    """从 cases_list 里找最匹配 keywords 的 n 条"""
    scored = []
    for c in cases_list:
        hl = (c.get('highlight') or '') + (c.get('title') or '')
        score = sum(1 for kw in keywords if kw in hl)
        scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:n]]

def escape(s):
    if s is None: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def fmt_pct(v):
    if v is None: return '—'
    return f"{v*100:.1f}%"

def inline_case_mini(c, metric_key):
    """内联小案例卡（简化版）"""
    val = fmt_pct(c['value']) if metric_key != 'price' else f"¥{c['value']:.0f}"
    return f'''<a class="inline-case" href="{c['note_url']}" target="_blank">
      <span class="ic-metric">{val}</span>
      <span class="ic-title">{escape(c['title'][:25])}{'…' if len(c.get('title',''))>25 else ''}</span>
      <span class="ic-hl">{escape(c.get('highlight',''))}</span>
    </a>'''

def method_card_with_cases(title, desc, source, cases_list, keywords, metric_key):
    matched = match_cases_to_method(cases_list, keywords, n=2)
    cases_html = ''.join(inline_case_mini(c, metric_key) for c in matched)
    return f'''<div class="method-card-v2">
      <div class="method-title">{title}</div>
      <div class="method-desc">{desc}</div>
      <div class="method-cases">{cases_html}</div>
      <div class="method-source">来源：{source}</div>
    </div>'''

# 给 CTR1 重新生成
ctr1_t = data['top_cases']['ctr1']['图文']
ctr1_v = data['top_cases']['ctr1']['视频']
CTR1_METHODS_NEW_T = ''.join([
    method_card_with_cases("📸 单主体+特写", "封面只放一个主体（产品/手部动作），剔除杂乱背景", "诺亚 insight-v20", ctr1_t, ['手','主体','特写','产品图'], 'ctr1'),
    method_card_with_cases("🔥 数字+反差词", '标题用数字钩子或反差词（如「100卡」「裸寄」「自黑」），吊起好奇', "creation-guide-v9 D2", ctr1_t, ['数字','卡','反差','自黑','悬念','好奇','craving'], 'ctr1'),
    method_card_with_cases("💬 情绪共鸣开头", '「打工人续命」「自律必吃」等第一人称场景，精准锁人群', "creation-guide-v9 D5", ctr1_t, ['情绪','共鸣','场景','人群','自律','打工','减脂'], 'ctr1'),
    method_card_with_cases("🎭 拟声/趣味词", '「duangduang」「裸寄了」等趣味表达，内容味极强', "三感六度", ctr1_t, ['拟声','趣味','梗','话题','联想','情趣','反向'], 'ctr1'),
    method_card_with_cases("👀 反向/制造悬念", '自黑标题、神秘感留白、意外反转，用户不点不甘心', "诺亚 insight-v20", ctr1_t, ['悬念','神秘','留白','翻车','反转','不一样'], 'ctr1'),
])
CTR1_METHODS_NEW_V = ''.join([
    method_card_with_cases("📸 单主体+特写", "封面只放一个主体（产品/手部动作），剔除杂乱背景", "诺亚 insight-v20", ctr1_v, ['手','主体','特写','产品图'], 'ctr1'),
    method_card_with_cases("🔥 数字+反差词", '标题用数字钩子或反差词', "creation-guide-v9 D2", ctr1_v, ['数字','卡','反差','自黑','悬念'], 'ctr1'),
    method_card_with_cases("💬 情绪共鸣开头", '第一人称场景，精准锁人群', "creation-guide-v9 D5", ctr1_v, ['情绪','共鸣','老师傅','推荐','背书'], 'ctr1'),
    method_card_with_cases("🎬 视频口播钩子", '开头3秒悬念/反问/报价，让用户继续看', "creation-guide-v9 D9", ctr1_v, ['视频','口播','动作','吃播','沉浸'], 'ctr1'),
    method_card_with_cases("🌍 地域/产地背书", '「厦门老味道」「厂家直发」等产地词，增加真实感', "诺亚 insight-v20", ctr1_v, ['地域','产地','老味道','厦门','地方'], 'ctr1'),
])

ctr2_t = data['top_cases']['ctr2']['图文']
ctr2_v = data['top_cases']['ctr2']['视频']
CTR2_METHODS_NEW_T = ''.join([
    method_card_with_cases("🏷️ 价格直给", '标题/封面露价格（9.9、6.6折、开业特惠），降低决策门槛', "creation-guide-v9 D8", ctr2_t, ['价格','折','9.9','优惠','便宜','自行车','划算'], 'ctr2'),
    method_card_with_cases("⏰ 节日/限时氛围", '节气、节假日、开业活动，制造时限紧迫感', "诺亚 insight-v20", ctr2_t, ['节日','限时','618','开业','儿童节','节气','芒种'], 'ctr2'),
    method_card_with_cases("📊 参数堆叠", '低卡+无面粉+高蛋白等多卖点参数化，商品卡信息密度高', "creation-guide-v9 D9", ctr2_t, ['参数','卡','卖点','蛋白','无','成分'], 'ctr2'),
    method_card_with_cases("🏆 稀缺/催促", '「别停产」「顾客催涨价」等稀缺感，触发囤货行为', "三感六度", ctr2_t, ['稀缺','催','停产','别','限量','紧迫'], 'ctr2'),
    method_card_with_cases("💊 对症解决方案", '节气症状+产品=精准解决方案，商品卡承接感强', "creation-guide-v9 D5", ctr2_t, ['症状','湿热','睡','功效','对症','补'], 'ctr2'),
])
CTR2_METHODS_NEW_V = ''.join([
    method_card_with_cases("🏷️ 价格直给", '视频口播强调价格/活动，卡片价格曝光', "creation-guide-v9 D8", ctr2_v, ['价格','折','优惠','便宜','划算','福利'], 'ctr2'),
    method_card_with_cases("👥 用户口碑/复购", '老用户回购、真实好评、每月福利，建立信任', "creation-guide-v9 D4", ctr2_v, ['复购','口碑','福利','每月','老用户','回购'], 'ctr2'),
    method_card_with_cases("🎭 拟声/口感描述", '「剥皮+爆汁」「沉浸式打包」等感官卖点，视频场景还原', "三感六度", ctr2_v, ['口感','爆汁','剥皮','沉浸','解压','感官'], 'ctr2'),
    method_card_with_cases("📦 具体配置/参数", '告诉用户买到什么（几个/几折/有什么），减少决策摩擦', "creation-guide-v9 D9", ctr2_v, ['参数','个','只','配置','几','套'], 'ctr2'),
    method_card_with_cases("🌍 场景代入", '高原/出行/特定人群精准场景，用户代入感强', "诺亚 insight-v20", ctr2_v, ['场景','高原','出行','人群','刚需'], 'ctr2'),
])

cvr_t = data['top_cases']['cvr']['图文']
cvr_v = data['top_cases']['cvr']['视频']
CVR_METHODS_NEW_T = ''.join([
    method_card_with_cases("🎯 精准人群锁定", '标题含具体人群词（备孕/减脂/宝妈），过滤无效流量', "creation-guide-v9 D5", cvr_t, ['人群','精准','减脂','宝妈','备孕','女性','锁定'], 'cvr'),
    method_card_with_cases("💬 停产/求回购焦虑", '「求别停产」「回购第N次」营造缺失焦虑，老粉情感强转化', "creation-guide-v9 D4", cvr_t, ['停产','求','焦虑','回购','老粉','情感'], 'cvr'),
    method_card_with_cases("🏢 品牌/渠道背书", '山姆/奥莱/直营等强渠道信任背书，降低决策门槛', "诺亚 insight-v20", cvr_t, ['山姆','代购','背书','渠道','品牌','直营','奥莱'], 'cvr'),
    method_card_with_cases("📦 打包/组合拼单", '「一筐零食」「组合套装」降低单次决策成本，拼单场景', "creation-guide-v9 D9", cvr_t, ['拼单','打包','一筐','组合','套装','囤'], 'cvr'),
    method_card_with_cases("📊 具体解决方案", '明确说「怎么用/效果是什么」，降低用户不确定性', "creation-guide-v9 D2", cvr_t, ['解决','方案','效果','具体','怎么'], 'cvr'),
])
CVR_METHODS_NEW_V = ''.join([
    method_card_with_cases("🎯 精准人群锁定", '视频明确目标人群，精准触达', "creation-guide-v9 D5", cvr_v, ['人群','精准','锁定','针对'], 'cvr'),
    method_card_with_cases("⭐ 明星/达人同款", '明星同款+低价品类，强冲动+低决策成本', "creation-guide-v9 D4", cvr_v, ['明星','同款','达人','推荐'], 'cvr'),
    method_card_with_cases("🎭 解压/治愈场景", '解压/沉浸打包等情绪价值场景，疗愈刚需', "三感六度", cvr_v, ['解压','治愈','沉浸','疗愈','双眼'], 'cvr'),
    method_card_with_cases("🏅 夸张赞美+信任", '「好吃到双眼迷离」「不愧是高人指点」夸张表达种草', "诺亚 insight-v20", cvr_v, ['夸张','好吃','双眼','高人','不愧'], 'cvr'),
    method_card_with_cases("📦 购物车/行动召唤", '视频末尾「点购物车/评论区链接」明确行动指令', "creation-guide-v9 D9", cvr_v, ['购物车','链接','行动','评论区','下方'], 'cvr'),
])

price_t = data['top_cases']['price']['图文']
price_v = data['top_cases']['price']['视频']
PRICE_METHODS_NEW_T = ''.join([
    method_card_with_cases("🎁 礼盒/送礼场景", '送礼/孝心/节日场景标题，客单价天然高', "creation-guide-v9 D8", price_t, ['礼','送','节日','孝心','情人节'], 'price'),
    method_card_with_cases("🍷 专业术语/藏家黑话", '一级园/老藤/年份/配额等专业词，高客单品类自带高价', "诺亚 insight-v20", price_t, ['一级园','老藤','年份','配额','专业','黑话','术语'], 'price'),
    method_card_with_cases("🏆 产地/限量", '产地直发、限量款、联名款等稀缺属性拉价', "三感六度", price_t, ['产地','限量','联名','稀缺','限定','年份'], 'price'),
    method_card_with_cases("📦 大份装/家庭装", '全家装/囤货价/大份量，推高单笔购买量', "creation-guide-v9 D9", price_t, ['全家','囤','大份','家庭','装'], 'price'),
    method_card_with_cases("💎 高端/品质定位", '强调品质/工艺/产地溯源，主动建立高价值感', "creation-guide-v9 D5", price_t, ['品质','工艺','溯源','高端','精品','标杆'], 'price'),
])
PRICE_METHODS_NEW_V = ''.join([
    method_card_with_cases("🍷 专业术语/藏家黑话", '老茶/扫地僧传人/百年老藤等专业黑话，圈层高客单', "诺亚 insight-v20", price_v, ['扫地僧','老藤','黑话','专业','藏家','茶'], 'price'),
    method_card_with_cases("🏆 名酒/稀缺开箱", '100瓶黑金LLM/25周年等名酒开箱，实拍强背书', "三感六度", price_v, ['开箱','黑金','名酒','25周年','稀缺','批次'], 'price'),
    method_card_with_cases("🎁 高价值场景叙事", '婚庆/高端宴席/馈赠等场景，高价格有叙事撑腰', "creation-guide-v9 D8", price_v, ['婚庆','宴席','馈赠','宴请','高端'], 'price'),
    method_card_with_cases("📊 价值数字化", '均价超1000/一瓶抵多瓶等量化价值，建立高客单认知', "creation-guide-v9 D2", price_v, ['均价','抵','低于','价值','数字'], 'price'),
    method_card_with_cases("🌍 产地/年份溯源", '特定产区+年份，老茶/名庄等直接定价锚点', "诺亚 insight-v20", price_v, ['产地','年份','产区','溯源','批次'], 'price'),
])

# ========= 3. 更新 build 脚本里的方法论变量 =========
# 把旧的 CTR1_METHODS/CTR2_METHODS/CVR_METHODS/PRICE_METHODS 替换成新的内联版
# 同时修改 funnel_tab 函数——传入两套 methods（图文/视频各一份）

NEW_FUNNEL_TAB = '''
def funnel_tab(tab_id, icon, title, metric_key, methods_t, methods_v, is_price=False):
    """生成一个漏斗 Tab 的完整 HTML（方法论+案例内联版）"""
    pct = not is_price
    xushi_p75_t = xushi_t.get(f\'{metric_key}_p75\')
    xushi_p75_v = xushi_v.get(f\'{metric_key}_p75\')
    ka_p75_t = ka_t.get(f\'{metric_key}_p75\')
    ka_p75_v = ka_v.get(f\'{metric_key}_p75\')

    def level(v):
        if v is None: return \'—\'
        if pct:
            if metric_key == \'ctr1\': return \'高\' if v>=0.10 else (\'中等\' if v>=0.07 else \'一般\')
            if metric_key == \'ctr2\': return \'高\' if v>=0.25 else (\'中等\' if v>=0.10 else \'一般\')
            if metric_key == \'cvr\':  return \'高\' if v>=0.06 else (\'中等\' if v>=0.02 else \'一般\')
        else:
            return \'高\' if v>=60 else (\'中等\' if v>=30 else \'一般\')
        return \'中等\'

    def ka_cmp(x_p75, k_p75):
        if x_p75 is None or k_p75 is None: return \'\'
        diff = x_p75 - k_p75
        threshold = 0.01 if pct else 5
        if abs(diff) < threshold: return \'与大盘持平\'
        return \'优于大盘\' if diff > 0 else \'略低大盘\'

    return f\'\'\'<div class="tab-panel hidden" id="tab-{tab_id}">
  <div class="hero hero-sub hero-{tab_id}">
    <h2>{icon} {title}</h2>
    <p class="meta">方法论 + 本周休食案例（数据驱动，非唯一答案）</p>
  </div>

  <div class="section-label">🎯 本周休食优秀笔记水平</div>
  <div class="kpi-grid kpi-grid-2col">
    <div class="kpi-card">
      <div class="kpi-title">📈 图文</div>
      <div class="kpi-value" style="color:#ff2442">{level(xushi_p75_t)}</div>
      <div class="kpi-sub">优秀笔记水平</div>
      <div class="kpi-ka">{ka_cmp(xushi_p75_t, ka_p75_t)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🎬 视频</div>
      <div class="kpi-value" style="color:#ff2442">{level(xushi_p75_v)}</div>
      <div class="kpi-sub">优秀笔记水平</div>
      <div class="kpi-ka">{ka_cmp(xushi_p75_v, ka_p75_v)}</div>
    </div>
  </div>

  <div class="section-label">📚 图文路径 · 多样化参考（非唯一答案）</div>
  <div class="methods-grid">{methods_t}</div>

  <div class="section-label">🎬 视频路径 · 多样化参考</div>
  <div class="methods-grid">{methods_v}</div>

  <div class="tips-box">
    <strong>💡 怎么用：</strong> 每条方法下有 2 个本周真实案例。找到适合你品类的方向，仿写标题或封面策略。方法没有优先级，哪个适合你的产品就用哪个。
  </div>
</div>\'\'\'
'''

# 替换旧的 funnel_tab 定义
old_funnel_tab_start = 'def funnel_tab(tab_id, icon, title, metric_key, methods_html, is_price=False):'
old_funnel_tab_end = "return f'''<div class=\"tab-panel hidden\" id=\"tab-{tab_id}\">"
# 找到旧函数结束（返回 f''' 直到匹配的 '''）
idx_start = src.find(old_funnel_tab_start)
if idx_start == -1:
    print('[WARN] old funnel_tab not found, skipping')
else:
    # 找函数结束（下一个空行 + def / CTR1_METHODS）
    idx_end = src.find('\nCTR1_METHODS = ', idx_start)
    if idx_end == -1:
        print('[WARN] cannot find funnel_tab end')
    else:
        src = src[:idx_start] + NEW_FUNNEL_TAB.strip() + '\n' + src[idx_end:]
        print('[OK] funnel_tab 替换完成')

# 替换 4 个方法论变量 + 4 个 Tab 生成调用
import textwrap

NEW_METHODS_AND_TABS = f'''
CTR1_METHODS_T = {repr(CTR1_METHODS_NEW_T)}
CTR1_METHODS_V = {repr(CTR1_METHODS_NEW_V)}
CTR2_METHODS_T = {repr(CTR2_METHODS_NEW_T)}
CTR2_METHODS_V = {repr(CTR2_METHODS_NEW_V)}
CVR_METHODS_T  = {repr(CVR_METHODS_NEW_T)}
CVR_METHODS_V  = {repr(CVR_METHODS_NEW_V)}
PRICE_METHODS_T = {repr(PRICE_METHODS_NEW_T)}
PRICE_METHODS_V = {repr(PRICE_METHODS_NEW_V)}

TAB_CTR1 = funnel_tab('ctr1', '👆', '提升 CTR1：封面+标题钩子', 'ctr1', CTR1_METHODS_T, CTR1_METHODS_V)
TAB_CTR2 = funnel_tab('ctr2', '🔗', '提升 CTR2：商品卡点击', 'ctr2', CTR2_METHODS_T, CTR2_METHODS_V)
TAB_CVR  = funnel_tab('cvr',  '💰', '提升 CVR：转化下单',      'cvr',  CVR_METHODS_T,  CVR_METHODS_V)
TAB_PRICE= funnel_tab('price','💎', '提升件单价：客单优化',     'price',PRICE_METHODS_T,PRICE_METHODS_V, is_price=True)
'''

# 找旧的 CTR1_METHODS = ... 到 TAB_PRICE 结束
old_block_start = 'CTR1_METHODS = '
old_block_end_marker = "TAB_PRICE = funnel_tab('price', '💎', '提升件单价：客单优化', 'price', PRICE_METHODS, is_price=True)"
idx_s = src.find(old_block_start)
idx_e = src.find(old_block_end_marker)
if idx_s != -1 and idx_e != -1:
    src = src[:idx_s] + NEW_METHODS_AND_TABS.strip() + '\n' + src[idx_e + len(old_block_end_marker):]
    print('[OK] 方法论变量 + Tab 调用替换完成')
else:
    print(f'[WARN] cannot find method blocks: s={idx_s} e={idx_e}')

# 同时给 CSS 加 method-card-v2 和 inline-case 样式
NEW_CSS_EXTRA = '''
/* === V8b 内联方法论+案例 === */
.method-card-v2 { background:white; border:1px solid #eee; border-left:3px solid #ff2442; border-radius:8px; padding:14px; }
.method-card-v2 .method-title { font-weight:600; color:#333; font-size:14px; margin-bottom:4px; }
.method-card-v2 .method-desc { font-size:13px; color:#555; line-height:1.5; margin-bottom:10px; }
.method-card-v2 .method-cases { display:flex; flex-direction:column; gap:6px; margin-bottom:8px; }
.method-card-v2 .method-source { font-size:11px; color:#bbb; margin-top:4px; }
.inline-case { display:flex; flex-direction:column; background:#fafafa; border-radius:6px; padding:8px 10px; text-decoration:none; border:1px solid #f0f0f0; transition:background .15s; }
.inline-case:hover { background:#fff0f0; border-color:#ffcdd2; }
.ic-metric { display:inline-block; background:#ff2442; color:white; padding:1px 6px; border-radius:3px; font-size:11px; font-weight:600; margin-bottom:3px; width:fit-content; }
.ic-title { font-size:12px; color:#333; font-weight:500; margin-bottom:2px; }
.ic-hl { font-size:11px; color:#888; line-height:1.4; }
'''
src = src.replace('/* === V8 隐藏 V7 残留 === */', NEW_CSS_EXTRA + '\n/* === V8 隐藏 V7 残留 === */', 1)
print('[OK] CSS 内联案例样式注入完成')

with open(BUILD_PATH, 'w') as f:
    f.write(src)
print('[OK] build_v8_gpm.py 更新完成')

