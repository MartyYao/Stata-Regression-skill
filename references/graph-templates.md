# Graph Templates — Stata 出图模板

> 所有模板要求 `set scheme s2color`，水平网格线 `gs14 vthin`。配色见 graph-standards.md。

---

## 0. 平行趋势 / 事件研究图硬性要求（2026-08-06 用户定版）

1. **每个被解释变量各出一张图**（dev/under/over 全覆盖），同一脚本循环生成，规格一致
2. **y=0 水平线用实线**：`yline(0, lcolor("128 128 128") lpattern(solid))`——不用虚线
3. **竖虚线在 0 期（政策当年）上**：rel_pos 偏移后 `xline(5)`（rel=-1 基期不画点，0 期为第 6 个点）——竖线不是画在 -2 与 0 之间，也不是画在基期与 0 期之间
4. **基期不画数据点**：基期系数 0 不出现（coeflabels 中跳过基期标签）
5. **图内文字全部简体中文**：标题、x/y 轴标签、图例、注释（禁止英文 "Kernel density estimate" 之类默认标题）
6. 视觉验证标准（出图后必须用 vision 检查）：pre 期所有点 95% CI 必须包含 0；post 期显著负/正与正文表述一致；竖线在 0 期；y=0 实线
7. 白底无边框、水平网格线 gs14 vthin、无垂直网格线

---

## 1. 事件研究 / 平行趋势检验图

**两阶段法**：TWFE 基线 → csdid（staggered DID 标准方案）。

```stata
* =============================================================================
* 0. 项目配置 — 替换为你的变量名
* =============================================================================
local outcome      over_v1
local controls     "size lev age ..."
local unit_id      Stkcd
local time_var     year
local treated      post
local first_treat  first_treat
local cluster_var  province
local lead_min     -5
local lag_max      5

* =============================================================================
* 1. 载入 + 核验
* =============================================================================
use "working_data.dta", clear

foreach var in `outcome' `unit_id' `time_var' `treated' ///
    `first_treat' `cluster_var' {
    capture confirm variable `var'
    if _rc {
        display as error "缺少变量: `var'"
        exit 111
    }
}
isid `unit_id' `time_var', sort

* =============================================================================
* 2. TWFE 基准 DID
* =============================================================================
reghdfe `outcome' `treated' `controls', ///
    absorb(`unit_id' `time_var') vce(cluster `cluster_var')
estimates store twfe_baseline

* =============================================================================
* 3. csdid（处理异质性处理效应 + 错位处理时间）
* =============================================================================
csdid `outcome' `controls', ///
    ivar(`unit_id') time(`time_var') gvar(`first_treat') ///
    method(dripw) notyet

* 聚合处理效应
estat simple

* 事件研究 + 正式预趋势检验
estat event, window(`lead_min' `lag_max') estore(csdid_event)
estat pretrend, pre(`=abs(`lead_min')')

* =============================================================================
* 4. 出图
* =============================================================================
csdid_plot, ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))

graph export "output/figures/event_study.pdf", replace
graph export "output/figures/event_study.png", replace width(1600)
```

> **为什么不用 coefplot + reghdfe 手工出事件研究图？**  
> reghdfe + `i.rel_pos` + coefplot 需要手动 coeflabels 映射、负值偏移、基期选择——rel_time 范围一变整套标注就错。csdid 的 `estat event` + `csdid_plot` 自动处理这些，是 staggered DID 的标准方案。

---

### 1B. 事件研究图 — TWFE 手动 twoway 版（2026-08-07 用户定版，推荐方案）

**适用**：多期 DID + reghdfe 手动事件研究（实证项目验证过的画法，用户确认效果满意——后续一律按此画）。

```stata
* =============================================================================
* 0. 期数变量构造（lead_min=-5, lag_max=+6）
* =============================================================================
gen rel_time = cond(ever_treated == 0, -1, year - bureau_year)
replace rel_time = -5 if rel_time <= -5
replace rel_time = 6 if rel_time >= 6
gen rel_pos = rel_time + 5          // 基期 rel_time=-1 → rel_pos=4（ib4 = 基期）

