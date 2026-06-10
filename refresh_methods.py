#!/usr/bin/env python3
"""V8d 升级版：①修件单价%bug ②空值兜底 ③CTR1/CTR2 案例拆标题+封面建议 ④件单价方法论加货品组合玩法"""
import json, re

WORK = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
BUILD = f'{WORK}/build_v8_gpm.py'

data = json.load(open(f'{WORK}/data.json'))
tc = data['top_cases']

# 空值兜底：fallback 文本
NA = '—'

def make_matcher():
    used = {}
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
        if len(result) < n:
            for _, c in scored:
                if c['note_id'] not in used[dedup_key]:
                    result.append(c)
                    used[dedup_key].add(c['note_id'])
                    if len(result) >= n:
                        break
        # 兜底再不够：从全部 cases 里随便补（避免空白）
        if len(result) < n and cases:
            for c in cases:
                if c['note_id'] not in used[dedup_key]:
                    result.append(c)
                    used[dedup_key].add(c['note_id'])
                    if len(result) >= n:
                        break
        return result
    return match

def esc(s):
    if s is None: return NA
    s = str(s)
    if not s.strip(): return NA
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def fmt_pct(v):
    if v is None: return NA
    return f'{v*100:.1f}%'

def fmt_money(v):
    if v is None: return NA
    return f'¥{v:.0f}'

def fmt_int(v):
    if v is None: return NA
    return f'{int(v):,}'

def render_case(c, metric_key='ctr1'):
    """V8d: 案例卡 = 数据条 + 标题 + 亮点解析；价格类用 ¥ 不用 %"""
    is_price = (metric_key == 'price')
    if is_price:
        val = fmt_money(c.get('value'))
    else:
        val = fmt_pct(c.get('value'))
    title = c.get('title') or NA
    if title == NA or not str(title).strip():
        title = '(无标题)'
    title_disp = title[:26] + ('…' if len(title) > 26 else '')
    hl = c.get('highlight') or NA
    url = c.get('note_url') or '#'
    seller = c.get('seller_name') or NA
    # 副指标小字（曝光/下单 让数据有支撑感）
    imp = fmt_int(c.get('imp'))
    buy = fmt_int(c.get('buy'))
    gmv = fmt_money(c.get('dgmv'))
    return (
        f'<a class="inline-case" href="{url}" target="_blank">'
        f'<div class="ic-head"><span class="ic-metric">{val}</span>'
        f'<span class="ic-seller">{esc(seller)[:15]}</span></div>'
        f'<div class="ic-title">{esc(title_disp)}</div>'
        f'<div class="ic-hl">{esc(hl)}</div>'
        f'<div class="ic-meta">曝光 {imp} · 下单 {buy} · 成交 {gmv}</div>'
        f'</a>'
    )

def method(title, desc, source, cases, kws, dedup_key, matcher, metric_key='ctr1', cover_tip=None, title_tip=None):
    """V8d: 方法卡支持"标题怎么写/封面怎么做"双 tip（CTR1 用）"""
    matched = matcher(cases, kws, n=2, dedup_key=dedup_key)
    cases_html = ''.join(render_case(c, metric_key) for c in matched)
    tip_block = ''
    if title_tip or cover_tip:
        parts = []
        if cover_tip:
            parts.append(f'<div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>{esc(cover_tip)}</div>')
        if title_tip:
            parts.append(f'<div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>{esc(title_tip)}</div>')
        tip_block = f'<div class="method-tips">{"".join(parts)}</div>'
    return (
        f'<div class="method-card-v2">'
        f'<div class="method-title">{title}</div>'
        f'<div class="method-desc">{esc(desc)}</div>'
        f'{tip_block}'
        f'<div class="method-cases">{cases_html}</div>'
        f'<div class="method-source">参考：{esc(source)}</div>'
        f'</div>'
    )

