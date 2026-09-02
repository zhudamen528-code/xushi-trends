#!/usr/bin/env python3
"""
方法论卡案例换新：保留 6 月结论，把每条卡底下的 high_examples 换成 8 月新笔记
- 案例来源：data/v10_pool_refresh.csv（8/05~9/01 池子，823 条）
- 每条规律用对应匹配规则筛候选，按该指标值降序取前 N 条
- 同步把新案例写入 title_to_noteid.json，保证跳转链可用
"""
import os, re, json, csv, shutil
from datetime import datetime, timezone, timedelta

WORKDIR = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
CDIR = os.path.join(WORKDIR, 'data', 'v10_clusters')
CN = timezone(timedelta(hours=8))

def log(m): print(m, flush=True)

def _f(v):
    try: return float(v)
    except (TypeError, ValueError): return None

rows = list(csv.DictReader(open(os.path.join(WORKDIR,'data/v10_pool_refresh.csv'), encoding='utf-8')))
log(f'8月池子：{len(rows)} 条')

def ctr1(r):
    imp, clk = _f(r.get('total_imp')), _f(r.get('total_clk'))
    return clk/imp if imp and clk is not None and imp>0 else None
def ctr2(r):
    clk, gv = _f(r.get('total_clk')), _f(r.get('total_gv'))
    return gv/clk if clk and gv is not None and clk>0 else None
def cvr(r):
    gv, buy = _f(r.get('total_gv')), _f(r.get('total_buy'))
    return buy/gv if gv and buy is not None and gv>0 else None
def ppi(r):
    dg, buy = _f(r.get('total_dgmv')), _f(r.get('total_buy'))
    return dg/buy if buy and dg is not None and buy>0 else None

METRIC_FN = {'ctr1':ctr1,'ctr2':ctr2,'cvr':cvr,'price':ppi}

def title_of(r): return (r.get('title') or '').strip()
def cat_of(r):   return (r.get('taxonomy2') or r.get('taxonomy1') or '未分类').strip()

# ── 每条规律的匹配规则（key = cluster_name 的稳定子串）────────────────────
def m_cover_low(r):
    return (r.get('first_img_aesthetic_level') or '') == '低'
def m_bracket(r):
    return bool(re.search(r'[《》「」“”\'\'()（）]', title_of(r)))
def m_bignum(r):
    t = title_of(r)
    return bool(re.search(r'\d+\s*(元|r\b|R\b|¥|块|万|w\b|W\b|单|斤|盒|箱)', t)) or bool(re.search(r'\d{3,}', t))
def m_first_person_num(r):
    t = title_of(r)
    return bool(re.search(r'我|自家|咱', t)) and bool(re.search(r'\d', t))

RULES = {
    '封面美学=低':      ('ctr1', m_cover_low),
    '书名号':           ('ctr1', m_bracket),
    '具体价格':         ('ctr1', m_bignum),
    '第一人称+具体数字': ('ctr1', m_first_person_num),
}

# 休食看板只展示食品相关类目的案例
FOOD_CATS_OK = ('美食', '养生食疗', '保健品', '零食', '饮品', '茶', '酒')

def is_food_cat(c):
    return any(k in c for k in FOOD_CATS_OK)

def pick(rule_fn, metric_key, n=5, exclude=()):
    fn = METRIC_FN[metric_key]
    cands = []
    for r in rows:
        t = title_of(r)
        nid = (r.get('note_id') or '').strip()
        if not t or not nid or nid in exclude:
            continue
        if len(t) < 6:
            continue
        if not is_food_cat(cat_of(r)):
            continue
        v = fn(r)
        if v is None:
            continue
        if not rule_fn(r):
            continue
        cands.append((v, t, cat_of(r), nid))
    # 同标题去重，按指标降序
    seen, out = set(), []
    for v, t, c, nid in sorted(cands, key=lambda x: -x[0]):
        if t in seen: continue
        seen.add(t)
        out.append((v, t, c, nid))
        if len(out) >= n: break
    return out

# ── 执行替换 ──────────────────────────────────────────────────────────────
diff_path = os.path.join(CDIR, 'ctr1.diff.json')
shutil.copy(diff_path, diff_path + '.bak_20260902')
log(f'已备份：{os.path.basename(diff_path)}.bak_20260902')

d = json.load(open(diff_path, encoding='utf-8'))
idx_path = os.path.join(CDIR, 'title_to_noteid.json')
TITLE_IDX = json.load(open(idx_path, encoding='utf-8'))
shutil.copy(idx_path, idx_path + '.bak_20260902')

used_ids = set()
changed = 0
for p in d.get('high_only_patterns', []):
    cname = p.get('cluster_name','')
    hit = None
    for kw, (mk, fn) in RULES.items():
        if kw in cname:
            hit = (kw, mk, fn); break
    if not hit:
        log(f'⏭  未匹配规则，跳过：{cname[:40]}')
        continue
    kw, mk, fn = hit
    want = len(p.get('high_examples', [])) or 5
    picks = pick(fn, mk, n=want, exclude=used_ids)
    if len(picks) < 2:
        log(f'⚠️  候选不足（{len(picks)} 条），保留原案例：{cname[:40]}')
        continue

    new_ex = []
    for v, t, c, nid in picks:
        new_ex.append(f'[{c}] {t}')
        TITLE_IDX[t] = nid          # 关键：写索引才有跳转链
        used_ids.add(nid)
    p['high_examples'] = new_ex
    p['examples_window'] = '20260805~20260901'
    changed += 1
    log(f'✅ {cname[:38]}')
    log(f'   {want} → {len(new_ex)} 条新案例（{mk} 降序）')
    for v, t, c, nid in picks:
        log(f'     {v:.4f} [{c}] {t[:34]}')

json.dump(d, open(diff_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
json.dump(TITLE_IDX, open(idx_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
log(f'\n✅ 已替换 {changed} 条卡的案例')
log(f'   title_to_noteid.json 现有 {len(TITLE_IDX)} 条映射')
