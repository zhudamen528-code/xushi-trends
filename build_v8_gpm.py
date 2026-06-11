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
    <button class="tab-btn" onclick="switchTab(event,'cat')">🎁 卖点&策划助手</button>
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
      <div class="formula-tip">📍 <strong>GPM 是你笔记生意提升的核心</strong>：GPM 是商家自己 100% 可控的。GPM 提升不仅让每一份曝光能赚到的钱更多，平台也会把流量倾斜给 GPM 高的笔记——所以提升 GPM 是「单价 × 流量」双重增长。</div>
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

  <!-- V8f: 商家自查 GPM 工具 -->
  <div class="self-check-card">
    <div class="self-check-head">
      <strong>🔍 我的笔记 GPM 自查</strong>
      <span class="self-check-sub">从你后台笔记数据中填进来，一键定位最弱环节</span>
    </div>
    <div class="self-check-form">
      <div class="sc-row"><label>笔记形态</label>
        <div class="sc-form-radio">
          <button class="sc-btn active" data-form="图文" onclick="selfCheckForm(this,'图文')">📷 图文</button>
          <button class="sc-btn" data-form="视频" onclick="selfCheckForm(this,'视频')">🎬 视频</button>
        </div>
      </div>
      <div class="sc-grid">
        <div class="sc-input"><label>CTR1 (封面点击率, %)</label><input type="number" step="0.1" id="sc-ctr1" placeholder="例 8.5"></div>
        <div class="sc-input"><label>CTR2 (商品卡点击率, %)</label><input type="number" step="0.1" id="sc-ctr2" placeholder="例 30"></div>
        <div class="sc-input"><label>CVR (转化率, %)</label><input type="number" step="0.1" id="sc-cvr" placeholder="例 5"></div>
        <div class="sc-input"><label>件单价 (¥)</label><input type="number" step="1" id="sc-price" placeholder="例 40"></div>
      </div>
      <button class="sc-btn-go" onclick="runSelfCheck()">🔍 对照行业 · 找到我最弱环节</button>
      <div id="sc-result" style="display:none;margin-top:14px"></div>
    </div>
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

