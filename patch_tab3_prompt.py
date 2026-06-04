#!/usr/bin/env python3
"""
Tab3「我的内容参考」全面重构：
- 拆除 hardcode KNOWLEDGE 匹配逻辑
- 改为调豆包 API，注入：
  1. Tab1 对应品类实时风向（本周 3 条 trend directions）
  2. Tab1 本周 TOP 笔记标题（同品类 Top3）
  3. Tab1 本周标题公式（高 CTR 结构）
  4. Tab1 本周热门话题
  5. 三感六度打分维度（内嵌方法论）
  6. 5 条 D 维方法论（D2/D5/D8/D4/D9）
  7. 商家自填：品类 + 价格带 + 卖点 + 人群 + 可选 SPU 名
- 输出：S/A/B 分级笔记方向卡（每级含标题模板 + 封面建议 + 话题 + 理由）
"""

content = open('index.html').read()

# ── 1. 替换 Tab3 HTML ──
OLD_TAB3 = '''id="tab-ref">
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
  </div>'''

NEW_TAB3 = '''id="tab-ref">
    <div class="section-label"><span class="icon">🎯</span> 我的内容参考 <span class="tag">本周行业数据 × 你的产品 → 个性化笔记策略</span></div>

    <div class="ref-intro">
      <strong>这里不是模板库。</strong>每次生成都会读取本周真实跑量风向（Tab1 数据），结合你的产品卖点，用 AI 推导出对你最有价值的内容打法。<br>
      <span style="color:var(--text2)">填得越具体，输出越精准。卖点不要写「好吃」，要写「冻干不结块/猪油渣手打」这类可感知的细节。</span>
    </div>

    <!-- ① 品类 -->
    <div class="ref-form" style="margin-bottom:0">
      <div class="ref-form-title">① 告诉我你的产品</div>

      <div class="form-row">
        <label class="form-label">品类 <span class="required">*</span></label>
        <div class="cat-l1-grid" id="ref-catL1Grid">
          <button class="cat-l1-btn" data-cat="snack"   onclick="refSelectL1(this)">🍿 零食</button>
          <button class="cat-l1-btn" data-cat="instant" onclick="refSelectL1(this)">🍜 速食</button>
          <button class="cat-l1-btn" data-cat="drink"   onclick="refSelectL1(this)">🧋 饮品</button>
          <button class="cat-l1-btn" data-cat="liquor"  onclick="refSelectL1(this)">🍷 酒类</button>
          <button class="cat-l1-btn" data-cat="herb"    onclick="refSelectL1(this)">🌿 中式滋补</button>
        </div>
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">产品名称（可以是 SPU 名或自定义）</label>
        <input class="form-input" id="ref-spu" type="text" placeholder="例：XX 牌古法红糖 / 自家炒的辣条 / 不填也行">
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">核心卖点 <span class="required">*</span> <span style="font-size:11px;color:var(--text2)">写可感知的细节，不要写「好吃」「高质量」</span></label>
        <input class="form-input" id="ref-selling" type="text" placeholder="例：猪油渣手打 / 0添加防腐剂 / 古法熬制48小时 / 产地直发不过中间商">
        <div style="margin-top:6px;font-size:11px;color:var(--text2)">填 2-4 个，用逗号分隔。✅「冻干不结块、汤底分离」 ❌「好喝、性价比高」</div>
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">价格带 <span class="required">*</span></label>
        <div style="display:flex;flex-wrap:wrap;gap:8px" id="ref-priceBtns">
          <button class="price-btn" data-price="9.9以下"  onclick="refSelectPrice(this)">¥9.9 以下</button>
          <button class="price-btn" data-price="9.9-29"   onclick="refSelectPrice(this)">¥9.9–29</button>
          <button class="price-btn" data-price="29-59"    onclick="refSelectPrice(this)">¥29–59</button>
          <button class="price-btn" data-price="59-99"    onclick="refSelectPrice(this)">¥59–99</button>
          <button class="price-btn" data-price="99-199"   onclick="refSelectPrice(this)">¥99–199</button>
          <button class="price-btn" data-price="199以上"  onclick="refSelectPrice(this)">¥199 以上</button>
        </div>
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">目标人群 <span class="required">*</span> <span style="font-size:11px;color:var(--text2)">可多选，AI 会为每类人群分别推导切入角</span></label>
        <div style="display:flex;flex-wrap:wrap;gap:8px" id="ref-audBtns">
          <button class="aud-btn" data-aud="gift"     onclick="refToggleAud(this)">🎁 送礼/伴手礼</button>
          <button class="aud-btn" data-aud="daily"    onclick="refToggleAud(this)">🧸 自己吃/日常</button>
          <button class="aud-btn" data-aud="kids"     onclick="refToggleAud(this)">👶 宝妈/给孩子</button>
          <button class="aud-btn" data-aud="office"   onclick="refToggleAud(this)">💼 办公室/下午茶</button>
          <button class="aud-btn" data-aud="diet"     onclick="refToggleAud(this)">🏋️ 减脂/健身</button>
          <button class="aud-btn" data-aud="elder"    onclick="refToggleAud(this)">🌸 送长辈/孝心</button>
          <button class="aud-btn" data-aud="student"  onclick="refToggleAud(this)">📚 学生党/宿舍</button>
          <button class="aud-btn" data-aud="midnight" onclick="refToggleAud(this)">🌙 深夜/加班</button>
        </div>
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">你觉得最大的竞争压力来自哪里？<span style="font-size:11px;color:var(--text2)">可以不填</span></label>
        <input class="form-input" id="ref-competitor" type="text" placeholder="例：同价位有太多类似产品 / 大牌在抢我的流量 / 同质化严重">
      </div>

      <div class="form-row" style="margin-top:14px">
        <label class="form-label">你希望这次内容主要解决什么问题？<span style="font-size:11px;color:var(--text2)">可以不填</span></label>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
          <button class="cat-l2-btn" data-goal="ctr"   onclick="refToggleGoal(this)">📈 提升封面点击率</button>
          <button class="cat-l2-btn" data-goal="cvr"   onclick="refToggleGoal(this)">🛒 提升商卡转化</button>
          <button class="cat-l2-btn" data-goal="brand" onclick="refToggleGoal(this)">🏷️ 建立品牌认知</button>
          <button class="cat-l2-btn" data-goal="new"   onclick="refToggleGoal(this)">✨ 新品上市破冷启动</button>
          <button class="cat-l2-btn" data-goal="node"  onclick="refToggleGoal(this)">🗓️ 节点/大促借势</button>
        </div>
      </div>

      <button class="btn-gen-main" onclick="generateRefV2()" id="genRefBtn">
        🤖 生成我的内容策略（AI 分析）
      </button>
    </div>

    <!-- 结果区 -->
    <div id="ref-result-area" style="display:none;margin-top:24px">
      <div class="section-label"><span class="icon">✨</span> AI 分析结果 <span class="tag" id="ref-result-meta"></span></div>
      <div id="ref-result-loading" style="text-align:center;padding:40px;font-size:14px;color:var(--text2)">
        <div style="font-size:28px;margin-bottom:12px">🤖</div>
        正在读取本周行业数据 + 分析你的产品定位…<br>
        <span style="font-size:12px;color:var(--text3)">大约需要 10-20 秒</span>
      </div>
      <div id="ref-result-content" style="display:none"></div>
      <div style="display:flex;gap:10px;margin-top:20px" id="ref-result-actions" style="display:none">
        <button class="btn-refresh" onclick="generateRefV2()">↻ 重新生成</button>
        <button class="btn-copy-all" onclick="copyRefResult()">📋 复制全部策略</button>
      </div>
    </div>

  </div>'''

