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
    <button class="tab-btn active" onclick="switchTab(event,'gpm')">💰 GMV 总览</button>
    <button class="tab-btn" onclick="switchTab(event,'ctr1')">👆 CTR1 封面+标题</button>
    <button class="tab-btn" onclick="switchTab(event,'ctr2')">🔗 CTR2 商品卡</button>
    <button class="tab-btn" onclick="switchTab(event,'cvr')">💵 CVR 转化</button>
    <button class="tab-btn" onclick="switchTab(event,'price')">💎 件单价</button>
    <button class="tab-btn" onclick="switchTab(event,'cat')">📦 品类风向</button>
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
    <h2>💰 GMV 总览 · 提升你的笔记生意</h2>
    <p class="meta">数据窗口：{data['window']['start_dtm'][:4]}-{data['window']['start_dtm'][4:6]}-{data['window']['start_dtm'][6:8]} 至 {data['window']['end_dtm'][:4]}-{data['window']['end_dtm'][4:6]}-{data['window']['end_dtm'][6:8]} · 笔记发布≥{data['window']['publish_min']} · 更新 {data['updated_at']}</p>
    <div class="funnel-formula">
      <div class="formula-line"><strong>笔记 GMV = GPM × 曝光（PV） ÷ 1000</strong></div>
      <div class="formula-line"><strong>GPM = CTR1 × CTR2 × CVR × 件单价 × 1000</strong></div>
      <div class="formula-flow">笔记曝光 → <span class="step ctr1">👆 封面点击</span> → <span class="step ctr2">🔗 商品卡点击</span> → <span class="step cvr">💵 下单</span> → <span class="step price">💎 客单价</span></div>
      <div class="formula-tip">📍 <strong>GPM 是你笔记生意提升的核心</strong>：曝光（PV）取决于平台分发，但 GPM 是商家自己 100% 可控的——只要 GPM 提升，每一份曝光能赚到的钱就更多。</div>
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
    数据基于近 14 天休食类目商品笔记的统计结果，每周一更新。
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

