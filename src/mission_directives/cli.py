"""Public Mission Directives command line interface."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .__about__ import __version__
from .installer import (
    PROJECT_DIR,
    TRACKING_MODES,
    find_project_root,
    install_project,
    migrate_project,
    router_environment,
    runtime_source,
    uninstall_project,
)

ROUTER_COMMANDS = {"route", "lookup", "compare", "explain", "plan", "pair-status"}


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _dispatch_router(args: list[str]) -> int:
    try:
        project = find_project_root()
        runtime = project / PROJECT_DIR / "runtime"
        environment = router_environment(project)
    except FileNotFoundError:
        runtime = runtime_source()
        environment = None
    command = [sys.executable, str(runtime / "tools/md.py"), *args]
    return subprocess.call(command, env=environment)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mission-directives")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="Install Mission Directives into a project")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--tracking", choices=TRACKING_MODES, default="ignored")
    init.add_argument("--dry-run", action="store_true")

    upgrade = sub.add_parser("upgrade", help="Upgrade the pinned project runtime")
    upgrade.add_argument("path", nargs="?", default=".")
    upgrade.add_argument("--tracking", choices=TRACKING_MODES)
    upgrade.add_argument("--dry-run", action="store_true")

    migrate = sub.add_parser("migrate", help="Migrate a managed legacy installation")
    migrate.add_argument("path", nargs="?", default=".")
    action = migrate.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--apply", action="store_true")
    migrate.add_argument("--tracking", choices=TRACKING_MODES, default="ignored")

    uninstall = sub.add_parser("uninstall", help="Remove a managed project installation")
    uninstall.add_argument("path", nargs="?", default=".")
    uninstall_action = uninstall.add_mutually_exclusive_group(required=True)
    uninstall_action.add_argument("--dry-run", action="store_true")
    uninstall_action.add_argument("--apply", action="store_true")

    config = sub.add_parser("config", help="View and maintain Project Config")
    config_sub = config.add_subparsers(dest="config_command", required=True)
    show = config_sub.add_parser("show")
    show.add_argument("--json", action="store_true")
    config_sub.add_parser("validate")
    config_sub.add_parser("open")
    refresh = config_sub.add_parser("refresh")
    refresh_action = refresh.add_mutually_exclusive_group(required=True)
    refresh_action.add_argument("--dry-run", action="store_true")
    refresh_action.add_argument("--apply", action="store_true")

    view = sub.add_parser("view", help="Serve project outputs locally")
    view.add_argument("--port", type=int, default=None)
    view.add_argument("--no-open", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ROUTER_COMMANDS:
        return _dispatch_router(argv)
    args = _parser().parse_args(argv)
    try:
        if args.command == "init":
            _emit(
                install_project(
                    args.path, tracking=args.tracking, dry_run=args.dry_run
                )
            )
        elif args.command == "upgrade":
            project = find_project_root(args.path)
            config = json.loads(
                (project / PROJECT_DIR / "config.json").read_text(encoding="utf-8")
            )
            _emit(
                install_project(
                    project,
                    tracking=args.tracking or config.get("tracking_mode", "ignored"),
                    replace=True,
                    dry_run=args.dry_run,
                )
            )
        elif args.command == "migrate":
            _emit(
                migrate_project(
                    args.path, apply=args.apply, tracking=args.tracking
                )
            )
        elif args.command == "uninstall":
            _emit(uninstall_project(args.path, apply=args.apply))
        elif args.command == "config":
            from . import project_config

            project = find_project_root()
            path = project / PROJECT_DIR / "project.json"
            if args.config_command == "show":
                value = project_config.load_project_config(project)
                if args.json:
                    _emit(value)
                else:
                    print(project_config.format_project_config(value))
            elif args.config_command == "validate":
                value = project_config.load_project_config(project)
                project_config.validate_project_config(value, project_root=project)
                _emit({"status": "pass", "path": str(path)})
            elif args.config_command == "refresh":
                proposal = project_config.refresh_project_config_diff(project)
                if args.apply:
                    project_config.save_project_config(
                        project,
                        proposal["refreshed"],
                        expected_revision=(proposal["current"] or {}).get("revision", 0),
                    )
                    proposal["status"] = "updated"
                _emit(proposal)
            elif args.config_command == "open":
                from .viewer import run_viewer

                return run_viewer(project, open_path="/settings")
        elif args.command == "view":
            from .viewer import run_viewer

            project = find_project_root()
            return run_viewer(
                project, port=args.port, open_browser=not args.no_open
            )
        return 0
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"mission-directives: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
