# Operator Guide

## Purpose

This guide is for the person running the suite, approving actions, inspecting manifests, and deciding whether a run may progress.

## Operator responsibilities

The operator is accountable for:

- declaring scope and authority;
- supplying or identifying authoritative evidence;
- resolving route-changing ambiguity;
- reviewing high-risk handoffs;
- approving exact actions rather than broad intent;
- monitoring state transitions;
- interpreting verification and residuals;
- refusing false completion.

## Canonical control load

```text
MD-00 → MD-01 → MD-03 → MD-04 → MD-02 → selected graph
```

Control prompts load once. Capability prompts may narrow but not weaken them.

## Route inspection

Start with keyword lookup when the target is not already known:

```bash
python tools/md.py lookup "<user terms>" --limit 8
```

The lookup result is a candidate list. Confirm the selected target with `explain`; do not execute directly from a weak lexical match.

```bash
python tools/md.py explain C-63
```

Review:

- selected prompt IDs;
- route confidence;
- injected security, privacy, accessibility, or release obligations;
- rejected prompts;
- unresolved questions;
- skill trust and lock status;
- model eligibility;
- required assurance and approvals.

A low-confidence route is not automatically wrong, but any unresolved question that changes authority or the execution graph must be answered before action.

## Planning

```bash
python tools/md.py plan C-63 \
  --mode DRAFT_ONLY \
  --root . \
  --out .prompt_suite/runs/feature.json
```

Use `--dry-run` to simulate state transitions without writing the manifest.

## Run states

```text
configured
→ investigating
→ evidence_ready
→ fan_in_pending
→ handoff_frozen
→ approval_pending
→ dry_run_ready
→ executing
→ verification_pending
→ verified | failed | rolled_back | residual_open
→ closed
```

The runtime rejects illegal transitions.

## Handoff review

Before approving an executive run, verify:

- evidence snapshot and freshness;
- findings and confidence;
- proposed action IDs;
- action dependencies;
- protected surfaces;
- rollback needs;
- acceptance criteria;
- unresolved blockers;
- target environment;
- budget and maintenance window.

Do not approve “fix everything.” Approve exact `+ACTION:{id}` records.

## Tool and skill review

For each external skill or tool:

- confirm repository and exact revision;
- inspect permissions;
- verify lock status;
- review network and file access;
- confirm output quarantine;
- identify native fallback;
- require conformance evidence for high assurance.

## Executive monitoring

During execution, watch for:

- a new `#FINDING:{id}`;
- target drift;
- action conflicts;
- budget exhaustion;
- partial state;
- failed verification;
- rollback uncertainty;
- undeclared tool permissions.

New findings do not inherit approval from the old plan.

## Verification review

Every criterion should have:

```text
=VERIFY:{id}
criterion
method
result
supporting evidence
revision or timestamp
```

A command exit code is not sufficient if the criterion concerns behavior, data, accessibility, security, or exact export quality.

## Closing a run

Close only when:

- verification passed or residual risk was explicitly accepted by an authorized human;
- rollback state is known;
- actions and residuals have owners;
- lineage and artifacts are recorded;
- no `!STOP` remains unresolved;
- completion criteria are satisfied.

## Operational commands

```bash
python tools/md.py lookup "<user terms>" --limit 8
python tools/md.py list --kind packs
python tools/md.py explain C-63
python tools/md.py plan C-63 --mode DRAFT_ONLY --root . --out run.json
python tools/md.py transition run.json investigating
python tools/md.py validate-run run.json
python tools/md.py select-model MD-29 --assurance HIGH_ASSURANCE
python tools/sync_agent_guidance.py --project-root /path/to/project --suite-root . --dry-run --show-diff
```

## Operator anti-patterns

- selecting every prompt in a department pack;
- approving a broad outcome instead of exact actions;
- treating a tool name as evidence of trust;
- allowing an executive to act on a stale handoff;
- accepting a polished artifact without exact export verification;
- closing with hidden residuals;
- rewriting acceptance criteria during execution;
- ignoring marker IDs and relying on prose alone.

## Operating the paired review gate

Use `freeze-pair-handoff`, `review-pair-plan`, and `consent-pair-execution` rather than manually moving a paired run from `handoff_frozen` to execution. The runtime resolves the executor from reciprocal `paired_prompt_id` metadata and fails closed when another executor is supplied. Revisions invalidate prior consent and require a new handoff hash and review receipt.
