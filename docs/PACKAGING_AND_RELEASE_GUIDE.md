# Packaging and Release Guide

## Distribution

`pyproject.toml` defines the public `mission-directives` package, Python 3.11 minimum, `mission-directives` console entry point, runtime dependencies, and `MIT OR Apache-2.0` license expression. Hatchling builds the wheel and source distribution.

The custom build hook reads `config/runtime_payload.json` and stages one temporary wheel payload under `src/mission_directives/_runtime`. It avoids a second tracked runtime copy and removes staging after the wheel build.

## Local release checks

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

Before the first release, confirm that the `mission-directives` distribution name is available and configure the repository as a trusted publisher in PyPI. Do not add a long-lived PyPI token.

Commit messages use past-tense declarative form without first-person pronouns, for example `Added packaged runtime validation`.
