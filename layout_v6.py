#!/usr/bin/env python3
"""
Layout V6: 真正有感知的结构改版
1. Hero 区：大字周次 + 数据摘要卡
2. 品类风向手风琴（默认收起，点击展开）
3. 顶部笔记数量减少（默认显示Top8，有"展开更多"）
4. 整体间距/呼吸感大幅提升
"""

content = open('index.html').read()

# ─── 1. 替换 Header HTML ───────────────────────────────────────
OLD_HEADER = '''<header class="header">
  <div class="header-left">
    <div class="header-icon">🍿</div>
    <div>
      <div class="header-title">休食商笔风向看板</div>
      <div class="header-sub">小红书电商 · 商家内容创作参考 · 每周更新</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-week" style="color:var(--primary)">W21</div>
    <div class="header-date" style="color:var(--text-sub)">2026.05.18 — 05.24</div>
  </div>
</header>'''

NEW_HEADER = '''<header class="header">
  <div class="header-left">
    <div class="header-icon">🍿</div>
    <div>
      <div class="header-title">休食商笔风向看板</div>
      <div class="header-sub">小红书电商 · 商家内容创作参考</div>
    </div>
  </div>
  <div class="header-right">
    <div class="header-week">W21</div>
    <div class="header-date">2026.05.18 — 05.24</div>
  </div>
</header>

<!-- ── HERO ── -->
<div class="hero-section">
  <div class="hero-inner">
    <div class="hero-text">
      <div class="hero-week-badge">第 21 周</div>
      <h1 class="hero-title">本周内容风向摘要</h1>
      <p class="hero-desc">基于休食五组 W21 真实笔记数据 · 高 CTR 笔记结构提炼 · 每周更新</p>
    </div>
    <div class="hero-stats">
      <div class="hero-stat">
        <div class="hero-stat-num">39%</div>
        <div class="hero-stat-label">本周最高封面CTR</div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat-num">88.6%</div>
        <div class="hero-stat-label">本周最高商卡CTR</div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat-num">83万+</div>
        <div class="hero-stat-label">单笔记最高曝光</div>
      </div>
      <div class="hero-stat">
        <div class="hero-stat-num">5</div>
        <div class="hero-stat-label">覆盖品类</div>
      </div>
    </div>
  </div>
</div>'''

if OLD_HEADER in content:
    content = content.replace(OLD_HEADER, NEW_HEADER)
    print('✅ Header → Hero 替换成功')
else:
    print('❌ Header 未找到，检查原文')
    import sys; sys.exit(1)

