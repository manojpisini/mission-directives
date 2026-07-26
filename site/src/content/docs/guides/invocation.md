---
title: Invocation and Planning
description: Exact IDs, natural intent, route comparison, planning modes, and execution handoffs.
---

## Natural intent first

```powershell
python tools/md.py route "<complete outcome, constraints, evidence, and expected artifact>"
```

Do not reduce a multi-part outcome to one profession label. Include what must be produced, what authority exists, and what proves success.

## Exact identity

Use an exact `MD-###` for one capability, `C-###` for a composite workflow, or a department-pack ID when the route is deliberate. Exact identity bypasses lexical selection, not the capability contract.

```powershell
python tools/md.py explain MD-37
python tools/md.py explain C-108
```

## Modes

| Mode | Use |
| --- | --- |
| `AUDIT_ONLY` | inspect and report without mutation |
| `PLAN_ONLY` | produce an execution-ready plan |
| `DRAFT_ONLY` | create a non-published artifact |
| `APPLY_APPROVED` | perform only the approved change |
| `VERIFY_ONLY` | validate an existing result |

Allowed modes come from the selected prompt or scenario. The router does not invent permission.

## Planning and exact twins

Some planning prompts declare one reciprocal execution twin. The plan must be frozen, reviewed, revised if needed, approved again, and explicitly authorized for that exact twin. Original task consent is not inferred as execution consent.

## Practical sequence

```powershell
python tools/md.py route "full request"
python tools/md.py compare <candidate-a> <candidate-b>
python tools/md.py explain <winner>
python tools/md.py plan <winner> --mode PLAN_ONLY --root . --dry-run
```

Then load only the control prompts, selected prompt bodies, and declared prerequisites needed for that graph.
