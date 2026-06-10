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
    """Tab1: 给行业参考值（优秀线/中位）+ 商家可对照自己后台"""
    fmt = fmt_pct if pct else fmt_money
    return f'''<div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{fmt(p75)}</div>
      <div class="kpi-sub">行业优秀线（参考）</div>
      <div class="kpi-ka">行业中位：{fmt(p50)}</div>
    </div>'''

# ============ Tab1 GPM 总览 ============
TAB1 = f'''<div class="tab-panel" id="tab-gpm">
  <div class="hero">
    <h2>📊 GPM 漏斗 · 本周大盘</h2>
    <p class="meta">数据窗口：{data['window']['start_dtm'][:4]}-{data['window']['start_dtm'][4:6]}-{data['window']['start_dtm'][6:8]} 至 {data['window']['end_dtm'][:4]}-{data['window']['end_dtm'][4:6]}-{data['window']['end_dtm'][6:8]} · 笔记发布≥{data['window']['publish_min']} · 更新 {data['updated_at']}</p>
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
    <strong>💡 怎么看：</strong> 把行业优秀线 / 中位作为参考，对照你后台笔记的封面点击率、商品卡点击率、转化率、客单价数据。<strong>哪一环明显落后行业，就优先优化哪一环</strong>。点击上方 Tab 看对应环节的方法路径 + 本周休食优秀案例。<br><br>
    数据基于近 4 周休食类目所有商品笔记的统计结果，每周一更新。
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

def funnel_tab(tab_id, icon, title, metric_key, methods_t, methods_v, is_price=False):
    """生成一个漏斗 Tab 的完整 HTML（方法论+案例内联版）"""
    pct = not is_price
    xushi_p75_t = xushi_t.get(f'{metric_key}_p75')
    xushi_p75_v = xushi_v.get(f'{metric_key}_p75')
    ka_p75_t = ka_t.get(f'{metric_key}_p75')
    ka_p75_v = ka_v.get(f'{metric_key}_p75')

    xushi_p50_t = xushi_t.get(f'{metric_key}_p50')
    xushi_p50_v = xushi_v.get(f'{metric_key}_p50')
    fmt = fmt_pct if pct else fmt_money

    return f'''<div class="tab-panel hidden" id="tab-{tab_id}">
  <div class="hero hero-sub hero-{tab_id}">
    <h2>{icon} {title}</h2>
    <p class="meta">方法论 + 本周休食案例（数据驱动，非唯一答案）</p>
  </div>

  <div class="section-label">🎯 行业参考值（对照你的笔记后台数据）</div>
  <div class="kpi-grid kpi-grid-2col">
    <div class="kpi-card">
      <div class="kpi-title">📈 图文</div>
      <div class="kpi-value">{fmt(xushi_p75_t)}</div>
      <div class="kpi-sub">行业优秀线（参考）</div>
      <div class="kpi-ka">行业中位：{fmt(xushi_p50_t)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-title">🎬 视频</div>
      <div class="kpi-value">{fmt(xushi_p75_v)}</div>
      <div class="kpi-sub">行业优秀线（参考）</div>
      <div class="kpi-ka">行业中位：{fmt(xushi_p50_v)}</div>
    </div>
  </div>

  <div class="section-label">📚 图文路径 · 多样化参考（非唯一答案）</div>
  <div class="methods-grid">{methods_t}</div>

  <div class="section-label">🎬 视频路径 · 多样化参考</div>
  <div class="methods-grid">{methods_v}</div>

  <div class="tips-box">
    <strong>💡 怎么用：</strong> 每条方法下有 2 个本周真实案例。找到适合你品类的方向，仿写标题或封面策略。方法没有优先级，哪个适合你的产品就用哪个。
  </div>
</div>'''

CTR1_METHODS_T = '<div class="method-card-v2"><div class="method-title">📸 单主体+特写</div><div class="method-desc">封面只放一个主体（产品/手部动作），剔除杂乱背景</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a213d4600000000350283c3" target="_blank"><span class="ic-metric">28.1%</span><span class="ic-title">泪水不用打湿剪脂餐了</span><span class="ic-hl">「剪脂餐+泪水」情绪反差，戳减脂痛点</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1aa07900000000070210fa" target="_blank"><span class="ic-metric">27.1%</span><span class="ic-title">其实缺蛋白质的人都有一个明显共性。。。</span><span class="ic-hl">「缺蛋白质共性」悬念句，钩健身人群</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 数字+反差词</div><div class="method-desc">标题用数字钩子或反差词（如「100卡」「裸寄」「自黑」），吊起好奇</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a214c980000000022026589" target="_blank"><span class="ic-metric">24.7%</span><span class="ic-title">我：有没有可能，它本来就是巧克力味呢❓❓❓❓</span><span class="ic-hl">反问句「本来就是」制造认知反差</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2120ee0000000006031444" target="_blank"><span class="ic-metric">23.9%</span><span class="ic-title">瘦到90斤的同事每天吃的午饭</span><span class="ic-hl">「瘦到90斤+同事午饭」反差人群+窥探欲</span></a></div><div class="method-source">来源：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开头</div><div class="method-desc">「打工人续命」「自律必吃」等第一人称场景，精准锁人群</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2156810000000022024977" target="_blank"><span class="ic-metric">21.7%</span><span class="ic-title">高考只剩下3天，很多人已经快没电了</span><span class="ic-hl">「高考3天+没电」共鸣考生家长情绪</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16b6930000000035038877" target="_blank"><span class="ic-metric">24.6%</span><span class="ic-title">🧋冷泡牛奶茶🧊测试完成！</span><span class="ic-hl">「冷泡牛奶茶+测试完成」实验感钩奶系人群</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎭 拟声/趣味词</div><div class="method-desc">「duangduang」「裸寄了」等趣味表达，内容味极强</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bd12a0000000007020a70" target="_blank"><span class="ic-metric">25.8%</span><span class="ic-title">一口沦陷！云朵牛乳也太温柔了☁️</span><span class="ic-hl">「云朵牛乳/温柔」拟态形容词诱食</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1eca8500000000350215a7" target="_blank"><span class="ic-metric">25.4%</span><span class="ic-title">现泡铂金黑咖啡！拧→摇→享3步搞定☕️  </span><span class="ic-hl">拧→摇→享三步钩，咖啡仪式感拆解</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">👀 反向/制造悬念</div><div class="method-desc">自黑标题、神秘感留白、意外反转，用户不点不甘心</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1692c3000000003502cdca" target="_blank"><span class="ic-metric">22.4%</span><span class="ic-title">你抄袭的数量永远跟不上我玻璃壶的质量🤣🤣</span><span class="ic-hl">「抄袭/玻璃壶」吐槽体，悬念+人群猎奇</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e422f000000000701219e" target="_blank"><span class="ic-metric">21.9%</span><span class="ic-title">我们的南昌拌粉变短了</span><span class="ic-hl">「南昌拌粉变短」地域+变化制造悬念</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div>'
CTR1_METHODS_V = '<div class="method-card-v2"><div class="method-title">📸 单主体+特写</div><div class="method-desc">视频开头用单主体+大特写或手部动作锁视线</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16d3d60000000036018d28" target="_blank"><span class="ic-metric">17.2%</span><span class="ic-title">不是真农户哪有这手速？看老妈沉浸式采竹荪</span><span class="ic-hl">「真农户手速+老妈采竹荪」溯源人物钩</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1abe150000000037035630" target="_blank"><span class="ic-metric">21.2%</span><span class="ic-title">同事吃了一口立马问我要烤鹅蛋🥚的链接</span><span class="ic-hl">「同事一口要链接」社交反应钩烤鹅蛋</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 数字+反差词</div><div class="method-desc">标题或视频前 3 秒抛数字钩子或反差</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2665930000000007024f37" target="_blank"><span class="ic-metric">18.0%</span><span class="ic-title">囤了不下10次…干巴酸奶真的好吃到惊为天人</span><span class="ic-hl">「囤10次+惊为天人」复购数字+情绪强钩</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d642400000000350243e5" target="_blank"><span class="ic-metric">16.2%</span><span class="ic-title">减脂期狂喜😁挖到了解馋又健康的零食！！！</span><span class="ic-hl">「减脂期+狂喜」人群词+情绪反差</span></a></div><div class="method-source">来源：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开头</div><div class="method-desc">第一人称场景或情绪话术，精准锁人群</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1a8dab00000000060218f0" target="_blank"><span class="ic-metric">16.0%</span><span class="ic-title">孕36周涨13斤，一篇说清我如何有效控制体重</span><span class="ic-hl">「孕36周涨13斤」精确数字+孕妈痛点共鸣</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2652400000000017029136" target="_blank"><span class="ic-metric">18.5%</span><span class="ic-title">我的料汁教程</span><span class="ic-hl">「料汁教程」实操干货钩做饭人群</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎬 视频口播钩子</div><div class="method-desc">开头悬念/反问/报价，让用户继续看</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a202132000000003503b363" target="_blank"><span class="ic-metric">16.7%</span><span class="ic-title">晚熟南高梅，还有两天就开始采摘啦</span><span class="ic-hl">「晚熟+采摘倒计时」鲜货时令悬念</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e1350000000003503a97a" target="_blank"><span class="ic-metric">16.4%</span><span class="ic-title">姐姐！你的双眼皮贴是何意味呢！</span><span class="ic-hl">「双眼皮贴何意味」整活悬念钩猎奇</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 地域/产地背书</div><div class="method-desc">「厦门老味道」「厂家直发」等产地词，增加真实感</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e859c0000000035028c6a" target="_blank"><span class="ic-metric">20.3%</span><span class="ic-title">水煮菜可以退休了…</span><span class="ic-hl">「水煮菜退休」夸张拟人句钩减脂党</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a25485e000000001503e85e" target="_blank"><span class="ic-metric">19.8%</span><span class="ic-title">(无标题)</span><span class="ic-hl">无标题，仅靠封面承接，标题维度缺失</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div>'
CTR2_METHODS_T = '<div class="method-card-v2"><div class="method-title">🏷️ 价格直给</div><div class="method-desc">标题/封面露价格（9.9、6.6折、开业特惠），降低决策门槛</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e61e0000000003700e840" target="_blank"><span class="ic-metric">80.4%</span><span class="ic-title">🔥小红书专属羊毛！¥9.9到手100g精品咖啡豆</span><span class="ic-hl">「9.9元100g精品豆」价格+品类直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1aa86a000000003503129c" target="_blank"><span class="ic-metric">66.1%</span><span class="ic-title">对不起了pxx 我们xhs9.9r3个碱水棒包邮到…</span><span class="ic-hl">「9.9/3个+包邮到家」拼多多对标价格直给</span></a></div><div class="method-source">来源：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">⏰ 节日/限时氛围</div><div class="method-desc">节气、节假日、限时活动，制造时限紧迫感</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1721760000000008027e1b" target="_blank"><span class="ic-metric">88.0%</span><span class="ic-title">儿童节限定｜孩子王的儿童三色积木巧克力</span><span class="ic-hl">「儿童节限定+三色积木」场景+价值钩童心</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e882f000000002100b6b3" target="_blank"><span class="ic-metric">68.0%</span><span class="ic-title">夏日养生饮👏生姜泡腾片秒杀来咯</span><span class="ic-hl">「夏日养生+秒杀」时令+限时双钩</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📊 参数堆叠</div><div class="method-desc">低卡+无面粉+高蛋白等多卖点参数化，商品卡信息密度高</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a165e48000000003700c765" target="_blank"><span class="ic-metric">65.5%</span><span class="ic-title">信我！7r一箱，软乎乎的好好吃～</span><span class="ic-hl">「7元一箱+软乎乎」感官+超低价直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a22f0850000000022020e8d" target="_blank"><span class="ic-metric">77.5%</span><span class="ic-title">补贴后24块啊</span><span class="ic-hl">「补贴后24块」一句价格直给降决策成本</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🏆 稀缺/催促</div><div class="method-desc">「别停产」「催涨价」等稀缺感，触发囤货行为</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a212c610000000035021457" target="_blank"><span class="ic-metric">74.8%</span><span class="ic-title">感谢小红书 已售几万包的黑巧又回归啦❗️</span><span class="ic-hl">「售几万包+回归」销量背书+稀缺</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a226e8d00000000360328e5" target="_blank"><span class="ic-metric">67.3%</span><span class="ic-title">⚠️先给大家道个歉 我们又降价，6.9免邮200单</span><span class="ic-hl">「6.9免邮+200单」道歉式降价+限量钩</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">💊 对症解决方案</div><div class="method-desc">症状+产品=精准解决方案，商品卡承接感强</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a229b37000000000803d7d6" target="_blank"><span class="ic-metric">73.2%</span><span class="ic-title">盲盒2.0来啦！一单回本！送保温杯那种！</span><span class="ic-hl">「一单回本+送保温杯」赠品+性价比直钩</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d5bda0000000036001821" target="_blank"><span class="ic-metric">69.5%</span><span class="ic-title">再说一遍：下单就🉐，mini酱料碟太可爱了！</span><span class="ic-hl">「下单即得+mini酱料碟」赠品萌物钩</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div>'
CTR2_METHODS_V = '<div class="method-card-v2"><div class="method-title">🏷️ 价格直给</div><div class="method-desc">视频口播强调价格/活动，卡片价格曝光</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a20518e0000000037035de3" target="_blank"><span class="ic-metric">48.9%</span><span class="ic-title">有谁懂这种碎碎的牛胸口脆🥹又省钱又解馋❗️</span><span class="ic-hl">「碎碎牛胸口脆+省钱解馋」价格+口感对症</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2106100000000038035d5a" target="_blank"><span class="ic-metric">46.9%</span><span class="ic-title">不要错过建宁白莲66周年庆活动，优惠券超大</span><span class="ic-hl">「66周年+优惠券」周年大促+券面价值</span></a></div><div class="method-source">来源：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">👥 用户口碑/复购</div><div class="method-desc">老用户回购、真实好评，建立信任</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank"><span class="ic-metric">56.8%</span><span class="ic-title">又是每月一号福利，晚上八点直接左下方拍</span><span class="ic-hl">「每月一号福利+8点拍」固定时段限量钩</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1a952d000000003502723e" target="_blank"><span class="ic-metric">52.5%</span><span class="ic-title">面包控的周末早餐来了～🥯🥖</span><span class="ic-hl">「面包控+周末早餐」人群+场景对症</span></a></div><div class="method-source">来源：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 拟声/口感描述</div><div class="method-desc">感官卖点+视频场景还原（爆汁、剥皮、咀嚼）</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17fe9f000000000803d280" target="_blank"><span class="ic-metric">51.7%</span><span class="ic-title">都来吃这个佤味鸡脚筋！酸辣解馋巨上头！</span><span class="ic-hl">「佤味鸡脚筋+酸辣解馋」地域品类直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d46c30000000006032f23" target="_blank"><span class="ic-metric">50.7%</span><span class="ic-title">馒头超人×天友｜A2版绵云鲜奶上架</span><span class="ic-hl">「A2版绵云鲜奶+联名上架」联名+品牌新品</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">📦 具体配置/参数</div><div class="method-desc">告诉用户买到什么（几个/几折/什么规格），减少决策摩擦</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ea433000000002202901d" target="_blank"><span class="ic-metric">47.0%</span><span class="ic-title">整块的牛肋条好了，这个就是肥瘦牛肉粒</span><span class="ic-hl">「整块牛肋条+肥瘦牛肉粒」原料参数直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a24e34c000000001603dcfa" target="_blank"><span class="ic-metric">47.9%</span><span class="ic-title">5肥5瘦偏甜款香肠，马上可以正常售卖啦😊</span><span class="ic-hl">「5肥5瘦偏甜+正常售卖」参数+回归限时</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 场景代入</div><div class="method-desc">高原/出行/节日精准场景，用户代入感强</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a24fa6c00000000350313f1" target="_blank"><span class="ic-metric">48.7%</span><span class="ic-title">黑松露美食分享——【黑松露拌有机面】</span><span class="ic-hl">「黑松露+有机面」高级食材+做法直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a195b670000000007027b0b" target="_blank"><span class="ic-metric">47.2%</span><span class="ic-title">(无标题)</span><span class="ic-hl">无标题，仅封面承接，标题维度缺失</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div>'
CVR_METHODS_T  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">标题含具体人群词（备孕/减脂/宝妈），过滤无效流量</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1839f3000000003501f9f7" target="_blank"><span class="ic-metric">53.8%</span><span class="ic-title">奥利奥焦糖乳酪司康！！奥利奥脑袋一定会刷到</span><span class="ic-hl">「奥利奥脑袋必刷」精准人群锁定+组合品</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1c1f360000000036018db2" target="_blank"><span class="ic-metric">50.0%</span><span class="ic-title">见一个劝一个，一天三顿裤子小两码</span><span class="ic-hl">「劝一个+裤子小两码」效果背书+人群共鸣</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">💬 复购/口碑背书</div><div class="method-desc">「回购率头榜」「老粉催更」复购数据背书减决策疑虑</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1fc30f0000000035021170" target="_blank"><span class="ic-metric">56.2%</span><span class="ic-title">抹茶柚子乳酪贝果｜回购率头榜凭什么是它？</span><span class="ic-hl">「回购率头榜」复购数据背书减决策疑虑</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1fc24d000000003601a5bc" target="_blank"><span class="ic-metric">53.6%</span><span class="ic-title">新店开业，决定28r满满一大箱免邮500单试试！</span><span class="ic-hl">「28r一大箱+500单」新店试销稀缺方案</span></a></div><div class="method-source">来源：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🏢 品牌/渠道背书</div><div class="method-desc">山姆/奥莱/直营等强渠道信任背书，降低决策门槛</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1b9a8d00000000360197c1" target="_blank"><span class="ic-metric">45.1%</span><span class="ic-title">这份螺蛳粉代购，是我26岁的勇气</span><span class="ic-hl">「26岁勇气+代购」情感叙事+稀缺品</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2525a30000000008032ad9" target="_blank"><span class="ic-metric">40.4%</span><span class="ic-title">别问可以存多久，无添加鲜货不耐放🥐</span><span class="ic-hl">「无添加鲜货+不耐放」品质背书化解疑虑</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 打包/组合拼单</div><div class="method-desc">「一筐零食」「组合套装」降低单次决策成本</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a19734f0000000035023244" target="_blank"><span class="ic-metric">42.6%</span><span class="ic-title">跳操一个月…不然杏皮茶一周…我悟了</span><span class="ic-hl">「跳操vs杏皮茶」对比悟道，方案直给</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2273e0000000002100b7ba" target="_blank"><span class="ic-metric">40.4%</span><span class="ic-title">从“易燃易爆”到“算了算了”只差这个！</span><span class="ic-hl">「易燃易爆→算了算了」情绪方案钩夫妻人群</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">📊 具体解决方案</div><div class="method-desc">明确说「怎么用/效果是什么」，降低用户不确定性</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a26a488000000001602554a" target="_blank"><span class="ic-metric">39.3%</span><span class="ic-title">我妈吃了几口，立！刻！让我再买2单…</span><span class="ic-hl">「我妈再买2单」长辈背书强转化推力</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16640600000000060350da" target="_blank"><span class="ic-metric">38.0%</span><span class="ic-title">备考期间花得最值的一笔钱！！没有之一！！</span><span class="ic-hl">「备考最值」备考人群专属价值锚定</span></a></div><div class="method-source">来源：creation-guide-v9 D2</div></div>'
CVR_METHODS_V  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">视频明确目标人群，精准触达</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d645800000000070253c9" target="_blank"><span class="ic-metric">24.6%</span><span class="ic-title">🔥贵州蘸水菜🥬减脂期也能吃的下饭菜🤩</span><span class="ic-hl">「贵州蘸水菜+减脂下饭」地域+精准人群方案</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a166a900000000007029914" target="_blank"><span class="ic-metric">43.4%</span><span class="ic-title">管理期重新认识你了，45大卡的无油咖喱！</span><span class="ic-hl">「管理期+45大卡无油」精准减脂数据方案</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">⭐ 明星/达人同款</div><div class="method-desc">达人推荐+低价品类，强冲动+低决策成本</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16970a000000000602281a" target="_blank"><span class="ic-metric">31.0%</span><span class="ic-title">什么是NFC？何家劲带你认识真正的鲜榨枸杞</span><span class="ic-hl">「何家劲+NFC鲜榨」明星背书+真假科普</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a199a02000000003502ea04" target="_blank"><span class="ic-metric">50.0%</span><span class="ic-title">天才美食发明家！灵魂菜：苤菜根！</span><span class="ic-hl">「灵魂菜+苤菜根」地域稀缺品+发明家背书</span></a></div><div class="method-source">来源：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 解压/治愈场景</div><div class="method-desc">解压/沉浸打包等情绪价值场景，疗愈刚需</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e90990000000035027566" target="_blank"><span class="ic-metric">25.1%</span><span class="ic-title">口感暴击</span><span class="ic-hl">「口感暴击」一句感官钩，强冲动转化</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a211b1800000000060303d1" target="_blank"><span class="ic-metric">37.7%</span><span class="ic-title">夏天黏糊糊，姜茶冲鸡蛋是我妈的“祖传㊙️方”</span><span class="ic-hl">「我妈祖传㊙️方+姜茶」长辈背书+对症夏天</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">🏅 夸张赞美+稀缺</div><div class="method-desc">「灵魂菜」「天才发明」等夸张表达种草</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a27cb1d000000001702fc6d" target="_blank"><span class="ic-metric">35.9%</span><span class="ic-title">几十种全球奶酪自己选！赠品🎁已准备！</span><span class="ic-hl">「几十种全球奶酪+赠品」品类丰富+赠品推力</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17b8f2000000003501e98c" target="_blank"><span class="ic-metric">29.1%</span><span class="ic-title">2026年第一锅新花生，软糯鲜香甜</span><span class="ic-hl">「2026第一锅新花生」时令首发稀缺感</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 行动召唤</div><div class="method-desc">视频末尾「点购物车/评论区链接」明确行动指令</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16ab06000000003502d7e8" target="_blank"><span class="ic-metric">28.6%</span><span class="ic-title">宅家追剧的标配零食🍖又被我挖到好吃的</span><span class="ic-hl">「宅家追剧+标配零食」场景人群对症推荐</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a238cb3000000001503dffe" target="_blank"><span class="ic-metric">27.9%</span><span class="ic-title">我宣布！这个烤花生才是我的本命花生！</span><span class="ic-hl">「本命花生」个人强背书+味觉锚定</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div>'
PRICE_METHODS_T = '<div class="method-card-v2"><div class="method-title">🎁 礼盒/送礼场景</div><div class="method-desc">送礼/孝心/节日场景标题，客单价天然高</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1839f000000000060231ff" target="_blank"><span class="ic-metric">32491.8%</span><span class="ic-title">送领导的端午节礼盒🎁💰268被误以为上千块</span><span class="ic-hl">「268被误为上千」礼盒人情面子价感</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17be570000000006034d8a" target="_blank"><span class="ic-metric">37228.9%</span><span class="ic-title">端午礼｜端午且慢，守夏得安</span><span class="ic-hl">「端午礼+守夏得安」节令礼盒+祝语溢价</span></a></div><div class="method-source">来源：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">一级园/老藤/年份/批次等专业词，高客单品类自带高价</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a190e4a0000000007022072" target="_blank"><span class="ic-metric">43342.3%</span><span class="ic-title">产区二把手史低价，革命老区的爱！</span><span class="ic-hl">「产区二把手+史低价」产区专业词+稀缺</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ff305000000003502727e" target="_blank"><span class="ic-metric">41184.2%</span><span class="ic-title">世女一Sancerre正式开售‼️</span><span class="ic-hl">「世女一Sancerre正式开售」专业产区直给</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🏆 产地/限量</div><div class="method-desc">产地直发、限量款、联名款等稀缺属性拉价</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a21000f000000003601eaf7" target="_blank"><span class="ic-metric">24742.2%</span><span class="ic-title">总共300瓶！法国贵腐拍1发2！骗人是🐶</span><span class="ic-hl">「300瓶+法国贵腐拍1发2」产地稀缺+赠品</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d72220000000007013829" target="_blank"><span class="ic-metric">35999.9%</span><span class="ic-title">💚端午限定|山茶花手作杯+点心竹编篮</span><span class="ic-hl">「端午限定+山茶花+竹编篮」限定+手作高客单</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">📦 大份装/家庭装</div><div class="method-desc">全家装/囤货价/大份量，推高单笔购买量</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16c1540000000008027fbe" target="_blank"><span class="ic-metric">19287.8%</span><span class="ic-title">囤 30 杯咖啡液直接送小熊杯🥤</span><span class="ic-hl">「30杯咖啡液+送小熊杯」组合囤货抬客单</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a168dd40000000036032661" target="_blank"><span class="ic-metric">26851.2%</span><span class="ic-title">🎮M Stand × 小霸王｜咖啡就位 童心无穷</span><span class="ic-hl">「M Stand×小霸王」联名IP溢价钩童心</span></a></div><div class="method-source">来源：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">💎 高端/品质定位</div><div class="method-desc">强调品质/工艺/产地溯源，主动建立高价值感</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ed0a0000000002202b0a4" target="_blank"><span class="ic-metric">26734.1%</span><span class="ic-title">福禄安康端午礼盒 | 排队出发，倒计时</span><span class="ic-hl">「福禄安康端午礼盒+倒计时」节令稀缺礼盒</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17be4b0000000038035bf4" target="_blank"><span class="ic-metric">22939.2%</span><span class="ic-title">📣和老板商量后：忍痛给大家买一送一！</span><span class="ic-hl">「Patchi+买一送一」品牌背书+组合溢价</span></a></div><div class="method-source">来源：creation-guide-v9 D5</div></div>'
PRICE_METHODS_V = '<div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">老茶/扫地僧传人/百年老藤等专业黑话，圈层高客单</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank"><span class="ic-metric">140272.8%</span><span class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</span><span class="ic-hl">「05版博友301+七级砖」年份+批次专业术语</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ffd26000000002103fb70" target="_blank"><span class="ic-metric">28558.8%</span><span class="ic-title">夏天喝水不解渴？你缺了“津”液！</span><span class="ic-hl">「津液」中医专业术语提升价值感</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🏆 名酒/稀缺开箱</div><div class="method-desc">名酒开箱/限量批次/年份酒，实拍强背书</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1980580000000006030fea" target="_blank"><span class="ic-metric">19171.3%</span><span class="ic-title">两百余罐清仓即将收官！茉莉熟普的长跑</span><span class="ic-hl">「两百余罐+茉莉熟普长跑」限量+年份稀缺</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16e59e000000003501d804" target="_blank"><span class="ic-metric">24052.6%</span><span class="ic-title">终于知道为什么修行人会偏爱吃黄精了！</span><span class="ic-hl">「修行人+黄精」养生人群+稀缺食材溢价</span></a></div><div class="method-source">来源：三感六度</div></div><div class="method-card-v2"><div class="method-title">🎁 高价值场景叙事</div><div class="method-desc">婚庆/高端宴席/馈赠等场景，高价格有叙事撑腰</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e57f6000000003501fc91" target="_blank"><span class="ic-metric">24404.9%</span><span class="ic-title">浓浓茶香🍵米其林餐厅专供的乌龙康普茶‼️</span><span class="ic-hl">「米其林餐厅专供+乌龙康普茶」高端背书</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bd3c90000000036030cab" target="_blank"><span class="ic-metric">38481.4%</span><span class="ic-title">从上架到今天，真的不容易，感谢大家支持</span><span class="ic-hl">情感叙事溢价+老客回购拉客单</span></a></div><div class="method-source">来源：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">📊 价值数字化</div><div class="method-desc">均价超1000/一瓶抵多瓶等量化价值，建立高客单认知</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a23d3820000000022028d3a" target="_blank"><span class="ic-metric">26279.8%</span><span class="ic-title">端午礼 | 打包一份端午香盒～</span><span class="ic-hl">「端午香盒+打包」节令礼盒拉客单</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bc6a700000000350234bb" target="_blank"><span class="ic-metric">23184.2%</span><span class="ic-title">第一批端午曲奇做好啦🍃</span><span class="ic-hl">「第一批端午曲奇」节令首发+手作客单</span></a></div><div class="method-source">来源：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">🌍 产地/年份溯源</div><div class="method-desc">特定产区+年份，名庄/老茶直接定价锚点</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1904a1000000000702dce1" target="_blank"><span class="ic-metric">19814.1%</span><span class="ic-title">(无标题)</span><span class="ic-hl">无标题，仅靠封面承接，标题维度缺失</span></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17f77c000000003700eaac" target="_blank"><span class="ic-metric">18337.5%</span><span class="ic-title">给娃喝了三年的营养早餐，脾脾舒服吃饭香</span><span class="ic-hl">「三年早餐+脾脾舒服」长期使用+功效背书</span></a></div><div class="method-source">来源：诺亚 insight-v20</div></div>'

TAB_CTR1 = funnel_tab('ctr1', '👆', '提升 CTR1：封面+标题钩子', 'ctr1', CTR1_METHODS_T, CTR1_METHODS_V)
TAB_CTR2 = funnel_tab('ctr2', '🔗', '提升 CTR2：商品卡点击', 'ctr2', CTR2_METHODS_T, CTR2_METHODS_V)
TAB_CVR  = funnel_tab('cvr',  '💰', '提升 CVR：转化下单',      'cvr',  CVR_METHODS_T,  CVR_METHODS_V)
TAB_PRICE= funnel_tab('price','💎', '提升件单价：客单优化',     'price',PRICE_METHODS_T,PRICE_METHODS_V, is_price=True)


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
