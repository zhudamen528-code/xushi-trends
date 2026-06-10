#!/usr/bin/env python3
"""根据最新 data.json 重新生成 8 个 METHODS 变量并注入 build_v8_gpm.py"""
import json, re

WORK = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
BUILD = f'{WORK}/build_v8_gpm.py'

data = json.load(open(f'{WORK}/data.json'))
tc = data['top_cases']

# 去重机制：每个 Tab 内（同形态）案例不重复
def make_matcher():
    used = {}  # key=dedup_key, value=set of note_ids
    def match(cases, keywords, n=2, dedup_key='default'):
        if dedup_key not in used:
            used[dedup_key] = set()
        scored = []
        for c in cases:
            hl = (c.get('highlight') or '') + (c.get('title') or '')
            sc = sum(1 for kw in keywords if kw in hl)
            scored.append((sc, c))
        scored.sort(key=lambda x: -x[0])
        result = []
        for _, c in scored:
            if c['note_id'] not in used[dedup_key]:
                result.append(c)
                used[dedup_key].add(c['note_id'])
                if len(result) >= n:
                    break
        # 兜底不够补
        if len(result) < n:
            for _, c in scored:
                if c['note_id'] not in used[dedup_key]:
                    result.append(c)
                    used[dedup_key].add(c['note_id'])
                    if len(result) >= n:
                        break
        return result
    return match

def esc(s):
    if s is None: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def fmt_pct(v):
    if v is None: return '—'
    return f'{v*100:.1f}%'

def render_case(c, is_price=False):
    val = f'¥{c["value"]:.0f}' if is_price else fmt_pct(c['value'])
    title = c['title'] or '(无标题)'
    return (f'<a class="inline-case" href="{c["note_url"]}" target="_blank">'
            f'<span class="ic-metric">{val}</span>'
            f'<span class="ic-title">{esc(title[:25])}{"…" if len(title)>25 else ""}</span>'
            f'<span class="ic-hl">{esc(c.get("highlight",""))}</span></a>')

def method(title, desc, source, cases, kws, dedup_key, matcher, is_price=False):
    matched = matcher(cases, kws, n=2, dedup_key=dedup_key)
    cases_html = ''.join(render_case(c, is_price) for c in matched)
    return (f'<div class="method-card-v2"><div class="method-title">{title}</div>'
            f'<div class="method-desc">{desc}</div>'
            f'<div class="method-cases">{cases_html}</div>'
            f'<div class="method-source">来源：{source}</div></div>')

# 每个 Tab 独立 matcher（重置去重池）
def build_methods_tab(tab):
    return tab

# =============== CTR1 ===============
m = make_matcher()
CTR1_T = ''.join([
    method('📸 单主体+特写', '封面只放一个主体（产品/手部动作），剔除杂乱背景', '诺亚 insight-v20', tc['ctr1']['图文'], ['手','主体','特写','产品图'], 'ctr1_t', m),
    method('🔥 数字+反差词', '标题用数字钩子或反差词（如「100卡」「裸寄」「自黑」），吊起好奇', 'creation-guide-v9 D2', tc['ctr1']['图文'], ['数字','卡','反差','自黑','悬念','好奇'], 'ctr1_t', m),
    method('💬 情绪共鸣开头', '「打工人续命」「自律必吃」等第一人称场景，精准锁人群', 'creation-guide-v9 D5', tc['ctr1']['图文'], ['情绪','共鸣','场景','人群','自律','痛点','减脂','打工'], 'ctr1_t', m),
    method('🎭 拟声/趣味词', '「duangduang」「裸寄了」等趣味表达，内容味极强', '三感六度', tc['ctr1']['图文'], ['拟声','趣味','梗','话题','联想','谐音','社交'], 'ctr1_t', m),
    method('👀 反向/制造悬念', '自黑标题、神秘感留白、意外反转，用户不点不甘心', '诺亚 insight-v20', tc['ctr1']['图文'], ['悬念','神秘','留白','反转','反向','疑问','好奇'], 'ctr1_t', m),
])
m2 = make_matcher()
CTR1_V = ''.join([
    method('📸 单主体+特写', '视频开头用单主体+大特写或手部动作锁视线', '诺亚 insight-v20', tc['ctr1']['视频'], ['手','主体','特写','动作','首帧'], 'ctr1_v', m2),
    method('🔥 数字+反差词', '标题或视频前 3 秒抛数字钩子或反差', 'creation-guide-v9 D2', tc['ctr1']['视频'], ['数字','反差','钩子','秒','开头'], 'ctr1_v', m2),
    method('💬 情绪共鸣开头', '第一人称场景或情绪话术，精准锁人群', 'creation-guide-v9 D5', tc['ctr1']['视频'], ['情绪','共鸣','人群','场景','痛点'], 'ctr1_v', m2),
    method('🎬 视频口播钩子', '开头悬念/反问/报价，让用户继续看', 'creation-guide-v9 D9', tc['ctr1']['视频'], ['口播','悬念','反问','钩子','秒'], 'ctr1_v', m2),
    method('🌍 地域/产地背书', '「厦门老味道」「厂家直发」等产地词，增加真实感', '诺亚 insight-v20', tc['ctr1']['视频'], ['地域','产地','老味道','厦门','地方','本地'], 'ctr1_v', m2),
])

