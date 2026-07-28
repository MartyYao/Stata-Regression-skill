# Stata Regression Skill

> 面向实证经济学论文的 Stata 编码规范、出图标准、表格格式与计量质量检查清单。
> Designed for AI coding assistants — Claude Code, Codex, Kimi Code, Cursor, and any agent that reads local context files.

---

## 这是什么？

当 AI 编程助手写 Stata do-file 时，最常见的问题是：**回归怎么写才规范？图怎么才不丑？表格怎么输出才能直接投稿？** 这个技能就是为此准备的。

它把一篇实证经济学论文从数据清理到最终表格和图形输出的全流程，拆解为可复用的编码规范、出图模板和检查清单。AI agent 按路由表逐步加载对应 reference 文件，而不是凭训练记忆拼凑命令。

---

## 它能做什么

### 1. Do-file 编码规范

| 能力 | 说明 |
|------|------|
| 标准化 header | 每条 do 文件按统一模板：File/Project/Inputs/Outputs/Log |
| 安全样板代码 | `version`、`set more off`、`set varabbrev off`、logging、seed |
| esttab 输出纪律 | CSV 加 `plain` 选项，同时出 LaTeX 备选 |
| 禁止模式清单 | `cd` 绝对路径、循环内 `set more off`、`varabbrev on` 等 |
| 完整模板框架 | 三列逐步回归的 do 文件可直接改变量名使用 |

### 2. 图形质量标准

| 能力 | 说明 |
|------|------|
| 标准色板 | 焦点系列 `#3191FF`、对比系列 `#8EA4B8`、参考线 `#808080` |
| 线型规格 | 焦点实线、对比虚线、参考线细虚线 |
| 导出双格式 | 每张图同时出 PDF（vector）+ PNG（1800px width） |
| 白色背景 | 无边框、仅水平网格线 |

### 3. 即用出图模板

| 图类型 | 模板 |
|--------|------|
| 事件研究 / 平行趋势检验图 | `coefplot` + 手动 `rcap + scatter` |
| 系数图（单模型 / 多模型对比） | `coefplot` |
| 异质性分析图（多 Panel） | 水平系数排列 |
| 边缘效应图 | `margins` + `marginsplot` |
| 趋势图 | `collapse` → `twoway line` |
| 分布图 | `histogram` / `kdensity` |
| DID 动态效应 | `csdid_plot` |
| 安慰剂检验图 | 随机置换分布 + 真实系数参考线 |
| RD 图（断点回归） | `rdplot` / `binscatter` |

### 4. 表格输出标准

| 能力 | 说明 |
|------|------|
| esttab CSV 输出 | 系数 4 位 + t 值 4 位 + 星号，`plain` 选项 |
| esttab LaTeX 输出 | booktabs 三线表，含完整 prehead/postfoot |
| 多列分组 | Panel A/B 分组，`\cmidrule` |
| 描述统计 | tabstat → 3 位小数 |
| 相关系数矩阵 | pwcorr + 显著性标记 |
| CSV → Pipe Table | `scripts/esttab2pipe.py` 一键转换 |

### 5. 计量质量检查（10 条）

| # | 检查项 | 核心要求 |
|---|--------|---------|
| 1 | 标准误 | 最高聚合层级聚类，G < 30 用 wild bootstrap |
| 2 | 固定效应 | 记录 absorb 变量和 singleton 处理 |
| 3 | 样本记录 | log 中重建样本漏斗 |
| 4 | IV 检验 | 报告第一段 F，F < 10 是红旗 |
| 5 | DID | 平行趋势检验必须展示，staggered 用 csdid |
| 6 | 离群值 | winsorize 1%/99%，检查稳健性 |
| 7 | 多重假设 | >= 5 个系数时报告校正 p 值 |
| 8 | 表格完整性 | N、Adj. R²、DV 均值、聚类数、全部系数 |
| 9 | 稳健性 | 每次只变一个参数 |
| 10 | Log 验证 | 每个数值必须有 log 源 |

### 6. 高频陷阱速查（24 条）

覆盖：
- 数据与回归陷阱（`corr` → `pwcorr`、大额变量未取对数等）
- Stata 语法陷阱（因子变量负值、esttab keep 不匹配等）
- 工作流陷阱（`read_file` + `write_file` 污染、zsh glob 冲突等）
- CSMAR 数据陷阱（变量类型不一致、winsor2 未安装等）
- DID 多期陷阱（误删对照组、TWFE forbidden comparisons）
- 处理强度陷阱（二元分组不如连续得分）
- 机制检验陷阱（固定特征做 M、研发投入内生性）

---

## 快速使用

### Claude Code

项目根目录放 `CLAUDE.md`：

```markdown
## Stata 编码规范
写 Stata do-file 前，读取 skills/Stata-Regression-skill/ 下的 SKILL.md，按路由表加载对应 reference 文件。
```

### Codex

项目根目录放 `AGENTS.md`，内容同上。

### 任意 Agent

将 `SKILL.md` 路径告知 Agent，按路由表逐步加载。

---

## 输出管线

```
Stata do 文件
  ├─ esttab → .csv (plain)  → scripts/esttab2pipe.py → markdown pipe table
  ├─ esttab → .tex (booktabs) → 备选 LaTeX 投稿
  └─ graph export → .pdf + .png
```

---

## 目录结构

