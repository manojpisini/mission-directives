# Plan Review and Exact-Twin Execution Guide

## Purpose

This guide defines the mandatory transition from a paired investigative planning prompt to its one authorized execution twin. The policy applies to every prompt whose frontmatter declares `prompt_role: investigative`, `pairing_required: true`, and `paired_prompt_id`.

The planner does not choose an executor dynamically. Its `paired_prompt_id` is the sole source of truth. The declared executor must reciprocally name the planner, have `prompt_role: executive`, and require the planner in `requires`.

## Non-negotiable rule

```text
plan → user review → requested revisions → re-verification → re-freeze
→ user re-review and approval → explicit execution consent
→ exact reciprocal executor only
```

No stage may be inferred from the original task. Asking for a complete result does not waive the plan-review gate.

## Why review and execution consent are separate

Plan review answers: “Is this the correct plan?”

Execution consent answers: “May this exact executor act on the approved frozen plan now?”

A user may approve a plan but postpone execution. A user may request edits without approving anything. The runtime therefore stores separate receipts and states.

## Canonical metadata

A paired planner declares:

```yaml
paired_prompt_id: MD-30
plan_review_required: true
execution_consent_required: true
exact_twin_only: true
review_cycle: review_revise_refreeze_rereview_then_consent
```

Its executor declares:

```yaml
paired_prompt_id: MD-29
accepted_planning_prompt_id: MD-29
reviewed_handoff_required: true
execution_consent_required: true
exact_twin_only: true
```

Do not add a second twin field or a routing override. Duplicate sources of truth can drift.

## Planner behavior

After investigation and handoff verification, the planner must:

1. freeze the evidence snapshot, findings, action plan, and acceptance criteria;
2. present the completed plan and material artifacts to the user;
3. explicitly invite changes, improvements, additions, removals, and refinements;
4. record review feedback without interpreting it as approval;
5. apply accepted feedback to every affected artifact;
6. update evidence or unknown records when the feedback changes assumptions;
7. re-run handoff-readiness verification;
8. re-freeze the complete handoff under a new content hash;
9. ask the user to review the revised plan again;
10. after explicit approval, ask whether to invoke the exact `paired_prompt_id`.

The execution question must name both the exact prompt ID and title.

## Review decisions

### Changes requested

The workflow enters `plan_revision_pending`. Prior plan approval and execution consent are invalidated. The planner revises, verifies, and re-freezes before requesting another review.

### Approved

The workflow enters `execution_consent_pending`. Approval does not execute the twin. The planner asks one explicit consent question.

### Declined

The workflow closes without execution and records an explicit residual or declined-execution record.

## Exact-twin enforcement

For planner `MD-29`, only `MD-30` is legal. The following must fail:

```text
MD-29 → MD-28
MD-29 → another debugging or engineering executor
MD-29 → a dynamically selected “better” executor
MD-29 → an executor inferred from keywords
```

Similarity, shared category, skill availability, or operator preference does not create another twin. A different executor requires a new canonical prompt relationship and suite review, not a runtime substitution.

## Executor admission checks

Before work begins, the executive must verify:

- planner ID equals its reciprocal `paired_prompt_id`;
- handoff hash matches the reviewed version;
- review receipt decision is `approved`;
- no plan artifact changed after review;
- execution-consent receipt names this exact executor;
- the consent applies to the current handoff hash;
- action scope, mode, environment, budget, and approval are current;
- no unresolved `!STOP:{reason}` blocks execution.

Any mismatch is `!STOP:invalid-reviewed-handoff-or-exact-twin-consent`.

## Runtime states

```text
handoff_frozen
→ plan_review_pending
→ plan_revision_pending      (when changes are requested)
→ handoff_frozen             (after revisions and re-verification)
→ plan_review_pending        (re-review)
→ execution_consent_pending  (after plan approval)
→ dry_run_ready              (DRAFT_ONLY / APPLY_SAFE path)
   or approval_pending       (APPLY_APPROVED path)
→ executing
```

## Runtime commands

Inspect the exact twin:

```bash
python tools/md.py pair-status MD-29 \
  --handoff-ready \
  --review-status approved
```

Freeze a handoff for review:

```bash
python tools/md.py freeze-pair-handoff run.json MD-29 \
  --handoff-hash sha256:<digest>
```

Record requested changes:

```bash
python tools/md.py review-pair-plan run.json MD-29 \
  --decision changes_requested \
  --feedback "Add Windows coverage and rollback evidence"
```

After revising, call `freeze-pair-handoff` again with the new hash. Then record approval:

```bash
python tools/md.py review-pair-plan run.json MD-29 \
  --decision approved
```

Record explicit consent:

```bash
python tools/md.py consent-pair-execution run.json MD-29 --approve
```

The runtime writes only `MD-30` into `authorized_execution_prompt_ids`.

## Failure examples

### Alternate executor requested

```text
Requested: MD-28
Required exact twin: MD-30
Result: rejected
```

### Revision after approval

Any material edit changes the handoff hash. The prior review and consent no longer apply. Return to `plan_review_pending` after re-freezing.

### Original request already says “execute”

The planner still presents the plan for review. The original request establishes desired outcome, not approval of an unseen plan.

### User says “looks fine” before seeing the final revision

Do not infer approval. Present the revised frozen plan and ask for review of that exact version.

## Validation

```bash
pytest -q tests/test_prompt_body_quality.py tests/test_md.py
python tools/audit_prompt_bodies.py --check
python tools/build_capability_graph.py --check
python tools/validate_suite.py
```

The validator checks all 32 genuine pairs, exact reciprocal IDs, required body blocks, state-machine support, and runtime refusal of alternate executors.

## Related guides

- [Pair Authoring and Verification Guide](PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md)
- [Executive Decision Rules Guide](EXECUTIVE_DECISION_RULES_GUIDE.md)
- [Operator Guide](OPERATOR_GUIDE.md)
- [Runtime Marker Protocol](RUNTIME_MARKER_PROTOCOL.md)
- [Prompt Body Validation Guide](PROMPT_BODY_VALIDATION_GUIDE.md)
