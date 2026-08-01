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
| 9 | `esttab` 首次输出 .csv 报 `file not found` | 无害 | 忽略，首次创建文件时的警告 |
| 10 | `esttab ... , plain` 不加 `plain` | 输出被 `=""` 包裹 | 检查 .csv：若含 `=""` 则需重新输出加 `plain` |

## 工作流陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 11 | zsh glob 与 `rm -f` 冲突 | rm -f *.csv → no matches found | 不批量清理；或 `2>/dev/null; true` |
| 12 | Stata 注释中含 `output/tables/*` | `/*` 启动 block comment → 后半文件被注释 | 用 `output/tables/` 避免 `/*` |
| 13 | `read_file` + `write_file` 污染 do 文件 | 行号前缀 `123|456|` 被写入 | **永远不**用 `read_file` 返值直接 `write_file`。改 do 文件只用 `patch` 或干净 `write_file` |

## CSMAR 数据陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 14 | CSMAR 财务数据库无 `year` 变量 | `year not found` r(111) | `gen year = year(date(Accper, "YMD"))` |
| 15 | CSMAR 变量类型不一致 | Stkcd 有时 str6 有时 long | long → `gen Stkcd_str = string(Stkcd, "%06.0f")`；string 已是对的直接 merge |
| 16 | `winsor2` 可能未安装 | command winsor2 not found | 手动替换：`sum v, d` → `replace v = r(p1) if v < r(p1)` |
| 17 | 审计意见全样本无变异 | insufficient observations r(2001) | A 股非标审计意见 < 5%，放弃该变量 |

## DID 多期陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 18 | `if !missing(rel_time)` 删除对照组 | 3066 obs 全丢 | `replace rel_time = -5 if missing(rel_time)` 保留为基期 |
| 19 | 基期选 `ib0.rel_time_pos` | 边界可能混入真实处理 | 选 `ib4.rel_time_pos`（即 rel_time=-1） |
| 20 | TWFE 中早期处理组做后期对照 | forbidden comparisons | staggered DID 用 csdid / eventstudyinteract |

## 处理强度陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 21 | 二元组间比较限定 ever-treated 子样本 | 聚类数 31→15-20，F 缺失 | 连续得分（treat_score1）全样本回归 |
| 22 | 三次项交互（实际为二次项）`treat_score1^2` | 共线性、不可解释 | 避免非线性剂量-反应；用分组替代 |

## 机制检验陷阱

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 23 | 三步法 Step 2 用固定特征做 M | X→M 永远不显著（M 时不变） | 固定特征（pc_any/SOE）只用交互项（调节效应） |
| 24 | 研发投入强度做 M 的内生性 | Step 2 显著但 Step 3 不显著 | 研发投入与补贴获取双向因果；避免或用滞后项 |
| 25 | CSMAR 现金流量表科目做寻租代理 | 方向反向不可解释 | 业务招待费在财务报表附注，不在现金流量表汇总科目 |

