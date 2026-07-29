---
name: stata-regression
description: Use when writing Stata do-files for empirical papers.
---

# Stata Regression — 实证论文 Stata 工作流

## 触发条件

加载本技能当任务涉及：
- 编写或修改 Stata do 文件（清洗、变量构造、回归、出图、出表）
- 回归诊断（平行趋势、IV 弱工具变量、稳健性检验）
- Stata 图形输出（事件研究图、系数图、边缘效应图、趋势图）
- Stata 表格输出（esttab 回归表、描述统计）
- do 文件质量审查（聚类层级、样本记录、log 验证）

不路由（仍走 paper-workflow）：
- Paper 层面的逻辑决策（V1/V2 主次、机制检验三步法、treat_score1 策略）
- Python 数据预处理
- 论文写作与润色

## 执行协议

每段 Stata 代码编写前按以下顺序执行：

**Step 1 — 路由**：查下面的 Routing Table，确认任务类型和对应 reference 文件

**Step 2 — 读模板**：打开对应 reference，找到最近似的模板或规范

**Step 3 — 适配**：结合 paper-workflow 提供的变量名、回归顺序、论文逻辑，组合成 do 文件

**Step 4 — 检查**：对照 econometric-checklist.md，确认回归参数无误

**Step 5 — 输出**：运行 do 文件，用 `esttab2html.py` 将 .tex 转为 .html + .docx

## 回归表强制规范（CSSCI 期刊标准）

以下规范为硬性要求，违反即退回：

1. **常数项**：必须包含 `_cons` 行，禁止 `drop(_cons)` 或 `keep()` 中省略
2. **全系数展示**：所有变量的系数和 t 值必须列示，不得用省略号替代。回归表内不允许出现 `...` 或空白省略控制变量
3. **固定效应**：标注为 `企业固定效应` 和 `年份固定效应`，不可简写为 `FE`
4. **Adj R²**：必须内嵌于表格最后两行之一，与 N 相邻
5. **聚类层级**：在表注中说明 `省份层面聚类稳健标准误`
6. **星号标注**：`* p<0.10 ** p<0.05 *** p<0.01` 写在表注中。Obsidian 中用 `<sup>***</sup>` 实现上标小角标
7. **t 值括号**：每行系数下方紧跟括号 t 值，格式 `(-5.20)`
8. **空白单元格**：以 `—` 填充，不用空格
9. **双格式输出**：CSV（→ Obsidian markdown pipe table）+ TeX（→ 投稿备选）
10. **样本量 & Adj R² 对齐**：N 和 Adj R² 行左对齐，系数无缩进

## 图形输出强制规范

1. 平行趋势检验必须对 dev、over、under 三个指标分别出图（如果样本覆盖）
2. 所有图形导出 PDF + PNG 双格式到 `output/figures/`
3. 图形必须具有：白色背景、无外边框、参考线虚线、轴标签

## Routing Table

### 回归任务

| 任务 | 先读 | 再读 |
|------|------|------|
| 写一条完整回归 do 文件 | `do-file-standards.md` | `table-standards.md`（esttab 选项） |
| DID 基准回归 + 平行趋势 + 事件研究 | `do-file-standards.md` | `graph-templates.md`（事件研究图） |
| IV 回归（第一/二阶段） | `do-file-standards.md` | `econometric-checklist.md`（IV 检查） |
| 机制检验 | `do-file-standards.md` | `table-standards.md`（机制表格式） |
| 异质性分析 | `do-file-standards.md` | `table-standards.md`（异质性子表） |
| 描述统计 + Table 1 | `do-file-standards.md` | `table-standards.md`（tabstat 格式） |

### 出图任务

| 图类型 | 先读 | 再读 |
|--------|------|------|
| 事件研究 / 平行趋势 | `graph-standards.md` | `graph-templates.md` → event study 节 |
| 系数图（单模型） | `graph-standards.md` | `graph-templates.md` → coefplot 节 |
| 系数图（多模型对比） | `graph-standards.md` | `graph-templates.md` → coefplot 对比节 |
| 异质性分析图（多 panel） | `graph-standards.md` | `graph-templates.md` → 异质性节 |
| 边缘效应图（marginsplot） | `graph-standards.md` | `graph-templates.md` → 边缘效应节 |
| 趋势图 / 时间序列 | `graph-standards.md` | `graph-templates.md` → 趋势线节 |
| 分布图（kdensity / histogram） | `graph-standards.md` | `graph-templates.md` → 分布节 |
| DID 动态效应（csdid_plot） | `graph-standards.md` | `graph-templates.md` → csdid 节 |
| 安慰剂检验图 | `graph-standards.md` | `graph-templates.md` → 安慰剂节 |
| RD 图 | `graph-standards.md` | `graph-templates.md` → RD 节 |

### 出表任务

| 表类型 | 参考文件 |
|--------|---------|
| 回归表（esttab → Obsidian） | `table-standards.md` → LaTeX 输出节 + esttab2html.py |
| 回归表（esttab → Word 投稿） | `table-standards.md` → LaTeX 输出节（同一管线） |
| 描述统计（tabstat） | `table-standards.md` → tabstat 节 |
| 相关系数矩阵（pwcorr） | `table-standards.md` → 相关系数节 |
| Obsidian 三线表 CSS | `table-standards.md` → CSS 节 |

### 质量检查任务

| 检查项目 | 参考文件 |
|----------|---------|
| 聚类层级是否正确 | `econometric-checklist.md` → 标准误节 |
| 样本记录是否完整 | `econometric-checklist.md` → 样本节 |
| IV 第一段 F > 10 | `econometric-checklist.md` → IV 节 |
| 平行趋势是否检验 | `econometric-checklist.md` → DID 节 |
| 固定效应是否记录 | `econometric-checklist.md` → FE 节 |

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
| 9 | `reghdfe` 中途报 insufficient obs | 某列无法估计 | 检查该变量样本量 + singleton 处理 |
| 10 | 回归表用 ✓ 省略控制变量 | 投稿退回 | 逐行列全部系数和 SE，仅 FE 可用 ✅ |

> 完整陷阱列表见 `references/stata-pitfalls.md`

## 与 paper-workflow 的集成

本技能不替代 paper-workflow，而是作为其阶段 4-5 的技术底层：

```
paper-workflow 阶段 4（数据构建）
    ↓ 加载 stata-regression
    ↓ 获得 do 文件模板 + 编码规范 + 输出标准
    ↓ 组合 do 文件 → 跑 Stata → 验证 log

paper-workflow 阶段 5（实证分析）
    ↓ 加载 stata-regression
    ↓ 获得回归模板 + 出图模板 + 计量检查清单
    ↓ 写 do 文件 → 跑回归 → esttab2pipe.py → Obsidian 表格
    ↓ 对照检查清单验证结果
    ↓ paper-workflow 组件决策门判断
```

调用方式：paper-workflow 在每次阶段 4 或阶段 5 进入时执行 `skill_view(name='stata-regression')`，然后根据路由表按需加载对应 reference。

## 输出管线

```
Stata do 文件
  └─ esttab → .tex (booktabs fragment) → esttab2html.py → .html + .docx
                                         └─ pandoc 自动转换

Obsidian: .html 直接插入预览（三线表 CSS 渲染）
Word投稿: .docx 打开即可用
```
