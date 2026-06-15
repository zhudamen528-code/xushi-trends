import json, os

def esc(s):
    if not s: return ''
    s = str(s).replace('<','&lt;').replace('>','&gt;').replace('{','&#123;').replace('}','&#125;')
    return s.replace('|','&#124;')

md = ['# 休食看板 V9 · 数据底池 + Claude 聚类全过程（完整版 8/8）', '']
md.append('> 这是 V9 改造的白盒——数据从哪来、Claude 怎么聚的、每个方法挑了哪些笔记，全部列清楚。')
md.append('')
md.append('**进度：8/8 池聚类已完成 / 共归纳 40 个内容方法**')
md.append('')
md.append('## 一、数据来源（6 表 JOIN）')
md.append('')
md.append('**基础表**：`redcdm.dm_ecm_note_fullchain_guide_1d_di`（dataset 1922 同源）')
md.append('')
md.append('| 表 | 用途 | JOIN key |')
md.append('|---|---|---|')
md.append('| `redcdm.dwd_con_note_info_all_df` | 笔记 title/content/video_asr_text | note_id |')
md.append('| `redcdm.dim_ecm_algo_note_label_df` | 算法质量分 / 购买意图分 | note_id |')
md.append('| `redcdm.dim_ecm_note_extend_df` | 电商笔记品类 / 多商品标记 | note_id |')
md.append('| `redcdm.dim_goods_base_df` | 商品维度（名/价/品牌/类目） | goods_id |')
md.append('| `redapp.app_ecm_ark_ai_note_score_base_nd_di` | **封面 URL（已 CDN 化）** | note_id |')
md.append('| `reddw.dw_soc_discovery_comment_detail_day` | 评论 Top5（高赞）| discovery_id |')
md.append('')
md.append('**时间窗**：2026-04-13 → 2026-06-11（60 天）')
md.append('')
md.append('**过滤**：')
md.append("- `seller_industry = '休食'`（行业品类，非部门）")
md.append("- `bridge_type IN ('goods_v2','goods_seller')` （仅商品笔记）")
md.append('- `SUM(note_imp_num) >= 500 AND SUM(dgmv) >= 100`')
md.append('')
md.append('**三层切分**：爆款 DGMV>=5万（200条）/ 优秀 1-5万（200条）/ 黑马 imp<10000 但 GPM>100（200条）= **600 条**')
md.append('')
md.append('**SQL 执行**：msgId `59770b4d-e3f8-447e-af5f-05e76ca59a12` / 30 分钟跑完 / 1.8MB CSV')
md.append('')

md.append('## 二、8 池切分')
md.append('')
md.append('600 条按 4 指标 × 2 形态切 8 池，每池 60 条干净数据进 Claude。')
md.append('')
md.append('**指标定义**（GPM 漏斗）：CTR1=clk/imp / CTR2=gv/clk / CVR=buy/gv / 件单价=dgmv/buy')
md.append('')
md.append('**异常过滤**：CTR2 失真(gv>clk×1.5) / CVR>100% / 件单价>5000元 / imp<100 / clk<5 → 544/600 进 8 池')
md.append('')
md.append('| 池 | 60 条指标中位 | 60 条 Max | 形态 |')
md.append('|---|---|---|---|')
md.append('| ctr1_pic | 15.4% | 36.4% | 图文 |')
md.append('| ctr1_vid | 9.9% | 21.3% | 视频 |')
md.append('| ctr2_pic | 0.60% | 1.39% | 图文 |')
md.append('| ctr2_vid | 0.84% | 1.48% | 视频 |')
md.append('| cvr_pic | 16.3% | 64.5% | 图文 |')
md.append('| cvr_vid | 16.5% | 100.0% | 视频 |')
md.append('| price_pic | 2541 元 | 4035 元 | 图文 |')
md.append('| price_vid | 978 元 | 4350 元 | 视频 |')
md.append('')
md.append('**ASR 覆盖率**：视频 278 条 / 含 ASR 258 条 = **92.8%**（远超估算 33%）')
md.append('**字段完整度**：cover_url 100% / goods 100% / 评论 80.7% / 算法质量 99.8%')
md.append('')