CTR1_METHODS_T = '<div class="method-card-v2"><div class="method-title">🎯 单主体+清晰特写</div><div class="method-desc">减少封面元素，让用户 1 秒看清&quot;是什么&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>产品大特写居中 / 手部操作场景 / 干净背景</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>产品名 + 1 个核心卖点（不超 15 字）</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a213d4600000000350283c3" target="_blank"><div class="ic-head"><span class="ic-metric">28.1%</span><span class="ic-seller">咖皇旗舰店</span></div><div class="ic-title">泪水不用打湿剪脂餐了</div><div class="ic-hl">「剪脂餐+泪水」情绪反差，戳减脂痛点</div><div class="ic-meta">曝光 52,389 · 下单 94 · 成交 ¥1882</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1aa07900000000070210fa" target="_blank"><div class="ic-head"><span class="ic-metric">27.1%</span><span class="ic-seller">西域美农休闲零食旗舰店</span></div><div class="ic-title">其实缺蛋白质的人都有一个明显共性。。。</div><div class="ic-hl">「缺蛋白质共性」悬念句，钩健身人群</div><div class="ic-meta">曝光 59,421 · 下单 50 · 成交 ¥1169</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 数字+反差词</div><div class="method-desc">用数字或反差词制造强钩子，吊起用户好奇</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>大字数字海报：100卡 / 9.9元 / 99%人不知道</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>公式：「具体数字 + 反差结果」如 &quot;90斤吃这个变 60 斤&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a214c980000000022026589" target="_blank"><div class="ic-head"><span class="ic-metric">24.7%</span><span class="ic-seller">猿小姐的甜酒铺的店</span></div><div class="ic-title">我：有没有可能，它本来就是巧克力味呢❓❓❓❓</div><div class="ic-hl">反问句「本来就是」制造认知反差</div><div class="ic-meta">曝光 130,379 · 下单 34 · 成交 ¥3241</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2120ee0000000006031444" target="_blank"><div class="ic-head"><span class="ic-metric">23.9%</span><span class="ic-seller">宁夏王小糊的店</span></div><div class="ic-title">瘦到90斤的同事每天吃的午饭</div><div class="ic-hl">「瘦到90斤+同事午饭」反差人群+窥探欲</div><div class="ic-meta">曝光 72,595 · 下单 65 · 成交 ¥892</div></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开头</div><div class="method-desc">第一人称场景或人群词，让目标用户对号入座</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>真实使用场景照（书桌/早餐桌/办公室）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开头用&quot;我/打工人/宝妈/减脂期&quot;等身份词锁人群</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16b6930000000035038877" target="_blank"><div class="ic-head"><span class="ic-metric">24.6%</span><span class="ic-seller">抹茶猫贝果的店</span></div><div class="ic-title">🧋冷泡牛奶茶🧊测试完成！</div><div class="ic-hl">「冷泡牛奶茶+测试完成」实验感钩奶系人群</div><div class="ic-meta">曝光 70,228 · 下单 14 · 成交 ¥449</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1fe5620000000022020a60" target="_blank"><div class="ic-head"><span class="ic-metric">24.3%</span><span class="ic-seller">MikkoMeow的店</span></div><div class="ic-title">吃完外卖后，我就想喝这种清爽口</div><div class="ic-hl">「外卖后想喝清爽」场景代入饮品需求</div><div class="ic-meta">曝光 22,003 · 下单 13 · 成交 ¥556</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎭 拟声/趣味表达</div><div class="method-desc">感官词+趣味表达，封面+标题强内容味</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>夸张表情包 / 反差对比图 / 食物特写+滴落感</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>用拟声词（duangduang/咔嚓/嘎嘣）或网络梗</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bd12a0000000007020a70" target="_blank"><div class="ic-head"><span class="ic-metric">25.8%</span><span class="ic-seller">九峰牧场旗舰店</span></div><div class="ic-title">一口沦陷！云朵牛乳也太温柔了☁️</div><div class="ic-hl">「云朵牛乳/温柔」拟态形容词诱食</div><div class="ic-meta">曝光 97,181 · 下单 75 · 成交 ¥3025</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1eca8500000000350215a7" target="_blank"><div class="ic-head"><span class="ic-metric">25.4%</span><span class="ic-seller">小乐家零食的店</span></div><div class="ic-title">现泡铂金黑咖啡！拧→摇→享3步搞定☕️  </div><div class="ic-hl">拧→摇→享三步钩，咖啡仪式感拆解</div><div class="ic-meta">曝光 19,988 · 下单 12 · 成交 ¥220</div></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">👀 反向/悬念</div><div class="method-desc">自黑/留白/反转，引发好奇必点</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>只露局部不露全貌 / &quot;丑首图&quot;反向引流</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>问句结尾或卖关子：&quot;你猜这是？&quot; / &quot;都没人发现…&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1692c3000000003502cdca" target="_blank"><div class="ic-head"><span class="ic-metric">22.4%</span><span class="ic-seller">茶冲鸭茶铺的店</span></div><div class="ic-title">你抄袭的数量永远跟不上我玻璃壶的质量🤣🤣</div><div class="ic-hl">「抄袭/玻璃壶」吐槽体，悬念+人群猎奇</div><div class="ic-meta">曝光 30,443 · 下单 13 · 成交 ¥256</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e422f000000000701219e" target="_blank"><div class="ic-head"><span class="ic-metric">21.9%</span><span class="ic-seller">叽里咕噜碳水快乐的店</span></div><div class="ic-title">我们的南昌拌粉变短了</div><div class="ic-hl">「南昌拌粉变短」地域+变化制造悬念</div><div class="ic-meta">曝光 31,015 · 下单 30 · 成交 ¥520</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CTR1_METHODS_V = '<div class="method-card-v2"><div class="method-title">🎬 首帧强主体</div><div class="method-desc">视频前 0.5 秒就要看到主角</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>视频首帧 = 产品大特写或主角眼神特写</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>副标用动词：&quot;吃 / 试 / 测 / 开&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1abe150000000037035630" target="_blank"><div class="ic-head"><span class="ic-metric">21.2%</span><span class="ic-seller">盈盈零食屋的店</span></div><div class="ic-title">同事吃了一口立马问我要烤鹅蛋🥚的链接</div><div class="ic-hl">「同事一口要链接」社交反应钩烤鹅蛋</div><div class="ic-meta">曝光 84,898 · 下单 66 · 成交 ¥1027</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2665930000000007024f37" target="_blank"><div class="ic-head"><span class="ic-metric">18.0%</span><span class="ic-seller">瑞的零食坊的店</span></div><div class="ic-title">囤了不下10次…干巴酸奶真的好吃到惊为天人</div><div class="ic-hl">「囤10次+惊为天人」复购数字+情绪强钩</div><div class="ic-meta">曝光 69,663 · 下单 44 · 成交 ¥823</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 反差+数字钩子</div><div class="method-desc">前 3 秒抛出反差或具体数字</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面叠大字反差：&quot;谁能想到 5 块买到？&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>&quot;X天/X斤/X次&quot;类带数字的反差结果</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d642400000000350243e5" target="_blank"><div class="ic-head"><span class="ic-metric">16.2%</span><span class="ic-seller">小叶子的减脂日记的店</span></div><div class="ic-title">减脂期狂喜😁挖到了解馋又健康的零食！！！</div><div class="ic-hl">「减脂期+狂喜」人群词+情绪反差</div><div class="ic-meta">曝光 85,182 · 下单 59 · 成交 ¥1021</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1a8dab00000000060218f0" target="_blank"><div class="ic-head"><span class="ic-metric">16.0%</span><span class="ic-seller">小莹纸的店</span></div><div class="ic-title">孕36周涨13斤，一篇说清我如何有效控制体重</div><div class="ic-hl">「孕36周涨13斤」精确数字+孕妈痛点共鸣</div><div class="ic-meta">曝光 20,325 · 下单 54 · 成交 ¥2208</div></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开场</div><div class="method-desc">第一人称口播+情绪话术锁人群</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>主播个人特写表情（兴奋/惊讶/无奈）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开口直接喊人群：&quot;姐妹们&quot; / &quot;打工人&quot; / &quot;宝妈们&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2652400000000017029136" target="_blank"><div class="ic-head"><span class="ic-metric">18.5%</span><span class="ic-seller">鲜参的店</span></div><div class="ic-title">我的料汁教程</div><div class="ic-hl">「料汁教程」实操干货钩做饭人群</div><div class="ic-meta">曝光 36,313 · 下单 35 · 成交 ¥2345</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a196aeb0000000035023fa1" target="_blank"><div class="ic-head"><span class="ic-metric">16.7%</span><span class="ic-seller">恬康TIERKOND旗舰店</span></div><div class="ic-title">618大促</div><div class="ic-hl">「618大促」时令大促直钩，弱情绪</div><div class="ic-meta">曝光 82,106 · 下单 55 · 成交 ¥1643</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎯 视频悬念口播</div><div class="method-desc">开头反问/报价/悬念锁停留</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面问号或大字悬念：&quot;这能吃吗？&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开头反问句：&quot;你敢信这是 X 做的吗？&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a202132000000003503b363" target="_blank"><div class="ic-head"><span class="ic-metric">16.7%</span><span class="ic-seller">邑切梅好的店</span></div><div class="ic-title">晚熟南高梅，还有两天就开始采摘啦</div><div class="ic-hl">「晚熟+采摘倒计时」鲜货时令悬念</div><div class="ic-meta">曝光 24,443 · 下单 20 · 成交 ¥1671</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e1350000000003503a97a" target="_blank"><div class="ic-head"><span class="ic-metric">16.4%</span><span class="ic-seller">F欣琳甄选的店</span></div><div class="ic-title">姐姐！你的双眼皮贴是何意味呢！</div><div class="ic-hl">「双眼皮贴何意味」整活悬念钩猎奇</div><div class="ic-meta">曝光 114,839 · 下单 59 · 成交 ¥687</div></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 地域/产地背书</div><div class="method-desc">产地词+地方梗，增强真实感</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>产地实景：田间/工厂/老店招牌</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题前缀地点：&quot;厦门&quot; / &quot;云南&quot; / &quot;潮汕&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e859c0000000035028c6a" target="_blank"><div class="ic-head"><span class="ic-metric">20.3%</span><span class="ic-seller">咖皇旗舰店</span></div><div class="ic-title">水煮菜可以退休了…</div><div class="ic-hl">「水煮菜退休」夸张拟人句钩减脂党</div><div class="ic-meta">曝光 11,567 · 下单 19 · 成交 ¥388</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a25485e000000001503e85e" target="_blank"><div class="ic-head"><span class="ic-metric">19.8%</span><span class="ic-seller">藤椒的藤的店</span></div><div class="ic-title">(无标题)</div><div class="ic-hl">无标题，仅靠封面承接，标题维度缺失</div><div class="ic-meta">曝光 20,748 · 下单 56 · 成交 ¥1766</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CTR2_METHODS_T = '<div class="method-card-v2"><div class="method-title">🏷️ 价格直给</div><div class="method-desc">正文/商品卡直接亮价格，降低决策门槛</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带大字价格 &quot;9.9 元/件&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文第一段先报价 + 多少件买够</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e61e0000000003700e840" target="_blank"><div class="ic-head"><span class="ic-metric">80.4%</span><span class="ic-seller">StellariaCafe的店</span></div><div class="ic-title">🔥小红书专属羊毛！¥9.9到手100g精品咖啡豆</div><div class="ic-hl">「9.9元100g精品豆」价格+品类直给</div><div class="ic-meta">曝光 5,656 · 下单 34 · 成交 ¥316</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ba40c0000000007027bc1" target="_blank"><div class="ic-head"><span class="ic-metric">68.8%</span><span class="ic-seller">理飨主义的店</span></div><div class="ic-title">🧀12 元 / 盒！进口奶油奶酪准临期捡漏</div><div class="ic-hl">「12元/盒+准临期」价格+捡漏氛围</div><div class="ic-meta">曝光 9,215 · 下单 11 · 成交 ¥359</div></a></div><div class="method-source">参考：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">⏰ 节日/限时氛围</div><div class="method-desc">节气节日制造紧迫感</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带节日符号 / 倒计时元素</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文提及&quot;今日截止 / 仅 X 天 / 限时&quot; 等时效词</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1721760000000008027e1b" target="_blank"><div class="ic-head"><span class="ic-metric">88.0%</span><span class="ic-seller">NIBBO巧克力旗舰店</span></div><div class="ic-title">儿童节限定｜孩子王的儿童三色积木巧克力</div><div class="ic-hl">「儿童节限定+三色积木」场景+价值钩童心</div><div class="ic-meta">曝光 9,760 · 下单 31 · 成交 ¥1853</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e882f000000002100b6b3" target="_blank"><div class="ic-head"><span class="ic-metric">68.0%</span><span class="ic-seller">直觉之食科技的店</span></div><div class="ic-title">夏日养生饮👏生姜泡腾片秒杀来咯</div><div class="ic-hl">「夏日养生+秒杀」时令+限时双钩</div><div class="ic-meta">曝光 12,746 · 下单 38 · 成交 ¥1050</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📊 参数堆叠</div><div class="method-desc">一图说清&quot;几个卖点&quot;提升商品卡决策</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面/详情图：表格化罗列 5+ 参数</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文用 emoji 罗列：✅低卡 ✅无糖 ✅高蛋白</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a165e48000000003700c765" target="_blank"><div class="ic-head"><span class="ic-metric">65.5%</span><span class="ic-seller">周三的情书 天气：小雨旗舰店</span></div><div class="ic-title">信我！7r一箱，软乎乎的好好吃～</div><div class="ic-hl">「7元一箱+软乎乎」感官+超低价直给</div><div class="ic-meta">曝光 28,646 · 下单 25 · 成交 ¥241</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a22f0850000000022020e8d" target="_blank"><div class="ic-head"><span class="ic-metric">77.5%</span><span class="ic-seller">久抹的店</span></div><div class="ic-title">补贴后24块啊</div><div class="ic-hl">「补贴后24块」一句价格直给降决策成本</div><div class="ic-meta">曝光 37,464 · 下单 20 · 成交 ¥1115</div></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🏆 稀缺/催促</div><div class="method-desc">触发&quot;再不买就没了&quot;心智</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面写&quot;最后 X 件&quot; / &quot;停产倒计时&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题/正文用&quot;求别停产 / 仓库只剩 X 件&quot; 强稀缺词</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a212c610000000035021457" target="_blank"><div class="ic-head"><span class="ic-metric">74.8%</span><span class="ic-seller">BENNS旗舰店</span></div><div class="ic-title">感谢小红书 已售几万包的黑巧又回归啦❗️</div><div class="ic-hl">「售几万包+回归」销量背书+稀缺</div><div class="ic-meta">曝光 13,625 · 下单 16 · 成交 ¥316</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a226e8d00000000360328e5" target="_blank"><div class="ic-head"><span class="ic-metric">67.3%</span><span class="ic-seller">小北吃遍潮汕的店</span></div><div class="ic-title">⚠️先给大家道个歉 我们又降价，6.9免邮200单</div><div class="ic-hl">「6.9免邮+200单」道歉式降价+限量钩</div><div class="ic-meta">曝光 10,222 · 下单 26 · 成交 ¥319</div></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">💊 对症解决方案</div><div class="method-desc">把产品 = 用户问题的解药</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面问&quot;X 症状怎么办？&quot; → 答案是产品</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文用&quot;3 天见效 / 1 周改善&quot;等具体效果承诺</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a229b37000000000803d7d6" target="_blank"><div class="ic-head"><span class="ic-metric">73.2%</span><span class="ic-seller">四只猫咖啡旗舰店</span></div><div class="ic-title">盲盒2.0来啦！一单回本！送保温杯那种！</div><div class="ic-hl">「一单回本+送保温杯」赠品+性价比直钩</div><div class="ic-meta">曝光 23,151 · 下单 16 · 成交 ¥485</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d5bda0000000036001821" target="_blank"><div class="ic-head"><span class="ic-metric">69.5%</span><span class="ic-seller">有乐岛食品旗舰店</span></div><div class="ic-title">再说一遍：下单就🉐，mini酱料碟太可爱了！</div><div class="ic-hl">「下单即得+mini酱料碟」赠品萌物钩</div><div class="ic-meta">曝光 13,176 · 下单 13 · 成交 ¥862</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div>'
CTR2_METHODS_V = '<div class="method-card-v2"><div class="method-title">🏷️ 视频强报价</div><div class="method-desc">主播直接喊价格+活动</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面文案：大字价格 + 划线原价</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>视频前 5 秒口播：&quot;今天只要 X 元&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a20518e0000000037035de3" target="_blank"><div class="ic-head"><span class="ic-metric">48.9%</span><span class="ic-seller">爱吃牛胸口的小当家的店</span></div><div class="ic-title">有谁懂这种碎碎的牛胸口脆🥹又省钱又解馋❗️</div><div class="ic-hl">「碎碎牛胸口脆+省钱解馋」价格+口感对症</div><div class="ic-meta">曝光 18,399 · 下单 137 · 成交 ¥7561</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2106100000000038035d5a" target="_blank"><div class="ic-head"><span class="ic-metric">46.9%</span><span class="ic-seller">闽熙元菌菇的店</span></div><div class="ic-title">不要错过建宁白莲66周年庆活动，优惠券超大</div><div class="ic-hl">「66周年+优惠券」周年大促+券面价值</div><div class="ic-meta">曝光 18,109 · 下单 19 · 成交 ¥895</div></a></div><div class="method-source">参考：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">👥 用户口碑/复购</div><div class="method-desc">老用户回购+真实好评</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带&quot;老粉回购第 X 次&quot; / 客户截图</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>视频中插用户原话：&quot;朋友买了又来回购&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank"><div class="ic-head"><span class="ic-metric">56.8%</span><span class="ic-seller">小影的店</span></div><div class="ic-title">又是每月一号福利，晚上八点直接左下方拍</div><div class="ic-hl">「每月一号福利+8点拍」固定时段限量钩</div><div class="ic-meta">曝光 9,181 · 下单 21 · 成交 ¥520</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1a952d000000003502723e" target="_blank"><div class="ic-head"><span class="ic-metric">52.5%</span><span class="ic-seller">白房子咖啡的店</span></div><div class="ic-title">面包控的周末早餐来了～🥯🥖</div><div class="ic-hl">「面包控+周末早餐」人群+场景对症</div><div class="ic-meta">曝光 33,840 · 下单 71 · 成交 ¥1958</div></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 感官+口感</div><div class="method-desc">拍出产品质感（爆汁/拉丝/酥脆）</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>慢镜头特写：切开瞬间/爆汁瞬间</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题用感官词：&quot;爆汁 / 拉丝 / 嘎嘣脆&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17fe9f000000000803d280" target="_blank"><div class="ic-head"><span class="ic-metric">51.7%</span><span class="ic-seller">好品食品的店</span></div><div class="ic-title">都来吃这个佤味鸡脚筋！酸辣解馋巨上头！</div><div class="ic-hl">「佤味鸡脚筋+酸辣解馋」地域品类直给</div><div class="ic-meta">曝光 44,651 · 下单 69 · 成交 ¥581</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d46c30000000006032f23" target="_blank"><div class="ic-head"><span class="ic-metric">50.7%</span><span class="ic-seller">馒头超人supermantou</span></div><div class="ic-title">馒头超人×天友｜A2版绵云鲜奶上架</div><div class="ic-hl">「A2版绵云鲜奶+联名上架」联名+品牌新品</div><div class="ic-meta">曝光 24,808 · 下单 21 · 成交 ¥495</div></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">📦 配置一图清</div><div class="method-desc">商品卡明确说&quot;买到几个/几折&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面或商品卡：「X 套装 = X 件」明列配置</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写明数量：&quot;5 件套 / 一年量装&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ea433000000002202901d" target="_blank"><div class="ic-head"><span class="ic-metric">47.0%</span><span class="ic-seller">通辽牛肉干(刚哥纯手工)的店</span></div><div class="ic-title">整块的牛肋条好了，这个就是肥瘦牛肉粒</div><div class="ic-hl">「整块牛肋条+肥瘦牛肉粒」原料参数直给</div><div class="ic-meta">曝光 15,330 · 下单 15 · 成交 ¥1006</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a24e34c000000001603dcfa" target="_blank"><div class="ic-head"><span class="ic-metric">47.9%</span><span class="ic-seller">安庆Aq小徐腊货的店</span></div><div class="ic-title">5肥5瘦偏甜款香肠，马上可以正常售卖啦😊</div><div class="ic-hl">「5肥5瘦偏甜+正常售卖」参数+回归限时</div><div class="ic-meta">曝光 14,311 · 下单 15 · 成交 ¥732</div></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 场景代入</div><div class="method-desc">锁定特定使用场景</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面用使用场景图（旅行/办公/聚餐）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题挂场景：&quot;出差必备&quot; / &quot;高考刚需&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a24fa6c00000000350313f1" target="_blank"><div class="ic-head"><span class="ic-metric">48.7%</span><span class="ic-seller">庆春朴门的店</span></div><div class="ic-title">黑松露美食分享——【黑松露拌有机面】</div><div class="ic-hl">「黑松露+有机面」高级食材+做法直给</div><div class="ic-meta">曝光 19,890 · 下单 28 · 成交 ¥4000</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a195b670000000007027b0b" target="_blank"><div class="ic-head"><span class="ic-metric">47.2%</span><span class="ic-seller">纯米制果（无麸质）的店</span></div><div class="ic-title">(无标题)</div><div class="ic-hl">无标题，仅封面承接，标题维度缺失</div><div class="ic-meta">曝光 5,943 · 下单 13 · 成交 ¥408</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CVR_METHODS_T  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">标题人群词 → 过滤无效流量</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1839f3000000003501f9f7" target="_blank"><div class="ic-head"><span class="ic-metric">53.8%</span><span class="ic-seller">小麦司康的店</span></div><div class="ic-title">奥利奥焦糖乳酪司康！！奥利奥脑袋一定会刷到</div><div class="ic-hl">「奥利奥脑袋必刷」精准人群锁定+组合品</div><div class="ic-meta">曝光 8,531 · 下单 57 · 成交 ¥359</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1c1f360000000036018db2" target="_blank"><div class="ic-head"><span class="ic-metric">50.0%</span><span class="ic-seller">寻味日记的店</span></div><div class="ic-title">见一个劝一个，一天三顿裤子小两码</div><div class="ic-hl">「劝一个+裤子小两码」效果背书+人群共鸣</div><div class="ic-meta">曝光 6,400 · 下单 65 · 成交 ¥390</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">💬 复购数据背书</div><div class="method-desc">亮&quot;回购率/老粉催更&quot;减疑虑</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1fc30f0000000035021170" target="_blank"><div class="ic-head"><span class="ic-metric">56.2%</span><span class="ic-seller">大麦糯叽叽的店</span></div><div class="ic-title">抹茶柚子乳酪贝果｜回购率头榜凭什么是它？</div><div class="ic-hl">「回购率头榜」复购数据背书减决策疑虑</div><div class="ic-meta">曝光 5,757 · 下单 36 · 成交 ¥260</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1fc24d000000003601a5bc" target="_blank"><div class="ic-head"><span class="ic-metric">53.6%</span><span class="ic-seller">书音离火烘焙工坊的店</span></div><div class="ic-title">新店开业，决定28r满满一大箱免邮500单试试！</div><div class="ic-hl">「28r一大箱+500单」新店试销稀缺方案</div><div class="ic-meta">曝光 2,243,394 · 下单 8,462 · 成交 ¥35952</div></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🏢 品牌/渠道背书</div><div class="method-desc">山姆/奥莱/直营等强信任来源</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1b9a8d00000000360197c1" target="_blank"><div class="ic-head"><span class="ic-metric">45.1%</span><span class="ic-seller">小海螺代GO螺蛳粉的店</span></div><div class="ic-title">这份螺蛳粉代购，是我26岁的勇气</div><div class="ic-hl">「26岁勇气+代购」情感叙事+稀缺品</div><div class="ic-meta">曝光 18,223 · 下单 46 · 成交 ¥863</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2525a30000000008032ad9" target="_blank"><div class="ic-head"><span class="ic-metric">40.4%</span><span class="ic-seller">臻焙手作的店</span></div><div class="ic-title">别问可以存多久，无添加鲜货不耐放🥐</div><div class="ic-hl">「无添加鲜货+不耐放」品质背书化解疑虑</div><div class="ic-meta">曝光 11,239 · 下单 61 · 成交 ¥263</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 打包组合拼单</div><div class="method-desc">降低单次决策门槛</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a19734f0000000035023244" target="_blank"><div class="ic-head"><span class="ic-metric">42.6%</span><span class="ic-seller">向往一杯的店</span></div><div class="ic-title">跳操一个月…不然杏皮茶一周…我悟了</div><div class="ic-hl">「跳操vs杏皮茶」对比悟道，方案直给</div><div class="ic-meta">曝光 20,270 · 下单 23 · 成交 ¥973</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2273e0000000002100b7ba" target="_blank"><div class="ic-head"><span class="ic-metric">40.4%</span><span class="ic-seller">农夫山泉生活馆旗舰店</span></div><div class="ic-title">从“易燃易爆”到“算了算了”只差这个！</div><div class="ic-hl">「易燃易爆→算了算了」情绪方案钩夫妻人群</div><div class="ic-meta">曝光 27,063 · 下单 23 · 成交 ¥998</div></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">📊 解决方案明确</div><div class="method-desc">说清&quot;怎么用 / 效果是什么&quot;</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a26a488000000001602554a" target="_blank"><div class="ic-head"><span class="ic-metric">39.3%</span><span class="ic-seller">碱体大人的店</span></div><div class="ic-title">我妈吃了几口，立！刻！让我再买2单…</div><div class="ic-hl">「我妈再买2单」长辈背书强转化推力</div><div class="ic-meta">曝光 11,125 · 下单 59 · 成交 ¥276</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16640600000000060350da" target="_blank"><div class="ic-head"><span class="ic-metric">38.0%</span><span class="ic-seller">启味林野零食小铺的店</span></div><div class="ic-title">备考期间花得最值的一笔钱！！没有之一！！</div><div class="ic-hl">「备考最值」备考人群专属价值锚定</div><div class="ic-meta">曝光 28,160 · 下单 38 · 成交 ¥999</div></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div>'
CVR_METHODS_V  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">视频明确目标人群</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d645800000000070253c9" target="_blank"><div class="ic-head"><span class="ic-metric">24.6%</span><span class="ic-seller">仙马桥-辣椒面蘸料的店</span></div><div class="ic-title">🔥贵州蘸水菜🥬减脂期也能吃的下饭菜🤩</div><div class="ic-hl">「贵州蘸水菜+减脂下饭」地域+精准人群方案</div><div class="ic-meta">曝光 24,510 · 下单 54 · 成交 ¥1105</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a166a900000000007029914" target="_blank"><div class="ic-head"><span class="ic-metric">43.4%</span><span class="ic-seller">咖皇旗舰店</span></div><div class="ic-title">管理期重新认识你了，45大卡的无油咖喱！</div><div class="ic-hl">「管理期+45大卡无油」精准减脂数据方案</div><div class="ic-meta">曝光 28,560 · 下单 36 · 成交 ¥669</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">⭐ 达人/明星同款</div><div class="method-desc">强冲动+低决策成本</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16970a000000000602281a" target="_blank"><div class="ic-head"><span class="ic-metric">31.0%</span><span class="ic-seller">劲家庄食品旗舰店</span></div><div class="ic-title">什么是NFC？何家劲带你认识真正的鲜榨枸杞</div><div class="ic-hl">「何家劲+NFC鲜榨」明星背书+真假科普</div><div class="ic-meta">曝光 9,974 · 下单 27 · 成交 ¥3871</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a199a02000000003502ea04" target="_blank"><div class="ic-head"><span class="ic-metric">50.0%</span><span class="ic-seller">好品食品的店</span></div><div class="ic-title">天才美食发明家！灵魂菜：苤菜根！</div><div class="ic-hl">「灵魂菜+苤菜根」地域稀缺品+发明家背书</div><div class="ic-meta">曝光 11,774 · 下单 26 · 成交 ¥268</div></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 解压/治愈场景</div><div class="method-desc">情绪价值刚需</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e90990000000035027566" target="_blank"><div class="ic-head"><span class="ic-metric">25.1%</span><span class="ic-seller">董饱饱手作工坊的店</span></div><div class="ic-title">口感暴击</div><div class="ic-hl">「口感暴击」一句感官钩，强冲动转化</div><div class="ic-meta">曝光 30,458 · 下单 50 · 成交 ¥686</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a211b1800000000060303d1" target="_blank"><div class="ic-head"><span class="ic-metric">37.7%</span><span class="ic-seller">养瑞和旗舰店</span></div><div class="ic-title">夏天黏糊糊，姜茶冲鸡蛋是我妈的“祖传㊙️方”</div><div class="ic-hl">「我妈祖传㊙️方+姜茶」长辈背书+对症夏天</div><div class="ic-meta">曝光 54,132 · 下单 55 · 成交 ¥4458</div></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">🏅 夸张赞美种草</div><div class="method-desc">&quot;灵魂菜 / 天才发明&quot; 类强主观推荐</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a27cb1d000000001702fc6d" target="_blank"><div class="ic-head"><span class="ic-metric">35.9%</span><span class="ic-seller">奶酪猴子Cheese Monk</span></div><div class="ic-title">几十种全球奶酪自己选！赠品🎁已准备！</div><div class="ic-hl">「几十种全球奶酪+赠品」品类丰富+赠品推力</div><div class="ic-meta">曝光 5,403 · 下单 33 · 成交 ¥365</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17b8f2000000003501e98c" target="_blank"><div class="ic-head"><span class="ic-metric">29.1%</span><span class="ic-seller">客家特产好事花生店的店</span></div><div class="ic-title">2026年第一锅新花生，软糯鲜香甜</div><div class="ic-hl">「2026第一锅新花生」时令首发稀缺感</div><div class="ic-meta">曝光 11,938 · 下单 16 · 成交 ¥419</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 行动召唤</div><div class="method-desc">末尾明确&quot;点购物车&quot;指令</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16ab06000000003502d7e8" target="_blank"><div class="ic-head"><span class="ic-metric">28.6%</span><span class="ic-seller">陈阿炳食品旗舰店</span></div><div class="ic-title">宅家追剧的标配零食🍖又被我挖到好吃的</div><div class="ic-hl">「宅家追剧+标配零食」场景人群对症推荐</div><div class="ic-meta">曝光 10,904 · 下单 48 · 成交 ¥1436</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a238cb3000000001503dffe" target="_blank"><div class="ic-head"><span class="ic-metric">27.9%</span><span class="ic-seller">仓鼠行动专卖店</span></div><div class="ic-title">我宣布！这个烤花生才是我的本命花生！</div><div class="ic-hl">「本命花生」个人强背书+味觉锚定</div><div class="ic-meta">曝光 44,226 · 下单 78 · 成交 ¥3282</div></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div>'
PRICE_METHODS_T = '<div class="method-card-v2"><div class="method-title">🎁 货品组合：套装/礼盒</div><div class="method-desc">【货品玩法】把多个 SKU 打成礼盒套装，自然提客单</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写&quot;X件套 / 礼盒装 / 一箱&quot;凸显数量</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1839f000000000060231ff" target="_blank"><div class="ic-head"><span class="ic-metric">¥325</span><span class="ic-seller">小婷婷滋补礼盒批发的店</span></div><div class="ic-title">送领导的端午节礼盒🎁💰268被误以为上千块</div><div class="ic-hl">「268被误为上千」礼盒人情面子价感</div><div class="ic-meta">曝光 17,850 · 下单 11 · 成交 ¥3574</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17be570000000006034d8a" target="_blank"><div class="ic-head"><span class="ic-metric">¥372</span><span class="ic-seller">瑭所旗舰店</span></div><div class="ic-title">端午礼｜端午且慢，守夏得安</div><div class="ic-hl">「端午礼+守夏得安」节令礼盒+祝语溢价</div><div class="ic-meta">曝光 47,736 · 下单 15 · 成交 ¥5584</div></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">💰 货品玩法：多件多折</div><div class="method-desc">【货品玩法】「2件8折/3件7折」降低多买阻力</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题直接写&quot;2 件立减 X&quot; / &quot;买 3 送 1&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16c1540000000008027fbe" target="_blank"><div class="ic-head"><span class="ic-metric">¥193</span><span class="ic-seller">星巴克家享咖啡旗舰店</span></div><div class="ic-title">囤 30 杯咖啡液直接送小熊杯🥤</div><div class="ic-hl">「30杯咖啡液+送小熊杯」组合囤货抬客单</div><div class="ic-meta">曝光 76,105 · 下单 20 · 成交 ¥3858</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a17be4b0000000038035bf4" target="_blank"><div class="ic-head"><span class="ic-metric">¥229</span><span class="ic-seller">Patchi旗舰店</span></div><div class="ic-title">📣和老板商量后：忍痛给大家买一送一！</div><div class="ic-hl">「Patchi+买一送一」品牌背书+组合溢价</div><div class="ic-meta">曝光 356,074 · 下单 84 · 成交 ¥19269</div></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🎁 货品玩法：赠品机制</div><div class="method-desc">【货品玩法】&quot;满 X 送赠品&quot;提升下单意愿</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题挂赠品：&quot;下单送杯子 / 送试饮装&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a21000f000000003601eaf7" target="_blank"><div class="ic-head"><span class="ic-metric">¥247</span><span class="ic-seller">小草与酒的店</span></div><div class="ic-title">总共300瓶！法国贵腐拍1发2！骗人是🐶</div><div class="ic-hl">「300瓶+法国贵腐拍1发2」产地稀缺+赠品</div><div class="ic-meta">曝光 88,393 · 下单 41 · 成交 ¥10144</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16b4100000000035020156" target="_blank"><div class="ic-head"><span class="ic-metric">¥193</span><span class="ic-seller">木子烘焙|Muzi cake的</span></div><div class="ic-title">客定端午礼盒🍃满满心意</div><div class="ic-hl">「客定端午礼盒」定制节令拉客单</div><div class="ic-meta">曝光 101,025 · 下单 63 · 成交 ¥12178</div></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">一级园/老藤/年份/批次等专业词撑高价</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a190e4a0000000007022072" target="_blank"><div class="ic-head"><span class="ic-metric">¥433</span><span class="ic-seller">兔总的葡萄酒买手店的店</span></div><div class="ic-title">产区二把手史低价，革命老区的爱！</div><div class="ic-hl">「产区二把手+史低价」产区专业词+稀缺</div><div class="ic-meta">曝光 17,854 · 下单 17 · 成交 ¥7368</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ff305000000003502727e" target="_blank"><div class="ic-head"><span class="ic-metric">¥412</span><span class="ic-seller">食葡专卖店</span></div><div class="ic-title">世女一Sancerre正式开售‼️</div><div class="ic-hl">「世女一Sancerre正式开售」专业产区直给</div><div class="ic-meta">曝光 34,120 · 下单 12 · 成交 ¥4942</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">💎 高端品质定位</div><div class="method-desc">强调品质/工艺/产地溯源</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1b96220000000007022908" target="_blank"><div class="ic-head"><span class="ic-metric">¥202</span><span class="ic-seller">膳禾一方专卖店</span></div><div class="ic-title">才三盒...不想好的别用（虚胖</div><div class="ic-hl">「才三盒+虚胖」限量+老客调侃式抬价</div><div class="ic-meta">曝光 71,010 · 下单 20 · 成交 ¥4043</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d72220000000007013829" target="_blank"><div class="ic-head"><span class="ic-metric">¥360</span><span class="ic-seller">白房子咖啡集合店的店</span></div><div class="ic-title">💚端午限定|山茶花手作杯+点心竹编篮</div><div class="ic-hl">「端午限定+山茶花+竹编篮」限定+手作高客单</div><div class="ic-meta">曝光 81,578 · 下单 46 · 成交 ¥16560</div></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div>'
PRICE_METHODS_V = '<div class="method-card-v2"><div class="method-title">🎁 货品组合：套装/礼盒</div><div class="method-desc">【货品玩法】视频展示套装组合的丰富度</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写&quot;高端礼盒 / 婚宴套装&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a23d3820000000022028d3a" target="_blank"><div class="ic-head"><span class="ic-metric">¥263</span><span class="ic-seller">白房子咖啡的店</span></div><div class="ic-title">端午礼 | 打包一份端午香盒～</div><div class="ic-hl">「端午香盒+打包」节令礼盒拉客单</div><div class="ic-meta">曝光 33,715 · 下单 12 · 成交 ¥3154</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank"><div class="ic-head"><span class="ic-metric">¥1403</span><span class="ic-seller">利佰年老茶馆的店</span></div><div class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</div><div class="ic-hl">「05版博友301+七级砖」年份+批次专业术语</div><div class="ic-meta">曝光 20,879 · 下单 14 · 成交 ¥19638</div></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">💰 货品玩法：多件多折</div><div class="method-desc">【货品玩法】视频明确说&quot;2 件 X 元/箱装更划算&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题&quot;整箱购 / 多件立省&quot;</div></div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ea05a0000000008025c47" target="_blank"><div class="ic-head"><span class="ic-metric">¥175</span><span class="ic-seller">好水壹仟加的店</span></div><div class="ic-title">捡漏时刻✨朝日全开盖特价来袭，赶快囤</div><div class="ic-hl">「朝日全开盖特价+清仓」名酒清仓囤货价</div><div class="ic-meta">曝光 37,232 · 下单 10 · 成交 ¥1753</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bd3c90000000036030cab" target="_blank"><div class="ic-head"><span class="ic-metric">¥385</span><span class="ic-seller">阿莹麦茶的店</span></div><div class="ic-title">从上架到今天，真的不容易，感谢大家支持</div><div class="ic-hl">情感叙事溢价+老客回购拉客单</div><div class="ic-meta">曝光 51,684 · 下单 37 · 成交 ¥14238</div></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">老茶/扫地僧传人/批次年份的圈层定价</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ffd26000000002103fb70" target="_blank"><div class="ic-head"><span class="ic-metric">¥286</span><span class="ic-seller">妈妈很忙旗舰店</span></div><div class="ic-title">夏天喝水不解渴？你缺了“津”液！</div><div class="ic-hl">「津液」中医专业术语提升价值感</div><div class="ic-meta">曝光 8,834 · 下单 11 · 成交 ¥3141</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1e57f6000000003501fc91" target="_blank"><div class="ic-head"><span class="ic-metric">¥244</span><span class="ic-seller">酒類美術館Wine Galle</span></div><div class="ic-title">浓浓茶香🍵米其林餐厅专供的乌龙康普茶‼️</div><div class="ic-hl">「米其林餐厅专供+乌龙康普茶」高端背书</div><div class="ic-meta">曝光 28,598 · 下单 10 · 成交 ¥2440</div></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🏆 名品开箱叙事</div><div class="method-desc">名酒名茶开箱+实拍背书</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1980580000000006030fea" target="_blank"><div class="ic-head"><span class="ic-metric">¥192</span><span class="ic-seller">茶理十八的店</span></div><div class="ic-title">两百余罐清仓即将收官！茉莉熟普的长跑</div><div class="ic-hl">「两百余罐+茉莉熟普长跑」限量+年份稀缺</div><div class="ic-meta">曝光 24,991 · 下单 15 · 成交 ¥2876</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16e59e000000003501d804" target="_blank"><div class="ic-head"><span class="ic-metric">¥241</span><span class="ic-seller">小憩居的店</span></div><div class="ic-title">终于知道为什么修行人会偏爱吃黄精了！</div><div class="ic-hl">「修行人+黄精」养生人群+稀缺食材溢价</div><div class="ic-meta">曝光 38,352 · 下单 23 · 成交 ¥5532</div></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">💎 价值数字化</div><div class="method-desc">&quot;均价超 X / 一瓶抵 N 瓶&quot; 建立高客单认知</div><div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bce23000000000702a15d" target="_blank"><div class="ic-head"><span class="ic-metric">¥179</span><span class="ic-seller">漩涡嘴里的店</span></div><div class="ic-title">这可能是最懂年轻人的一瓶酒</div><div class="ic-hl">「最懂年轻人的酒」人群定位拉品类溢价</div><div class="ic-meta">曝光 462,244 · 下单 189 · 成交 ¥33754</div></a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1bc6a700000000350234bb" target="_blank"><div class="ic-head"><span class="ic-metric">¥232</span><span class="ic-seller">木子烘焙|Muzi cake的</span></div><div class="ic-title">第一批端午曲奇做好啦🍃</div><div class="ic-hl">「第一批端午曲奇」节令首发+手作客单</div><div class="ic-meta">曝光 25,403 · 下单 19 · 成交 ¥4405</div></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div>'

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