```
stata-regression/
├── README.md                          ← 本文件
├── AGENTS.md                          ← Codex 入口
├── CLAUDE.md                          ← Claude Code 入口
├── SKILL.md                           ← 主路由表 + 执行协议
├── references/
│   ├── do-file-standards.md           ← Do 文件编码规范 + 完整模板
│   ├── table-standards.md             ← esttab 输出标准 + pipe table 规范
│   ├── graph-standards.md             ← 图形质量标准（RGB 色号/线型/导出）
│   ├── graph-templates.md             ← 9 类出图模板
│   ├── econometric-checklist.md       ← 10 条计量质量检查
│   └── stata-pitfalls.md              ← 24 条高频陷阱速查
└── scripts/
    └── esttab2pipe.py                 ← esttab CSV → markdown pipe table
```

---

## 设计原则

### 为什么要分 SKILL.md + references/？

**渐进式加载**。SKILL.md 是路由表（~100 行），只告诉 Agent 哪个任务读哪个文件。Agent 不会一次性加载全部内容，而是按需读取对应 reference。这与 dylantmoore/stata-skill（272★）和 YoungFujun/stata-graphics-skill 的理念一致。

### 与同类项目的区别

| 项目 | 定位 | 与本文差异 |
|------|------|-----------|
| dylantmoore/stata-skill | Stata 语法参考大全（37 文件 + 20 包） | 本文聚焦**论文级工作流**而非语言参考 |
| YoungFujun/stata-graphics-skill | Stata 出图专项参考（14 文件） | 本文将出图与回归/出表/检查整合为完整流水线 |
| maxwell2732/codex-stata-for-economists | Codex 项目模板（AGENTS.md + rules/） | 本文独立于特定 Agent，Claude/Codex/Kimi 皆可用 |
| 本技能 | **论文全流程 Stata 编码规范** | 从 do 文件模板 → 回归 → 出图 → 出表 → 检查的完整闭环 |

---

## 致谢

本技能参考了以下开源项目，在此表示感谢：

- **[maxwell2732/codex-stata-for-economists](https://github.com/maxwell2732/codex-stata-for-economists)**（199★）— Do-file 编码规范（header/boilerplate/logging）、图形色彩标准（RGB 色号/线型）、计量最佳实践 10 条。本技能的 `do-file-standards.md` 和 `econometric-checklist.md` 以此为基础裁剪和适配。

- **[dylantmoore/stata-skill](https://github.com/dylantmoore/stata-skill)**（272★）— estout/esttab 出版级表格模板（AER Style）、输出格式（CSV/LaTeX/RTF）。本技能的 `table-standards.md` 中的 LaTeX 三线表模板和 esttab 选项参考自此项目。

- **[YoungFujun/stata-graphics-skill](https://github.com/YoungFujun/stata-graphics-skill)**（22★）— 渐进式路由表设计理念、出图模板分类、图形坑点清单。本技能的 `SKILL.md` 路由结构和 `graph-templates.md` 的模板分类借鉴了此项目的三层架构。

### 本技能的改进

相比于上述参考项目，本技能做了以下整合与增强：

| 改进 | 说明 |
|------|------|
| **论文全流程闭环** | 从 do 文件模板 → 回归 → 出图 → 出表 → 质量检查，单一技能覆盖完整实证循环 |
| **独立于特定 Agent** | 同时提供 AGENTS.md（Codex）、CLAUDE.md（Claude Code）、SKILL.md（通用），无需插件系统 |
| **中文优先** | 所有注释、模板、说明以中文撰写，降低中国经管研究者使用门槛 |
| **附赠转换工具** | `esttab2pipe.py` 将 esttab CSV 一键转为 markdown pipe table，填补了 CSV → 可读表格的缺失环节 |
| **CSMAR 数据陷阱** | 新增 CSMAR 数据特有的 6 条陷阱（变量类型不一致、Accper 日期解析等），来自实战踩坑记录 |
| **DID 多期陷阱** | 补充 staggered DID 的三个具体坑（对照组误删、基期选择、TWFE forbidden comparisons） |
| **多轮审查修复** | 经 Kimi Code K3 和 Claude Code 两轮审查共修复 20+ 个问题（负 t 值正则、coeflabels 通配覆盖、predictnl 伪代码等） |
| **可复现 CSS** | 附带 Obsidian CSS 片段，pipe table 预览时可渲染为专业三线表 |

---

## 技术规范速览

| 规范 | 标准 |
|------|------|
| 系数小数位 | 4 位 |
| 括号内 | t 值（非标准误） |
| 控制变量 | 逐行列全部系数，不可用 ✓ |
| 显著性标记 | * p<0.10, ** p<0.05, *** p<0.01 |
| 焦点系列颜色 | RGB 49 145 255 (`#3191FF`) |
| 对比系列颜色 | RGB 142 164 184 (`#8EA4B8`) |
| 图形导出 | PDF + PNG (1800px width) |
| 聚类 SE | 最高聚合层级 |

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| **v0.1.1** | 2026-07-28 | 新增「推荐项目目录结构」规范（do 文件/log/表格/图形/旧文件的分类存放规则、命名约定、禁止模式） |
| **v0.1.0** | 2026-07-27 | 初始发布。Do 文件编码规范、9 类出图模板、esttab 表格输出标准、10 条计量检查、24 条陷阱速查、esttab2pipe.py 转换工具 |

---

## 许可证

MIT
