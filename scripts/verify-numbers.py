#!/usr/bin/env python3
"""verify-numbers.py — 正文表格数字 vs 实证 CSV 自动对账（论文消费端）

解决的问题：正文实证数字与最终采用版本对不上、追溯无门。本脚本把
"正文数字必须能追溯到 CSV"从人肉 grep 变成机器检查。

Usage:
    python3 verify-numbers.py <正文md> --tables output/tables/<tag>/
    python3 verify-numbers.py <正文md> --tables output/tables/<tag>/ --verbose
    python3 verify-numbers.py <正文md> --tables output/tables/<tag>/ --state-line

逻辑：
  1. 提取正文 markdown 表格块（连续 | 行），按"表 N"标题分组
  2. 提取单元格数字：小数 / 大整数 / 百分数 / 括号 t 值 / 星号列
  3. 读取 --tables 目录全部 CSV 的数值 token（剥离 esttab 的 \\^ 转义）
  4. 对账：正文数字在 CSV 数字集中找不到 → 输出未匹配清单
  5. --state-line：校验正文头部 `> 版本：<tag>` 能映射到真实 tag 目录

退出码：有未匹配数字 → 1（准入审查用）；--ignore-unmatched 放行。

局限（设计使然）：
  - 描述统计/正文自行计算的数字不在 CSV → 会列入未匹配，须人工解释出处
  - 对账是"抓明显对不上"，不是完备证明
  - 小数位差异（3 位 vs 4 位）不自动放行，用 --verbose 明细人工判断
  - 设计取舍：2 位整数（如 N=42）、裸 0、科学计数法（e-notation）不参与对账
    （esttab fmt(4) 输出不产生 e-notation，2 位整数多为计数类，两侧都不查）
"""

import argparse
import csv
import os
import re
import sys

# ── 正文数字提取 ──────────────────────────────────────────────

# 表标题：支持 "## 表 5 xxx" / "**表 5 xxx**" / "表 5 xxx"
TABLE_HEAD_RE = re.compile(r"^(?:#{1,6}\s*|\*{1,2}\s*)?(表\s*\d+[^\n*]*)")
TABLE_ROW_RE = re.compile(r"^\|.*\|\s*$")

# 数字 token 提取：小数 / 整数(≥3位) / 百分数；括号 t 值单独成类
NUM_RE = re.compile(
    r"(-?\d{1,3}(?:,\d{3})*\.\d+|-?\d{3,}(?:,\d{3})*|\d+(?:\.\d+)?%)"
)
SE_RE = re.compile(r"\((-?\d+\.\d+)\)")
STAR_RE = re.compile(r"\*\*\*|\*\*|\*")


def norm_num(s: str) -> str:
    """归一化数字：去千分位逗号、去百分号。'1,234.5' -> '1234.5'"""
    return s.replace(",", "").replace("%", "").strip()