# V8d: 品类风向 Tab
CAT_TAB = '<div class="tab-panel hidden" id="tab-cat">\n  <div class="hero hero-sub hero-cat">\n    <h2>📦 品类风向 · 5 大子品类内容方向</h2>\n    <p class="meta">休食 5 大子品类（零食 / 速食 / 饮品 / 茶酒 / 中式滋补）的内容方向参考，结合本周大盘趋势</p>\n  </div>\n  <div class="section-label">\n    <span class="icon">📦</span> 品类风向\n    <span class="tag">休食5大品类内容方向（参考，下版本会按周更新）</span>\n  </div>\n  <div class="cat-wrap">\n    <div class="cat-grid">\n\n      <div class="cat-card">\n        <div class="cat-head snack">🍿 零食</div>\n        <div class="cat-items">\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>「裸寄」反向吸睛持续爆量：卤味/糖果/果干多条同题 CTR 20~32%，最高曝光 83万+</span></div>\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>仅退款情绪共鸣：商家视角「什么都仅退款只会害了你」CTR 20~25%，曝光 6~70万</span></div>\n          <div class="cat-item"><span class="cat-dot">→</span><span>节日礼品/新口味冲量：迪拜曲奇/Apple礼包 CTR 20~25%，商卡转化 4~18%</span></div>\n        </div>\n        <div class="cat-focus">重点关注：裸寄/仅退款情绪共鸣 + 节日礼品场景</div>\n      </div>\n\n      <div class="cat-card">\n        <div class="cat-head fast">🍜 速食</div>\n        <div class="cat-items">\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>商家被抄/破防情绪：「刚创业还没靠XX赚钱就被抄袭」CTR 18~23%，曝光 16~23万</span></div>\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>价格性价比反差：「30r够吃两周，终结外卖焦虑」CTR 20%，商卡转化 15.7%</span></div>\n          <div class="cat-item"><span class="cat-dot">→</span><span>减脂低卡场景稳定：「能撑死人但热量很低」CTR 22.3%，商卡转化 16.5%</span></div>\n        </div>\n        <div class="cat-focus">重点关注：商家情绪叙事 + 外卖替代/性价比场景</div>\n      </div>\n\n      <div class="cat-card">\n        <div class="cat-head drink">🧋 饮品</div>\n        <div class="cat-items">\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>体型焦虑精准人群：「肚子这样再节食也没用」养生茶系列 CTR 19~25%，曝光 5~55万</span></div>\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>好奇疑问句高点击：「请问这杯是神吗？？？！」CTR 26.4%，曝光 7.4万，商卡 10.9%</span></div>\n          <div class="cat-item"><span class="cat-dot">→</span><span>生活场景轻松调性：普洱/乳制品日常趣味感 CTR 18~23%，商卡 5~8%</span></div>\n        </div>\n        <div class="cat-focus">重点关注：体型焦虑功效承诺 + 好奇疑问句式</div>\n      </div>\n\n      <div class="cat-card">\n        <div class="cat-head liquor">🍵 茶/酒</div>\n        <div class="cat-items">\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>好奇疑问句引爆点击：「请问这杯是神吗？？？！」花草茶 CTR 26.4%，曝光 7.4万，商卡 10.9%，悬念感极强</span></div>\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>普洱×生活轻松场景：「一个人出门兜里太轻了，请带上猫」CTR 23.6%，「6.0猫盒预告 仲夏夜之猫」CTR 24.7%，IP调性带动购买</span></div>\n          <div class="cat-item"><span class="cat-dot">→</span><span>体型焦虑+养生茶精准人群：「肚子这样再节食也没用」系列 CTR 19~25%，曝光 5~55万，精准人群即转化</span></div>\n        </div>\n        <div class="cat-focus">重点关注：好奇疑问句式 + 体型焦虑功效场景</div>\n      </div>\n\n      <div class="cat-card">\n        <div class="cat-head herb">🌿 中式滋补</div>\n        <div class="cat-items">\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>长辈/专家权威背书：「93岁老先生推荐！坚持吃了一个月好舒服」CTR 23.8%，权威人物背书是最稳定信任公式</span></div>\n          <div class="cat-item"><span class="cat-dot up">↑</span><span>亚健康摆脱功效：「黄精吃吧！成功摆脱了班味」CTR 24.7%；「如果你的肚子也是这样，再节食也没用」CTR 19~25%，痛点精准触达</span></div>\n          <div class="cat-item"><span class="cat-dot">→</span><span>母亲节礼品场景：「50+的妈妈想要什么礼物」阿胶膏方 CTR 22.6%，节日礼赠+中老年人群，是5月主力内容方向</span></div>\n        </div>\n        <div class="cat-focus">重点关注：长辈背书信任 + 母亲节礼品场景</div>\n      </div>\n\n    </div>\n  </div>\n  <div class="tips-box" style="margin-top:20px">\n    <strong>💡 怎么用：</strong> 找到你的产品所在品类，看本周该品类的"重点关注"方向，参考 ↑ 上升趋势的内容形式仿写。\n  </div>\n</div>'


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
all_panels = '\n'.join([TAB1, TAB_CTR1, TAB_CTR2, TAB_CVR, TAB_PRICE, CAT_TAB, TAB_AUDIT, TAB_TOOLS])
if '<div class="main-content">' in v8:
    v8 = v8.replace('<div class="main-content">', '<div class="main-content">\n' + all_panels, 1)