CTR1_METHODS_T = '<div class="method-card-v2"><div class="method-title">🎯 单主体+清晰特写</div><div class="method-desc">减少封面元素，让用户 1 秒看清&quot;是什么&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>产品大特写居中 / 手部操作场景 / 干净背景</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>产品名 + 1 个核心卖点（不超 15 字）</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a213d4600000000350283c3" target="_blank"><span class="ic-metric">28.1%</span><span class="ic-title">泪水不用打湿剪脂餐了</span><span class="ic-hl">「剪脂餐+泪水」情绪反差，戳减脂痛点</span><span class="ic-meta-row">咖皇旗舰店 · 曝光 52,389 · 下单 94</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1aa07900000000070210fa" target="_blank"><span class="ic-metric">27.1%</span><span class="ic-title">其实缺蛋白质的人都有一个明显共性。。。</span><span class="ic-hl">「缺蛋白质共性」悬念句，钩健身人群</span><span class="ic-meta-row">西域美农休闲零食旗舰店 · 曝光 59,421 · 下单 50</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 数字+反差词</div><div class="method-desc">用数字或反差词制造强钩子，吊起用户好奇</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>大字数字海报：100卡 / 9.9元 / 99%人不知道</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>公式：「具体数字 + 反差结果」如 &quot;90斤吃这个变 60 斤&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a214c980000000022026589" target="_blank"><span class="ic-metric">24.7%</span><span class="ic-title">我：有没有可能，它本来就是巧克力味呢❓❓❓❓</span><span class="ic-hl">反问句「本来就是」制造认知反差</span><span class="ic-meta-row">猿小姐的甜酒铺的店 · 曝光 130,379 · 下单 34</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2120ee0000000006031444" target="_blank"><span class="ic-metric">23.9%</span><span class="ic-title">瘦到90斤的同事每天吃的午饭</span><span class="ic-hl">「瘦到90斤+同事午饭」反差人群+窥探欲</span><span class="ic-meta-row">宁夏王小糊的店 · 曝光 72,595 · 下单 65</span></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开头</div><div class="method-desc">第一人称场景或人群词，让目标用户对号入座</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>真实使用场景照（书桌/早餐桌/办公室）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开头用&quot;我/打工人/宝妈/减脂期&quot;等身份词锁人群</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16b6930000000035038877" target="_blank"><span class="ic-metric">24.6%</span><span class="ic-title">🧋冷泡牛奶茶🧊测试完成！</span><span class="ic-hl">「冷泡牛奶茶+测试完成」实验感钩奶系人群</span><span class="ic-meta-row">抹茶猫贝果的店 · 曝光 70,228 · 下单 14</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1fe5620000000022020a60" target="_blank"><span class="ic-metric">24.3%</span><span class="ic-title">吃完外卖后，我就想喝这种清爽口</span><span class="ic-hl">「外卖后想喝清爽」场景代入饮品需求</span><span class="ic-meta-row">MikkoMeow的店 · 曝光 22,003 · 下单 13</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎭 拟声/趣味表达</div><div class="method-desc">感官词+趣味表达，封面+标题强内容味</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>夸张表情包 / 反差对比图 / 食物特写+滴落感</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>用拟声词（duangduang/咔嚓/嘎嘣）或网络梗</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1bd12a0000000007020a70" target="_blank"><span class="ic-metric">25.8%</span><span class="ic-title">一口沦陷！云朵牛乳也太温柔了☁️</span><span class="ic-hl">「云朵牛乳/温柔」拟态形容词诱食</span><span class="ic-meta-row">九峰牧场旗舰店 · 曝光 97,181 · 下单 75</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1eca8500000000350215a7" target="_blank"><span class="ic-metric">25.4%</span><span class="ic-title">现泡铂金黑咖啡！拧→摇→享3步搞定☕️  </span><span class="ic-hl">拧→摇→享三步钩，咖啡仪式感拆解</span><span class="ic-meta-row">小乐家零食的店 · 曝光 19,988 · 下单 12</span></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">👀 反向/悬念</div><div class="method-desc">自黑/留白/反转，引发好奇必点</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>只露局部不露全貌 / &quot;丑首图&quot;反向引流</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>问句结尾或卖关子：&quot;你猜这是？&quot; / &quot;都没人发现…&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1692c3000000003502cdca" target="_blank"><span class="ic-metric">22.4%</span><span class="ic-title">你抄袭的数量永远跟不上我玻璃壶的质量🤣🤣</span><span class="ic-hl">「抄袭/玻璃壶」吐槽体，悬念+人群猎奇</span><span class="ic-meta-row">茶冲鸭茶铺的店 · 曝光 30,443 · 下单 13</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e422f000000000701219e" target="_blank"><span class="ic-metric">21.9%</span><span class="ic-title">我们的南昌拌粉变短了</span><span class="ic-hl">「南昌拌粉变短」地域+变化制造悬念</span><span class="ic-meta-row">叽里咕噜碳水快乐的店 · 曝光 31,015 · 下单 30</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CTR1_METHODS_V = '<div class="method-card-v2"><div class="method-title">🎬 首帧强主体</div><div class="method-desc">视频前 0.5 秒就要看到主角</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>视频首帧 = 产品大特写或主角眼神特写</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>副标用动词：&quot;吃 / 试 / 测 / 开&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1abe150000000037035630" target="_blank"><span class="ic-metric">21.2%</span><span class="ic-title">同事吃了一口立马问我要烤鹅蛋🥚的链接</span><span class="ic-hl">「同事一口要链接」社交反应钩烤鹅蛋</span><span class="ic-meta-row">盈盈零食屋的店 · 曝光 84,898 · 下单 66</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2665930000000007024f37" target="_blank"><span class="ic-metric">18.0%</span><span class="ic-title">囤了不下10次…干巴酸奶真的好吃到惊为天人</span><span class="ic-hl">「囤10次+惊为天人」复购数字+情绪强钩</span><span class="ic-meta-row">瑞的零食坊的店 · 曝光 69,663 · 下单 44</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🔥 反差+数字钩子</div><div class="method-desc">前 3 秒抛出反差或具体数字</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面叠大字反差：&quot;谁能想到 5 块买到？&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>&quot;X天/X斤/X次&quot;类带数字的反差结果</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d642400000000350243e5" target="_blank"><span class="ic-metric">16.2%</span><span class="ic-title">减脂期狂喜😁挖到了解馋又健康的零食！！！</span><span class="ic-hl">「减脂期+狂喜」人群词+情绪反差</span><span class="ic-meta-row">小叶子的减脂日记的店 · 曝光 85,182 · 下单 59</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1a8dab00000000060218f0" target="_blank"><span class="ic-metric">16.0%</span><span class="ic-title">孕36周涨13斤，一篇说清我如何有效控制体重</span><span class="ic-hl">「孕36周涨13斤」精确数字+孕妈痛点共鸣</span><span class="ic-meta-row">小莹纸的店 · 曝光 20,325 · 下单 54</span></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div><div class="method-card-v2"><div class="method-title">💬 情绪共鸣开场</div><div class="method-desc">第一人称口播+情绪话术锁人群</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>主播个人特写表情（兴奋/惊讶/无奈）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开口直接喊人群：&quot;姐妹们&quot; / &quot;打工人&quot; / &quot;宝妈们&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2652400000000017029136" target="_blank"><span class="ic-metric">18.5%</span><span class="ic-title">我的料汁教程</span><span class="ic-hl">「料汁教程」实操干货钩做饭人群</span><span class="ic-meta-row">鲜参的店 · 曝光 36,313 · 下单 35</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a196aeb0000000035023fa1" target="_blank"><span class="ic-metric">16.7%</span><span class="ic-title">618大促</span><span class="ic-hl">「618大促」时令大促直钩，弱情绪</span><span class="ic-meta-row">恬康TIERKOND旗舰 · 曝光 82,106 · 下单 55</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">🎯 视频悬念口播</div><div class="method-desc">开头反问/报价/悬念锁停留</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面问号或大字悬念：&quot;这能吃吗？&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>开头反问句：&quot;你敢信这是 X 做的吗？&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a202132000000003503b363" target="_blank"><span class="ic-metric">16.7%</span><span class="ic-title">晚熟南高梅，还有两天就开始采摘啦</span><span class="ic-hl">「晚熟+采摘倒计时」鲜货时令悬念</span><span class="ic-meta-row">邑切梅好的店 · 曝光 24,443 · 下单 20</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e1350000000003503a97a" target="_blank"><span class="ic-metric">16.4%</span><span class="ic-title">姐姐！你的双眼皮贴是何意味呢！</span><span class="ic-hl">「双眼皮贴何意味」整活悬念钩猎奇</span><span class="ic-meta-row">F欣琳甄选的店 · 曝光 114,839 · 下单 59</span></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 地域/产地背书</div><div class="method-desc">产地词+地方梗，增强真实感</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>产地实景：田间/工厂/老店招牌</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题前缀地点：&quot;厦门&quot; / &quot;云南&quot; / &quot;潮汕&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e859c0000000035028c6a" target="_blank"><span class="ic-metric">20.3%</span><span class="ic-title">水煮菜可以退休了…</span><span class="ic-hl">「水煮菜退休」夸张拟人句钩减脂党</span><span class="ic-meta-row">咖皇旗舰店 · 曝光 11,567 · 下单 19</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a25485e000000001503e85e" target="_blank"><span class="ic-metric">19.8%</span><span class="ic-title">(无标题)</span><span class="ic-hl">无标题，仅靠封面承接，标题维度缺失</span><span class="ic-meta-row">藤椒的藤的店 · 曝光 20,748 · 下单 56</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CTR2_METHODS_T = '<div class="method-card-v2"><div class="method-title">🏷️ 价格直给</div><div class="method-desc">正文/商品卡直接亮价格，降低决策门槛</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带大字价格 &quot;9.9 元/件&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文第一段先报价 + 多少件买够</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e61e0000000003700e840" target="_blank"><span class="ic-metric">80.4%</span><span class="ic-title">🔥小红书专属羊毛！¥9.9到手100g精品咖啡豆</span><span class="ic-hl">「9.9元100g精品豆」价格+品类直给</span><span class="ic-meta-row">StellariaCaf · 曝光 5,656 · 下单 34</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1ba40c0000000007027bc1" target="_blank"><span class="ic-metric">68.8%</span><span class="ic-title">🧀12 元 / 盒！进口奶油奶酪准临期捡漏</span><span class="ic-hl">「12元/盒+准临期」价格+捡漏氛围</span><span class="ic-meta-row">理飨主义的店 · 曝光 9,215 · 下单 11</span></a></div><div class="method-source">参考：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">⏰ 节日/限时氛围</div><div class="method-desc">节气节日制造紧迫感</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带节日符号 / 倒计时元素</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文提及&quot;今日截止 / 仅 X 天 / 限时&quot; 等时效词</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1721760000000008027e1b" target="_blank"><span class="ic-metric">88.0%</span><span class="ic-title">儿童节限定｜孩子王的儿童三色积木巧克力</span><span class="ic-hl">「儿童节限定+三色积木」场景+价值钩童心</span><span class="ic-meta-row">NIBBO巧克力旗舰店 · 曝光 9,760 · 下单 31</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e882f000000002100b6b3" target="_blank"><span class="ic-metric">68.0%</span><span class="ic-title">夏日养生饮👏生姜泡腾片秒杀来咯</span><span class="ic-hl">「夏日养生+秒杀」时令+限时双钩</span><span class="ic-meta-row">直觉之食科技的店 · 曝光 12,746 · 下单 38</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📊 参数堆叠</div><div class="method-desc">一图说清&quot;几个卖点&quot;提升商品卡决策</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面/详情图：表格化罗列 5+ 参数</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文用 emoji 罗列：✅低卡 ✅无糖 ✅高蛋白</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a165e48000000003700c765" target="_blank"><span class="ic-metric">65.5%</span><span class="ic-title">信我！7r一箱，软乎乎的好好吃～</span><span class="ic-hl">「7元一箱+软乎乎」感官+超低价直给</span><span class="ic-meta-row">周三的情书 天气：小雨旗 · 曝光 28,646 · 下单 25</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a22f0850000000022020e8d" target="_blank"><span class="ic-metric">77.5%</span><span class="ic-title">补贴后24块啊</span><span class="ic-hl">「补贴后24块」一句价格直给降决策成本</span><span class="ic-meta-row">久抹的店 · 曝光 37,464 · 下单 20</span></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🏆 稀缺/催促</div><div class="method-desc">触发&quot;再不买就没了&quot;心智</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面写&quot;最后 X 件&quot; / &quot;停产倒计时&quot;</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题/正文用&quot;求别停产 / 仓库只剩 X 件&quot; 强稀缺词</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a212c610000000035021457" target="_blank"><span class="ic-metric">74.8%</span><span class="ic-title">感谢小红书 已售几万包的黑巧又回归啦❗️</span><span class="ic-hl">「售几万包+回归」销量背书+稀缺</span><span class="ic-meta-row">BENNS旗舰店 · 曝光 13,625 · 下单 16</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a226e8d00000000360328e5" target="_blank"><span class="ic-metric">67.3%</span><span class="ic-title">⚠️先给大家道个歉 我们又降价，6.9免邮200单</span><span class="ic-hl">「6.9免邮+200单」道歉式降价+限量钩</span><span class="ic-meta-row">小北吃遍潮汕的店 · 曝光 10,222 · 下单 26</span></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">💊 对症解决方案</div><div class="method-desc">把产品 = 用户问题的解药</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面问&quot;X 症状怎么办？&quot; → 答案是产品</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>正文用&quot;3 天见效 / 1 周改善&quot;等具体效果承诺</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a229b37000000000803d7d6" target="_blank"><span class="ic-metric">73.2%</span><span class="ic-title">盲盒2.0来啦！一单回本！送保温杯那种！</span><span class="ic-hl">「一单回本+送保温杯」赠品+性价比直钩</span><span class="ic-meta-row">四只猫咖啡旗舰店 · 曝光 23,151 · 下单 16</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d5bda0000000036001821" target="_blank"><span class="ic-metric">69.5%</span><span class="ic-title">再说一遍：下单就🉐，mini酱料碟太可爱了！</span><span class="ic-hl">「下单即得+mini酱料碟」赠品萌物钩</span><span class="ic-meta-row">有乐岛食品旗舰店 · 曝光 13,176 · 下单 13</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div>'
CTR2_METHODS_V = '<div class="method-card-v2"><div class="method-title">🏷️ 视频强报价</div><div class="method-desc">主播直接喊价格+活动</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面文案：大字价格 + 划线原价</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>视频前 5 秒口播：&quot;今天只要 X 元&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a20518e0000000037035de3" target="_blank"><span class="ic-metric">48.9%</span><span class="ic-title">有谁懂这种碎碎的牛胸口脆🥹又省钱又解馋❗️</span><span class="ic-hl">「碎碎牛胸口脆+省钱解馋」价格+口感对症</span><span class="ic-meta-row">爱吃牛胸口的小当家的店 · 曝光 18,399 · 下单 137</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2106100000000038035d5a" target="_blank"><span class="ic-metric">46.9%</span><span class="ic-title">不要错过建宁白莲66周年庆活动，优惠券超大</span><span class="ic-hl">「66周年+优惠券」周年大促+券面价值</span><span class="ic-meta-row">闽熙元菌菇的店 · 曝光 18,109 · 下单 19</span></a></div><div class="method-source">参考：creation-guide-v9 D8</div></div><div class="method-card-v2"><div class="method-title">👥 用户口碑/复购</div><div class="method-desc">老用户回购+真实好评</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面带&quot;老粉回购第 X 次&quot; / 客户截图</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>视频中插用户原话：&quot;朋友买了又来回购&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank"><span class="ic-metric">56.8%</span><span class="ic-title">又是每月一号福利，晚上八点直接左下方拍</span><span class="ic-hl">「每月一号福利+8点拍」固定时段限量钩</span><span class="ic-meta-row">小影的店 · 曝光 9,181 · 下单 21</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1a952d000000003502723e" target="_blank"><span class="ic-metric">52.5%</span><span class="ic-title">面包控的周末早餐来了～🥯🥖</span><span class="ic-hl">「面包控+周末早餐」人群+场景对症</span><span class="ic-meta-row">白房子咖啡的店 · 曝光 33,840 · 下单 71</span></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 感官+口感</div><div class="method-desc">拍出产品质感（爆汁/拉丝/酥脆）</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>慢镜头特写：切开瞬间/爆汁瞬间</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题用感官词：&quot;爆汁 / 拉丝 / 嘎嘣脆&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a17fe9f000000000803d280" target="_blank"><span class="ic-metric">51.7%</span><span class="ic-title">都来吃这个佤味鸡脚筋！酸辣解馋巨上头！</span><span class="ic-hl">「佤味鸡脚筋+酸辣解馋」地域品类直给</span><span class="ic-meta-row">好品食品的店 · 曝光 44,651 · 下单 69</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d46c30000000006032f23" target="_blank"><span class="ic-metric">50.7%</span><span class="ic-title">馒头超人×天友｜A2版绵云鲜奶上架</span><span class="ic-hl">「A2版绵云鲜奶+联名上架」联名+品牌新品</span><span class="ic-meta-row">馒头超人superman · 曝光 24,808 · 下单 21</span></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">📦 配置一图清</div><div class="method-desc">商品卡明确说&quot;买到几个/几折&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面或商品卡：「X 套装 = X 件」明列配置</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写明数量：&quot;5 件套 / 一年量装&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1ea433000000002202901d" target="_blank"><span class="ic-metric">47.0%</span><span class="ic-title">整块的牛肋条好了，这个就是肥瘦牛肉粒</span><span class="ic-hl">「整块牛肋条+肥瘦牛肉粒」原料参数直给</span><span class="ic-meta-row">通辽牛肉干(刚哥纯手工) · 曝光 15,330 · 下单 15</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a24e34c000000001603dcfa" target="_blank"><span class="ic-metric">47.9%</span><span class="ic-title">5肥5瘦偏甜款香肠，马上可以正常售卖啦😊</span><span class="ic-hl">「5肥5瘦偏甜+正常售卖」参数+回归限时</span><span class="ic-meta-row">安庆Aq小徐腊货的店 · 曝光 14,311 · 下单 15</span></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">🌍 场景代入</div><div class="method-desc">锁定特定使用场景</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-cover">📷 封面</span>封面用使用场景图（旅行/办公/聚餐）</div><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题挂场景：&quot;出差必备&quot; / &quot;高考刚需&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a24fa6c00000000350313f1" target="_blank"><span class="ic-metric">48.7%</span><span class="ic-title">黑松露美食分享——【黑松露拌有机面】</span><span class="ic-hl">「黑松露+有机面」高级食材+做法直给</span><span class="ic-meta-row">庆春朴门的店 · 曝光 19,890 · 下单 28</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a195b670000000007027b0b" target="_blank"><span class="ic-metric">47.2%</span><span class="ic-title">(无标题)</span><span class="ic-hl">无标题，仅封面承接，标题维度缺失</span><span class="ic-meta-row">纯米制果（无麸质）的店 · 曝光 5,943 · 下单 13</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div>'
CVR_METHODS_T  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">标题人群词 → 过滤无效流量</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1839f3000000003501f9f7" target="_blank"><span class="ic-metric">53.8%</span><span class="ic-title">奥利奥焦糖乳酪司康！！奥利奥脑袋一定会刷到</span><span class="ic-hl">「奥利奥脑袋必刷」精准人群锁定+组合品</span><span class="ic-meta-row">小麦司康的店 · 曝光 8,531 · 下单 57</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1c1f360000000036018db2" target="_blank"><span class="ic-metric">50.0%</span><span class="ic-title">见一个劝一个，一天三顿裤子小两码</span><span class="ic-hl">「劝一个+裤子小两码」效果背书+人群共鸣</span><span class="ic-meta-row">寻味日记的店 · 曝光 6,400 · 下单 65</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">💬 复购数据背书</div><div class="method-desc">亮&quot;回购率/老粉催更&quot;减疑虑</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1fc30f0000000035021170" target="_blank"><span class="ic-metric">56.2%</span><span class="ic-title">抹茶柚子乳酪贝果｜回购率头榜凭什么是它？</span><span class="ic-hl">「回购率头榜」复购数据背书减决策疑虑</span><span class="ic-meta-row">大麦糯叽叽的店 · 曝光 5,757 · 下单 36</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1fc24d000000003601a5bc" target="_blank"><span class="ic-metric">53.6%</span><span class="ic-title">新店开业，决定28r满满一大箱免邮500单试试！</span><span class="ic-hl">「28r一大箱+500单」新店试销稀缺方案</span><span class="ic-meta-row">书音离火烘焙工坊的店 · 曝光 2,243,394 · 下单 8,462</span></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🏢 品牌/渠道背书</div><div class="method-desc">山姆/奥莱/直营等强信任来源</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1b9a8d00000000360197c1" target="_blank"><span class="ic-metric">45.1%</span><span class="ic-title">这份螺蛳粉代购，是我26岁的勇气</span><span class="ic-hl">「26岁勇气+代购」情感叙事+稀缺品</span><span class="ic-meta-row">小海螺代GO螺蛳粉的店 · 曝光 18,223 · 下单 46</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2525a30000000008032ad9" target="_blank"><span class="ic-metric">40.4%</span><span class="ic-title">别问可以存多久，无添加鲜货不耐放🥐</span><span class="ic-hl">「无添加鲜货+不耐放」品质背书化解疑虑</span><span class="ic-meta-row">臻焙手作的店 · 曝光 11,239 · 下单 61</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 打包组合拼单</div><div class="method-desc">降低单次决策门槛</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a19734f0000000035023244" target="_blank"><span class="ic-metric">42.6%</span><span class="ic-title">跳操一个月…不然杏皮茶一周…我悟了</span><span class="ic-hl">「跳操vs杏皮茶」对比悟道，方案直给</span><span class="ic-meta-row">向往一杯的店 · 曝光 20,270 · 下单 23</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a2273e0000000002100b7ba" target="_blank"><span class="ic-metric">40.4%</span><span class="ic-title">从“易燃易爆”到“算了算了”只差这个！</span><span class="ic-hl">「易燃易爆→算了算了」情绪方案钩夫妻人群</span><span class="ic-meta-row">农夫山泉生活馆旗舰店 · 曝光 27,063 · 下单 23</span></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div><div class="method-card-v2"><div class="method-title">📊 解决方案明确</div><div class="method-desc">说清&quot;怎么用 / 效果是什么&quot;</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a26a488000000001602554a" target="_blank"><span class="ic-metric">39.3%</span><span class="ic-title">我妈吃了几口，立！刻！让我再买2单…</span><span class="ic-hl">「我妈再买2单」长辈背书强转化推力</span><span class="ic-meta-row">碱体大人的店 · 曝光 11,125 · 下单 59</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16640600000000060350da" target="_blank"><span class="ic-metric">38.0%</span><span class="ic-title">备考期间花得最值的一笔钱！！没有之一！！</span><span class="ic-hl">「备考最值」备考人群专属价值锚定</span><span class="ic-meta-row">启味林野零食小铺的店 · 曝光 28,160 · 下单 38</span></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div>'
CVR_METHODS_V  = '<div class="method-card-v2"><div class="method-title">🎯 精准人群锁定</div><div class="method-desc">视频明确目标人群</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d645800000000070253c9" target="_blank"><span class="ic-metric">24.6%</span><span class="ic-title">🔥贵州蘸水菜🥬减脂期也能吃的下饭菜🤩</span><span class="ic-hl">「贵州蘸水菜+减脂下饭」地域+精准人群方案</span><span class="ic-meta-row">仙马桥-辣椒面蘸料的店 · 曝光 24,510 · 下单 54</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a166a900000000007029914" target="_blank"><span class="ic-metric">43.4%</span><span class="ic-title">管理期重新认识你了，45大卡的无油咖喱！</span><span class="ic-hl">「管理期+45大卡无油」精准减脂数据方案</span><span class="ic-meta-row">咖皇旗舰店 · 曝光 28,560 · 下单 36</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div><div class="method-card-v2"><div class="method-title">⭐ 达人/明星同款</div><div class="method-desc">强冲动+低决策成本</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16970a000000000602281a" target="_blank"><span class="ic-metric">31.0%</span><span class="ic-title">什么是NFC？何家劲带你认识真正的鲜榨枸杞</span><span class="ic-hl">「何家劲+NFC鲜榨」明星背书+真假科普</span><span class="ic-meta-row">劲家庄食品旗舰店 · 曝光 9,974 · 下单 27</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a199a02000000003502ea04" target="_blank"><span class="ic-metric">50.0%</span><span class="ic-title">天才美食发明家！灵魂菜：苤菜根！</span><span class="ic-hl">「灵魂菜+苤菜根」地域稀缺品+发明家背书</span><span class="ic-meta-row">好品食品的店 · 曝光 11,774 · 下单 26</span></a></div><div class="method-source">参考：creation-guide-v9 D4</div></div><div class="method-card-v2"><div class="method-title">🎭 解压/治愈场景</div><div class="method-desc">情绪价值刚需</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e90990000000035027566" target="_blank"><span class="ic-metric">25.1%</span><span class="ic-title">口感暴击</span><span class="ic-hl">「口感暴击」一句感官钩，强冲动转化</span><span class="ic-meta-row">董饱饱手作工坊的店 · 曝光 30,458 · 下单 50</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a211b1800000000060303d1" target="_blank"><span class="ic-metric">37.7%</span><span class="ic-title">夏天黏糊糊，姜茶冲鸡蛋是我妈的“祖传㊙️方”</span><span class="ic-hl">「我妈祖传㊙️方+姜茶」长辈背书+对症夏天</span><span class="ic-meta-row">养瑞和旗舰店 · 曝光 54,132 · 下单 55</span></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">🏅 夸张赞美种草</div><div class="method-desc">&quot;灵魂菜 / 天才发明&quot; 类强主观推荐</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a27cb1d000000001702fc6d" target="_blank"><span class="ic-metric">35.9%</span><span class="ic-title">几十种全球奶酪自己选！赠品🎁已准备！</span><span class="ic-hl">「几十种全球奶酪+赠品」品类丰富+赠品推力</span><span class="ic-meta-row">奶酪猴子Cheese M · 曝光 5,403 · 下单 33</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a17b8f2000000003501e98c" target="_blank"><span class="ic-metric">29.1%</span><span class="ic-title">2026年第一锅新花生，软糯鲜香甜</span><span class="ic-hl">「2026第一锅新花生」时令首发稀缺感</span><span class="ic-meta-row">客家特产好事花生店的店 · 曝光 11,938 · 下单 16</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">📦 行动召唤</div><div class="method-desc">末尾明确&quot;点购物车&quot;指令</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16ab06000000003502d7e8" target="_blank"><span class="ic-metric">28.6%</span><span class="ic-title">宅家追剧的标配零食🍖又被我挖到好吃的</span><span class="ic-hl">「宅家追剧+标配零食」场景人群对症推荐</span><span class="ic-meta-row">陈阿炳食品旗舰店 · 曝光 10,904 · 下单 48</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a238cb3000000001503dffe" target="_blank"><span class="ic-metric">27.9%</span><span class="ic-title">我宣布！这个烤花生才是我的本命花生！</span><span class="ic-hl">「本命花生」个人强背书+味觉锚定</span><span class="ic-meta-row">仓鼠行动专卖店 · 曝光 44,226 · 下单 78</span></a></div><div class="method-source">参考：creation-guide-v9 D9</div></div>'
PRICE_METHODS_T = '<div class="method-card-v2"><div class="method-title">🎁 货品组合：套装/礼盒</div><div class="method-desc">【货品玩法】把多个 SKU 打成礼盒套装，自然提客单</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写&quot;X件套 / 礼盒装 / 一箱&quot;凸显数量</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1839f000000000060231ff" target="_blank"><span class="ic-metric">¥325</span><span class="ic-title">送领导的端午节礼盒🎁💰268被误以为上千块</span><span class="ic-hl">「268被误为上千」礼盒人情面子价感</span><span class="ic-meta-row">小婷婷滋补礼盒批发的店 · 曝光 17,850 · 下单 11</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a17be570000000006034d8a" target="_blank"><span class="ic-metric">¥372</span><span class="ic-title">端午礼｜端午且慢，守夏得安</span><span class="ic-hl">「端午礼+守夏得安」节令礼盒+祝语溢价</span><span class="ic-meta-row">瑭所旗舰店 · 曝光 47,736 · 下单 15</span></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">💰 货品玩法：多件多折</div><div class="method-desc">【货品玩法】「2件8折/3件7折」降低多买阻力</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题直接写&quot;2 件立减 X&quot; / &quot;买 3 送 1&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16c1540000000008027fbe" target="_blank"><span class="ic-metric">¥193</span><span class="ic-title">囤 30 杯咖啡液直接送小熊杯🥤</span><span class="ic-hl">「30杯咖啡液+送小熊杯」组合囤货抬客单</span><span class="ic-meta-row">星巴克家享咖啡旗舰店 · 曝光 76,105 · 下单 20</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a17be4b0000000038035bf4" target="_blank"><span class="ic-metric">¥229</span><span class="ic-title">📣和老板商量后：忍痛给大家买一送一！</span><span class="ic-hl">「Patchi+买一送一」品牌背书+组合溢价</span><span class="ic-meta-row">Patchi旗舰店 · 曝光 356,074 · 下单 84</span></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🎁 货品玩法：赠品机制</div><div class="method-desc">【货品玩法】&quot;满 X 送赠品&quot;提升下单意愿</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题挂赠品：&quot;下单送杯子 / 送试饮装&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a21000f000000003601eaf7" target="_blank"><span class="ic-metric">¥247</span><span class="ic-title">总共300瓶！法国贵腐拍1发2！骗人是🐶</span><span class="ic-hl">「300瓶+法国贵腐拍1发2」产地稀缺+赠品</span><span class="ic-meta-row">小草与酒的店 · 曝光 88,393 · 下单 41</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16b4100000000035020156" target="_blank"><span class="ic-metric">¥193</span><span class="ic-title">客定端午礼盒🍃满满心意</span><span class="ic-hl">「客定端午礼盒」定制节令拉客单</span><span class="ic-meta-row">木子烘焙|Muzi ca · 曝光 101,025 · 下单 63</span></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">一级园/老藤/年份/批次等专业词撑高价</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a190e4a0000000007022072" target="_blank"><span class="ic-metric">¥433</span><span class="ic-title">产区二把手史低价，革命老区的爱！</span><span class="ic-hl">「产区二把手+史低价」产区专业词+稀缺</span><span class="ic-meta-row">兔总的葡萄酒买手店的店 · 曝光 17,854 · 下单 17</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1ff305000000003502727e" target="_blank"><span class="ic-metric">¥412</span><span class="ic-title">世女一Sancerre正式开售‼️</span><span class="ic-hl">「世女一Sancerre正式开售」专业产区直给</span><span class="ic-meta-row">食葡专卖店 · 曝光 34,120 · 下单 12</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">💎 高端品质定位</div><div class="method-desc">强调品质/工艺/产地溯源</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1b96220000000007022908" target="_blank"><span class="ic-metric">¥202</span><span class="ic-title">才三盒...不想好的别用（虚胖</span><span class="ic-hl">「才三盒+虚胖」限量+老客调侃式抬价</span><span class="ic-meta-row">膳禾一方专卖店 · 曝光 71,010 · 下单 20</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1d72220000000007013829" target="_blank"><span class="ic-metric">¥360</span><span class="ic-title">💚端午限定|山茶花手作杯+点心竹编篮</span><span class="ic-hl">「端午限定+山茶花+竹编篮」限定+手作高客单</span><span class="ic-meta-row">白房子咖啡集合店的店 · 曝光 81,578 · 下单 46</span></a></div><div class="method-source">参考：creation-guide-v9 D5</div></div>'
PRICE_METHODS_V = '<div class="method-card-v2"><div class="method-title">🎁 货品组合：套装/礼盒</div><div class="method-desc">【货品玩法】视频展示套装组合的丰富度</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题写&quot;高端礼盒 / 婚宴套装&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a23d3820000000022028d3a" target="_blank"><span class="ic-metric">¥263</span><span class="ic-title">端午礼 | 打包一份端午香盒～</span><span class="ic-hl">「端午香盒+打包」节令礼盒拉客单</span><span class="ic-meta-row">白房子咖啡的店 · 曝光 33,715 · 下单 12</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank"><span class="ic-metric">¥1403</span><span class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</span><span class="ic-hl">「05版博友301+七级砖」年份+批次专业术语</span><span class="ic-meta-row">利佰年老茶馆的店 · 曝光 20,879 · 下单 14</span></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">💰 货品玩法：多件多折</div><div class="method-desc">【货品玩法】视频明确说&quot;2 件 X 元/箱装更划算&quot;</div><div class="method-tips"><div class="tip-line"><span class="tip-tag tip-title">✍️ 标题</span>标题&quot;整箱购 / 多件立省&quot;</div></div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1ea05a0000000008025c47" target="_blank"><span class="ic-metric">¥175</span><span class="ic-title">捡漏时刻✨朝日全开盖特价来袭，赶快囤</span><span class="ic-hl">「朝日全开盖特价+清仓」名酒清仓囤货价</span><span class="ic-meta-row">好水壹仟加的店 · 曝光 37,232 · 下单 10</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1bd3c90000000036030cab" target="_blank"><span class="ic-metric">¥385</span><span class="ic-title">从上架到今天，真的不容易，感谢大家支持</span><span class="ic-hl">情感叙事溢价+老客回购拉客单</span><span class="ic-meta-row">阿莹麦茶的店 · 曝光 51,684 · 下单 37</span></a></div><div class="method-source">参考：货品玩法</div></div><div class="method-card-v2"><div class="method-title">🍷 专业术语/藏家黑话</div><div class="method-desc">老茶/扫地僧传人/批次年份的圈层定价</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1ffd26000000002103fb70" target="_blank"><span class="ic-metric">¥286</span><span class="ic-title">夏天喝水不解渴？你缺了“津”液！</span><span class="ic-hl">「津液」中医专业术语提升价值感</span><span class="ic-meta-row">妈妈很忙旗舰店 · 曝光 8,834 · 下单 11</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1e57f6000000003501fc91" target="_blank"><span class="ic-metric">¥244</span><span class="ic-title">浓浓茶香🍵米其林餐厅专供的乌龙康普茶‼️</span><span class="ic-hl">「米其林餐厅专供+乌龙康普茶」高端背书</span><span class="ic-meta-row">酒類美術館Wine Ga · 曝光 28,598 · 下单 10</span></a></div><div class="method-source">参考：诺亚 insight-v20</div></div><div class="method-card-v2"><div class="method-title">🏆 名品开箱叙事</div><div class="method-desc">名酒名茶开箱+实拍背书</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1980580000000006030fea" target="_blank"><span class="ic-metric">¥192</span><span class="ic-title">两百余罐清仓即将收官！茉莉熟普的长跑</span><span class="ic-hl">「两百余罐+茉莉熟普长跑」限量+年份稀缺</span><span class="ic-meta-row">茶理十八的店 · 曝光 24,991 · 下单 15</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a16e59e000000003501d804" target="_blank"><span class="ic-metric">¥241</span><span class="ic-title">终于知道为什么修行人会偏爱吃黄精了！</span><span class="ic-hl">「修行人+黄精」养生人群+稀缺食材溢价</span><span class="ic-meta-row">小憩居的店 · 曝光 38,352 · 下单 23</span></a></div><div class="method-source">参考：三感六度</div></div><div class="method-card-v2"><div class="method-title">💎 价值数字化</div><div class="method-desc">&quot;均价超 X / 一瓶抵 N 瓶&quot; 建立高客单认知</div><div class="method-cases"><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1bce23000000000702a15d" target="_blank"><span class="ic-metric">¥179</span><span class="ic-title">这可能是最懂年轻人的一瓶酒</span><span class="ic-hl">「最懂年轻人的酒」人群定位拉品类溢价</span><span class="ic-meta-row">漩涡嘴里的店 · 曝光 462,244 · 下单 189</span></a><a class="inline-case inline-case-row" href="https://www.xiaohongshu.com/explore/6a1bc6a700000000350234bb" target="_blank"><span class="ic-metric">¥232</span><span class="ic-title">第一批端午曲奇做好啦🍃</span><span class="ic-hl">「第一批端午曲奇」节令首发+手作客单</span><span class="ic-meta-row">木子烘焙|Muzi ca · 曝光 25,403 · 下单 19</span></a></div><div class="method-source">参考：creation-guide-v9 D2</div></div>'

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
CAT_TAB = '<div class="tab-panel hidden" id="tab-cat">\n    <div class="section-label"><span class="icon">🎁</span> 卖点 & 内容策划助手 <span class="tag">填表格 → 一键生成完整 AI prompt → 复制到你的 AI 用</span></div>\n\n    <div class="ref-intro">\n      <strong>不需要你先想清楚卖点。</strong>填一下产品事实——原料、工艺、价格、买家说啥——一键生成 prompt，复制粘贴到豆包/Kimi/DeepSeek/ChatGPT 任一 AI 都能跑，AI 会推导你的核心卖点 + 出 S/A/B 三档笔记策略。<br>\n      <span style="font-size:12px;color:var(--text2)">填得越具体，输出越精准。「猪筒骨慢炖、炸响铃、9级辣」比「好吃、有特色」有用 10 倍。</span>\n    </div>\n\n    <div class="ref-form">\n      <div class="ref-form-title">描述你的产品（不需要提炼，说事实就行）</div>\n\n      <!-- ① 品类 -->\n      <div class="form-row">\n        <label class="form-label">① 品类 <span class="required">*</span></label>\n        <div style="display:flex;flex-wrap:wrap;gap:8px" id="ref-catL1Grid">\n          <button class="cat-l1-btn" data-cat="snack"   onclick="refSelectL1(this)">🍿 零食</button>\n          <button class="cat-l1-btn" data-cat="instant" onclick="refSelectL1(this)">🍜 速食</button>\n          <button class="cat-l1-btn" data-cat="drink"   onclick="refSelectL1(this)">🧋 饮品</button>\n          <button class="cat-l1-btn" data-cat="liquor"  onclick="refSelectL1(this)">🍷 酒类</button>\n          <button class="cat-l1-btn" data-cat="herb"    onclick="refSelectL1(this)">🌿 中式滋补</button>\n        </div>\n      </div>\n\n      <!-- ② 产品名 + 价格 -->\n      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">\n        <div class="form-row">\n          <label class="form-label">② 产品叫什么</label>\n          <input class="form-input" id="ref-spu" type="text" placeholder="例：满小饱肥汁米线 / 古法红糖姜茶">\n        </div>\n        <div class="form-row">\n          <label class="form-label">③ 售价（单包/单件）<span class="required">*</span></label>\n          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px" id="ref-priceBtns">\n            <button class="price-btn" data-price="9.9以下"  onclick="refSelectPrice(this)">¥9.9-</button>\n            <button class="price-btn" data-price="10-29元"  onclick="refSelectPrice(this)">¥10-29</button>\n            <button class="price-btn" data-price="30-59元"  onclick="refSelectPrice(this)">¥30-59</button>\n            <button class="price-btn" data-price="60-99元"  onclick="refSelectPrice(this)">¥60-99</button>\n            <button class="price-btn" data-price="100-199元" onclick="refSelectPrice(this)">¥100-199</button>\n            <button class="price-btn" data-price="200元以上" onclick="refSelectPrice(this)">¥200+</button>\n          </div>\n        </div>\n      </div>\n\n      <!-- ③ 原料/工艺 -->\n      <div class="form-row" style="margin-top:14px">\n        <label class="form-label">④ 原料或工艺是什么 <span class="required">*</span></label>\n        <input class="form-input" id="ref-ingredient" type="text" placeholder="例：猪筒骨慢炖肥汁、炸响铃、9级魔鬼椒 / 古法石磨 / 产地直发不过中间商 / 0添加防腐剂">\n        <div style="margin-top:5px;font-size:11px;color:var(--text2)">写具体的原料名、工艺名、认证/奖项，不要写「精选原料」「传统工艺」这类模糊词</div>\n      </div>\n\n      <!-- ④ 买家场合 -->\n      <div class="form-row" style="margin-top:14px">\n        <label class="form-label">⑤ 买家通常在什么场合买你的产品 <span class="required">*</span> <span style="font-size:11px;color:var(--text2)">可多选</span></label>\n        <div style="display:flex;flex-wrap:wrap;gap:8px" id="ref-audBtns">\n          <button class="aud-btn" data-aud="gift"     onclick="refToggleAud(this)">🎁 送礼/节日伴手礼</button>\n          <button class="aud-btn" data-aud="daily"    onclick="refToggleAud(this)">🧸 自己吃/日常囤货</button>\n          <button class="aud-btn" data-aud="kids"     onclick="refToggleAud(this)">👶 给孩子/宝妈选购</button>\n          <button class="aud-btn" data-aud="office"   onclick="refToggleAud(this)">💼 办公室茶歇/下午茶</button>\n          <button class="aud-btn" data-aud="diet"     onclick="refToggleAud(this)">🏋️ 减脂期/健身补充</button>\n          <button class="aud-btn" data-aud="elder"    onclick="refToggleAud(this)">🌸 送长辈/孝心礼</button>\n          <button class="aud-btn" data-aud="student"  onclick="refToggleAud(this)">📚 学生党/宿舍夜宵</button>\n          <button class="aud-btn" data-aud="midnight" onclick="refToggleAud(this)">🌙 深夜加班/追剧</button>\n          <button class="aud-btn" data-aud="outdoor"  onclick="refToggleAud(this)">🏕️ 户外/露营/运动</button>\n        </div>\n      </div>\n\n      <!-- ⑤ 买家评论 -->\n      <div class="form-row" style="margin-top:14px">\n        <label class="form-label">⑥ 买家最常说的话是什么 <span style="font-size:11px;color:var(--text2)">（直接粘贴 1-3 条真实评论，越真实越好）</span></label>\n        <textarea class="form-input" id="ref-review" rows="3" style="resize:vertical" placeholder="例：&#10;「这个汤底真的太香了，比外卖强多了」&#10;「每次焦虑的时候都会煮一碗，好治愈」&#10;「包装也太精致了，送朋友很有面子」"></textarea>\n        <div style="margin-top:5px;font-size:11px;color:var(--text2)">💡 这个字段最有价值——买家评论里直接藏着你的核心卖点和人群画像</div>\n      </div>\n\n      <!-- ⑥ 竞争和目标（可选） -->\n      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">\n        <div class="form-row">\n          <label class="form-label">⑦ 你觉得和同类产品最不一样的一点 <span style="font-size:11px;color:var(--text2)">（可不填，说不清楚也没关系）</span></label>\n          <input class="form-input" id="ref-diff" type="text" placeholder="例：我们家是手打的 / 配料比别人多 3 包 / 是同类里最辣的">\n        </div>\n        <div class="form-row">\n          <label class="form-label">⑧ 这次内容主要想解决什么</label>\n          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">\n            <button class="cat-l2-btn" data-goal="ctr"   onclick="refToggleGoal(this)">📈 提升点击率</button>\n            <button class="cat-l2-btn" data-goal="cvr"   onclick="refToggleGoal(this)">🛒 提升转化</button>\n            <button class="cat-l2-btn" data-goal="brand" onclick="refToggleGoal(this)">🏷️ 建立认知</button>\n            <button class="cat-l2-btn" data-goal="new"   onclick="refToggleGoal(this)">✨ 新品冷启动</button>\n            <button class="cat-l2-btn" data-goal="node"  onclick="refToggleGoal(this)">🗓️ 节点借势</button>\n          </div>\n        </div>\n      </div>\n\n      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px">\n        <button class="btn-gen-main btn-gen-doubao" onclick="generateRefAI()" id="genRefAIBtn" style="background:linear-gradient(90deg,#5b7cfa,#7c5bfa)">\n          🤖 直接用豆包生成结果\n        </button>\n        <button class="btn-gen-main" onclick="generateRefPrompt()" id="genRefBtn">\n          📋 复制 prompt 自己用\n        </button>\n      </div>\n      <div style="text-align:center;margin-top:10px;font-size:11px;color:#999">推荐左边：豆包直接出策略 · 失败可改用右边粘到 Kimi/ChatGPT</div>\n    </div>\n\n    <!-- 结果区 -->\n    <div id="ref-result-area" style="display:none;margin-top:24px">\n      <div class="section-label"><span class="icon">✨</span> 生成的 prompt <span class="tag" id="ref-result-meta"></span></div>\n      <div id="ref-result-loading" style="text-align:center;padding:40px;font-size:14px;color:var(--text2)">\n        <div style="font-size:28px;margin-bottom:12px">🤖</div>\n        生成 prompt 中…<br>\n        <span style="font-size:12px;color:var(--text3)">不到 1 秒</span>\n      </div>\n      <div id="ref-result-content" style="display:none"></div>\n      <div style="display:none;gap:10px;margin-top:20px" id="ref-result-actions">\n        <button class="btn-refresh" onclick="generateRefPrompt()">↻ 重新生成</button>\n        <button class="btn-copy-all" onclick="copyRefResult()">📋 再次复制 prompt</button>\n      </div>\n    </div>\n</div>\n'
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


