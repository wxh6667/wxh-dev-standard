#!/bin/bash
# Claude Code 状态栏:左=目录 | 模型 ⎇ 分支,右=context 用量进度条(绿 <50% / 黄 50-79% / 红 ≥80%)
# 右对齐依据:Claude Code 运行脚本前会把终端宽度写入 COLUMNS(官方文档说明)
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty')
dir=$(echo "$input" | jq -r '.workspace.current_dir // .current_dir // empty')
base=$(basename "$dir" 2>/dev/null)
branch=$(cd "$dir" 2>/dev/null && git --no-optional-locks branch --show-current 2>/dev/null)

# Context 用量:10 格进度条,官方字段已算好百分比
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /▓}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

if [ "$PCT" -ge 80 ]; then COLOR='\033[31m'
elif [ "$PCT" -ge 50 ]; then COLOR='\033[33m'
else COLOR='\033[32m'
fi
CTX=$(printf '%b%s %s\033[0m' "$COLOR" "$BAR" "$PCT%")

# 可见宽度:CJK 等全角字符实际占 2 列,补偿 bash ${#} 的字符计数
vis_len() {
  local s=$1 cjk=0
  cjk=$(printf '%s' "$s" | grep -oP '[\p{Han}\p{Hangul}\p{Katakana}\p{Hiragana}\x{3000}-\x{303F}\x{FF01}-\x{FF60}]' 2>/dev/null | wc -l)
  echo $(( ${#s} + cjk ))
}

if [ -n "$branch" ]; then
  LEFT="$base | $model ⎇ $branch"
else
  LEFT="$base | $model"
fi
RIGHT_PLAIN="$BAR $PCT%"

COLS="${COLUMNS:-100}"
# 系统通知/verbose 计数器临时出现在行右侧,会短暂挤占宽度;平时为空。
# RESERVE 只留小缓冲保证平时贴右;若通知出现时容忍截断可保持,反之调大
RESERVE=3
pad=$(( COLS - $(vis_len "$LEFT") - ${#RIGHT_PLAIN} - 1 - RESERVE ))
[ "$pad" -lt 1 ] && pad=1

printf '%s%*s%s' "$LEFT" "$pad" '' "$CTX"