# =============== CTR2 ===============
m = make_matcher()
CTR2_T = ''.join([
    method('🏷️ 价格直给', '标题/封面露价格（9.9、6.6折、开业特惠），降低决策门槛', 'creation-guide-v9 D8', tc['ctr2']['图文'], ['价格','折','9.9','优惠','便宜','史低','开业'], 'ctr2_t', m),
    method('⏰ 节日/限时氛围', '节气、节假日、限时活动，制造时限紧迫感', '诺亚 insight-v20', tc['ctr2']['图文'], ['节','限时','618','开业','端午','节气','芒种','限定'], 'ctr2_t', m),
    method('📊 参数堆叠', '低卡+无面粉+高蛋白等多卖点参数化，商品卡信息密度高', 'creation-guide-v9 D9', tc['ctr2']['图文'], ['参数','卡','卖点','蛋白','无','成分','低','克'], 'ctr2_t', m),
    method('🏆 稀缺/催促', '「别停产」「催涨价」等稀缺感，触发囤货行为', '三感六度', tc['ctr2']['图文'], ['稀缺','催','停产','别','限量','紧迫','囤'], 'ctr2_t', m),
    method('💊 对症解决方案', '症状+产品=精准解决方案，商品卡承接感强', 'creation-guide-v9 D5', tc['ctr2']['图文'], ['症状','湿热','睡','功效','对症','补','上火'], 'ctr2_t', m),
])
m2 = make_matcher()
CTR2_V = ''.join([
    method('🏷️ 价格直给', '视频口播强调价格/活动，卡片价格曝光', 'creation-guide-v9 D8', tc['ctr2']['视频'], ['价格','折','优惠','便宜','史低','清仓'], 'ctr2_v', m2),
    method('👥 用户口碑/复购', '老用户回购、真实好评，建立信任', 'creation-guide-v9 D4', tc['ctr2']['视频'], ['复购','口碑','福利','老用户','回购','好评','信任'], 'ctr2_v', m2),
    method('🎭 拟声/口感描述', '感官卖点+视频场景还原（爆汁、剥皮、咀嚼）', '三感六度', tc['ctr2']['视频'], ['口感','爆','剥','咀嚼','沉浸','感官','治愈'], 'ctr2_v', m2),
    method('📦 具体配置/参数', '告诉用户买到什么（几个/几折/什么规格），减少决策摩擦', 'creation-guide-v9 D9', tc['ctr2']['视频'], ['参数','个','只','配置','几','套','规格'], 'ctr2_v', m2),
    method('🌍 场景代入', '高原/出行/节日精准场景，用户代入感强', '诺亚 insight-v20', tc['ctr2']['视频'], ['场景','高原','出行','人群','刚需','节日'], 'ctr2_v', m2),
])

# =============== CVR ===============
m = make_matcher()
CVR_T = ''.join([
    method('🎯 精准人群锁定', '标题含具体人群词（备孕/减脂/宝妈），过滤无效流量', 'creation-guide-v9 D5', tc['cvr']['图文'], ['人群','精准','减脂','宝妈','备孕','女性','锁定','针对'], 'cvr_t', m),
    method('💬 复购/口碑背书', '「回购率头榜」「老粉催更」复购数据背书减决策疑虑', 'creation-guide-v9 D4', tc['cvr']['图文'], ['复购','回购','口碑','老粉','回头','头榜','催'], 'cvr_t', m),
    method('🏢 品牌/渠道背书', '山姆/奥莱/直营等强渠道信任背书，降低决策门槛', '诺亚 insight-v20', tc['cvr']['图文'], ['山姆','代购','背书','渠道','品牌','直营','奥莱','官方'], 'cvr_t', m),
    method('📦 打包/组合拼单', '「一筐零食」「组合套装」降低单次决策成本', 'creation-guide-v9 D9', tc['cvr']['图文'], ['拼单','打包','一筐','组合','套装','囤','合集'], 'cvr_t', m),
    method('📊 具体解决方案', '明确说「怎么用/效果是什么」，降低用户不确定性', 'creation-guide-v9 D2', tc['cvr']['图文'], ['解决','方案','效果','具体','怎么','治','补'], 'cvr_t', m),
])
m2 = make_matcher()
CVR_V = ''.join([
    method('🎯 精准人群锁定', '视频明确目标人群，精准触达', 'creation-guide-v9 D5', tc['cvr']['视频'], ['人群','精准','锁定','针对','群体'], 'cvr_v', m2),
    method('⭐ 明星/达人同款', '达人推荐+低价品类，强冲动+低决策成本', 'creation-guide-v9 D4', tc['cvr']['视频'], ['明星','同款','达人','推荐','背书'], 'cvr_v', m2),
    method('🎭 解压/治愈场景', '解压/沉浸打包等情绪价值场景，疗愈刚需', '三感六度', tc['cvr']['视频'], ['解压','治愈','沉浸','疗愈','情绪','感官'], 'cvr_v', m2),
    method('🏅 夸张赞美+稀缺', '「灵魂菜」「天才发明」等夸张表达种草', '诺亚 insight-v20', tc['cvr']['视频'], ['夸张','灵魂','天才','绝','神','极'], 'cvr_v', m2),
    method('📦 行动召唤', '视频末尾「点购物车/评论区链接」明确行动指令', 'creation-guide-v9 D9', tc['cvr']['视频'], ['购物车','链接','行动','评论区','下方','点击'], 'cvr_v', m2),
])

