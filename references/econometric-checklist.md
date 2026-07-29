# Econometric Checklist — 计量质量检查 10 条

## 每条 do 文件跑完后逐项确认

---

### 1. 标准误：在最高聚合层级聚类

| 场景 | 默认聚类 | 理由 |
|------|---------|------|
| 面板数据 | 企业层面（`Stkcd`） | 企业内部序列相关 |
| DID，处理在省份层面 | 省份（`province`） | 省内企业残差相关（Bertrand, Duflo & Mullainathan 2004） |
| 处理变量在同一层级分配 | 处理分配层级 | 标准误反映处理分配层级的变异（Abadie, Athey, Imbens & Wooldridge 2023） |
| 聚类数少（G < ~30） | wild bootstrap（`boottest`） | t 分布不可靠 |
| IV / 2SLS | 与 OLS 相同层级 | 一致性要求 |

**不聚类（`robust` 仅异方差稳健）是错误默认**。除非注释说明为何不需要聚类。

**每条 do 文件必须报告聚类层级和聚类数**：

```stata
display "Cluster variable: province"
display "Number of clusters: "
tabulate province if e(sample)
```

---

### 2. 固定效应：记录 absorb 变量和 singleton 处理

```stata
reghdfe over_v1 post $controls, absorb(Stkcd year) vce(cluster province)
```

- 在注释中记录 `absorb()` 选择理由
- 记录 singleton 处理情况（`dropsingletons` 是 reghdfe 默认）
- 报告吸收后的 N

---

### 3. 样本记录：log 中重建样本漏斗

每步样本限制必须在 log 中记录：

```stata
display "Full sample N: " _N
keep if in_sample_condition
display "After restriction [理由]: " _N
keep if another_condition
display "After restriction [理由]: " _N
```

审稿人应能从 log 单步重建样本量变化。

---

### 4. 工具变量：报告第一段 F 值和弱 IV 检验

```stata
* ivreg2 需要 ssc install ivreg2
ivreg2 over_v1 ($instrument = $exogenous), robust
estat firststage
```

- F < 10 是红旗
- F < ~24（Lee et al. 2022）→ 报告 Anderson-Rubin CI
- 多 IV 时报告 Kleibergen-Paap rk Wald F

---

### 5. DID：平行趋势检验必须展示

| 检验 | 命令 | 通过标准 |
|------|------|---------|
| 事件研究图 | `coefplot` 或手动 `rcap + scatter` | 处理前系数不显著异于 0 |
| 事件研究系数 | 同上 | 处理前 joint F-test 不显著 |
| CSDID（heterogeneity-robust） | `csdid` + `estat pretrend` | staggered DID 时强制做 |

- 只用 TWFE 不够 → 处理时间交错时必须加 `csdid` 或 `eventstudyinteract`

---

### 6. 离群值：winsorize 报告

```stata
* 替代 winsor2（防止未安装）
foreach var in `vars' {
    qui sum `var', d
    replace `var' = r(p1) if `var' < r(p1) & !missing(`var')
    replace `var' = r(p99) if `var' > r(p99) & !missing(`var')
}
```

- 报告 winsorize 阈值（默认 1%/99%）
- 检查关键结果在 1%/5% winsorize 下是否稳健

---

### 7. 多重假设检验

如果同一回归家族产出 >= 5 个系数（如同时跑 5 个机制变量）：

- 报告原始 p 值 **AND**
- 报告校正 p 值：Bonferroni / Holm / Romano-Wolf（`rwolf`）

---

### 8. 输出格式：回归表每列报告

每条 do 文件的回归表输出最小必须包含：

- [ ] N（样本量）
- [ ] Adj. R²（或 within R²）
- [ ] FE 标注（企业/年份固定效应）
- [ ] 聚类层级（在表注中说明）
- [ ] 控制变量集（全部系数，不可用 ✓）

`esttab` 统计行：

```stata
stats(N r2_a, fmt(%9.0f %9.4f) labels("N" "Adj. R$^2$"))
```

---

### 9. 稳健性检验每次只变一个参数

| 一次变动 | 具体操作 |
|----------|---------|
| 替代 DV 定义 | V1 → V2 |
| 替代样本 | 去掉某省、缩短窗口 |
| 替代聚类 | 省份 → 城市，或双向聚类 |
| 替代 SE | 普通聚类 → wild bootstrap |
| 替代 FE | 加行业×年份 FE |
| 替换关键控制变量 | 不同控制变量组合 |

---

### 10. Log 验证：每个数值声明必须可追溯

- 所有输出的系数、SE、p 值、N 必须有 log 源
- 检查 `esttab` 输出的 .csv 存在且通过 log 验证
- 检查 `.log` 文件尾部确认 `log close` 且无 `r(###)` 错误

```bash
# Shell 中验证
tail -3 logs/03_analysis_05_main_regression.log
# 应显示 "log close" 或类似信息
```
