# Mission Directives Installation and Project Integration Guide

## Purpose

This guide explains how to install the complete suite into an existing project without overwriting human-authored instructions. The installed suite lives at `./prompts`, while project documentation remains tracked under `./docs`.

## Quick installation

### Linux or macOS

```bash
./install.sh /absolute/path/to/project
```

### Windows PowerShell 7

```powershell
./install.ps1 -ProjectPath 'C:\path\to\project'
```

### Portable Python

```bash
python install.py /path/to/project
```

Use `--dry-run` first to inspect the operation. Use `--replace` only when updating an existing `./prompts` installation; the installer creates a timestamped backup before replacement.

## Exact effects

1. Copies the distribution to `<project>/prompts` through a staging directory.
2. Adds one managed block to `<project>/.gitignore` for `/prompts/`, `/.prompt_suite/`, `/results/`, `/reports/`, `/logs/`, `/artifacts/`, `/outputs/`, `/.md-prompts-staging-*/`, and `/.md-prompts-backup-*/`.
3. Leaves `/docs/` tracked and creates it when absent.
4. Creates internal runtime directories.
5. Creates or updates only `AGENTS.md` and `CLAUDE.md` using managed markers; all text outside those markers is preserved.
6. Writes installation and guidance receipts to `<project>/.prompt_suite/`.

## Reinstallation and rollback

When `./prompts` already exists, the installer fails closed unless `--replace` is supplied. Replacement first renames the old copy to `.md-prompts-backup-<timestamp>`. If the staged copy cannot be promoted, the previous copy is restored. Review and delete backups only after validation.

## Skill directories

Mission Directives resolves global skill directories by application and platform through `prompts/compatibility/agent_skill_paths.json`:

- `.agents`: `%USERPROFILE%\.agents\skills` on Windows, `$HOME/.agents/skills` on Linux and macOS;
- Claude Code: `%USERPROFILE%\.claude\skills` on Windows, `$HOME/.claude/skills` on Linux and macOS;
- OpenCode: `%USERPROFILE%\.config\opencode\skills` on Windows, `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` on Linux and macOS.

Environment overrides `MD_AGENTS_SKILLS_DIR`, `MD_CLAUDE_SKILLS_DIR`, and `MD_OPENCODE_SKILLS_DIR` take precedence.

## Verification

```bash
python prompts/tools/md.py lookup 'audit fix verify'
python prompts/tools/validate_suite.py
python prompts/tools/build_manifest.py --check
```

Confirm that `.gitignore` does not ignore `docs/`, and confirm that `AGENTS.md` and `CLAUDE.md` contain exactly one `BEGIN MD MANAGED GUIDANCE` block.

## Removing an installation

Use the [Project Cleanup and Uninstall Guide](PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md) for the approval-bound inverse workflow. It removes `prompts/`, managed runtime paths, and managed text blocks while preserving unrelated project content.
