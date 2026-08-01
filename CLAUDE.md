# CLAUDE.md — Stata Research Pipeline for Economists

## Entry Point

Always read `SKILL.md` first for any Stata coding task. It contains the routing table that tells you which reference file to read for which task type.

## Core Principles

- **Plan first** — read the relevant reference before writing code
- **Verify after** — run the do-file, inspect the log, confirm output exists
- **Log-verified results** — every numerical claim traces to a `logs/*.log` line or `output/tables/*.csv` cell
- **No log, no claim**
- **Reproducibility** — version pinned, set seed once, do-files runnable from a fresh clone

## Reference Quick Index

| Task | Start with |
|------|-----------|
| Writing a regression do-file | `references/do-file-standards.md` |
| Producing a regression table | `references/table-standards.md` |
| HonestDiD sensitivity analysis | `references/honestdid-stata-notes.md` |
| PSM-DID matching | `references/psm-did-matching-specs.md` |
| Inverted-V pretrend pattern | `references/inverted-v-pretrend-diagnosis.md` |
| Pure control group event study | `references/pure-control-event-study.md` |
| Cross-group dynamics (residual method) | `references/cross-group-dynamics-decomposition.md` |
| Creating a publication-ready graph | `references/graph-standards.md` |
| Event study / parallel trends plot | `references/graph-templates.md` |
| Checking regression quality | `references/econometric-checklist.md` |
| Debugging common Stata errors | `references/stata-pitfalls.md` |
