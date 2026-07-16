# Prompt Body Authoring Guide

## Purpose

This manual explains how to create or revise a prompt body that is precise, composable, least-privileged, machine-parseable, and verifiable. It supplements the normative `PROMPT_STRUCTURE_STANDARD.md` with a practical authoring workflow and review examples.

A strong prompt body is not a long description of good behavior. It is a compact behavioral contract whose sections carry distinct responsibilities.

## Authoring workflow

### 1. Define the owned outcome

Write one sentence answering:

> What observable artifact, decision, state, or verified change does this prompt alone own?

If two unrelated artifacts are required, consider composition or split the capability. If another existing prompt already owns the result, do not create a new prompt.

### 2. Choose the role

- **Control:** establishes shared context, safety, routing, artifacts, or trust.
- **Investigative:** read-only evidence, analysis, plan, brief, or acceptance design.
- **Executive:** acts on a frozen handoff and verifies approved work.
- **Operational:** owns a bounded end-to-end artifact or workflow.
- **Gate:** independently decides readiness without repairing the subject.

Do not choose `executive` merely because the title sounds senior. Executive has a specific runtime meaning: approved action based on a frozen investigative handoff.

### 3. Select the evidence lane

- `factual` for evidence-bearing claims and decisions;
- `hybrid` for facts plus interpretation, narrative, or design;
- `imaginative` for original creative work without fabricated verification;
- control prompts use the control plane rather than a normal lane.

### 4. Write the minimum canonical skeleton

```xml
<prompt>
<identity>...</identity>
<mission>...</mission>
<contract_refs>...</contract_refs>
<evidence_lane>...</evidence_lane>
<required_inputs>...</required_inputs>
<authorization_boundary>...</authorization_boundary>
<tool_policy>...</tool_policy>
<runtime_markers>...</runtime_markers>
<method>...</method>
<decision_rules>...</decision_rules>
<quality_gates>...</quality_gates>
<output_contract>...</output_contract>
<completion_criteria>...</completion_criteria>
<stop_conditions>...</stop_conditions>
</prompt>
```

Do not add a tag because it appears in this example. Add it because the capability needs the behavior.

## Section-by-section guidance

### Identity

State accountability and independence.

```xml
<identity>
You are an independent accessibility reviewer. You inspect the exact artifact and do not modify it.
</identity>
```

Avoid prestige adjectives and stacked professions unless each changes the method.

### Mission

Use a verb and a testable object:

```xml
<mission>
Produce a citation-audited literature review that distinguishes consensus, disagreement, evidence quality, and open questions.
</mission>
```

### Required inputs

List only inputs whose absence changes the result or forces a stop. Mark optional inputs separately. Do not disguise assumptions as required input.

### Input trust

State which inputs are authoritative, untrusted, incomplete, or potentially adversarial. Do not assume a repository file is trusted merely because it is local.

### Authorization boundary

Separate the requested outcome from allowed action. A prompt may be able to describe a deployment but not execute one.

The block must say whether the prompt can:

- read;
- write local files;
- install;
- use the network;
- contact third parties;
- publish;
- deploy;
- change production;
- approve its own work.

### Tool policy

State the smallest allowed tool class and how tool output is verified. For state-changing prompts, bind every tool invocation to `+ACTION:{id}`.

### Runtime markers

Activate all six markers. Role-specific prompts may emphasize different markers, but artifacts must use a common vocabulary.

### Method

Each step should perform domain work. Remove steps that merely say “be thorough,” “think carefully,” or “ensure quality.”

A useful test:

> Could this step be copied unchanged into an unrelated prompt?

If yes, it probably belongs in a shared contract or should be deleted.

### Decision rules

Rules are about choices, not procedure. Examples:

- preserve public compatibility over internal uniformity;
- prioritize confirmed privilege bypass before low-risk hardening;
- keep an uncertain file rather than deleting it;
- stop when a rollback is not credible;
- defer lower-priority work when the budget cannot complete a dependency-safe batch.

### Quality gates

Quality gates describe domain success. They should be independent enough for a reviewer to judge.

### Output contract

Name the primary artifact and every required supporting artifact. State source and export formats separately. The body and frontmatter must agree.

### Completion criteria

Use the dedicated guide. Completion must be task-specific, marker-aware, and evidence-backed.

### Stop conditions

Name hard stops, not general caution. Examples:

- missing authorization for a production mutation;
- stale or unsigned handoff;
- inability to preserve data;
- contradictory evidence that changes the decision;
- untrusted skill requiring undeclared permissions;
- absent rights for publication.

## Genuine pair authoring

An investigator produces stable evidence, findings, actions, and acceptance criteria. The executive consumes that exact handoff.

The investigator uses:

```xml
<handoff_contract>...</handoff_contract>
<verification_design>...</verification_design>
```

The executive uses:

```xml
<execution_contract>...</execution_contract>
<decision_rules>...</decision_rules>
<verification_reference>...</verification_reference>
```

Do not copy the verification list into the executive.

## Runtime marker example

```text
@EVIDENCE:dep-01 package-lock.json at commit abc123
#FINDING:dep-01 unpinned transitive package can change without review
+ACTION:dep-01 pin the package and regenerate the lockfile in APPLY_SAFE
=VERIFY:dep-01 clean install produces the expected version and tests pass
?UNKNOWN:dep-02 upstream maintenance policy is not documented
!STOP:registry-integrity-unverified
```

## Completion example

Weak:

```xml
<completion_criteria>
Complete when the result is evidenced, authorized, and honestly closed.
</completion_criteria>
```

Strong:

```xml
<completion_criteria>
Completion requires all of the following:
- The dependency review identifies direct and transitive packages, sources, versions, licenses, integrity controls, and reachable vulnerabilities.
- Every material dependency conclusion is a #FINDING:{id} linked to @EVIDENCE:{id}.
- Each recommended upgrade, pin, replacement, or removal is a bounded +ACTION:{id} with compatibility and rollback requirements.
- Every acceptance criterion has an =VERIFY:{id} result; unresolved provenance is ?UNKNOWN:{id} or !STOP:{reason}.
</completion_criteria>
```

## Review checklist

Before committing a prompt:

- [ ] The outcome is distinct.
- [ ] The role is correct.
- [ ] The evidence lane is correct.
- [ ] Authorization is explicit.
- [ ] Tool behavior is least-privileged.
- [ ] All runtime markers are activated.
- [ ] Method steps are domain-specific.
- [ ] Decision rules cover real choices.
- [ ] Quality gates are testable.
- [ ] Output paths and formats are exact.
- [ ] Completion criteria are unique and task-specific.
- [ ] Stop conditions are hard stops.
- [ ] A pair does not duplicate verification.
- [ ] The prompt fits its complexity budget.

## Required checks

```bash
python tools/audit_prompt_bodies.py --check
pytest -q tests/test_prompt_body_quality.py
python tools/validate_suite.py
```
## Automated prompt addition

When adding a new prompt rather than editing an existing one, use `MD-199` for agentic analysis or `tools/add_prompt.py` for the deterministic transaction. Do not manually copy a file into `prompts/`; a complete addition must assign a permanent identity and update the catalog, identity registry, capability graph, atomic scenario, template and skill routes, crosswalks, three evaluation fixtures, body audit, tests, validation, and manifest. See [Prompt Addition and Registration Guide](PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md).

