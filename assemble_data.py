#!/usr/bin/env python3
"""把已有 P75 数据 + TOP 案例数据组装成 data.json"""
import json, os
from datetime import datetime

# P75 数据（来自之前 SQL 结果，硬编码）
P75_RAW = [
    {"seller_industry":"亲子生活","note_form":"图文","note_cnt":517036,"ctr1_p50":0.0690,"ctr1_p75":0.1002,"ctr2_p50":None,"ctr2_p75":0.3933,"cvr_p50":0.0000,"cvr_p75":0.0286,"price_p50":33.0,"price_p75":67.91},
    {"seller_industry":"亲子生活","note_form":"视频","note_cnt":328803,"ctr1_p50":0.0455,"ctr1_p75":0.0737,"ctr2_p50":0.0395,"ctr2_p75":0.1216,"cvr_p50":0.0000,"cvr_p75":0.0000,"price_p50":36.9,"price_p75":69.9},
    {"seller_industry":"休食","note_form":"图文","note_cnt":911459,"ctr1_p50":0.0678,"ctr1_p75":0.1014,"ctr2_p50":None,"ctr2_p75":0.3556,"cvr_p50":0.0000,"cvr_p75":0.0625,"price_p50":25.33,"price_p75":46.0},
    {"seller_industry":"休食","note_form":"视频","note_cnt":532385,"ctr1_p50":0.0472,"ctr1_p75":0.0766,"ctr2_p50":0.0286,"ctr2_p75":0.0893,"cvr_p50":0.0000,"cvr_p75":0.0769,"price_p50":24.3,"price_p75":41.46},
    {"seller_industry":"大健康","note_form":"图文","note_cnt":300937,"ctr1_p50":0.0714,"ctr1_p75":0.1120,"ctr2_p50":0.1429,"ctr2_p75":0.2571,"cvr_p50":0.0000,"cvr_p75":0.0625,"price_p50":49.9,"price_p75":74.8},
    {"seller_industry":"大健康","note_form":"视频","note_cnt":77915,"ctr1_p50":0.0523,"ctr1_p75":0.0897,"ctr2_p50":None,"ctr2_p75":0.1429,"cvr_p50":0.0000,"cvr_p75":0.0061,"price_p50":55.51,"price_p75":118.57},
    {"seller_industry":"宠物","note_form":"图文","note_cnt":233447,"ctr1_p50":0.0915,"ctr1_p75":0.1412,"ctr2_p50":0.1364,"ctr2_p75":0.2727,"cvr_p50":0.0000,"cvr_p75":0.0690,"price_p50":23.27,"price_p75":39.9},
    {"seller_industry":"宠物","note_form":"视频","note_cnt":162974,"ctr1_p50":0.0563,"ctr1_p75":0.0945,"ctr2_p50":0.0279,"ctr2_p75":0.0868,"cvr_p50":0.0000,"cvr_p75":0.0804,"price_p50":20.42,"price_p75":36.35},
    {"seller_industry":"家用","note_form":"图文","note_cnt":821059,"ctr1_p50":0.0710,"ctr1_p75":0.1065,"ctr2_p50":None,"ctr2_p75":0.3444,"cvr_p50":0.0000,"cvr_p75":0.0423,"price_p50":24.9,"price_p75":44.11},
    {"seller_industry":"家用","note_form":"视频","note_cnt":630166,"ctr1_p50":0.0473,"ctr1_p75":0.0777,"ctr2_p50":0.0351,"ctr2_p75":0.1111,"cvr_p50":0.0000,"cvr_p75":0.0526,"price_p50":21.8,"price_p75":41.9},
    {"seller_industry":"生鲜","note_form":"图文","note_cnt":357392,"ctr1_p50":0.0618,"ctr1_p75":0.0920,"ctr2_p50":None,"ctr2_p75":None,"cvr_p50":0.0000,"cvr_p75":0.0741,"price_p50":27.5,"price_p75":59.8},
    {"seller_industry":"生鲜","note_form":"视频","note_cnt":129113,"ctr1_p50":0.0424,"ctr1_p75":0.0712,"ctr2_p50":0.0308,"ctr2_p75":0.0949,"cvr_p50":0.0000,"cvr_p75":0.0769,"price_p50":32.8,"price_p75":69.9},
]

# 转成嵌套结构
p75 = {}
for r in P75_RAW:
    ind = r['seller_industry']
    form = r['note_form']
    p75.setdefault(ind, {})[form] = {
        'note_cnt': r['note_cnt'],
        'ctr1_p50': r['ctr1_p50'], 'ctr1_p75': r['ctr1_p75'],
        'ctr2_p50': r['ctr2_p50'], 'ctr2_p75': r['ctr2_p75'],
        'cvr_p50': r['cvr_p50'], 'cvr_p75': r['cvr_p75'],
        'price_p50': r['price_p50'], 'price_p75': r['price_p75'],
    }

# 算 KA 快消大盘（6 品类各指标的中位）
import statistics
ka_avg = {'图文':{}, '视频':{}}
for form in ['图文','视频']:
    for key in ['ctr1_p50','ctr1_p75','ctr2_p50','ctr2_p75','cvr_p50','cvr_p75','price_p50','price_p75']:
        vals = [p75[ind][form].get(key) for ind in p75 if p75[ind].get(form, {}).get(key) is not None]
        ka_avg[form][key] = round(statistics.median(vals), 4) if vals else None

# TOP 案例
with open('/home/node/.openclaw/workspace/tmp/top_cases_result.json') as f:
    cases_raw = json.load(f)

# 把 note_form 1/2 转为图文/视频，metric_name AOV→price，组织成嵌套
metric_map = {'CTR1':'ctr1','CTR2':'ctr2','CVR':'cvr','AOV':'price'}
form_map = {1:'图文', 2:'视频'}
top_cases = {'ctr1':{'图文':[],'视频':[]}, 'ctr2':{'图文':[],'视频':[]}, 'cvr':{'图文':[],'视频':[]}, 'price':{'图文':[],'视频':[]}}
for r in cases_raw:
    m = metric_map[r['metric_name']]
    f = form_map[r['note_form']]
    top_cases[m][f].append({
        'rank': r['rank'],
        'note_id': r['note_id'],
        'title': r['title'] or '(无标题)',
        'seller_name': r['seller_name'],
        'value': r['metric_value'],
        'imp': r['imp'], 'click': r['click'], 'buy': r['buy'], 'dgmv': r['dgmv'],
        'note_url': f"https://www.xiaohongshu.com/explore/{r['note_id']}",
        'highlight': None,  # Claude 待补
    })

# 组装最终 data
data = {
    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
    'window': ['2026-05-14', '2026-06-09'],
    'p75': {**p75, 'ka_avg': ka_avg},
    'top_cases': top_cases,
}

with open('data.json','w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"data.json written: {os.path.getsize('data.json')} bytes")
print(f"KA avg 图文 CTR1 P75 = {ka_avg['图文']['ctr1_p75']*100:.1f}%")
print(f"休食 图文 CTR1 P75 = {p75['休食']['图文']['ctr1_p75']*100:.1f}%")
print(f"案例数：CTR1 图文={len(top_cases['ctr1']['图文'])}, CVR 视频={len(top_cases['cvr']['视频'])}")
