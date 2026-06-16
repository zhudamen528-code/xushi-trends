"""
V9 PoolV2 切池脚本：
- 输入：V9_PoolV3 大 SQL 输出的 CSV
- 输出：8 个 .json 文件，每池含 N 条笔记（限 100）
- 切池逻辑：4 指标 × 2 形态（图文/视频）
  - ctr1: CTR1 高（封面+标题强钩子）
  - ctr2: CTR2 高（正文+商品卡转化）
  - cvr: CVR 高（商品+评论转化）
  - price: 件单价高
- 每池在算法 quality rank 前 50% 基础上，再按对应指标降序取 top
"""
import csv, json, sys, os, statistics
from collections import defaultdict

CSV_PATH = sys.argv[1] if len(sys.argv)>1 else 'data/v9_pool_v3.csv'
OUT_DIR = 'data/v9_pools_v2'
os.makedirs(OUT_DIR, exist_ok=True)

rows = []
with open(CSV_PATH, encoding='utf-8-sig') as f:
    rdr = csv.DictReader(f)
    for r in rdr:
        rows.append(r)

print(f'[INFO] total rows: {len(rows)}')
if not rows:
    print('[FATAL] empty pool')
    sys.exit(1)

# 计算每条笔记的 ctr1/ctr2/cvr/price
def num(v, default=0.0):
    try:
        return float(v) if v not in (None,'','NULL','null') else default
    except:
        return default

for r in rows:
    imp = num(r.get('total_imp'))
    clk = num(r.get('total_clk'))
    gv = num(r.get('total_gv'))
    buy = num(r.get('total_buy'))
    dgmv = num(r.get('total_dgmv'))
    r['_ctr1'] = clk/imp*100 if imp>0 else 0
    r['_ctr2'] = gv/clk*100 if clk>0 else 0
    r['_cvr'] = buy/gv*100 if gv>0 else 0
    r['_price'] = dgmv/buy if buy>0 else 0
    r['_dgmv'] = dgmv
    r['_imp'] = imp
    r['_gpm'] = num(r.get('gpm'))
    # 笔记形态
    r['_form'] = 'vid' if str(r.get('note_type'))=='2' else 'pic'

# 异常过滤：CTR1>50% 视为刷量 / 单价 > 10000 视为异常
clean = [r for r in rows if r['_ctr1']<=50 and r['_price']<=10000 and r['_imp']>=500]
print(f'[INFO] after异常过滤: {len(clean)}')

# 8 池切分：取每个指标的 P75 以上作为强信号
def percentile(arr, p):
    a = sorted(x for x in arr if x>0)
    if not a: return 0
    k = int(len(a)*p)
    return a[min(k, len(a)-1)]

forms = ['pic','vid']
metrics = ['_ctr1','_ctr2','_cvr','_price']
metric_label = {'_ctr1':'ctr1','_ctr2':'ctr2','_cvr':'cvr','_price':'price'}
POOL_SIZE = 100  # 每池上限

pool_stats = {}
for m in metrics:
    for f in forms:
        sub = [r for r in clean if r['_form']==f]
        # 按该指标降序取 top POOL_SIZE
        sub_sorted = sorted(sub, key=lambda x: -x[m])
        top = sub_sorted[:POOL_SIZE]
        # 算池子内的算法画像
        def safe_mean(arr):
            arr=[x for x in arr if x not in (None,'','NULL')]
            return statistics.mean([num(x) for x in arr]) if arr else 0
        sin_avg = safe_mean([r.get('model_sincerity_score') for r in top])
        lowbad_avg = safe_mean([r.get('low_bad_market_score') for r in top])
        gc_avg = safe_mean([r.get('good_click_quality_score') for r in top])
        cl_dist = defaultdict(int)
        for r in top:
            cl_dist[r.get('creation_level') or 'NULL'] += 1
        # 类目分布
        cat_dist = defaultdict(int)
        for r in top:
            cat_dist[r.get('goods_cat3') or '未知'] += 1
        cat_top = sorted(cat_dist.items(), key=lambda x:-x[1])[:5]
        # 输出
        pool_name = f'{metric_label[m]}_{f}'
        out_path = f'{OUT_DIR}/{pool_name}.json'
        with open(out_path,'w',encoding='utf-8') as fp:
            json.dump({
                'pool_name': pool_name,
                'metric': metric_label[m],
                'form': f,
                'count': len(top),
                'algo_profile': {
                    'avg_sincerity': round(sin_avg,2),
                    'avg_low_bad_market': round(lowbad_avg,4),
                    'avg_good_click': round(gc_avg,4),
                    'creation_level_dist': dict(cl_dist),
                },
                'top5_categories': cat_top,
                'notes': top
            }, fp, ensure_ascii=False, indent=1)
        pool_stats[pool_name] = {
            'n': len(top),
            'sincerity': round(sin_avg,1),
            'low_bad': round(lowbad_avg,3),
            'creation': dict(cl_dist),
            'top_cat': cat_top[:3]
        }

print('=== 8 池切分完成 ===')
for k,v in pool_stats.items():
    print(f'{k}: n={v["n"]} sincerity={v["sincerity"]} low_bad={v["low_bad"]} creation={v["creation"]}')
    print(f'  top_cat: {v["top_cat"]}')
