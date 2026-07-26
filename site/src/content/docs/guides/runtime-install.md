---
title: Install Runtime
description: The project installation boundary, payload contract, receipts, replacement, rollback, and source-only tooling.
---

Project installation is a deployment operation. The checked-in contract at `config/runtime_payload.json` is the source of truth.

## What is installed

The runtime payload contains:

- prompt and scenario catalogs;
- canonical prompt bodies;
- router concepts and policies;
- schemas used by runtime planning and receipts;
- templates, integrations, compatibility maps, and examples;
- runtime tools required to route, explain, plan, synchronize guidance, invoke skills, log, and clean up;
- `requirements-runtime.txt`.

The installer validates declared paths, rejects source symlinks and path escapes, stages the payload, verifies it, then atomically promotes it to `<project>/prompts`.

## What stays upstream

Repository-only material includes tests, evaluations, prompt-import sources, development validators, build and release tooling, CI configuration, and the Astro site source.

| Runtime project | Source repository |
| --- | --- |
| route, explain, plan, execute | author and import prompts |
| validate runtime schemas | evaluate prompt behavior |
| synchronize agent guidance | run repository CI |
| resolve templates and skills | build manifests and releases |
| write local receipts | build the documentation site |

## Receipts and rollback

A successful receipt records `payload_profile: runtime` and `installed_file_count`. Replacement requires `--replace`; the previous installation is backed up first. If guidance synchronization or receipt creation fails, the prior suite and human-authored project files are restored.

## Commands

```powershell
python tools/install.py D:\path\to\project --dry-run
python tools/install.py D:\path\to\project
python tools/install.py D:\path\to\project --replace
```

For a project install:

```powershell
python -m pip install -r D:\path\to\project\prompts\requirements-runtime.txt
python D:\path\to\project\prompts\tools\md.py route "MD plan a release"
```
