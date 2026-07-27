#!/usr/bin/env python3
"""
esttab2pipe.py — Convert esttab CSV output to markdown three-line pipe table.

Usage:
    python esttab2pipe.py output/tables/main_regression.csv
    python esttab2pipe.py output/tables/main_regression.csv --title "Table 2: 基准回归 V1"
    python esttab2pipe.py output/tables/main_regression.csv -o output/tables/main_table.md

Features:
- Strips esttab's ="" wrapping
- Handles coefficient + t-statistic paired rows
- Handles stats rows (N, R², etc.)
- Outputs Obsidian-compatible markdown pipe table
- Three-line table styling (preview via CSS)
"""

import csv
import sys
import re
import argparse


def clean_value(val):
    """Remove esttab's ="" wrapping and trim."""
    val = val.strip()
    # Remove ="..." wrapping
    m = re.match(r'^="(.*)"$', val)
    if m:
        return m.group(1).strip()
    return val


def parse_csv(filepath):
    """Read esttab CSV and return cleaned rows."""
    with open(filepath, encoding='utf-8-sig') as f:
        # Sniff for the delimiter (esttab uses comma)
        content = f.read()
    
    # Split into lines, handle possible Windows line endings
    lines = content.replace('\r\n', '\n').split('\n')
    
    # Remove empty trailing lines
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    
    if not lines:
        return []
    
    # Parse CSV properly
    reader = csv.reader(lines)
    rows = []
    for row in reader:
        cleaned = [clean_value(cell) for cell in row]
        rows.append(cleaned)
    
    return rows


def is_coef_row(cell):
    """Check if a cell looks like a coefficient (number with optional stars)."""
    cell = cell.strip()
    # Matches: 0.1234***, -0.1234**, 0.12, etc.
    pattern = r'^-?[\d,]+\.?\d*\s*\*{0,3}$'
    return bool(re.match(pattern, cell))


def is_se_row(cell):
    """Check if a cell looks like a standard error in parentheses."""
    cell = cell.strip()
    pattern = r'^\(?-?[\d,]+\.?\d*\)?$'
    return bool(re.match(pattern, cell))


def is_stat_row(cells):
    """Check if this is a statistics row (N, R², etc)."""
    if not cells:
        return False
    label = cells[0].strip()
    stat_labels = ['n', 'r²', 'r2', 'r2_a', 'adj. r²', 'r2_within', 
                   'mean', 'dv mean', 'f', 'chi2', 'll']
    return any(label.lower().startswith(s) for s in stat_labels)


def classify_rows(rows):
    """
    Classify rows into: header, coef, se, stat, blank, other.
    Returns list of (type, row_data).
    """
    classified = []
    i = 0
    while i < len(rows):
        row = rows[i]
        # Skip completely empty rows
        if not any(c.strip() for c in row):
            classified.append(('blank', row))
            i += 1
            continue
        
        # Check if this is a header row (first cell is a column header)
        if not classified or classified[-1][0] == 'blank' or classified[-1][0] == 'title':
            first = row[0].strip() if row else ''
            # Multi-method header detection:
            # Method 1: parenthesized (1) (2) ...
            if any(c.strip().startswith('(') and c.strip().endswith(')') for c in row[1:]):
                classified.append(('header', row))
                i += 1
                continue
            # Method 2: check for typical esttab mtitles pattern
            # (column labels like "Baseline" or "Model 1" - not data, not stats)
            if (len(row) >= 3 and
                not is_coef_row(row[1]) and
                not row[0].strip().lower().startswith(('n', 'r2', 'r²', 'adj', 'mean', 'f', 'chi2'))):
                # Check if this looks like a header (short non-numeric labels in columns)
                col_labels = [c.strip() for c in row[1:] if c.strip()]
                if col_labels and all(not re.match(r'^-?\d', c) for c in col_labels):
                    classified.append(('header', row))
                    i += 1
                    continue
        
        # Check if this is a coefficient row
        if row and len(row) > 1 and is_coef_row(row[1]):
            # Check next row for SE
            if i + 1 < len(rows) and is_se_row(rows[i + 1][1]):
                classified.append(('coef_pair', (row, rows[i + 1])))
                i += 2
                continue
            else:
                classified.append(('coef_solo', row))
                i += 1
                continue
        
        # Check if stat row
        if is_stat_row(row):
            classified.append(('stat', row))
            i += 1
            continue
        
        # Everything else
        classified.append(('other', row))
        i += 1
    
    return classified


