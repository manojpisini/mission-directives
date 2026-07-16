# Troubleshooting Guide

## Route selects too many prompts

Check whether the outcome names one primary artifact. Remove broad department language, state exclusions, and clarify authority. A department pack is a discovery surface, not an execution request.

## Route confidence is low

Inspect `questions_that_change_route`. Answer only questions that alter capability selection, authority, evidence lane, medium, or assurance.

## Prompt-body audit fails

### Boilerplate completion criteria

Rewrite the block using the artifact, domain gates, verification IDs, residual behavior, and stop conditions. See `COMPLETION_CRITERIA_GUIDE.md`.

### Missing tool policy

Add role-specific allowed and prohibited tool classes, operating-mode limits, output quarantine, and verification behavior.

### Runtime marker missing

The `<runtime_markers>` block must name all six exact markers.

### Legacy authorization tag

Rename `<security_execution_boundary>` to `<authorization_boundary>` and retain the security-specific content.

### Executive decision rules missing

Add action eligibility, a domain-specific priority rule, conflict resolution, budget behavior, and hard stops.

### Pair verification duplicated

Delete the executive verification list and add `<verification_reference>` to the frozen investigator criteria.

### Self-dependency

Remove the prompt's own ID from `requires` or `contract_refs`, then rebuild the capability graph.

## Manifest mismatch

Run all tests and generated checks first. Then rebuild:

```bash
python tools/build_manifest.py
```

## Audit report mismatch

Regenerate only after reviewing why metrics changed:

```bash
python tools/audit_prompt_bodies.py
```

## Executive refuses handoff

Check:

- snapshot freshness;
- acceptance-criteria hash;
- approval receipt;
- target environment;
- unresolved `?UNKNOWN` records;
- action IDs;
- rollback readiness.

Refusal may be correct.

## No model selected

`model_profiles.json` may contain no measured production-eligible model for the assurance level. Run benchmarks and ingest real results; do not mark an unmeasured profile eligible manually.

## Skill cannot auto-install

The lock is unresolved, trust tier is insufficient, or permissions exceed policy. Resolve the exact revision and checksum in a networked review environment, or use native execution.

## Verification passes but artifact looks wrong

Check whether the verifier reviewed the source rather than the exact export. Add medium-specific checks for PDF, slides, responsive layout, fonts, clipping, chart data, or accessibility.

## Run is stuck in `residual_open`

A residual requires an owner, disposition, and acceptance decision. The run cannot close merely because the main artifact exists.

## Tests pass but validator fails

The unit tests cover runtime functions; the validator also checks catalogs, fixtures, manuals, schemas, graphs, paths, locks, and manifest integrity. Read `VALIDATION.json` for the exact error.

## Validator passes but behavior is poor

Static validation is not live model proof. Add or run behavioral fixtures and model benchmarks.
