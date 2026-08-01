# PSM-DID 诊断平行趋势失败的流程

## 问题背景

当按残差符号（ε>0 或 ε<0）拆分子样本时，子样本的平行趋势可能全样本通过但子样本不通过。
原因不一定是 DID 识别失效——更可能是**选择入组偏误（selection-into-sample）**：处理组和对照组中落入该子样本的个体在协变量上存在系统性差异。

## 诊断流程

### Step 1：区分结构性违反 vs 协变量不平衡

```stata
* 比较处理组和对照组在子样本中的协变量均值
ttest Size if over_v1 > 0, by(post)
ttest ROA if over_v1 > 0, by(post)
```

如果多变量存在显著差异 → 协变量不平衡是 pre-trend 的可能原因。

### Step 2：PSM 匹配 + 事件研究

```stata
* 预处理均值匹配
* 1:1 最近邻（caliper=0.05），逐步尝试 NN4 和 Kernel
psmatch2 ever_treated $firm_C, outcome(dev_v1) logit neighbor(1) caliper(0.05) common

* 匹配后事件研究
reghdfe dev_v1 ib4.rel_clean_pos $firm_C $prov_C [pw=w_psm], absorb(Stkcd year) vce(cluster prov_id)
```

### Step 3：比较多规格

| 规格 | 目的 |
|------|------|
| 全样本（无匹配） | 基线 |
| 1:1 最近邻 | 最严格匹配 |
| NN4（1:4） | 更高功效 |
| Kernel 密度 | 利用全部分布信息 |

## 经济学解释

如果匹配前 pre-trend 显著、匹配后不显著：
- 结论不是"PSM 弥补了平行趋势违反"
- 而是**前趋势的显著性是协变量不平衡导致的伪相关**，不是 DGP 的结构性违反
- 匹配恢复了处理组和对照组的可比性，条件平行趋势成立

## 注意

- PSM 匹配会损失样本量（全样本→匹配后，通常 -30%~40%）
- 如用户接受样本损失（"样本量很足"），此方案可行
- 匹配后主回归系数应和全样本方向一致（可能稍小），如果符号翻转说明匹配规格有问题
- 对 over 子样本（一次性冲击型效应），PSM 后 t=0 显著性可能从 ** 降为 *，这是功效损失的正常代价