/* === V8e 卖点助手 CSS ===*/
.ref-grid     { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
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
.ref-case {
  border: 1px solid var(--border);
  border-radius: var(--r10);
  padding: 12px 16px;
  margin: 8px 0;
  background: var(--bg2);
}
.ref-actions { display: flex; gap: 10px; margin-top: 16px; }
.ref-grid    { grid-template-columns: 1fr; }
.price-btn.active {
  background: var(--text);
  color: #fff;
  border-color: var(--text);
}
.aud-btn {
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
.aud-btn.active {
  background: var(--purple);
  color: #fff;
  border-color: var(--purple);
}
.form-row   { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.form-label { font-size: 13px; font-weight: 600; color: var(--text2); }
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
.required   { color: var(--red); }
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
.cat-l1-btn,.cat-l2-btn,.price-btn,.aud-btn{padding:6px 12px;border-radius:6px;border:1px solid #e0e0e0;background:#fafafa;color:#555;font-size:12px;cursor:pointer;transition:all .15s}
.cat-l1-btn:hover,.cat-l2-btn:hover,.price-btn:hover,.aud-btn:hover{border-color:#ff2442;color:#ff2442}
.cat-l1-btn.active,.cat-l2-btn.active,.price-btn.active,.aud-btn.active{background:#ff2442;color:white;border-color:#ff2442}
.ref-intro{padding:14px;background:#fff9f5;border-left:3px solid #ff6b35;border-radius:6px;margin-bottom:16px;font-size:13px;color:#555;line-height:1.6}
.ref-form{background:white;border:1px solid #eee;border-radius:10px;padding:18px}
.ref-form-title{font-size:14px;font-weight:600;color:#333;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #f0f0f0}
.form-row{display:flex;flex-direction:column}
.form-label{font-size:13px;color:#444;margin-bottom:6px;font-weight:500}
.form-input{padding:8px 12px;border:1px solid #ddd;border-radius:6px;font-size:13px;font-family:inherit}
.form-input:focus{outline:none;border-color:#ff2442}
.required{color:#ff2442}
.btn-gen-main{width:100%;margin-top:18px;padding:12px;background:linear-gradient(90deg,#ff2442,#ff6b35);color:white;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;transition:opacity .15s}
.btn-gen-main:hover{opacity:0.9}
.btn-gen-main:disabled{opacity:0.5;cursor:not-allowed}
.btn-refresh,.btn-copy-all{padding:8px 16px;border-radius:6px;border:1px solid #ff2442;background:white;color:#ff2442;cursor:pointer;font-size:13px}
.btn-refresh:hover,.btn-copy-all:hover{background:#fff0f0}
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


/* === V8f: GPM 自查工具 === */
.self-check-card { background:white; border:1px solid #eee; border-radius:12px; padding:18px; margin-top:18px; box-shadow:0 2px 6px rgba(255,36,66,0.05); }
.self-check-head { display:flex; flex-direction:column; gap:4px; margin-bottom:14px; }
.self-check-head strong { font-size:15px; color:#333; }
.self-check-sub { font-size:12px; color:#888; }
.sc-row { display:flex; align-items:center; gap:12px; margin-bottom:12px; }
.sc-row label { font-size:13px; color:#444; min-width:80px; }
.sc-form-radio { display:flex; gap:8px; }
.sc-btn { padding:6px 14px; border-radius:6px; border:1px solid #e0e0e0; background:white; cursor:pointer; font-size:13px; color:#555; }
.sc-btn:hover { border-color:#ff2442; color:#ff2442; }
.sc-btn.active { background:#ff2442; color:white; border-color:#ff2442; }
.sc-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:14px; }
.sc-input { display:flex; flex-direction:column; gap:4px; }
.sc-input label { font-size:11px; color:#666; }
.sc-input input { padding:8px 10px; border:1px solid #ddd; border-radius:6px; font-size:13px; font-family:inherit; }
.sc-input input:focus { outline:none; border-color:#ff2442; }
.sc-btn-go { width:100%; padding:11px; background:linear-gradient(90deg,#ff2442,#ff6b35); color:white; border:none; border-radius:8px; font-size:14px; font-weight:600; cursor:pointer; }
.sc-btn-go:hover { opacity:0.9; }
@media (max-width:768px) {
  .sc-grid { grid-template-columns:1fr 1fr; }
}


/* === V8g: 横向单行案例布局 === */
.inline-case-row { display: grid !important; grid-template-columns: 50px minmax(0,1.2fr) minmax(0,1.5fr) minmax(0,0.9fr); gap: 10px; align-items: center; padding: 8px 12px !important; min-height: 36px; }
.inline-case-row .ic-metric { display: inline-block; background: #ff2442; color: white; padding: 3px 6px; border-radius: 4px; font-size: 12px; font-weight: 600; text-align: center; }
.inline-case-row .ic-title { font-size: 13px; color: #333; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.inline-case-row .ic-hl { font-size: 12px; color: #888; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.inline-case-row .ic-meta-row { font-size: 11px; color: #bbb; text-align: right; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.method-card-v2 .method-cases { gap: 4px !important; }

/* 让方法卡里的案例占满宽度 */
.method-card-v2 { width: 100%; }
.methods-grid { display: grid; grid-template-columns: 1fr; gap: 14px; }

@media (max-width: 768px) {
  .inline-case-row { grid-template-columns: 44px 1fr; grid-template-rows: auto auto; }
  .inline-case-row .ic-hl { grid-column: 1 / -1; }
  .inline-case-row .ic-meta-row { grid-column: 1 / -1; text-align: left; }
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
print(f"tab-panel 数量：{n_panel}（预期 8）")
panel_ids = _re.findall(r'<div class="tab-panel[^"]*" id="tab-(\w+)"', v8)
print(f"panel ids: {panel_ids}")

# V8e: 注入卖点助手 JS
print('[V8e] 注入卖点助手 JS')
INJECT_JS = '// V8e Tab 卖点&内容策划助手 - 生成 prompt 模式（不调 AI API）\n// 用 window.* 命名空间避免和已有 window.v8e.cat 等冲突\nwindow.v8e = window.v8e || { cat: null, price: null, aud: [], goal: [] };\n\nfunction refSelectL1(btn) {\n  document.querySelectorAll(\'#ref-catL1Grid .cat-l1-btn\').forEach(b => b.classList.remove(\'active\'));\n  btn.classList.add(\'active\');\n  window.v8e.cat = btn.dataset.cat;\n}\n\nfunction refSelectPrice(btn) {\n  document.querySelectorAll(\'#ref-priceBtns .price-btn\').forEach(b => b.classList.remove(\'active\'));\n  btn.classList.add(\'active\');\n  window.v8e.price = btn.dataset.price;\n}\n\nfunction refToggleAud(btn) {\n  btn.classList.toggle(\'active\');\n  window.v8e.aud = Array.from(document.querySelectorAll(\'#ref-audBtns .aud-btn.active\')).map(b => b.dataset.aud);\n}\n\nfunction refToggleGoal(btn) {\n  btn.classList.toggle(\'active\');\n  window.v8e.goal = Array.from(document.querySelectorAll(\'#tab-cat .cat-l2-btn.active\')).map(b => b.dataset.goal);\n}\n\nfunction buildRefPromptText(p) {\n  const catName = { snack: \'零食\', instant: \'速食\', drink: \'饮品\', liquor: \'酒类\', herb: \'中式滋补\' }[p.cat] || p.cat;\n  const audMap = { gift: \'送礼/节日伴手礼\', daily: \'自己吃/日常囤货\', kids: \'给孩子/宝妈选购\', office: \'办公室茶歇/下午茶\', diet: \'减脂期/健身补充\', elder: \'送长辈/孝心礼\', student: \'学生党/宿舍夜宵\', midnight: \'深夜加班/追剧\', outdoor: \'户外/露营/运动\' };\n  const goalMap = { ctr: \'提升点击率\', cvr: \'提升转化率\', brand: \'建立认知\', new: \'新品冷启动\', node: \'节点借势\' };\n  const audText = p.aud.map(a => audMap[a] || a).join(\'、\') || \'未指定\';\n  const goalText = p.goal.map(g => goalMap[g] || g).join(\'、\') || \'未指定\';\n\n  return `# 任务：基于以下产品事实，帮我推导核心卖点 + 制定 S/A/B 三档小红书笔记策略\n\n## 产品信息\n- 品类：${catName}\n- 产品名：${p.spu || \'（未填，按品类通用打）\'}\n- 售价：${p.price}\n- 原料/工艺：${p.ingredient}\n- 主要购买场合：${audText}\n- 买家真实评论：${p.review || \'（暂无）\'}\n- 与同类差异点：${p.diff || \'（未填）\'}\n- 本次内容目标：${goalText}\n\n## 你的输出要求（请严格按此结构）\n\n### 一、卖点拆解（先帮我想清楚）\n基于「原料/工艺」「买家评论」「差异点」三个维度，告诉我：\n1. **真正的核心卖点**是什么？（不要重复产品描述，要挖出"为什么用户会买"的本质原因）\n2. **最精准的人群画像**是谁？（不要只说"年轻女性"，要说出具体场景+情绪）\n3. **可挑战的痛点**有哪些？（用户痛在哪里 → 我的产品如何解决）\n\n### 二、S/A/B 三档笔记策略\n基于上面的卖点+人群洞察，输出三档可直接执行的笔记策划：\n\n**S 档（重点笔记，押宝爆款）**\n- 标题（3 候选，每个 ≤22 字，必带 emoji）\n- 封面建议（主体+场景+反差点）\n- 正文结构（开头钩子 / 中段证据 / 结尾 CTA）\n- 商品卡文案（突出价格 + 核心卖点）\n- 预估表现：CTR1 / CTR2 / CVR 各档参考\n\n**A 档（日常铺量，跑稳量）**\n- 同上结构，更日常化\n\n**B 档（测试款，跑差异方向）**\n- 同上结构，刻意做反差/小众路径\n\n### 三、本周内容方向建议\n结合本周休食大盘趋势（数据由"GMV 总览" Tab 提供：图文 CTR1 优秀线 10.1% / CTR2 35.6% / CVR 6.2% / 件单价 ¥46；视频 CTR1 7.7% / CTR2 8.9% / CVR 7.7% / 件单价 ¥41），告诉我：\n- 这周哪种类型的笔记最容易跑出来？\n- 我的产品该重点做哪个漏斗环节？\n\n—— 请直接开始输出，不要复述上面的指令。`;\n}\n\nasync function generateRefPrompt() {\n  if (!window.v8e.cat) { alert(\'请选品类\'); return; }\n  if (!window.v8e.price) { alert(\'请选价格区间\'); return; }\n  const ingredient = (document.getElementById(\'ref-ingredient\').value || \'\').trim();\n  if (!ingredient) { alert(\'请填原料或工艺\'); return; }\n  if (window.v8e.aud.length === 0) { alert(\'至少选 1 个购买场合\'); return; }\n\n  const params = {\n    cat: window.v8e.cat,\n    price: window.v8e.price,\n    spu: (document.getElementById(\'ref-spu\').value || \'\').trim(),\n    ingredient: ingredient,\n    aud: window.v8e.aud,\n    review: (document.getElementById(\'ref-review\').value || \'\').trim(),\n    diff: (document.getElementById(\'ref-diff\').value || \'\').trim(),\n    goal: window.v8e.goal\n  };\n\n  const prompt = buildRefPromptText(params);\n  window._lastRefResult = prompt;\n\n  const area = document.getElementById(\'ref-result-area\');\n  const loading = document.getElementById(\'ref-result-loading\');\n  const content = document.getElementById(\'ref-result-content\');\n  const actions = document.getElementById(\'ref-result-actions\');\n  area.style.display = \'block\';\n  loading.style.display = \'none\';\n  content.style.display = \'block\';\n  content.innerHTML = `\n    <div style="background:#fff9e0;border:1px solid #ffe9b3;border-radius:8px;padding:12px;margin-bottom:14px;font-size:13px;color:#5d4a1f">\n      ✅ Prompt 已自动复制到剪贴板。粘到豆包/Kimi/DeepSeek/ChatGPT 任一 AI 都能跑，约 20 秒出结果。\n    </div>\n    <pre style="background:#f8f9fa;border:1px solid #e0e0e0;border-radius:8px;padding:16px;font-size:12px;line-height:1.65;white-space:pre-wrap;word-wrap:break-word;max-height:600px;overflow:auto;color:#333">${prompt.replace(/</g,\'&lt;\')}</pre>\n  `;\n  if (actions) actions.style.display = \'flex\';\n  area.scrollIntoView({ behavior: \'smooth\', block: \'start\' });\n\n  // 自动复制\n  try {\n    await navigator.clipboard.writeText(prompt);\n  } catch(e) {\n    console.warn(\'clipboard failed\', e);\n  }\n}\n\nfunction copyRefResult() {\n  if (!window._lastRefResult) return;\n  navigator.clipboard.writeText(window._lastRefResult).then(() => {\n    alert(\'✅ 已复制到剪贴板\');\n  }).catch(() => {\n    alert(\'复制失败，请手动选中文本复制\');\n  });\n}\n\n\n// 直接用豆包生成（前端 fetch，商家自己浏览器调）\nasync function generateRefAI() {\n  const cat = window.v8e.cat;\n  if (!cat) { alert(\'请先填表后再用\'); return; }\n  if (!window._lastRefResult) {\n    generateRefPrompt();\n    await new Promise(r => setTimeout(r, 200));\n  }\n  const prompt = window._lastRefResult;\n  if (!prompt) { alert(\'prompt 还没准备好\'); return; }\n\n  const area = document.getElementById(\'ref-result-area\');\n  const content = document.getElementById(\'ref-result-content\');\n  area.style.display = \'block\';\n  area.scrollIntoView({ behavior: \'smooth\', block: \'start\' });\n  content.innerHTML = \'<div style="padding:30px;text-align:center;font-size:14px;color:#666"><div style="font-size:32px;margin-bottom:10px">🤖</div>豆包生成中…大约 15-25 秒<br><span style="font-size:12px;color:#999">（如果失败可改为复制 prompt 粘到 Kimi/ChatGPT 用）</span></div>\';\n  content.style.display = \'block\';\n\n  try {\n    const resp = await fetch(\'https://ark.cn-beijing.volces.com/api/v3/chat/completions\', {\n      method: \'POST\',\n      headers: { \'Content-Type\': \'application/json\', \'Authorization\': \'Bearer \' + (window._ak || \'fcb33774-0143-492b-bd55-c95c01c60eb5\') },\n      body: JSON.stringify({\n        model: \'doubao-seed-2-0-lite-260215\',\n        messages: [\n          { role: \'system\', content: \'你是专业的小红书休食内容策划专家，按用户要求结构严格输出，不要加额外开场白。\' },\n          { role: \'user\', content: prompt }\n        ],\n        max_tokens: 3500,\n        temperature: 0.72\n      })\n    });\n    const data = await resp.json();\n    if (!data.choices) throw new Error(data.error ? data.error.message : \'API请求失败\');\n    const result = data.choices[0].message.content.trim();\n    // markdown 渲染（简化版）\n    const html = result\n      .replace(/&/g, \'&amp;\').replace(/</g, \'&lt;\').replace(/>/g, \'&gt;\')\n      .replace(/^### (.+)$/gm, \'<h3 style="font-size:15px;color:#ff2442;margin:18px 0 8px;border-left:3px solid #ff2442;padding-left:8px">$1</h3>\')\n      .replace(/^## (.+)$/gm, \'<h2 style="font-size:17px;color:#222;margin:22px 0 10px">$1</h2>\')\n      .replace(/\\*\\*(.+?)\\*\\*/g, \'<strong style="color:#ff2442">$1</strong>\')\n      .replace(/^- (.+)$/gm, \'<div style="margin:4px 0 4px 16px">• $1</div>\')\n      .replace(/\\n\\n/g, \'<br><br>\').replace(/\\n/g, \'<br>\');\n    content.innerHTML = \'<div style="background:#fff;border:1px solid #eee;border-radius:8px;padding:18px;font-size:13px;line-height:1.7;color:#333;max-height:700px;overflow:auto">\' + html + \'</div><div style="margin-top:10px;font-size:11px;color:#999;text-align:right">由豆包生成 · \' + new Date().toLocaleTimeString() + \'</div>\';\n    window._lastRefAIResult = result;\n  } catch(e) {\n    content.innerHTML = \'<div style="padding:20px;color:#c00;background:#fff5f5;border-radius:8px"><strong>❌ 豆包请求失败：</strong>\' + e.message + \'<br><br>💡 备用方案：点上方"📋 生成 prompt 并复制"，把 prompt 粘到 <a href="https://www.kimi.com" target="_blank">Kimi</a> 或 <a href="https://chat.deepseek.com" target="_blank">DeepSeek</a> 里用。</div>\';\n  }\n}\n\n\n// V8f: GPM 自查工具\nwindow.scForm = \'图文\';\nfunction selfCheckForm(btn, form) {\n  document.querySelectorAll(\'.sc-btn\').forEach(b => b.classList.remove(\'active\'));\n  btn.classList.add(\'active\');\n  window.scForm = form;\n}\nfunction runSelfCheck() {\n  const ctr1 = parseFloat(document.getElementById(\'sc-ctr1\').value);\n  const ctr2 = parseFloat(document.getElementById(\'sc-ctr2\').value);\n  const cvr = parseFloat(document.getElementById(\'sc-cvr\').value);\n  const price = parseFloat(document.getElementById(\'sc-price\').value);\n  if (isNaN(ctr1) || isNaN(ctr2) || isNaN(cvr) || isNaN(price)) {\n    alert(\'请把 4 个数据都填上\'); return;\n  }\n  // 行业 P75 优秀线\n  const benchmark = window.scForm === \'图文\'\n    ? { ctr1: 10.1, ctr2: 35.6, cvr: 6.2, price: 46 }\n    : { ctr1: 7.7,  ctr2: 8.9,  cvr: 7.7, price: 41 };\n  const labels = { ctr1: \'CTR1 封面点击\', ctr2: \'CTR2 商品卡\', cvr: \'CVR 转化\', price: \'件单价\' };\n  const tabMap = { ctr1: \'ctr1\', ctr2: \'ctr2\', cvr: \'cvr\', price: \'price\' };\n  const my = { ctr1, ctr2, cvr, price };\n  const gaps = [];\n  for (const k of [\'ctr1\',\'ctr2\',\'cvr\',\'price\']) {\n    const gap = (my[k] - benchmark[k]) / benchmark[k];\n    gaps.push({ key: k, label: labels[k], my: my[k], bench: benchmark[k], gap: gap });\n  }\n  gaps.sort((a, b) => a.gap - b.gap);\n  const worst = gaps[0];\n  const myGPM = (ctr1/100) * (ctr2/100) * (cvr/100) * price * 1000;\n  const benchGPM = (benchmark.ctr1/100) * (benchmark.ctr2/100) * (benchmark.cvr/100) * benchmark.price * 1000;\n  let html = `\n    <div style="background:#fff9e0;border:1px solid #ffe9b3;border-radius:8px;padding:14px;margin-bottom:12px">\n      <div style="font-size:14px;color:#5d4a1f">📊 你的笔记 GPM = <strong style="font-size:18px;color:#d84315">¥${myGPM.toFixed(2)}</strong> / 千次曝光</div>\n      <div style="font-size:12px;color:#8b6914;margin-top:4px">行业优秀线 GPM ≈ ¥${benchGPM.toFixed(2)} · 差距 ${((myGPM-benchGPM)/benchGPM*100).toFixed(0)}%</div>\n    </div>\n    <div style="font-size:13px;color:#666;margin-bottom:8px">📍 各环节对比（按落后程度排序）：</div>\n    <table style="width:100%;border-collapse:collapse;font-size:12px">\n      <thead><tr style="background:#f5f5f5"><th style="padding:8px;text-align:left">环节</th><th style="padding:8px;text-align:right">我</th><th style="padding:8px;text-align:right">行业优秀</th><th style="padding:8px;text-align:right">差距</th><th style="padding:8px;text-align:center">行动</th></tr></thead>\n      <tbody>`;\n  for (const g of gaps) {\n    const pct = (g.gap * 100).toFixed(0);\n    const color = g.gap < -0.2 ? \'#c00\' : (g.gap < 0 ? \'#ff6b35\' : \'#16a34a\');\n    const isWorst = g === worst;\n    html += `<tr style="${isWorst?\'background:#fff5f5\':\'\'}"><td style="padding:8px">${isWorst?\'🔴 \':\'\'}${g.label}</td><td style="padding:8px;text-align:right">${g.my}${g.key===\'price\'?\'\':\'%\'}</td><td style="padding:8px;text-align:right">${g.bench}${g.key===\'price\'?\'\':\'%\'}</td><td style="padding:8px;text-align:right;color:${color};font-weight:600">${pct>=0?\'+\':\'\'}${pct}%</td><td style="padding:8px;text-align:center"><a href="javascript:void(0)" onclick="document.querySelectorAll(\'.tab-btn\').forEach(b=>{if(b.getAttribute(\'onclick\').includes(\'${tabMap[g.key]}\'))b.click()});window.scrollTo({top:0,behavior:\'smooth\'})" style="color:#ff2442;text-decoration:none;font-size:11px">看方法 →</a></td></tr>`;\n  }\n  html += `</tbody></table>\n    <div style="margin-top:12px;padding:10px;background:#fff5f5;border-left:3px solid #ff2442;border-radius:4px;font-size:13px;color:#333">\n      💡 <strong>建议优先优化：${worst.label}</strong>（落后行业 ${(worst.gap*100).toFixed(0)}%），点击右边「看方法 →」直达对应 Tab。\n    </div>`;\n  const r = document.getElementById(\'sc-result\');\n  r.innerHTML = html;\n  r.style.display = \'block\';\n}\n\n// V8f: 案例点击 404 fallback（小红书有反爬，仅 toast 提示）\ndocument.addEventListener(\'click\', function(e){\n  const a = e.target.closest(\'a.inline-case\');\n  if (!a) return;\n  // 给个温和提示\n  setTimeout(() => {\n    // 跳转后无法检测 404，仅做"如何反馈死链"的提示\n  }, 0);\n});\n'
html = open('index.html').read()
if 'function generateRefPrompt' not in html:
    html = html.replace('</body>', '<script>\n' + INJECT_JS + '\n</script>\n</body>', 1)
    open('index.html','w').write(html)
    print('[V8e] JS injected, new size:', len(html))
else:
    print('[V8e] JS already present, skipping')

# V8f: header W21 → 动态时间窗
print('[V8f] header 时间窗动态化')
import json as _json
from datetime import date as _date
_html = open('index.html').read()
_data_f = _json.load(open('data.json'))
_win = _data_f.get('window', {})
if isinstance(_win, dict) and 'start_dtm' in _win and 'end_dtm' in _win:
    _start_f = _win['start_dtm']  # 20260527
    _end_f = _win['end_dtm']      # 20260609
    _ed = _date(int(_end_f[:4]), int(_end_f[4:6]), int(_end_f[6:8]))
    _wk = _ed.isocalendar()[1]
    _html = re.sub(r'<div class="header-week">[^<]*</div>', f'<div class="header-week">W{_wk}</div>', _html, count=1)
    _disp_start = f'{_start_f[4:6]}.{_start_f[6:8]}'
    _disp_end = f'{_end_f[4:6]}.{_end_f[6:8]}'
    _html = re.sub(r'<div class="header-date">[^<]*</div>', f'<div class="header-date">{_disp_start} — {_disp_end}</div>', _html, count=1)
    _html = re.sub(r'<div class="hero-week-badge">[^<]*</div>', f'<div class="hero-week-badge">第 {_wk} 周</div>', _html, count=1)
    open('index.html','w').write(_html)
    print(f'[V8f] header → W{_wk} · {_disp_start} - {_disp_end}')