## 2026-07 实证项目新增（多期 DID + PSM + 残差法实战）

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 26 | 事件研究控制组污染（staggered DID） | t+2 后效应消失，与主回归矛盾 | 改用纯控制组（never-treated 省份设为 rel_time=-1） |
| 27 | `merge ... nogen` 未加 `keep(master match)` | 使用数据中的额外观测被拉入主数据集（如 25K→80K 膨胀） | 加新变量时用 `merge ... keep(master match) nogen` 保证不膨胀 |
| 28 | 多期 DID 误以为需要"永远不处理"省份 | 去搜"为什么没有控制组" | 多期 DID 中尚未处理的观测即为控制组——不需要"永远不处理"省份；纯控制组方法（#27）是审稿人稳健性要求，非 DID 必要条件 |
| 29 | PSM-DID 匹配用 `psmatch2 post ...`（时变处理变量） | 同企业跨年自己匹配自己，`_weight` 出现 >1 异常（实测最高 52），结果作废 | 匹配变量必须时不变：ever_treated 截面匹配（处理前协变量均值）或逐年 PSM（每年"当年新处理 vs 从未处理"）；跑完检查 `_weight` 分布，>1 即匹配错误信号。完整方案见 `references/psm-did-matching-specs.md` |
| 30 | 机制检验在 PSM 匹配样本上重复跑 | 样本减半导致 Step2 边缘显著（p=0.06~0.09），徒增噪声 | **机制检验只跑全样本**（用户明确纠正 2026-07-30）；PSM 仅用于主回归与平行趋势稳健性 |
| 31 | HonestDiD 提取事件研究系数含基期因子列 | e(b) 前 12 列含 `4b.rel_pos`（系数 0），`B[1,1..11]` 把基期混入 → Original 恒 0.000、CI 全对称假象 | 跳过基期列：`B[1,1..4], B[1,6..12]`；用 `numpre(4)` + 显式 `b()/vcov()`，不用 pre()/post() 位置索引。完整流程见 `references/honestdid-stata-notes.md` |
| 32 | 事件研究"事前正→事后负"倒 V 型，直接套 PSM/换基期 | 倒 V 不是简单趋势违规，事后下降可能与均值回归/子样本成员切换混淆；论坛无现成方案，瞎试浪费轮次 | 先诊断成因（均值回归/构成切换/预期效应/真实效应）：符号一致子样本是关键判别检验；PSM 可压缩但未必消除趋势；HonestDiD 定量。框架见 `references/inverted-v-pretrend-diagnosis.md` |
| 33 | 符号一致子样本（始终 under/over）筛完直接跑事件研究 | 控制组也被筛掉：纯控制组设定下从未成立省份 rel_time 恒=-1，子样本中控制组观测极少且全落基期 → pre/post 系数完全由处理组识别，"pre 不显著、post 消失"是没功效不是没效应，据此下结论被用户纠正 | 下结论前必查 `tab ever_treated if <子样本条件>` 与 `tab rel_pos if <子样本条件> & ever_treated == 0`；条件 DV 转非条件 DV（`max(0,-e_v1)` / `max(0,e_v1)`）全样本跑是干净解法 |
| 34 | 残差法 over/under 拆分后不处理跨组动态（under→over、over→under） | 非条件 DV 的 0 值混入"真命中"（-0.3→-0.05）与"翻转"（-0.3→+0.3），无法区分"向 0 收敛"与"穿过 0"；审稿人必问"从不足补成超发算不算改善"；固定 θ 阈值（25% 分位等）无理论依据会被攻击 | 主分析用**无阈值连续分解**（Δ\|ε\| = 收敛边际 + 跨组边际 + 翻转频率三边际 DID）；按**基期状态**分组做异质性（时不变分组，不引入成员切换偏误）；阈值版本仅作描述性展示。方案见 `references/cross-group-dynamics-decomposition.md` |
| 35 | 省级控制变量过度参数化（10 个省级 > 8 个企业，且高度共线） | 省级控制变量间相关性高达 0.8（urban_rate↔ln_avg_wage 0.81、sci_ratio↔ln_fiscal_ratio 0.69）；31 省聚类下省级控制过多 → 过度参数化 + 与省级政策变量 post 纠缠（bad controls）；实测 under_intensity PSM 样本加完整 10 个省级控制后系数腰斩（-0.53→-0.27，p=0.33 消失），精简到 3 个恢复边缘显著（-0.54，p=0.06） | **企业固定效应已吸收省级时不变特征**（企业不跨省移动）→ 省级控制只需处理省级时变混淆：制度 + 规模 + 结构（market_index + ln_gdp + tertiary_share）3 个足够；完整版作稳健性。选省级控制前先跑 `pwcorr` 查共线 |
| 36 | psmatch2 多策略对比（有放回/不放回/核/caliper 变体）结果全部相同 | tempfile 在 preserve 块内 save、循环内 tempfile 变量被覆盖 → 五个策略读到同一匹配（N 完全相同是红旗）；另 `(_treated == 0 & _weight > 0)` 中 _weight 为 missing 时比较返回真（Stata missing 视为无穷大）→ 未匹配控制组被误算为匹配 | 多策略对比时每个策略**单独 use 企业层面文件 → psmatch2 → 保存真实文件**（如 /tmp/fm_A.dta）再合并对比；匹配标识必须写 `(_treated == 1 \| (_treated == 0 & _weight > 0 & !missing(_weight)))`。匹配企业数不同（1990/2020/2021）才是正常 |
| 37 | PSM 样本下效应边缘显著（p≈0.06-0.07），想换 PSM 策略凑两颗星 | 五种策略（1:1 有放回/不放回/核/caliper 0.10/1:2）系数全在 -0.47~-0.53、p 全在 0.06-0.13——稳定边缘显著，**换策略凑 p<0.05 是 p-hacking**，审稿人查匹配设定即被击穿；post_lag（滞后一期）定义同样救不了（p≈0.10） | 效应边缘显著是数据事实时：报告全样本显著主证据 + 事件研究脉冲效应（t+1/t+3 显著）+ "五种匹配策略结果一致"的稳健性说明；PSM 单系数如实标注边缘显著，定位为方向一致的辅助证据 |
| 38 | Stata 命令行 do 路径含空格 | `stata-mp -b do "/Users/.../working data/xxx.do"` 报 `file .../working.do not found` r(601)——**带空格路径在命令行参数中被截断**（"working data" → "working.do"） | do 文件先 `cp` 到无空格路径（如 `/tmp/xxx.do`）再运行；或把 do 文件放在无空格目录 |
| 39 | do 文件开头缺 `cd`（相对路径 use 依赖 cwd） | 从 `/Applications/Stata 18` 启动 Stata 后 `use working_data.dta` 报 file not found——**macOS 上 Stata 必须从安装目录启动（license 定位），cwd 是安装目录不是项目目录** | do 文件开头显式 `cd "/绝对路径/数据目录"`（实测修复）；"禁止 cd"规范只适用于从项目根目录交互式运行的情形 |

## 补充（与 SKILL.md 高频速查 top10 对齐）

| # | 陷阱 | 表现 | 修复 |
|---|------|------|------|
| 40 | `reghdfe` 中途报 insufficient obs | 某列无法估计 | 检查该变量样本量 + singleton 处理（dropsingletons 是 reghdfe 默认，报告吸收前后 N） |
| 41 | 回归表用 ✓ 省略控制变量 | 投稿退回 | 逐行列全部系数和 SE，仅固定效应可用 ✅ 标注 |
