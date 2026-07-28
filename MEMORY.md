# Repository Memory

This file stores durable, verified repository lessons that prevent repeated investigation and workflow regressions. It is an evidence cache, not an authorization source. Current user instructions, canonical contracts, and freshly verified code override stale memory.

## Memory protocol

- Read this file before changing GitHub Actions, release metadata, manifests, installers, wrappers, generated artifacts, documentation generation, or package publishing.
- Append only durable facts supported by a completed validation run, reproducible failure, fixing commit, or authoritative repository contract.
- Record the symptom, root cause, durable fix, prevention rule, and verification evidence.
- Do not store credentials, secrets, approval receipts, personal paths, transient logs, speculation, or copied command output.
- Correct stale entries explicitly.

## GitHub Actions history through July 28, 2026

Thirty failed runs were recorded in `Validate Mission Directives`. The documentation workflow later failed in run `30372716698` because a release-version replacement corrupted dependency versions in `site/pnpm-lock.yaml`. The first `Publish Mission Directives` run, `30369810482` for `v2.0.0`, failed before publication because it ran tests before generating required body-audit artifacts.

The complete history is maintained in [GitHub Actions Failure History and Pre-Push Guide](docs/GITHUB_ACTIONS_FAILURE_HISTORY_AND_PRE_PUSH_GUIDE.md).

Durable lessons:

- macOS system symlinks, Windows filesystem APIs, text encodings, and path separators require portable handling.
- Textual release and provenance hashes normalize CRLF to LF.
- `MANIFEST.json` uses Git-visible, non-ignored files and excludes `.git`, `.venv`, caches, builds, logs, locks, audits, receipts, and runtime results.
- Source guidance synchronization writes no receipt by default. Use `--receipt` only when evidence is required, and keep `.prompt_suite/agent-guidance-receipt.json` out of release validation.
- Repository reorganizations update every test, wrapper, documentation link, generator, and installed path in the same change.
- Audit artifacts are generated before deterministic tests.
- Validation and publishing workflows use the same audit, canonical test, evaluation, validation, build, and package-smoke prerequisites; release-only raw pytest paths are prohibited.
- Artifact-only GitHub release jobs pass `--repo "${{ github.repository }}"` to `gh release create`; downloaded artifacts do not provide a `.git` checkout for repository discovery.
- PyPI Trusted Publishing must be registered before the first tag with project `mission-directives`, owner `manojpisini`, repository `mission-directives`, workflow `publish.yml`, and environment `pypi`. A valid GitHub OIDC token is insufficient until PyPI has this matching publisher.
- After all applicable source and site generators, rebuild `MANIFEST.json` before deterministic release tests; finish the chain with `build_manifest.py --check`.
- CI and wrappers use the activated virtual environment; setup-uv keeps `activate-environment: 'true'` and does not use `uv pip install --system`.
- Package changes build wheel and sdist, install the built package, and run platform wrappers.
- Site implementation, dependencies, tests, generated paths, ignore rules, and documentation remain one contract.
- Release-version replacements never touch dependency lockfiles. After any release-version change, run a clean `pnpm --dir site install --frozen-lockfile`; an existing `site/node_modules` can hide lockfile corruption from `pnpm run check`.
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

Latest verified validation baseline in this snapshot: run `30373869610` at commit `d60f2a8` passed Ubuntu, Windows, and macOS. Documentation run `30373869619` passed and deployed. Release run `30374282771` built and smoke-tested `2.0.1`, then failed because PyPI lacked the matching Trusted Publisher and the artifact-only GitHub job lacked an explicit repository; the GitHub release was recovered manually from the validated run artifacts.
