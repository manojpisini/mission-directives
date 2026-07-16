# Model Routing Guide

## Purpose

Model routing selects a model only when measured evidence supports the requested prompt, evidence lane, output contract, tools, and assurance profile.

The router is allowed to return **no selection**. That is safer than inventing confidence from model names or provider claims.

## Profile status

`model_profiles.json` distinguishes:

- declared but unmeasured profiles;
- measured profiles;
- production-eligible profiles;
- synthetic test profiles;
- revoked or restricted profiles.

Unmeasured profiles cannot be automatically selected for production work.

## Required measurement dimensions

Depending on the task:

- structured-output reliability;
- instruction and schema adherence;
- correct refusal and escalation;
- fabrication rate;
- evidence and citation integrity;
- tool-boundary adherence;
- code or artifact correctness;
- visual or multimodal capability;
- long-context reliability;
- latency;
- tokens;
- cost;
- known failure modes;
- context and output limits.

## Benchmark design

Choose fixtures across risk and role:

- low-risk creative or transformation;
- medium factual research;
- high-risk code or privacy;
- critical security or production action;
- control and structured-output cases;
- adversarial untrusted-input cases.

Keep constant:

- prompt revision;
- fixture revision;
- model settings;
- tools;
- evidence;
- schema;
- retry policy.

Record any difference.

## Running selection

```bash
python tools/md.py select-model MD-29 --assurance HIGH_ASSURANCE
```

The result includes ranked eligible profiles and reasons, or:

```json
{
  "status": "no_selection"
}
```

Manual override must be recorded in the run manifest with its rationale and limitations.

## Benchmark result record

```json
{
  "model_id": "provider/model-revision",
  "fixture_id": "MD-29-adversarial-01",
  "prompt_revision": "hash",
  "schema_conformance": true,
  "refusal_correct": true,
  "fabricated_evidence": false,
  "input_tokens": 8200,
  "output_tokens": 1900,
  "latency_ms": 34000,
  "cost": 0.42,
  "review": {
    "score": 0.91,
    "reviewer": "human-or-deterministic-rubric"
  }
}
```

Preserve raw output separately.

## Assurance-aware routing

### FAST

May prioritize latency and cost among profiles that meet the minimum task contract.

### STANDARD

Requires measured schema, grounding, and task-quality evidence.

### HIGH_ASSURANCE

Requires relevant high-risk and adversarial fixtures, correct refusal, evidence integrity, tool-boundary adherence, and recent measurements.

A fallback must not silently lower assurance.

## Model specialization

Model selection may vary by phase:

- retrieval or classification;
- deep analysis;
- code generation;
- structured artifact production;
- visual review;
- independent verification.

Multiple models are justified only when the handoff is typed and the quality gain outweighs cost and complexity.

## Production eligibility

Eligibility requires review of:

- risk-tier coverage;
- failure modes;
- provider or model revision;
- measurement recency;
- operating environment;
- data policy;
- tool support;
- fallback;
- monitoring and revocation thresholds.

A measured profile is not automatically approved for every department.

## Calibration and drift

Compare expected confidence to actual correctness. Track:

- schema failure;
- refusal error;
- fabrication;
- citation error;
- tool misuse;
- cost and latency drift;
- fixture regression;
- production verification failures.

Revoke eligibility when performance falls below thresholds or model revision changes materially.

## Privacy

Benchmark artifacts may contain sensitive data. Prefer synthetic or redacted fixtures. Store provider, retention, and data-use settings with the result.

## Limitations

The delivered suite does not claim production model performance until real benchmark output is ingested. The synthetic profile tests routing mechanics only.
