# Mission Directives Support Guide

## Scope

Support covers installation, prompt routing, exact pairs, templates, schemas, skills, telemetry, cross-platform wrappers, generated artifacts, documentation, evaluation, validation, and release integrity for the active version.

## Severity and response target

| Severity | Definition | Examples | Handling |
|---|---|---|---|
| S1 | Safety, privacy, data, or authority emergency | installer data loss, secret exposure, unauthorized action, wrong executor | stop affected operation, preserve evidence, escalate immediately |
| S2 | Core suite unusable or release invalid | routing failure, invalid schema output, manifest mismatch, platform wrapper failure | reproduce, assign owner, block release |
| S3 | Material degradation with workaround | incomplete template selection, misleading manual, non-blocking telemetry issue | document workaround, schedule focused repair |
| S4 | Clarification or minor refinement | wording, navigation, optional usability concern | answer or queue with rationale |

## Before opening a request

Run the narrowest relevant command and capture its exit code. For installation issues, use `--dry-run`. For routing, run `python tools/md.py lookup` and `explain`. For release issues, run deterministic tests and `validate_suite.py` before rebuilding the manifest.

## Required evidence

Include:

- `VERSION` and archive checksum;
- operating system, architecture, Python version, Bash or PowerShell version, and agentic application;
- exact command and working directory;
- expected behavior and actual behavior;
- focused stdout, stderr, TOML span, or receipt;
- affected prompt, scenario, template, schema, skill, or tool ID;
- reproduction frequency and smallest known reproduction;
- whether the project path contains spaces, Unicode, symlinks, or a separate filesystem;
- rollback or workaround already attempted;
- explicit redaction of credentials and personal paths.

## Request categories

### Installation and update

State whether `prompts/` already existed, whether `--replace` was used, the backup path, `.gitignore` managed block, and whether unmanaged agent-file content was preserved.

### Prompt routing

Provide the query, lookup results, selected route, and why the selected observable outcome is incorrect or incomplete.

### Exact pair workflow

Provide planner and executor IDs, handoff hash, review state, revision number, and consent state. Never share sensitive handoff contents when metadata is sufficient.

### Template or documentation

Provide the prompt ID, required and conditional template routes, requested artifact type, missing or irrelevant sections, and conformance result.

### Skill or path resolution

Provide the application (`.agents`, Claude Code, or OpenCode), operating system, logical path, environment override presence, lock status, and hash-verification result.

### Telemetry

Provide the daily filename, event and span IDs, category, action, status, and a redacted excerpt. Do not attach unredacted logs.

## Resolution standard

A request closes only when the symptom is reproduced or explicitly bounded, canonical cause is identified, a focused regression exists for behavioral defects, the correction passes adjacent contracts, relevant manuals are updated, and residual limitations are recorded. “Cannot reproduce” requires the attempted environments and evidence, not a silent closure.

## Escalation

Escalate immediately for S1 issues. Escalate S2 issues when they affect multiple platforms, corrupt generated artifacts, invalidate manifests, or prevent safe rollback. Security reports follow `SECURITY.md`; governance disputes follow `GOVERNANCE.md`.
