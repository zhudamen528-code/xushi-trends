#!/bin/bash
# 每周一 09:00 自动刷新 xushi-trends V10 看板
set -e
export TZ='Asia/Shanghai'
WORK="/home/node/.openclaw/workspace/xushi-trends-cron/work"
DEPLOY_KEY="/home/node/.openclaw/workspace/xushi-trends-cron/deploy_key"
LOG="$WORK/refresh_v10_$(date +%Y%m%d).log"

exec >> "$LOG" 2>&1
echo "===== V10 周更开始 $(date) ====="

cd "$WORK"

# 当前 MVP：复用现有数据 + build；下版本接 SQL/subagent 全自动化
echo "[1] 当前 MVP：复用 data/v10_clusters/*.diff.json + data.json"

echo "[2] build HTML（build_v10.py 会先调 build_v9.py 再注入 V10 section）"
python3 build_v10.py

echo "[3] git push"
git add -A
git commit -m "V10 weekly refresh $(date +%Y-%m-%d)" || echo "no changes"
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o StrictHostKeyChecking=no" git push

COMMIT=$(git rev-parse --short HEAD)
SIZE=$(stat -c%s index.html)
HC=$(grep -c 'v10-card-high' index.html)
LC=$(grep -c 'v10-card-low' index.html)
echo "===== V10 周更摘要 $(date) ====="
echo "✅ commit: $COMMIT"
echo "✅ index.html: $SIZE bytes"
echo "✅ V10 高组卡: $HC / 低组卡: $LC"
echo "✅ 看板地址: https://zhudamen528-code.github.io/xushi-trends/"
echo "===== 完成 ====="