elif '</main>' in v8:
    v8 = v8.replace('</main>', all_panels + '\n</main>', 1)
else:
    v8 = v8.replace('</body>', all_panels + '\n</body>', 1)

# 4. 注入 GPM 专用 CSS（追加到现有 <style> 内）
GPM_CSS = '''

/* === V8d 内联方法论+案例 === */
.method-card-v2 { background:white; border:1px solid #eee; border-left:3px solid #ff2442; border-radius:10px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.method-card-v2 .method-title { font-weight:600; color:#333; font-size:15px; margin-bottom:6px; }
.method-card-v2 .method-desc { font-size:13px; color:#666; line-height:1.5; margin-bottom:10px; }
.method-tips { background:#fffbf0; border:1px solid #ffe9b3; border-radius:6px; padding:8px 10px; margin-bottom:10px; }
.method-tips .tip-line { font-size:12px; color:#5d4a1f; line-height:1.6; }
.method-tips .tip-line + .tip-line { margin-top:4px; }
.method-tips .tip-tag { display:inline-block; padding:1px 6px; border-radius:3px; font-size:11px; margin-right:6px; font-weight:600; }
.method-tips .tip-cover { background:#fff3e0; color:#e65100; }
.method-tips .tip-title { background:#e3f2fd; color:#1565c0; }
.method-card-v2 .method-cases { display:flex; flex-direction:column; gap:8px; margin-bottom:8px; }
.method-card-v2 .method-source { font-size:11px; color:#bbb; margin-top:6px; }
.inline-case { display:block; background:#fafafa; border-radius:6px; padding:10px 12px; text-decoration:none; border:1px solid #f0f0f0; transition:all .15s; }
.inline-case:hover { background:#fff0f0; border-color:#ffcdd2; transform:translateX(2px); }
.ic-head { display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap; }
.ic-metric { display:inline-block; background:#ff2442; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.ic-seller { font-size:11px; color:#999; }
.ic-title { font-size:13px; color:#333; font-weight:500; margin-bottom:3px; line-height:1.4; }
.ic-hl { font-size:11px; color:#666; line-height:1.4; margin-bottom:4px; }
.ic-meta { font-size:10px; color:#bbb; }

/* === V8d Hero+公式增强 === */
.funnel-formula .formula-line { padding:6px 0; }
.funnel-formula .formula-flow { padding:8px 0; }
.funnel-formula .formula-tip { background:#fff9e0; border-left:3px solid #ffb300; padding:8px 12px; margin-top:8px; border-radius:4px; font-size:13px; color:#5d4a1f; line-height:1.6; }

/* === V8d 手机端适配 === */
@media (max-width: 768px) {
  .methods-grid { grid-template-columns: 1fr !important; }
  .kpi-grid-2col { grid-template-columns: 1fr !important; }
  .method-tips .tip-line { font-size:11px; }
  .ic-title { font-size:12px; }
  .funnel-formula .formula-line strong { font-size:13px; }
}
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


/* === V8d 品类风向 === */
.cat-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.cat-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      min-width: 700px;
    }
.cat-card {
      background: var(--card-bg);
      border-radius: 14px;
      padding: 18px 16px;
      border: 1px solid var(--border);
      transition: border-color 0.2s;
    }
.cat-head {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 12px;
      padding: 8px 12px;
      border-radius: 8px;
      color: #fff;
    }
.cat-name {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 2px solid #f5f0eb;
    }
.cat-items { display: flex; flex-direction: column; gap: 8px; }
.cat-item {
      font-size: 12px;
      color: #94a3b8;
      line-height: 1.5;
      display: flex;
      gap: 6px;
      align-items: flex-start;
    }
.cat-dot { font-weight: 700; font-size: 13px; flex-shrink: 0; margin-top: 1px; }
.cat-dot      { color: #999; }
.cat-focus {
      margin-top: 12px;
      padding: 8px 10px;
      background: rgba(99,102,241,0.08);
      border: 1px solid rgba(99,102,241,0.2);
      border-radius: 8px;
      font-size: 11px;
      font-weight: 600;
      color: #818cf8;
    }
.cat-grid { grid-template-columns: repeat(2, 1fr); min-width: unset; }
.cat-wrap {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x mandatory;
        padding-bottom: 8px;
      }
.cat-grid {
        grid-template-columns: repeat(5, 80vw);
        min-width: unset;
      }
.cat-card {
        scroll-snap-align: start;
      }
.cat-select-group {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
.cat-radio { cursor: pointer; }
.hero-cat { background: linear-gradient(135deg,#e8f5e9,#f1f8e9); }
.hero-cat h2 { color: #2e7d32; }

/* V8d cat-grid 覆盖：响应式纵向布局 */
#tab-cat .cat-wrap { overflow: visible !important; }
#tab-cat .cat-grid { 
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) !important;
  gap: 14px !important;
  min-width: 0 !important;
}
#tab-cat .cat-card { 
  min-width: 0 !important;
  max-width: none !important;
  width: 100% !important;
  background: white;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #eee;
}
#tab-cat .cat-head { font-size:15px; font-weight:600; margin-bottom:8px; padding:4px 8px; border-radius:4px; }
#tab-cat .cat-head.snack { background:#fff3e0; color:#e65100; }
#tab-cat .cat-head.fast { background:#fff9c4; color:#827717; }
#tab-cat .cat-head.drink { background:#e3f2fd; color:#1565c0; }
#tab-cat .cat-head.liquor { background:#e8f5e9; color:#2e7d32; }
#tab-cat .cat-head.herb { background:#fce4ec; color:#ad1457; }
#tab-cat .cat-items { display:flex; flex-direction:column; gap:6px; margin-bottom:10px; }
#tab-cat .cat-item { display:flex; gap:6px; font-size:12px; color:#555; line-height:1.5; align-items:flex-start; }
#tab-cat .cat-dot { color:#999; font-weight:600; flex-shrink:0; }
#tab-cat .cat-dot.up { color:#ff2442; }
#tab-cat .cat-focus { font-size:11px; color:#1565c0; background:#e3f2fd; padding:6px 10px; border-radius:4px; }
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
print(f"tab-panel 数量：{n_panel}（预期 8）")
panel_ids = _re.findall(r'<div class="tab-panel[^"]*" id="tab-(\w+)"', v8)
print(f"panel ids: {panel_ids}")
