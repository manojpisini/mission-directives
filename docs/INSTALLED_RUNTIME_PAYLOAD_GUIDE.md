# Installed Runtime Payload Guide

## Purpose

This guide defines the boundary between a working-project installation and the Mission Directives source repository. `config/runtime_payload.json` is the machine-readable source of truth.

## Runtime profile

The `runtime` profile contains everything required to:

- route natural-language intent and exact IDs;
- inspect prompts, scenarios, packs, schemas, policies, and identity maps;
- compile plans and execution graphs;
- resolve templates and registered skills;
- synchronize root agent guidance;
- write local telemetry and receipts;
- run the managed cleanup workflow.

The profile includes canonical catalogs, prompt bodies, runtime configuration, compatibility data, policies, schemas, templates, examples, integrations, selected Python tools, and `requirements-runtime.txt`.

## Repository-only profile

The source repository retains assets needed to author, evaluate, test, validate, package, and publish the suite:

- `.github/`;
- `tests/`;
- `evaluations/`;
- `site/`;
- prompt import and addition tools;
- audit, test, validation, and manifest builders;
- `requirements-dev.txt`.

These assets certify or develop the product. They are not dependencies of normal prompt execution in a target project.

## Installation transaction

`tools/install.py`:

1. validates the target and rejects overlap with the suite source;
2. loads and validates the runtime payload contract;
3. rejects duplicate, escaped, missing, linked, or special-file payload entries;
4. stages only declared files and directories;
5. verifies the staged tree;
6. backs up an existing installation when replacement is explicit;
7. atomically promotes the staged runtime;
8. updates managed `.gitignore` and agent-guidance blocks;
9. creates runtime directories and ownership markers;
10. writes schema-valid installation and guidance receipts;
11. restores the previous state if a post-promotion step fails.

## Audit fields

A successful installation receipt records:

- `payload_profile: runtime`;
- `installed_file_count`;
- suite version and destination;
- backup location when applicable;
- created runtime directories;
- preexisting project files;
- guidance synchronization result;
- UTC installation time.

A dry run reports the repository-only exclusions so operators can review the boundary before mutation.

## Verification

```bash
python tools/install.py /path/to/project --dry-run
python tools/install.py /path/to/project
python /path/to/project/prompts/tools/md.py route "MD cleanup dead code safely"
```

Confirm that the project installation does not contain tests, evaluations, prompt imports, CI workflows, site sources, repository validators, or development requirements.

## Changing the payload

Treat a payload change as a runtime compatibility change:

1. prove the file is required by a runtime code path;
2. add or remove it in `config/runtime_payload.json`;
3. update installer regressions;
4. perform a real temporary install;
5. smoke-test routing from the installed path;
6. validate receipts and rollback;
7. update this guide and the manifest.

Do not copy the repository and rely on ignore filters. An allowlisted payload is reviewable, fails closed, and does not silently grow when a new source-only directory appears.
