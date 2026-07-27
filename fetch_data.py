#!/usr/bin/env python3
"""
fetch_data.py - 拉 P75 + TOP 案例（V3 SQL，含算法分门槛）+ 亮点提炼，生成 data.json

流程：
  1. 计算时间窗口（T-1 往前 27 天 + 近 14 天发布）
  2. 提交 P75 基准值 SQL
  3. 提交 Top 案例 V3 SQL（算法分质量门槛 + Top 50）
  4. 解析结果，为每条案例生成亮点文案（规则提炼，不依赖外部 API）
  5. 写入 data.json
"""
import subprocess, json, time, sys, os, re
from datetime import datetime, timedelta
from collections import defaultdict

TZ_OFFSET = timedelta(hours=8)
WORKDIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON = os.path.join(WORKDIR, 'data.json')

def cn_now():
    return datetime.utcnow() + TZ_OFFSET

def log(msg):
    print(f"[{cn_now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def submit_sql(sql):
    """提交 HiveSQL，返回 msgId"""
    res = subprocess.run(
        ['dp', 'dataverse', 'sql', 'submit', '--code', sql, '--language', 'HiveSQL'],
        capture_output=True, text=True, cwd=WORKDIR
    )
    out = res.stdout + res.stderr
    for line in out.split('\n'):
        if 'msgId:' in line:
            return line.split('msgId:')[1].strip()
    raise RuntimeError(f"SQL submit failed:\n{out[:800]}")

def wait_finish(msg_id, max_min=25, label=''):
    """轮询直到 FINISHED/SUCCESS，超时抛异常"""
    deadline = time.time() + max_min * 60
    while time.time() < deadline:
        res = subprocess.run(
            ['dp', 'dataverse', 'sql', 'status', '--msg-id', msg_id],
            capture_output=True, text=True
        )
        out = res.stdout + res.stderr
        # 精确匹配状态行：查询状态: XXX
        import re as _re
        m = _re.search(r'查询状态[:\s]+(\w+)', out)
        state = m.group(1).upper() if m else ''
        if state in ('FINISHED', 'SUCCESS', 'SUCCEEDED'):
            return True
        if state in ('FAILED', 'CANCELLED', 'KILLED'):
            raise RuntimeError(f"SQL FAILED [{label}] state={state}:\n{out[:800]}")
        log(f"  ... 等待 {label} state={state or '?'} msgId={msg_id[:10]}")
        time.sleep(30)
    raise TimeoutError(f"SQL 超时 {max_min}min [{label}]")

def get_result(msg_id):
    """获取 SQL 结果 JSON 字符串"""
    res = subprocess.run(
        ['dp', 'dataverse', 'sql', 'result', '--msg-id', msg_id, '--raw'],
        capture_output=True, text=True
    )
    return res.stdout

def parse_rows(raw_json):
    """解析 dp result 返回的 JSON → list of dict"""
    try:
        data = json.loads(raw_json)
        # dp result 通常是 {"dataList": [...], ...} 或直接 [...]
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ['dataList', 'data', 'rows', 'result']:
                if key in data and isinstance(data[key], list):
                    return data[key]
        log(f"  ⚠️ 无法识别结果格式，keys={list(data.keys()) if isinstance(data, dict) else type(data)}")
        return []
    except Exception as e:
        log(f"  ⚠️ 解析结果失败：{e}，原始前200字：{raw_json[:200]}")
        return []

# ── 亮点文案规则提炼 ───────────────────────────────────────────────────────────
PATTERNS = [
    # (正则, 标签模板)
    (r'(\d+)[克g].*蛋白', '「{0}g蛋白质」数字营养卖点'),
    (r'(\d+)[卡kcal]', '「{0}卡」热量量化，健康人群直击'),
    (r'减[脂肥]|瘦身|健身', '减脂/健身场景绑定，刚需人群精准'),
    (r'(\d+)[天月]', '「{0}天/月」时间线背书，增强可信度'),
    (r'[？?]', '问句结构，激发好奇心点击'),
    (r'没想到|竟然|其实|原来', '反差句式，打破预期引发点击'),
    (r'第一次|初次', '破圈场景，降低尝试门槛'),
    (r'一个人|独居|一人食', '一人食场景，情感共鸣'),
    (r'[0-9]+[元r].*[袋包箱盒]|[袋包箱盒].*[0-9]+[元r]', '价格+量感并列，性价比直给'),
    (r'礼[物盒]|送[妈朋友]|节[日]', '送礼场景，购买决策明确'),
    (r'回购|又买|第[二三四]次', '复购信号，真实用户口碑'),
    (r'史低|最低|打折|折扣|优惠', '价格锚点，决策提速'),
]

def gen_highlight(title):
    """根据标题规则提炼亮点文案（纯本地，不依赖外部 API）"""
    if not title:
        return '优质内容，点击查看'
    title = title.strip()
    for pattern, tmpl in PATTERNS:
        m = re.search(pattern, title)
        if m:
            try:
                groups = m.groups()
                return tmpl.format(*groups) if groups else tmpl
            except Exception:
                return tmpl
    # 兜底：截取标题前20字
    short = title[:20].rstrip('，。！？、')
    return f'「{short}」引发点击'

# ── P75 解析 ─────────────────────────────────────────────────────────────────
def parse_p75(rows):
    """把 P75 SQL 结果转为嵌套 dict"""
    def _f(v):
        if v is None: return None
        try: return float(v)
        except (TypeError, ValueError): return None
    p75 = {}
    for r in rows:
        ind = r.get('seller_industry') or r.get('行业') or ''
        form = r.get('note_form') or r.get('形态') or ''
        if not ind or not form:
            continue
        p75.setdefault(ind, {})[form] = {
            'note_cnt':   int(r.get('note_cnt', 0) or 0),
            'ctr1_p50':   _f(r.get('ctr1_p50')),
            'ctr1_p75':   _f(r.get('ctr1_p75')),
            'ctr2_p50':   _f(r.get('ctr2_p50')),
            'ctr2_p75':   _f(r.get('ctr2_p75')),
            'cvr_p50':    _f(r.get('cvr_p50')),
            'cvr_p75':    _f(r.get('cvr_p75')),
            'price_p50':  _f(r.get('price_p50')),
            'price_p75':  _f(r.get('price_p75')),
        }
    # 算 KA 快消大盘（6 品类中位）
    import statistics
    KA_CATS = ['休食', '大健康', '生鲜', '亲子生活', '宠物', '家用']
    ka_avg = {}
    for form in ['图文', '视频']:
        ka_avg[form] = {}
        for key in ['ctr1_p50','ctr1_p75','ctr2_p50','ctr2_p75','cvr_p50','cvr_p75','price_p50','price_p75']:
            vals_raw = [p75[c][form].get(key) for c in KA_CATS if c in p75 and form in p75[c] and p75[c][form].get(key) is not None]
            vals = []
            for v in vals_raw:
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
            ka_avg[form][key] = round(statistics.median(vals), 4) if vals else None
    p75['ka_avg'] = ka_avg
    return p75

# ── Top 案例解析 ─────────────────────────────────────────────────────────────
METRIC_MAP = {'CTR1': 'ctr1', 'CTR2': 'ctr2', 'CVR': 'cvr', 'AOV': 'price'}
FORM_MAP = {1: '图文', 2: '视频', '1': '图文', '2': '视频'}

def parse_top_cases(rows):
    """把 Top 案例结果转为嵌套 dict，并生成亮点"""
    top_cases = {
        'ctr1': {'图文': [], '视频': []},
        'ctr2': {'图文': [], '视频': []},
        'cvr':  {'图文': [], '视频': []},
        'price':{'图文': [], '视频': []},
    }
    for r in rows:
        mn = r.get('metric_name', '')
        m = METRIC_MAP.get(mn)
        if not m:
            continue
        nf_raw = r.get('note_form')
        f = FORM_MAP.get(nf_raw)
        if not f:
            continue
        note_id = str(r.get('note_id', ''))
        title = r.get('title') or ''
        top_cases[m][f].append({
            'rank':        int(r.get('rank', 0) or 0),
            'note_id':     note_id,
            'title':       title or '(无标题)',
            'seller_name': r.get('seller_name') or '',
            'value':       float(r.get('metric_value', 0) or 0),
            'imp':         int(r.get('imp', 0) or 0),
            'click':       int(r.get('click', 0) or 0),
            'buy':         int(r.get('buy', 0) or 0),
            'dgmv':        float(r.get('dgmv', 0) or 0),
            'note_url':    f'https://www.xiaohongshu.com/explore/{note_id}',
            'highlight':   gen_highlight(title),
            'sincerity':   float(r.get('sincerity_score', 0) or 0),
            'good_click':  float(r.get('good_click_score', 0) or 0),
            'cover_aesthetic':   r.get('cover_aesthetic', '') or '',
            'cover_definition':  r.get('cover_definition', '') or '',
            'cover_quality':     r.get('cover_quality', '') or '',
        })
    # 按 rank 排序
    for m in top_cases:
        for f in top_cases[m]:
            top_cases[m][f].sort(key=lambda x: x['rank'])
    return top_cases

# ── 主流程 ───────────────────────────────────────────────────────────────────
def main():
    end = cn_now() - timedelta(days=1)           # T-1
    start = end - timedelta(days=27)             # 近28天
    publish_start = end - timedelta(days=14)     # 发布近14天
    algo_start = end - timedelta(days=7)         # 算法分近7天

    end_dtm        = end.strftime('%Y%m%d')
    start_dtm      = start.strftime('%Y%m%d')
    algo_start_dtm = algo_start.strftime('%Y%m%d')
    publish_start_date = publish_start.strftime('%Y-%m-%d')

    log(f"统计窗口：{start_dtm} → {end_dtm}")
    log(f"算法分窗口：{algo_start_dtm} → {end_dtm}")
    log(f"发布时间窗口：≥ {publish_start_date}")

    # ── Step 1：P75 基准值 ─────────────────────────────────────────────────
    msg_p75 = None
    p75_sql_path = os.path.join(WORKDIR, 'fetch_p75.sql')
    if not os.path.exists(p75_sql_path):
        log(f"⚠️ fetch_p75.sql 不存在，跳过 P75 步骤")
    else:
        with open(p75_sql_path) as f:
            sql_p75 = f.read().format(start_dtm=start_dtm, end_dtm=end_dtm)
        log("提交 P75 SQL...")
        msg_p75 = submit_sql(sql_p75)
        log(f"P75 msgId: {msg_p75}")

    # ── Step 2：Top 案例 V3 ────────────────────────────────────────────────
    msg_cases = None
    cases_sql_path = os.path.join(WORKDIR, 'fetch_top_cases_v3.sql')
    if not os.path.exists(cases_sql_path):
        log(f"⚠️ fetch_top_cases_v3.sql 不存在，跳过 Top 案例步骤")
    else:
        with open(cases_sql_path) as f:
            sql_cases = f.read().format(
                start_dtm=start_dtm,
                end_dtm=end_dtm,
                publish_start_date=publish_start_date,
                algo_start_dtm=algo_start_dtm,
            )
        log("提交 Top 案例 V3 SQL（算法分门槛 + Top 50）...")
        msg_cases = submit_sql(sql_cases)
        log(f"Top 案例 msgId: {msg_cases}")

    # ── Step 3：等待两个 SQL 完成 ──────────────────────────────────────────
    raw_p75 = '{}'
    if msg_p75:
        log("等待 P75 SQL 完成...")
        wait_finish(msg_p75, max_min=25, label='P75')
        raw_p75 = get_result(msg_p75)
        with open(os.path.join(WORKDIR, 'last_p75_raw.json'), 'w') as f:
            f.write(raw_p75)
        log(f"P75 结果 {len(raw_p75)} 字节")

    raw_cases = '[]'
    if msg_cases:
        log("等待 Top 案例 SQL 完成...")
        wait_finish(msg_cases, max_min=30, label='TopCases')
        raw_cases = get_result(msg_cases)
        with open(os.path.join(WORKDIR, 'last_cases_v3_raw.json'), 'w') as f:
            f.write(raw_cases)
        log(f"Top 案例结果 {len(raw_cases)} 字节")

    # ── Step 4：解析 ──────────────────────────────────────────────────────
    p75_rows_parsed   = parse_rows(raw_p75)
    cases_rows_parsed = parse_rows(raw_cases)

    log(f"P75 行数：{len(p75_rows_parsed)}")
    log(f"Top 案例行数：{len(cases_rows_parsed)}")

    # P75 解析（若为空则从旧 data.json 继承）
    if p75_rows_parsed:
        p75 = parse_p75(p75_rows_parsed)
        log("P75 解析完成")
    else:
        log("⚠️ P75 空结果，从旧 data.json 继承")
        try:
            with open(DATA_JSON) as f:
                old = json.load(f)
            p75 = old.get('p75', {})
        except Exception:
            p75 = {}

    # Top 案例解析（若为空则从旧 data.json 继承）
    if cases_rows_parsed:
        top_cases = parse_top_cases(cases_rows_parsed)
        # 统计
        for m in ['ctr1', 'ctr2', 'cvr', 'price']:
            n_tw = len(top_cases[m].get('图文', []))
            n_sp = len(top_cases[m].get('视频', []))
            log(f"  {m.upper()}: 图文 {n_tw} 条 / 视频 {n_sp} 条")
    else:
        log("⚠️ Top 案例空结果，从旧 data.json 继承")
        try:
            with open(DATA_JSON) as f:
                old = json.load(f)
            top_cases = old.get('top_cases', {})
        except Exception:
            top_cases = {}

    # ── Step 5：写 data.json ──────────────────────────────────────────────
    window = {
        'start_dtm': start_dtm,
        'end_dtm':   end_dtm,
        'publish_min': publish_start_date,
    }
    data = {
        'updated_at': cn_now().strftime('%Y-%m-%d %H:%M'),
        'window':     window,
        'p75':        p75,
        'top_cases':  top_cases,
    }

    # 安全写：先写临时文件再 rename
    tmp_path = DATA_JSON + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, DATA_JSON)

    sz = os.path.getsize(DATA_JSON)
    log(f"data.json 写出完成：{sz} 字节")

    # 快速摘要
    xushi_tw = p75.get('休食', {}).get('图文', {})
    log(f"休食 图文 CTR1 P75 = {(xushi_tw.get('ctr1_p75') or 0)*100:.1f}%")
    log(f"Top 案例总条数 = {sum(len(top_cases.get(m, {}).get(f, [])) for m in top_cases for f in ['图文','视频'])}")
    log("DONE")

if __name__ == '__main__':
    main()
