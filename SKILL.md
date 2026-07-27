---
name: stata-regression
description: Use when writing Stata do-files for empirical papers.
---

# Stata Regression — 实证论文 Stata 工作流

## 触发条件

本技能适用于以下任务：
- 编写或修改 Stata do 文件（清洗、变量构造、回归、出图、出表）
- 回归诊断（平行趋势、IV 弱工具变量、稳健性检验）
- Stata 图形输出（事件研究图、系数图、边缘效应图、趋势图）
- Stata 表格输出（esttab 回归表、描述统计）
- do 文件质量审查（聚类层级、样本记录、log 验证）

不覆盖：
- 论文层面的逻辑决策（V1/V2 主次、机制检验协议等）
- Python 数据预处理
- 论文写作与润色

## 执行协议

每段 Stata 代码编写前按以下顺序执行：

**Step 1 — 路由**：查下面的 Routing Table，确认任务类型和对应 reference 文件

**Step 2 — 读模板**：打开对应 reference，找到最近似的模板或规范

**Step 3 — 适配**：结合具体论文的变量名、回归顺序、识别策略，组合成 do 文件

**Step 4 — 检查**：对照 econometric-checklist.md，确认回归参数无误

**Step 5 — 输出**：运行 do 文件，用 esttab2pipe.py 处理 CSV，生成标准表格

## Routing Table

### 回归任务

| 任务 | 先读 | 再读 |
|------|------|------|
| 写一条完整回归 do 文件 | `references/do-file-standards.md` | `references/table-standards.md`（esttab 选项） |
| DID 基准回归 + 平行趋势 + 事件研究 | `references/do-file-standards.md` | `references/graph-templates.md`（事件研究图） |
| IV 回归（第一/二阶段） | `references/do-file-standards.md` | `references/econometric-checklist.md`（IV 检查） |
| 异质性分析 | `references/do-file-standards.md` | `references/graph-templates.md`（异质性图） |
| 描述统计 + Table 1 | `references/do-file-standards.md` | `references/table-standards.md`（tabstat 格式） |

### 出图任务

| 图类型 | 先读 | 再读 |
|--------|------|------|
| 事件研究 / 平行趋势 | `references/graph-standards.md` | `references/graph-templates.md` → event study 节 |
| 系数图（单模型） | `references/graph-standards.md` | `references/graph-templates.md` → coefplot 节 |
| 系数图（多模型对比） | `references/graph-standards.md` | `references/graph-templates.md` → coefplot 对比节 |
| 异质性分析图（多 panel） | `references/graph-standards.md` | `references/graph-templates.md` → 异质性节 |
| 边缘效应图（marginsplot） | `references/graph-standards.md` | `references/graph-templates.md` → 边缘效应节 |
| 趋势图 / 时间序列 | `references/graph-standards.md` | `references/graph-templates.md` → 趋势线节 |
| 分布图（kdensity / histogram） | `references/graph-standards.md` | `references/graph-templates.md` → 分布节 |
| DID 动态效应（csdid_plot） | `references/graph-standards.md` | `references/graph-templates.md` → csdid 节 |
| 安慰剂检验图 | `references/graph-standards.md` | `references/graph-templates.md` → 安慰剂节 |
| RD 图（断点回归） | `references/graph-standards.md` | `references/graph-templates.md` → RD 节 |

### 出表任务

| 表类型 | 参考文件 |
|--------|---------|
| 回归表（esttab → CSV + pipe table） | `references/table-standards.md` → CSV 输出节 + scripts/esttab2pipe.py |
| 回归表（esttab → LaTeX） | `references/table-standards.md` → LaTeX 输出节 |
| 描述统计（tabstat） | `references/table-standards.md` → tabstat 节 |
| 相关系数矩阵（pwcorr） | `references/table-standards.md` → 相关系数节 |

### 质量检查任务

| 检查项目 | 参考文件 |
|----------|---------|
| 聚类层级是否正确 | `references/econometric-checklist.md` → 标准误节 |
| 样本记录是否完整 | `references/econometric-checklist.md` → 样本节 |
| IV 第一段 F > 10 | `references/econometric-checklist.md` → IV 节 |
| 平行趋势是否检验 | `references/econometric-checklist.md` → DID 节 |
| 固定效应是否记录 | `references/econometric-checklist.md` → FE 节 |

## 高频陷阱速查

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 1 | `corr` 变量缺失值不同 | no observations r(2000) | 改 `pwcorr ..., obs` |
| 2 | 因子变量不接受负值 | `i.rel_time` → r(452) | `gen rel_pos = rel_time + 5`, `ib4.rel_pos` |
| 3 | `preserve/restore` 循环内溢出 | already preserved r(621) | 循环内不用 preserve |
| 4 | `use data.dta, clear` 后丢失临时变量 | `ln_x not found` r(111) | 重载后 regenerate |
| 5 | 大额绝对量变量未取对数 | 系数 5e-06 | `gen ln_x = ln(x)` |
| 6 | esttab 首次输出 CSV 报 file not found | 无害 | 忽略 |
| 7 | Stata 注释中 `output/tables/*` → block comment | 后半 do 文件被注释 | 用 `output/tables/` 避免 `/*` |
| 8 | `esttab keep()` 不匹配因子名 | 找不到变量 | 用偏移后的变量名 |
| 9 | `reghdfe` 中途报 insufficient obs | 某列无法估计 | 检查变量样本量 + singleton 处理 |
| 10 | 回归表用 ✓ 省略控制变量 | 投稿退回 | 逐行列全部系数和 SE，仅 FE 可用 ✓ |

> 完整陷阱列表见 `references/stata-pitfalls.md`

## 输出规范

```
Stata do 文件
  ├─ esttab → .csv (plain)  → scripts/esttab2pipe.py → markdown pipe table
  ├─ esttab → .tex (booktabs) → 备选 LaTeX 投稿
  └─ graph export → .pdf + .png
```