# =============== CTR1 (封面+标题钩子) — 加 cover/title 双 tip ===============
m = make_matcher()
CTR1_T = ''.join([
    method('🎯 单主体+清晰特写', '减少封面元素，让用户 1 秒看清"是什么"',
           '诺亚 insight-v20', tc['ctr1']['图文'],
           ['手','主体','特写','产品图'], 'ctr1_t', m,
           metric_key='ctr1',
           cover_tip='产品大特写居中 / 手部操作场景 / 干净背景',
           title_tip='产品名 + 1 个核心卖点（不超 15 字）'),
    method('🔥 数字+反差词', '用数字或反差词制造强钩子，吊起用户好奇',
           'creation-guide-v9 D2', tc['ctr1']['图文'],
           ['数字','卡','反差','悬念','好奇','克','斤'], 'ctr1_t', m,
           metric_key='ctr1',
           cover_tip='大字数字海报：100卡 / 9.9元 / 99%人不知道',
           title_tip='公式：「具体数字 + 反差结果」如 "90斤吃这个变 60 斤"'),
    method('💬 情绪共鸣开头', '第一人称场景或人群词，让目标用户对号入座',
           'creation-guide-v9 D5', tc['ctr1']['图文'],
           ['情绪','场景','自律','减脂','打工','痛点','人群'], 'ctr1_t', m,
           metric_key='ctr1',
           cover_tip='真实使用场景照（书桌/早餐桌/办公室）',
           title_tip='开头用"我/打工人/宝妈/减脂期"等身份词锁人群'),
    method('🎭 拟声/趣味表达', '感官词+趣味表达，封面+标题强内容味',
           '三感六度', tc['ctr1']['图文'],
           ['拟声','梗','话题','谐音','社交','duang'], 'ctr1_t', m,
           metric_key='ctr1',
           cover_tip='夸张表情包 / 反差对比图 / 食物特写+滴落感',
           title_tip='用拟声词（duangduang/咔嚓/嘎嘣）或网络梗'),
    method('👀 反向/悬念', '自黑/留白/反转，引发好奇必点',
           '诺亚 insight-v20', tc['ctr1']['图文'],
           ['悬念','神秘','留白','反转','反向','疑问'], 'ctr1_t', m,
           metric_key='ctr1',
           cover_tip='只露局部不露全貌 / "丑首图"反向引流',
           title_tip='问句结尾或卖关子："你猜这是？" / "都没人发现…"'),
])
m2 = make_matcher()
CTR1_V = ''.join([
    method('🎬 首帧强主体', '视频前 0.5 秒就要看到主角',
           '诺亚 insight-v20', tc['ctr1']['视频'],
           ['手','主体','特写','动作','首帧','吃'], 'ctr1_v', m2,
           metric_key='ctr1',
           cover_tip='视频首帧 = 产品大特写或主角眼神特写',
           title_tip='副标用动词："吃 / 试 / 测 / 开"'),
    method('🔥 反差+数字钩子', '前 3 秒抛出反差或具体数字',
           'creation-guide-v9 D2', tc['ctr1']['视频'],
           ['数字','反差','钩子','秒','开头'], 'ctr1_v', m2,
           metric_key='ctr1',
           cover_tip='封面叠大字反差："谁能想到 5 块买到？"',
           title_tip='"X天/X斤/X次"类带数字的反差结果'),
    method('💬 情绪共鸣开场', '第一人称口播+情绪话术锁人群',
           'creation-guide-v9 D5', tc['ctr1']['视频'],
           ['情绪','共鸣','人群','场景','痛点'], 'ctr1_v', m2,
           metric_key='ctr1',
           cover_tip='主播个人特写表情（兴奋/惊讶/无奈）',
           title_tip='开口直接喊人群："姐妹们" / "打工人" / "宝妈们"'),
    method('🎯 视频悬念口播', '开头反问/报价/悬念锁停留',
           'creation-guide-v9 D9', tc['ctr1']['视频'],
           ['口播','悬念','反问','钩子','秒'], 'ctr1_v', m2,
           metric_key='ctr1',
           cover_tip='封面问号或大字悬念："这能吃吗？"',
           title_tip='开头反问句："你敢信这是 X 做的吗？"'),
    method('🌍 地域/产地背书', '产地词+地方梗，增强真实感',
           '诺亚 insight-v20', tc['ctr1']['视频'],
           ['地域','产地','老味道','地方','本地','省','市'], 'ctr1_v', m2,
           metric_key='ctr1',
           cover_tip='产地实景：田间/工厂/老店招牌',
           title_tip='标题前缀地点："厦门" / "云南" / "潮汕"'),
])

