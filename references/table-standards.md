# Table Standards — 表格输出规范

## 1. 回归表：esttab → .csv → HTML + docx

### 输出管线

```
esttab → .csv (plain) → esttab2html.py → .html + .docx
                          └─ Python 直接生成，不依赖 pandoc
```

- `.html` → Obsidian 预览模式直接插入（inline 三线表样式）
- `.docx` → Word 打开，CSSCI 投稿用（宋体 10pt 三线表，可再微调）

### esttab 命令

```stata
* 先添加 FE/Controls 标记（必须在 esttab 前）
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

* 可选：DV 均值与聚类层级（需先计算）
* quietly summarize over_v1 if e(sample)
* estadd local MeanDV = string(r(mean), "%9.4f")
* estadd local Cluster "province"

* 输出 CSV（plain，供 esttab2html.py 解析）
esttab m1 m2 m3 using "output/tables/main.csv", replace ///
    b(4) se(4) plain ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label compress ///
    mtitles("(1)" "(2)" "(3)") ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$"))
```

选项含义：
- `b(4) se(4)` → 系数和标准误保留 4 位小数
- `plain` → CSV 不加 `=""` 包裹（esttab2html.py 解析前提，缺了会报错）
- `star(* 0.10 ** 0.05 *** 0.01)` → 显著性标记
- `stats(...)` → 底部统计行
- `estadd local` → 在 esttab 前逐列标记 Controls/FE 状态

### 强制规则

1. **全系数展示**：不得使用 `keep()` 或 `drop()` 过滤控制变量，所有系数逐行列示
2. **_cons 保留**：禁止 `drop(_cons)`
3. **双格式输出**：.csv 必须用 `plain`，同一 `.csv` 生成 `.html` + `.docx`
4. **星号规范**：`* p<0.10, ** p<0.05, *** p<0.01`

### 调用转换脚本

```bash
# 基础用法
python scripts/esttab2html.py output/tables/main.csv

# 带标题
python scripts/esttab2html.py output/tables/main.csv --title "Table 2: 基准回归 V1"

# 自定义表尾注脚（默认：括号内为标准误；* p<0.10, ** p<0.05, *** p<0.01）
python scripts/esttab2html.py output/tables/main.csv --note "省份层面聚类稳健标准误"
```

输出：
```
output/tables/main.html   ← Obsidian 插入用
output/tables/main.docx   ← Word 投稿用
```

### 插入 Obsidian

生成的 .html 文件包含 inline 三线表样式。将 .html 文件内容作为 HTML 源码粘贴到 Obsidian 笔记中，切换到阅读视图即可预览。

---

## 2. 多列分组（Panel A/B 或多模型对比）

机制表、异质性子表用 `mgroups` 分组。**6 个模型均需 `estadd local`，不可遗漏：**

```stata
* 先逐列添加 FE/Controls 标记（必须在 esttab 前）
eststo m1_v1: reghdfe over_v1 post, absorb(Stkcd year) vce(cluster province)
estadd local Controls "No"; estadd local FirmFE "是"; estadd local YearFE "是"
eststo m2_v1: reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"; estadd local FirmFE "是"; estadd local YearFE "是"
eststo m3_v1: reghdfe over_v1 post $controls $prov_C, absorb(Stkcd year) vce(cluster province)
estadd local Controls "Yes"; estadd local FirmFE "是"; estadd local YearFE "是"
* （m1_v2 ~ m3_v2 同理，每列均需 estadd local）

esttab m1_v1 m2_v1 m3_v1 m1_v2 m2_v2 m3_v2 using "output/tables/main.csv", replace ///
    b(4) se(4) plain ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    label compress ///
    mgroups("Panel A: V1" "Panel B: V2", pattern(1 0 0 1 0 0) span) ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$"))
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

```stata
* 输出到 log 并标注
log close 后，pwcorr 结果在 .log 文件中，无需额外导出表格。
```

---

## 5. 前置条件

- **python-docx**：`pip install python-docx`（esttab2html.py 生成 .docx 用，不依赖 pandoc）
- **Stata**：esttab 需要 estout 包（`ssc install estout`）
- **脚本部署**：将 `scripts/esttab2html.py` 和 `scripts/merge_tables.py` 复制到项目根目录的 `scripts/` 文件夹下
---

## 6. 合并表格为附录

```bash
python scripts/merge_tables.py output/tables/ --output output/附录-实证表格.docx
```

合并后每张表带标题，表间分页，可直接提交投稿。
