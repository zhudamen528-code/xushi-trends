#!/bin/bash
# 每周一 09:00 自动刷新 xushi-trends V8 GPM 看板
set -e
export TZ='Asia/Shanghai'
WORK="/home/node/.openclaw/workspace/xushi-trends-cron/work"
DEPLOY_KEY="/home/node/.openclaw/workspace/xushi-trends-cron/deploy_key"
LOG="$WORK/refresh_v8_$(date +%Y%m%d).log"

exec >> "$LOG" 2>&1
echo "===== 开始 $(date) ====="

cd "$WORK"

# 1. 拉 P75 + TOP 案例 + Claude 亮点 → 重组 data.json
# （TODO: 后续完整版要把 SQL 跑数 + Claude 调用真正自动化）
# 当前 MVP：先复用现有 data.json，仅 build 一次确保最新结构
echo "[1] 当前 MVP：复用 data.json（下版本接全自动化）"

# 2. build
echo "[2] build HTML"
python3 build_v8_gpm.py

# 3. push
echo "[3] git push"
git add -A
git commit -m "auto: weekly refresh $(date +%Y-%m-%d)" || echo "  no changes"
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o StrictHostKeyChecking=no" git push origin main || echo "  push failed"

echo "===== 完成 $(date) ====="
