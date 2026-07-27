# Stata Regression — 实证论文 Stata 工作流

面向经管专业的 Stata 可复现编码规范、出图标准、表格格式与计量质量检查清单。适用于任何 AI 编程助手（Claude Code、Codex、Kimi Code、Cursor 等）。

---

## 快速使用

### Claude Code

项目根目录下添加 `CLAUDE.md`，内容：

```markdown
## Stata 编码规范
写 Stata do-file 前，先读取 skills/stata-regression/ 下的 SKILL.md，按路由表加载对应 reference 文件。
```

### Codex

项目根目录下添加 `AGENTS.md`，内容同上。

### 任意 Agent

直接将 `SKILL.md` 及对应 reference 文件的路径告知 Agent。Agent 会按路由表逐步加载。

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
│   ├── graph-templates.md             ← 8 类出图模板（事件研究/coefplot/异质性等）
│   ├── econometric-checklist.md       ← 10 条计量质量检查
│   └── stata-pitfalls.md              ← 24 条高频陷阱速查
└── scripts/
    └── esttab2pipe.py                 ← esttab CSV → markdown pipe table 转换
```

---

## 输出管线

```
Stata do 文件
  ├─ esttab → .csv (plain)  → esttab2pipe.py → markdown pipe table
  └─ graph export → .pdf + .png
```

---

## 关键技术规范速览

| 规范 | 标准 |
|------|------|
| 系数小数位 | 4 位 |
| 括号内 | t 值（非标准误） |
| 控制变量 | 逐行列全部系数，不可用 ✓ |
| 显著性标记 | * p<0.10, ** p<0.05, *** p<0.01 |
| 焦点系列颜色 | RGB 49 145 255 (#3191FF) |
| 对比系列颜色 | RGB 142 164 184 (#8EA4B8) |
| 图形导出 | PDF + PNG (1800px width) |
| 聚类 SE | 最高聚合层级 |

---

## 许可证

MIT
