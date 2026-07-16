# Architecture Guide

## Purpose

This guide explains the suite as a set of cooperating layers. The architecture is designed to prevent a single oversized prompt from owning context, authority, research, execution, verification, and publication simultaneously.

## Layer 1: Permanent capability identity

Every prompt has a permanent `capability_id`, `prompt_id`, and `prompt_slug`. Sequence is an address, not identity. Compatibility files preserve aliases and redirects.

## Layer 2: Control plane

Five control prompts establish:

- run context;
- safety and authorization;
- routing and execution graph;
- artifact and handoff contracts;
- input trust and prompt structure.

The control plane is loaded once per run.

## Layer 3: Capability roles

- investigative;
- executive;
- operational;
- gate.

Role determines mutation rights, handoff behavior, verification ownership, and tool policy.

## Layer 4: Prompt-body contract

Every body contains canonical action, tool, marker, output, and completion semantics. The body is independently audited from frontmatter.

Key invariants:

- one authorization tag name;
- explicit tool policy;
- full marker vocabulary;
- task-specific completion;
- executive decision rules;
- reference-based pair verification.

## Layer 5: Scenario graph

Scenarios compose capabilities into phases with:

- required inputs;
- produced and consumed artifacts;
- modes;
- parallel groups;
- locks;
- branches;
- completion gates.

Department packs are discovery indexes, not executable graphs.

## Layer 6: Policy engine

Policies enforce external actions and high-stakes domains independently of prompt prose. Policy areas include publication, employment, legal, financial, OSINT, security testing, data handling, skills, and role authority.

## Layer 7: Artifact system

Typed artifacts separate:

- evidence;
- findings;
- actions;
- approvals;
- dry runs;
- execution logs;
- verification;
- residuals;
- lineage;
- domain outputs.

Stable marker IDs connect the artifacts.

## Layer 8: State machine

The state machine makes lifecycle claims enforceable. A run cannot jump from investigation to closure or from approval pending directly to execution.

## Layer 9: Tool and skill adapters

Skills are optional adapters selected by output contract, trust, permission, and measured value. Lockfiles and quarantine prevent moving third-party code from becoming silently trusted.

## Layer 10: Model profiles

Model routing uses measured profile data. Unmeasured models are not production-eligible. The runtime may return no selection.

## Layer 11: Evaluation and proof

Proof surfaces remain separate:

- static structure;
- deterministic runtime tests;
- fixture specifications;
- live model measurements;
- live skill conformance;
- human-reviewed golden runs.

## Dependency graph

`capability_graph.json` is generated from prompt frontmatter. It contains requirement and handoff edges. The builder removes self-dependencies and the validator rejects them.

```bash
python tools/build_capability_graph.py --check
```

## Pair architecture

Investigative side:

```text
evidence → findings → actions → acceptance criteria → frozen handoff
```

Executive side:

```text
approved handoff → dry run → action batches → verification reference → residuals
```

The verification list is not duplicated.

## Failure containment

The architecture contains failure through:

- read-only investigation;
- scoped authority;
- least-privileged tools;
- action IDs;
- approval receipts;
- dry runs;
- execution locks;
- rollback;
- independent verification;
- residual-open state;
- `!STOP` markers.

## Source-of-truth hierarchy

1. policies and signed runtime authority;
2. prompt and scenario machine metadata;
3. schemas and state machine;
4. prompt bodies;
5. generated catalogs and graphs;
6. manuals and examples.

Generated files must be rebuilt from canonical sources rather than hand-edited when a builder exists.

## Paired review and exact-twin control

True investigative/executive pairs include an explicit human review layer between `handoff_frozen` and execution preparation. The planner presents the plan, incorporates requested revisions, re-verifies and re-freezes the handoff, and obtains review again. Explicit execution consent then authorizes only the reciprocal `paired_prompt_id`; the runtime rejects substitute executors.