def extract_tables(text: str):
    """返回 [(表号, [(行号, 单元格文本, [数字], [SE], [星号]), ...]), ...]"""
    lines = text.splitlines()
    tables = []
    cur_title = None
    cur_rows = []

    def flush():
        if cur_rows:
            tables.append((cur_title, cur_rows))

    for i, line in enumerate(lines, 1):
        m = TABLE_HEAD_RE.match(line)
        if m:
            flush()
            cur_title = m.group(1).strip()
            cur_rows = []
            continue
        if TABLE_ROW_RE.match(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            nums = [norm_num(x) for x in NUM_RE.findall(line)]
            ses = [norm_num(x) for x in SE_RE.findall(line)]
            stars = STAR_RE.findall(line)
            cur_rows.append((i, cells, nums, ses, stars))
        elif cur_rows:
            flush()
            cur_title = None
            cur_rows = []
    flush()
    return tables


# ── CSV 数字集 ────────────────────────────────────────────────

def load_csv_numbers(tables_dir: str) -> set:
    """读取目录下全部 CSV 的数值 token（含括号 SE），返回归一化集合。"""
    nums = set()
    if not os.path.isdir(tables_dir):
        print(f"❌ tables 目录不存在: {tables_dir}", file=sys.stderr)
        sys.exit(2)
    for fn in sorted(os.listdir(tables_dir)):
        if not fn.lower().endswith(".csv"):
            continue
        path = os.path.join(tables_dir, fn)
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for row in csv.reader(f):
                    for cell in row:
                        cell = cell.replace(r"\^", "").strip()
                        if not cell:
                            continue
                        # esttab CSV：数字行 / "(SE)" 行 / 星号行
                        for tok in NUM_RE.findall(cell):
                            nums.add(norm_num(tok))
                        for tok in SE_RE.findall(cell):
                            nums.add(norm_num(tok))
        except OSError as e:
            print(f"⚠️  跳过 {fn}: {e}", file=sys.stderr)
    return nums


# ── 状态行校验 ────────────────────────────────────────────────

# 状态行：兼容 "> 状态：..." 与 "> 版本：..."，提取其中形如
# 20260808 / 20260808_v5 / rerun_20260808 的 run 标记
STATE_LINE_RE = re.compile(
    r"^>\s*(?:状态|版本)[：:].*?(?:rerun_)?(\d{8})(?:_v\d+)?", re.M
)


def check_state_line(text: str, tables_dir: str) -> bool:
    m = STATE_LINE_RE.search(text)
    if not m:
        print("⚠️  正文未找到状态行（> 状态/版本：...），无法校验版本映射")
        return False
    tag = m.group(1)
    base = os.path.basename(os.path.normpath(tables_dir))
    candidates = {tag, f"{tag}_v5", f"rerun_{tag}"}
    # 允许 --tables 指向 tag 子目录、父目录、或 rerun_<日期> 目录
    ok = base in candidates or any(
        os.path.isdir(os.path.join(tables_dir, c)) for c in candidates
    ) or any(
        os.path.isdir(os.path.join(os.path.dirname(tables_dir), c)) for c in candidates
    )
    print(f"{'✅' if ok else '❌'} 状态行 run 标记 {tag} -> {'映射到 CSV 目录' if ok else '无对应 CSV 目录（空头支票）'}")
    return ok


# ── 主流程 ────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md", help="正文 markdown 路径")
    ap.add_argument("--tables", required=True, help="CSV 目录（output/tables/<tag>/）")
    ap.add_argument("--verbose", action="store_true", help="输出全部明细（含匹配项）")
    ap.add_argument("--state-line", action="store_true", help="校验正文状态行版本映射")
    ap.add_argument("--ignore-unmatched", action="store_true", help="未匹配不置退出码 1")
    args = ap.parse_args()

    if not os.path.isfile(args.md):
        print(f"❌ 正文文件不存在: {args.md}", file=sys.stderr)
        sys.exit(2)

    text = open(args.md, encoding="utf-8-sig").read()
    csv_nums = load_csv_numbers(args.tables)

    unmatched_total = 0
    matched_total = 0
    for title, rows in extract_tables(text):
        if not rows:
            continue
        # 统计本表
        seen = set()
        t_matched = t_unmatched = 0
        matched_items = []
        unmatched_items = []
        for line_no, cells, nums, ses, stars in rows:
            # 数字 + SE 一起对账；星号列只统计不比对（CSV 里也可能有星号）
            for tok in nums + ses:
                if tok in seen:
                    continue
                seen.add(tok)
                if tok in csv_nums:
                    t_matched += 1
                    matched_items.append((line_no, tok))
                else:
                    t_unmatched += 1
                    unmatched_items.append((line_no, tok))
        if t_matched or t_unmatched:
            matched_total += t_matched
            unmatched_total += t_unmatched
            status = "✅" if t_unmatched == 0 else "❌"
            print(f"{status} {title or '(无表号)'}: 匹配 {t_matched} / 未匹配 {t_unmatched}")
            for ln, tok in unmatched_items:
                print(f"   行 {ln}: 数字 {tok} 在 CSV 中无对应")
            if args.verbose and matched_items:
                print(f"   （匹配明细 {len(matched_items)} 项，前 20: "
                      + ", ".join(f"{tok}@L{ln}" for ln, tok in matched_items[:20]) + "）")

    print(f"\n合计: 正文数字 {matched_total + unmatched_total} 个，匹配 {matched_total}，未匹配 {unmatched_total}")
    if args.state_line:
        check_state_line(text, args.tables)

    if unmatched_total > 0 and not args.ignore_unmatched:
        print("\n❌ 存在未匹配数字。处理方式：")
        print("   1) 数字来自描述统计/log → 在正文表格旁注明出处（log/CSV 路径）")
        print("   2) 数字确实出自某次旧 run → 找回对应 tag 目录，或更新正文")
        print("   3) 误报 → 用 --verbose 核对精度差异，确认后 --ignore-unmatched 放行")
        sys.exit(1)
    print("✅ 对账通过")


if __name__ == "__main__":
    main()
