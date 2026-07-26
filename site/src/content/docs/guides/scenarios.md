---
title: Scenarios and Graphs
description: Atomic scenarios, composite workflows, phase ordering, locks, branches, and completion gates.
---

A prompt is one capability contract. A scenario is an execution graph that composes capabilities around one observable outcome.

## Atomic and composite scenarios

Atomic scenarios wrap a single prompt with the standard scenario contract. Composite scenarios sequence multiple capabilities and may contain investigation, planning, production, and verification phases.

Each scenario declares:

- required and consumed inputs;
- produced artifacts;
- default mode and minimum assurance;
- ordered phases and prompt IDs;
- parallelization rules;
- execution locks;
- protected surfaces and possible external effects;
- branches for stale evidence, failed verification, or approval;
- a completion gate.

## Selection rule

Prefer an existing composite scenario when it already owns the complete workflow. Otherwise begin with one primary prompt and add only required prerequisites or handoffs. Do not load a department pack as an execution graph; compile the relevant capabilities from it.

## Inspect and plan

```powershell
python tools/md.py explain C-108
python tools/md.py plan C-108 --mode AUDIT_ONLY --root . --dry-run
```

The plan output is a contract, not evidence that work happened.

## Parallel work

Parallelize only read-only phases with non-overlapping evidence and artifact ownership. Keep one writer for each source of truth. Run dependent phases sequentially and verify upstream artifacts before downstream use.

## Stop conditions

Stop on verified success, exhausted authority, missing evidence, a failed gate, an explicit human stop, or a bounded loop plateau. Record incomplete work as residual risk; do not translate a partial run into a completion claim.
