# Runtime Marker Protocol

## Purpose

Runtime markers give human-readable artifacts stable machine identifiers. They connect evidence, uncertainty, findings, actions, verification, and stops across prompts, tools, models, files, and handoffs.

Markers are not decorative prefixes. They represent typed records and must remain stable through the run lifecycle.

## Marker definitions

### `@EVIDENCE:{id}`

Represents a source or reproducible observation.

Required context:

- origin;
- location or revision;
- collection time when freshness matters;
- trust state;
- scope;
- redaction status;
- hash or citation where available.

Example:

```text
@EVIDENCE:test-17 pytest tests/test_sessions.py::test_refresh_replay — failed at commit 7ab21e
```

### `?UNKNOWN:{id}`

Represents unresolved information that could change a conclusion, action, risk, or acceptance result.

Example:

```text
?UNKNOWN:owner-03 No owner is recorded for the production rollback runbook.
```

An unknown must not be silently converted to an assumption. Resolve it with new evidence, defer it with ownership, or stop.

### `#FINDING:{id}`

Represents an evidence-backed issue, opportunity, contradiction, or conclusion.

Example:

```text
#FINDING:auth-08 Refresh tokens remain valid after password reset.
Evidence: @EVIDENCE:auth-08a, @EVIDENCE:auth-08b
Confidence: high
```

### `+ACTION:{id}`

Represents bounded work. Its lifecycle may be proposed, approved, executing, executed, skipped, deferred, failed, or rolled back.

Required fields:

- target;
- expected effect;
- mode;
- authority;
- dependencies;
- risk;
- rollback;
- verification IDs;
- current status.

### `=VERIFY:{id}`

Represents an acceptance criterion and result. Execution alone is not verification.

Example:

```text
=VERIFY:auth-08
Criterion: refresh token is invalid after password reset
Method: automated regression test and API replay attempt
Result: pass
Evidence: @EVIDENCE:auth-08c
```

### `!STOP:{reason}`

Represents a hard halt. The reason is a stable machine-readable slug where possible.

Examples:

```text
!STOP:approval-does-not-cover-production
!STOP:evidence-snapshot-stale
!STOP:rollback-unavailable
!STOP:untrusted-skill-requires-network
```

## Lifecycle relationships

```text
@EVIDENCE:e1
   ↓ supports
#FINDING:f1
   ↓ motivates
+ACTION:a1
   ↓ evaluated by
=VERIFY:v1
```

`?UNKNOWN:u1` may block any transition. `!STOP:reason` halts the affected path.

## Pair handoff behavior

The investigator creates evidence, findings, proposed actions, and acceptance criteria. The executive preserves those IDs.

The executive may add a new `#FINDING:{id}`, but it may not convert that finding into an action inside the same approved batch unless the runtime obtains new approval.

## Marker use by role

| Role | Primary markers |
|---|---|
| Control | `?UNKNOWN`, `!STOP`, `=VERIFY` |
| Investigative | `@EVIDENCE`, `?UNKNOWN`, `#FINDING`, `+ACTION`, `=VERIFY` |
| Executive | preserved `+ACTION`, `=VERIFY`, new `#FINDING`, `!STOP` |
| Operational | all markers as required by the workflow |
| Gate | `@EVIDENCE`, `#FINDING`, `=VERIFY`, `!STOP` |

Every prompt still declares the complete vocabulary to preserve composability.

## ID rules

- IDs are unique within a run.
- IDs are never recycled for a different record.
- Handoffs preserve IDs.
- Derivatives reference parent IDs.
- Corrections append history rather than rewriting prior evidence.
- Redacted public artifacts may map internal IDs to safe public identifiers.

## Parsing guidance

The marker identifies a record; the surrounding artifact or JSON schema supplies fields. Do not infer full structured data from the marker string alone.

Recommended JSON representation:

```json
{
  "record_id": "#FINDING:auth-08",
  "type": "finding",
  "summary": "Refresh tokens remain valid after password reset",
  "evidence_ids": ["@EVIDENCE:auth-08a"],
  "confidence": "high",
  "status": "open"
}
```

## Anti-patterns

- using markers only in the control contract but not capability prompts;
- changing IDs during handoff;
- marking a proposed action as verified;
- using `@EVIDENCE` for unsupported model output;
- hiding uncertainty in prose rather than `?UNKNOWN`;
- continuing after `!STOP` without a new authorized run state;
- inventing evidence IDs without source records.

## Validation

Every prompt body must contain a `<runtime_markers>` block naming all six markers. `audit_prompt_bodies.py` verifies coverage.
