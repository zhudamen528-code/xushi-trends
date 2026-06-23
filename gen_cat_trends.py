#!/usr/bin/env python3
"""
gen_cat_trends.py - 从 data.json 的 top_cases 自动生成 CAT_TRENDS JS 对象
逻辑：
  1. 读 data.json top_cases（CTR1/CTR2/CVR/price 各 Top N 案例）
  2. 按品类（零食/速食/饮品/酒类/滋补）归拢案例
  3. 提炼每品类的 directions（本周方向文案）、formulas（标题公式）、cover（封面建议）
  4. 输出 JS 片段，供 build_v10.py 注入 index.html

设计原则：
  - 全程中文，不暴露英文字段名
  - 方向文案从真实标题/亮点提炼，不凭空捏造
  - 每品类至少 3 条案例才提炼，否则用兜底文案
"""
import json, os, re, sys
from collections import defaultdict
from datetime import datetime

WORKDIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON = os.path.join(WORKDIR, 'data.json')

# 品类关键词映射（seller_name/title 关键词 → 品类）
CATEGORY_KEYWORDS = {
    '零食': ['零食','薯片','饼干','糖果','坚果','瓜子','爆米花','膨化','脆','饼','小饼','酥','麻薯','魔芋','辣条','蜜饯','果干'],
    '速食': ['速食','泡面','方便面','自热','火锅','螺蛳粉','米线','拉面','乌冬','即食','代餐','燕麦','麦片','粥'],
    '饮品': ['饮品','饮料','果汁','茶','咖啡','奶茶','牛奶','豆浆','气泡水','苏打水','运动饮料','功能饮料','椰汁'],
    '酒类': ['酒','啤酒','葡萄酒','白酒','黄酒','米酒','梅子酒','果酒','洋酒','威士忌','红酒'],
    '滋补': ['滋补','保健','燕窝','胶原','蛋白','维生素','益生菌','枸杞','红枣','阿胶','人参','虫草','蜂蜜'],
}

# 兜底文案（当样本不足时使用）
FALLBACK_TRENDS = {
    '零食': {
        'directions': ['减脂场景切入，把零食和健康生活方式强绑定', '用具体数字说话：热量/蛋白质/配料表透明化', '反差感标题：不像零食但好吃'],
        'formulas': ['「XX 也能吃的零食」痛点消解式', '「X 克蛋白 / X 卡」数字背书式', '「减脂期最爱的 XX」场景代入式'],
        'cover': '手持产品+营养标签特写，或减脂食谱搭配场景'
    },
    '速食': {
        'directions': ['深夜/加班场景，解决「想吃好但懒得做」痛点', '口味还原度对比：和堂食一样好吃', '一人食场景，情绪共鸣优先'],
        'formulas': ['「X 分钟搞定一顿饭」效率式', '「一个人也要好好吃饭」情感式', '「比外卖好吃还便宜」对比式'],
        'cover': '热腾腾出锅瞬间，或工作桌上的精致一人食'
    },
    '饮品': {
        'directions': ['颜值/出片感驱动，强调适合拍照分享', '功能性卖点前置：提神/美颜/解腻', '季节场景绑定：夏日清凉/冬日暖身'],
        'formulas': ['「XX 天的 XX 瓶」打卡挑战式', '「喝了 X 次还在买」复购背书式', '「XX 味的夏天」情绪共鸣式'],
        'cover': '饮品+手/背景出片，光线明亮，强调液体色泽'
    },
    '酒类': {
        'directions': ['送礼/社交场景切入，降低选酒门槛', '口感描述细腻化：香型/入口感/回甘', '年轻化：低度微醺/调酒方案'],
        'formulas': ['「XX 场合必备的 XX」场景强绑定式', '「第一次喝酒就选 XX」破圈式', '「不懂酒也能喝对的 XX」降门槛式'],
        'cover': '酒瓶+酒杯精致陈列，或聚餐/礼品场景'
    },
    '滋补': {
        'directions': ['功效具体化：用了多久/改善了什么', '成分透明+溯源背书', '人群精准：熬夜党/职场人/女性养护'],
        'formulas': ['「坚持 XX 天的变化」时间线式', '「XX 岁开始养 XX」年龄段切入式', '「熬夜必备的 XX」人群精准式'],
        'cover': '产品+使用场景（早晨/睡前），质感光线，强调仪式感'
    },
}