assert OLD_TAB3 in content, f'Tab3 HTML not found (len={len(OLD_TAB3)})'
content = content.replace(OLD_TAB3, NEW_TAB3)

# ── 2. 替换 generateRef JS 函数（以及相关的 renderRefResult / copyRefAll） ──
OLD_GEN_REF_JS = '''function generateRef() {
    if (!currentCatId) { alert('请先选择品类'); return; }
    if (!selectedPrice) { alert('请选择价格带'); return; }
    const kw = document.getElementById('refKeywords').value.trim();
    if (!kw) { alert('请填写核心卖点'); return; }
    const pkg = KNOWLEDGE[currentCatId];
    if (!pkg) { showNoData(); return; }
    const keywords = kw.split(/[，,、\\s]+/).filter(Boolean);
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
        '<div class="ref-card-title"><span>🧑\\u200d🤝\\u200d🧑</span> 高潜人群</div>' +
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
  }'''

NEW_GEN_REF_JS = r'''// ── Tab3 状态变量 ──
  let refCatId = '';
  let refPrice = '';
  let refAudiences = [];
  let refGoals = [];

  function refSelectL1(btn) {
    document.querySelectorAll('#ref-catL1Grid .cat-l1-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    refCatId = btn.dataset.cat;
  }
  function refSelectPrice(btn) {
    document.querySelectorAll('#ref-priceBtns .price-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    refPrice = btn.dataset.price;
  }
  function refToggleAud(btn) {
    btn.classList.toggle('active');
    refAudiences = Array.from(document.querySelectorAll('#ref-audBtns .aud-btn.active')).map(b => b.textContent.trim());
  }
  function refToggleGoal(btn) {
    btn.classList.toggle('active');
    refGoals = Array.from(document.querySelectorAll('[data-goal].active')).map(b => b.textContent.trim());
  }

  // ── 从 Tab1 HTML 抽取当前品类风向文本 ──
  function getTab1TrendData(catId) {
    const catMap = { snack:'snack', instant:'fast', drink:'drink', liquor:'liquor', herb:'herb' };
    const cls = catMap[catId] || catId;
    const head = document.querySelector('.trend-head.' + cls);
    if (!head) return null;
    const card = head.closest('.trend-card');
    if (!card) return null;
    const dirs = Array.from(card.querySelectorAll('.trend-dir')).map(d => d.textContent.trim());
    return dirs;
  }

  // ── 从 Tab1 抽取 TOP 笔记（同品类） ──
  function getTab1TopNotes(catId) {
    const catLabelMap = { snack:'零食', instant:'速食', drink:'饮品', liquor:'酒', herb:'滋补' };
    const label = catLabelMap[catId] || '';
    // TOP_NOTES 是 JS 全局变量
    if (typeof TOP_NOTES === 'undefined') return [];
    return TOP_NOTES.filter(n => n.cat && n.cat.includes && (n.cat.includes(label) || label === '')).slice(0, 5);
  }

  // ── 从 Tab1 抽取本周标题公式 ──
  function getTab1Formulas() {
    const rows = document.querySelectorAll('.formula-row');
    const result = [];
    rows.forEach(row => {
      const pills = Array.from(row.querySelectorAll('.formula-pill')).map(p => p.textContent.trim());
      const example = row.querySelector('.formula-example');
      if (pills.length) result.push(pills.join(' + ') + (example ? '（例：' + example.textContent.trim() + '）' : ''));
    });
    return result;
  }

  // ── 从 Tab1 抽取热门话题 ──
  function getTab1Topics() {
    const tags = Array.from(document.querySelectorAll('.topic-tag.hot, .topic-tag')).map(t => t.textContent.trim()).filter(t => t.startsWith('#'));
    return [...new Set(tags)].slice(0, 12);
  }

  // ── 构建完整 prompt ──
  function buildRefPrompt(params) {
    const { catId, catName, spuName, selling, price, audiences, competitor, goals } = params;

    const directions = getTab1TrendData(catId) || ['（本周数据加载中，请刷新页面后重试）'];
    const topNotes   = getTab1TopNotes(catId);
    const formulas   = getTab1Formulas();
    const topics     = getTab1Topics();

    const topNoteText = topNotes.length
      ? topNotes.map(n => `「${n.title}」 CTR ${n.ctr}%${n.tagCtr ? '，商卡转化 ' + n.tagCtr + '%' : ''}`).join('\n')
      : '（本周数据未加载，请刷新后重试）';
    const formulaText = formulas.length ? formulas.join('\n') : '（公式数据未加载）';
    const topicsText  = topics.length ? topics.join(' ') : '（话题数据未加载）';
    const dirText     = directions.map((d, i) => `${i+1}. ${d}`).join('\n');

    const goalText = goals.length ? '核心目标：' + goals.join('、') : '';
    const compText = competitor ? '竞争压力：' + competitor : '';

    return `你是一位深耕小红书休食行业的资深内容策划，手上有本周平台真实跑量数据。

商家产品信息如下：
【品类】${catName}
【产品名/SPU】${spuName || '（商家未填）'}
【核心卖点】${selling}
【价格带】${price}
【目标人群】${audiences.length ? audiences.join('、') : '（未指定）'}
${goalText}
${compText}

━━━━ 本周 ${catName} 类目真实跑量风向（你必须深度用好这些数据）━━━━
${dirText}

━━━━ 本周同类目高 CTR 笔记标题（真实案例，学习其语言节奏）━━━━
${topNoteText}

━━━━ 本周全行业高 CTR 标题结构公式（提炼自 TOP 笔记，用于启发）━━━━
${formulaText}

━━━━ 本周热门话题池（选 5-8 个适配的打在内容里）━━━━
${topicsText}

━━━━ 休食内容创作 5 条核心方法论（必须评估每套方案命中哪些）━━━━
D2 卖点前置：标题/封面前 8 字必须出现最核心的可感知卖点，绝不用模糊词开头
D5 人群×场景：内容必须锁定「谁 + 在什么场景下」，越具体越好（不是"学生党"而是"备考期间宿舍深夜饿了"）
D8 使用场景具体：不说功效，说使用体验的细节——味道/口感/动作/情绪反应，让用户产生"我就是这样的"的共鸣
D4 评论引导：正文结尾必须有一个让用户想回复的具体问题或行动钩子（不是"快来购买"，是"你平时什么时候最需要它"）
D9 内容饱满：图文 200 字以上，视频有真实使用画面，不能是纯文字+产品白图

━━━━ 三感六度评估框架（用于检验内容质量）━━━━
三感：视觉感（封面是否抓眼）、味觉感（味道描述是否可感知）、情绪感（读者是否有感触）
六度：真实度（像真人说话）、场景度（有具体时间地点）、细节度（有超出预期的小细节）、卖点度（核心利益清晰）、传播度（是否有让人转发/收藏的点）、转化度（是否有促进行动的设计）

━━━━ 违规红线（三套方案均不得出现）━━━━
❌ 禁止极值词：最好/第一/唯一/极致/史上/天花板/NO.1
❌ 禁止功效词（普通食品）：减肥/瘦身/燃脂/美白/助消化/排毒/降血糖/抗癌
❌ 禁止虚假承诺：X天瘦X斤/临床验证/医学证明
❌ 禁止诱导行为：加微信/私信我/点关注抽奖/加群

━━━━ 你的任务 ━━━━
请输出 S / A / B 三个等级的笔记策略方向，每个等级 1 套（共 3 套）。

【S 级——借势本周最强风向，潜力最高】
必须深度结合上方「本周跑量风向」中的某一条，注明用了第几条。不是简单提及，而是真正复刻这条风向的逻辑，把产品嫁接进去。

【A 级——挖产品本质细节，差异化竞争】
完全不看行业趋势，从产品的某个具体细节/工艺/使用体验出发，找一个竞品不会写的切入角。

【B 级——人群精准锁定，转化优先】
从目标人群的真实生活场景出发，用 D5（人群×场景）+ D8（使用场景具体）为核心，专注于把商卡转化率拉上去。

━━━━ 每套方案输出格式（严格执行）━━━━

▌S/A/B 级 · [用一句话概括这套方案的核心思路]

📌 方法论命中：[列出命中的 D 维编号，如 D2、D5]
🎯 三感六度亮点：[说出这套方案最强的 2 个维度]

📝 标题方向（给 3 条候选，每条 ≤20 字含 emoji）
1.
2.
3.
说明：[为什么这 3 条标题能跑量，标题里用了哪个公式逻辑]

🖼️ 封面策划
画面：[描述封面里有什么，构图，颜色，有没有人]
主文案：[≤8 字，覆盖在封面上的文字]
点击逻辑：[为什么用户会点这个封面]

📄 正文框架（写出开头 2 句 + 结构提示）
开头：[前 2 句，第一人称，有具体场景或细节]
结构：[正文应该怎么展开，比如：场景引入→细节描述→使用体验→购买引导]
结尾钩子：[一个能让人回复评论的具体问题]

🏷️ 推荐话题（5-8 个，从本周热门话题池中选+补充）

⚠️ 违规自查：[逐条检查，有风险词标出并给替换词，全部通过则写"✅ 无违规风险"]

---

最后单独输出一个【本周最值得蹭的 1 个话题】：
> 说明为什么这个话题和这个产品最契合，给出一条专门为这个话题量身设计的标题。`;
  }

  // ── 渲染 AI 结果 ──
  function renderRefAIResult(text) {
    const lines = text.split('\n');
    let html = '<div style="font-size:14px;line-height:1.8;color:var(--text)">';
    let inBlock = false;
    lines.forEach(line => {
      const l = line.trim();
      if (!l) { html += '<br>'; return; }
      if (l.startsWith('▌')) {
        if (inBlock) html += '</div>';
        html += `<div class="ref-card" style="margin-bottom:16px"><div style="font-size:15px;font-weight:800;color:var(--text);margin-bottom:14px;border-left:3px solid var(--primary);padding-left:10px">${l}</div>`;
        inBlock = true;
      } else if (l.startsWith('📝') || l.startsWith('🖼️') || l.startsWith('📄') || l.startsWith('🏷️') || l.startsWith('⚠️') || l.startsWith('📌') || l.startsWith('🎯')) {
        html += `<div style="font-size:13px;font-weight:700;color:var(--text2);margin:12px 0 6px;padding-top:10px;border-top:1px solid var(--border)">${l}</div>`;
      } else if (l.startsWith('1.') || l.startsWith('2.') || l.startsWith('3.')) {
        html += `<div class="ref-template">${l}</div>`;
      } else if (l.startsWith('>')) {
        html += `<div class="check-top-tip">${l.slice(1).trim()}</div>`;
      } else if (l.startsWith('【本周最值得')) {
        if (inBlock) { html += '</div>'; inBlock = false; }
        html += `<div class="sgld-card" style="margin-top:20px"><div class="sgld-title">💡 ${l}</div>`;
        inBlock = true;
      } else {
        html += `<div style="margin:3px 0">${l}</div>`;
      }
    });
    if (inBlock) html += '</div>';
    html += '</div>';
    return html;
  }

  // ── 主函数：生成 Tab3 内容参考 ──
  async function generateRefV2() {
    if (!refCatId) { alert('请先选择品类'); return; }
    if (!refPrice) { alert('请选择价格带'); return; }
    const selling = document.getElementById('ref-selling').value.trim();
    if (!selling) { alert('请填写核心卖点（例：猪油渣手打/0添加防腐剂）'); return; }
    if (refAudiences.length === 0) { alert('请至少选择一个目标人群'); return; }

    const catNameMap = { snack:'零食', instant:'速食', drink:'饮品', liquor:'酒类', herb:'中式滋补' };
    const params = {
      catId:      refCatId,
      catName:    catNameMap[refCatId] || refCatId,
      spuName:    document.getElementById('ref-spu').value.trim(),
      selling,
      price:      refPrice,
      audiences:  refAudiences,
      competitor: document.getElementById('ref-competitor').value.trim(),
      goals:      refGoals
    };

    const area    = document.getElementById('ref-result-area');
    const loading = document.getElementById('ref-result-loading');
    const content = document.getElementById('ref-result-content');
    const actions = document.getElementById('ref-result-actions');
    const meta    = document.getElementById('ref-result-meta');

    area.style.display    = 'block';
    loading.style.display = 'block';
    content.style.display = 'none';
    if (actions) actions.style.display = 'none';

    const btn = document.getElementById('genRefBtn');
    btn.disabled = true;
    btn.textContent = '⏳ AI 分析中（约 15 秒）…';

    window.scrollTo({ top: area.offsetTop - 80, behavior: 'smooth' });

    try {
      const prompt = buildRefPrompt(params);
      const resp = await fetch('https://ark.cn-beijing.volces.com/api/v3/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + _ak },
        body: JSON.stringify({
          model: 'doubao-seed-2-0-lite-260215',
          messages: [
            { role: 'system', content: '你是专业的小红书休食行业内容策划专家，精通平台算法和行业数据。请按用户要求的格式严格输出，不要添加额外的开场白或结束语。' },
            { role: 'user',   content: prompt }
          ],
          max_tokens: 3000,
          temperature: 0.75
        })
      });
      const data = await resp.json();
      if (!data.choices) throw new Error(data.error ? data.error.message : 'API 请求失败');

      const result = data.choices[0].message.content.trim();
      loading.style.display = 'none';
      content.innerHTML = renderRefAIResult(result);
      content.style.display = 'block';
      if (actions) actions.style.display = 'flex';
      meta.textContent = params.catName + ' · ' + params.price + ' · 本周数据驱动';
      window._lastRefResult = result;
      gtag('event', 'ref_generated_v2', { cat: refCatId, price: refPrice });
    } catch (e) {
      loading.style.display = 'none';
      content.innerHTML = '<div style="color:var(--red);padding:20px;text-align:center">❌ 生成失败：' + e.message + '<br><button class="btn-refresh" style="margin-top:12px" onclick="generateRefV2()">重试</button></div>';
      content.style.display = 'block';
    } finally {
      btn.disabled = false;
      btn.textContent = '🤖 重新生成';
    }
  }

  function copyRefResult() {
    const text = window._lastRefResult || document.getElementById('ref-result-content').innerText;
    navigator.clipboard.writeText(text).then(() => {
      const btn = document.querySelector('#ref-result-actions .btn-copy-all');
      if (btn) { btn.textContent = '✅ 已复制'; setTimeout(() => btn.textContent = '📋 复制全部策略', 2000); }
    });
  }

  // 保留旧函数防止其他地方调用报错
  function generateRef() { generateRefV2(); }
  function copyRefAll() { copyRefResult(); }'''

assert OLD_GEN_REF_JS in content, 'generateRef JS not found'
content = content.replace(OLD_GEN_REF_JS, NEW_GEN_REF_JS)

# ── 3. 校验 style 平衡 ──
opens  = content.count('<style>')
closes = content.count('</style>')
print(f'style: {opens} ↔ {closes}')
assert opens == closes, 'style 不平衡！'

open('index.html', 'w').write(content)
print(f'写入: {len(content)} bytes')
