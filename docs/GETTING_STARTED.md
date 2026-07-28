# Getting Started

Mission Directives installs a command-line runtime globally and pins a complete operational copy inside each project. The project copy keeps routing behavior stable across global package upgrades.

## Requirements

- Python 3.11 or newer.
- `uv` is recommended. `pipx`, user-level `pip`, and one-off `uvx` execution are also supported.

## 1. Install the command

```bash
uv tool install mission-directives
```

Alternative installers:

```bash
pipx install mission-directives
python -m pip install --user mission-directives
```

Run a one-off command without persistent installation:

```bash
uvx mission-directives --help
```

After installing with pip, the module entry point is available even when the console-script directory is not on `PATH`:

```bash
python -m mission_directives --help
```

## 2. Initialize a project

Run the command from the project root:

```bash
mission-directives init --tracking ignored
```

This creates `.mission-directives/` with the pinned runtime, Project Config, local viewer, state, and output categories. Use `--tracking outputs` to track Project Config and generated outputs, or `--tracking all` to track the complete managed installation except transient state.

See the [Installation and Project Integration Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md) for the full layout, migration behavior, and tracking rules.

## 3. Validate Project Config

```bash
mission-directives config show
mission-directives config validate
```

Open the local settings page when project details need review or correction:

```bash
mission-directives config open
```

Project Config is a knowledge cache, not an authorization source. Current user instructions and verified repository evidence take precedence.

## 4. Route the first request

```bash
mission-directives route "MD audit this project and report the highest-risk gaps"
mission-directives explain C-108
mission-directives plan C-108 --mode AUDIT_ONLY --root . --dry-run
```

Use the target returned by `route` in the `explain` and `plan` commands. The example target shows the audit, remediation, and verification scenario.

## 5. View generated output

```bash
mission-directives view
```

The loopback-only viewer indexes project-specific results, reports, artifacts, plans, outputs, docs, and logs without rewriting the underlying files.

## Next steps

- [User Manual](USER_MANUAL.md) for routing, modes, artifacts, and completion.
- [Operator Guide](OPERATOR_GUIDE.md) for daily command workflows.
- [Project Config Guide](PROJECT_CONFIG_GUIDE.md) for config-first agent lookup and refresh rules.
- [Local Output Viewer Guide](LOCAL_OUTPUT_VIEWER_GUIDE.md) for rendering and security behavior.
- [Contributing](../CONTRIBUTING.md) for repository development.
