# Evaluation Manual

## Purpose

Evaluation determines whether the suite behaves as intended. File counts and valid frontmatter are necessary but do not prove model behavior, tool safety, or artifact quality.

## Proof levels

### Static validation

Checks IDs, tags, graphs, schemas, catalogs, paths, locks, and documentation presence.

### Deterministic tests

Checks reference Python behavior such as routing, state transitions, no-selection, and manifest validation.

### Fixture coverage

Specifies expected and prohibited behavior for healthy, problematic, and adversarial cases.

### Live model measurement

Runs named models against fixtures and records schema conformance, refusal correctness, fabrication, cost, and latency.

### Live skill conformance

Runs an installed locked skill and validates the output against its adapter contract.

### Human golden review

Promotes a complete run only after accountable human review.

## Prompt fixtures

Each prompt has:

- healthy fixture;
- problematic fixture;
- adversarial fixture.

Adversarial cases include prompt injection, fabricated evidence, scope creep, stale inputs, missing authority, and unsafe tool requests.

## Pair fixtures

Every genuine pair has a contaminated-handoff fixture. The executive must refuse, flag, or escalate rather than silently execute.

Contamination types include:

- stale snapshot;
- contradictory findings;
- injected instructions in evidence;
- unfrozen acceptance criteria;
- expired approval;
- action outside scope.

## Pair-versus-single evaluation

The same task is run as:

1. investigation → handoff → executive;
2. one bounded full-cycle prompt.

Score:

- safety;
- missed findings;
- action precision;
- reviewer clarity;
- token cost;
- latency;
- unnecessary ceremony.

A pair is retained only when the split materially helps.

## Prompt-body static audit

`audit_prompt_bodies.py` adds focused checks for:

- task-specific completion criteria;
- tool-policy presence;
- marker activation;
- authorization naming;
- executive decision rules;
- pair verification de-duplication;
- self-dependencies;
- complexity budgets.

## Model benchmarks

Use:

```bash
python tools/run_model_benchmarks.py
```

Do not populate measurements from memory or vendor claims. Record the exact model revision, fixture revision, temperature, tool configuration, date, cost, and latency.

## Skill conformance

Use:

```bash
python tools/run_skill_conformance.py \
  --skill-id <SKILL_ID> \
  --artifact <OUTPUT_PATH>
```

The test must use the locked revision. Output remains quarantined until the contract passes.

## Golden runs

Machine-reference runs are not golden. Promotion requires:

- complete manifest;
- evidence snapshot;
- artifacts;
- verification;
- residuals;
- human reviewer identity;
- decision and rationale;
- immutable hashes.

```bash
python tools/promote_golden_run.py
```

Promoted manifests are counted automatically in `EVALUATION_STATUS.json` and
`python tools/md.py lifecycle`. A promotion is not inferred from the presence of
a machine reference run.

## Route-confusion regression set

`evaluations/route_confusion.json` contains near-neighbor natural-language
requests whose correct owners differ. The deterministic evaluation harness
checks status, selection type, and exact ordered targets through
`md.route_intent`. Add a case whenever operator feedback reveals ambiguous or
incorrect selection.

`evaluations/exact_twin_negative_cases.json` separately proves that plan
approval without execution consent, changes after approval, and executor
mismatch all fail closed.

## Lifecycle report

```bash
python tools/md.py lifecycle
```

The report derives prompt and scenario counts, promoted golden coverage, skill
locks, live skill passes, measured production models, and external completion
blockers directly from canonical files. `structural_surface: implemented` does
not override `status: external_evidence_pending`.

## Mutation testing

Mutations should include:

- generic completion criteria;
- removed tool policy;
- removed runtime marker;
- alternate authorization tag;
- missing executive decision rule;
- duplicated pair verification;
- self-dependency;
- stale handoff acceptance;
- unauthorized external action;
- removed stop condition.

A useful invariant must fail when its protection is removed.

## Running the deterministic evaluation chain

```bash
python tools/audit_prompt_bodies.py --check
python tools/run_evaluations.py
python tools/run_tests.py
python tools/validate_suite.py
```

## Interpreting status

`pass_with_external_measurements_pending` means deterministic proof passed but live model, live skill, or human-golden proof remains incomplete. It is an honest status, not a failure.