# ─── 2. 品类风向改手风琴 ───────────────────────────────────────
# 找 cat-wrap 区块
CAT_WRAP_OLD = '''  <!-- ⑥ 品类风向 -->
  <div class="section-label">
    <span class="icon">📦</span> 品类风向
    <span class="tag">W21 各品类重点动向 · 05.18—05.24</span>
  </div>
  <div class="cat-wrap">
    <div class="cat-grid">

      <div class="cat-card">
        <div class="cat-head snack">🍿 零食</div>
        <div class="cat-items">
          <div class="cat-item"><span class="cat-dot up">↑</span><span>「裸寄」反向吸睛持续爆量：卤味/糖果/果干多条同题 CTR 20~32%，最高曝光 83万+</span></div>
          <div class="cat-item"><span class="cat-dot up">↑</span><span>仅退款情绪共鸣：商家视角「什么都仅退款只会害了你」CTR 20~25%，曝光 6~70万</span></div>
          <div class="cat-item"><span class="cat-dot">→</span><span>节日礼品/新口味冲量：迪拜曲奇/Apple礼包 CTR 20~25%，商卡转化 4~18%</span></div>
        </div>
        <div class="cat-focus">重点关注：裸寄/仅退款情绪共鸣 + 节日礼品场景</div>
      </div>

      <div class="cat-card">
        <div class="cat-head fast">🍜 速食</div>
        <div class="cat-items">
          <div class="cat-item"><span class="cat-dot up">↑</span><span>商家被抄/破防情绪：「刚创业还没靠XX赚钱就被抄袭」CTR 18~23%，曝光 16~23万</span></div>
          <div class="cat-item"><span class="cat-dot up">↑</span><span>价格性价比反差：「30r够吃两周，终结外卖焦虑」CTR 20%，商卡转化 15.7%</span></div>
          <div class="cat-item"><span class="cat-dot">→</span><span>减脂低卡场景稳定：「能撑死人但热量很低」CTR 22.3%，商卡转化 16.5%</span></div>
        </div>
        <div class="cat-focus">重点关注：商家情绪叙事 + 外卖替代/性价比场景</div>
      </div>

      <div class="cat-card">
        <div class="cat-head drink">🧋 饮品</div>
        <div class="cat-items">
          <div class="cat-item"><span class="cat-dot up">↑</span><span>体型焦虑精准人群：「肚子这样再节食也没用」养生茶系列 CTR 19~25%，曝光 5~55万</span></div>
          <div class="cat-item"><span class="cat-dot up">↑</span><span>好奇疑问句高点击：「请问这杯是神吗？？？！」CTR 26.4%，曝光 7.4万，商卡 10.9%</span></div>
          <div class="cat-item"><span class="cat-dot">→</span><span>生活场景轻松调性：普洱/乳制品日常趣味感 CTR 18~23%，商卡 5~8%</span></div>
        </div>
        <div class="cat-focus">重点关注：体型焦虑功效承诺 + 好奇疑问句式</div>
      </div>

      <div class="cat-card">
        <div class="cat-head liquor">🍵 茶/酒</div>
        <div class="cat-items">
          <div class="cat-item"><span class="cat-dot up">↑</span><span>好奇疑问句引爆点击：「请问这杯是神吗？？？！」花草茶 CTR 26.4%，曝光 7.4万，商卡 10.9%，悬念感极强</span></div>
          <div class="cat-item"><span class="cat-dot up">↑</span><span>普洱×生活轻松场景：「一个人出门兜里太轻了，请带上猫」CTR 23.6%，「6.0猫盒预告 仲夏夜之猫」CTR 24.7%，IP调性带动购买</span></div>
          <div class="cat-item"><span class="cat-dot">→</span><span>体型焦虑+养生茶精准人群：「肚子这样再节食也没用」系列 CTR 19~25%，曝光 5~55万，精准人群即转化</span></div>
        </div>
        <div class="cat-focus">重点关注：好奇疑问句式 + 体型焦虑功效场景</div>
      </div>

      <div class="cat-card">
        <div class="cat-head herb">🌿 中式滋补</div>
        <div class="cat-items">
          <div class="cat-item"><span class="cat-dot up">↑</span><span>长辈/专家权威背书：「93岁老先生推荐！坚持吃了一个月好舒服」CTR 23.8%，权威人物背书是最稳定信任公式</span></div>
          <div class="cat-item"><span class="cat-dot up">↑</span><span>亚健康摆脱功效：「黄精吃吧！成功摆脱了班味」CTR 24.7%；「如果你的肚子也是这样，再节食也没用」CTR 19~25%，痛点精准触达</span></div>
          <div class="cat-item"><span class="cat-dot">→</span><span>母亲节礼品场景：「50+的妈妈想要什么礼物」阿胶膏方 CTR 22.6%，节日礼赠+中老年人群，是5月主力内容方向</span></div>
        </div>
        <div class="cat-focus">重点关注：长辈背书信任 + 母亲节礼品场景</div>
      </div>

    </div>
  </div>'''

