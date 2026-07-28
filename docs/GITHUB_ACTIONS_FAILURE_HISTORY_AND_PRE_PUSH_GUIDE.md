# GitHub Actions Failure History and Pre-Push Guide

## Purpose

This guide records every failed GitHub Actions validation run through July 28, 2026, its root cause, durable correction, and prevention rule. GitHub Actions results are commit-specific evidence: a green run proves the checked commit, not future commits.

## Workflow history

| Workflow | Successful | Failed | Current state |
|---|---:|---:|---|
| Validate Mission Directives | 15 | 30 | Passing on Ubuntu, Windows, and macOS |
| Deploy documentation | 10 | 1 | Passing |
| Publish Mission Directives | 0 | 2 | Build corrected; PyPI publisher registration pending |

Thirty historical failures belonged to `Validate Mission Directives`. One later failure belonged to documentation deployment, and two belonged to release publication attempts.

## Complete failure history

### Initial cross-platform assumptions

Failed runs: `29529958144`, `29530747339`, `29531136214`, `29554778009`, `29554972542`, `29555307992`.

Errors included rejection of macOS `/var -> /private/var`, unsupported Windows `os.fchmod`, CP1252 decoding of UTF-8 files, platform-specific path assertions, cleanup output assumptions, and `.git` or `.ruff_cache` entering the manifest.

Fixes allowed trusted root-owned system symlinks without weakening project checks, guarded unsupported calls, required UTF-8, normalized serialized paths, made assertions portable, and excluded repository metadata and caches. Fix commits: `606c2a5`, `4168fdf`, `8817234`, `e51fe16`, `cba941c`.

### CRLF and manifest reproducibility

Failed runs: `29589741042`, `29590586557`, `29591202031`, `29591799002`.

Windows checkout converted LF to CRLF while manifest and reproducibility checks compared raw text bytes. Partial fixes normalized individual files but not every hashing path.

Fix `0738404` normalized CRLF to LF before textual manifest hashing. First green replacement: `29592414262`.

### Untracked runtime file in the manifest

Failed run: `29592784853`.

Local `.prompt_suite/logs/README.md` entered `MANIFEST.json` but was absent from a clean CI checkout. Fix `cf7037b` removed the local-only file from the release manifest. Green replacement: `29594660309`.

### Repository reorganization and stale consumers

Failed runs: `29721691430`, `29721993952`, `29724260633`, `29762473652`, `29764115546`, `29767730008`, `29808403553`.

Tests and documentation still referenced files moved into `tools/`, `config/`, `policies/`, and `docs/`; wrapper tests expected removed implementation details; audits were tested before generation; `uv pip install --system` conflicted with runner Python; one schema helper recursed; cleanup tests used obsolete paths.

Fixes updated every consumer, tested wrapper behavior, generated audits before tests, installed into the activated environment, and repaired schema and cleanup tests. Fix commits: `081a755`, `5402f24`, `0fcf66a`, `ed1a4e5`, `956304a`, `71facc3`.

### Virtual-environment traversal

Failed runs: `29809207480`, `29809774383`, `29810933814`, `29840484389`.

Linux `.venv/lib64` and macOS `.venv/bin/python` are symlinks. Installers, tree walkers, state digests, and manifest scans copied or rejected them.

Fixes excluded `.venv` from installer copies, tree walks, state digests, manifest scans, and packaged runtime paths, and corrected the installed cleanup path. Fix commits: `14dd430`, `0d67071`, `4f85bdd`, `b91005f`.

### Generated receipts changed the sealed path set

Failed run: `29910133114`.

Validation generated receipts and result files that unrestricted manifest enumeration then treated as release content. Fix `c2061bf` excluded generated audits, reports, results, runtime data, logs, locks, and caches.

### Python environment and Node-action migration

Failed runs: `29945762711`, `29950497647`.

The PowerShell wrapper selected system Python without `PyYAML`; an action update stopped activating uv's environment; older action releases emitted Node 20 warnings.

Fixes made wrappers prefer the active virtual environment, retained setup-uv `activate-environment: 'true'`, and upgraded to Node 24-compatible actions. Fix commits: `568ae7c`, `2a00f50`. Green runs: `29949228240`, `29953020848`.

### Platform-dependent prompt-import provenance

Failed run: `30209697568`.

Provenance creation and validation hashed different line-ending representations. Fix `a22e987` normalized CRLF to LF in both paths. Green replacement: `30212982055`.

### Documentation implementation and tests diverged

Failed run: `30219062633`.

The site had moved from Starlight to a custom static Astro shell, while tests still required Starlight and its previous generated paths. Fix `8866ed1` aligned implementation, tests, dependencies, generated sections, ignore rules, and documentation. Green replacement: `30220932102`.

### Packaged runtime, symlink contract, and local blog content

Failed runs: `30357381343`, `30358939782`, `30359363664`.

The security test targeted obsolete `.prompt_suite`; guard text said `symbolic link` while the tested contract expected `symlink`; ignored local `blog/` and `blog.zip` entered the local manifest but were absent in CI.

Fixes updated the test, added explicit destination-symlink rejection, stabilized error wording, switched manifest enumeration to `git ls-files --cached --others --exclude-standard`, ignored `blog.zip`, and added a regression for Git-ignored paths. Fix commits: `236bb60`, `b0f0c3c`, `912b32f`. Green replacement `30360409885` passed every applicable step on all three platforms.

### Local pre-push guidance receipt conflict

The July 28 release pre-push run failed `tests/test_release_consistency.py` because `sync_agent_guidance.py` created `.prompt_suite/agent-guidance-receipt.json` by default while the release gate correctly rejected machine-local receipts. The tool already described receipts as optional, so the durable fix removed the contradictory CLI default and added a regression proving that only explicit `--receipt` use writes the file. Remove any receipt left by an older invocation before release validation.

