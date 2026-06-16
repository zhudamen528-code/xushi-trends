#!/bin/bash
# V9 周更脚本（先版：只 rebuild + push 当前 V9 数据，自动取数+聚类下版本接）
# 每周一 09:00 触发
set -e
export TZ='Asia/Shanghai'
WORK="/home/node/.openclaw/workspace/xushi-trends-cron/work"
DEPLOY_KEY="/home/node/.openclaw/workspace/xushi-trends-cron/deploy_key"
LOG="$WORK/refresh_v9_$(date +%Y%m%d).log"

exec >> "$LOG" 2>&1
echo "===== V9 周更开始 $(date) ====="

cd "$WORK"

# 1. 验证 V9 数据完整（8 池 cluster + pool 数据齐全）
echo "[1] 检查 V9 数据完整性"
MISSING=0
for p in ctr1_pic ctr1_vid ctr2_pic ctr2_vid cvr_pic cvr_vid price_pic price_vid; do
  CLUSTER="data/v9_clusters_v3/${p}.cluster.json"
  POOL="data/v9_pools_v3/${p}.json"
  if [ ! -f "$CLUSTER" ] || [ ! -f "$POOL" ]; then
    echo "  ❌ 缺失 $p 数据"
    MISSING=$((MISSING+1))
  fi
done
if [ $MISSING -gt 0 ]; then
  echo "  ⚠️ V9 数据缺失 $MISSING 个池，跳过 build（用户需手动更新数据）"
  exit 1
fi
echo "  ✅ 8 池 V9 数据完整"

# 2. build V9 HTML
echo "[2] build V9 HTML"
python3 build_v9.py 2>&1 | tail -15

# 3. push to GitHub
echo "[3] git push"
git add index.html
git -c user.email='zhujincheng@xiaohongshu.com' -c user.name='zhujincheng' \
  commit -m "auto V9 refresh $(date +%Y-%m-%d)" 2>&1 || echo "  no changes"
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o StrictHostKeyChecking=no" \
  git push origin main 2>&1 || echo "  push failed"

# 4. 输出摘要
echo ""
echo "===== V9 周更摘要 $(date) ====="
COMMIT=$(git log -1 --format='%h')
SIZE=$(wc -c < index.html)
N_METHODS=$(grep -c 'class="method-card-v2"' index.html)
echo "✅ commit: $COMMIT"
echo "✅ index.html: $SIZE bytes"
echo "✅ V9 方法卡: $N_METHODS / 40"
echo "✅ 看板地址: https://zhudamen528-code.github.io/xushi-trends/"
echo "===== 完成 ====="
