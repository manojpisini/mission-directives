# Exact Paired Execution Review Gate Implementation Plan

> **For agentic workers:** Implement task-by-task with regression tests before production changes.

**Goal:** Require every investigative planning prompt with a true execution twin to present its plan for user review, incorporate requested refinements, re-freeze the handoff, ask for explicit execution consent, and dispatch only its exact reciprocal twin.

**Architecture:** `paired_prompt_id` remains the single source of truth. Prompt bodies declare a concise review-and-consent contract, the runtime exposes deterministic pair lookup and review/consent state transitions, and validation rejects missing gates, non-reciprocal twins, mismatched dispatch, or automatic execution before review.

**Tech Stack:** Markdown prompt contracts, YAML frontmatter, Python 3 runtime and validators, JSON Schema, pytest.

## Global Constraints

- Preserve all existing prompts, scenarios, capabilities, skill routes, schemas, and policies.
- Do not infer user consent from the original task.
- Do not permit a planning prompt to invoke any executor other than its exact reciprocal `paired_prompt_id`.
- Requested plan changes must be incorporated and the handoff re-frozen before consent is requested.
- User review and execution consent are distinct receipts.

---

### Task 1: Add failing pair-review contract tests

**Files:**
- Modify: `tests/test_prompt_body_quality.py`
- Modify: `tests/test_md.py`

- [ ] Assert every investigative paired prompt contains the review gate and exact twin ID.
- [ ] Assert every executive prompt accepts only the reciprocal planner and reviewed handoff.
- [ ] Assert pair lookup rejects non-investigative, unknown, and mismatched executors.
- [ ] Assert plan review must precede execution consent.
- [ ] Assert changes requested require revision and re-freeze before consent.

### Task 2: Implement deterministic pair workflow

**Files:**
- Modify: `tools/md.py`
- Create: `schemas/plan_review_receipt.schema.json`
- Create: `schemas/execution_consent_receipt.schema.json`
- Modify: `schemas/run_manifest.schema.json`
- Modify: `run_state_machine.json`

- [ ] Add exact reciprocal pair resolution.
- [ ] Add plan-review disposition logic.
- [ ] Add manifest commands for review, re-freeze, consent, and exact twin preparation.
- [ ] Reject all alternate executors.

### Task 3: Update all true pair prompt bodies

**Files:**
- Modify: 32 investigative prompt files.
- Modify: 32 executive prompt files.

- [ ] Add review and execution handoff contract to each planner.
- [ ] Add reviewed-handoff authority contract to each executor.
- [ ] Use the exact `paired_prompt_id` in each body.
- [ ] Keep prompt-specific completion criteria intact.

### Task 4: Strengthen validation and graph semantics

**Files:**
- Modify: `tools/audit_prompt_bodies.py`
- Modify: `tools/validate_suite.py`
- Modify: `tools/build_capability_graph.py`

- [ ] Validate all pair gates and exact IDs.
- [ ] Add review and consent edges to the capability graph.
- [ ] Reject any pair dispatch not sourced from reciprocal frontmatter.

### Task 5: Update manuals and examples

**Files:**
- Modify: `PROMPT_SUITE_CONVENTIONS.md`
- Modify: `PROMPT_STRUCTURE_STANDARD.md`
- Modify: `PROMPT_EXECUTION_ORDER.md`
- Modify: `docs/PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md`
- Modify: `docs/USER_MANUAL.md`
- Modify: `docs/OPERATOR_GUIDE.md`
- Create: `docs/PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md`
- Modify: `MANUALS.md`
- Modify: `README.md`

- [ ] Document review, revision, re-freeze, consent, and exact-twin dispatch.
- [ ] Include successful, revision-required, declined, and mismatch examples.

### Task 6: Rebuild generated artifacts and verify archive

**Files:**
- Regenerate: `catalog.json`, `PROMPT_CATALOG.md`, `capability_graph.json`, body audit, manifest, validation, test results.
- Update: `VERSION`, `RELEASE_ID`, all prompt `suite_version` fields.

- [ ] Run all tests and validators.
- [ ] Build ZIP and SHA-256.
- [ ] Extract ZIP independently and rerun verification.
