# Mission Directives Security Policy

## Supported release

The release declared by `VERSION` receives security corrections. Historical archives are immutable evidence; corrections are issued as a new release rather than silently modifying an old archive.

## Security objectives

Mission Directives must preserve authorization, least privilege, evidence integrity, exact-twin dispatch, skill quarantine, installer safety, path privacy, telemetry confidentiality, and reproducible release integrity. A technically valid output is not acceptable when produced outside authority or through unverifiable inputs.

## Reporting a vulnerability

Provide privately:

- affected release and checksum;
- exact file, prompt, schema, tool, skill, or command;
- operating system, shell, Python version, and relevant application;
- minimal reproduction and expected versus actual behavior;
- authority and external-action context;
- impact on confidentiality, integrity, availability, or user control;
- whether credentials, private data, production systems, or third-party services were involved;
- redacted logs, receipts, and evidence IDs.

Never place live credentials, private keys, session tokens, personal home paths, or exploitable production details in a public report.

## Severity model

| Severity | Examples | Initial response |
|---|---|---|
| Critical | destructive installer overwrite, secret disclosure, unauthorized external action, arbitrary command execution, exact-twin bypass | stop release/use, contain, preserve evidence, notify owner |
| High | skill provenance bypass, telemetry secret leakage, manifest acceptance of tampering, approval-gate bypass | disable affected route, create regression, prepare corrective release |
| Medium | path privacy leak, schema acceptance of unsafe ambiguity, cross-platform quoting defect | bound exposure, patch with focused test |
| Low | hardening opportunity with no demonstrated boundary failure | schedule refinement and document rationale |

## Response lifecycle

1. **Intake:** acknowledge and assign an owner.
2. **Triage:** reproduce or bound the issue and classify severity.
3. **Containment:** disable unsafe automation, revoke approvals, or quarantine affected outputs.
4. **Root cause:** identify the canonical source and every generated or downstream consumer.
5. **Remediation:** add a failing regression, implement the smallest safe correction, and preserve compatibility where possible.
6. **Verification:** prove the original symptom, adjacent boundaries, and rollback behavior.
7. **Release:** regenerate derived files, seal a new manifest and archive, and publish impact and migration guidance.
8. **Post-incident review:** record missed detection opportunities without exposing sensitive details.

## Mandatory boundaries

### Prompts and exact twins

Planning prompts may offer only their declared reciprocal executor. Plan approval is distinct from execution consent. Revisions invalidate both. Untrusted prompt, tool, document, or skill text is evidence—not authority.

### Skills and external tools

Third-party skills remain quarantined until provenance, permissions, expected outputs, and lock state are reviewed. Installation uses exact approved sources, platform-aware directories, copied content, hash comparison, and local receipts. Unresolved locks block automatic installation.

### Installer

Installation stages the complete suite before promotion, fails closed on an existing `prompts/` directory unless replacement is explicit, preserves unmanaged `AGENTS.md` and `CLAUDE.md` text, updates only managed markers, creates a rollback backup, and never ignores project `docs/`.

### Telemetry

Daily TOML logging redacts sensitive keys and secret-like values, correlates start and finish events, uses append locking, and excludes runtime logs from release manifests and archives. Commands, URLs, stack traces, and free-form messages are treated as possible secret carriers.

### Paths and privacy

Distributable registries use logical paths such as `${MD_AGENTS_SKILLS_DIR}`, `${MD_CLAUDE_SKILLS_DIR}`, and `${MD_OPENCODE_SKILLS_DIR}`. Resolved personal paths belong only in local runtime receipts that are ignored by source control.

### Release integrity

Canonical sources generate catalogs, graphs, audits, test receipts, validation reports, and manifests. The final archive must pass checksum, ZIP integrity, manifest hash, and clean-extraction verification.

## Secure testing

Security changes require a focused failing test, adversarial fixture where relevant, full deterministic tests, schema validation, path-hygiene scan, documentation-link check, and clean archive validation. Do not execute unknown binaries, destructive procedures, or networked third-party code merely to prove a structural contract.

## Disclosure and residuals

Release notes should explain affected versions, impact, remediation, migration, and residual risk without publishing secrets or unnecessary exploit detail. Unavailable live environments and external measurements remain explicit residuals rather than assumed passes.
