# Project Cleanup and Uninstall Guide

This guide explains how to remove a Mission Directives project installation without deleting unrelated project content. The cleanup workflow is the transactional inverse of `install.py`.

## What cleanup removes

After validating the installation under `<project>/prompts`, cleanup removes:

- the complete `prompts/` suite copy;
- Mission Directives-owned `.prompt_suite/` runtime state, receipts, logs, locks, and results;
- runtime directories created and marked by the installer: `results/`, `reports/`, `logs/`, `artifacts/`, and `outputs/`;
- an empty installer-created `docs/` directory;
- verified stale `.md-prompts-backup-*` and `.md-prompts-staging-*` suite directories;
- the block between `# BEGIN MISSION DIRECTIVES MANAGED IGNORE` and `# END MISSION DIRECTIVES MANAGED IGNORE` in `.gitignore`;
- the block between `<!-- BEGIN MD MANAGED GUIDANCE -->` and `<!-- END MD MANAGED GUIDANCE -->` in `AGENTS.md` and `CLAUDE.md`.

Files are deleted only when their remaining content is empty. Existing human instructions and unrelated `.gitignore` entries are preserved.

## What cleanup deliberately preserves

Cleanup fails closed or preserves content when ownership cannot be demonstrated. In particular:

- a nonempty `docs/` directory is preserved because it may contain project documentation;
- preexisting generic directories are preserved unless the installation receipt or managed marker proves that Mission Directives created them;
- unverified backup or staging directories are retained and reported;
- unrelated content outside the managed blocks in `AGENTS.md`, `CLAUDE.md`, and `.gitignore` is never rewritten or removed.

## Preview first

### Python

```bash
python cleanup.py /path/to/project --dry-run
```

### Windows PowerShell

```powershell
.\cleanup.ps1 -ProjectPath 'C:\path\to\project' -DryRun
```

### Linux and macOS

```bash
./cleanup.sh /path/to/project --dry-run
```

The preview returns a SHA-256 approval token bound to the current suite tree, managed project files, selected removal paths, and preservation decisions. A later project change invalidates the token.

## Interactive cleanup

```bash
python cleanup.py /path/to/project
```

The tool displays every planned removal and preservation decision. Type `REMOVE` exactly to continue.

## Noninteractive cleanup

Execute the current preview directly:

```bash
python cleanup.py /path/to/project --yes
```

For a separately reviewed preview, pass its token:

```bash
python cleanup.py /path/to/project --approval-token '<TOKEN>'
```

Use `--no-tui` for deterministic line-oriented progress in CI or redirected terminals.

## Transaction and rollback model

Cleanup performs these stages:

1. validate the project path and installed suite identity;
2. discover receipts, ownership markers, managed blocks, and safe preservation decisions;
3. bind the preview to a SHA-256 approval token;
4. acquire an exclusive project cleanup lock;
5. recompute the plan and reject stale approval;
6. snapshot `.gitignore`, `AGENTS.md`, and `CLAUDE.md` with their modes;
7. remove only managed text blocks;
8. quarantine all managed directories with atomic same-filesystem renames;
9. validate the result and optional receipt;
10. purge the quarantine and print a formatted summary.

Failures before destructive purge restore every quarantined path and the original project files. Purge is the explicit commit boundary: quarantined trees are deleted one at a time and verified absent. If a purge operation has already deleted or altered data and a later deletion fails, cleanup never restores only the surviving subset. It leaves the project integrations removed, retains the remaining `.md-cleanup-staging-*` quarantine, exits with status code `4`, and reports the exact recovery path. Release the file lock or permission obstruction, inspect the reported quarantine, and remove only that quarantine directory when safe. A purge failure that made no destructive change remains rollback-safe and restores the project completely.

## TUI and summary

Interactive terminals receive a live progress bar. CI and `--no-tui` receive stable lines such as:

```text
PROGRESS 4/10 verified approval against current project state
PROGRESS 7/10 quarantined managed suite and runtime paths
```

The final panel reports removed paths, managed files cleaned, bytes reclaimed, preserved paths, warnings, and elapsed time. A failure panel states the bounded reason and whether rollback was attempted.

## Optional external receipt

Cleanup normally leaves no Mission Directives file in the project. To retain an audit receipt, choose an external location:

```bash
python cleanup.py /path/to/project --yes --receipt ../mission-directives-cleanup.json
```

The receipt must not be inside a path scheduled for removal.

## Troubleshooting

### “Project state changed since approval”

A managed file, receipt, suite file, or ownership decision changed after preview. Run `--dry-run` again and review the new token.

### “Mission Directives installation was not found”

The project does not contain a valid `prompts/VERSION` and matching `prompts/RELEASE_ID`. Point cleanup at the project root, not at the `prompts` directory.

### A runtime directory was preserved

The installer could not prove ownership, usually because the directory existed before installation or the installation predates ownership metadata. Review it manually rather than forcing deletion.

### `docs/` remains

Cleanup preserves nonempty documentation. Remove it manually only after confirming that its contents are no longer required.

## Related documentation

- [Installation and Project Integration Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md)
- [Cross-Platform Tooling Guide](CROSS_PLATFORM_TOOLING_GUIDE.md)
- [TUI and Operator Experience Guide](TUI_AND_OPERATOR_EXPERIENCE_GUIDE.md)
- [Logging and Telemetry Guide](LOGGING_AND_TELEMETRY_GUIDE.md)
- [Security Operations Guide](SECURITY_OPERATIONS_GUIDE.md)


## Exit codes

- `0`: preview or cleanup completed successfully.
- `1`: validation or rollback-safe cleanup failure.
- `3`: the user explicitly declined the interactive confirmation.
- `4`: cleanup crossed the purge commit boundary but residual quarantine remains.
- `130`: the process was interrupted with Ctrl-C or an equivalent signal.

The distinct decline code lets automation differentiate a deliberate refusal from an interrupted process.