# =============== CTR2 (商品卡承接) — 拆"商品卡设计/正文埋点" ===============
m = make_matcher()
CTR2_T = ''.join([
    method('🏷️ 价格直给', '正文/商品卡直接亮价格，降低决策门槛',
           'creation-guide-v9 D8', tc['ctr2']['图文'],
           ['价格','折','9.9','优惠','便宜','史低','开业','元'], 'ctr2_t', m,
           metric_key='ctr2',
           cover_tip='封面带大字价格 "9.9 元/件"',
           title_tip='正文第一段先报价 + 多少件买够'),
    method('⏰ 节日/限时氛围', '节气节日制造紧迫感',
           '诺亚 insight-v20', tc['ctr2']['图文'],
           ['节','限时','618','开业','端午','节气','限定','活动'], 'ctr2_t', m,
           metric_key='ctr2',
           cover_tip='封面带节日符号 / 倒计时元素',
           title_tip='正文提及"今日截止 / 仅 X 天 / 限时" 等时效词'),
    method('📊 参数堆叠', '一图说清"几个卖点"提升商品卡决策',
           'creation-guide-v9 D9', tc['ctr2']['图文'],
           ['参数','卡','卖点','蛋白','无','成分','低','克'], 'ctr2_t', m,
           metric_key='ctr2',
           cover_tip='封面/详情图：表格化罗列 5+ 参数',
           title_tip='正文用 emoji 罗列：✅低卡 ✅无糖 ✅高蛋白'),
    method('🏆 稀缺/催促', '触发"再不买就没了"心智',
           '三感六度', tc['ctr2']['图文'],
           ['稀缺','催','停产','别','限量','紧迫','囤','最后'], 'ctr2_t', m,
           metric_key='ctr2',
           cover_tip='封面写"最后 X 件" / "停产倒计时"',
           title_tip='标题/正文用"求别停产 / 仓库只剩 X 件" 强稀缺词'),
    method('💊 对症解决方案', '把产品 = 用户问题的解药',
           'creation-guide-v9 D5', tc['ctr2']['图文'],
           ['症状','湿热','睡','功效','对症','补','上火','虚'], 'ctr2_t', m,
           metric_key='ctr2',
           cover_tip='封面问"X 症状怎么办？" → 答案是产品',
           title_tip='正文用"3 天见效 / 1 周改善"等具体效果承诺'),
])
m2 = make_matcher()
CTR2_V = ''.join([
    method('🏷️ 视频强报价', '主播直接喊价格+活动',
           'creation-guide-v9 D8', tc['ctr2']['视频'],
           ['价格','折','优惠','便宜','史低','清仓','元'], 'ctr2_v', m2,
           metric_key='ctr2',
           cover_tip='封面文案：大字价格 + 划线原价',
           title_tip='视频前 5 秒口播："今天只要 X 元"'),
    method('👥 用户口碑/复购', '老用户回购+真实好评',
           'creation-guide-v9 D4', tc['ctr2']['视频'],
           ['复购','口碑','福利','老用户','回购','好评','信任'], 'ctr2_v', m2,
           metric_key='ctr2',
           cover_tip='封面带"老粉回购第 X 次" / 客户截图',
           title_tip='视频中插用户原话："朋友买了又来回购"'),
    method('🎭 感官+口感', '拍出产品质感（爆汁/拉丝/酥脆）',
           '三感六度', tc['ctr2']['视频'],
           ['口感','爆','剥','咀嚼','沉浸','感官','治愈'], 'ctr2_v', m2,
           metric_key='ctr2',
           cover_tip='慢镜头特写：切开瞬间/爆汁瞬间',
           title_tip='标题用感官词："爆汁 / 拉丝 / 嘎嘣脆"'),
    method('📦 配置一图清', '商品卡明确说"买到几个/几折"',
           'creation-guide-v9 D9', tc['ctr2']['视频'],
           ['参数','个','只','配置','几','套','规格','件'], 'ctr2_v', m2,
           metric_key='ctr2',
           cover_tip='封面或商品卡：「X 套装 = X 件」明列配置',
           title_tip='标题写明数量："5 件套 / 一年量装"'),
    method('🌍 场景代入', '锁定特定使用场景',
           '诺亚 insight-v20', tc['ctr2']['视频'],
           ['场景','高原','出行','人群','刚需','节日','送'], 'ctr2_v', m2,
           metric_key='ctr2',
           cover_tip='封面用使用场景图（旅行/办公/聚餐）',
           title_tip='标题挂场景："出差必备" / "高考刚需"'),
])

