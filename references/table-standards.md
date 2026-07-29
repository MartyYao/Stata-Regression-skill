# Table Standards — 表格输出规范

## 1. 回归表：esttab → .tex → pandoc

### 输出管线

```
esttab → .tex (booktabs) → esttab2html.py → .html + .docx
                              └─ pandoc 自动转换
```

- `.html` → Obsidian 预览模式直接插入（三线表 CSS 渲染）
- `.docx` → Word 打开，CSSCI 投稿用（可再微调字体/边框）

### esttab 命令

```stata
* 先添加 FE/Controls 标记（必须在 esttab 前）
eststo m1: reghdfe over_v1 post, absorb(Stkcd year) vce(cluster province)
estadd local Controls "No"
estadd local FirmFE "Yes"
estadd local YearFE "Yes"

eststo m2: reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"
estadd local FirmFE "Yes"
estadd local YearFE "Yes"

eststo m3: reghdfe over_v1 post $controls $prov_C, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"
estadd local FirmFE "Yes"
estadd local YearFE "Yes"

* 输出 LaTeX（booktabs 三线表）
esttab m1 m2 m3 using "output/tables/main.tex", replace ///
    b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    booktabs ///
    label compress ///
    mtitles("(1)" "(2)" "(3)") ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "Firm FE" "Year FE" "N" "Adj. R&sup2")) ///
    substitute(\_ _) ///
    fragment
```

选项含义：
- `b(4) se(4)` → 系数和标准误保留 4 位小数
- `booktabs` → 使用 LaTeX booktabs 三线表（`\toprule`/`\midrule`/`\bottomrule`）
- `star(* 0.10 ** 0.05 *** 0.01)` → 显著性标记
- `booktabs fragment` → 不包含 `\begin{table}` 环境，供 pandoc 直接处理
- `stats(...)` → 底部统计行
- `estadd local` → 在 esttab 前逐列标记 Controls/FE 状态

### 强制规则

1. **全系数展示**：不得使用 `keep()` 或 `drop()` 过滤控制变量，所有系数逐行列示
2. **_cons 保留**：禁止 `drop(_cons)`
3. **双格式输出**：.tex 必须用 `booktabs fragment`，同一 `.tex` 生成 `.html` + `.docx`
4. **星号规范**：`* p<0.10, ** p<0.05, *** p<0.01`

### 调用转换脚本

```bash
# 基础用法
python scripts/esttab2html.py output/tables/main.tex

# 带标题
python scripts/esttab2html.py output/tables/main.tex --title "Table 2: 基准回归 V1"
```

输出：
```
output/tables/main.html   ← Obsidian 插入用
output/tables/main.docx   ← Word 投稿用
```

---

## 2. 多列分组（Panel A/B 或多模型对比）

```stata
esttab m1_v1 m2_v1 m3_v1 m1_v2 m2_v2 m3_v2 using "output/tables/main.tex", replace ///
    b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    booktabs fragment ///
    label compress ///
    mgroups("Panel A: V1" "Panel B: V2", pattern(1 0 0 1 0 0) ///
            prefix(\multicolumn{@span}{c}{) suffix(}) span ///
            erepeat(\cmidrule(lr){@span})) ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f)) ///
    substitute(\_ _)
```

---

## 3. 描述统计表（tabstat）

```stata
estpost tabstat over_v1 over_v2 size lev age ..., ///
    statistics(mean sd p50 min max N) columns(statistics)

esttab . using "output/tables/table1_descriptives.tex", replace ///
    cells("mean(fmt(3)) sd(fmt(3)) p50(fmt(3)) min(fmt(3)) max(fmt(3)) count(fmt(0))") ///
    nomtitle label booktabs fragment

python scripts/esttab2html.py output/tables/table1_descriptives.tex --title "Table 1: 描述统计"
```

描述统计统一保留 **3 位小数**。

---

## 4. 相关系数矩阵（pwcorr）

```stata
pwcorr over_v1 over_v2 size lev age ..., obs sig star(0.05)
```

- `obs` → 显示观测数
- `sig` → 显示 p 值
- `star(0.05)` → 在 5% 水平上标记显著性

---

## 5. 前置条件

- **pandoc**：macOS 安装 `brew install pandoc`
- **Stata**：`booktabs` 选项需要 estout 包（`ssc install estout`）
- **LaTeX booktabs 包**：pandoc 内置支持，无需额外安装