# =============== Price/AOV ===============
m = make_matcher()
PRICE_T = ''.join([
    method('🎁 礼盒/送礼场景', '送礼/孝心/节日场景标题，客单价天然高', 'creation-guide-v9 D8', tc['price']['图文'], ['礼','送','节','孝心','端午','中秋','礼盒'], 'price_t', m),
    method('🍷 专业术语/藏家黑话', '一级园/老藤/年份/批次等专业词，高客单品类自带高价', '诺亚 insight-v20', tc['price']['图文'], ['一级园','老藤','年份','配额','专业','批次','黑话','藏家'], 'price_t', m),
    method('🏆 产地/限量', '产地直发、限量款、联名款等稀缺属性拉价', '三感六度', tc['price']['图文'], ['产地','限量','联名','稀缺','限定','产区'], 'price_t', m),
    method('📦 大份装/家庭装', '全家装/囤货价/大份量，推高单笔购买量', 'creation-guide-v9 D9', tc['price']['图文'], ['全家','囤','大份','家庭','装','超值'], 'price_t', m),
    method('💎 高端/品质定位', '强调品质/工艺/产地溯源，主动建立高价值感', 'creation-guide-v9 D5', tc['price']['图文'], ['品质','工艺','溯源','高端','精品','标杆','旗舰'], 'price_t', m),
])
m2 = make_matcher()
PRICE_V = ''.join([
    method('🍷 专业术语/藏家黑话', '老茶/扫地僧传人/百年老藤等专业黑话，圈层高客单', '诺亚 insight-v20', tc['price']['视频'], ['扫地僧','老藤','黑话','专业','藏家','茶','级'], 'price_v', m2),
    method('🏆 名酒/稀缺开箱', '名酒开箱/限量批次/年份酒，实拍强背书', '三感六度', tc['price']['视频'], ['开箱','名酒','稀缺','批次','年份','限量','版'], 'price_v', m2),
    method('🎁 高价值场景叙事', '婚庆/高端宴席/馈赠等场景，高价格有叙事撑腰', 'creation-guide-v9 D8', tc['price']['视频'], ['婚庆','宴席','馈赠','宴请','高端','送'], 'price_v', m2),
    method('📊 价值数字化', '均价超1000/一瓶抵多瓶等量化价值，建立高客单认知', 'creation-guide-v9 D2', tc['price']['视频'], ['均价','抵','低于','价值','数字','元'], 'price_v', m2),
    method('🌍 产地/年份溯源', '特定产区+年份，名庄/老茶直接定价锚点', '诺亚 insight-v20', tc['price']['视频'], ['产地','年份','产区','溯源','批次','庄'], 'price_v', m2),
])

# 注入到 build 脚本
src = open(BUILD).read()
new_block = (
    f"CTR1_METHODS_T = {CTR1_T!r}\n"
    f"CTR1_METHODS_V = {CTR1_V!r}\n"
    f"CTR2_METHODS_T = {CTR2_T!r}\n"
    f"CTR2_METHODS_V = {CTR2_V!r}\n"
    f"CVR_METHODS_T  = {CVR_T!r}\n"
    f"CVR_METHODS_V  = {CVR_V!r}\n"
    f"PRICE_METHODS_T = {PRICE_T!r}\n"
    f"PRICE_METHODS_V = {PRICE_V!r}\n"
)

# 用正则替换从 CTR1_METHODS_T 开始到 PRICE_METHODS_V 结束
pattern = re.compile(r"CTR1_METHODS_T = '.*?\nPRICE_METHODS_V = '.*?'\n", re.DOTALL)
m_obj = pattern.search(src)
if not m_obj:
    print('[ERR] pattern not found')
    exit(1)
src_new = src[:m_obj.start()] + new_block + src[m_obj.end():]
open(BUILD, 'w').write(src_new)
print(f'[OK] 8 个 METHODS 变量已更新（{len(new_block)} chars）')
