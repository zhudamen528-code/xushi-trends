#!/bin/bash
# weekly_refresh_v10.sh - 每周一 09:00 自动刷新 xushi-trends V10 看板
# 流程：fetch 新数据 → gen_cat_trends → build → push → 通知
set -euo pipefail
export TZ='Asia/Shanghai'

WORK="/home/node/.openclaw/workspace/xushi-trends-cron/work"
DEPLOY_KEY="/home/node/.openclaw/workspace/xushi-trends-cron/deploy_key"
LOG="$WORK/refresh_v10_$(TZ='Asia/Shanghai' date +%Y%m%d).log"

exec >> "$LOG" 2>&1
echo "===== V10 周更开始 $(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S') ====="

cd "$WORK"

# ─── 步骤1：fetch 最新 Top 案例数据 ─────────────────────────────────────────
echo ""
echo "[1/5] 拉取最新 Top 案例（fetch_data.py）"
# fetch_data.py 目前只跑 P75，Top 案例 SQL 待接入（V3 SQL 已写好，等接口稳定后补）
# 当前 MVP：检查 data.json 是否存在，有则跳过 fetch
if [ -f "$WORK/data.json" ]; then
    DATA_AGE=$(( ( $(TZ='Asia/Shanghai' date +%s) - $(stat -c %Y "$WORK/data.json") ) / 86400 ))
    echo "  data.json 存在，已有 ${DATA_AGE} 天，跳过重新 fetch（接入 V3 SQL 后改为每次强制刷新）"
else
    echo "  data.json 不存在，尝试运行 fetch_data.py"
    python3 fetch_data.py || echo "  ⚠️ fetch_data.py 失败，继续用现有数据 build"
fi

# ─── 步骤2：生成最新 CAT_TRENDS（品类风向文案）────────────────────────────────
echo ""
echo "[2/5] 生成品类风向文案（gen_cat_trends.py）"
if python3 gen_cat_trends.py; then
    echo "  ✅ cat_trends_generated.js 已更新"
else
    echo "  ⚠️ gen_cat_trends.py 失败，build 将使用 backup 兜底"
fi

# ─── 步骤3：build HTML ────────────────────────────────────────────────────────
echo ""
echo "[3/5] 生成 index.html（build_v10.py）"
python3 build_v10.py

# 自检：关键 JS 函数是否存在
echo "  自检关键函数..."
MISSING=0
for FUNC in "getFormData" "CAT_TRENDS" "buildPrompt" "TITLE_FORMULAS"; do
    if grep -q "$FUNC" index.html; then
        echo "    ✅ $FUNC"
    else
        echo "    ❌ $FUNC 缺失！"
        MISSING=1
    fi
done
if [ "$MISSING" -eq 1 ]; then
    echo "  ❌ 关键函数缺失，终止推送"
    exit 1
fi

# ─── 步骤4：配色周轮换（按周号换主题色）──────────────────────────────────────
echo ""
echo "[4/5] 配色周轮换"
WEEK_NUM=$(TZ='Asia/Shanghai' date +%V | sed 's/^0//')
# 7 色调色板：蓝/绿/橙/紫/红/青/棕
COLORS=("#2563eb" "#16a34a" "#ea580c" "#7c3aed" "#dc2626" "#0891b2" "#92400e")
COLOR_IDX=$(( ($WEEK_NUM - 1) % 7 ))
THEME_COLOR="${COLORS[$COLOR_IDX]}"
echo "  第 $WEEK_NUM 周，主题色 $THEME_COLOR"

# 在 index.html 里替换主题色 CSS 变量（--theme-color 或 #2563eb 第一处）
# 只替换 :root 里的主题色变量，避免误改内容
if grep -q '\-\-theme-color' index.html; then
    sed -i "s/--theme-color:[^;]*/--theme-color: $THEME_COLOR/" index.html
    echo "  ✅ 主题色已更新（--theme-color）"
else
    echo "  ℹ️ 未找到 --theme-color 变量，跳过配色轮换"
fi

# ─── 步骤5：git push ──────────────────────────────────────────────────────────
echo ""
echo "[5/5] git push"
git add -A
COMMIT_MSG="V10 周更 $(TZ='Asia/Shanghai' date '+%Y-%m-%d')（主题色 $THEME_COLOR，第 $WEEK_NUM 周）"
git commit -m "$COMMIT_MSG" || echo "  没有变更，跳过 commit"
GIT_SSH_COMMAND="ssh -i $DEPLOY_KEY -o StrictHostKeyChecking=no" git push origin main
echo "  ✅ push 完成"

# ─── 完成 ─────────────────────────────────────────────────────────────────────
echo ""
echo "===== V10 周更完成 $(TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S') ====="
echo "  线上：https://zhudamen528-code.github.io/xushi-trends/"
