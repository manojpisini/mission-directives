# Mission Directives Installation and Project Integration Guide

## Purpose

This guide explains how to install the lean execution runtime into an existing project without overwriting human-authored instructions. The installed runtime lives at `./prompts`; source-only tests, evaluations, import tooling, CI, and site assets remain in the Mission Directives repository.

The exact boundary is declared by `config/runtime_payload.json` and explained in the [Installed Runtime Payload Guide](INSTALLED_RUNTIME_PAYLOAD_GUIDE.md).

## Requirements

Install the runtime dependency set in the environment that will invoke the installed tools:

```bash
python -m pip install -r requirements-runtime.txt
```

Repository contributors use `requirements-dev.txt` instead.

## Quick installation

Always inspect the dry run first.

### Linux or macOS

```bash
./install.sh /absolute/path/to/project --dry-run
./install.sh /absolute/path/to/project
```

### Windows PowerShell 7

```powershell
./install.ps1 -ProjectPath 'C:\path\to\project' -DryRun
./install.ps1 -ProjectPath 'C:\path\to\project'
```

### Portable Python

```bash
python tools/install.py /absolute/path/to/project --dry-run
python tools/install.py /absolute/path/to/project
```

Use `--replace` only when updating an existing installation.

## Runtime payload

The installer includes all files needed to route, inspect, plan, execute, verify runtime contracts, resolve templates and skills, synchronize agent guidance, log, and uninstall. This includes catalogs, prompts, scenarios, compatibility maps, configuration, examples, integrations, policies, schemas, templates, selected runtime tools, and `requirements-runtime.txt`.

The following remain source-only:

- `.github/`;
- `tests/`;
- `evaluations/`;
- `prompt_imports/`;
- `site/`;
- prompt authoring/import tools;
- repository audit, validation, test, evaluation, and manifest tools;
- `requirements-dev.txt`.

This is an allowlist, not a repository copy with ignore rules. New source directories cannot silently bloat future installations.

## Exact effects

1. Validates the project path and rejects overlap with the suite source.
2. Loads and validates `config/runtime_payload.json`.
3. Stages only the declared runtime files and verifies the staged tree.
4. Promotes the payload to `<project>/prompts`.
5. Adds one managed block to `<project>/.gitignore`.
6. Keeps `<project>/docs` tracked and creates runtime-owned directories when absent.
7. Creates or updates only `AGENTS.md` and `CLAUDE.md` using managed markers.
8. Preserves all content outside managed markers.
9. Writes installation and guidance receipts under `<project>/.prompt_suite/`.
10. Restores the prior suite and project files if a post-promotion step fails.

## Receipt

A successful installation receipt records the runtime profile, installed file count, suite version, destination, backup path, created runtime directories, preexisting project files, guidance result, and UTC timestamp. It validates against `schemas/installation_receipt.schema.json`.

The dry-run response also lists repository-only exclusions.

## Reinstallation and rollback

When `./prompts` already exists, the installer fails closed unless `--replace` is supplied. Replacement first renames the old copy to `.md-prompts-backup-<timestamp>-<uuid>`. A post-promotion failure removes the failed runtime, restores the backup, and restores preserved project files.

Review and delete backups only after the installed runtime passes its smoke checks.

## Skill directories

Mission Directives resolves global skill directories by application and platform through `prompts/compatibility/agent_skill_paths.json`:

- `.agents`: `%USERPROFILE%\.agents\skills` on Windows, `$HOME/.agents/skills` on Linux and macOS;
- Claude Code: `%USERPROFILE%\.claude\skills` on Windows, `$HOME/.claude/skills` on Linux and macOS;
- OpenCode: `%USERPROFILE%\.config\opencode\skills` on Windows, `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` on Linux and macOS.

Environment overrides `MD_AGENTS_SKILLS_DIR`, `MD_CLAUDE_SKILLS_DIR`, and `MD_OPENCODE_SKILLS_DIR` take precedence.

## Installed-runtime verification

```bash
python <project>/prompts/tools/md.py route "MD cleanup dead code safely"
python <project>/prompts/tools/md.py explain C-25
python <project>/prompts/tools/md.py plan C-25 --mode AUDIT_ONLY --root <project> --dry-run
```

Confirm:

- `payload_profile` is `runtime`;
- `installed_file_count` is positive;
- `config/router_keywords.json` and runtime schemas exist;
- source-only paths are absent;
- `.gitignore` does not ignore project `docs/`;
- `AGENTS.md` and `CLAUDE.md` contain exactly one managed guidance block.

Repository validators such as `validate_suite.py` and `build_manifest.py` intentionally remain upstream; run them in the Mission Directives source repository.

## Removing an installation

Use the [Project Cleanup and Uninstall Guide](PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md) for the approval-bound inverse workflow. It removes only validated Mission Directives-managed paths and text blocks while preserving unrelated project content.
