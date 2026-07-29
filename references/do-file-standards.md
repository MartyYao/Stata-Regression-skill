# Do-File 编码规范与模板

## 1. 文件头

每条 do 文件必须以标准 header 开头：

```stata
*-----------------------------------------------------------------------------
* File: dofiles/03_analysis/05_main_regression.do
* Project: [论文项目名]
* Author: [自动]
* Purpose: [本文件做什么——DID 主回归 V1，机制检验]
* Inputs: working_data.dta
* Outputs: output/tables/main_regression.csv
*          output/tables/main_regression.html
*          output/tables/main_regression.rtf
*          output/figures/event_study.pdf
*          output/figures/event_study.png
* Log: logs/03_analysis_05_main_regression.log
*-----------------------------------------------------------------------------
```

## 2. 顶部样板代码

每条 do 文件严格按此顺序开头：

```stata
version 18  // 根据你的 Stata 版本修改（Stata 17/18/MP）
clear all
set more off
set varabbrev off

capture log close
log using "logs/03_analysis_05_main_regression.log", replace text

set seed 20260726
```

- `set varabbrev off` → 防止变量名缩写 typo 编译通过
- `log using ..., replace text` → `text` 格式可用 grep 检索
- `set seed ONCE` 在文件顶部，**永不在循环内重设**

## 3. 路径约定

- **只使用相对路径**。do 文件从项目根目录执行
- 永远不 `cd "C:\..."` 或 `cd "/Users/..."` 
- Stata 接受前斜杠 `/`（macOS 上必须，Windows 上也可用）
- 中间文件用 `tempfile`，不写入 `data/`

## 4. 命名规范

