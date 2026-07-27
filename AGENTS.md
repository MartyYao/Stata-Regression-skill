# AGENTS.md — Codex Operating Guide

This repository provides Stata coding standards for empirical economics papers. 

## Entry Point

Before writing or modifying any Stata do-file, read `SKILL.md` for the routing table, then load the corresponding reference file from `references/`.

## Repository Map

```
SKILL.md                           → Routing table + execution protocol
references/do-file-standards.md    → Do-file template + coding conventions
references/table-standards.md      → esttab output + table formatting
references/graph-standards.md      → Graph style (colors, line types, export)
references/graph-templates.md      → Graph code templates (event study, coefplot, etc.)
references/econometric-checklist.md → 10 quality checks per regression
references/stata-pitfalls.md       → 24 common Stata mistakes
scripts/esttab2pipe.py             → CSV → markdown pipe table converter
```

## Non-Negotiable Rules

- No numerical claim without a source in `logs/*.log` or `output/tables/*`.
- Do not fabricate coefficients, standard errors, p-values, or sample sizes.
- Use relative paths in Stata code. No hardcoded machine-specific paths.
- Every `.do` file must have `version`, `set more off`, `set varabbrev off`, logging, and a header.
- `esttab` CSV output must use the `plain` option (no `=""` wrapping).
- Always export graphs as both PDF and PNG (1800px width).
- Cluster standard errors at the most aggregate plausible level.