md.append('## 三、Prompt 红线')
md.append('')
md.append('给 Claude 的核心约束：')
md.append('- 不许编标题/亮点：方法依据必须能从笔记里找到证据')
md.append('- 不许预设方法（不要套现成标签）')
md.append('- 必须从数据归纳：先看完 60 条找规律，再定方法名')
md.append('- 至少 1 个方法包含反直觉发现')
md.append('- 视频池关注 ASR；图文池关注正文段落结构')
md.append('')

md.append('## 四、8 池聚类结果（全 40 方法）')
md.append('')

name_map = {
    'ctr1_pic':'CTR1 · 图文', 'ctr1_vid':'CTR1 · 视频',
    'ctr2_pic':'CTR2 · 图文', 'ctr2_vid':'CTR2 · 视频',
    'cvr_pic':'CVR · 图文', 'cvr_vid':'CVR · 视频',
    'price_pic':'件单价 · 图文', 'price_vid':'件单价 · 视频',
}
order = ['ctr1_pic','ctr1_vid','ctr2_pic','ctr2_vid','cvr_pic','cvr_vid','price_pic','price_vid']

for i, pool in enumerate(order, 1):
    p = f'data/v9_clusters/{pool}.cluster.json'
    d = json.load(open(p))
    md.append(f"### 4.{i} {name_map[pool]}")
    md.append('')
    md.append(f"耗时 {d.get('runtime_sec')}秒 / 输入 60 条候选笔记")
    md.append('')
    
    if 'methods' in d:
        md.append('| 方法 | 笔记数 | 适配品类 | 核心定义 |')
        md.append('|---|---|---|---|')
        for m in d['methods']:
            cat = ' / '.join(m['applicable_category'][:3])
            md.append(f"| {esc(m['method_name'])} | {len(m['note_ids'])} | {esc(cat)} | {esc(m['essence'])} |")
        md.append('')
        md.append(f"**聚类逻辑**：{esc(d.get('cluster_rationale',''))}")
        md.append('')
        md.append('**每方法代表 note 直链**：')
        md.append('')
        for m in d['methods']:
            if m['note_ids']:
                nid = m['note_ids'][0]
                md.append(f"- {esc(m['method_name'])} → https://www.xiaohongshu.com/explore/{nid}")
        md.append('')
        md.append('**完整 note_ids**：')
        md.append('')
        for m in d['methods']:
            ids = ', '.join(f'`{nid}`' for nid in m['note_ids'])
            md.append(f"- **{esc(m['method_name'])}** ({len(m['note_ids'])}条): {ids}")
        md.append('')
    else:
        md.append('| 方法 | 笔记数 | 适配品类 |')
        md.append('|---|---|---|')
        for name, cnt, cats in d['methods_brief']:
            md.append(f"| {esc(name)} | {cnt} | {esc(' / '.join(cats[:4]))} |")
        md.append('')
        md.append(f"**聚类逻辑**：{esc(d.get('rationale',''))}")
        md.append('')

md.append('## 五、跨池强方法（4+ 池命中可作王炸候选）')
md.append('')
md.append('| 方法簇 | 出现池 | 跨指标价值 |')
md.append('|---|---|---|')
md.append('| **反套路/去营销化**（老板喊冤/店主自述/反套路情绪/劝退式）| ctr1_pic + ctr2_pic + ctr2_vid + cvr_vid | 4 池命中，跨指标共性最强 |')
md.append('| **行家/专业身份**（圈层黑话/行家开品/专家溯源/名庄身份/老饕私藏）| ctr1_vid + ctr2_vid + cvr_pic + price_pic | 4 池命中，高客单核心 |')
md.append('| **痛点+人群锚定**（凌晨3点/痛点自查/人群精准/场景痛点）| ctr1_vid + cvr_pic + cvr_vid + ctr2_vid | 4 池命中，转化层引擎 |')
md.append('| **场景礼赠/情感寄托**（送礼场景/场景礼赠/高定情感）| ctr1_pic + cvr_pic + price_pic | 3 池命中，跨形态 |')
md.append('| **工艺/规格数字化**（工厂溯源/规格数字化/节气工艺）| ctr2_vid + price_vid + cvr_vid | 3 池命中，信任硬通货 |')
md.append('')