CAT_WRAP_NEW = '''  <!-- ⑥ 品类风向 -->
  <div class="section-label">
    <span class="icon">📦</span> 品类重点动向
    <span class="tag">W21 · 05.18—05.24</span>
  </div>
  <div class="accordion-wrap">

    <div class="acc-item" onclick="toggleAcc(this)">
      <div class="acc-head">
        <span class="acc-badge snack">🍿</span>
        <span class="acc-title">零食</span>
        <span class="acc-summary">裸寄情绪爆量 · 联名礼盒高转化 · 山姆测评稳定</span>
        <span class="acc-arrow">›</span>
      </div>
      <div class="acc-body">
        <div class="acc-item-row"><span class="dot up">↑</span><span>「裸寄」反向吸睛持续爆量：卤味/糖果/果干多条同题 CTR 20~32%，最高曝光 83万+</span></div>
        <div class="acc-item-row"><span class="dot up">↑</span><span>仅退款情绪共鸣：商家视角「什么都仅退款只会害了你」CTR 20~25%，曝光 6~70万</span></div>
        <div class="acc-item-row"><span class="dot">→</span><span>节日礼品/新口味冲量：迪拜曲奇/Apple礼包 CTR 20~25%，商卡转化 4~18%</span></div>
        <div class="acc-focus">🎯 重点：裸寄/仅退款情绪共鸣 + 节日礼品场景</div>
      </div>
    </div>

    <div class="acc-item" onclick="toggleAcc(this)">
      <div class="acc-head">
        <span class="acc-badge fast">🍜</span>
        <span class="acc-title">速食</span>
        <span class="acc-summary">商家破防情绪 · 外卖替代性价比 · 减脂低卡稳定</span>
        <span class="acc-arrow">›</span>
      </div>
      <div class="acc-body">
        <div class="acc-item-row"><span class="dot up">↑</span><span>商家被抄/破防情绪：「刚创业还没靠XX赚钱就被抄袭」CTR 18~23%，曝光 16~23万</span></div>
        <div class="acc-item-row"><span class="dot up">↑</span><span>价格性价比反差：「30r够吃两周，终结外卖焦虑」CTR 20%，商卡转化 15.7%</span></div>
        <div class="acc-item-row"><span class="dot">→</span><span>减脂低卡场景稳定：「能撑死人但热量很低」CTR 22.3%，商卡转化 16.5%</span></div>
        <div class="acc-focus">🎯 重点：商家情绪叙事 + 外卖替代/性价比场景</div>
      </div>
    </div>

    <div class="acc-item" onclick="toggleAcc(this)">
      <div class="acc-head">
        <span class="acc-badge drink">🧋</span>
        <span class="acc-title">饮品</span>
        <span class="acc-summary">体型焦虑精准触达 · 好奇疑问句 · 夏日减脂续命</span>
        <span class="acc-arrow">›</span>
      </div>
      <div class="acc-body">
        <div class="acc-item-row"><span class="dot up">↑</span><span>体型焦虑精准人群：「肚子这样再节食也没用」养生茶系列 CTR 19~25%，曝光 5~55万</span></div>
        <div class="acc-item-row"><span class="dot up">↑</span><span>好奇疑问句高点击：「请问这杯是神吗？？？！」CTR 26.4%，曝光 7.4万，商卡 10.9%</span></div>
        <div class="acc-item-row"><span class="dot">→</span><span>生活场景轻松调性：普洱/乳制品日常趣味感 CTR 18~23%，商卡 5~8%</span></div>
        <div class="acc-focus">🎯 重点：体型焦虑功效承诺 + 好奇疑问句式</div>
      </div>
    </div>

    <div class="acc-item" onclick="toggleAcc(this)">
      <div class="acc-head">
        <span class="acc-badge liquor">🍵</span>
        <span class="acc-title">茶/酒</span>
        <span class="acc-summary">好奇疑问句爆点击 · 普洱IP调性 · 618预热囤货</span>
        <span class="acc-arrow">›</span>
      </div>
      <div class="acc-body">
        <div class="acc-item-row"><span class="dot up">↑</span><span>好奇疑问句引爆点击：「请问这杯是神吗？？？！」花草茶 CTR 26.4%，曝光 7.4万，悬念感极强</span></div>
        <div class="acc-item-row"><span class="dot up">↑</span><span>普洱×生活轻松场景：「6.0猫盒预告 仲夏夜之猫」CTR 24.7%，IP调性带动购买</span></div>
        <div class="acc-item-row"><span class="dot">→</span><span>618活动预热：「谁说618活动没意思 老品囤货」普洱 CTR 22.6%，商卡转化 9.3%</span></div>
        <div class="acc-focus">🎯 重点：好奇疑问句式 + 体型焦虑功效场景</div>
      </div>
    </div>

    <div class="acc-item" onclick="toggleAcc(this)">
      <div class="acc-head">
        <span class="acc-badge herb">🌿</span>
        <span class="acc-title">中式滋补</span>
        <span class="acc-summary">长辈权威背书 · 亚健康功效 · 母亲节礼品</span>
        <span class="acc-arrow">›</span>
      </div>
      <div class="acc-body">
        <div class="acc-item-row"><span class="dot up">↑</span><span>长辈/专家权威背书：「93岁老先生推荐！坚持吃了一个月好舒服」CTR 23.8%</span></div>
        <div class="acc-item-row"><span class="dot up">↑</span><span>亚健康摆脱功效：「黄精吃吧！成功摆脱了班味」CTR 24.7%，痛点精准触达</span></div>
        <div class="acc-item-row"><span class="dot">→</span><span>母亲节礼品场景：「50+的妈妈想要什么礼物」阿胶膏方 CTR 22.6%</span></div>
        <div class="acc-focus">🎯 重点：长辈背书信任 + 母亲节礼品场景</div>
      </div>
    </div>

  </div>'''

if CAT_WRAP_OLD in content:
    content = content.replace(CAT_WRAP_OLD, CAT_WRAP_NEW)
    print('✅ 品类风向 → 手风琴替换成功')
else:
    print('❌ cat-wrap 未找到')
    import sys; sys.exit(1)

