# Graph Templates — Stata 出图模板

> 所有模板要求 `set scheme s2color`，水平网格线 `gs14 vthin`。配色见 graph-standards.md。

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
