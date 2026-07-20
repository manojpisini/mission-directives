#!/usr/bin/env python3
"""Interactive TUI menu for Mission Directives operations."""

from __future__ import annotations
import os, shutil, subprocess, sys, textwrap, time, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tools = ROOT / "tools"


def c():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    c()
    v = (ROOT / "VERSION").read_text().strip()[:20]
    w = shutil.get_terminal_size().columns
    print("=" * w)
    print(f"  Mission Directives  v{v}".center(w))
    print("=" * w)
    print()


def pick(items: list[tuple[str, str]]) -> str | None:
    for i, (label, _) in enumerate(items, 1):
        print(f"  {i}. {label}")
    print(f"  {len(items) + 1}. Exit")
    try:
        n = int(input("\n  Choice: ").strip())
        if 1 <= n <= len(items):
            return items[n - 1][1]
    except (ValueError, EOFError):
        pass
    return None


def run(cmd: list[str], title: str) -> int:
    banner()
    print(f"  {title}...\n")
    t0 = time.time()
    r = subprocess.run(cmd, cwd=ROOT)
    e = time.time() - t0
    print(
        f"\n  {'Done' if r.returncode == 0 else 'Failed'} ({e:.1f}s, exit {r.returncode})"
    )
    input("  Press Enter to continue")
    return r.returncode


def menu():
    items = [
        ("Install mission directives", "install"),
        ("Run tests", "tests"),
        ("Run full validation", "validate"),
        ("Generate audit artifacts", "audit"),
        ("Run evaluations", "evaluations"),
        ("Clean up project", "cleanup"),
    ]
    while True:
        banner()
        print("  Operations:\n")
        action = pick(items)
        if action is None:
            c()
            print("Bye.")
            return
        if action == "install":
            run(
                [
                    sys.executable,
                    str(tools / "install.py"),
                    input("  Target project path: ").strip(),
                    "--replace",
                    "--no-tui",
                ],
                "Installing",
            )
        elif action == "tests":
            run([sys.executable, str(tools / "run_tests.py")], "Running tests")
        elif action == "validate":
            run(
                [sys.executable, str(tools / "validate_suite.py")], "Running validation"
            )
        elif action == "audit":
            run(
                [sys.executable, str(tools / "audit_prompt_bodies.py")],
                "Generating audit",
            )
        elif action == "evaluations":
            run(
                [sys.executable, str(tools / "run_evaluations.py")],
                "Running evaluations",
            )
        elif action == "cleanup":
            run(
                [
                    sys.executable,
                    str(tools / "cleanup.py"),
                    input("  Target project path: ").strip(),
                    "--dry-run",
                    "--no-tui",
                ],
                "Previewing cleanup",
            )


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        c()
        print("Interrupted.")
