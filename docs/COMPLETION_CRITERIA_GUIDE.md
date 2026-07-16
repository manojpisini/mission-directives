# Completion Criteria Guide

## Why completion criteria exist

`<completion_criteria>` is the contract that prevents a model or operator from confusing activity with completion. It answers:

> What observable evidence proves this exact prompt has fulfilled its responsibility?

It is not a summary of the mission, a motivational sentence, or a copy of suite-wide truth rules.

## Required properties

Every completion block must:

1. contain at least three explicit conditions;
2. name the task, artifact, decision, or changed state;
3. include domain-specific success conditions;
4. require `=VERIFY:{id}` evidence;
5. state what happens to unknowns, failures, residuals, and missing authority;
6. remain unique to the prompt.

## Completion by role

### Control

Completion proves the shared contract is resolvable by downstream prompts.

Example conditions:

- the runtime context identifies scope, authority, and protected surfaces;
- downstream prompts can determine permitted modes;
- unresolved inputs are `?UNKNOWN:{id}`;
- the control artifact has an `=VERIFY:{id}` integrity record.

### Investigative

Completion proves the evidence and handoff are ready, not that the proposed action occurred.

Require:

- evidence index;
- finding register;
- bounded actions or recommendations;
- acceptance criteria;
- evidence freshness;
- explicit unknowns and contradictions;
- frozen handoff verification.

### Executive

Completion proves approved actions were handled and acceptance criteria were evaluated.

Require:

- each approved `+ACTION:{id}` executed, skipped, or deferred;
- unchanged action IDs;
- current approval and handoff;
- `=VERIFY:{id}` result for every criterion;
- rollback and residual state;
- hard stop for scope expansion or failed verification.

### Operational

Completion proves the declared artifact or workflow works for its audience and medium.

Require the exact source artifact, exact exports, domain quality gates, and unresolved dependencies.

### Gate

Completion is an independent decision, not a repair. Require the decision, supporting evidence, blocking findings, and verification status.

## How to derive task-specific criteria

Use these sources in order:

1. mission;
2. primary artifact;
3. domain quality gates;
4. investigative verification design;
5. execution method;
6. audience task;
7. required residual and rollback records.

Do not derive completion solely from generic control text.

## Good patterns

### Creative writing

```xml
<completion_criteria>
Completion requires all of the following:
- The manuscript fulfills the requested form, viewpoint, length, and scene purpose.
- Every scene changes the situation and preserves causal continuity.
- Character motives and language remain distinct, and concrete detail carries emotional work.
- Editorial review records each accepted quality gate as =VERIFY:{id}.
- Unresolved continuity questions remain ?UNKNOWN:{id}; rights or safety conflicts trigger !STOP:{reason}.
</completion_criteria>
```

### Security remediation

```xml
<completion_criteria>
Completion requires all of the following:
- Every approved remediation +ACTION:{id} is executed, deferred, or rejected with evidence.
- The original vulnerable path is no longer reproducible under the authorized test plan.
- Negative and abuse-case tests pass without weakening another control.
- Every investigative criterion has an =VERIFY:{id} result tied to exact commands or observations.
- New findings are not silently fixed; they enter the residual register or trigger !STOP:{reason}.
</completion_criteria>
```

### Report production

```xml
<completion_criteria>
Completion requires all of the following:
- The report answers the declared decision question and reconciles every material figure to its source.
- Exhibits, narrative, terminology, and recommendations agree.
- The exact DOCX/PDF/export is checked for clipping, broken links, accessibility, and pagination.
- Claims and exports have =VERIFY:{id} records; unresolved evidence is ?UNKNOWN:{id}.
</completion_criteria>
```

## Anti-patterns

Reject:

- “Complete when high quality.”
- “Complete when evidenced and honestly closed.”
- “Complete when all requirements are met.”
- a copy of `<quality_gates>` with no artifact or verification requirement;
- a claim that execution occurred in an investigative prompt;
- a gate that repairs the subject before issuing a decision;
- a completion block shared unchanged across unrelated prompts.

## Static checks

The body audit reports:

- completion blocks present;
- unique normalized blocks;
- known boilerplate matches;
- duplicate count;
- bullet count;
- task-title overlap;
- `=VERIFY:{id}` presence.

Run:

```bash
python tools/audit_prompt_bodies.py --check
```

Static uniqueness is necessary but not sufficient. Live fixtures must still test whether models follow the conditions.
