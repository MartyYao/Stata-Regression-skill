# Stata 技术陷阱速查

## 数据与回归陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 1 | `corr` 多变量缺失值不同 | no observations r(2000) | 改用 `pwcorr ..., obs` |
| 2 | `preserve/restore` 在循环内溢出 | already preserved r(621) | 循环内不用 preserve；每次 reload |
| 3 | 安慰剂检验 500 轮 reghdfe | 耗时数小时 | ≤100 轮；或降至省年面板 |
| 4 | 大额绝对量变量未取对数 | 系数极小（5e-06） | `gen ln_x = ln(x)` |
| 5 | `use data, clear` 后丢失临时变量 | `ln_x not found` r(111) | 重载后 regenerate |
| 6 | 描述统计缺少控制变量 | Table 1 不完整 | 包含全部回归变量 |

## Stata 语法陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 7 | 因子变量不接受负值 | `i.rel_time` → r(452) | `gen rel_pos = rel_time + 5`, `ib4.rel_pos` |
| 8 | `esttab keep()` 不匹配因子名 | `keep(*.rel_time)` 找不到 | 改 `keep(*.rel_time_pos)` |
| 9 | esttab 首次输出 CSV | file not found | 忽略（首次创建的正常提示） |
| 10 | `esttab ... , plain` 不加 `plain` | CSV 被 `=""` 包裹 | 必须加 `plain` 选项 |

## 工作流陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 11 | zsh glob 与 `rm -f` 冲突 | rm -f *.csv → no matches found | 不批量清理；或 `2>/dev/null; true` |
| 12 | Stata 注释中含 `output/tables/*` | `/*` 启动 block comment → 后半文件被注释 | 用 `output/tables/` 避免 `/*` |
| 13 | `read_file` + `write_file` 污染 do 文件 | 行号前缀 `123|456|` 被写入 | **永远不**用 `read_file` 返值直接 `write_file`。改 do 文件只用 `patch` 或干净 `write_file` |

## CSMAR 数据陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 15 | CSMAR 财务数据库无 `year` 变量 | `year not found` r(111) | `gen year = year(date(Accper, "YMD"))` |
| 16 | CSMAR 变量类型不一致 | Stkcd 有时 str6 有时 long | long → `gen Stkcd_str = string(Stkcd, "%06.0f")`；string 已是对的直接 merge |
| 17 | `winsor2` 可能未安装 | command winsor2 not found | 手动替换：`sum v, d` → `replace v = r(p1) if v < r(p1)` |
| 18 | 审计意见全样本无变异 | insufficient observations r(2001) | A 股非标审计意见 < 5%，放弃该变量 |

## DID 多期陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 19 | `if !missing(rel_time)` 删除对照组 | 3066 obs 全丢 | `replace rel_time = -5 if missing(rel_time)` 保留为基期 |
| 20 | 基期选 `ib0.rel_time_pos` | 边界可能混入真实处理 | 选 `ib4.rel_time_pos`（即 rel_time=-1） |
| 21 | TWFE 中早期处理组做后期对照 | forbidden comparisons | staggered DID 用 csdid / eventstudyinteract |

## 处理强度陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 22 | 二元组间比较限定 ever-treated 子样本 | 聚类数 31→15-20，F 缺失 | 连续得分（treat_score1）全样本回归 |
| 23 | 三次项交互（实际为二次项）`treat_score1^2` | 共线性、不可解释 | 避免非线性剂量-反应；用分组替代 |

## 机制检验陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 24 | 三步法 Step 2 用固定特征做 M | X→M 永远不显著（M 时不变） | 固定特征（pc_any/SOE）只用交互项（调节效应） |
| 25 | 研发投入强度做 M 的内生性 | Step 2 显著但 Step 3 不显著 | 研发投入与补贴获取双向因果；避免或用滞后项 |
| 26 | CSMAR 现金流量表科目做寻租代理 | 方向反向不可解释 | 业务招待费在财务报表附注，不在现金流量表汇总科目 |