def classify_note(title, seller_name):
    """根据标题和商家名判断品类"""
    text = (title or '') + (seller_name or '')
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cat
    return None

def extract_directions_from_cases(cases, max_directions=3):
    """从真实案例的 highlight 字段提炼方向文案"""
    highlights = []
    for c in cases:
        h = c.get('highlight', '')
        if h and len(h) > 5:
            # 去掉「」包裹（如果有）
            h = h.strip('「」')
            highlights.append(h)

    if len(highlights) < 2:
        return None  # 样本不足，用兜底

    # 去重、截取前 max_directions 条
    seen = set()
    directions = []
    for h in highlights:
        # 取前30字，避免太长
        h_short = h[:40] if len(h) > 40 else h
        if h_short not in seen:
            seen.add(h_short)
            directions.append(h_short)
        if len(directions) >= max_directions:
            break
    return directions if len(directions) >= 2 else None

def extract_title_formulas(cases, max_formulas=3):
    """从真实案例标题提炼标题公式"""
    titles = [c.get('title', '') for c in cases if c.get('title')]

    formulas = []
    # 识别常见公式模式
    patterns = [
        ('数字量化式', r'\d+[克克卡元天次瓶包件]'),
        ('问句探索式', r'[？?]'),
        ('反差对比式', r'(但|却|没想到|竟然|其实)'),
        ('场景绑定式', r'(减脂|熬夜|早餐|宵夜|健身|上班|一人食)'),
        ('情绪共鸣式', r'(泪|哭|爱上|沉迷|绝了|yyds|救命)'),
    ]

    pattern_examples = defaultdict(list)
    for title in titles:
        for formula_name, pattern in patterns:
            if re.search(pattern, title):
                if len(pattern_examples[formula_name]) < 2:
                    pattern_examples[formula_name].append(title[:20])

    for formula_name, examples in list(pattern_examples.items())[:max_formulas]:
        ex = examples[0] if examples else ''
        formulas.append(f'「{ex}...」{formula_name}')

    return formulas if len(formulas) >= 2 else None

def build_cat_trends(data_json_path):
    """主函数：读 data.json → 生成 CAT_TRENDS dict"""
    with open(data_json_path, encoding='utf-8') as f:
        data = json.load(f)

    top_cases = data.get('top_cases', {})
    updated_at = data.get('updated_at', datetime.now().strftime('%Y-%m-%d'))
    window_raw = data.get('window', {})
    # 兼容两种格式：list ['start','end'] 或 dict {'start_dtm':..., 'end_dtm':...}
    if isinstance(window_raw, list):
        window = window_raw
    elif isinstance(window_raw, dict):
        window = [window_raw.get('start_dtm',''), window_raw.get('end_dtm','')]
    else:
        window = ['', '']

    # 收集所有案例，按品类归拢
    cat_cases = defaultdict(list)
    for metric in ['ctr1', 'ctr2', 'cvr', 'price']:
        for form in ['图文', '视频']:
            cases = top_cases.get(metric, {}).get(form, [])
            for c in cases:
                cat = classify_note(c.get('title', ''), c.get('seller_name', ''))
                if cat:
                    cat_cases[cat].append(c)

    print(f"品类归拢结果：")
    for cat, cases in cat_cases.items():
        print(f"  {cat}: {len(cases)} 条案例")

    # 生成每品类的 CAT_TRENDS 条目
    cat_trends = {}
    for cat in ['零食', '速食', '饮品', '酒类', '滋补']:
        cases = cat_cases.get(cat, [])

        # 提炼方向和公式
        directions = extract_directions_from_cases(cases) if len(cases) >= 3 else None
        formulas = extract_title_formulas(cases) if len(cases) >= 3 else None

        # 不足时使用兜底
        fallback = FALLBACK_TRENDS[cat]
        if not directions:
            directions = fallback['directions']
            print(f"  {cat}: 方向文案使用兜底（样本{len(cases)}条不足）")
        if not formulas:
            formulas = fallback['formulas']
            print(f"  {cat}: 标题公式使用兜底（样本{len(cases)}条不足）")

        # cover 目前固定（从 data.json 中没有封面建议字段，用兜底）
        cover = fallback['cover']

        # 取本品类最高 CTR1 的案例作为本周代表案例
        best_cases = sorted(
            [c for c in cases if c.get('note_url')],
            key=lambda x: x.get('value', 0),
            reverse=True
        )[:3]

        cat_trends[cat] = {
            'directions': directions,
            'formulas': formulas,
            'cover': cover,
            'top_notes': [
                {
                    'title': c.get('title', ''),
                    'url': c.get('note_url', ''),
                    'highlight': c.get('highlight', ''),
                    'seller': c.get('seller_name', ''),
                }
                for c in best_cases
            ],
            'sample_count': len(cases),
            'data_window': f"{window[0]} ~ {window[1]}" if window else '',
        }

    return cat_trends, updated_at

