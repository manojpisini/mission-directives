# Contributing to Mission Directives

## Principle

Change the smallest canonical surface that owns the problem, preserve permanent identities and safety boundaries, and provide fresh evidence before claiming completion.

## Development setup

1. Use a focused branch or isolated worktree.
2. Install `requirements-dev.txt` in a supported Python environment.
3. Read `GOVERNANCE.md`, `SECURITY.md`, the mastery manual, and the specific policy or schema being changed.
4. Identify canonical files and generated consumers before editing.
5. Run the relevant baseline test so pre-existing failures are visible.

## Canonical-source discipline

Do not manually edit generated catalogs, graphs, audit reports, test receipts, validation reports, or manifests. Modify prompt bodies, scenario definitions, templates, schemas, policies, tools, compatibility records, or evaluation definitions, then run their canonical generators.

`VERSION` is the current release source. Do not hard-code the active version in tools or tests when it can be read through `tools/release_meta.py`.

## Behavioral changes

For a behavior change:

1. write a focused failing test or adversarial fixture;
2. reproduce the failure;
3. implement the minimal correction;
4. rerun the focused test;
5. run adjacent contract tests;
6. update documentation and compatibility records in the same change;
7. regenerate deterministic artifacts;
8. run the complete validation chain.

## Prompt changes

Preserve prompt ID, capability ID, observable outcome, authorization boundary, evidence lane, task-specific completion criteria, runtime markers, and template semantics. For a genuine pair, preserve one reciprocal exact twin and the review–revise–re-freeze–consent workflow.

## Template changes

Keep unconditional routes minimal. Put compatible but non-universal templates in `conditional_template_routes`. Every template section must give artifact-specific direction, evidence requirements, accessibility expectations, and verification—not generic placeholder prose.

## Tool changes

- Separate parsing, pure decision logic, rendering, and filesystem mutation where practical.
- Propagate exit codes and structured errors.
- Use the shared TUI, telemetry, release metadata, and path resolver.
- Maintain Bash and PowerShell semantic parity.
- Test paths with spaces and Unicode.
- Never embed local usernames, absolute home paths, credentials, or runtime receipts.

## Installer changes

Prove dry-run behavior, preservation of unmanaged files, idempotent managed blocks, staging, explicit replacement, backup, rollback, managed `.gitignore`, tracked `docs/`, and successful validation from the installed `prompts/` directory.

## Schema changes

Validate the schema itself, a healthy contract fixture, an adversarial fixture, and every current runtime artifact mapped to it. State compatibility implications for added required fields, removed values, or stricter `additionalProperties` rules.

## Required checks

Run at minimum:

```bash
python tools/run_tests.py
python tools/validate_templates.py
python tools/audit_prompt_bodies.py
python tools/check_documentation_links.py
python tools/check_script_parity.py
python tools/run_evaluations.py
python tools/check_generated_reproducibility.py
python tools/validate_suite.py
```

Before release, rebuild and check `MANIFEST.json`, create the ZIP, extract it into a clean directory, and repeat non-mutating verification.

## Pull-request or review description

Explain:

- problem and observable outcome;
- canonical files changed;
- compatibility and authority impact;
- tests added and exact commands run;
- generated files refreshed;
- documentation updated;
- cross-platform evidence;
- security and privacy assessment;
- known residuals and external measurements not performed.

## Prohibited contributions

Do not commit credentials, private data, personal paths, caches, local runtime logs, machine receipts, unresolved generated diffs, fabricated benchmark results, or unrelated refactors hidden inside a focused change.