# =============== CVR (转化推力) ===============
m = make_matcher()
CVR_T = ''.join([
    method('🎯 精准人群锁定', '标题人群词 → 过滤无效流量',
           'creation-guide-v9 D5', tc['cvr']['图文'],
           ['人群','精准','减脂','宝妈','备孕','女性','锁定','针对'], 'cvr_t', m, metric_key='cvr'),
    method('💬 复购数据背书', '亮"回购率/老粉催更"减疑虑',
           'creation-guide-v9 D4', tc['cvr']['图文'],
           ['复购','回购','口碑','老粉','回头','头榜','催'], 'cvr_t', m, metric_key='cvr'),
    method('🏢 品牌/渠道背书', '山姆/奥莱/直营等强信任来源',
           '诺亚 insight-v20', tc['cvr']['图文'],
           ['山姆','代购','背书','渠道','品牌','直营','奥莱','官方'], 'cvr_t', m, metric_key='cvr'),
    method('📦 打包组合拼单', '降低单次决策门槛',
           'creation-guide-v9 D9', tc['cvr']['图文'],
           ['拼单','打包','一筐','组合','套装','囤','合集'], 'cvr_t', m, metric_key='cvr'),
    method('📊 解决方案明确', '说清"怎么用 / 效果是什么"',
           'creation-guide-v9 D2', tc['cvr']['图文'],
           ['解决','方案','效果','具体','怎么','治','补'], 'cvr_t', m, metric_key='cvr'),
])
m2 = make_matcher()
CVR_V = ''.join([
    method('🎯 精准人群锁定', '视频明确目标人群',
           'creation-guide-v9 D5', tc['cvr']['视频'],
           ['人群','精准','锁定','针对','群体'], 'cvr_v', m2, metric_key='cvr'),
    method('⭐ 达人/明星同款', '强冲动+低决策成本',
           'creation-guide-v9 D4', tc['cvr']['视频'],
           ['明星','同款','达人','推荐','背书'], 'cvr_v', m2, metric_key='cvr'),
    method('🎭 解压/治愈场景', '情绪价值刚需',
           '三感六度', tc['cvr']['视频'],
           ['解压','治愈','沉浸','疗愈','情绪','感官'], 'cvr_v', m2, metric_key='cvr'),
    method('🏅 夸张赞美种草', '"灵魂菜 / 天才发明" 类强主观推荐',
           '诺亚 insight-v20', tc['cvr']['视频'],
           ['夸张','灵魂','天才','绝','神','极'], 'cvr_v', m2, metric_key='cvr'),
    method('📦 行动召唤', '末尾明确"点购物车"指令',
           'creation-guide-v9 D9', tc['cvr']['视频'],
           ['购物车','链接','行动','评论区','下方','点击'], 'cvr_v', m2, metric_key='cvr'),
])

