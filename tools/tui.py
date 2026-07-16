#!/usr/bin/env python3
"""Dependency-free, accessible terminal progress and outcome rendering."""
from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterable


class TUI:
    """Small stderr-only TUI that degrades to deterministic line output."""

    def __init__(self, title: str, total: int = 1, enabled: bool | None = None):
        self.title = title
        self.total = max(1, total)
        self.current = 0
        self.started = time.perf_counter()
        self.enabled = (
            sys.stderr.isatty()
            and not os.environ.get("CI")
            and not os.environ.get("MD_NO_TUI")
        ) if enabled is None else enabled

    @property
    def elapsed_ms(self) -> int:
        return int((time.perf_counter() - self.started) * 1000)

    def _bar(self) -> str:
        ratio = min(1.0, self.current / self.total)
        width = 28
        filled = int(width * ratio)
        return "[" + "#" * filled + "-" * (width - filled) + f"] {ratio * 100:6.2f}%"

    def _clear_dynamic_line(self) -> None:
        if self.enabled:
            print("\r" + " " * 110 + "\r", end="", file=sys.stderr)

    def start(self) -> None:
        self.message("START", self.title)
        self.render("initializing")

    def render(self, label: str = "working") -> None:
        text = f"{self._bar()} {label}"
        if self.enabled:
            print("\r" + text.ljust(100), end="", file=sys.stderr, flush=True)
        else:
            print(f"PROGRESS {self.current}/{self.total} {label}", file=sys.stderr, flush=True)

    def step(self, label: str = "working", advance: int = 1) -> None:
        self.current = min(self.total, self.current + max(0, advance))
        self.render(label)

    def message(self, status: str, text: str) -> None:
        self._clear_dynamic_line()
        print(f"{status}: {text}", file=sys.stderr, flush=True)

    def finish(self, status: str = "PASS") -> None:
        self.current = self.total
        self.render(status.lower())
        if self.enabled:
            print(file=sys.stderr)
        self.message(status, f"{self.title} ({self.elapsed_ms} ms)")

    def summary(
        self,
        status: str,
        heading: str,
        details: Iterable[tuple[str, object]] = (),
    ) -> None:
        """Render a bounded, readable final status panel to stderr."""
        rows = [(str(key), str(value)) for key, value in details if value not in (None, "")]
        body = [f"{status}: {heading}"] + [f"{key}: {value}" for key, value in rows]
        width = min(100, max(48, *(len(line) + 4 for line in body)))
        border = "+" + "-" * (width - 2) + "+"
        self._clear_dynamic_line()
        print(border, file=sys.stderr)
        for index, line in enumerate(body):
            clipped = line[: width - 4]
            print(f"| {clipped.ljust(width - 4)} |", file=sys.stderr)
            if index == 0 and len(body) > 1:
                print("|" + "-" * (width - 2) + "|", file=sys.stderr)
        print(border, file=sys.stderr, flush=True)
