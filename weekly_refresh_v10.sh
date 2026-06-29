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

# ─── 步骤1：fetch 最新数据（P75 + Top 案例 V3）───────────────────────────────
echo ""
echo "[1/5] 拉取最新数据（fetch_data.py，P75 + 算法分门槛 Top 50）"
# 记录 fetch 前的 data.json mtime，用于判断是否真的更新了
DATA_MTIME_BEFORE=$(stat -c %Y "$WORK/data.json" 2>/dev/null || echo 0)

if python3 fetch_data.py; then
    DATA_MTIME_AFTER=$(stat -c %Y "$WORK/data.json" 2>/dev/null || echo 0)
    if [ "$DATA_MTIME_AFTER" -le "$DATA_MTIME_BEFORE" ]; then
        echo "  ❌ fetch_data.py 返回成功但 data.json 未更新"
        exit 1
    fi
    # 验证 data.json 里的 window 是本周/上周窗口（end_dtm 应≥7天内）
    DATA_END=$(python3 -c "import json; d=json.load(open('$WORK/data.json')); w=d.get('window',{}); print(w.get('end_dtm','') if isinstance(w,dict) else (w[1] if w else ''))" 2>/dev/null)
    DATA_END_TS=$(date -d "${DATA_END:0:4}-${DATA_END:4:2}-${DATA_END:6:2}" +%s 2>/dev/null || echo 0)
    NOW_TS=$(TZ='Asia/Shanghai' date +%s)
    AGE_DAYS=$(( (NOW_TS - DATA_END_TS) / 86400 ))
    if [ "$AGE_DAYS" -gt 7 ]; then
        echo "  ❌ data.json end_dtm=$DATA_END，超过7天（age=${AGE_DAYS}d），fetch 实际未拿到新数据"
        exit 1
    fi
    echo "  ✅ data.json 已刷新到 $DATA_END（age=${AGE_DAYS}d）"
else
    echo "  ❌ fetch_data.py 执行失败，终止本次周更（不要用旧数据假更新）"
    exit 1
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
