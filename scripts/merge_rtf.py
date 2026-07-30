#!/usr/bin/env python3
"""
merge_rtf.py — 合并 output/tables/ 下所有 .rtf 为一个附录文档。

每表前加标题（从文件名推导），表间加分页符。
RTF 是纯文本格式，按表号排序后拼接。

Usage:
    python scripts/merge_rtf.py output/tables/ --output output/附录-实证表格.rtf
"""

import argparse
import os
import re
import sys

TABLE_NUM_PATTERN = re.compile(r"table(\d+)", re.IGNORECASE)


def die(msg):
    print(f"错误: {msg}", file=sys.stderr)
    sys.exit(1)


def table_sort_key(filename):
    m = TABLE_NUM_PATTERN.search(filename)
    return (0, int(m.group(1)), filename) if m else (1, 0, filename)


def title_from_filename(basename):
    m = TABLE_NUM_PATTERN.search(basename)
    if not m:
        return basename.replace("_", " ")
    desc = TABLE_NUM_PATTERN.sub("", basename).strip("_")
    desc = re.sub(r"\bv(\d+)\b", lambda x: f"V{x.group(1)}", desc, flags=re.IGNORECASE)
    desc = desc.replace("_", " ")
    title = f"Table {int(m.group(1))}"
    return f"{title}: {desc}" if desc else title


def rtf_escape(text):
    """转义 RTF 中的特殊字符。"""
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    return text


def merge(tables_dir, output_path):
    rtf_files = sorted(
        (f for f in os.listdir(tables_dir) if f.lower().endswith(".rtf")),
        key=table_sort_key,
    )
    out_name = os.path.basename(output_path)
    rtf_files = [f for f in rtf_files if f != out_name]
    if not rtf_files:
        die(f"{tables_dir} 下没有 .rtf 文件")

    header = None
    body_parts = []

    for fname in rtf_files:
        path = os.path.join(tables_dir, fname)
        with open(path, encoding="gbk", errors="replace") as f:
            content = f.read()

        # 提取 RTF 文件头（第一个文件的字体表、颜色表、样式表）
        tbl_idx = content.find("\\trowd")
        if tbl_idx == -1:
            print(f"⚠️ 跳过（无表格）: {fname}")
            continue

        if header is None:
            header = content[:tbl_idx].rstrip() + "\n"

        # 截取表格部分（去掉每个文件末尾的 `}`，避免括号失配）
        table_content = content[tbl_idx:]
        # 去掉文件末尾的单个 `}`（RTF 文档闭合符）
        table_content = table_content.rstrip()
        if table_content.endswith("}"):
            table_content = table_content[:-1].rstrip()

        # 标题
        title = title_from_filename(os.path.splitext(fname)[0])
        title_rtf = (
            "{\\pard\\qc\\b\\f0\\fs24 "  # 居中、粗体、宋体、12pt
            + rtf_escape(title)
            + "\\par}\n\\par\n"
        )
        body_parts.append(title_rtf)
        body_parts.append(table_content)

        # 表间分页（最后一表不加）
        if fname != rtf_files[-1]:
            body_parts.append("\\page\\par\n")

        print(f"✅ {fname} → {title}")

    if not body_parts:
        die("所有 .rtf 文件中均未找到表格")

    # 组装完整 RTF
    output = header + "\n".join(body_parts) + "\n}"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="gbk", errors="replace") as f:
        f.write(output)

    print(f"\n✅ 合并完成: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="合并 output/tables/ 下所有 .rtf 为一个附录文档（按表号排序，表间分页）"
    )
    parser.add_argument("tables_dir", help="表格目录（如 output/tables/）")
    parser.add_argument(
        "--output", "-o", default=None,
        help="输出 rtf 路径（默认: <tables_dir>/../附录-实证表格.rtf）"
    )
    args = parser.parse_args()

    tables_dir = args.tables_dir.rstrip("/")
    output_path = args.output or os.path.join(os.path.dirname(tables_dir), "附录-实证表格.rtf")
    merge(tables_dir, output_path)


if __name__ == "__main__":
    main()
