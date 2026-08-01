# Table Standards — 表格输出规范

## 1. 回归表：esttab 双输出

### 输出管线

```
Obsidian:  esttab → .csv (plain) → esttab2html.py → .html（阅读视图粘贴）
Word 投稿: esttab → .rtf         → Word 直接打开
合并投稿:  .rtf 文件 → merge_rtf.py → 附录-实证表格.rtf
```

### esttab 命令

```stata
* FE/Controls 标记（必须在 esttab 前）
eststo m1: reghdfe over_v1 post, absorb(Stkcd year) vce(cluster province)
estadd local Controls "No"
estadd local FirmFE "是"
estadd local YearFE "是"

eststo m2: reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"
estadd local FirmFE "是"
estadd local YearFE "是"

eststo m3: reghdfe over_v1 post $controls $prov_C, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"
estadd local FirmFE "是"
estadd local YearFE "是"

* HTML（→ Obsidian）
esttab m1 m2 m3 using "output/tables/main.csv", replace ///
    b(4) se(4) plain ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label compress ///
    mtitles("(1)" "(2)" "(3)") ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$"))

* RTF（→ Word）
esttab m1 m2 m3 using "output/tables/main.rtf", replace ///
    b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label compress ///
    mtitles("(1)" "(2)" "(3)") ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$"))
```

选项含义：
- `b(4) se(4)` → 系数和标准误保留 4 位小数
- `plain` → CSV 不加 `=""` 包裹（仅 .csv 需要，.rtf 不需要）
- `star(* 0.10 ** 0.05 *** 0.01)` → 显著性标记
- `stats(...)` → 底部统计行
- `estadd local` → 在 esttab 前逐列标记 Controls/FE 状态

### 强制规则

1. **全系数展示**：不得使用 `keep()` 或 `drop()` 过滤控制变量，所有系数逐行列示
2. **_cons 保留**：禁止 `drop(_cons)`
3. **双输出**：同一回归同时出 `.csv`（→ HTML）+ `.rtf`（→ Word）
4. **星号规范**：`* p<0.10, ** p<0.05, *** p<0.01`

### 调用转换脚本

```bash
# HTML（Obsidian）
python scripts/esttab2html.py output/tables/main.csv --title "Table 2: 基准回归"
python scripts/esttab2html.py output/tables/main.csv --note "省份层面聚类稳健标准误"

# 合并 RTF 为附录
python scripts/merge_rtf.py output/tables/ --output output/附录-实证表格.rtf
```

### 插入 Obsidian

生成的 .html 文件包含 inline 三线表样式。将 .html 文件内容作为 HTML 源码粘贴到 Obsidian 笔记中，切换到阅读视图即可预览。

---

## 2. 多列分组（Panel A/B 或多模型对比）

机制表、异质性子表用 `mgroups`。**6 个模型均需 `estadd local`：**

```stata
eststo m1_v1: reghdfe over_v1 post, absorb(Stkcd year) vce(cluster province)
estadd local Controls "No"; estadd local FirmFE "是"; estadd local YearFE "是"
* （其余 5 列同理）

esttab m1_v1 m2_v1 m3_v1 m1_v2 m2_v2 m3_v2 using "output/tables/main.csv", replace ///
    b(4) se(4) plain ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label compress ///
    mgroups("Panel A: V1" "Panel B: V2", pattern(1 0 0 1 0 0) span) ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$"))

* 同步出 .rtf（同上，去掉 plain）
```

---

## 3. 描述统计表（tabstat）

```stata
estpost tabstat over_v1 over_v2 size lev age ..., ///
    statistics(mean sd p50 min max N) columns(statistics)

esttab . using "output/tables/table1_descriptives.csv", replace plain ///
    cells("mean(fmt(3)) sd(fmt(3)) p50(fmt(3)) min(fmt(3)) max(fmt(3)) count(fmt(0))") ///
    nomtitle label

python scripts/esttab2html.py output/tables/table1_descriptives.csv --title "Table 1: 描述统计"
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
- 结果在 `.log` 文件中，无需额外导出表格

---

<<<<<<< HEAD
## 5. 前置条件

=======
## 5. TeX 输出（LaTeX 投稿 / 数据存档）

用户偏好：论文表格系数和 t 值 **4 位小数**，括号内展示 **t 值**（非标准误），同时导出 CSV + TeX（+ HTML/RTF 展示管线）：

```stata
esttab m1 m2 m3 using "output/tables/table2_main.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    stats(N r2_a, fmt(0 3)) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    nonumbers nomtitles collabels(none) label

esttab m1 m2 m3 using "output/tables/table2_main.tex", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    stats(N r2_a, fmt(0 3)) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    booktabs nomtitles collabels(none) label
```

- 描述统计：**3 位小数**
- 每列必须报告 N 和 Adj R²，固定效应在表下方标注（企业固定效应 / 年份固定效应 / 省份聚类）
- 不省略控制变量——每行控制变量列出系数和 t 值

> Obsidian 中显著性星号必须用 `<sup>***</sup>` 包裹（裸写 `***` 会被 markdown 解析吞掉）。

---

## 6. 前置条件

>>>>>>> 568dcef (v0.2.3: merge stata-empirical experience library)
- **Stata**：esttab 需要 estout 包（`ssc install estout`）
- **脚本部署**：将 `scripts/esttab2html.py` 和 `scripts/merge_rtf.py` 复制到项目根目录的 `scripts/` 文件夹下
