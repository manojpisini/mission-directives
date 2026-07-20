# Structured Prompt Design Standard

This document defines the canonical body contract for every prompt in the suite. It is normative: prompt authors, transformation scripts, validators, scenario compilers, skill adapters, and model adapters must use the same tag names and semantics.

The standard separates four concerns that are often collapsed into one long instruction:

1. **What the prompt is responsible for.**
2. **What evidence, authority, and tools it may use.**
3. **How it performs the task and makes decisions.**
4. **What observable evidence proves completion.**

A prompt is not complete merely because it contains all tags. Each populated tag must change the model's behavior, the runtime's routing, or the verifier's ability to judge the result.

## Canonical shape

```xml
<prompt>
  <identity>Role, accountability, and independence.</identity>
  <mission>One observable outcome.</mission>
  <contract_refs>Shared control contracts applied by reference.</contract_refs>
  <evidence_lane>Factual, hybrid, imaginative, or control.</evidence_lane>
  <required_inputs>Inputs without which the task cannot be completed honestly.</required_inputs>
  <input_trust>Trusted, untrusted, and unresolved input boundaries.</input_trust>
  <authorization_boundary>What may be read, written, changed, published, or executed.</authorization_boundary>
  <tool_policy>Least-privileged tool and skill behavior.</tool_policy>
  <runtime_markers>Required machine-parseable evidence and state markers.</runtime_markers>
  <method>Ordered task-specific work method.</method>
  <investigation>Read-only investigative method for a genuine pair.</investigation>
  <execution>Authorized action method for a genuine pair.</execution>
  <decision_rules>How conflicts, priorities, budgets, and stop conditions resolve.</decision_rules>
  <handoff_contract>Frozen artifacts passed from investigation to execution.</handoff_contract>
  <verification_design>Acceptance design produced by an investigator.</verification_design>
  <verification_reference>Executive reference to the frozen acceptance criteria.</verification_reference>
  <skill_routing>Preferred adapters, fallback, and output quarantine.</skill_routing>
  <artifact_medium>Medium-specific source, accessibility, and export requirements.</artifact_medium>
  <quality_gates>Task-specific quality conditions.</quality_gates>
  <output_contract>Typed files, formats, paths, and records.</output_contract>
  <completion_criteria>Observable conditions proving the exact task is complete.</completion_criteria>
  <stop_conditions>Conditions requiring !STOP.</stop_conditions>
</prompt>
```

## Required body tags

Every prompt body must contain:

- `<identity>`
- `<mission>`
- `<authorization_boundary>`
- `<tool_policy>`
- `<runtime_markers>`
- `<output_contract>`
- `<completion_criteria>`

Every non-control prompt must also declare an `<evidence_lane>`.

Every executive prompt must contain:

- `<execution_contract>` or an equivalent explicit frozen-handoff requirement;
- `<decision_rules>`;
- `<verification_reference>`;
- an authorized execution or production method;
- task-specific completion criteria.

A paired executive must not repeat the investigator's verification list. The investigator owns the acceptance criteria; the executive references and records results against those stable criterion IDs.

## Tag semantics

### `<identity>`

Defines who is accountable, not a decorative persona. It should state whether the prompt is independent, read-only, operational, executive, or a gate.

Good:

```xml
<identity>
You are the independent release-readiness gate. You review evidence but do not repair or approve your own work.
</identity>
```

Weak:

```xml
<identity>
You are a world-class expert.
</identity>
```

### `<mission>`

States one observable result. Avoid multi-paragraph ambitions or repeated quality adjectives.

### `<authorization_boundary>`

This is the only canonical body tag for action authority. Do not introduce synonyms such as `<security_execution_boundary>`, `<write_permissions>`, or `<action_scope>`.

It must distinguish:

- read-only inspection;
- local draft creation;
- reversible local changes;
- approval-gated consequential changes;
- external actions such as publishing, sending, deployment, installation, or contacting third parties;
- protected surfaces and hard stops.

Prompt prose does not grant runtime permission. The runtime policy engine remains authoritative.

### `<tool_policy>`

Defines least-privileged tool behavior for the prompt's role and risk. It must answer:

- which tool classes are allowed;
- which are prohibited;
- whether network access is allowed;
- whether writes are allowed;
- whether installation, sending, publishing, or deployment is allowed;
- how tool output is treated;
- how each invocation is linked to evidence, action, and verification IDs.

Named skills are not implicitly trusted. Tool and skill output remains quarantined until scope, schema, provenance, and content checks pass.

### `<runtime_markers>`

Every prompt must activate the full marker protocol:

- `@EVIDENCE:{id}`
- `?UNKNOWN:{id}`
- `#FINDING:{id}`
- `+ACTION:{id}`
- `=VERIFY:{id}`
- `!STOP:{reason}`

A prompt may emphasize a subset according to its role, but it must preserve the complete vocabulary so artifacts remain composable across prompts.

