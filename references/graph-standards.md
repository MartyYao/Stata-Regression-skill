# Graph Standards — Stata 图形质量标准

> 参考 codex-stata-for-economists 的 muted Stata-style 图形规范。

## 1. Scheme

```stata
set scheme s2color
```

- 使用 Stata 内置 `s2color`，零额外安装
- 所有模板不覆盖 scheme 默认配色（只标注焦点/对比组颜色用于区分两条线）

## 2. 色板

| 元素 | RGB | HEX | 用途 |
|------|-----|-----|------|
| 焦点系列 | `"49 145 255"` | `#3191FF` | 处理组、核心系数、主线条 |
| 对比系列 | `"142 164 184"` | `#8EA4B8` | 控制组、稳健性对比线条 |
| 主标题 | `"31 55 73"` | `#1F3749` | 图标题、轴标题 |
| 副文本 | `"74 89 105"` | `#4A5969` | 轴标签、刻度数字 |
| 参考线 | `"128 128 128"` | `#808080` | 零线、基期线 |
| CI 填充 | `"182 211 245"` | `#B6D3F5` | 置信区间填充带 |
| 网格线 | `gs14` | — | 水平网格线（Stata 灰度 14） |

## 3. 线型 / 标记

| 用途 | 线型 | 粗细 |
|------|------|------|
| 焦点线 | `solid` | `lwidth(medium)` |
| 对比线 | `dash` | `lwidth(thin)` |
| 参考线 | `dash` | `lwidth(vthin)` |
| 焦点点估计 | `O` (circle) | `msize(medium)` |
| 对比点估计 | `S` (square) | `msize(small)` |

## 4. 图形区域

```stata
twoway ..., ///
    graphregion(fcolor(white) lcolor(white) lwidth(none)) ///
    plotregion(fcolor(white) lcolor(white) lwidth(none)) ///
    ylabel(, grid glcolor(gs14) glwidth(vthin) labcolor("74 89 105") labsize(small)) ///
    xlabel(, labcolor("74 89 105") labsize(small)) ///
    title("标题", color("31 55 73") size(medium)) ///
    ytitle("Y 轴", color("31 55 73") size(small)) ///
    xtitle("X 轴", color("31 55 73") size(small))
```

- 白色背景 + 无可见边框
- 水平网格线 `gs14 vthin`，不设垂直网格线
- 字体使用 Stata 默认 Sans（Arial），`labsize(small)`，`size(small)`

## 5. 导出格式

每条图 PDF + PNG 双格式：

```stata
graph export "output/figures/fig_name.pdf", replace
graph export "output/figures/fig_name.png", replace width(1600)
```

| 格式 | 用途 |
|------|------|
| `.pdf` | LaTeX 投稿（矢量） |
| `.png` | Word 投稿 / Obsidian / 幻灯片 |

## 6. 检查清单

- [ ] PDF + PNG 双格式齐全
- [ ] `set scheme s2color` 已设
- [ ] 焦点 "49 145 255" 蓝，对比 "142 164 184" 灰
- [ ] 白色背景，无边框
- [ ] 水平网格线 `gs14 vthin`，无垂直网格线
- [ ] 轴标签 `labsize(small)`，不旋转竖排
- [ ] 标题/轴标题存在且有意义
- [ ] 参考线虚线，标注或可见
- [ ] 多线/多组时区分度足够
- [ ] 图例位置不遮挡数据
