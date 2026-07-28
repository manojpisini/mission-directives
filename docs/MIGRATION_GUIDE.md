# Migration Guide

## Scope

Migration moves only content proven to belong to an older managed Mission Directives installation. Generic project folders are not treated as owned merely because their names match prompt or output categories.

## Preview and apply

```bash
mission-directives migrate /path/to/project --dry-run
mission-directives migrate /path/to/project --apply
```

The preview lists every recognized managed path and destination. Application stages the 2.0 runtime, verifies checksums, updates managed guidance and ignore rules, moves eligible content, and removes old managed paths only after successful promotion.

Recognized legacy evidence includes Mission Directives receipts and managed markers. Unmarked `prompts/`, `.prompt_suite/`, `results/`, `reports/`, `artifacts/`, `plans/`, `outputs/`, `docs/`, and `logs/` content is preserved.

## After migration

```bash
mission-directives config validate
mission-directives route "MD explain this project"
mission-directives view
```

Review `.mission-directives/project.json`, the selected tracking mode, managed `AGENTS.md` and `CLAUDE.md` blocks, and output category contents. Use `mission-directives uninstall ... --dry-run` to verify the new ownership boundary.
