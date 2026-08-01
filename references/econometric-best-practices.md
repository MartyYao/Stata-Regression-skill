# 计量最佳实践

> Stata 实证分析默认规范。每条可以偏离，但必须**有意识地偏离并注释原因**。
> 改编自 codex-stata-for-economists econometric-best-practices。

---

## 1. 标准误

**默认：在最高可行层级聚类。**

| 场景 | 默认聚类 | 依据 |
|------|---------|------|
| 面板数据 | 个体（firm, individual） | 个体内序列相关 |
| DID 状态级处理 | 州/省 | 州内相关（Bertrand–Duflo–Mullainathan 2004） |
| 处理分配层级变化 | 处理分配层级 | Abadie–Athey–Imbens–Wooldridge 2023 |
| 少聚类（G < ~30） | wild bootstrap（`boottest`） | t 分布不可靠 |
| IV / 2SLS | 同 OLS 的聚类层级 | 一致性 |

`robust`（异方差稳健但不聚类）是 **错误默认**——当组内相关可能存在时。如果用 `robust`，必须在 do 文件注释中说明为何无需聚类。

---

## 2. 固定效应

- `reghdfe` 处理高维 FE 吸收；注释 `absorb()` 层级选择理由
- 自动去除 singletons（`dropsingleton`），在 log 中报告去除前后的 N
- 双聚类：`reghdfe ..., cluster(unit time)`——声明两个维度
- 多期 DID 事件研究：优先用 `csdid`、`eventstudyinteract` 等异质稳健估计量，避免经典 TWFE 的 forbidden comparisons

---

## 3. 样本选择

每个分析 do 文件必须在 log 中记录样本量变化：

```stata
display "样本限制前 N: " _N
keep if <condition_1>
display "限制1后（<理由>）: " _N
keep if <condition_2>
display "限制2后（<理由>）: " _N
```

审稿人可从 log 单独重构整个样本漏斗。

---

## 4. 权重

| Stata 权重 | 何时用 |
|-----------|--------|
| `pweight` | 抽样权重（总体推断），几乎总是调查数据 |
| `aweight` | 分析权重（单元格均值方差），DV 是组均值时 |
| `fweight` | 频率权重，每行代表 N 个观测 |
| `iweight` | 重要性权重——极少用，特定命令才行 |

`pweight` 和 `cluster()` 同时用前，确认该命令同时支持两者。

---

## 5. 工具变量

- 每个 IV 规格**必须报告第一阶段 F 值**
- 单内生+单工具：用 Olea–Pflueger `weakivtest`
- 多工具：`ivreg2` + `ranktest`，报告 Kleibergen–Paap rk Wald F
- F < 10：红旗。F < 24（Lee et al. 2022）：需报告 Anderson–Rubin CI
- 少聚类下的 IV 推断：`boottest`

---

## 6. 多重假设检验

如果 do 文件在同一结果族上估计 ≥5 个系数，报告：
- **原始 p 值**，以及
- **调整后 p 值**：Bonferroni（保守）、Holm（略松）、或 Romano–Wolf（`rwolf` 包）

在表格注释中标明使用哪种调整方法。

---

## 7. DID 专项

- **显式展示预处理趋势**：事件研究的处理前系数联合不显著
- **可视化**：事件研究图（滞后+超前系数 + 95% CI）
- **稳健性**：至少 TWFE + 一种异质稳健估计量（`csdid` / `did_multiplegt` / `eventstudyinteract`）并列
- **Honest DiD**：`honestdid` 敏感性检验（平行趋势假设可能违反时）

---

## 8. 自助法与模拟

- 生产用自助法次数 ≥999；开发用 99/199（在代码中标注）
- 少聚类（G < ~30）用 wild cluster bootstrap（`boottest`）
- `set seed` 在文件顶部设一次，绝不在循环内设
- 保存自助法分布（`saving()`）供审稿人审计

---

## 9. 回归表报告

每个回归表必须包含：

| 条目 | Stata | 备注 |
|------|-------|------|
| N | `stats(N ...)` | 必报 |
| Adj R² | `stats(r2_a ...)` | 必报 |
| 因变量均值 | `stats(mean_dep ...)` | 建议报告 |
| 聚类层级+数量 | `addnotes()` | 必报 |
| FE 包含 | `addnotes()` | 必报 |
| 控制集标识 | 列标题 | 必报 |

`esttab` 标准调用：

```stata
esttab m1 m2 m3 using "output/tables/<name>.csv", replace ///
    cells(b(star fmt(4)) t(fmt(4))) ///
    stats(N r2_a, fmt(0 3)) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    nonumbers nomtitles collabels(none) label ///
    addnotes("括号内为 t 值" "标准误聚类在 [层级] 层面")
```

---

## 10. 稳健性

每篇论文的 do 文件应产出**逐一变动**的稳健性检验：

- 替换 DV 定义（V1 → V2）
- 替换样本限制（换窗口期、剔除极端值）
- 替换聚类层级（个体→州→行业）
- 替换 SE 方法（聚类→`boottest`→稳健）
- 替换 FE 规格
- 剔除有影响力的观测 / 更换 winsorize 阈值
