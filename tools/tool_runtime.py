#!/usr/bin/env python3
"""Shared lifecycle, TUI, and telemetry bootstrap for direct tool execution."""
from __future__ import annotations

import atexit
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

try:
    from tui import TUI
    from telemetry import append_event
except ImportError:
    from tools.tui import TUI
    from tools.telemetry import append_event


class ToolRuntime:
    """One correlated lifecycle record that fails closed on uncaught errors."""

    def __init__(self, path: str, total: int = 1):
        self.name = Path(path).name
        self.tui = TUI(self.name, total=total)
        self.started = time.perf_counter()
        self.run_id = os.environ.get("MD_RUN_ID") or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self._failed = False
        self._error = ""
        self._finished = False
        self._original_excepthook = sys.excepthook
        self.tui.start()
        try:
            append_event("tool", "invoke", "started", tool=self.name, run_id=self.run_id, span_id=self.span_id, context={"arg_count": max(0, len(sys.argv) - 1)})
        except Exception:
            pass
        sys.excepthook = self._excepthook
        atexit.register(self._finish)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.tui, name)

    def fail(self, error: BaseException | str) -> None:
        self._failed = True
        self._error = str(error)

    def succeed(self) -> None:
        if not self._failed:
            self._error = ""

    def _excepthook(self, exc_type, exc, tb) -> None:
        if not issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            self.fail(exc)
        self._original_excepthook(exc_type, exc, tb)

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        # sys.last_value is populated for uncaught exceptions before atexit.
        last = getattr(sys, "last_value", None)
        if last is not None and not isinstance(last, SystemExit):
            self.fail(last)
        status = "fail" if self._failed else "pass"
        label = "FAIL" if self._failed else "DONE"
        duration = int((time.perf_counter() - self.started) * 1000)
        try:
            self.tui.finish(label)
        except Exception:
            pass
        try:
            append_event("tool", "invoke", status, duration_ms=duration, tool=self.name, run_id=self.run_id, span_id=self.span_id, error=self._error or None)
        except Exception:
            pass
        try:
            sys.excepthook = self._original_excepthook
        except Exception:
            pass


def bootstrap_tool(path: str, total: int = 1) -> ToolRuntime:
    return ToolRuntime(path, total=total)
