# Mission Directives Governance

**Applies to:** the active release declared by `VERSION`  
**Canonical release identifier:** `RELEASE_ID`

## Purpose

Governance protects the suite's permanent identities, execution boundaries, evidence standards, generated artifacts, templates, skills, telemetry, installers, and compatibility promises. It defines who may decide, what evidence is required, and when a change must stop rather than silently degrading a contract.

## Authority model

| Role | Authority | May not do |
|---|---|---|
| Repository maintainer | Approve releases, assign owners, accept compatibility migrations, revoke unsafe routes | Waive security, manifest, or exact-twin failures without recording a residual and blocking automatic release |
| Prompt owner | Refine one capability's body, fixtures, templates, and documentation | Change a permanent prompt ID or another capability's authority without governance review |
| Pair owner | Maintain reciprocal planner/executor contracts and handoff schemas | Substitute an executor or collapse review and execution consent |
| Template owner | Maintain one artifact contract and its conformance fixtures | Make a conditional template silently mandatory for unrelated outputs |
| Tool owner | Maintain one executable entry point and paired shell wrappers | Diverge Bash and PowerShell semantics or bypass telemetry and exit-code propagation |
| Reviewer | Block changes on evidence, safety, compatibility, or quality grounds | Approve their own consequential change without independent review where policy requires separation |
| Release operator | Run the release checklist, seal the manifest, build and verify the archive | Edit canonical source while presenting generated verification as current |

## Canonical versus generated artifacts

Canonical sources include prompt bodies, scenario definitions, policies, schemas, templates, compatibility records, tool source, and evaluation definitions. Generated views include catalogs, capability graphs, body-audit reports, test receipts, validation reports, and the integrity manifest.

Rules:

1. Generated files are never edited by hand.
2. Their generator must be deterministic for identical canonical inputs.
3. Validation must regenerate them and compare byte-for-byte with committed output.
4. `VERSION` is the sole active-version source; other current-version fields are derived.
5. Historical versions may appear only in explicit migration, compatibility, changelog, or archived evidence records.
6. Build-machine paths, usernames, caches, runtime logs, and local receipts are not distributable canonical data.

## Change classes

### Class A — editorial refinement

Clarifies wording without changing routing, authority, inputs, outputs, schemas, or completion criteria. Requires focused tests and documentation-link validation.

### Class B — contract refinement

Changes prompt method, template obligations, policy interpretation, schema fields, tool behavior, or verification semantics while preserving permanent identity. Requires healthy, problematic, adversarial, and mutation coverage where applicable.

### Class C — compatibility change

Changes a public command, path, field, route, alias, state, or generated format. Requires a compatibility record, migration behavior, rollback path, and tests against the previous supported form.

### Class D — consequential boundary change

Changes external actions, permissions, installation, skill acquisition, security posture, telemetry handling, exact-twin dispatch, or destructive behavior. Requires security review, explicit approval gates, and clean-environment verification.

## Permanent identity rules

- Prompt, scenario, capability, template, skill, schema, and policy IDs remain stable once published.
- Renames require an alias or migration record when a supported consumer could still reference the prior identity.
- A planning prompt has exactly one declared reciprocal execution twin.
- Requested plan changes invalidate previous plan approval and execution consent.
- Related prompts and keyword matches never override exact pair metadata.

## Decision procedure

1. Identify the canonical files and owners.
2. Classify the change.
3. State observable outcomes and prohibited regressions.
4. Add a failing test or fixture for behavioral changes.
5. Implement the smallest coherent change.
6. Regenerate all affected views.
7. Run focused, deterministic, cross-platform, schema, documentation, and manifest checks.
8. Record unresolved external measurements as limitations rather than inferred proof.
9. Obtain the required independent review.
10. Seal and verify a fresh archive extraction.

## Release gate

A release is blocked unless all applicable checks pass:

- active version and release ID consistency;
- no stale current-version metadata outside historical records;
- no personal absolute paths in distributable content;
- prompt-body audit and exact-twin reciprocity;
- scenario, template, skill, policy, and schema validation;
- positive and adversarial evaluation coverage;
- documentation links and manual consistency;
- Bash/PowerShell semantic parity and supported OS CI;
- installer preservation, idempotency, staging, backup, and rollback tests;
- telemetry validity, correlation, redaction, locking, and log exclusion;
- deterministic generated-artifact reproduction;
- clean manifest construction and verification;
- ZIP integrity and fresh-extraction validation.

Passing structural checks does not prove live-model quality, third-party skill safety, or untested platform behavior. Such claims remain pending until measured.

## Deprecation and compatibility

A deprecation record must name the old identity, replacement, first deprecated version, support window, migration procedure, affected consumers, and removal evidence. Removal requires proof that no supported scenario, prompt, template, tool, integration, documentation link, fixture, or compatibility record still consumes the identity.

## Exception handling

Exceptions are narrow, time-bounded, owned, and machine-readable where possible. An exception must identify the failed gate, reason, affected scope, compensating controls, expiration, reviewer, and rollback. Security, data loss, secret exposure, wrong-executor dispatch, manifest corruption, installer overwrite risk, and silent template substitution are not waivable release defects.

## Escalation

- **Immediate stop:** data loss, credential exposure, unauthorized external action, corrupted release artifact, or non-reciprocal executor dispatch.
- **Release blocker:** cross-platform divergence, invalid schema output, missing required template content, stale generated files, or installer preservation failure.
- **Review required:** ambiguous compatibility impact, new permissions, telemetry-field expansion, or unresolved provenance.
- **Documented residual:** unavailable live environment or external benchmark that does not invalidate deterministic claims.

## Records and auditability

Decisions should reference evidence IDs, changed paths, tests, review receipts, execution consent where relevant, generated-file comparison, manifest hash, archive checksum, and residual limitations. Daily TOML telemetry supports runtime investigation but does not replace release evidence or human review.
