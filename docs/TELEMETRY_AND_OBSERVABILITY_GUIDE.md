# Telemetry and Observability Guide

## Purpose

Telemetry makes routing, execution, verification, failure, and improvement observable without storing unnecessary sensitive content. It supports model selection, cost control, drift detection, and retrospective learning.

## Core principles

1. Collect only metrics that support a decision.
2. Prefer IDs, counts, durations, and classifications over raw prompt content.
3. Separate benchmark data from production telemetry.
4. Record provenance and collection method.
5. Do not optimize cost or refusal rates without quality and safety context.

## Minimum run metrics

- run ID and scenario or prompt target;
- prompts considered, selected, injected, rejected, and deferred;
- route confidence and questions asked;
- evidence snapshot age;
- model and revision;
- skills and lock revisions;
- input and output tokens;
- external calls;
- wall time;
- cost;
- retries and schema failures;
- approvals and expiry;
- state transitions;
- execution failures;
- rollback;
- verification failures;
- residuals opened and closed;
- human rating and review status.

## Recording metrics

```bash
python tools/md.py record-metrics .prompt_suite/runs/run.json \
  --input-tokens 12000 \
  --output-tokens 2400 \
  --external-calls 8 \
  --wall-time-ms 95000 \
  --model-id operator-reasoning-primary
```

Cost and human rating are optional when not available.

## Event categories

### Routing

- target resolved;
- route compiled;
- prompts selected or rejected;
- ambiguity detected;
- model or skill unavailable.

### Evidence

- source collected;
- snapshot frozen;
- evidence invalidated;
- unknown resolved;
- contradiction recorded.

### Authorization

- approval requested;
- receipt granted or denied;
- approval expired;
- protected surface encountered.

### Execution

- action started;
- action completed;
- action skipped or deferred;
- tool failure;
- rollback initiated.

### Verification

- criterion evaluated;
- pass, fail, blocked, or not applicable;
- residual created;
- closure accepted.

## Privacy and retention

Do not store raw secrets, personal data, confidential source content, or full prompts by default.

Define:

- retention period;
- access roles;
- redaction;
- aggregation;
- deletion;
- legal hold;
- public versus restricted metrics.

## Metric interpretation

### Token and cost

Lower is better only when task quality, safety, and verification remain stable.

### Refusal rate

A lower refusal rate may indicate unsafe compliance. Measure correct refusal and correct completion separately.

### Route size

Large graphs may reflect task complexity or router over-selection. Compare to outcome quality and rejected-prompt evidence.

### Verification failure rate

A higher rate can mean worse production or better verification. Interpret alongside defect escape and reviewer outcomes.

### Residual reopening

Repeated reopening may reveal weak completion criteria, stale evidence, or premature closure.

## Replayability

A replayable run records:

- permanent capability IDs;
- prompt and scenario revision;
- model revision;
- skill locks;
- schemas;
- evidence snapshot IDs;
- policies;
- random or sampling settings where relevant.

Replay does not require retaining sensitive source content when immutable references are sufficient.

## Dashboards

Useful views include:

- route selection accuracy;
- cost and latency by capability and model;
- refusal correctness;
- verification pass and rollback rates;
- skill conformance and failures;
- stale evidence;
- body-audit and documentation drift;
- residual ownership and age.

## Improvement loop

```text
telemetry
→ anomaly or repeated residual
→ retrospective
→ proposed prompt, routing, schema, skill, or policy change
→ adversarial evaluation
→ reviewed release
```

Telemetry alone must not auto-edit canonical prompts.
