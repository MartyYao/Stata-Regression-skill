# Graph Templates — Stata 出图模板

## 1. 事件研究 / 平行趋势检验图

### 输入数据

`reghdfe` 后用 `coefplot` 直接出，或手动构造：

```stata
* 用 coefplot 直接从回归结果出图（推荐，自动处理系数和 CI）
reghdfe over_v1 b4.rel_pos i.rel_pos $controls, ///
    absorb(Stkcd year) vce(cluster province)

* 提取并画事件研究图（排除基期 ib4 = rel_time=-1）
coefplot, ///
    keep(*.rel_pos) ///
    coeflabels(1.rel_pos = "-4" 2.rel_pos = "-3"  ///
               3.rel_pos = "-2" 5.rel_pos = "0"    ///
               6.rel_pos = "1"  7.rel_pos = "2"    ///
               8.rel_pos = "3") ///
    xline(4.5, lcolor("128 128 128") lpattern(dash) lwidth(vthin)) ///
    yline(0, lcolor("128 128 128") lpattern(dash) lwidth(vthin)) ///
    mcolor("49 145 255") msymbol(O) msize(medium) ///
    ciopts(lcolor("49 145 255")) ///
    ytitle("系数估计值") ///
    xtitle("距政策推行年数") ///
    legend(off) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 基期 | `rel_time = -1` | 处理前一期，非边界 |
| 偏移 | `gen rel_pos = rel_time + 5` | 避免 Stata 因子变量负值报错 |
| 参考线 | `xline(4.5)` | 在 -1 和 0 之间画竖线 |
| 窗口 | 通常 `leads = -5` 到 `lags = +5` | 根据面板长度调整 |

### CSDID 替代

```stata
csdid over_v1 $controls, ivar(Stkcd) time(year) gvar(first_treat)
estat event, window(-5 5) estore(csdid_event)
csdid_plot, name(event_study, replace)
graph export "output/figures/event_study.pdf", replace
graph export "output/figures/event_study.png", replace width(1800)
```

## 2. 系数图 — 单模型

```stata
* 适用：异质性分组、机制变量各自跑回归后画系数排列
coefplot, ///
    drop(*.cons *.year *.Stkcd) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") msymbol(O) ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white))
```

## 3. 系数图 — 多模型对比

```stata
* 适用：M1→M6 逐步加入控制变量/FE，展示系数稳定性
coefplot m1 || m2 || m3 || m4 || m5 || m6, ///
    keep(post) ///
    vertical ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white))
```

## 4. 异质性分析图

```stata
* 适用：SOE vs 非 SOE、东中西部分组
coefplot (m_soe, label("国有企业")) ///
         (m_non_soe, label("非国有企业")) ///
         (m_east, label("东部")) ///
         (m_west, label("中西部")), ///
    keep(post) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white))
```

## 5. 边缘效应图

```stata
* 适用：连续处理变量的剂量-反应
reghdfe over_v1 c.treat_score1 $controls, ///
    absorb(Stkcd year) vce(cluster province)

margins, at(treat_score1 = (0(1)5))
marginsplot, ///
    xlabel(0 "0" 1 "1" 2 "2" 3 "3" 4 "4" 5 "5") ///
    ytitle("预测 DV 值") ///           （根据实际 DV 改）
    xtitle("处理强度得分") ///
    ciopts(lcolor("182 211 245") lwidth(none) lpattern(solid)) ///
    recast(line) ///
    plotopts(lcolor("49 145 255") lwidth(medium)) ///
    graphregion(fcolor(white) lcolor(white))
```

## 6. 趋势图

```stata
* 适用：展示处理组/控制组 DV 随时间走势
preserve
collapse (mean) over_v1, by(year treat_group)
twoway (line over_v1 year if treat_group == 1, ///
        lcolor("49 145 255") lwidth(medium)) ///
       (line over_v1 year if treat_group == 0, ///
        lcolor("142 164 184") lwidth(thin) lpattern(dash)), ///
    xline(2018, lcolor("128 128 128") lpattern(dash)) ///
    ytitle("DV 均值") ///           （根据实际 DV 改）
    xtitle("年份") ///
    legend(order(1 "处理组" 2 "控制组") pos(6) ring(0)) ///
    graphregion(fcolor(white) lcolor(white))
restore
```

## 7. 安慰剂检验图

```stata
* 适用：随机分配处理组后重跑 DID，积累 500/1000 次系数分布
* （实际运行时循环 500-1000 次，收集系数放入 placebo_coefs.dta）

* 画图
use "archive/datasets/placebo_coefs.dta", clear

* 从回归结果获取真实系数做参考线
local true_coef = _b[post]

kdensity coef, ///
    lcolor("49 145 255") lwidth(medium) ///
    xline(`true_coef', lcolor("red") lpattern(dash)) ///
    ytitle("密度") ///
    xtitle("安慰剂检验系数") ///
    graphregion(fcolor(white) lcolor(white))
```

## 8. 分布图

```stata
* 适用：检查变量分布、winsorize 效果
* 直方图
histogram over_v1, ///
    color("182 211 245") ///
    lcolor("49 145 255") lwidth(vthin) ///
    ytitle("频数") ///              （根据实际变量改）
    xtitle("over_v1") ///           （根据实际变量改）
    graphregion(fcolor(white) lcolor(white))

* 核密度叠加（处理组 vs 控制组）
kdensity over_v1 if treat_group == 1, ///
    lcolor("49 145 255") lwidth(medium) ///
    addplot(kdensity over_v1 if treat_group == 0, ///
            lcolor("142 164 184") lwidth(thin) lpattern(dash)) ///
    legend(order(1 "处理组" 2 "控制组")) ///
    graphregion(fcolor(white) lcolor(white))
```

## 9. RD 图（断点回归）

```stata
* 适用：断点回归设计（RDD）可视化
* 前提：已用 rdrobust 估算

* 用 rdplot 出图
rdplot over_v1 treat_score1, ///
    c(3)              /* 断点值 */ ///
    p(2)              /* 多项式阶数 */ ///
    nbins(20 20)      /* 断点左右分箱数 */ ///
    graph_options( ///
        graphregion(fcolor(white) lcolor(white)) ///
        plotregion(fcolor(white) lcolor(white)) ///
        ytitle("DV 均值") ///
        xtitle("Running variable") /// （根据实际变量改）
        legend(off) /// （或自定义 legend）
    )
graph export "output/figures/rd_plot.pdf", replace
graph export "output/figures/rd_plot.png", replace width(1800)

* 也可用 binscatter 包
* ssc install binscatter, replace
binscatter over_v1 treat_score1, ///
    rd(3)             /* 断点 = 3 */ ///
    linetype(none)    /* 不画全局线性拟合 */ ///
    by(above)         /* 断点左右分别拟合 */ ///
    graphregion(fcolor(white) lcolor(white))
graph export "output/figures/rd_binscatter.pdf", replace
```

## 出图通用检查清单

- [ ] `set scheme` 已设（推荐 `plotplain`）
- [ ] PDF + PNG 双格式导出
- [ ] 白色背景、无边框
- [ ] 水平网格线、无垂直网格线
- [ ] 焦点蓝色 "49 145 255"，对比灰蓝 "142 164 184"
- [ ] 轴标签大小适当（`vsmall`/`small`）
- [ ] 图例不影响数据区域
- [ ] X/Y 轴标题存在且有意义
- [ ] 如有参考线，线型为虚线