* =============================================================================
* 1. 估计（每个被解释变量循环）
* =============================================================================
reghdfe `dvn' ib4.rel_pos $firm_C $prov_C if ev_sample == 1, ///
    absorb(Stkcd year) vce(cluster prov_id)

* =============================================================================
* 2. 提取系数 → 绘图数据
*    关键：set obs = 期数（-5..+6 共 12 期），x = rel + 6（0 期 → x=6）
* =============================================================================
preserve
clear
set obs 12
gen x = _n
gen rel = x - 6                     // x=1→-5 ... x=12→+6
gen double b = 0
gen double se = 1
forvalues i = 0/11 {                // rel_pos ∈ [0,11] 共 12 个系数
    quietly replace b = _b[`i'.rel_pos] if x == `i' + 1
    quietly replace se = _se[`i'.rel_pos] if x == `i' + 1
}
gen byte keep = (rel != -1)         // 基期 -1 不画点
gen ci_lo = b - 1.96*se
gen ci_hi = b + 1.96*se

* =============================================================================
* 3. 出图
* =============================================================================
twoway (rcap ci_lo ci_hi x if keep == 1, lcolor(navy%60) lwidth(medium)) ///
       (scatter b x if keep == 1, mcolor(navy) msize(small) msymbol(circle)) ///
       (function y = 0, range(1 12) lcolor(black) lpattern(dash) lwidth(thin)), ///
       xline(6, lcolor(red) lwidth(thin) lpattern(dash)) ///   ← 0 期 = x = rel_time + 6（曾错位画在 rel=1）
       xlabel(1 "-5" 2 "-4" 3 "-3" 4 "-2" 5 "-1" 6 "0" 7 "1" 8 "2" 9 "3" 10 "4" 11 "5" 12 "6", labsize(small)) ///
       yline(0, lcolor(black) lpattern(solid)) ///
       xtitle("政策相对年份") ytitle("估计系数") ///
       title("") legend(off) xsize(7) ysize(4.5) ///
       scheme(s2color) graphregion(color(white))
graph export "`pic'/图N-平行趋势-`dvn'-v4.png", replace width(2400)   // 换新文件名（同名覆盖 Obsidian 不刷新）
restore
```

**硬性要点（踩过坑，照抄即可）**：
1. **竖线位置**：`xline(6)` = 0 期（x = rel_time + 偏移量 6）；若偏移量不同，竖线 = `xline(偏移量)`，不是 0 期的期数标签
2. **set obs 12**：必须 = 全部期数（-5..+6 共 12 期），少了会漏画 +6 期
3. **基期**：`keep = (rel != -1)` 不画点，但 `xlabel` 仍要标 "-1"（读者知道那是基期）
4. **循环取系数**：`forvalues i = 0/11` 对应 `_b[0.rel_pos]`..`_b[11.rel_pos]`（rel_pos = rel_time + 5，范围 [0,11]）
5. 出图后必须 vision 检查：竖线在 0 期、pre 期 CI 全含 0、画到 +6 期、基期无点

---

## 2. 系数图 — 单模型

```stata
set scheme s2color

coefplot, ///
    drop(*.cons) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") msymbol(O) ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 3. 系数图 — 多模型对比

```stata
set scheme s2color

coefplot m1 || m2 || m3 || m4 || m5 || m6, ///
    keep(post) ///
    vertical ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 4. 异质性分析图

```stata
set scheme s2color

coefplot (m_soe, label("国有企业")) ///
         (m_non_soe, label("非国有企业")) ///
         (m_east, label("东部")) ///
         (m_west, label("中西部")), ///
    keep(post) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 5. 边缘效应图（marginsplot）

