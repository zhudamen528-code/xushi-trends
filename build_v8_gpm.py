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
    <p class="meta">数据窗口：{data['window'][0]} 至 {data['window'][1]} · 更新 {data['updated_at']}</p>
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

CTR1_METHODS_T = '<div class="method-card-v2">\n      <div class="method-title">📸 单主体+特写</div>\n      <div class="method-desc">封面只放一个主体（产品/手部动作），剔除杂乱背景</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a250f1f00000000360001a9" target="_blank">\n      <span class="ic-metric">57.1%</span>\n      <span class="ic-title">白茶草庐 | 橱窗非我意，但愿草庐宁</span>\n      <span class="ic-hl">反消费宣言+诗意短句，戳中反内卷情绪</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a007953000000003503bdd1" target="_blank">\n      <span class="ic-metric">43.5%</span>\n      <span class="ic-title">遇到裸寄了。。。。</span>\n      <span class="ic-hl">&quot;裸寄&quot;悬念词，制造拆包翻车好奇</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🔥 数字+反差词</div>\n      <div class="method-desc">标题用数字钩子或反差词（如「100卡」「裸寄」「自黑」），吊起好奇</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a007953000000003503bdd1" target="_blank">\n      <span class="ic-metric">43.5%</span>\n      <span class="ic-title">遇到裸寄了。。。。</span>\n      <span class="ic-hl">&quot;裸寄&quot;悬念词，制造拆包翻车好奇</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6916959000000000070095be" target="_blank">\n      <span class="ic-metric">36.1%</span>\n      <span class="ic-title">这张首图，丑是真的丑啊</span>\n      <span class="ic-hl">自黑&quot;丑首图&quot;反向引流，反差吸睛</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D2</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">💬 情绪共鸣开头</div>\n      <div class="method-desc">「打工人续命」「自律必吃」等第一人称场景，精准锁人群</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69a13cd3000000002801fb30" target="_blank">\n      <span class="ic-metric">34.9%</span>\n      <span class="ic-title">我一自律期就吃这个</span>\n      <span class="ic-hl">第一人称自律场景，精准锁瘦身人群</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a250f1f00000000360001a9" target="_blank">\n      <span class="ic-metric">57.1%</span>\n      <span class="ic-title">白茶草庐 | 橱窗非我意，但愿草庐宁</span>\n      <span class="ic-hl">反消费宣言+诗意短句，戳中反内卷情绪</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🎭 拟声/趣味词</div>\n      <div class="method-desc">「duangduang」「裸寄了」等趣味表达，内容味极强</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/68d0afd6000000001201e46c" target="_blank">\n      <span class="ic-metric">34.5%</span>\n      <span class="ic-title">现在才顿悟！哄男人还得用跳跳糖…</span>\n      <span class="ic-hl">情趣联想+跳跳糖反差，话题感拉满</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6916959000000000070095be" target="_blank">\n      <span class="ic-metric">36.1%</span>\n      <span class="ic-title">这张首图，丑是真的丑啊</span>\n      <span class="ic-hl">自黑&quot;丑首图&quot;反向引流，反差吸睛</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">👀 反向/制造悬念</div>\n      <div class="method-desc">自黑标题、神秘感留白、意外反转，用户不点不甘心</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a007953000000003503bdd1" target="_blank">\n      <span class="ic-metric">43.5%</span>\n      <span class="ic-title">遇到裸寄了。。。。</span>\n      <span class="ic-hl">&quot;裸寄&quot;悬念词，制造拆包翻车好奇</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69eb11820000000022025f46" target="_blank">\n      <span class="ic-metric">34.7%</span>\n      <span class="ic-title">(无标题)</span>\n      <span class="ic-hl">无标题反靠封面留白，神秘感引点击</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div>'
CTR1_METHODS_V = '<div class="method-card-v2">\n      <div class="method-title">📸 单主体+特写</div>\n      <div class="method-desc">封面只放一个主体（产品/手部动作），剔除杂乱背景</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69dc53dd0000000021007b99" target="_blank">\n      <span class="ic-metric">44.2%</span>\n      <span class="ic-title">不愧是老师傅推荐用的小炒酱，吃完还想吃</span>\n      <span class="ic-hl">&quot;老师傅推荐&quot;权威背书+复购暗示</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69c877d40000000022028c9f" target="_blank">\n      <span class="ic-metric">40.8%</span>\n      <span class="ic-title">🍖香贡贡肉松！厦门老味道真香！</span>\n      <span class="ic-hl">emoji+地域味道&quot;厦门老味道&quot;，唤起共鸣</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🔥 数字+反差词</div>\n      <div class="method-desc">标题用数字钩子或反差词</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d9d5e9000000001a02b60d" target="_blank">\n      <span class="ic-metric">34.0%</span>\n      <span class="ic-title">(无标题)</span>\n      <span class="ic-hl">无标题制造神秘，靠首帧悬念吸点击</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69dc53dd0000000021007b99" target="_blank">\n      <span class="ic-metric">44.2%</span>\n      <span class="ic-title">不愧是老师傅推荐用的小炒酱，吃完还想吃</span>\n      <span class="ic-hl">&quot;老师傅推荐&quot;权威背书+复购暗示</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D2</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">💬 情绪共鸣开头</div>\n      <div class="method-desc">第一人称场景，精准锁人群</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69dc53dd0000000021007b99" target="_blank">\n      <span class="ic-metric">44.2%</span>\n      <span class="ic-title">不愧是老师傅推荐用的小炒酱，吃完还想吃</span>\n      <span class="ic-hl">&quot;老师傅推荐&quot;权威背书+复购暗示</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69c877d40000000022028c9f" target="_blank">\n      <span class="ic-metric">40.8%</span>\n      <span class="ic-title">🍖香贡贡肉松！厦门老味道真香！</span>\n      <span class="ic-hl">emoji+地域味道&quot;厦门老味道&quot;，唤起共鸣</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🎬 视频口播钩子</div>\n      <div class="method-desc">开头3秒悬念/反问/报价，让用户继续看</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69c7d4e4000000001a029d83" target="_blank">\n      <span class="ic-metric">36.1%</span>\n      <span class="ic-title">视频同款“膳食五白”👇️👇️下方购买</span>\n      <span class="ic-hl">视频同款+引导下方购买，强行动召唤</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69dc53dd0000000021007b99" target="_blank">\n      <span class="ic-metric">44.2%</span>\n      <span class="ic-title">不愧是老师傅推荐用的小炒酱，吃完还想吃</span>\n      <span class="ic-hl">&quot;老师傅推荐&quot;权威背书+复购暗示</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🌍 地域/产地背书</div>\n      <div class="method-desc">「厦门老味道」「厂家直发」等产地词，增加真实感</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69c877d40000000022028c9f" target="_blank">\n      <span class="ic-metric">40.8%</span>\n      <span class="ic-title">🍖香贡贡肉松！厦门老味道真香！</span>\n      <span class="ic-hl">emoji+地域味道&quot;厦门老味道&quot;，唤起共鸣</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69255cb0000000001e00158a" target="_blank">\n      <span class="ic-metric">33.9%</span>\n      <span class="ic-title">浙江小孩🧒的噩梦已经开始</span>\n      <span class="ic-hl">&quot;浙江小孩噩梦&quot;地域梗，制造好奇</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div>'
CTR2_METHODS_T = '<div class="method-card-v2">\n      <div class="method-title">🏷️ 价格直给</div>\n      <div class="method-desc">标题/封面露价格（9.9、6.6折、开业特惠），降低决策门槛</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/67d533d9000000001b03db5d" target="_blank">\n      <span class="ic-metric">200.0%</span>\n      <span class="ic-title">这价格还要什么自行车！！</span>\n      <span class="ic-hl">&quot;还要什么自行车&quot;价格爆款梗，直击便宜</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0936fb000000003502e04d" target="_blank">\n      <span class="ic-metric">93.9%</span>\n      <span class="ic-title">6.6折抹茶千层10只</span>\n      <span class="ic-hl">6.6折+具体数量10只，折扣强吸引</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D8</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">⏰ 节日/限时氛围</div>\n      <div class="method-desc">节气、节假日、开业活动，制造时限紧迫感</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a22ed3a000000002100809a" target="_blank">\n      <span class="ic-metric">91.7%</span>\n      <span class="ic-title">芒种后湿热睡不醒，每天一杯薏米茶伏湿</span>\n      <span class="ic-hl">节气+症状+解决方案，精准对症种草</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a129a7800000000350235bf" target="_blank">\n      <span class="ic-metric">88.6%</span>\n      <span class="ic-title">618狂欢，6.18抢好物抢不到别怪我!</span>\n      <span class="ic-hl">618谐音梗+怕抢不到，限时紧迫</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📊 参数堆叠</div>\n      <div class="method-desc">低卡+无面粉+高蛋白等多卖点参数化，商品卡信息密度高</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69e30880000000001a036594" target="_blank">\n      <span class="ic-metric">86.0%</span>\n      <span class="ic-title">几十大卡+高含水量+无面粉｜蛋白三角太懂事！</span>\n      <span class="ic-hl">低卡+无面粉+三角形参数，强卖点堆叠</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/67d533d9000000001b03db5d" target="_blank">\n      <span class="ic-metric">200.0%</span>\n      <span class="ic-title">这价格还要什么自行车！！</span>\n      <span class="ic-hl">&quot;还要什么自行车&quot;价格爆款梗，直击便宜</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🏆 稀缺/催促</div>\n      <div class="method-desc">「别停产」「顾客催涨价」等稀缺感，触发囤货行为</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0526bd00000000350265b8" target="_blank">\n      <span class="ic-metric">91.7%</span>\n      <span class="ic-title">警告！买过的顾客都在催：“商家别涨价！！”🤣</span>\n      <span class="ic-hl">顾客催更涨价，制造稀缺紧迫感</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a129a7800000000350235bf" target="_blank">\n      <span class="ic-metric">88.6%</span>\n      <span class="ic-title">618狂欢，6.18抢好物抢不到别怪我!</span>\n      <span class="ic-hl">618谐音梗+怕抢不到，限时紧迫</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">💊 对症解决方案</div>\n      <div class="method-desc">节气症状+产品=精准解决方案，商品卡承接感强</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a22ed3a000000002100809a" target="_blank">\n      <span class="ic-metric">91.7%</span>\n      <span class="ic-title">芒种后湿热睡不醒，每天一杯薏米茶伏湿</span>\n      <span class="ic-hl">节气+症状+解决方案，精准对症种草</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/67d533d9000000001b03db5d" target="_blank">\n      <span class="ic-metric">200.0%</span>\n      <span class="ic-title">这价格还要什么自行车！！</span>\n      <span class="ic-hl">&quot;还要什么自行车&quot;价格爆款梗，直击便宜</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div>'
CTR2_METHODS_V = '<div class="method-card-v2">\n      <div class="method-title">🏷️ 价格直给</div>\n      <div class="method-desc">视频口播强调价格/活动，卡片价格曝光</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank">\n      <span class="ic-metric">74.9%</span>\n      <span class="ic-title">又是每月一号福利，晚上八点直接左下方拍</span>\n      <span class="ic-hl">每月1号福利+八点开抢，定期蹲点心智</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0fff4400000000350333ca" target="_blank">\n      <span class="ic-metric">60.4%</span>\n      <span class="ic-title">芜湖～均价2r的牛乳来咯🤩</span>\n      <span class="ic-hl">均价2元牛乳，超低价格震撼</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D8</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">👥 用户口碑/复购</div>\n      <div class="method-desc">老用户回购、真实好评、每月福利，建立信任</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank">\n      <span class="ic-metric">74.9%</span>\n      <span class="ic-title">又是每月一号福利，晚上八点直接左下方拍</span>\n      <span class="ic-hl">每月1号福利+八点开抢，定期蹲点心智</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69ec5f85000000001a036ba2" target="_blank">\n      <span class="ic-metric">67.6%</span>\n      <span class="ic-title">高原出行怕高反？试试这个用过的都说好</span>\n      <span class="ic-hl">高原痛点+老用户口碑，刚需场景转化</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D4</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🎭 拟声/口感描述</div>\n      <div class="method-desc">「剥皮+爆汁」「沉浸式打包」等感官卖点，视频场景还原</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a2528d6000000001702c42e" target="_blank">\n      <span class="ic-metric">66.7%</span>\n      <span class="ic-title">剥皮软糖➕爆汁软糖！</span>\n      <span class="ic-hl">剥皮+爆汁双口感卖点，产品力直给</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1d331b0000000035039d06" target="_blank">\n      <span class="ic-metric">74.9%</span>\n      <span class="ic-title">又是每月一号福利，晚上八点直接左下方拍</span>\n      <span class="ic-hl">每月1号福利+八点开抢，定期蹲点心智</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📦 具体配置/参数</div>\n      <div class="method-desc">告诉用户买到什么（几个/几折/有什么），减少决策摩擦</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1ea02100000000380214b2" target="_blank">\n      <span class="ic-metric">63.5%</span>\n      <span class="ic-title">老爹：9.9🍞咱就赚个手工费 不贪心💰</span>\n      <span class="ic-hl">老爹人设+9.9只赚手工费，朴实真诚</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69ec5f85000000001a036ba2" target="_blank">\n      <span class="ic-metric">67.6%</span>\n      <span class="ic-title">高原出行怕高反？试试这个用过的都说好</span>\n      <span class="ic-hl">高原痛点+老用户口碑，刚需场景转化</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🌍 场景代入</div>\n      <div class="method-desc">高原/出行/特定人群精准场景，用户代入感强</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69ec5f85000000001a036ba2" target="_blank">\n      <span class="ic-metric">67.6%</span>\n      <span class="ic-title">高原出行怕高反？试试这个用过的都说好</span>\n      <span class="ic-hl">高原痛点+老用户口碑，刚需场景转化</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/690933590000000007020316" target="_blank">\n      <span class="ic-metric">63.2%</span>\n      <span class="ic-title">宝集来川麦冬</span>\n      <span class="ic-hl">原产地+品类名直说，垂类人群精准</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div>'
CVR_METHODS_T  = '<div class="method-card-v2">\n      <div class="method-title">🎯 精准人群锁定</div>\n      <div class="method-desc">标题含具体人群词（备孕/减脂/宝妈），过滤无效流量</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69f015770000000035025097" target="_blank">\n      <span class="ic-metric">600.0%</span>\n      <span class="ic-title">干饭人的种草风！！！</span>\n      <span class="ic-hl">&quot;干饭人&quot;标签+种草直说，精准人群</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/683feb6d0000000021002105" target="_blank">\n      <span class="ic-metric">1250.0%</span>\n      <span class="ic-title">山姆这些巨巨巨好吃的😋，你都尝遍了吗</span>\n      <span class="ic-hl">山姆代购心智+经典选品，目标人群明确</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">💬 停产/求回购焦虑</div>\n      <div class="method-desc">「求别停产」「回购第N次」营造缺失焦虑，老粉情感强转化</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69cb2e6d0000000022028511" target="_blank">\n      <span class="ic-metric">900.0%</span>\n      <span class="ic-title">😭求求别停产…太好吃了！！给我狠狠的火🥹</span>\n      <span class="ic-hl">停产焦虑+求火，老粉情感强转化</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/676aad0800000000140251c9" target="_blank">\n      <span class="ic-metric">600.0%</span>\n      <span class="ic-title">三拼布列塔尼酥饼 | 感谢季每天做不完</span>\n      <span class="ic-hl">&quot;做不完&quot;暗示热销，限量焦虑促单</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D4</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🏢 品牌/渠道背书</div>\n      <div class="method-desc">山姆/奥莱/直营等强渠道信任背书，降低决策门槛</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/683feb6d0000000021002105" target="_blank">\n      <span class="ic-metric">1250.0%</span>\n      <span class="ic-title">山姆这些巨巨巨好吃的😋，你都尝遍了吗</span>\n      <span class="ic-hl">山姆代购心智+经典选品，目标人群明确</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69cb2e6d0000000022028511" target="_blank">\n      <span class="ic-metric">900.0%</span>\n      <span class="ic-title">😭求求别停产…太好吃了！！给我狠狠的火🥹</span>\n      <span class="ic-hl">停产焦虑+求火，老粉情感强转化</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📦 打包/组合拼单</div>\n      <div class="method-desc">「一筐零食」「组合套装」降低单次决策成本，拼单场景</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0e750b000000003502098e" target="_blank">\n      <span class="ic-metric">900.0%</span>\n      <span class="ic-title">这一筐零食的快乐是谁的呀🎊</span>\n      <span class="ic-hl">&quot;一筐零食&quot;打包心智，拼单刚需直击</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/683feb6d0000000021002105" target="_blank">\n      <span class="ic-metric">1250.0%</span>\n      <span class="ic-title">山姆这些巨巨巨好吃的😋，你都尝遍了吗</span>\n      <span class="ic-hl">山姆代购心智+经典选品，目标人群明确</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📊 具体解决方案</div>\n      <div class="method-desc">明确说「怎么用/效果是什么」，降低用户不确定性</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/683feb6d0000000021002105" target="_blank">\n      <span class="ic-metric">1250.0%</span>\n      <span class="ic-title">山姆这些巨巨巨好吃的😋，你都尝遍了吗</span>\n      <span class="ic-hl">山姆代购心智+经典选品，目标人群明确</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69cb2e6d0000000022028511" target="_blank">\n      <span class="ic-metric">900.0%</span>\n      <span class="ic-title">😭求求别停产…太好吃了！！给我狠狠的火🥹</span>\n      <span class="ic-hl">停产焦虑+求火，老粉情感强转化</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D2</div>\n    </div>'
CVR_METHODS_V  = '<div class="method-card-v2">\n      <div class="method-title">🎯 精准人群锁定</div>\n      <div class="method-desc">视频明确目标人群，精准触达</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a1584ae0000000006031839" target="_blank">\n      <span class="ic-metric">433.3%</span>\n      <span class="ic-title">薏米水太快了...我妈以为我又没好好吃饭🤣</span>\n      <span class="ic-hl">妈妈反应场景，养生口粮人群精准</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a06816100000000070269f2" target="_blank">\n      <span class="ic-metric">900.0%</span>\n      <span class="ic-title">胡萝卜搭配苹果做无添加雪糕，孩子超爱吃！</span>\n      <span class="ic-hl">无添加+孩子超爱，宝妈精准转化</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">⭐ 明星/达人同款</div>\n      <div class="method-desc">明星同款+低价品类，强冲动+低决策成本</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d9de7400000000230223e8" target="_blank">\n      <span class="ic-metric">8700.0%</span>\n      <span class="ic-title">好吃到双眼迷离❗️明星同款泡面居然这个味道</span>\n      <span class="ic-hl">明星同款+泡面品类，强冲动+低决策</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69be74f8000000001d0181d2" target="_blank">\n      <span class="ic-metric">1066.7%</span>\n      <span class="ic-title">超解压‼️治愈满分💯！沉浸式打包果茶</span>\n      <span class="ic-hl">解压沉浸感+果茶品类，疗愈刚需</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D4</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🎭 解压/治愈场景</div>\n      <div class="method-desc">解压/沉浸打包等情绪价值场景，疗愈刚需</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69be74f8000000001d0181d2" target="_blank">\n      <span class="ic-metric">1066.7%</span>\n      <span class="ic-title">超解压‼️治愈满分💯！沉浸式打包果茶</span>\n      <span class="ic-hl">解压沉浸感+果茶品类，疗愈刚需</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d9de7400000000230223e8" target="_blank">\n      <span class="ic-metric">8700.0%</span>\n      <span class="ic-title">好吃到双眼迷离❗️明星同款泡面居然这个味道</span>\n      <span class="ic-hl">明星同款+泡面品类，强冲动+低决策</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🏅 夸张赞美+信任</div>\n      <div class="method-desc">「好吃到双眼迷离」「不愧是高人指点」夸张表达种草</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d9de7400000000230223e8" target="_blank">\n      <span class="ic-metric">8700.0%</span>\n      <span class="ic-title">好吃到双眼迷离❗️明星同款泡面居然这个味道</span>\n      <span class="ic-hl">明星同款+泡面品类，强冲动+低决策</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69f01f2e0000000035020c8f" target="_blank">\n      <span class="ic-metric">1000.0%</span>\n      <span class="ic-title">不是‼️现在每日杂粮都受高人指点了吗！</span>\n      <span class="ic-hl">&quot;高人指点&quot;调侃+杂粮赛道，强种草感</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📦 购物车/行动召唤</div>\n      <div class="method-desc">视频末尾「点购物车/评论区链接」明确行动指令</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d9de7400000000230223e8" target="_blank">\n      <span class="ic-metric">8700.0%</span>\n      <span class="ic-title">好吃到双眼迷离❗️明星同款泡面居然这个味道</span>\n      <span class="ic-hl">明星同款+泡面品类，强冲动+低决策</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69be74f8000000001d0181d2" target="_blank">\n      <span class="ic-metric">1066.7%</span>\n      <span class="ic-title">超解压‼️治愈满分💯！沉浸式打包果茶</span>\n      <span class="ic-hl">解压沉浸感+果茶品类，疗愈刚需</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div>'
PRICE_METHODS_T = '<div class="method-card-v2">\n      <div class="method-title">🎁 礼盒/送礼场景</div>\n      <div class="method-desc">送礼/孝心/节日场景标题，客单价天然高</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69be470600000000220243a1" target="_blank">\n      <span class="ic-metric">¥1054</span>\n      <span class="ic-title">上海国际饭店蝴蝶酥伴手礼免排队顺丰到家啦</span>\n      <span class="ic-hl">上海地标伴手礼+免排队顺丰，高端礼赠</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a12979f000000003601875e" target="_blank">\n      <span class="ic-metric">¥3651</span>\n      <span class="ic-title">低于均价1000+喝一级园标杆蜜蜂园！</span>\n      <span class="ic-hl">勃艮第一级园+低于均价1000，专业藏家锁单</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D8</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🍷 专业术语/藏家黑话</div>\n      <div class="method-desc">一级园/老藤/年份/配额等专业词，高客单品类自带高价</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a12979f000000003601875e" target="_blank">\n      <span class="ic-metric">¥3651</span>\n      <span class="ic-title">低于均价1000+喝一级园标杆蜜蜂园！</span>\n      <span class="ic-hl">勃艮第一级园+低于均价1000，专业藏家锁单</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16f83b0000000006022ef1" target="_blank">\n      <span class="ic-metric">¥2073</span>\n      <span class="ic-title">菜刀酒庄 皮耶侯奇酒庄夜圣乔治老藤一级园</span>\n      <span class="ic-hl">酒庄+一级园+老藤全要素，硬通货标的</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🏆 产地/限量</div>\n      <div class="method-desc">产地直发、限量款、联名款等稀缺属性拉价</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/69fdaeca000000003502dceb" target="_blank">\n      <span class="ic-metric">¥1861</span>\n      <span class="ic-title">酩一配额上新｜天时地利人和的大年佳酿</span>\n      <span class="ic-hl">配额限量+大年表述，行家追捧高客单</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a12979f000000003601875e" target="_blank">\n      <span class="ic-metric">¥3651</span>\n      <span class="ic-title">低于均价1000+喝一级园标杆蜜蜂园！</span>\n      <span class="ic-hl">勃艮第一级园+低于均价1000，专业藏家锁单</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📦 大份装/家庭装</div>\n      <div class="method-desc">全家装/囤货价/大份量，推高单笔购买量</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a12979f000000003601875e" target="_blank">\n      <span class="ic-metric">¥3651</span>\n      <span class="ic-title">低于均价1000+喝一级园标杆蜜蜂园！</span>\n      <span class="ic-hl">勃艮第一级园+低于均价1000，专业藏家锁单</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a16f83b0000000006022ef1" target="_blank">\n      <span class="ic-metric">¥2073</span>\n      <span class="ic-title">菜刀酒庄 皮耶侯奇酒庄夜圣乔治老藤一级园</span>\n      <span class="ic-hl">酒庄+一级园+老藤全要素，硬通货标的</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D9</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">💎 高端/品质定位</div>\n      <div class="method-desc">强调品质/工艺/产地溯源，主动建立高价值感</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a12979f000000003601875e" target="_blank">\n      <span class="ic-metric">¥3651</span>\n      <span class="ic-title">低于均价1000+喝一级园标杆蜜蜂园！</span>\n      <span class="ic-hl">勃艮第一级园+低于均价1000，专业藏家锁单</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/69d4cc68000000002102e6d7" target="_blank">\n      <span class="ic-metric">¥1231</span>\n      <span class="ic-title">周董同款酒庄平替！400+喝一级园！</span>\n      <span class="ic-hl">明星同款酒庄平替，高端心智借势</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D5</div>\n    </div>'
PRICE_METHODS_V = '<div class="method-card-v2">\n      <div class="method-title">🍷 专业术语/藏家黑话</div>\n      <div class="method-desc">老茶/扫地僧传人/百年老藤等专业黑话，圈层高客单</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0410c00000000007011964" target="_blank">\n      <span class="ic-metric">¥2430</span>\n      <span class="ic-title">默尔索扫地僧传人，百年老藤仙泉园！</span>\n      <span class="ic-hl">默尔索扫地僧+百年老藤，行家黑话精准</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank">\n      <span class="ic-metric">¥1228</span>\n      <span class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</span>\n      <span class="ic-hl">05版博友+七级砖，老茶藏家术语</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🏆 名酒/稀缺开箱</div>\n      <div class="method-desc">100瓶黑金LLM/25周年等名酒开箱，实拍强背书</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a042d5f00000000080241a9" target="_blank">\n      <span class="ic-metric">¥1484</span>\n      <span class="ic-title">拿了100多瓶25周年黑金LLM光明僧侣，开一箱</span>\n      <span class="ic-hl">黑金LLM25周年+开箱实拍，稀缺名酒</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank">\n      <span class="ic-metric">¥1228</span>\n      <span class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</span>\n      <span class="ic-hl">05版博友+七级砖，老茶藏家术语</span>\n    </a></div>\n      <div class="method-source">来源：三感六度</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🎁 高价值场景叙事</div>\n      <div class="method-desc">婚庆/高端宴席/馈赠等场景，高价格有叙事撑腰</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/689ab7060000000023027bec" target="_blank">\n      <span class="ic-metric">¥843</span>\n      <span class="ic-title">【测评】宋观十年，无过滤黄酒又出爆品了！</span>\n      <span class="ic-hl">宋观十年无过滤黄酒，新爆品高端测评</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0410c00000000007011964" target="_blank">\n      <span class="ic-metric">¥2430</span>\n      <span class="ic-title">默尔索扫地僧传人，百年老藤仙泉园！</span>\n      <span class="ic-hl">默尔索扫地僧+百年老藤，行家黑话精准</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D8</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">📊 价值数字化</div>\n      <div class="method-desc">均价超1000/一瓶抵多瓶等量化价值，建立高客单认知</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0410c00000000007011964" target="_blank">\n      <span class="ic-metric">¥2430</span>\n      <span class="ic-title">默尔索扫地僧传人，百年老藤仙泉园！</span>\n      <span class="ic-hl">默尔索扫地僧+百年老藤，行家黑话精准</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a042d5f00000000080241a9" target="_blank">\n      <span class="ic-metric">¥1484</span>\n      <span class="ic-title">拿了100多瓶25周年黑金LLM光明僧侣，开一箱</span>\n      <span class="ic-hl">黑金LLM25周年+开箱实拍，稀缺名酒</span>\n    </a></div>\n      <div class="method-source">来源：creation-guide-v9 D2</div>\n    </div><div class="method-card-v2">\n      <div class="method-title">🌍 产地/年份溯源</div>\n      <div class="method-desc">特定产区+年份，老茶/名庄等直接定价锚点</div>\n      <div class="method-cases"><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a224d0e0000000008002b04" target="_blank">\n      <span class="ic-metric">¥1228</span>\n      <span class="ic-title">鸿运熟茶已上车。开05版博友301批次七级砖</span>\n      <span class="ic-hl">05版博友+七级砖，老茶藏家术语</span>\n    </a><a class="inline-case" href="https://www.xiaohongshu.com/explore/6a0410c00000000007011964" target="_blank">\n      <span class="ic-metric">¥2430</span>\n      <span class="ic-title">默尔索扫地僧传人，百年老藤仙泉园！</span>\n      <span class="ic-hl">默尔索扫地僧+百年老藤，行家黑话精准</span>\n    </a></div>\n      <div class="method-source">来源：诺亚 insight-v20</div>\n    </div>'

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
