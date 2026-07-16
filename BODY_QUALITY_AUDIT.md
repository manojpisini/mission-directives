# Prompt Body Quality Audit

This report is generated from the canonical prompt files. It measures static body-contract coverage and does not claim live language-model performance.

**Status:** `pass`

## Summary

| Check | Result |
|---|---:|
| Prompt bodies inspected | 200 |
| Completion criteria present | 200 |
| Unique completion-criteria blocks | 200 |
| Boilerplate completion blocks | 0 |
| Canonical tool policies | 200 |
| Prompt bodies implementing all runtime markers | 200 |
| Canonical authorization boundaries | 200 |
| Legacy security-execution boundary tags | 0 |
| Executive prompts with decision rules | 32 / 32 |
| Executive prompts with verification references | 32 / 32 |
| Pair verification blocks duplicated | 0 |
| Paired planners with review and exact-twin gate | 32 / 32 |
| Paired executors with reviewed-handoff authority | 32 / 32 |
| Self dependencies | 0 |
| Complexity-budget violations | 0 |

## Interpretation

- Completion criteria are counted by normalized full-block text; a unique block does not by itself prove quality, but it prevents a small boilerplate set from satisfying the contract.
- Runtime-marker coverage means each prompt explicitly instructs use of evidence, unknown, finding, action, verification, and stop identifiers.
- Pair de-duplication requires the executive to reference the investigator's frozen acceptance criteria instead of repeating the same verification list.
- Paired planners must present the plan for review, incorporate requested changes, re-freeze the handoff, and ask for consent to invoke only the exact reciprocal executor.
- Tool-policy and authorization checks validate canonical tag presence and naming; live enforcement still belongs to the runtime policy engine.

## Errors

- None.

## Reproduce

```bash
python tools/audit_prompt_bodies.py --check
pytest -q tests/test_prompt_body_quality.py
python tools/validate_suite.py
```