### Publishing workflow skipped required audit generation

Failed run: `30369810482` for tag `v2.0.0`.

The main validation workflow was green, but the separate publishing workflow ran raw `python -m pytest -q` in a clean checkout before generating `BODY_QUALITY_AUDIT.json` and `BODY_QUALITY_AUDIT.md`. Reproducibility and prompt-body tests therefore failed with two missing-artifact errors. Build failure skipped both PyPI publication and GitHub Release creation, so no package or release was published from that tag.

The durable fix aligned publishing with the canonical order: generate body audits, run `tools/run_tests.py`, run evaluations, validate the suite, build distributions, and smoke-test the installed wheel. A workflow regression now verifies both command presence and order. The failed public tag remains immutable; recovery uses patch release `v2.0.1`.

### Local patch-release manifest mismatch

The first targeted `2.0.1` release test passed 20 checks but failed release consistency because `MANIFEST.json` still declared suite version `2.0.0`. The old pre-push list rebuilt the manifest after deterministic tests even though those tests already enforce release consistency.

The durable fix moved manifest generation ahead of the deterministic suite. Run all applicable source and site generators first, generate audits, rebuild the manifest, then run tests and finish with `build_manifest.py --check`. CI still verifies rather than mutates the committed manifest.

### Release replacement corrupted the site lockfile

Failed run: `30372716698` at commit `dd11169`.

A mechanical `2.0.0` to `2.0.1` replacement changed package versions, peer ranges, and engine constraints throughout `site/pnpm-lock.yaml`, including the valid `github-slugger@2.0.0` resolution to a nonexistent `2.0.1` tarball. The local site check reused the existing `site/node_modules`, so it passed without proving that the committed lockfile could install in a clean checkout. GitHub's clean documentation build failed with `ERR_PNPM_FETCH_404` before deployment.

The durable fix restored the complete lockfile from before the release sweep. Release-version edits must target suite-owned metadata only and must exclude package-manager lockfiles. After every release-version change or site dependency edit, run `pnpm --dir site install --frozen-lockfile` before `pnpm --dir site run check`.

### First Trusted Publishing exchange and artifact-only release job

Failed run: `30374282771` for tag `v2.0.1`.

The corrected release build passed audits, deterministic tests, evaluations, full validation, distribution build, and installed-package smoke tests. PyPI then rejected the valid GitHub OIDC token with `invalid-publisher` because no matching Trusted Publisher existed for project `mission-directives`, owner `manojpisini`, repository `mission-directives`, workflow `publish.yml`, and environment `pypi`.

The independent GitHub release job also failed because it downloaded artifacts without checking out the repository, while `gh release create --verify-tag` attempted `.git`-based repository discovery. The release was recovered from the validated artifacts with an explicit repository target. The durable workflow fix passes `--repo "${{ github.repository }}"`, and its regression test requires that argument.

## Required pre-push workflow

Create and activate the CI-equivalent environment:

```powershell
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv pip install -r requirements-dev.txt
```

Run from the repository root, in order:

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

For documentation or site changes, also run:

```powershell
pnpm --dir site install --frozen-lockfile
pnpm --dir site run check
```

Do not push unless every applicable command exits successfully.

## Prevention rules

- Run all applicable generators, rebuild `MANIFEST.json` before deterministic release tests, and finish with `--check` after the final tracked-file change.
- Never seal `.git`, `.venv`, caches, builds, generated audits, logs, locks, receipts, runtime results, or ignored machine-local content.
- Guidance synchronization writes a source-repository receipt only when `--receipt` is explicit; release checkouts contain no `.prompt_suite/agent-guidance-receipt.json`.
- Use Git-aware enumeration for release files.
- Specify UTF-8 for repository text and normalize line endings before hashing it.
- Serialize project-relative paths with `/`; avoid cross-platform absolute-path assertions.
- After moving files, search the entire repository for every previous path.
- Update a generator, committed outputs, tests, manifest, and documentation together.
- Preserve CI order: environment, dependencies, audits, tests, evaluations, checks, validation, package build, package smoke, wrappers, artifacts.
- Keep validation and publication prerequisites aligned; every clean-checkout test path generates body audits before the canonical deterministic runner.
- Register and verify the exact PyPI Trusted Publisher before pushing the first public tag; repository workflow configuration cannot create the account-side publisher.
- Pass an explicit repository to GitHub CLI commands in artifact-only jobs that do not check out the repository.
- Keep setup-uv environment activation enabled; do not restore `uv pip install --system`.
- Test direct Python entry points and Bash/PowerShell wrappers.
- Keep site implementation, dependencies, tests, generated paths, ignore rules, and documentation synchronized.
- Never apply suite-version replacements to dependency lockfiles; target only declared suite-version fields.
- Prove the committed site lockfile with a frozen install before relying on site checks that may reuse existing modules.
- Build wheel and sdist and install the built package for package changes.
- Use a clean clone or isolated worktree for broad changes so untracked files cannot hide omissions.
- Use past-tense declarative commit messages without first-person pronouns.
- After pushing, verify Ubuntu, Windows, and macOS; one green platform is insufficient.

## Current action baseline

- `actions/checkout@v7`;
- `astral-sh/setup-uv@v9` with `activate-environment: 'true'`;
- `actions/upload-artifact@v6`;
- `actions/download-artifact@v7`;
- `actions/deploy-pages@v5`;
- `withastro/action@v6`.

Do not downgrade these actions without checking the runner's Node policy and rerunning workflow contract tests.
