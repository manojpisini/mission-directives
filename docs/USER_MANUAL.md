# User Manual

## Purpose

This manual explains how to use the suite without reading all 199 prompts. It focuses on selecting the right outcome, setting honest authority, choosing an evidence lane, understanding generated artifacts, and knowing when work is not complete.

## Mental model

The suite is not a bag of prompts. It is a routed system:

```text
request
→ context and authority
→ prompt or scenario selection
→ evidence and brief
→ production or execution
→ verification
→ residuals and closure
```

Use one atomic prompt when one capability owns the result. Use a composite scenario when the result spans multiple distinct capabilities.

## Starting a run

A useful directive contains:

```text
RUN {PROMPT_ID|SCENARIO_ID|DEPARTMENT_PACK}
MODE {AUDIT_ONLY|PLAN_ONLY|DRAFT_ONLY|APPLY_SAFE|APPLY_APPROVED|VERIFY_ONLY}
ASSURANCE {FAST|STANDARD|HIGH_ASSURANCE}
ROOT {PROJECT_ROOT}
OUTCOME {OBSERVABLE_RESULT}
AUDIENCE {USERS_REVIEWERS_DECISION_MAKERS}
SCOPE {IN_SCOPE}
EXCLUDE {OUT_OF_SCOPE_AND_PROTECTED_SURFACES}
AUTHORITY {ALLOWED_WRITES_AND_EXTERNAL_ACTIONS}
EVIDENCE_LANE {FACTUAL|HYBRID|IMAGINATIVE}
EVIDENCE {AUTHORITATIVE_INPUTS}
MEDIA {SOURCE_AND_EXPORT_FORMATS}
SKILLS {AUTO|EXACT_IDS|NONE}
BUDGET {PROMPTS_CALLS_COST_TIME_PARALLELISM}
CONSTRAINTS {LEGAL_PRIVACY_BRAND_ACCESSIBILITY_TECHNICAL}
QUALITY {ACCEPTANCE_CRITERIA}
```

The most important fields are outcome, authority, evidence, and quality. Missing cosmetic preferences can usually be resolved later; missing authority or evidence may change the entire route.

## Using the MD keyword

When root agent guidance is installed, begin a request with `MD` followed by an exact ID or ordinary task words:

```text
MD C-95
MD research report
MD visual assets for a slide deck
MD audit fix verify
```

The agent should run deterministic keyword lookup first and inspect the selected target before execution. The keyword is a convenience layer; it does not weaken authorization, evidence, skill, loop, or verification rules.

See [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md).

## Choosing by outcome

### Research and analysis

Use deep research, protocol, analytics, fact verification, or a department-specific investigative capability. Public or decision-critical claims normally require `MD-82`.

### Writing and communication

Choose the artifact owner: article, script, academic paper, report, policy, pitch, communication, or social package. Add editorial review only when it materially improves the result.

### Engineering

Use discovery or requirements before implementation when the target is unclear. Use true pairs for debugging, cleanup, refactoring, security remediation, migration, performance, reliability, delivery, and similar change surfaces.

### Visual and interactive work

Choose presentation, dashboard, infographic, diagram, workshop board, web artifact, or frontend refinement. Verify source and exact export separately.

### Organizational work

Use department packs to discover capabilities, then compile the smallest graph. Do not execute an entire department pack.

## Modes

### `AUDIT_ONLY`

Use when you want findings, evidence, or review without changes.

### `PLAN_ONLY`

Use for plans, specifications, acceptance criteria, or approval preparation.

### `DRAFT_ONLY`

Use for local, unapproved artifacts. A draft is not accepted, submitted, published, sent, or deployed.

### `APPLY_SAFE`

Use for reversible local changes within explicit authority.

### `APPLY_APPROVED`

Use only for the exact approved consequential action. A valid receipt, recovery path, and verification plan are required.

### `VERIFY_ONLY`

Use for independent checks. The verifier should not alter the reviewed subject.

## Assurance profiles

Choose the minimum assurance that matches the risk, not the shortest route you prefer.

- FAST: low-risk local work.
- STANDARD: current evidence, typed artifacts, review, verification, residuals.
- HIGH_ASSURANCE: formal evidence, counterevidence, approvals, dry run, recovery, independent verification, lineage.

## Reading marker-rich output

A good run exposes its reasoning products without revealing private chain-of-thought:

```text
@EVIDENCE:market-01 authoritative market report, collected 2026-07-15
#FINDING:market-01 demand is concentrated in two segments
?UNKNOWN:market-02 regional price sensitivity is not measured
+ACTION:market-01 run a limited pricing experiment
=VERIFY:market-01 finding supported by two independent sources
```

Markers let you trace decisions and identify where uncertainty remains.

## Understanding completion

Do not judge completion by length or confidence. Check the prompt's task-specific `<completion_criteria>`.

A run is not complete when:

- a required artifact is missing;
- a verification record is absent;
- a failed action is hidden;
- an unknown is treated as fact;
- a residual has no owner;
- an executive discovered new work and executed it without approval;
- the source is correct but the export is broken;
- publication or deployment was assumed rather than authorized.

## Skills

`SKILLS AUTO` permits the router to consider registered adapters. It does not authorize installation or external effects. Unresolved locks and unreviewed permissions block automatic high-assurance use.

Use `SKILLS NONE` when native prompt execution is sufficient or supply-chain risk is unacceptable.

## Common examples

### Research-backed report

```text
RUN C-95
MODE DRAFT_ONLY
ASSURANCE STANDARD
OUTCOME Produce a decision-ready report with reconciled exhibits and exact PDF QA
AUTHORITY local artifacts only
EVIDENCE_LANE FACTUAL
```

### Safe cleanup

```text
RUN C-04
MODE PLAN_ONLY
ASSURANCE HIGH_ASSURANCE
OUTCOME Identify junk, dead code, generated artifacts, and duplicate sources of truth without deleting anything
AUTHORITY read-only
```

The approved executive run can follow only after evidence proves non-use.

### Brand and deck

```text
RUN C-37 + C-41
MODE DRAFT_ONLY
ASSURANCE STANDARD
OUTCOME Create a coherent brand system and browser-native presentation
EVIDENCE_LANE HYBRID
```

### Imaginative work

```text
RUN C-33
MODE DRAFT_ONLY
ASSURANCE FAST
OUTCOME Draft a short story with a specified viewpoint and scene turn
EVIDENCE_LANE IMAGINATIVE
```

Do not force factual research into fiction unless the work intentionally makes factual claims.

## Failure and residuals

A good run may end in:

- `failed` because verification did not pass;
- `rolled_back` because execution caused damage or uncertainty;
- `residual_open` because approved work remains;
- `!STOP` because evidence, authority, or recovery is insufficient.

These are honest outcomes, not system failures to conceal.

## Where to learn more

- [Operator Guide](OPERATOR_GUIDE.md)
- [Runtime Marker Protocol](RUNTIME_MARKER_PROTOCOL.md)
- [Completion Criteria Guide](COMPLETION_CRITERIA_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)

## Reviewing a paired plan before execution

When a planning prompt has an execution twin, the system will show the completed plan before doing execution work. Review the plan and provide changes, additions, removals, or refinements. The planner applies accepted feedback and presents the revised plan again. After you approve that exact version, the planner asks whether to invoke its named execution twin. Approval of the plan and permission to execute are separate choices.
