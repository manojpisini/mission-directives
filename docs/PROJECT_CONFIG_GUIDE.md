# Project Config Guide

## Contract

`.mission-directives/project.json` is durable, agent-facing project knowledge. `.mission-directives/config.json` is system-owned installation and viewer configuration. Project Config is a cache, not an authority source: it cannot grant mutation, deployment, publication, credentials, approval, or external action.

The schema is `schemas/project_context.schema.json`. Unknown top-level fields and secret-like keys are rejected. Environment-variable names may be recorded; secret values may not.

## Sections

- `project`: identity, mission, lifecycle, status, audiences, and owners.
- `goals`: outcomes, success criteria, and non-goals.
- `scope`: included areas, exclusions, and protected paths.
- `stack`: languages, frameworks, package managers, services, databases, and deployment targets.
- `paths` and `commands`: operational locations and verified commands.
- `constraints`: security, privacy, legal, compatibility, performance, and budget boundaries.
- `working_agreements`: coding, testing, documentation, and commit conventions.
- `current_state`: active focus, known issues, decisions, and open questions.
- `provenance`: update and verification metadata.
- `extensions`: namespaced project-specific additions.

## Agent lookup order

1. Read the current user request and current-run authorization.
2. Read relevant fresh fields from `project.json`.
3. Inspect targeted repository evidence when fields are missing, stale, contradicted, or high-risk.
4. Mark unresolved values unknown instead of guessing.

Current user instructions and freshly verified repository evidence override cached values. Agents may update freshly verified operational facts changed by their authorized task. Mission, scope, protected paths, owners, non-goals, and constraints require explicit user modification.

## Commands

```bash
mission-directives config show
mission-directives config show --json
mission-directives config validate
mission-directives config refresh --dry-run
mission-directives config refresh --apply
mission-directives config open
```

Refresh scans only standard manifests and returns a proposed diff. The Settings page validates on the server, checks the loaded revision, writes atomically, and retains bounded backups under `.mission-directives/state/config-backups`.
