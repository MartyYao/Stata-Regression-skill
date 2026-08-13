---
name: stata-regression
description: Use when writing Stata do-files for empirical papers.
version: 0.2.5
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

## 交流用语规范（用户纠正 2026-07-31）

- 与用户交流实证内容时**避免英文缩写**（DV/IV/PT/FE 等）——用户问过"DV是啥"。
  用中文全称：被解释变量/解释变量/平行趋势/固定效应；首次使用缩写时附全称。
- 概念名词先给定义再展开（如"基期"有两种含义：事件研究基期 = t-1 vs 分组基期 =
  处理前最后一期，须区分），不要假设用户记得构造细节。

## 执行协议

每段 Stata 代码编写前按以下顺序执行：

**Step 1 — 路由**：查下面的 Routing Table，确认任务类型和对应 reference 文件

**Step 2 — 读模板**：打开对应 reference，找到最近似的模板或规范

**Step 3 — 适配**：结合 paper-workflow 提供的变量名、回归顺序、论文逻辑，组合成 do 文件

**Step 4 — 检查**：对照 econometric-checklist.md，确认回归参数无误

**Step 5 — 输出**：运行 do 文件，用 `esttab2html.py` 将 .csv 转为 .html；esttab 直接出 .rtf

## 快速诊断运行模式

当用户只要求看结果（不保存表格）时，用以下三步骤：

1. **写 do 文件**：内容包含目标分析 + 完整控制变量 + 固定效应，并在开头加 `log using "/tmp/<name>.log", replace text`
2. **运行**：`cd "/Applications/Stata 18" && ./StataMP.app/Contents/MacOS/stata-mp -b do /tmp/<name>.do`（必须 `-b` 才有 log；`-e` 模式不写 log 文件）
3. **读 log**：`cat /tmp/<name>.log | grep -v "^>"`（过滤 heredoc 行）

**典型场景**：平行趋势快速核对、IV 第一阶段 F 值验证、系数方向确认。
**注意**：macOS 上 Stata 必须从安装目录启动（license 定位），CWD 是安装目录不是项目目录——do 文件内显式 `cd` 到数据目录。

## 回归表强制规范（CSSCI 期刊标准）

以下规范为硬性要求，违反即退回：

1. **常数项**：必须包含 `_cons` 行，禁止 `drop(_cons)` 或 `keep()` 中省略
2. **全系数展示**：所有变量的系数和标准误必须列示，不得用省略号替代。回归表内不允许出现 `...` 或空白省略控制变量
3. **固定效应**：标注为 `企业固定效应` 和 `年份固定效应`，不可简写为 `FE`
4. **Adj R²**：必须内嵌于表格最后两行之一，与 N 相邻
5. **聚类层级**：在表注中说明 `省份层面聚类稳健标准误`
6. **星号标注**：`* p<0.10 ** p<0.05 *** p<0.01` 写在表注中。Obsidian 中用 `<sup>***</sup>` 实现上标小角标
7. **标准误括号**：每行系数下方紧跟括号内标准误，格式 `(0.0038)`。**此规则适用于 HTML/RTF 展示管线**（`b(4) se(4)`）；TeX/数据存档管线（`cells(b t)`）括号内为 **t 值**——两条管线并存，见 `table-standards.md` §5
8. **空白单元格**：以 `—` 填充，不用空格
9. **双格式输出**：HTML（→ Obsidian 预览）+ RTF（→ Word 投稿），.csv 经 esttab2html.py 出 .html，esttab 直接出 .rtf
10. **样本量 & Adj R² 对齐**：N 和 Adj R² 行左对齐，系数无缩进

## 图形输出强制规范

1. 平行趋势检验必须对 dev、over、under 三个指标分别出图（如果样本覆盖）
2. 所有图形导出 PDF + PNG 双格式到 `output/figures/`
3. 图形必须具有：白色背景、无外边框、参考线虚线、轴标签

## Routing Table

### 回归任务

| 任务 | 先读 | 再读 |
|------|------|------|
| 写一条完整回归 do 文件 | `do-file-standards.md` | `table-standards.md`（esttab 选项）；可直接套用 `templates/master-do-template.do` |
| DID 基准回归 + 平行趋势 + 事件研究 | `do-file-standards.md` | `graph-templates.md`（事件研究图） |
| IV 回归（第一/二阶段） | `do-file-standards.md` | `econometric-checklist.md`（IV 检查） |
| 机制检验 | `do-file-standards.md` | `table-standards.md`（机制表格式见 sec 2 多列分组） |
| 异质性分析 | `do-file-standards.md` | `table-standards.md`（异质性子表见 sec 2 多列分组） |
| 描述统计 + Table 1 | `do-file-standards.md` | `table-standards.md`（tabstat 格式） |

* 执行顺序见 `do-file-standards.md` §10 分析顺序

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
| 匹配平衡性图（Love plot / 标准化偏差） | `graph-standards.md` | `graph-templates.md` → Love plot 节 |
| DID 动态效应（csdid_plot） | `graph-standards.md` | `graph-templates.md` → sec 1 CSDID 替代 |
| 安慰剂检验图 | `graph-standards.md` | `graph-templates.md` → 安慰剂节 |
| RD 图 | `graph-standards.md` | `graph-templates.md` → RD 节 |

### 出表任务

| 表类型 | 参考文件 |
|--------|---------|
| 回归表（esttab → Obsidian） | `table-standards.md` → esttab 输出节 + esttab2html.py |
| 回归表（esttab → Word 投稿） | `table-standards.md` → esttab 输出节（同一管线） |
| 描述统计（tabstat） | `table-standards.md` → tabstat 节 |
| 相关系数矩阵（pwcorr） | `table-standards.md` → 相关系数节 |

