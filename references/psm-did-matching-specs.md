# PSM-DID 匹配方案规范（多期 DID）

> 来源：2026-07-30 实测验证（论文"数字政府与补贴配置效率"）。经管之家共识：多期 PSM-DID 的标准做法是"逐年 PSM"（B 站专栏 cv5089953 免费教程；论坛 19 元付费代码是抄它的骗局）。

## 铁律

**匹配变量必须时不变。** 多期 DID 中 `post` 是时变的（处理前=0、处理后=1），用它做 `psmatch2 post ...` 会让同一家企业跨年既当控制组又当处理组——**自己匹配自己**。检测信号：`_weight` 分布出现 >1 的异常值（实测最高 52）。`_weight` > 1 即匹配错误，结果作废。

## 方案 A：ever_treated 截面匹配（推荐主版本）

企业层面一次性匹配，权重固定：

```stata
* 1. 构造时不变处理变量
gen yr = year if post == 1
bysort prov_id: egen bureau_year = min(yr)
replace bureau_year = 2024 if missing(bureau_year)   // never-treated 赋样本期后
drop yr
gen byte ever_treated = (bureau_year != 2024)

* 2. 处理前协变量均值（处理组取各自处理前年份；从未处理组取固定基期如 2015-2017）
foreach v in Size Lev ROA SOE Growth TobinQ FirmAge Top1 {
    gen pre_`v' = `v' if (ever_treated == 1 & year < bureau_year) | (ever_treated == 0 & year <= 2017)
}

* 3. 企业层面 1:1 匹配
preserve
collapse (mean) pre_* (max) ever_treated, by(Stkcd)
psmatch2 ever_treated pre_Size pre_Lev pre_ROA pre_SOE pre_Growth pre_TobinQ pre_FirmAge pre_Top1, ///
    logit neighbor(1) common caliper(0.05)
gen byte firm_matched = (_treated == 1 | (_treated == 0 & _weight > 0))
keep Stkcd firm_matched
tempfile matched_firms
save `matched_firms', replace
restore
merge m:1 Stkcd using `matched_firms', keep(master match) nogen
replace firm_matched = 0 if missing(firm_matched)

* 4. 主回归 / 平行趋势：if firm_matched == 1
```

**自动排除**：处理前无观测的企业（样本期开始即已处理的省份；处理前新上市企业）——logit 遇缺失 pre_* 自动丢弃，属正常样本代价，不必手工处理。

## 方案 B：逐年 PSM（稳健性补充）

每年将"当年新受处理"企业与"从未受处理"企业用当年协变量 1:1 匹配，逐年累积：

```stata
clear
tempfile all
save `all', replace emptyok

forvalues y = 2015/2023 {
    use working_data.dta, clear
    * ...（构造 bureau_year / ever_treated，同方案 A）...
    keep if year == `y'
    gen byte treat_now = (bureau_year == `y')
    count if treat_now == 1
    local n_treat = r(N)
    if `n_treat' > 0 {
        keep if treat_now == 1 | ever_treated == 0
        psmatch2 treat_now Size Lev ROA SOE Growth TobinQ FirmAge Top1, ///
            logit neighbor(1) common caliper(0.05)
        gen byte in_match = (_treated == 1 | (_treated == 0 & _weight > 0))
        keep Stkcd year in_match
        duplicates drop Stkcd year, force   // 防累积重复
        append using `all'
        save `all', replace
    }
}
* 合并回主数据后：bysort Stkcd: egen firm_matched = max(in_match)
```

**坑**：循环累积 tempfile 时必须 `duplicates drop Stkcd year`（Stata 报 r(459) merge 不唯一）；`r(N)` 先存 local 再用，`di` 里的 r(N) 会被后续 keep 覆盖。

## 平行趋势修复边界（重要）

PSM 只能修复**可由可观测特征解释**的组间不平衡。若子样本（如残差法按符号拆分的 under 组）的处理组/控制组结构性不同（行业集中、盈利模式差异超出协变量范围），两种 PSM 方案都修不好前趋势——这是**真正的识别限制**，应降级该子样本的结论（如降为补充分析），而不是继续试匹配方法。

## 报告规范

- PSM-DID 定位是**稳健性检验**，不是主识别（经管之家 17 楼共识："野路子"，政策不完全外生时才需要）
- 匹配后仍要平行趋势检验（匹配只平衡可观测特征）
- 两种方案都跑时：以方案 A 为主版本，方案 B 作稳健性
- 机制检验只跑全样本，不在 PSM 样本上重复（用户明确纠正 2026-07-30）
