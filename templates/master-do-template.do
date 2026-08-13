*------------------------------------------------------------------------------
* File:   dofiles/03_analysis/<name>.do
* Project: [YOUR PROJECT NAME]
* Author:  [YOUR NAME]
* Purpose: [Describe the task: e.g. Estimate main DID specification]
* Inputs:  data/derived/analysis_sample.dta
* Outputs: output/tables/$TAG/tableNN.csv
*          output/tables/$TAG/tableNN.tex
*          output/figures/event_study.pdf
*          output/figures/event_study.png
* Log:     logs/$TAG/<表号>_<内容>.log
*
* 使用说明：
*   1. 将本文件复制到 dofiles/03_analysis/ 下
*   2. 在 Section 0 中替换变量名
*   3. 确认 data/derived/ 下的输入文件已就绪
*   4. 取消 dofiles/00_master.do 中对应的调用
*   5. 开新 run 前先执行 rerun.sh new "YYYYMMDD_vN"（见 stata-regression 技能）
*------------------------------------------------------------------------------
version 17
clear all
set more off
set varabbrev off
capture mkdir "logs"
capture mkdir "output"
capture mkdir "output/tables/$TAG"
capture mkdir "output/figures"
capture log close
log using "logs/$TAG_<name>.log", replace text
set seed 20260726

*--- 0. 项目配置 --------------------------------------------------------------
* Run Tag：每次全量重跑/样本口径变更 = 新 tag（rerun.sh new 创建目录）。
* 输出路径一律用 output/tables/$TAG/，禁止写根目录（防覆盖旧结果）。
global TAG = "YYYYMMDD_vN"

local analysis_data  "data/derived/analysis_sample.dta"
local outcome        outcome_var
local unit_id        unit_id          // 面板个体 ID
local time_var       year
local treated        treated          // DID 处理虚拟变量
local first_treat    first_treat_yr   // 首次处理年份（staggered 必须）
local controls       "control1 control2 control3"
local prov_controls  "prov_control1 prov_control2"
local cluster_var    unit_id          // 聚类层级（处理分配层级）

* 事件研究窗口。根据数据长度和处理时间分布调整。
local lead_min = -5
local lag_max  = 5

*--- 1. 加载和验证分析样本 ----------------------------------------------------
use "`analysis_data'", clear

* 验证必需变量存在
foreach var in `outcome' `unit_id' `time_var' `treated' /// 
    `first_treat' `cluster_var' `controls' `prov_controls' {
    capture confirm variable `var'
    if _rc {
        display as error "Missing required variable: `var'"
        exit 111
    }
}

* 验证面板结构
isid `unit_id' `time_var', sort

display _n as text ">>> 样本信息 <<<"
display "总观测数: " _N
display "个体数: " _N / (`lag_max' - `lead_min' + 1)
tabulate `treated'
tabulate `first_treat' if `first_treat' < ., missing

*--- 2. 描述统计 + 相关性 -----------------------------------------------------

display _n as text ">>> 描述统计 <<<"
tabstat `outcome' `treated' `controls' `prov_controls', ///
    stats(n mean sd min p25 median p75 max) columns(statistics)

display _n as text ">>> 相关性矩阵 <<<"
pwcorr `outcome' `treated' `controls' `prov_controls', obs sig

*--- 3. 主回归 ----------------------------------------------------------------

display _n as text ">>> 主回归 <<<"

* M1: 裸回归
reghdfe `outcome' `treated', ///
    absorb(`unit_id' `time_var') ///
    vce(cluster `cluster_var')
estimates store m1

* M2: 加企业控制变量
reghdfe `outcome' `treated' `controls', ///
    absorb(`unit_id' `time_var') ///
    vce(cluster `cluster_var')
estimates store m2

* M3: 加省级控制变量
reghdfe `outcome' `treated' `controls' `prov_controls', ///
    absorb(`unit_id' `time_var') ///
    vce(cluster `cluster_var')
estimates store m3

* 导出主回归表
esttab m1 m2 m3 using "output/tables/$TAG/tableNN.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    stats(N r2_a, fmt(0 3)) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    nonumbers nomtitles collabels(none) label ///
    title("主回归：基准 DID 结果")

esttab m1 m2 m3 using "output/tables/$TAG/tableNN.tex", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    stats(N r2_a, fmt(0 3)) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    booktabs nomtitles collabels(none) label ///
    title("主回归：基准 DID 结果") ///
    addnotes("括号内为 t 值" "标准误聚类在 `cluster_var' 层面" ///
             "所有回归包含 `unit_id' 和 `time_var' 固定效应")

*--- 4. 平行趋势（事件研究法）-------------------------------------------------

display _n as text ">>> 事件研究图 <<<"

* 构造相对时间变量（因子变量不接受负值，需偏移）
gen rel_time = `time_var' - `first_treat' if !missing(`first_treat')
replace rel_time = -1 if missing(`first_treat')   // 纯控制组固定在基期（防控制组污染，见 pure-control-event-study）
gen rel_time_pos = rel_time + abs(`lead_min') + 1  // 偏移 +6：rel_time=-5 → 1，rel_time=-1 → 5
* 基期选 rel_time = -1（偏移后为 ib5.rel_time_pos）
* 注意：若修改 lead_min，基期位置需同步调整（pos = -1 + abs(lead_min) + 1）

reghdfe `outcome' ib5.rel_time_pos `controls' `prov_controls', ///
    absorb(`unit_id' `time_var') ///
    vce(cluster `cluster_var')

* 提取系数并绘图
coefplot (main, label("估计系数") ///
    color("49 145 255") ciopts(color("49 145 255%50"))) ///
    , keep(*.rel_time_pos) vertical ///
    yline(0, lcolor(gs8) lwidth(thin)) ///
    xline(5.5, lcolor(gs14) lwidth(vthin) lpattern(dash)) /// 基期参考线（pos=5）
    ylabel(, angle(horizontal) labcolor("74 89 105")) ///
    xlabel(, labcolor("74 89 105")) ///
    graphregion(color(white)) plotregion(color(white)) ///
    legend(region(color(white))) ///

graph export "output/figures/event_study.pdf", replace
graph export "output/figures/event_study.png", replace width(1600)

*--- 5. 稳健性（视论文需要）--------------------------------------------------

* 此处添加：bacondecomp、安慰剂检验、PSM、替换 DV 等

*--- 6. 关闭 log --------------------------------------------------------------

log close
*==============================================================================
* EOF
