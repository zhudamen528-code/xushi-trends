#!/usr/bin/env python3
"""
V10 差分聚类池子重跑（参数化版）
用近 8 周数据重新生成 4 个指标的 high/low 对照组池子

输出：data/v10_clusters/{metric}_high.txt / {metric}_low.txt
之后交给 LLM 做差分聚类，产出 {metric}.diff.json
"""
import os, sys, json, subprocess, time
from datetime import datetime, timedelta, timezone

WORKDIR = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
CLUSTER_DIR = os.path.join(WORKDIR, 'data', 'v10_clusters')
CN = timezone(timedelta(hours=8))

def cn_now():
    return datetime.now(CN)

def log(msg):
    print(f"[{cn_now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# ── 复用 fetch_data.py 的 SQL 提交/轮询 ────────────────────────────────────
sys.path.insert(0, WORKDIR)
import fetch_data as fd


def probe_snap_dtm(end_dtm, lookback=7):
    """探测算法分表最近可用的单日分区（避免 JOIN 空分区导致 0 行）"""
    from datetime import datetime as _dt
    cands = []
    d = _dt.strptime(end_dtm, '%Y%m%d')
    for i in range(lookback):
        cands.append((d - timedelta(days=i)).strftime('%Y%m%d'))
    in_list = ','.join(f"'{c}'" for c in cands)
    sql = (
        "SELECT dtm FROM redapp.app_ecm_ark_ai_note_score_base_nd_di "
        f"WHERE dtm IN ({in_list}) GROUP BY dtm ORDER BY dtm DESC LIMIT 1"
    )
    log(f"探测算法分表可用分区（回看 {lookback} 天）...")
    mid = fd.submit_sql(sql)
    fd.wait_finish(mid, max_min=10, label='ProbeSnap')
    rows = fd.parse_rows(fd.get_result(mid))
    if not rows:
        raise RuntimeError(f"算法分表近 {lookback} 天无可用分区，终止")
    snap = str(rows[0].get('dtm'))
    log(f"算法分/维表快照分区选定：{snap}" + ("（= end_dtm）" if snap == end_dtm else f"（end_dtm={end_dtm} 无数据，已回退）"))
    return snap

def main():
    # 近 8 周窗口（T-1 往前 56 天）
    end = cn_now() - timedelta(days=1)
    start = end - timedelta(days=27)
    end_dtm = end.strftime('%Y%m%d')
    start_dtm = start.strftime('%Y%m%d')

    log(f"聚类池子窗口：{start_dtm} → {end_dtm}（近 4 周·轻量版无评论）")

    snap_dtm = probe_snap_dtm(end_dtm)

    sql_path = os.path.join(WORKDIR, 'v10_pool_refresh_light.sql')
    with open(sql_path) as f:
        sql = f.read().format(start_dtm=start_dtm, end_dtm=end_dtm, snap_dtm=snap_dtm)

    log("提交池子 SQL（预计 15-30 分钟）...")
    msg_id = fd.submit_sql(sql)
    log(f"池子 msgId: {msg_id}")

    fd.wait_finish(msg_id, max_min=90, label='Pool')
    raw = fd.get_result(msg_id)
    raw_path = os.path.join(WORKDIR, 'data', 'v10_pool_refresh_raw.json')
    with open(raw_path, 'w') as f:
        f.write(raw)
    log(f"池子结果 {len(raw)} 字节 → {raw_path}")

    rows = fd.parse_rows(raw)
    log(f"池子行数：{len(rows)}")
    if not rows:
        # 打印原始返回帮助定位（totalSize=0 vs 解析失败）
        log(f"❌ 池子为空，终止。原始返回前 400 字符：\n{raw[:400]}")
        sys.exit(1)
    if len(rows) < 100:
        log(f"⚠️ 池子仅 {len(rows)} 行，样本偏少，分位切组可能不稳；继续但需人工复核")

    # 落 CSV 便于检查
    import csv
    csv_path = os.path.join(WORKDIR, 'data', 'v10_pool_refresh.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log(f"CSV 落盘：{csv_path}")

    build_pools(rows, start_dtm, end_dtm)

def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def build_pools(rows, start_dtm, end_dtm):
    """按类目内分位切高低组，为 4 个指标各生成 high/low txt"""
    import statistics

    # 指标定义：(key, 计算函数, 该指标关注的字段)
    def ctr1(r):
        imp, clk = _f(r.get('total_imp')), _f(r.get('total_clk'))
        return (clk / imp) if imp and clk is not None and imp > 0 else None

    def ctr2(r):
        clk, gv = _f(r.get('total_clk')), _f(r.get('total_gv'))
        return (gv / clk) if clk and gv is not None and clk > 0 else None

    def cvr(r):
        gv, buy = _f(r.get('total_gv')), _f(r.get('total_buy'))
        return (buy / gv) if gv and buy is not None and gv > 0 else None

    def price(r):
        dgmv, buy = _f(r.get('total_dgmv')), _f(r.get('total_buy'))
        return (dgmv / buy) if buy and dgmv is not None and buy > 0 else None

    METRICS = {
        'ctr1':  (ctr1,  ['title', 'cover_aesthetic', 'cover_definition', 'cover_quality']),
        'ctr2':  (ctr2,  ['title', 'goods_name', 'content_snip']),
        'cvr':   (cvr,   ['title', 'asr_snip', 'content_snip']),
        'price': (price, ['title', 'goods_name', 'goods_price', 'content_snip']),
    }

    # 字段名映射（SQL 输出 → txt 里展示的字段名）
    FIELD_ALIAS = {
        'title': '标题',
        'goods_name': '商品名',
        'content_snip': '正文',
        'asr_snip': 'ASR',
        'goods_price': '售价',
        'cover_aesthetic': '封面美学',
        'cover_definition': '封面清晰度',
        'cover_quality': '封面质量',
        'first_img_aesthetic_level': '封面美学',
        'first_img_definition_level': '封面清晰度',
        'first_img_quality_level': '封面质量',
    }

    os.makedirs(CLUSTER_DIR, exist_ok=True)

    for mkey, (calc, fields) in METRICS.items():
        # 算指标值
        enriched = []
        for r in rows:
            v = calc(r)
            if v is None:
                continue
            cat = r.get('taxonomy2') or r.get('taxonomy1') or '未分类'
            enriched.append((cat, v, r))

        if not enriched:
            log(f"⚠️ {mkey}: 无有效数据，跳过")
            continue

        # 类目 × 曝光档 双重分层内切分位
        # 为什么要分曝光档：小曝光笔记天然 CTR 高（实测曝光 Q1 CTR1 中位 9.2% vs Q4 3.4%），
        # 只按类目切会让"高组"退化成"小曝光组"，标题特征差异被曝光这个混淆变量吃掉。
        imps = sorted(_f(r.get('total_imp')) or 0 for _, _, r in enriched)
        n_all = len(imps)
        imp_cuts = [imps[int(n_all * q)] for q in (0.25, 0.5, 0.75)] if n_all >= 8 else []

        def imp_band(r):
            iv = _f(r.get('total_imp')) or 0
            if not imp_cuts:
                return 'all'
            for i, c in enumerate(imp_cuts):
                if iv <= c:
                    return f'B{i}'
            return f'B{len(imp_cuts)}'

        by_strata = {}
        for cat, v, r in enriched:
            by_strata.setdefault((cat, imp_band(r)), []).append((v, r))

        high_rows, low_rows = [], []
        for (cat, band), items in by_strata.items():
            if len(items) < 8:   # 层内样本太少，分位没意义
                continue
            vals = sorted(x[0] for x in items)
            n = len(vals)
            p75 = vals[int(n * 0.75)]
            p25 = vals[int(n * 0.25)]
            for v, r in items:
                if v >= p75:
                    high_rows.append((cat, v, r))
                elif v <= p25:
                    low_rows.append((cat, v, r))

        # 写 txt
        for grp, data in [('high', high_rows), ('low', low_rows)]:
            path = os.path.join(CLUSTER_DIR, f'{mkey}_{grp}.txt')
            with open(path, 'w', encoding='utf-8') as f:
                for cat, v, r in data:
                    nid = r.get('note_id', '')
                    imp = r.get('total_imp', '')
                    head = f"[{nid}|{cat}|{mkey}={v:.4f}|imp={imp}]"
                    parts = []
                    for fld in fields:
                        raw_key = fld
                        # 封面字段在 SQL 里是 first_img_* 命名
                        if fld.startswith('cover_'):
                            raw_key = {'cover_aesthetic': 'first_img_aesthetic_level',
                                       'cover_definition': 'first_img_definition_level',
                                       'cover_quality': 'first_img_quality_level'}[fld]
                        val = r.get(raw_key)
                        if val:
                            alias = FIELD_ALIAS.get(fld, fld)
                            parts.append(f"[{alias}]{str(val)[:300]}")
                    f.write(head + ' ' + ' | '.join(parts) + '\n')
            log(f"{mkey}_{grp}.txt: {len(data)} 条 → {path}")

        # 更新任务定义文件里的窗口说明
        task_path = os.path.join(CLUSTER_DIR, f'{mkey}_task.md')
        if os.path.exists(task_path):
            t = open(task_path, encoding='utf-8').read()
            import re
            t = re.sub(r'（\d+ 条）', f'（见文件实际行数）', t)
            t = f"<!-- 池子窗口：{start_dtm} ~ {end_dtm}（重跑于 {cn_now().strftime('%Y-%m-%d %H:%M')}）-->\n" + \
                re.sub(r'^<!-- 池子窗口：.*?-->\n', '', t, flags=re.S)
            open(task_path, 'w', encoding='utf-8').write(t)

    log("✅ 4 个指标的高低组池子已全部生成")
    log(f"下一步：把 data/v10_clusters/{{metric}}_high.txt / _low.txt 交给 LLM 做差分聚类")

if __name__ == '__main__':
    main()