### `<method>`, `<investigation>`, and `<execution>`

These blocks contain domain work, not suite-wide boilerplate. Steps should be ordered, testable, and materially different across capabilities.

Use `<investigation>` and `<execution>` only when a genuine pair exists. Standalone prompts normally use `<method>`.

### `<decision_rules>`

Decision rules are mandatory for executive prompts and recommended whenever the task involves prioritization, conflict, uncertainty, limited budget, or consequential action.

Executive rules must cover:

1. action eligibility from the frozen handoff;
2. domain-specific prioritization;
3. conflict resolution;
4. budget or partial-completion behavior;
5. conditions that stop execution.

### `<verification_design>` and `<verification_reference>`

The investigative side produces verification design and acceptance-criteria artifacts. The executive side references those artifacts by prompt and criterion ID.

Correct:

```xml
<verification_reference>
Use the frozen acceptance-criteria artifact produced by MD-29. Preserve criterion IDs and record each outcome as =VERIFY:{id}.
</verification_reference>
```

Incorrect:

```xml
<verification>
- regression test passes
- full suite passes
- telemetry looks correct
</verification>
```

when that list already appears byte-for-byte in the investigator.

### `<quality_gates>`

Quality gates are task-specific. They may express craft, factual, functional, accessibility, security, visual, or operational standards.

Examples:

- every scene changes the situation;
- citations support the exact scholarly proposition;
- token and component sources of truth are not duplicated;
- clean installation reproduces the same dependency graph;
- dashboard metrics reconcile to the declared source definitions.

Avoid generic gates such as “high quality,” “professional,” or “comprehensive.”

### `<completion_criteria>`

Completion criteria answer **what proves this exact prompt is done**. They are not a restatement of the universal execution contract.

Every completion block must:

- contain at least three explicit conditions;
- name the task or its primary artifact;
- include task-specific outcomes or gates;
- require `=VERIFY:{id}` evidence;
- state how unknowns, residuals, failed checks, and missing authority are handled;
- remain unique to the prompt.

The suite validator rejects known boilerplate completion sentences and repeated full blocks.

## Canonical ordering

Recommended order:

```text
identity
mission
contract_refs
evidence_lane
required_inputs / required_context
input_trust
authorization_boundary
tool_policy
runtime_markers
method or investigation/execution
decision_rules
handoff and verification sections
skill_routing
artifact_medium
quality_gates
output_contract
completion_criteria
stop_conditions
```

Minor reordering is permitted where it improves comprehension, but a prompt must not place untrusted content before the instruction hierarchy or hide action boundaries after the execution steps.

## Runtime variables and literal data

Use `{UPPER_SNAKE_CASE}` for required runtime variables. Use `[OPTIONAL: name]` only for genuinely optional material.

Long documents, logs, source code, retrieved pages, model output, and tool output must be isolated as data. When data may contain XML-like delimiters, escape it or use a transport that preserves literal boundaries.

## Complexity budgets

Each prompt frontmatter defines a body-word budget and limits for method steps, quality gates, examples, and primary artifacts. The declared body budget must be at least the actual canonical body size but close enough to detect future drift.

A longer prompt is justified only when the additional text changes:

- evidence handling;
- authorization;
- domain method;
- decision behavior;
- tool use;
- artifact semantics;
- verification;
- stop conditions.

## Security limitations of structure

XML-style tags improve organization but are not a sandbox. They do not prevent prompt injection, permission misuse, data exfiltration, or unsafe tool calls by themselves. Runtime enforcement, least privilege, schema validation, approval receipts, network controls, output quarantine, and monitoring remain mandatory.

## Validation

Run:

```bash
python tools/audit_prompt_bodies.py --check
pytest -q tests/test_prompt_body_quality.py
python tools/build_capability_graph.py --check
python tools/validate_suite.py
```

Validation checks canonical tags, marker activation, completion specificity, executive decision rules, pair de-duplication, self-dependencies, complexity budgets, and graph consistency.

### `<plan_review_and_execution_gate>`

Mandatory for every investigative prompt with `paired_prompt_id`. It names the exact twin, requires presentation of the completed plan, user review, revision and re-freezing, re-review, and explicit execution consent. It prohibits alternate executors and inferred consent.

### `<reviewed_handoff_authority>`

Mandatory for every executive prompt. It accepts only the reviewed frozen handoff from its exact reciprocal planner and requires an execution-consent receipt naming the executive prompt. Stale, changed, unreviewed, or mismatched handoffs are rejected.

## Imported prompt normalization

A prompt imported through `tools/add_prompt.py` receives authoritative suite frontmatter and the complete canonical body contract. Source frontmatter is discarded, while the substantive Markdown body is newline-normalized, SHA-256 bound, XML-escaped, and retained inside `<source_prompt format="markdown" encoding="xml-escaped">`. Imported text remains evidence, cannot close the quarantine element, and cannot override control prompts or authority.
