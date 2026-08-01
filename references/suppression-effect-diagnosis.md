# 遮掩效应 vs 中介效应的诊断

## 问题

三步法中发现 `c' > c`（加入 M 后 X 的系数变大），或者间接效应符号与总效应相反。这是**遮掩效应（suppression effect）**，不是中介效应。

## 诊断

```stata
* Step 1：总效应
reghdfe dev_v1 post $C, absorb(Stkcd year) vce(cluster prov_id)
local c = _b[post]

* Step 2：X → M
reghdfe M post $C, absorb(Stkcd year) vce(cluster prov_id)
local a = _b[post]
local se_a = _se[post]

* Step 3：X + M → Y
reghdfe dev_v1 post M $C, absorb(Stkcd year) vce(cluster prov_id)
local c_prime = _b[post]
local b = _b[M]
local se_b = _se[M]

* 间接效应
local indirect = `a' * `b'
* Sobel z
local sobel_z = (`a' * `b') / sqrt(`a'^2 * `se_b'^2 + `b'^2 * `se_a'^2)
di "间接效应 = `indirect'"
di "c' - c = `= `c_prime' - `c''"

* 判断
if `c_prime' > `c' {
    di "!!! 遮掩效应：加入 M 后主效应系数变大（c' > c）"
    di "    结果仍可报告，但不是中介变量"
}
```

## 处理方式

| 情况 | 是否可报 | 说明 |
|------|---------|------|
| 间接效应方向与总效应相反 | ❌ | 遮掩效应。M 不是中介变量，不能写入正文机制 |
| Step2 或 Step3 任一不显著 | ❌ | 三步法失败。不报中介 |
| 两条都通过、方向一致 | ✅ | 正文写中介机制 |

## 经管之家论坛确认

经管之家 thread-10728821（2021 年讨论）：提问者遇到 `c' > c` 问题，回答"可能是一些遮掩效应的体现"，结论与标准计量教材一致。

## 常见原因

遮掩效应出现的原因可能是：
1. 选择的 M 变量不是政策的主要作用渠道（政策通过其他路径影响 Y，M 只是附带现象）
2. 数据中存在两条方向相反的路径，且间接路径和直接路径分别通过不同变量传导
3. M 与 Y 的内生关系（如反向因果、遗漏变量）
