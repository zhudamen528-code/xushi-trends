#!/usr/bin/env python3
"""
接力取结果：已提交的池子 SQL 跑完后，直接用 msgId 取结果并切高低组
用法：python3 resume_pool.py <msgId> <start_dtm> <end_dtm>
"""
import os, sys, json, csv
sys.path.insert(0, '/home/node/.openclaw/workspace/xushi-trends-cron/work')
os.chdir('/home/node/.openclaw/workspace/xushi-trends-cron/work')

import fetch_data as fd
import refresh_clusters as rc

def main():
    if len(sys.argv) < 4:
        print("用法: python3 resume_pool.py <msgId> <start_dtm> <end_dtm>")
        sys.exit(1)
    msg_id, start_dtm, end_dtm = sys.argv[1], sys.argv[2], sys.argv[3]

    rc.log(f"接力取结果 msgId={msg_id}")
    # 只等剩余时间，不重新提交
    fd.wait_finish(msg_id, max_min=90, label='PoolResume')

    raw = fd.get_result(msg_id)
    raw_path = 'data/v10_pool_refresh_raw.json'
    with open(raw_path, 'w') as f:
        f.write(raw)
    rc.log(f"池子结果 {len(raw)} 字节 → {raw_path}")

    rows = fd.parse_rows(raw)
    rc.log(f"池子行数：{len(rows)}")
    if not rows:
        rc.log(f"❌ 池子为空。原始返回前 400 字符：\n{raw[:400]}")
        sys.exit(1)
    if len(rows) < 100:
        rc.log(f"⚠️ 池子仅 {len(rows)} 行，样本偏少，分位切组可能不稳")

    with open('data/v10_pool_refresh.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    rc.log("CSV 落盘：data/v10_pool_refresh.csv")

    rc.build_pools(rows, start_dtm, end_dtm)

if __name__ == '__main__':
    main()
