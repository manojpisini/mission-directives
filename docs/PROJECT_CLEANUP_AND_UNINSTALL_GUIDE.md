# Project Cleanup and Uninstall Guide

## Purpose

The 2.0 uninstaller removes only a validated Mission Directives project installation and its managed guidance and ignore blocks. It does not infer ownership from common directory names and never removes unrelated project content.

## Preview

```bash
mission-directives uninstall /path/to/project --dry-run
```

The preview reports the `.mission-directives` tree and managed files that would change. It makes no filesystem changes.

## Apply

```bash
mission-directives uninstall /path/to/project --apply
```

Application requires a valid managed installation receipt. It removes:

- the validated `.mission-directives` installation;
- the block between the Mission Directives markers in `.gitignore`;
- the managed guidance block in `AGENTS.md` and `CLAUDE.md`.

Content outside managed markers is preserved. Empty guidance files created only for the managed block may be removed; human-authored files remain.

## Preserved content

- source code, tests, and project documentation outside `.mission-directives`;
- unmarked legacy `prompts/`, output directories, and other generic project paths;
- unrelated `.gitignore`, `AGENTS.md`, and `CLAUDE.md` content;
- any path whose ownership or containment cannot be validated.

## Failure behavior

Malformed markers, missing receipts, traversal, and symlink escape fail closed. If removal cannot be validated, inspect the reported path instead of deleting it manually as part of the same operation.

## Reinstall

After a successful uninstall, run:

```bash
mission-directives init /path/to/project --tracking ignored
```

For an older managed root-level installation, use `mission-directives migrate ... --dry-run` rather than uninstalling current paths by hand.

## Related documentation

- [Installation and Project Integration Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Project Config Guide](PROJECT_CONFIG_GUIDE.md)
- [Local Output Viewer Guide](LOCAL_OUTPUT_VIEWER_GUIDE.md)
