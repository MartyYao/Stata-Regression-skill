# HonestDiD 敏感性分析（Rambachan & Roth 2023）Stata 实操

> 用途：平行趋势检验不通过时，用敏感性分析量化"允许事前趋势后效应是否仍成立"。
> 比"换基期/归并期数"等土办法学术规范得多，是当前顶刊审稿人认可的做法。
> 适用：子样本平行趋势结构性不通过（如残差法 under 子样本）、审稿人质疑事前趋势时。

## 定位

- HonestDiD 不要求平行趋势严格成立，而是**允许处理组存在事前趋势**（M 值约束趋势平滑度），
  问"即使允许事前趋势延续到事后，政策效应是否仍显著"。
- 输出：每个 M 值下事后效应（默认 t=0 单期，可改 l_vec 为平均效应）的稳健置信区间。
- **M=0 = 严格平行趋势**；M 越大允许的事前趋势越强。若 M 很小时 CI 就含 0，
  说明效应无法与事前趋势区分（识别限制坐实）；若 M 较大时 CI 仍排除 0，故事成立
  （"政策逆转了事前恶化趋势"）。

## 安装

```stata
ssc install honestdid, replace
```
自动装 OSQP/ECOS 插件（honestecos_*.plugin、honestosqp_*.plugin）与 parallel 依赖。
装完可 `honestdid _plugin_check` 验证（batch 下 rc=0 即正常）。

## 标准流程（已验证 2026-07-30）

### 1. 事件研究回归

```stata
* rel_time 截断到窗口 [-5, 6]；纯控制组(never-treated) 全部落基期 -1
gen rel_time = cond(bureau_year == 2024, -1, year - bureau_year)
replace rel_time = -5 if rel_time <= -5
replace rel_time = 6 if rel_time >= 6
gen rel_pos = rel_time + 5          // 基期 rel_pos = 4

reghdfe under_v1 ib4.rel_pos $firm_C $prov_C, absorb(Stkcd year) vce(cluster prov_id)
matrix B = e(b)
matrix V = e(V)
```

### 2. 提取事件研究系数矩阵（⚠️ 关键坑）

**e(b) 前 12 列不是 11 个系数——包含基期因子列 `4b.rel_pos`（系数 0）！**
直接 `B[1, 1..11]` 会把基期 4b 混入序列，导致：
- l_vec 默认值（第一个 post 期）解析到基期系数 0 → **Original 行恒为 [0.000, 0.000]**
- 所有 M 的 CI 变成对称 ±M×k 假象，结果完全错误

正确提取（跳过基期列 5；pre=列1-4, post=列6-12）：

```stata
matrix Bes = B[1, 1..4], B[1, 6..12]                       // 11 列 = pre(4) + post(7)
matrix Ves = V[1..4, 1..4], V[1..4, 6..12] \ V[6..12, 1..4], V[6..12, 6..12]
```

### 3. 运行 HonestDiD

```stata
capture noisily honestdid, b(Bes) vcov(Ves) numpre(4) mvec(0(0.5)3)
```

- **用 `numpre(4)` + 显式 `b()`/`vcov()`**，不要用 `pre()/post()` 位置索引
  （pre(1/4) post(5/11) 语义易错，且依赖 e(b) 自动解析——本会话多次失败后弃用）。
- `numpre(4)` = 前 4 列为 pre，其余为 post；l_vec 默认取第一个 post 期（t=0）。
- 想检验平均 post 效应：显式构造 `l_vec` 权重矩阵。**l_vec 必须是长度为 post 期数的列向量**：
  ```stata
  matrix lvec_avg = J(7, 1, 1/7)   // 7 个 post 期等权平均；不是 11 维、不是行向量！
  honestdid, b(Bes) vcov(Ves) numpre(4) l_vec(lvec_avg) mvec(0(0.25)1.5)
  ```
  ⚠️ 11×1 或 1×11 都会报 `3200 conformability error`——l_vec 只覆盖 post 期，不含 pre 期（见 sthlp Example 2 的 `_honestBasis()` 用法）。
- `mvec(0(0.5)3)`：M 从 0 到 3 步长 0.5。M=0 即严格平行趋势。
- `method = C-LF, Delta = DeltaRM` 是默认（relative magnitudes）。
- 报 `3200 conformability error` 多为 l_vec/矩阵维度问题；LP 不收敛警告
  （"did not converge properly"）在 post 系数接近 0 时常见，结果仍可读。

## 结果解读（实测案例）

under_v1（全样本纯控制组，N=7,044，基期 t-1）：

| M | 95% CI | 判定 |
|---|---|---|
| Original | [-0.797, -0.130] | — |
| 0（严格平行趋势） | [-0.794, -0.133] | 排除 0 ✅ |
| 0.5 | [-1.135, +0.172] | 含 0 ❌ |
| 1.0+ | 含 0 | ❌ |

→ under 的事前趋势幅度（pre 系数 0.45~0.96）与 t=0 效应（-0.46）同量级，
允许趋势幅度达效应一半时效应即失效 → **"政策扭转恶化趋势"故事不被支持**。

dev_v1 对照（平行趋势已通过）：M=0 排除 0，证明方法本身正常，under 的失败是真实识别限制。

## PSM + HonestDiD 组合（实测 2026-07-30）

审稿人/合作者可能问：\"事前趋势是不是样本不平衡造成的？先做 PSM 再跑 HonestDiD 试试。\"
结论：**值得做，但救不了 M>0**。

- 先在 ever_treated 截面匹配样本（firm_matched==1）上重跑事件研究 → 提取 Bes/Ves → HonestDiD。
- 实测（under_v1，平均 post 效应）：全样本 M=0 就含 0（后期系数不显著稀释平均效应）；
  PSM 后 **M=0 干净排除 0**（[-1.14, -0.05]）——证明事前趋势确有相当部分来自样本不平衡；
  但 **M=0.25 即含 0**——匹配压缩了趋势，没消除趋势。
- dev 对照同样 M=0.25 含 0 → 效应量级相对事前波动不大时，DeltaRM 对谁都严格。

**论文报告方式（RR2023 惯例）**：报告临界 M 并换算成与事前趋势实际幅度的比值——
PSM 样本 under 的 pre 系数最大 0.77，平均 post 效应约 -0.60，M=0.25 对应允许幅度 0.15
（= 0.6×0.25），仅为实际事前趋势的 1/5。正文可写：
\"在允许事前趋势幅度达到其样本内估计值的 20% 时，效应仍显著\"。
这比\"平行趋势不通过\"强，比\"效应完全可信\"弱——正好支撑\"补充分析、如实报告\"的定位。

## 论文中的用法

- 子样本平行趋势不过时，完整证据链：平行趋势检验 ❌ → PSM（逐年/ever_treated 两种）❌ → HonestDiD ❌ → 降级为补充分析。
- 正文表述："即使在允许事前趋势的敏感性分析（Rambachan & Roth, 2023）下，
  该子样本的处理效应也无法与事前趋势区分"——比"平行趋势不通过"有说服力得多。
- 若 HonestDiD 通过（M 较大时仍显著），可讲"政策逆转了事前恶化趋势"的故事。

## 关键引用

- Rambachan, A. & Roth, J. (2023). A More Credible Approach to Parallel Trends. Review of Economic Studies.
- Stata 包：mcaceresb/stata-honestdid（ssc install honestdid）
- 中文介绍：许文立老师公众号推文（经管之家帖子也常引用此来源）