def format_coef(val):
    """Format coefficient value with stars preserved."""
    val = val.strip()
    # Extract the numeric part and stars
    m = re.match(r'^(-?[\d,]+\.?\d*)(\s*\*{0,3})$', val)
    if m:
        num, stars = m.groups()
        # Remove commas from numbers (thousands separators)
        num = num.replace(',', '')
        return f"{num}{stars}"
    return val


def format_tstat(val):
    """Format t-statistic (always wrap in parentheses)."""
    val = val.strip()
    val = val.strip('()')
    return f"({val})"


def pipe_escape(text):
    """Escape pipe characters in markdown table cells."""
    return text.replace('|', '\\|')


def generate_pipe_table(classified, title=None):
    """Generate markdown pipe table from classified rows."""
    lines = []
    
    # Optional title
    if title:
        lines.append(f"**{title}**")
        lines.append("")
    
    # Find header row and column count
    headers = None
    num_cols = 0
    for typ, row in classified:
        if typ == 'header':
            headers = row
            num_cols = len(row)
            break
    
    if not headers:
        # Try to infer from the first data row
        for typ, row in classified:
            if typ in ('coef_pair', 'coef_solo'):
                if typ == 'coef_pair':
                    num_cols = len(row[0])
                else:
                    num_cols = len(row)
                break
        # Create generic headers
        headers = ['变量'] + [f"({i})" for i in range(1, max(num_cols, 2))]
    
    num_cols = max(num_cols, len(headers) if headers else 2)
    
    # Pad headers
    while len(headers) < num_cols:
        headers.append('')
    
    # Write header
    header_str = '| ' + ' | '.join(pipe_escape(str(h)) for h in headers) + ' |'
    lines.append(header_str)
    
    # Write separator (three-line table style — just one line)
    sep = '|' + '|'.join([' --- '] * num_cols) + '|'
    lines.append(sep)
    
    # Write data rows
    for typ, data in classified:
        if typ in ('coef_pair',):
            coef_row, se_row = data
            # Coefficient row
            coef_cells = [pipe_escape(str(coef_row[0]))] if coef_row else ['']
            for j in range(1, num_cols):
                if j < len(coef_row) and coef_row[j].strip():
                    coef_cells.append(format_coef(coef_row[j]))
                else:
                    coef_cells.append('')
            lines.append('| ' + ' | '.join(coef_cells) + ' |')
            
            # SE row (indented)
            se_cells = ['']  # blank first cell for variable name
            for j in range(1, num_cols):
                if j < len(se_row) and se_row[j].strip():
                    se_cells.append(format_tstat(se_row[j]))
                else:
                    se_cells.append('')
            lines.append('| ' + ' | '.join(se_cells) + ' |')
        
        elif typ == 'coef_solo':
            cells = [pipe_escape(str(data[0]))] if data else ['']
            for j in range(1, num_cols):
                if j < len(data) and data[j].strip():
                    cells.append(format_coef(data[j]))
                else:
                    cells.append('')
            lines.append('| ' + ' | '.join(cells) + ' |')
        
        elif typ == 'stat':
            label = pipe_escape(data[0].strip()) if data else ''
            cells = [label]
            for j in range(1, num_cols):
                if j < len(data) and data[j].strip():
                    val = data[j].strip()
                    # Remove commas from numbers
                    val = val.replace(',', '')
                    cells.append(val)
                else:
                    cells.append('')
            lines.append('| ' + ' | '.join(cells) + ' |')
        
        elif typ == 'header':
            pass  # Already handled above
        
        elif typ == 'other':
            # Try to render as descriptive text
            non_empty = [c for c in data if c.strip()]
            if non_empty:
                # Could be a panel label or table note
                label = pipe_escape(data[0].strip())
                cells = [label]
                for j in range(1, num_cols):
                    if j < len(data) and data[j].strip():
                        cells.append(data[j].strip())
                    else:
                        cells.append('')
                lines.append('| ' + ' | '.join(cells) + ' |')
    
    # Add blank line at end
    lines.append('')
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Convert esttab CSV to markdown three-line pipe table'
    )
    parser.add_argument('input', help='Path to esttab CSV file')
    parser.add_argument('--title', '-t', help='Table title (markdown bold)')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    rows = parse_csv(args.input)
    if not rows:
        print("Error: Empty or unreadable CSV file.", file=sys.stderr)
        sys.exit(1)
    
    classified = classify_rows(rows)
    markdown = generate_pipe_table(classified, args.title)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == '__main__':
    main()
