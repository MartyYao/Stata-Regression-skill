# Graph Standards — Stata 图形质量标准

## 1. 颜色方案

### 标准色板（实证论文用）

| 元素 | RGB / 十六进制 | 用途 |
|------|---------------|------|
| **焦点系列** | `"49 145 255"` / `#3191FF` | 处理组、处理效应系数 |
| **对比系列** | `"142 164 184"` / `#8EA4B8` | 控制组、稳健性对比 |
| **标题文本** | `"31 55 73"` / `#1F3749` | 图标题、轴标题 |
| **副文本** | `"74 89 105"` / `#4A5969` | 轴标签、刻度 |
| **参考线** | `"128 128 128"` / `#808080` | 零线、基期线 |
| **置信区间** | `"182 211 245"` / `#B6D3F5` | 填充带 |

### 线型规格

| 用途 | 线型 | 粗细 |
|------|------|------|
| 焦点系列（处理组） | `solid` | `medium-thick` (lwidth(medium)) |
| 对比系列（控制组） | `dash` | `medium-thin` (lwidth(thin)) |
| 参考线（零线） | `dash` | `thin` (lwidth(vthin)) |
| 置信区间 | 填充 `arear` 或 `rcap` | — |

### 标记规格

| 用途 | 符号 | 大小 |
|------|------|------|
| 焦点点估计 | `O` (circle hollow) | `msize(medium)` |
| 对比点估计 | `S` (square hollow) | `msize(small)` |

## 2. 图形区域设置

所有图按此规格：

```stata
* 白色背景 + 无边框
twoway ..., ///
    graphregion(fcolor(white) lcolor(white) lwidth(none)) ///
    plotregion(fcolor(white) lcolor(white) lwidth(none)) ///
    ylabel(, labcolor("74 89 105") labsize(small)) ///
    xlabel(, labcolor("74 89 105") labsize(small)) ///
    title("图标题", color("31 55 73") size(medium)) ///
    ytitle("Y 轴标题", color("31 55 73") size(small)) ///
    xtitle("X 轴标题", color("31 55 73") size(small))
```

- 白色 `graphregion()` 和 `plotregion()`，无可见边框
- 设置水平网格线：`ylabel(, grid)` 或 `yline(, lcolor(gs14) lwidth(vthin) lpattern(dash))`
- 不显示垂直网格线

## 3. Scheme 设置

推荐安装 `blindschemes` 包：

```stata
ssc install blindschemes, replace
set scheme plotplain
```

如果未安装，回退到 Stata 内置 `s1color`：

```stata
set scheme s1color
```

**原则**：scheme 管理配色基调（标题色、轴标签色、图元默认色），模板中的手动配色仅用于**区分焦点/对比组**，不覆盖 scheme 的全局样式。如果只用单色图（没有比较组），不需要手动指定颜色。

## 4. 导出格式

**每条 Stata 图都输出两种格式**：

```stata
* PDF（Vector，适合 LaTeX 投稿）
graph export "output/figures/event_study.pdf", replace

* PNG（适合 Word 投稿和 Obsidian 快速预览）
graph export "output/figures/event_study.png", replace width(1800)
```

| 格式 | 分辨率/尺寸 | 用途 |
|------|-------------|------|
| `.pdf` | Vector | LaTeX 投稿 |
| `.png` | 1800px width | Word 投稿 / Obsidian / 幻灯片 |

## 5. 各类型图的具体规格

### 事件研究图（平行趋势）

```stata
* 系数 + rcap CI
twoway (rcap ci_lower ci_upper rel_pos, lcolor("49 145 255") lwidth(medium)) ///
       (scatter coef rel_pos, mcolor("49 145 255") msymbol(O) msize(medium)), ///
    xline(4.5, lcolor("128 128 128") lpattern(dash) lwidth(vthin)) ///
    yline(0, lcolor("128 128 128") lpattern(dash) lwidth(vthin)) ///
    xlabel(1"-4" 2"-3" 3"-2" 4"-1" 5"0" 6"1" 7"2" 8"3", labsize(vsmall)) ///
    xtitle("距政策推行年数", size(small)) ///
    ytitle("系数估计值", size(small)) ///
    legend(off) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

**事件研究三原则**：
1. 基期选处理前一期（`rel_time=-1`），不是边界
2. 负值偏移：`gen rel_pos = rel_time + 5`，`ib4.rel_pos` 做基期
3. 参考线在基期位置（`xline(4.5)` 对应 -1 和 0 之间）

### 系数图（coefplot）

```stata
* 单模型系数图
coefplot, ///
    keep(post) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))

* 多模型对比（M1→M6）
coefplot m1 || m2 || m3 || m4 || m5 || m6, ///
    keep(post) ///
    vertical ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

### 异质性分析图（多 Panel）

```stata
* 各子组系数水平排列
coefplot (m_soe, label("国有企业")) ///
         (m_non_soe, label("非国有企业")) ///
         (m_east, label("东部")) ///
         (m_west, label("中西部")), ///
    keep(post) ///
    xline(0, lcolor("128 128 128") lpattern(dash)) ///
    mcolor("49 145 255") ///
    ciopts(lcolor("49 145 255")) ///
    graphregion(fcolor(white) lcolor(white))
```

### 边缘效应图（marginsplot）

```stata
margins, at(treat_score1 = (0(1)5)) post
marginsplot, ///
    xlabel(0 "0" 1 "1" 2 "2" 3 "3" 4 "4" 5 "5") ///
    ytitle("预测值") ///
    xtitle("处理强度得分") ///
    ciopts(lcolor("182 211 245") lwidth(none)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

### 趋势图

```stata
* 先 collapse 再画
collapse (mean) over_v1, by(year treat_group)

twoway (line over_v1 year if treat_group == 1, ///
        lcolor("49 145 255") lwidth(medium)) ///
       (line over_v1 year if treat_group == 0, ///
        lcolor("142 164 184") lwidth(thin) lpattern(dash)), ///
    xline(2018, lcolor("128 128 128") lpattern(dash)) ///
    ytitle("DV 均值") ///
    xtitle("年份") ///
    legend(order(1 "处理组" 2 "控制组") pos(6)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

### 分布图

```stata
* 直方图
histogram over_v1, ///
    color("182 211 245") ///   填充
    lcolor("49 145 255") ///   边框
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))

* 核密度图
kdensity over_v1, ///
    lcolor("49 145 255") lwidth(medium) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
```

### DID 动态效应（csdid_plot）

```stata
csdid `outcome' `controls', ivar(Stkcd) time(year) gvar(first_treat)
csdid_plot, ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(white))
graph export "output/figures/csdid_event_study.pdf", replace
graph export "output/figures/csdid_event_study.png", replace width(1800)
```

## 6. 检查清单

出图后逐项确认：
- [ ] 两张格式齐全：PDF + PNG
- [ ] 焦点系列为 "49 145 255" 蓝色
- [ ] 白色背景，无边框
- [ ] 水平网格线，无垂直网格线
- [ ] 图例位置合理（不影响数据区域）
- [ ] 轴标签文字可读（不过小、不旋转到竖排）
- [ ] 如果有多条线/多个组，区分度足够
- [ ] 参考线有标注或可见