md.append('## 六、5 大反直觉发现（B 方案的核心价值）')
md.append('')
md.append('这些预设标签法学不到，必须从 600 条数据归纳：')
md.append('')
md.append('1. **食品标题不写"好吃"反而高 CTR1**（CTR1·图文）：写悬念/吐槽/八卦比直白卖货高 2-3 倍')
md.append('2. **圈层黑话低曝光高 CTR**（CTR1·视频）：imp 仅 500-3000 但 CTR 8-15%，精准筛人比追求曝光更划算')
md.append('3. **店主自述体 CVR 高达 85%**（CTR2·图文 / CVR·视频）：去营销化反而高转化（"为啥我们卖酒卖不过别人""真心劝退""老板自爆"）')
md.append('4. **战绩公示反向种草**（CVR·图文）：不夸产品只夸销量（"阿嬷熬不动了""卖了21万"）触发抢购焦虑')
md.append('5. **整箱小瓶套装件单价反而高于正装单卖**（件单价·视频）：用户买的是"组合仪式感"不是单 SKU')
md.append('6. **高定情感寄托跨品类有效**（件单价·图文）：定制蛋糕/孕期燕窝/古法滋补能挤进葡萄酒主导的高客单池，关键是"情感场景具象成实物"')
md.append('')

md.append('## 七、特别提醒')
md.append('')
md.append('**MCN 同款话术警告**：CVR·视频 池里"对手句式"（X的对手是Y）基本是某 MCN（仓鼠行动/有人买食品/斯贝利/味多多）的同款话术，AM 推自己商家用这个方法时**要差异化**避免同质化。')
md.append('')

md.append('## 八、原始数据池（可下钻）')
md.append('')
md.append('每池 60 条原始数据 JSON：')
md.append('')
md.append('```')
md.append('/home/node/.openclaw/workspace/xushi-trends-cron/work/data/v9_pools/{pool}.json')
md.append('/home/node/.openclaw/workspace/xushi-trends-cron/work/data/v9_clusters/{pool}.cluster.json')
md.append('```')
md.append('')

md.append('## 九、下一步')
md.append('')
md.append('1. 你审完 40 个方法（重点看反直觉点），选 8 个王炸（每池 1 个）')
md.append('2. 王炸用 Claude 生成完整 5 件套 SOP（封面/标题/脚本/商品卡/评论）')
md.append('3. 写 build_v9.py 重做 4 指标 Tab：')
md.append('   - 顶部行业 P50/P75')
md.append('   - 🏆 王炸方法（5 件套，红色边框）')
md.append('   - ◇ 其他 4 个方法（精简卡 + 案例横向）')
md.append('   - 📋 全 600 篇完整案例榜（折叠）')
md.append('')
md.append('---')
md.append('')
md.append('生成时间：2026-06-12 12:35 / 8/8 全部完成')

content = '\n'.join(md)
open('V9_DATA_LINEAGE_V2.md','w', encoding='utf-8').write(content)
# REDoc 转义
out = []
in_code = False
for ln in content.split('\n'):
    if ln.startswith('```'):
        in_code = not in_code; out.append(ln); continue
    if in_code: out.append(ln); continue
    ln = ln.replace('<', '&lt;').replace('>', '&gt;')
    out.append(ln)
open('V9_DATA_LINEAGE_V2.redoc.md','w').write('\n'.join(out))
print(f'wrote {len(content)} chars')