```stata
set scheme s2color

reghdfe over_v1 c.treat_score1 $controls, ///
    absorb(Stkcd year) vce(cluster province)

margins, at(treat_score1 = (0(1)5)) post
marginsplot, ///
    xlabel(0 "0" 1 "1" 2 "2" 3 "3" 4 "4" 5 "5") ///
    ytitle("预测值") ///                    ← 替换为实际 DV
    xtitle("处理强度得分") ///
    ciopts(lcolor("182 211 245") lwidth(none)) ///
    recast(line) plotopts(lcolor("49 145 255") lwidth(medium)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 6. 趋势图

```stata
set scheme s2color

preserve
collapse (mean) over_v1, by(year treat_group)
twoway (line over_v1 year if treat_group == 1, ///
        lcolor("49 145 255") lwidth(medium)) ///
       (line over_v1 year if treat_group == 0, ///
        lcolor("142 164 184") lwidth(thin) lpattern(dash)), ///
    xline(2018, lcolor("128 128 128") lpattern(dash)) ///
    ytitle("DV 均值") ///                    ← 替换为实际 DV
    xtitle("年份") ///
    legend(order(1 "处理组" 2 "控制组") pos(6) ring(0)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
restore
```

---

## 7. 安慰剂检验图

```stata
set scheme s2color

* 循环前先存真实系数（不要依赖 use 后 e() 幸存）
local true_coef = _b[post]

* 运行 500-1000 轮随机置换后：
use "archive/datasets/placebo_coefs.dta", clear

kdensity coef, ///
    lcolor("49 145 255") lwidth(medium) ///
    xline(`true_coef', lcolor("198 40 40") lpattern(dash)) ///
    ytitle("密度") ///
    xtitle("安慰剂检验系数") ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 8. 分布图

```stata
set scheme s2color

* 直方图
histogram over_v1, ///
    color("182 211 245") ///
    lcolor("49 145 255") lwidth(vthin) ///
    ytitle("频数") ///
    xtitle("over_v1") ///                    ← 替换为实际变量
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))

* 核密度叠加（处理组 vs 控制组）
kdensity over_v1 if treat_group == 1, ///
    lcolor("49 145 255") lwidth(medium) ///
    addplot(kdensity over_v1 if treat_group == 0, ///
            lcolor("142 164 184") lwidth(thin) lpattern(dash)) ///
    legend(order(1 "处理组" 2 "控制组")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin))
```

---

## 9. RD 图（断点回归）

```stata
set scheme s2color

* rdplot（前提：已用 rdrobust 估算）
rdplot over_v1 treat_score1, ///
    c(3) nbins(20 20) p(2) ///
    graph_options( ///
        graphregion(fcolor(white) lcolor(white)) ///
        plotregion(fcolor(white) lcolor(white)) ///
        ytitle("DV 均值") ///                ← 替换为实际 DV
        xtitle("Running variable") ///       ← 替换为实际变量
        ylabel(, grid glcolor(gs14) glwidth(vthin)))

graph export "output/figures/rd_plot.pdf", replace
graph export "output/figures/rd_plot.png", replace width(1600)

* binscatter 替代（需安装：ssc install binscatter）
binscatter over_v1 treat_score1, ///
    rd(3) linetype(none) by(above) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))

graph export "output/figures/rd_binscatter.pdf", replace
graph export "output/figures/rd_binscatter.png", replace width(1600)
```

---

## 出图通用检查清单

- [ ] `set scheme s2color` 已设
- [ ] PDF + PNG 双格式，width 1600
- [ ] 白色背景，无边框
- [ ] 水平网格线 `gs14 vthin`，无垂直网格线
- [ ] 焦点 "49 145 255"，对比 "142 164 184"
- [ ] 轴标签 `labsize(small)`，标题存在且有意义
- [ ] 图例不遮挡数据区域
- [ ] 参考线虚线
- [ ] 平行趋势图专项：y=0 实线、竖虚线在 0 期、基期不画点、图内文字全中文、每个 DV 一张、出图后 vision 验证 pre 期 CI 全含 0（见 §0）