# =============== Price (件单价) — V8d 新增货品组合玩法 ===============
m = make_matcher()
PRICE_T = ''.join([
    method('🎁 货品组合：套装/礼盒', '【货品玩法】把多个 SKU 打成礼盒套装，自然提客单',
           '货品玩法', tc['price']['图文'],
           ['礼','送','节','礼盒','套装','组合','装','箱'], 'price_t', m, metric_key='price',
           title_tip='标题写"X件套 / 礼盒装 / 一箱"凸显数量'),
    method('💰 货品玩法：多件多折', '【货品玩法】「2件8折/3件7折」降低多买阻力',
           '货品玩法', tc['price']['图文'],
           ['多件','折','满','送','省','囤','超值'], 'price_t', m, metric_key='price',
           title_tip='标题直接写"2 件立减 X" / "买 3 送 1"'),
    method('🎁 货品玩法：赠品机制', '【货品玩法】"满 X 送赠品"提升下单意愿',
           '货品玩法', tc['price']['图文'],
           ['赠','送','加送','额外','福利','满'], 'price_t', m, metric_key='price',
           title_tip='标题挂赠品："下单送杯子 / 送试饮装"'),
    method('🍷 专业术语/藏家黑话', '一级园/老藤/年份/批次等专业词撑高价',
           '诺亚 insight-v20', tc['price']['图文'],
           ['一级园','老藤','年份','配额','专业','批次','黑话','藏家'], 'price_t', m, metric_key='price'),
    method('💎 高端品质定位', '强调品质/工艺/产地溯源',
           'creation-guide-v9 D5', tc['price']['图文'],
           ['品质','工艺','溯源','高端','精品','标杆','旗舰','限量'], 'price_t', m, metric_key='price'),
])
m2 = make_matcher()
PRICE_V = ''.join([
    method('🎁 货品组合：套装/礼盒', '【货品玩法】视频展示套装组合的丰富度',
           '货品玩法', tc['price']['视频'],
           ['礼','套装','组合','礼盒','箱','装'], 'price_v', m2, metric_key='price',
           title_tip='标题写"高端礼盒 / 婚宴套装"'),
    method('💰 货品玩法：多件多折', '【货品玩法】视频明确说"2 件 X 元/箱装更划算"',
           '货品玩法', tc['price']['视频'],
           ['多件','折','满','囤','整箱','超值'], 'price_v', m2, metric_key='price',
           title_tip='标题"整箱购 / 多件立省"'),
    method('🍷 专业术语/藏家黑话', '老茶/扫地僧传人/批次年份的圈层定价',
           '诺亚 insight-v20', tc['price']['视频'],
           ['扫地僧','老藤','黑话','专业','藏家','茶','级','批次'], 'price_v', m2, metric_key='price'),
    method('🏆 名品开箱叙事', '名酒名茶开箱+实拍背书',
           '三感六度', tc['price']['视频'],
           ['开箱','名酒','稀缺','批次','年份','限量','版'], 'price_v', m2, metric_key='price'),
    method('💎 价值数字化', '"均价超 X / 一瓶抵 N 瓶" 建立高客单认知',
           'creation-guide-v9 D2', tc['price']['视频'],
           ['均价','抵','低于','价值','数字','元','瓶'], 'price_v', m2, metric_key='price'),
])

# 注入 build
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
pattern = re.compile(r"CTR1_METHODS_T = '.*?\nPRICE_METHODS_V = '.*?'\n", re.DOTALL)
m_obj = pattern.search(src)
if not m_obj:
    print('[ERR] pattern not found')
    exit(1)
src_new = src[:m_obj.start()] + new_block + src[m_obj.end():]
open(BUILD, 'w').write(src_new)
print(f'[OK] V8d METHODS 已注入（{len(new_block)} chars）')
