# Do-File 编码规范与模板

## 1. 文件头

每条 do 文件必须以标准 header 开头：

```stata
*-----------------------------------------------------------------------------
* File: dofiles/03_analysis/05_main_regression.do
* Project: [论文项目名]
* Author: [自动]
* Purpose: [本文件做什么——DID 主回归 V1，机制检验]
* Inputs: data/derived/analysis_sample.dta
* Outputs: output/tables/main_regression.csv
*          output/tables/main_regression.tex
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
| 文件命名 | 镜像阶段：`01_clean.do`, `02_construct.do`, `03_analysis.do` |

## 5. 回归输出纪律

每次估计后立即存储：

```stata
reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
estimates store m1
```

保存 CSV 和 TeX 双格式：

```stata
* 回归表 - CSV（用于 Obsidian pipe table）
esttab m1 m2 m3 using "output/tables/main_regression.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    title("Table 2: 基准回归 V1") ///
    nomtitle label nonumber compress plain

* 回归表 - LaTeX（用于投稿）
esttab m1 m2 m3 using "output/tables/main_regression.tex", replace ///
    booktabs b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    nomtitle label compress
```

**关于 `plain` 选项**：CSV 输出必须加 `plain`，否则 esttab 会用 `=""` 包裹所有值，后续 Python 处理时需要额外清洗。

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

## 10. 完整模板框架

```stata
*-----------------------------------------------------------------------------
* File: dofiles/03_analysis/05_main_regression.do
* Project: [项目名]
* Author: [自动]
* Purpose: DID 主回归 V1 + 平行趋势检验
* Inputs: data/derived/analysis_sample.dta
* Outputs: output/tables/main_regression.csv
*          output/tables/main_regression.tex
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
local analysis_data "data/derived/analysis_sample.dta"
local outcome "over_v1"
local treat "post"
local controls "size lev age ..."
local fe "Stkcd year"
local cluster "province"

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

* Column 2: + 企业控制变量
eststo m2: reghdfe `outcome' `treat' `controls', absorb(`fe') vce(cluster `cluster')

* Column 3: + 省级控制变量
eststo m3: reghdfe `outcome' `treat' `controls' `prov_C', ///
    absorb(`fe') vce(cluster `cluster')

*--- 3. 输出表格 ------------------------------------------------------------
* CSV（→ Obsidian pipe table）
esttab m1 m2 m3 using "output/tables/main_regression.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    title("Table 2: 基准回归 V1") ///
    nomtitle label nonumber compress plain

* LaTeX（→ 投稿备选）
esttab m1 m2 m3 using "output/tables/main_regression.tex", replace ///
    booktabs b(4) se(4) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R²")) ///
    nomtitle label compress

log close
```
