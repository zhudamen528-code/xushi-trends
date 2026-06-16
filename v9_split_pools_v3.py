"""V9 切池 V3：基于合并后宽表，按 note_type 切 8 池"""
import csv, json, os, statistics
from collections import defaultdict

CSV_PATH='data/v9_pool_merged.csv'
OUT_DIR='data/v9_pools_v3'
os.makedirs(OUT_DIR, exist_ok=True)

def num(v, default=0.0):
    try:
        return float(v) if v not in (None,'','NULL','null') else default
    except: return default

def safe_mean(arr):
    arr=[num(x) for x in arr if x not in (None,'','NULL')]
    return statistics.mean(arr) if arr else 0

rows=list(csv.DictReader(open(CSV_PATH, encoding='utf-8')))
print(f'[INFO] loaded {len(rows)} rows')

# 计算指标
for r in rows:
    imp=num(r.get('total_imp')); clk=num(r.get('total_clk'))
    gv=num(r.get('total_gv')); buy=num(r.get('total_buy'))
    dgmv=num(r.get('total_dgmv'))
    r['_ctr1']=clk/imp*100 if imp>0 else 0
    r['_ctr2']=gv/clk*100 if clk>0 else 0
    r['_cvr']=buy/gv*100 if gv>0 else 0
    r['_price']=dgmv/buy if buy>0 else 0
    r['_gpm']=num(r.get('gpm'))
    r['_dgmv']=dgmv; r['_imp']=imp
    r['_form'] = 'vid' if str(r.get('note_type'))=='2' else 'pic'

# 异常过滤
clean=[r for r in rows if r['_ctr1']<=50 and r['_price']<=10000 and r['_imp']>=500]
print(f'[INFO] clean: {len(clean)}')

# 8 池切分
metrics=[('ctr1','_ctr1'),('ctr2','_ctr2'),('cvr','_cvr'),('price','_price')]
forms=['pic','vid']
POOL_SIZE=100

stats={}
for m_label, m_key in metrics:
    for f in forms:
        sub=[r for r in clean if r['_form']==f]
        sub_sorted=sorted(sub, key=lambda x: -x[m_key])
        top=sub_sorted[:POOL_SIZE]
        if not top: continue
        # 算法画像
        sin=safe_mean([r.get('model_sincerity_score') for r in top])
        lb=safe_mean([r.get('low_bad_market_score') for r in top])
        gc=safe_mean([r.get('good_click_quality_score') for r in top])
        # 创作等级分布
        cl=defaultdict(int)
        for r in top: cl[r.get('creation_level') or 'NULL']+=1
        # 类目分布
        cat=defaultdict(int)
        for r in top: cat[r.get('goods_cat3') or '未知']+=1
        # 商家集中度
        sellers=defaultdict(int)
        for r in top: sellers[r.get('seller_name') or '未知']+=1
        
        pool_name=f'{m_label}_{f}'
        out_path=f'{OUT_DIR}/{pool_name}.json'
        with open(out_path,'w',encoding='utf-8') as fp:
            json.dump({
                'pool_name':pool_name,
                'metric':m_label,'form':f,'count':len(top),
                'algo_profile':{
                    'avg_sincerity':round(sin,2),
                    'avg_low_bad_market':round(lb,4),
                    'avg_good_click':round(gc,4),
                    'creation_level_dist':dict(cl),
                },
                'top10_categories':sorted(cat.items(),key=lambda x:-x[1])[:10],
                'top10_sellers':sorted(sellers.items(),key=lambda x:-x[1])[:10],
                'notes':top
            }, fp, ensure_ascii=False, indent=1)
        stats[pool_name]={
            'n':len(top),'sin':round(sin,1),'lb':round(lb,3),'gc':round(gc,3),
            'top_cat':sorted(cat.items(),key=lambda x:-x[1])[:3]
        }

print('\n=== 8 池切分完成 ===')
for k,v in stats.items():
    print(f'{k}: n={v["n"]} sin={v["sin"]} lb={v["lb"]} gc={v["gc"]} top_cat={v["top_cat"]}')