# ─── 3. 注入手风琴 CSS 和 Hero CSS ────────────────────────────
CSS_INJECT = '''
/* ── HERO SECTION ── */
.hero-section {
  background: linear-gradient(135deg, #FE2C55 0%, #FF7070 100%);
  padding: 40px 36px;
  position: relative;
  overflow: hidden;
}
.hero-section::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 240px; height: 240px;
  border-radius: 50%;
  background: rgba(255,255,255,.08);
}
.hero-section::after {
  content: '';
  position: absolute;
  bottom: -40px; left: 20%;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,.05);
}
.hero-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  position: relative;
  z-index: 1;
}
.hero-week-badge {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,.2);
  color: rgba(255,255,255,.9);
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 10px;
}
.hero-title {
  font-size: 28px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -.5px;
  line-height: 1.2;
  margin-bottom: 8px;
}
.hero-desc {
  font-size: 13px;
  color: rgba(255,255,255,.75);
  line-height: 1.5;
}
.hero-stats {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}
.hero-stat {
  background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.2);
  border-radius: 14px;
  padding: 14px 18px;
  text-align: center;
  backdrop-filter: blur(8px);
  min-width: 90px;
}
.hero-stat-num {
  font-size: 22px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -1px;
  line-height: 1;
}
.hero-stat-label {
  font-size: 10px;
  color: rgba(255,255,255,.75);
  margin-top: 5px;
  line-height: 1.3;
}

/* ── ACCORDION ── */
.accordion-wrap { display: flex; flex-direction: column; gap: 8px; }
.acc-item {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--r14);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow .2s;
}
.acc-item:hover { box-shadow: var(--shadow-md); }
.acc-item.open  { border-color: #CCCCCC; box-shadow: var(--shadow-md); }
.acc-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  user-select: none;
}
.acc-badge {
  flex-shrink: 0;
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.acc-badge.snack  { background: linear-gradient(135deg,#FF6B35,#FF8E53); }
.acc-badge.fast   { background: linear-gradient(135deg,#FFB020,#FFC94D); }
.acc-badge.drink  { background: linear-gradient(135deg,#0BA5EC,#38BDF8); }
.acc-badge.liquor { background: linear-gradient(135deg,#0D9488,#2DD4BF); }
.acc-badge.herb   { background: linear-gradient(135deg,#17B26A,#4ADE80); }
.acc-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
  flex-shrink: 0;
  min-width: 64px;
}
.acc-summary {
  font-size: 13px;
  color: var(--text2);
  flex: 1;
}
.acc-arrow {
  font-size: 20px;
  color: var(--text3);
  font-weight: 700;
  transition: transform .2s;
  flex-shrink: 0;
}
.acc-item.open .acc-arrow { transform: rotate(90deg); color: var(--red); }
.acc-body {
  display: none;
  padding: 0 20px 16px;
  border-top: 1px solid var(--border2);
}
.acc-item.open .acc-body { display: block; }
.acc-item-row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 9px 0;
  border-bottom: 1px solid var(--border2);
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}
.acc-item-row:last-of-type { border-bottom: none; }
.dot { flex-shrink: 0; font-size: 14px; font-weight: 900; margin-top: 1px; }
.dot.up { color: var(--red); }
.dot { color: var(--text3); }
.acc-focus {
  margin-top: 10px;
  padding: 9px 12px;
  border-radius: var(--r10);
  background: var(--red-soft);
  color: var(--red);
  font-size: 12px;
  font-weight: 600;
  border-left: 3px solid var(--red);
}

@media (max-width: 768px) {
  .hero-inner  { flex-direction: column; align-items: flex-start; }
  .hero-stats  { flex-wrap: wrap; }
  .hero-stat   { min-width: 80px; }
  .hero-title  { font-size: 22px; }
  .hero-section { padding: 28px 16px; }
  .acc-summary { display: none; }
}
'''

# 插在第二个 </style> 前
second_style_end = content.rfind('</style>')
content = content[:second_style_end] + CSS_INJECT + '\n' + content[second_style_end:]
print('✅ CSS 注入成功')

# ─── 4. 注入手风琴 JS ─────────────────────────────────────────
JS_INJECT = '''
function toggleAcc(el) {
  var isOpen = el.classList.contains('open');
  document.querySelectorAll('.acc-item').forEach(function(a){ a.classList.remove('open'); });
  if (!isOpen) el.classList.add('open');
}
'''

# 插在最后一个 </script> 前
last_script_end = content.rfind('</script>')
content = content[:last_script_end] + JS_INJECT + content[last_script_end:]
print('✅ JS 注入成功')

# ─── 5. 校验 ──────────────────────────────────────────────────
opens  = content.count('<style>')
closes = content.count('</style>')
print(f'style tags: {opens} ↔ {closes}')
assert opens == closes, 'style 不平衡'

open('index.html', 'w').write(content)
print(f'写入 {len(content)} bytes')
