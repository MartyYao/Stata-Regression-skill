# AGENTS.md — Codex Operating Guide

This repository provides Stata coding standards for empirical economics papers. 

## Entry Point

Before writing or modifying any Stata do-file, read `SKILL.md` for the routing table, then load the corresponding reference file from `references/`.

## Repository Map

```
SKILL.md                                  → Routing table + execution protocol
references/do-file-standards.md           → Do-file template + coding conventions
references/table-standards.md             → esttab output + table formatting (+ TeX section)
references/graph-standards.md             → Graph style (colors, line types, export)
references/graph-templates.md             → Graph code templates (event study, coefplot, etc.)
references/econometric-checklist.md       → 10 quality checks per regression
references/econometric-best-practices.md  → Full econometric conventions (weights, bootstrap, HonestDiD)
references/stata-pitfalls.md              → 41 Stata mistakes (25 base + 14 project + 2 top10 align)
references/honestdid-stata-notes.md       → HonestDiD sensitivity analysis walkthrough
references/psm-did-matching-specs.md      → PSM-DID matching specs (ever_treated rule, yearly PSM)
references/psm-parallel-trends-diagnosis.md → PSM + parallel trend failure diagnosis
references/pure-control-event-study.md    → Pure control group event study setup
references/inverted-v-pretrend-diagnosis.md → Inverted-V pretrend diagnosis framework
references/cross-group-dynamics-decomposition.md → Threshold-free decomposition (convergence/cross-group/flip)
references/suppression-effect-diagnosis.md → Sub-sample suppression effect diagnosis
templates/master-do-template.do           → Master do-file template
scripts/esttab2html.py                    → CSV → HTML converter
scripts/merge_rtf.py                       → RTF merger for appendix
```

## Non-Negotiable Rules

- No numerical claim without a source in `logs/*.log` or `output/tables/*`.
- Do not fabricate coefficients, standard errors, p-values, or sample sizes.
- Use relative paths in Stata code. No hardcoded machine-specific paths.
- Every `.do` file must have `version`, `set more off`, `set varabbrev off`, logging, and a header.
- `esttab` CSV output must use the `plain` option (no `=""` wrapping).
- Always export graphs as both PDF and PNG (1800px width).
- Cluster standard errors at the most aggregate plausible level.
