# Pair Authoring and Verification Guide

## Purpose

A genuine pair separates non-mutating investigation from authorized execution. The split is justified only when the handoff improves safety, reviewability, parallelism, or output quality.

Pairs are not a naming style. They are a runtime architecture.

## The five-part pair test

Create a pair only when all conditions are true:

1. Investigation can remain read-only.
2. Investigation produces a stable, reviewable handoff.
3. Execution owns a materially distinct production or mutation responsibility.
4. Both roles share objective acceptance criteria.
5. The split improves the work more than it adds ceremony.

If a single bounded prompt is clearer and equally safe, use a standalone prompt.

## Investigator responsibilities

The investigator must produce:

- frozen evidence snapshot;
- evidence index;
- `#FINDING:{id}` register;
- bounded `+ACTION:{id}` plan;
- dependencies and action risk;
- authorization requirements;
- rollback needs;
- acceptance criteria;
- `?UNKNOWN:{id}` and contradictions;
- `=VERIFY:{id}` handoff-readiness record.

The investigator must not modify the governed subject or approve its own plan.

## Executive responsibilities

The executive must:

- verify the handoff is current and approved;
- preserve evidence, finding, action, and criterion IDs;
- dry-run state-changing work;
- execute dependency-complete approved batches;
- apply decision rules when actions conflict or budgets are limited;
- reference the frozen acceptance criteria;
- record each result as `=VERIFY:{id}`;
- stop on scope expansion, stale approval, failed verification, or uncertain rollback;
- record residuals and rollback state.

## Verification ownership

The investigator owns `<verification_design>` and the acceptance-criteria artifact.

The executive owns `<verification_reference>` and the result records.

Correct relationship:

```text
MD-29 verification design
→ acceptance_criteria.json with criterion IDs
→ frozen handoff and approval
→ MD-30 executes actions
→ MD-30 records =VERIFY results against the same IDs
```

## Why duplication is prohibited

Repeating the same verification list in the executive creates three risks:

1. the two lists drift;
2. the executive silently weakens or omits criteria;
3. the suite pays the same token cost twice without adding behavior.

An executive may contain `<verification_additions>` only when execution reveals a genuinely new check that was not knowable during investigation. The new check is recorded as a finding and reviewed rather than silently replacing the frozen plan.

## Handoff validation

Before execution, verify:

- investigator prompt and capability IDs;
- evidence snapshot hash and freshness;
- action-plan hash;
- acceptance-criteria hash;
- approval receipt;
- target environment;
- protected surfaces;
- action budget;
- rollback readiness;
- unresolved blockers.

Failure produces `!STOP:invalid-or-stale-handoff`.

## Executive decision rules

Every executive must contain decision rules. At minimum:

- action eligibility;
- one domain-specific priority or preservation rule;
- conflict resolution;
- budget behavior;
- stop behavior.

See `EXECUTIVE_DECISION_RULES_GUIDE.md`.

## Pair completion

Investigator completion means the handoff is ready. It does not mean the change is complete.

Executive completion means:

- every approved action is dispositioned;
- every acceptance criterion has a result;
- failures and residuals are explicit;
- rollback status is known;
- no new finding was silently executed.

## Pair review checklist

- [ ] The investigator is read-only.
- [ ] The executive requires the investigator.
- [ ] The handoff is typed and frozen.
- [ ] IDs remain stable.
- [ ] The investigator owns verification design.
- [ ] The executive references rather than duplicates criteria.
- [ ] Executive decision rules are domain-specific.
- [ ] New findings cannot be executed without approval.
- [ ] Dry-run and rollback requirements match risk.
- [ ] Pair-versus-single evaluation exists.

## Validation

```bash
pytest -q tests/test_prompt_body_quality.py
python tools/run_evaluations.py
python tools/validate_suite.py
```

The body validator rejects executive `<verification>` blocks and requires `<verification_reference>` for all paired executives.

## Mandatory user review and exact execution twin

Every paired investigator contains `<plan_review_and_execution_gate>`. Handoff readiness starts the review cycle; it does not authorize execution.

The investigator must present the plan, invite changes and refinements, incorporate accepted feedback, re-run readiness checks, re-freeze the handoff, and request review again. Only after explicit approval may it ask whether to invoke the exact reciprocal `paired_prompt_id`.

Every paired executive contains `<reviewed_handoff_authority>`. It rejects any handoff from another planner, any version changed after approval, and any consent that names a different executor. See [Plan Review and Exact-Twin Execution Guide](PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md).
