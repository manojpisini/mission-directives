# Mission Directives Installation and Project Integration Guide

## Purpose

Mission Directives 2.0 installs a global command and a pinned, project-specific runtime. The global package provides lifecycle commands. Routing inside an initialized project uses `./.mission-directives/runtime`, so a later global upgrade cannot silently change that project's prompt behavior.

The runtime boundary is declared by `config/runtime_payload.json`. Repository tests, evaluations, CI configuration, release tooling, and the Astro documentation site remain source-only.

## Install the command

Python 3.11 or newer is required.

```bash
uv tool install mission-directives
```

Compatible persistent alternatives are `pipx install mission-directives` and `python -m pip install --user mission-directives`. Use `uvx mission-directives <command>` for one-off execution without persistent installation, or `python -m mission_directives <command>` after pip installation when the console-script directory is not on `PATH`. The package does not claim the `md` executable because PowerShell reserves that name as an alias.

## Initialize a project

```bash
cd /path/to/project
mission-directives init --tracking ignored
```

An explicit destination is also accepted:

```bash
mission-directives init /path/to/project --tracking outputs
```

Initialization is transactional. It stages the allowlisted payload, verifies it, promotes it to `.mission-directives/runtime`, creates Project Config and the local viewer, updates only managed `AGENTS.md`, `CLAUDE.md`, and `.gitignore` blocks, and rolls back the complete transaction on failure.

## Installed layout

```text
.mission-directives/
|-- runtime/          pinned prompts, catalogs, schemas, policies, and tools
|-- site/             independent local viewer templates and static files
|-- results/
|-- reports/
|-- artifacts/
|-- plans/
|-- outputs/
|-- docs/
|-- logs/
|-- state/            receipts, backups, locks, and local viewer state
|-- project.json      agent-facing Project Config
`-- config.json       installation and viewer settings
```

The repository Astro `site/` is not installed. The project viewer has independent package assets copied into `.mission-directives/site`.

## Tracking modes

- `ignored`: ignores the complete `.mission-directives` tree.
- `outputs`: tracks `project.json` and the seven output categories; ignores runtime, site, system config, and state.
- `all`: tracks runtime, site, configs, and output categories; still ignores transient state, locks, caches, and tokens.

Change the mode from the viewer Settings page. The explicit confirmation is required because the managed `.gitignore` block changes.

## Project Config

Initialization performs a bounded scan of standard manifests and writes confirmed facts to `.mission-directives/project.json`. Uncertain fields remain empty. Validate or refresh it with:

```bash
mission-directives config show
mission-directives config validate
mission-directives config refresh --dry-run
mission-directives config refresh --apply
mission-directives config open
```

Refresh preserves user-authored mission, goals, exclusions, constraints, and ownership. See [Project Config Guide](PROJECT_CONFIG_GUIDE.md).

## Routing and outputs

```bash
mission-directives route "MD cleanup dead code safely"
mission-directives explain C-25
mission-directives plan C-25 --mode AUDIT_ONLY --root . --dry-run
```

The launcher sets the installed project root and artifact root before dispatching to the pinned router. Existing logical output paths under `results/`, `reports/`, `artifacts/`, `plans/`, `outputs/`, `docs/`, and `logs/` therefore resolve under `.mission-directives` without changing prompt output contracts.

## Upgrade and migration

```bash
mission-directives upgrade /path/to/project --dry-run
mission-directives upgrade /path/to/project
mission-directives migrate /path/to/project --dry-run
mission-directives migrate /path/to/project --apply
```

Upgrade preserves Project Config and outputs. Migration recognizes only managed legacy receipts and markers, previews each move, preserves unmarked project content, and removes old managed paths only after verified promotion. See [Migration Guide](MIGRATION_GUIDE.md).

## Verification and removal

```bash
mission-directives config validate
mission-directives route "MD explain this project"
mission-directives view --no-open
mission-directives uninstall /path/to/project --dry-run
```

Use `mission-directives uninstall /path/to/project --apply` only after reviewing the preview. The uninstaller removes the validated `.mission-directives` installation and managed text blocks while preserving unrelated files.
