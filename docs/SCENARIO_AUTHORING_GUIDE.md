# Scenario Authoring Guide

## Purpose

A scenario is a reusable cross-capability execution route. It is justified when the same combination of evidence, planning, production, review, authorization, and verification recurs often enough that operators benefit from a named route.

A scenario is not a department bundle and not a list of every prompt that might be relevant. It is a conditional graph whose nodes are selected only when their inputs, change surfaces, and authority requirements apply.

## Required scenario contract

Every scenario declares:

```yaml
scenario_id:
title:
purpose:
primary_owner:
prompts:
required_inputs:
consumed_artifacts:
produced_artifacts:
protected_surfaces:
possible_external_effects:
minimum_assurance:
phases:
parallel_groups:
execution_locks:
branches:
completion_gate:
```

## Outcome definition

The scenario purpose should describe one observable cross-capability result.

Good:

> Implement an approved feature across product requirements, code, tests, security checks, documentation, and release evidence.

Weak:

> Run the engineering department prompts.

## Primary owner

Choose the prompt that owns the final result. Other prompts provide prerequisites, evidence, review, or gates.

Without a primary owner, the scenario tends to produce several reports without one accountable outcome.

## Phase-specific modes

Do not assign one global mode to a scenario that contains different behaviors.

Example:

```yaml
phases:
  - phase_id: discovery
    mode: AUDIT_ONLY
  - phase_id: planning
    mode: PLAN_ONLY
  - phase_id: implementation
    mode: APPLY_SAFE
  - phase_id: deployment
    mode: APPLY_APPROVED
  - phase_id: verification
    mode: VERIFY_ONLY
```

The runtime may skip phases whose artifacts already exist and remain current, but it may not weaken their mode requirements.

## Inputs and artifacts

`required_inputs` identifies information that changes routing or makes the scenario unsafe when absent.

`consumed_artifacts` and `produced_artifacts` should use stable artifact types or exact paths where appropriate. If two prompts produce the same source-of-truth artifact, add a single-writer lock or redesign the graph.

## Protected surfaces and external effects

State explicitly:

- files or systems that cannot change;
- data that cannot be exposed;
- production environments;
- external publication, sending, deployment, installation, financial, legal, or employment effects;
- approvals required for each effect.

## Parallel groups

Parallelize only independent read-only work or isolated variants.

Safe examples:

- source retrieval and user research;
- code inventory and documentation audit;
- independent visual and factual review;
- isolated creative directions.

Unsafe examples:

- two workers editing the same manuscript;
- concurrent schema migration and application deployment;
- two agents changing one design-token source;
- overlapping cleanup branches without a merge plan.

## Execution locks

Use locks for:

- one source-of-truth artifact;
- production systems;
- publication channels;
- data migrations;
- credentials and secrets;
- employment, financial, or legal decisions;
- irreversible exports or submissions.

## Conditional branches

Scenarios should model real uncertainty.

Common branches:

```text
evidence sufficient?
├─ no → collect more evidence or stop
└─ yes → continue

skill locked and conformant?
├─ no → native fallback
└─ yes → quarantined skill execution

production action approved?
├─ no → plan or draft only
└─ yes → dry run → execute → verify

verification passed?
├─ no → failed or rolled_back → residual_open
└─ yes → verified
```

## Completion gate

The scenario gate should aggregate completion from all required phases without hiding partial success.

It should require:

- primary artifact or changed state;
- phase-specific `=VERIFY:{id}` records;
- no unresolved hard stop;
- known rollback state;
- residual ownership;
- authorized external action status.

## Fixture requirements

Every scenario requires:

- healthy fixture;
- problematic fixture;
- adversarial fixture;
- negative-routing expectations where over-selection is plausible;
- rollback or residual fixture when the scenario can mutate state.

## Anti-patterns

Do not create scenarios that:

- load a whole department;
- duplicate another scenario with a new title;
- hide an execution phase behind `PLAN_ONLY`;
- omit protected surfaces;
- assume publication or deployment;
- lack a primary owner;
- allow several writers to modify one artifact;
- have no failure or verification branch;
- merely concatenate prompts without handoff semantics.

## Authoring checklist

1. Define one observable outcome.
2. Select the primary owner.
3. Add only prompts that change the result.
4. Define required inputs and evidence freshness.
5. Assign phase-specific modes.
6. Define consumed and produced artifacts.
7. Protect sensitive and live surfaces.
8. Identify parallel-safe work and locks.
9. Add evidence, approval, fallback, rollback, and verification branches.
10. Define an independent completion gate.
11. Add all fixture tiers.
12. Update execution order, catalog, coverage, graph, manuals, and manifest.

## Validation

```bash
python tools/run_evaluations.py
python tools/validate_suite.py
```
