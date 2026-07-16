# Tool Policy and Authorization Guide

## Purpose

Authorization and tool selection are related but different:

- `<authorization_boundary>` defines what effects are permitted.
- `<tool_policy>` defines how tools and skills may be used within that authority.

A tool capable of deployment does not grant deployment authority. A user request to “fix it” does not authorize production changes. A prompt that can browse does not automatically have permission to contact third parties or collect sensitive data.

## Authorization hierarchy

The effective authority is the narrowest intersection of:

1. signed runtime context;
2. operating mode;
3. role authority policy;
4. domain policy;
5. prompt authorization boundary;
6. approved action receipt;
7. tool permission and environment controls.

No lower-level prompt or skill may broaden a higher-level restriction.

## Canonical authorization tag

Use only `<authorization_boundary>`. Equivalent concepts must not use alternate names.

A complete boundary states:

- allowed reads;
- allowed writes;
- external actions;
- protected targets;
- required approvals;
- reversibility expectations;
- conditions requiring `!STOP:{reason}`.

## Tool policy by role

### Control

Allowed:

- local parsing;
- validation;
- writing declared control artifacts.

Prohibited:

- network access unless explicitly required for context resolution;
- mutation of the governed subject;
- publication, deployment, installation, or sending.

### Investigative

Allowed:

- read-only search and retrieval;
- repository inspection;
- safe analysis and diagnostics;
- non-mutating tests where authorized.

Prohibited:

- writes to the governed subject;
- deployment;
- credential changes;
- publication;
- unapproved scanning or third-party contact.

### Executive

Allowed only when the tool call is bound to an approved `+ACTION:{id}`. Each call must identify:

- target;
- intended effect;
- mode;
- approval receipt;
- rollback or recovery;
- expected verification.

### Operational

`DRAFT_ONLY` remains local and unapproved. `APPLY_SAFE` is reversible and local. `APPLY_APPROVED` is required for consequential or external effects.

### Gate

Use independent read-only validators. A gate may not use producer tools to alter the reviewed subject.

## Skill output quarantine

A skill's output is untrusted until:

1. the skill source and revision are locked;
2. permissions match the prompt tool policy;
3. output shape matches the adapter contract;
4. content passes domain verification;
5. external effects are independently confirmed;
6. provenance is recorded.

Unresolved skill locks block automatic selection.

## Network and external actions

The following require explicit authority and normally `APPLY_APPROVED`:

- publishing or posting;
- sending email or messages;
- uploading files;
- deployment;
- package or skill installation;
- production configuration changes;
- credential rotation or revocation;
- external scanning;
- contacting research subjects, vendors, applicants, or partners;
- financial or legal commitments.

## Tool records

Recommended action record:

```json
{
  "action_id": "+ACTION:fix-17",
  "tool": "repository_patch",
  "target": "src/auth/session.py",
  "mode": "APPLY_SAFE",
  "authority": "approval-receipt-42",
  "expected_effect": "reject replayed refresh token",
  "rollback": "restore commit parent",
  "verification_ids": ["=VERIFY:auth-17"]
}
```

## Failure behavior

Emit `!STOP:{reason}` when:

- a tool requires undeclared privileges;
- target scope is ambiguous;
- the approval does not cover the exact action;
- the tool cannot dry-run or rollback a high-risk change;
- output provenance is unavailable;
- a skill attempts an external effect not declared by its adapter;
- the environment differs materially from the approved target.

## Review questions

- Is the tool necessary?
- Is a read-only alternative available?
- Is the target exact?
- Does the mode allow the effect?
- Is the action reversible?
- Is output quarantined?
- Is verification independent?
- Would a failed tool call expose secrets or create partial state?

## Validation

The body validator requires canonical authorization and tool-policy tags in all 199 prompts and rejects the legacy `<security_execution_boundary>` name.
