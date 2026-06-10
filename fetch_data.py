#!/usr/bin/env python3
# fetch_data.py - 拉 P50/P75 + TOP 案例 + Claude 亮点分析，生成 data.json
import subprocess, json, time, sys, os
from datetime import datetime, timedelta
TZ_OFFSET = timedelta(hours=8)

WORKDIR = '/home/node/.openclaw/workspace/xushi-trends-cron/work'
DATA_JSON = os.path.join(WORKDIR, 'data.json')

def cn_now():
    return datetime.utcnow() + TZ_OFFSET

def log(msg):
    print(f"[{cn_now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def submit_sql(sql):
    """提交 SQL，返回 msgId"""
    res = subprocess.run(
        ['dp', 'dataverse', 'sql', 'submit', '--code', sql, '--language', 'HiveSQL'],
        capture_output=True, text=True, cwd=WORKDIR
    )
    out = res.stdout + res.stderr
    for line in out.split('\n'):
        if 'msgId:' in line:
            return line.split('msgId:')[1].strip()
    raise RuntimeError(f"submit failed: {out}")

def wait_finish(msg_id, max_min=15):
    """轮询到 FINISHED"""
    deadline = time.time() + max_min * 60
    while time.time() < deadline:
        res = subprocess.run(
            ['dp', 'dataverse', 'sql', 'status', '--msg-id', msg_id],
            capture_output=True, text=True
        )
        out = res.stdout + res.stderr
        if 'FINISHED' in out or 'SUCCESS' in out.upper():
            return True
        if 'FAILED' in out or 'ERROR' in out.upper():
            raise RuntimeError(f"SQL failed: {out[:500]}")
        log(f"  ... waiting msgId={msg_id[:8]}")
        time.sleep(30)
    raise TimeoutError(f"SQL timeout after {max_min}min")

def get_result(msg_id):
    """获取结果 JSON"""
    res = subprocess.run(
        ['dp', 'dataverse', 'sql', 'result', '--msg-id', msg_id, '--raw'],
        capture_output=True, text=True
    )
    return res.stdout

# --- main ---
def main():
    end = cn_now() - timedelta(days=1)
    start = end - timedelta(days=27)
    end_dtm = end.strftime('%Y%m%d')
    start_dtm = start.strftime('%Y%m%d')
    log(f"Window: {start_dtm} → {end_dtm}")

    # 1. P75 SQL
    with open(os.path.join(WORKDIR, 'fetch_p75.sql')) as f:
        sql_p75 = f.read().format(start_dtm=start_dtm, end_dtm=end_dtm)
    log("Submitting P75 SQL...")
    msg = submit_sql(sql_p75)
    log(f"P75 msgId: {msg}")
    wait_finish(msg, max_min=20)
    raw = get_result(msg)
    log(f"P75 result length: {len(raw)}")

    # 持久化原始结果（人工排错用）
    with open(os.path.join(WORKDIR, 'last_p75_raw.json'), 'w') as f:
        f.write(raw)

    # 2. TODO: TOP 案例 SQL（等 subagent 给出 SQL 后补）
    # 3. TODO: Claude 亮点分析
    # 4. 解析并写 data.json
    log("DONE step 1 (P75)")

if __name__ == '__main__':
    main()
