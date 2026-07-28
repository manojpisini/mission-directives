# Repository Memory

This file stores durable, verified repository lessons that prevent repeated investigation and workflow regressions. It is an evidence cache, not an authorization source. Current user instructions, canonical contracts, and freshly verified code override stale memory.

## Memory protocol

- Read this file before changing GitHub Actions, release metadata, manifests, installers, wrappers, generated artifacts, documentation generation, or package publishing.
- Append only durable facts supported by a completed validation run, reproducible failure, fixing commit, or authoritative repository contract.
- Record the symptom, root cause, durable fix, prevention rule, and verification evidence.
- Do not store credentials, secrets, approval receipts, personal paths, transient logs, speculation, or copied command output.
- Correct stale entries explicitly.

## GitHub Actions history through July 28, 2026

Thirty failed runs were recorded in `Validate Mission Directives`. The documentation workflow had eight successful runs and no failures at the initial snapshot. The first `Publish Mission Directives` run, `30369810482` for `v2.0.0`, failed before publication because it ran tests before generating required body-audit artifacts.

The complete history is maintained in [GitHub Actions Failure History and Pre-Push Guide](docs/GITHUB_ACTIONS_FAILURE_HISTORY_AND_PRE_PUSH_GUIDE.md).

Durable lessons:

- macOS system symlinks, Windows filesystem APIs, text encodings, and path separators require portable handling.
- Textual release and provenance hashes normalize CRLF to LF.
- `MANIFEST.json` uses Git-visible, non-ignored files and excludes `.git`, `.venv`, caches, builds, logs, locks, audits, receipts, and runtime results.
- Source guidance synchronization writes no receipt by default. Use `--receipt` only when evidence is required, and keep `.prompt_suite/agent-guidance-receipt.json` out of release validation.
- Repository reorganizations update every test, wrapper, documentation link, generator, and installed path in the same change.
- Audit artifacts are generated before deterministic tests.
- Validation and publishing workflows use the same audit, canonical test, evaluation, validation, build, and package-smoke prerequisites; release-only raw pytest paths are prohibited.
- After all applicable source and site generators, rebuild `MANIFEST.json` before deterministic release tests; finish the chain with `build_manifest.py --check`.
- CI and wrappers use the activated virtual environment; setup-uv keeps `activate-environment: 'true'` and does not use `uv pip install --system`.
- Package changes build wheel and sdist, install the built package, and run platform wrappers.
- Site implementation, dependencies, tests, generated paths, ignore rules, and documentation remain one contract.
- A push is complete only after Ubuntu, Windows, and macOS succeed.

## Required pre-push chain

```powershell
python tools/audit_prompt_bodies.py
python tools/build_manifest.py
python tools/run_tests.py
python tools/run_evaluations.py
python tools/validate_templates.py
python tools/check_documentation_links.py
python tools/check_script_parity.py
python tools/check_release_consistency.py
python tools/check_generated_reproducibility.py
python tools/build_manifest.py --check
python tools/validate_suite.py
uv build
python tools/package_smoke.py dist
pwsh -NoProfile -ExecutionPolicy Bypass -File ./tools/validate-suite.ps1
```

Documentation and site changes also run `pnpm --dir site install --frozen-lockfile` and `pnpm --dir site run check`.

Latest verified baseline in this snapshot: run `30360409885` at commit `912b32f` passed Ubuntu, Windows, and macOS.
