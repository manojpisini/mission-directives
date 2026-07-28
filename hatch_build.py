"""Build the declared runtime payload into the wheel without tracking a copy."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        if self.target_name != "wheel":
            return
        root = Path(self.root)
        contract = json.loads(
            (root / "config/runtime_payload.json").read_text(encoding="utf-8")
        )
        staging = root / "src/mission_directives/_runtime"
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

        for relative in contract["root_files"]:
            self._copy(root, staging, relative)
        for relative in contract["directories"]:
            source = root / relative
            shutil.copytree(source, staging / relative)
        for name in contract["tool_files"]:
            self._copy(root, staging, f"tools/{name}")

        build_data.setdefault("artifacts", []).append(
            "src/mission_directives/_runtime"
        )

    def finalize(
        self, version: str, build_data: dict, artifact_path: str
    ) -> None:
        if self.target_name != "wheel":
            return
        staging = Path(self.root) / "src/mission_directives/_runtime"
        if staging.exists():
            shutil.rmtree(staging)

    @staticmethod
    def _copy(root: Path, staging: Path, relative: str) -> None:
        source = root / relative
        destination = staging / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