| 元素 | 规范 |
|------|------|
| 变量名 | `snake_case`，描述性（`post`, `ln_fiscal_ratio`, `treat_score1`） |
| Local macro | `local varlist age educ ...` |
| 文件命名 | `dofiles/03_analysis/05_main_regression.do`（阶段目录 + 编号_描述） |
| 全局宏 | `$controls`, `$prov_C` | 跨 do 文件引用的变量列表用全局宏，在 master_analysis.do 顶部定义 |
| 本地宏 | `` `varlist' `` | 单 do 文件内的临时变量用本地宏 |

## 5. 回归输出纪律

每次估计后立即存储：

```stata
reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
estimates store m1
```

回归表输出格式见第 11 节完整模板。
关键参数：`se(4) plain`。

## 6. 每条 do 文件必须伴随 log

```stata
capture log close
log using "logs/03_analysis_05_main_regression.log", replace text
... 文件主体 ...
log close
```

每个数值声明必须能在 `.log` 或 `output/tables/*.csv` 中追溯。

## 7. 每条 do 文件结束时

```stata
log close
```

## 8. 禁止模式

| 禁止 | 原因 | 替代 |
|------|------|------|
| `cd "C:\..."` 或 `/Users/...` | 不可复现 | 从项目根运行 |
| 循环内 `set more off` | 掩盖错误 | 文件顶部一次 |
| `clear` 而未先 `tempfile` | 丢失数据 | `preserve`/`restore` 或 `tempfile` |
| 文件内多次 `set seed` | 伪可复现 | 文件顶部一次 |
| `varabbrev on` | typo 编译通过 | 始终 `set varabbrev off` |
| 硬编码绝对路径 macro | 换机器就崩 | 定义项目根 macro |

## 9. 注释风格

- 注释解释 **WHY**（样本限制理由、识别策略选择），而非 WHAT
- 节标题用编号 banner：

```stata
*--- 1. 载入样本 + 限制条件 -------------------------------------------
*--- 2. 定义处理变量 + 结果变量 -----------------------------------------
*--- 3. 主回归 ---------------------------------------------------------
*--- 4. 平行趋势检验 ---------------------------------------------------
*--- 5. 表格输出 -------------------------------------------------------
```

- 不保留注释掉的死代码
- 没有 unexplained magic number → 用 `local` 命名并加注释

## 10. 推荐项目目录结构

### 标准结构

```
项目工作文件夹/
├── master_analysis.do              ← 唯一主入口 do 文件
├── working_data.dta                 ← 当前分析用数据（唯一主数据文件）
│                                      * data/derived/ 在 archive/datasets/ 中
│
├── dofiles/                         ← 所有 do 文件，按阶段分目录
│   ├── 01_clean/                    ← 原始数据清洗
│   ├── 02_construct/                ← 变量构造、样本筛选
│   ├── 03_analysis/                 ← 主回归、机制、异质性
│   └── 04_robustness/               ← 稳健性检验、IV、安慰剂
│
├── logs/                            ← 所有 .log 文件，命名对齐 do 文件（如 `logs/03_analysis_05_main_regression.log`）
│
├── output/
│   ├── tables/                      ← 所有 CSV + HTML + RTF（回归表、描述统计等）
│   └── figures/                     ← 所有 PDF + PNG（事件研究图、系数图等）
│
├── archive/                         ← 已废弃的旧版本、旧数据、旧过程文件
│   ├── dofiles/                     ← 旧版 do 文件
│   ├── logs/                        ← 同步废弃的 log
│   └── datasets/                    ← 旧版 dta 文件
│
└── docs/                            ← .md 文档（变量说明、数据构造记录等）
```

### 分析顺序（严格按此顺序执行）

0. 描述统计 + 相关性分析（Table 1，企业+省级全部控制变量，三位小数）
1. 主回归（基准回归，V1/V2）
2. 处理强度（连续得分，如 treat_score1；paper-workflow 场景下紧接主回归后）
3. 平行趋势检验（DID 必须）
4. 稳健性检验（替换 DV、竞争政策、PSM、Leave-One-Out）
5. 内生性检验（IV / Heckman）
6. 机制检验（三步法：直接效应 → 中介 → 交互项）
7. 异质性分析（产权/市场化/地区分组）
8. 进一步检验（经济后果等）

每个检验的 do 文件命名对齐编号，放在 `dofiles/03_analysis/` 下：
`00_describe.do`, `01_main.do`, `02_intensity.do`, `03_parallel.do`, `04_robust.do`, `05_endog.do`, `06_mech.do`, `07_hetero.do`, `08_further.do`

### 文件生命周期

```
新建 do 文件 → dofiles/03_analysis/ 下创建
     │
首次运行 → logs/ 下生成对应 .log
     │
产出表格 → output/tables/ 下生成 .csv → .html + .rtf
     │
产出图形 → output/figures/ 下生成 .pdf + .png
     │
废弃/重写 → 旧 do 文件和对应 log 移入 archive/
     │
论文完稿 → 最终版 output/ 和 dofiles/ 保持整洁即可
```

### 命名约定

| 文件类型 | 命名规范 | 示例 |
|----------|---------|------|
| Do 文件 | `数字_描述.do` | `03_analysis_main_regression.do` |
| Log 文件 | 与 do 文件同名 | `03_analysis_main_regression.log` |
| 表格 HTML | 与 CSV 同名 | `table2_main_regression.html` |
| 表格 RTF | 与 CSV 同名 | `table2_main_regression.rtf` |
| 图形 PNG | 与 PDF 同名 | `fig_event_study.png` |
| 数据文件 | `描述.dta` | `working_data.dta` |

### 禁止模式

| 禁止 | 理由 |
|------|------|
| do 文件、log、CSV 混在根目录 | 不可维护，无法快速定位 |
| 大量废弃版本（`_v2` `_v3` `_final3`）留在根目录 | 不知道当前用的是哪个版本 |
| log 文件和 do 文件同名但放在不同路径 | 无法对应检查 |
| 老旧数据覆盖当前数据 | 无法回退 |
| 多个版本的 dta 文件散落各处（`data_v1.dta`、`data_v2.dta`） | 不知道哪个是当前版 |

## 11. 完整模板框架

```stata
*-----------------------------------------------------------------------------
* File: dofiles/03_analysis/05_main_regression.do
* Project: [项目名]
* Author: [自动]
* Purpose: DID 主回归 V1 + 平行趋势检验
* Inputs: working_data.dta
* Outputs: output/tables/main_regression.csv
*          output/tables/main_regression.html
*          output/tables/main_regression.rtf
*          output/figures/event_study.pdf
*          output/figures/event_study.png
* Log: logs/03_analysis_05_main_regression.log
*-----------------------------------------------------------------------------

version 18  // 根据你的 Stata 版本修改（Stata 17/18/MP）
clear all
set more off
set varabbrev off

capture log close
log using "logs/03_analysis_05_main_regression.log", replace text
set seed 20260726

*--- 0. 项目配置 ------------------------------------------------------------
local analysis_data "working_data.dta"
local outcome "over_v1"
local treat "post"
local controls "size lev age ..."
local fe "Stkcd year"
local cluster "province"
local prov_C "gdp_growth pop_density fiscal_ratio industry_structure"
* 替换为你的省级控制变量

*--- 1. 载入 + 验证样本 ----------------------------------------------------
use "`analysis_data'", clear

* 确认所有变量存在
foreach var in `outcome' `treat' `controls' Stkcd year `cluster' {
    capture confirm variable `var'
    if _rc {
        display as error "Missing: `var'"
        exit 111
    }
}

* 记录样本量
display "Full sample N: " _N

*--- 2. 主回归：三列逐步 ---------------------------------------------------
eststo clear

* Column 1: treat only
eststo m1: reghdfe `outcome' `treat', absorb(`fe') vce(cluster `cluster')
estadd local Controls "No"
estadd local FirmFE "是"
estadd local YearFE "是"

* Column 2: + 企业控制变量
eststo m2: reghdfe `outcome' `treat' `controls', absorb(`fe') vce(cluster `cluster')
estadd local Controls "Yes"
estadd local FirmFE "是"
estadd local YearFE "是"

* Column 3: + 省级控制变量
eststo m3: reghdfe `outcome' `treat' `controls' `prov_C', ///
    absorb(`fe') vce(cluster `cluster')
estadd local Controls "Yes"
estadd local FirmFE "是"
estadd local YearFE "是"

*--- 3. 输出表格 ------------------------------------------------------------
* HTML（→ Obsidian，esttab2html.py 转换）
esttab m1 m2 m3 using "output/tables/main_regression.csv", replace ///
    b(4) se(4) plain ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$")) ///
    mtitles("(1)" "(2)" "(3)") label compress

* RTF（→ Word，直接打开）
esttab m1 m2 m3 using "output/tables/main_regression.rtf", replace ///
    b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(Controls FirmFE YearFE N r2_a, ///
        fmt(%3s %3s %3s %9.0f %9.4f) ///
        labels("Controls" "企业固定效应" "年份固定效应" "N" "Adj. R$^2$")) ///
    mtitles("(1)" "(2)" "(3)") label compress

* 转换为 HTML（需要在 shell 中运行）
* shell python scripts/esttab2html.py output/tables/main_regression.csv

log close
```
