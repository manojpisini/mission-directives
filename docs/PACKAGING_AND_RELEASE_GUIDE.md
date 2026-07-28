# Packaging and Release Guide

## Distribution

`pyproject.toml` defines the public `mission-directives` package, Python 3.11 minimum, `mission-directives` console entry point, runtime dependencies, and `MIT OR Apache-2.0` license expression. Hatchling builds the wheel and source distribution.

The custom build hook reads `config/runtime_payload.json` and stages one temporary wheel payload under `src/mission_directives/_runtime`. It avoids a second tracked runtime copy and removes staging after the wheel build.

## Local release checks

The authoritative pre-push and pre-tag sequence, including historical failure prevention, is [GitHub Actions Failure History and Pre-Push Guide](GITHUB_ACTIONS_FAILURE_HISTORY_AND_PRE_PUSH_GUIDE.md).

The tag-triggered publishing workflow must generate prompt-body audits before `tools/run_tests.py`, then run evaluations and full validation before building. Do not replace this sequence with raw pytest in a clean checkout because audit-dependent tests intentionally fail when their generated evidence is absent.

Release-version replacements must target suite metadata and exclude dependency lockfiles. Prove the documentation lockfile independently with `pnpm --dir site install --frozen-lockfile`; an existing module directory is not clean-install evidence.

```bash
python -m pytest
python tools/build_manifest.py
python tools/validate_suite.py
uv build
python tools/package_smoke.py dist
```

The smoke check installs the wheel into a clean environment, initializes a temporary project, validates Project Config, exercises pinned routing, starts viewer routes, and verifies shutdown behavior.

## Publication

Tags matching `v*` trigger `.github/workflows/publish.yml`. The workflow validates, builds wheel and sdist, runs the package smoke test, publishes through PyPI Trusted Publishing, and creates a GitHub release with artifacts and SHA-256 checksums.

Before the first release, confirm that the `mission-directives` distribution name is available and create the PyPI Trusted Publisher with project `mission-directives`, GitHub owner `manojpisini`, repository `mission-directives`, workflow `publish.yml`, and environment `pypi`. PyPI must contain this account-side registration before the tag requests an OIDC token. Do not add a long-lived PyPI token.

Artifact-only jobs do not contain `.git`. GitHub CLI release commands therefore pass `--repo "${{ github.repository }}"` instead of relying on repository discovery.

Commit messages use past-tense declarative form without first-person pronouns, for example `Added packaged runtime validation`.
