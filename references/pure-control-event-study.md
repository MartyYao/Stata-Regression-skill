# 纯控制组事件研究

## 问题

Staggered DID 中，后处理省份（later-treated）在事件研究中充当先处理省份（early-treated）的"控制组"观测，导致远期的处理效应被系统性低估——因为后处理省份自身也产生了 pre-treatment 效应，DID 差分时被减掉了。

## 解决方案

用从未处理的省份（never-treated）作为控制组，永远设定它们的 rel_time=-1（基准期），排除后处理省份对参照组的污染。

## Stata 实现

```stata
* 1. 构造各批次首次成立年份
gen yr = year if post == 1
bysort prov_id: egen bureau = min(yr)
replace bureau = 2024 if missing(bureau)   // 未处理省份赋样本外年份
drop yr

* 2. 构造事件时间（纯控制组设定）
gen rel_clean = cond(bureau == 2024, -1, year - bureau)
replace rel_clean = -5 if rel_clean <= -5  // 截尾远端
replace rel_clean = 6 if rel_clean >= 6
gen rel_clean_pos = rel_clean + 5          // Stata 因子变量不接受负值

* 3. 回归（ib4 = rel_time=-1 为基准）
reghdfe Y ib4.rel_clean_pos $controls, absorb(Stkcd year) vce(cluster prov_id)
```

## 适用条件

- 至少有 1 个省份在样本期内从未经历处理
- 若从未处理省份少于总省份的 10%，估计不稳定
- 主回归仍用全样本 TWFE（纯控制组仅在事件研究中用作 robustness）

## 验证对比

同时跑两种控制组设定，对比 post-treatment 系数是否在后几期出现差异：

| rel_time | 全样本控制组 | 纯控制组 | 差异 |
|:---:|:---:|:---:|:---:|
| t+2 | 不显著 | 显著 | 控制组污染导致低估 |
| t+3~t+6 | 不显著 | 显著 | 同上 |

## 参考文献

- Goodman-Bacon (2021). Difference-in-differences with variation in treatment timing.
- Callaway & Sant'Anna (2021). Difference-in-differences with multiple time periods.
- Sun & Abraham (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects.
