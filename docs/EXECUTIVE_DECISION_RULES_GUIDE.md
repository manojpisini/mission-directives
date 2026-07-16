# Executive Decision Rules Guide

## Purpose

Executive prompts take approved action. Procedure alone is insufficient because execution encounters conflicts, incomplete budgets, stale evidence, failed checks, and domain-specific tradeoffs.

`<decision_rules>` defines how the executive chooses without inventing authority.

## Required rule categories

Every executive prompt must contain rules for all five categories.

### 1. Action eligibility

Only approved `+ACTION:{id}` records from the current frozen handoff may execute.

New issues become `#FINDING:{id}` and return to investigation or approval.

### 2. Domain-specific priority

The rule must name what the capability preserves or addresses first.

Examples:

- debugging: causal fix before symptom suppression;
- cleanup: proof of non-use before deletion;
- migration: data integrity and rollback before speed;
- accessibility: blocked user task before visual polish;
- academic writing: methods and evidence before narrative force;
- slides: narrative and legibility before motion;
- security: confirmed reachable control bypass before cosmetic hardening.

### 3. Conflict resolution

When actions conflict, resolve by:

1. safety and protected boundaries;
2. evidence strength;
3. dependency order;
4. public contract, data, or user preservation;
5. reversibility;
6. approved priority.

Do not combine mutually incompatible actions into one batch.

### 4. Budget and partial completion

If time, tokens, cost, or maintenance window cannot complete the whole plan:

- choose the highest-priority dependency-complete batch;
- do not start an action that cannot reach a safe terminal state;
- place remaining actions in the residual register;
- record owners and prerequisites;
- do not claim full completion.

### 5. Hard stops

Stop when:

- approval is stale or absent;
- scope expands;
- the target differs from the approved environment;
- verification fails;
- rollback is uncertain;
- an action weakens a protected boundary;
- a new critical finding changes the plan;
- a tool requires undeclared permissions.

## Example: cleanup executive

```xml
<decision_rules>
- Execute only approved +ACTION:{id} records from the frozen cleanup handoff.
- Delete only when non-use is evidenced across code, build, packaging, runtime, docs, and generated-source boundaries; uncertainty means retain or quarantine.
- Resolve conflicts by safety, evidence, dependency order, compatibility, and reversibility.
- If the budget is insufficient, remove only a dependency-complete batch and defer the rest with owners.
- Emit !STOP:{reason} when runtime dependence appears, rollback is uncertain, or verification fails.
</decision_rules>
```

## Example: model-security executive

```xml
<decision_rules>
- Execute only approved model-security actions against the declared model, dataset, serving path, and environment.
- Prioritize artifact integrity, sensitive-data exposure, unsafe output trust, and abuse controls before quality tuning.
- Do not trade away auditability or rollback for throughput.
- Defer lower-priority controls if the evaluation budget cannot verify them independently.
- Stop on data provenance failure, unsafe external effect, or inability to reproduce the pre-change baseline.
</decision_rules>
```

## Anti-patterns

- no decision rules in an executive prompt;
- generic “use best judgment” language;
- prioritization by ease rather than risk and evidence;
- silent execution of newly discovered work;
- partial execution reported as completion;
- budget rules that permit unsafe half-migrations;
- verification failure treated as a warning rather than a stop.

## Review questions

- What can this executive execute?
- What must it preserve?
- Which finding class comes first?
- What happens when two actions conflict?
- What is a safe partial batch?
- What exact conditions stop the run?

## Validation

All 32 executive prompts must contain `<decision_rules>`. The static audit reports coverage, while adversarial pair fixtures test behavior against contaminated or stale handoffs.
