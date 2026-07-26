---
title: Troubleshooting
description: Diagnose dependency, routing, identity, installation, validation, and site-build failures.
---

## `jsonschema` is missing

Install the runtime dependency set:

```powershell
python -m pip install -r requirements-runtime.txt
```

Repository contributors should install `requirements-dev.txt`, which includes development and validation dependencies.

## No confident route

Keep the full outcome and add the intended artifact or decision owner. Use `lookup` to inspect candidates. If two candidates are close, use `compare`; do not guess from filenames.

## Wrong shortcut route

Check the parsed invocation context and policy shortcut. Generic shortcuts can declare `match_mode: exact`; specific phrases should have higher priority. Semantic lookup remains the fallback.

## Project install is too large

Inspect `config/runtime_payload.json` and the installation receipt. The installed tree should exclude `tests`, `evaluations`, `prompt_imports`, `.github`, `site`, repository validators, and development requirements.

## Existing `prompts` directory

The installer fails closed. Review the destination, then rerun with `--replace` only when replacement is intended. The prior directory is backed up and restored on downstream failure.

## Identity mismatch

Run `python tools/md.py explain <ID>` and inspect `compatibility/capability_identity_registry.json`. CP provenance IDs are not executable MD identities.

## Site build fails

```powershell
cd site
npm ci
npm run generate
npm run build
```

Generated reference pages live under `site/src/content/docs/reference/` and must not be edited or committed. Fix the canonical source or the generator.

## Manifest mismatch

After tracked changes:

```powershell
python tools/build_manifest.py
python tools/build_manifest.py --check
```

Generated receipts, test outputs, runtime logs, dependency trees, and built site output remain outside the sealed manifest.
