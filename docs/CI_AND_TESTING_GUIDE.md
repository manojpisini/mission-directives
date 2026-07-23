# CI and Testing Guide

## Purpose

This guide describes the deterministic checks that keep the suite coherent after prompt, schema, scenario, policy, skill, model, documentation, or runtime changes.

## Local prerequisites

```bash
python -m pip install -r requirements-dev.txt
```

The test environment requires Python, PyYAML, jsonschema, and pytest.

## Fast focused checks

### Prompt-body work

```bash
pytest -q tests/test_prompt_body_quality.py
python tools/audit_prompt_bodies.py --check
```

### Runtime work

```bash
pytest -q tests/test_md.py
```

### Graph or dependency work

```bash
python tools/build_capability_graph.py --check
```

### Skill registry or lock work

```bash
python tools/check_skill_lock.py
```

## Complete local chain

```bash
python tools/build_capability_graph.py --check
python tools/audit_prompt_bodies.py
python tools/check_skill_lock.py
python tools/run_evaluations.py
python tools/run_tests.py
python tools/validate_templates.py
python tools/check_documentation_links.py
python tools/check_script_parity.py
python tools/check_release_consistency.py
python tools/check_generated_reproducibility.py
python tools/build_manifest.py --check
python tools/validate_suite.py
```

If canonical files intentionally changed, regenerate the graph, audit, test status, and manifest before running `--check`.

## Test-driven defect repair

For a bug or missing invariant:

1. write a focused failing test;
2. run it and confirm the failure is caused by the defect;
3. implement the smallest correction;
4. run the focused test;
5. run the full test suite;
6. regenerate derived artifacts;
7. run full validation;
8. inspect the semantic diff.

The prompt-body defect repairs use this pattern. The tests fail against generic completion text, missing tool policies and markers, missing executive decision rules, duplicated verification, and self-dependencies.

## GitHub Actions

`.github/workflows/validate.yml` runs on every push and pull request across Ubuntu, Windows, and macOS with Python 3.12.

The workflow must run checks in this order:

1. install development dependencies;
2. generate prompt-body audit artifacts;
3. run deterministic tests and public-command smoke coverage;
4. run evaluation, route-confusion, and exact-twin fixtures;
5. validate templates and Bash/PowerShell script parity;
6. check release metadata and generated reproducibility;
7. run complete validation;
8. smoke-test the platform-native wrapper;
9. upload audit, test, evaluation, and validation artifacts even when an earlier step fails.

Generated artifacts are reviewed as CI uploads. Canonical reproducibility and the manifest still fail when committed package content diverges.

## Uploaded evidence

Each matrix job uploads a `validation-<os>` artifact containing:

- `BODY_QUALITY_AUDIT.json` and `.md`;
- `.prompt_suite/results/TEST_RESULTS.json`;
- `.prompt_suite/results/EVALUATION_STATUS.json`;
- `VALIDATION.json` when full validation reached its reporting stage.

Artifact upload uses `if: always()` so an early failure still preserves whatever evidence was produced. Missing files warn rather than masking the original failure.

## Pre-commit

The local hooks run body audit, graph check, evaluations, tests, and suite validation. Install with:

```bash
pre-commit install
```

## Manifest handling

`MANIFEST.json` records every package file except the manifest and current validation result. After an intentional change:

```bash
python tools/build_manifest.py
python tools/build_manifest.py --check
```

Never hand-edit hashes.

## Common failures

### Manifest mismatch

A file changed after the manifest was generated. Re-run the relevant tests first, then rebuild the manifest.

### Audit report mismatch

Prompt bodies changed without regenerating `BODY_QUALITY_AUDIT.json` and `.md`. Review the metric change before regenerating.

### Graph mismatch

Prompt `requires` or pairing changed. Rebuild `capability_graph.json` and inspect added or removed edges.

### Catalog mismatch

Frontmatter and `catalog.json` disagree. Rebuild the catalog from canonical frontmatter or fix the source inconsistency.

### Body word budget exceeded

Remove duplicated prose or intentionally update the budget with a small margin after review. Do not inflate every budget to hide growth.

## Proof boundary

CI proves deterministic package integrity. It does not execute third-party skills, benchmark external models, deploy systems, or provide human approval unless those jobs are explicitly configured with secure credentials and environments.

## Documentation integrity check

Run:

```bash
python tools/check_documentation_links.py
```

The checker scans root and `docs/` Markdown files, ignores external URLs and in-document anchors, rejects missing relative targets, and rejects links that escape the repository root. The same check runs in pytest, pre-commit, the complete validator, and CI.