### 版本管理任务（v0.2.5）

| 任务 | 工具 | 用法 |
|------|------|------|
| 开新 run（归档旧表 + 建 tag 目录 + MAPPING） | `scripts/rerun.sh` | `bash rerun.sh new "20260813_v4"`（do 模板 `global TAG` 配合） |
| 查看当前 run 状态 | `scripts/rerun.sh` | `bash rerun.sh status` |
| 正文数字 vs CSV 对账（准入审查/审计） | `scripts/verify-numbers.py` | `python3 verify-numbers.py <正文md> --tables output/tables/<tag>/ --state-line` |

> **铁律（2026-08-13 定案）**：CSV 只允许输出到 `output/tables/$TAG/`（do 模板已强制），禁止写根目录——原地覆盖是"正文数字追溯无门"的根源。开新 run 必须走 rerun.sh，旧表自动归档到 `output/archive/tables_<旧tag>/`。

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
| 11 | 事件研究图竖线错位（画在 rel=1 而非 0） | xline 用了期数标签而非 x 坐标 | 竖线 = `xline(偏移量)`（x = rel_time + 偏移，0 期 → xline(6)） |
| 12 | 事件研究图漏画最后一期（+6 无点） | `set obs` 少于期数 | `set obs` = 全部期数（-5..+6 → 12），`forvalues` 同步 0/11 |

> 完整陷阱列表见 `references/stata-pitfalls.md`（41 条：25 条基础坑 + 14 条实战坑 + 2 条速查对齐）

## 实战经验（2026-07 实证项目沉淀）

### IV F 值读取（实测 2026-07-30）

- `ivreghdfe` 估计后 KP rk Wald F 在 `e(widstat)`，直接 `di e(widstat)` 读取（estat firststage 在 ivreghdfe 后可能静默无输出）
- `ivreg2 ... partial(Stkcd year)` 报 `r(198)`——partial() 里的变量必须同时在回归列表中；高维固定效应场景直接用 ivreghdfe 替代
- **`ivreg2` 不支持 reghdfe 风格的 `absorb(Stkcd year)` 语法**——会静默失败（`capture` 下无输出，e(widstat) 取不到）；reghdfe 第一阶段无 `_varb` 矩阵（那是 ivreg2 的），交互项组合效应（post+post×flip 等）用 `lincom` 计算
- 单工具变量时第一阶段 t² ≈ KP F（快速估算），但报告值以 ivreghdfe/ivreg2 输出的 e(widstat) 为准
- reghdfe 表头的 e(F) 是模型整体 F，**不是**弱工具变量检验值；报告 IV 只写 KP rk Wald F + Stock-Yogo 临界值

### 机制检验专项

- **三步法不可用于固定特征 M**（pc_any/SOE/srdi_any）——M 必须有时序变异
- **研发投入类变量做 M 的内生性**——补贴→研发存在反向因果
- **经济后果全不显著**——从唯一通过的那条倒退故事，不强凑
- **机制批量探索策略**：先批量跑 Step2（M~post），p<0.05 的才进 Step3

### 诊断方案参考（实证踩坑的完整方法论）

| 场景 | 参考文件 |
|------|---------|
| 平行趋势不通过 → HonestDiD 敏感性分析（Rambachan & Roth 2023），含 e(b) 基期列提取坑、numpre + 显式矩阵调用、论文表述模板 | `references/honestdid-stata-notes.md` |
| 事件研究"事前显著正→事后显著负"倒 V 型 → 四种解释与判别检验，符号一致子样本是关键 | `references/inverted-v-pretrend-diagnosis.md` |
| 多期 DID 的 PSM 匹配（ever_treated 时不变铁律、逐年 PSM、_weight>1 异常信号） | `references/psm-did-matching-specs.md` |
| PSM 后平行趋势仍失败 → 成员切换 vs 真实趋势诊断 | `references/psm-parallel-trends-diagnosis.md` |
| 事件研究控制组污染 → 纯控制组设定（never-treated 省份 rel_time=-1） | `references/pure-control-event-study.md` |
| 残差法 over/under 拆分后跨组动态（无阈值连续分解三边际 DID、基期状态分组、θ 任意性） | `references/cross-group-dynamics-decomposition.md` |
| 残差法子样本 suppress/翻转效应诊断 | `references/suppression-effect-diagnosis.md` |
| 计量规范全文（聚类/固定效应/权重/自助法/HonestDiD/表报告） | `references/econometric-best-practices.md` |

## 依赖包

```stata
ssc install reghdfe ftools estout ivreg2 ranktest boottest csdid eventstudyinteract psmatch2 pstest honestdid coefplot, replace
```

- `psmatch2`：PSM 匹配（psm-did-matching-specs.md 必需）
- `honestdid`：HonestDiD 敏感性分析（honestdid-stata-notes.md 必需）
- `coefplot`：系数图/事件研究图（graph-templates.md、master-do-template.do 必需）

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
    ↓ 写 do 文件 → 跑回归 → esttab2html.py → .html + .rtf
    ↓ 对照检查清单验证结果
    ↓ paper-workflow 组件决策门判断
```

调用方式：paper-workflow 在每次阶段 4 或阶段 5 进入时执行 `skill_view(name='stata-regression')`，然后根据路由表按需加载对应 reference。

## 输出管线

```
Stata do 文件
  └─ esttab → .csv (plain) → esttab2html.py → .html
  └─ esttab → .rtf → merge_rtf.py → 附录-实证表格.rtf

Obsidian: .html 直接插入预览（三线表 inline 样式）
Word投稿: .rtf 打开即可用（esttab 原生输出，Word 格式完整）
  └─ .rtf 文件 → merge_rtf.py → 附录-实证表格.rtf（合并投稿）
```
