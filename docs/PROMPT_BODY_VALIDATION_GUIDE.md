# Prompt Body Validation Guide

## Purpose

The suite validates prompt bodies separately from frontmatter, catalogs, scenarios, schemas, skills, and runtime state. This prevents a structurally complete catalog from hiding weak or unused body contracts.

## Static body audit

Run:

```bash
python tools/audit_prompt_bodies.py
python tools/audit_prompt_bodies.py --check
```

The tool produces:

- `BODY_QUALITY_AUDIT.json`
- `BODY_QUALITY_AUDIT.md`

The JSON file is intended for CI and dashboards. The Markdown file is a human summary.

## Current invariant classes

### Completion criteria

Checks:

- present in every prompt;
- at least three bullets;
- known boilerplate absent;
- task-specific title or artifact terms present;
- `=VERIFY:{id}` required;
- normalized full blocks are not duplicated across unrelated prompts.

### Tool policy

Checks canonical `<tool_policy>` presence in all prompts.

The audit does not prove runtime enforcement; policy files and execution controls remain separate proof surfaces.

### Runtime markers

Checks that each prompt explicitly names:

- `@EVIDENCE:{id}`
- `?UNKNOWN:{id}`
- `#FINDING:{id}`
- `+ACTION:{id}`
- `=VERIFY:{id}`
- `!STOP:{reason}`

### Authorization naming

Checks canonical `<authorization_boundary>` presence and rejects `<security_execution_boundary>`.

### Executive behavior

Checks all executive prompts contain:

- `<decision_rules>`;
- `<verification_reference>`;
- no duplicated `<verification>` block.

### Pair de-duplication

Compares investigator `<verification_design>` to executive verification content and rejects byte-equivalent duplication.

### Dependency integrity

Checks that no prompt requires or contract-references itself and that `capability_graph.json` has no self-edge.

### Complexity budgets

Counts body words and compares them to the declared frontmatter budget.

## Regression tests

`tests/test_prompt_body_quality.py` provides focused tests for every invariant. Tests were written to fail against the deficient body set before the transformations were applied.

Run:

```bash
pytest -q tests/test_prompt_body_quality.py
```

## Full validation sequence

```bash
python tools/build_capability_graph.py --check
python tools/audit_prompt_bodies.py --check
python tools/check_skill_lock.py
python tools/run_evaluations.py
python tools/run_tests.py
python tools/build_manifest.py --check
python tools/validate_suite.py
```

## Reading the audit report

A `pass` means the static prompt-body invariants are satisfied. It does not mean:

- every model follows the prompt;
- every skill is safe;
- a live external action was verified;
- a human approved the content;
- quality is universally optimal.

Those claims require behavioral fixtures, model benchmarks, skill conformance, external verification, or human review.

## Adding a new invariant

1. Write a failing test.
2. Confirm it fails for the intended reason.
3. Add the smallest validator or transformation change.
4. Confirm the focused test passes.
5. Run all tests.
6. Regenerate the audit report.
7. Update manuals and CI.
8. Rebuild the manifest.

## Mutation examples

The validator should detect mutations such as:

- replacing completion criteria with a generic sentence;
- deleting `<tool_policy>`;
- removing one runtime marker;
- changing `<authorization_boundary>` to an undocumented synonym;
- deleting executive decision rules;
- copying investigator verification into the executive;
- adding a prompt self-dependency;
- exceeding the declared body budget.

## Troubleshooting

### Audit report differs in CI

Regenerate locally and inspect the prompt changes. Do not simply overwrite the report without understanding the changed metric.

### Completion block fails task-specific check

Name the artifact or domain outcome directly. Do not add random title words merely to satisfy the test.

### Executive fails verification-reference check

Remove the repeated list and reference the frozen acceptance-criteria artifact produced by the paired investigator.

### Tool policy is present but too broad

Static presence is only the first check. Review allowed tool classes, modes, network, writes, external effects, and output quarantine manually.
