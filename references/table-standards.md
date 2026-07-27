# Table Standards — 表格输出规范

## 1. 回归表：esttab 输出

### CSV 输出（→ markdown pipe table）

必须使用 `plain` 选项避免 `=""` 包裹：

```stata
esttab m1 m2 m3 using "output/tables/main.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    title("Table 2: 基准回归 V1") ///
    nomtitle label nonumber compress plain
```

选项含义：
- `cells(b(star fmt(4)) t(fmt(4)))` → 系数（4 位小数）+ 星号 + t 值（4 位小数）
- `star(* 0.10 ** 0.05 *** 0.01)` → 显著性标记
- `plain` → 不带 `=""` 包裹，供后续工具直接读取
- `compress` → 减小表宽
- `label` → 用变量标签替代变量名
- `nomtitle nonumber` → 不显示模型标题和编号

### LaTeX 输出（→ 投稿备选）

```stata
esttab m1 m2 m3 using "output/tables/main.tex", replace ///
    booktabs b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    nomtitle label compress ///
    prehead("\begin{table}[htbp]\centering" ///
            "\caption{Table 2: 基准回归}\label{tab:main}" ///
            "\begin{tabular}{l*{@M}{c}}\toprule") ///
    posthead("\midrule") ///
    prefoot("\midrule") ///
    postfoot("\bottomrule" ///
             "\end{tabular}" ///
             "\end{table}")
```

### 多列分组（Panel A/B 或多模型对比）

```stata
* V1 和 V2 分 Panel
esttab m1_v1 m2_v1 m3_v1 m1_v2 m2_v2 m3_v2 using "output/tables/main.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    mgroups("Panel A: V1" "Panel B: V2", pattern(1 0 0 1 0 0) ///
            prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span})) ///
    nomtitle label compress plain
```

## 2. 描述统计表（tabstat）

```stata
estpost tabstat over_v1 over_v2 size lev age ..., ///
    statistics(mean sd p50 min max N) columns(statistics)

esttab . using "output/tables/table1_descriptives.csv", replace ///
    cells("mean(fmt(3)) sd(fmt(3)) p50(fmt(3)) min(fmt(3)) max(fmt(3)) count(fmt(0))") ///
    nomtitle label plain
```

描述统计统一保留 **3 位小数**。

## 3. 相关系数矩阵（pwcorr）

```stata
pwcorr over_v1 over_v2 size lev age ..., obs sig star(0.05)
```

- `obs` → 显示观测数
- `sig` → 显示 p 值
- `star(0.05)` → 在 5% 水平上标记显著性

## 4. CSV → Markdown Pipe Table 转换

### 使用 `scripts/esttab2pipe.py`

```bash
python scripts/esttab2pipe.py output/tables/main.csv
```

输出到文件：

```bash
python scripts/esttab2pipe.py output/tables/main.csv -o output/tables/main_table.md
```

### 手动格式要求

如果手动编辑 pipe table，必须符合以下规范：

```
| 变量 | (1) | (2) | (3) |
|------|-----|-----|-----|
| Post | 0.0123*** | 0.0112** | 0.0108** |
|      | (3.2145) | (2.4567) | (2.1234) |
| 控制变量 | 否 | 是 | 是 |
| 企业 FE | 是 | 是 | 是 |
| 年份 FE | 是 | 是 | 是 |
| N | 25,432 | 25,432 | 25,432 |
| Adj. R² | 0.5678 | 0.6123 | 0.6345 |
```

**强制规则**：
- 系数 + t 值各占一行（系数行在上，t 值在括号内下一行）
- 系数保留 4 位小数
- 括号内 t 值保留 4 位小数
- 不可用 ✓ 省略控制变量
- 必须报告 N 和 Adj. R²
