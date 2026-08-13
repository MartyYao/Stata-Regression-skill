#!/usr/bin/env bash
# rerun.sh — 实证 run 版本管理入口（论文产出端）
#
# 解决的问题：output/tables/*.csv 原地覆盖导致旧数字消失、正文追溯无门。
# 核心原则：开新 run 必须走本脚本，旧表归档 + 新 tag 目录 + MAPPING 更新一次完成。
#
# Usage:
#   bash rerun.sh new "20260813_v4"   # 开新 run（tag 格式 YYYYMMDD_vN）
#   bash rerun.sh status              # 当前 tag 与目录状态
#   bash rerun.sh new "20260813_v4" --dir /path/to/working   # 指定工作目录
#
# 之后 do 文件顶部写：global TAG = "20260813_v4"
# 输出路径一律用：output/tables/$TAG/tableNN.csv
set -euo pipefail

TAG_RE='^[0-9]{8}_v[0-9]+$'

die() { echo "ABORT: $*" >&2; exit 1; }

WORKDIR="$(pwd)"
CMD="${1:-}"
[ $# -ge 1 ] && shift

REST=()
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) WORKDIR="${2:?--dir needs a path}"; shift 2 ;;
    -h|--help) sed -n '2,/^$/p' "$0" | head -n 10; exit 0 ;;
    *) REST+=("$1"); shift ;;
  esac
done

set -- ${REST[@]+"${REST[@]}"}

[ -d "$WORKDIR" ] || die "workdir not found: $WORKDIR"

TABLES_DIR="$WORKDIR/output/tables"
ARCHIVE_DIR="$WORKDIR/output/archive"
MAPPING="$WORKDIR/output/MAPPING.md"

current_tag() {
  if [ -f "$MAPPING" ]; then
    grep -m1 '^Current tag:' "$MAPPING" | sed 's/^Current tag: *//'
  fi
}

cmd_status() {
  echo "== workdir: $WORKDIR"
  local tag
  tag="$(current_tag || true)"
  echo "current tag : ${tag:-（无 MAPPING.md 或未设置）}"
  if [ -d "$TABLES_DIR" ]; then
    echo "tables dir  : $TABLES_DIR"
    ls "$TABLES_DIR" | head -20
  else
    echo "tables dir  : （不存在）"
  fi
  [ -f "$MAPPING" ] && echo "MAPPING     : $MAPPING" || echo "MAPPING     : （不存在）"
}

cmd_new() {
  local tag="${1:-}"
  [ -n "$tag" ] || die "usage: rerun.sh new <YYYYMMDD_vN>"
  [[ "$tag" =~ $TAG_RE ]] || die "非法 tag 格式: ${tag}（应为 YYYYMMDD_vN，如 20260813_v4）"

  local old_tag
  old_tag="$(current_tag || true)"
  local new_dir="$TABLES_DIR/$tag"

  if [ -d "$new_dir" ]; then
    die "tag 目录已存在: ${new_dir}（幂等保护，不覆盖）"
  fi

  # 1) 归档散落的旧 CSV（非 tag 目录形式）
  if [ -d "$TABLES_DIR" ]; then
    local loose
    loose=$(find "$TABLES_DIR" -maxdepth 1 -type f -name '*.csv' | head -1 || true)
    if [ -n "$loose" ]; then
      local stamp="${old_tag:-$(date +%Y%m%d_%H%M)}"
      local arch="$ARCHIVE_DIR/tables_$stamp"
      mkdir -p "$ARCHIVE_DIR"
      [ -d "$arch" ] && die "归档目录已存在: ${arch}（先处理，避免覆盖旧归档）"
      mv "$TABLES_DIR" "$arch"
      echo "已归档旧表: $TABLES_DIR -> $arch"
    fi
  fi

  # 2) 建新 tag 目录
  mkdir -p "$new_dir"
  echo "已创建: $new_dir"

  # 3) 更新 MAPPING.md（保留既有映射表，只更新头部）
  mkdir -p "$WORKDIR/output"
  if [ -f "$MAPPING" ]; then
    if grep -q '^Current tag:' "$MAPPING"; then
      sed -i.bak \
        -e "s|^Current tag:.*|Current tag: $tag|" \
        -e "s|^Previous tag:.*|Previous tag: ${old_tag:-（无）}|" \
        "$MAPPING"
      rm -f "$MAPPING.bak"
    else
      # MAPPING 存在但头部缺失（手工创建？）——插入头部，不覆盖映射表
      {
        printf '# MAPPING — 表号 ↔ CSV ↔ do 段落 ↔ log ↔ 样本口径\n'
        printf '# 由 rerun.sh 维护头部，映射表手工/随跑追加。\n\n'
        printf 'Current tag: %s\n' "$tag"
        printf 'Started: %s\n' "$(date '+%Y-%m-%d %H:%M')"
        printf 'Previous tag: %s\n\n' "${old_tag:-（无）}"
        cat "$MAPPING"
      } > "$MAPPING.tmp" && mv "$MAPPING.tmp" "$MAPPING"
    fi
  else
    cat > "$MAPPING" <<EOF
# MAPPING — 表号 ↔ CSV ↔ do 段落 ↔ log ↔ 样本口径
# 由 rerun.sh 维护头部，映射表手工/随跑追加。

Current tag: $tag
Started: $(date '+%Y-%m-%d %H:%M')
Previous tag: ${old_tag:-（无）}

| 表号 | CSV 文件 | do 段落 | log | 样本口径 | 备注 |
|------|---------|---------|-----|---------|------|
EOF
  fi
  echo "已更新: $MAPPING"

  # 4) 提示
  cat <<EOF

✅ 新 run 已开启: $tag
下一步：
  1. do 文件顶部写:  global TAG = "$tag"
  2. 输出路径一律用:  output/tables/\$TAG/tableNN.csv
  3. 跑完后在 MAPPING.md 追加映射行，log 存 logs/$tag/
EOF
}

case "$CMD" in
  new)    cmd_new "$@" ;;
  status) cmd_status ;;
  *) die "usage: rerun.sh <new|status> [--dir <path>]" ;;
esac