def render_js(cat_trends, updated_at):
    """生成 JS 片段（CAT_TRENDS 对象）"""
    lines = ['const CAT_TRENDS = {']
    for cat, data in cat_trends.items():
        directions_js = json.dumps(data['directions'], ensure_ascii=False)
        formulas_js = json.dumps(data['formulas'], ensure_ascii=False)
        top_notes_js = json.dumps(data['top_notes'], ensure_ascii=False, indent=6)
        lines.append(f'  "{cat}": {{')
        lines.append(f'    "directions": {directions_js},')
        lines.append(f'    "formulas": {formulas_js},')
        lines.append(f'    "cover": {json.dumps(data["cover"], ensure_ascii=False)},')
        lines.append(f'    "top_notes": {top_notes_js},')
        lines.append(f'    "sample_count": {data["sample_count"]},')
        lines.append(f'    "data_window": {json.dumps(data["data_window"], ensure_ascii=False)},')
        lines.append('  },')
    lines.append('};')
    lines.append(f'// 数据时间：{updated_at}（自动生成，勿手动修改）')
    return '\n'.join(lines)

def main():
    print(f"[gen_cat_trends] 开始生成 CAT_TRENDS，数据源：{DATA_JSON}")

    if not os.path.exists(DATA_JSON):
        print(f"[ERROR] data.json 不存在：{DATA_JSON}")
        sys.exit(1)

    cat_trends, updated_at = build_cat_trends(DATA_JSON)
    js_snippet = render_js(cat_trends, updated_at)

    # 输出到文件，供 build_v10.py 读取注入
    out_path = os.path.join(WORKDIR, 'cat_trends_generated.js')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(js_snippet)

    print(f"[gen_cat_trends] 写出：{out_path} ({os.path.getsize(out_path)} bytes)")
    print(f"[gen_cat_trends] 品类数：{len(cat_trends)}")
    for cat, d in cat_trends.items():
        print(f"  {cat}: {d['sample_count']}条案例，{'真实提炼' if d['sample_count']>=3 else '兜底文案'}")

    # 同时打印预览
    print("\n--- CAT_TRENDS 预览 ---")
    for cat, d in cat_trends.items():
        print(f"\n【{cat}】（{d['sample_count']}条样本，{d['data_window']}）")
        for i, direction in enumerate(d['directions'], 1):
            print(f"  方向{i}：{direction}")
        for i, formula in enumerate(d['formulas'], 1):
            print(f"  公式{i}：{formula}")
        if d['top_notes']:
            note = d['top_notes'][0]
            print(f"  代表案例：{note['title'][:30]}  ({note['seller']})")

if __name__ == '__main__':
    main()
