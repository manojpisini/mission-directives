#!/usr/bin/env python3
"""Install the built wheel in an isolated environment and exercise public commands."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import venv
from pathlib import Path
from http.cookies import SimpleCookie
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main() -> int:
    distribution = Path(sys.argv[1] if len(sys.argv) > 1 else "dist").resolve()
    wheels = sorted(distribution.glob("mission_directives-*.whl"))
    archives = sorted(distribution.glob("mission_directives-*.tar.gz"))
    if len(wheels) != 1 or len(archives) != 1:
        raise SystemExit("Expected exactly one wheel and one source archive")
    uv = shutil.which("uv")
    if not uv:
        raise SystemExit("uv is required for the isolated package smoke test")

    with tempfile.TemporaryDirectory(prefix="mission-directives-package-") as raw:
        root = Path(raw)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=False).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [uv, "pip", "install", "--python", str(python), str(wheels[0])],
            check=True,
        )
        project = root / "project"
        project.mkdir()
        run = lambda *args: subprocess.run(  # noqa: E731
            [str(python), "-m", "mission_directives", *args],
            cwd=project,
            text=True,
            capture_output=True,
            check=True,
        )
        version = run("--version").stdout.strip()
        init = json.loads(run("init", ".").stdout)
        validate = json.loads(run("config", "validate").stdout)
        route = json.loads(run("route", "MD report repository status").stdout)
        plan = json.loads(
            run(
                "plan", "C-63", "--mode", "DRAFT_ONLY", "--root", ".",
                "--out", "reports/package-plan.json",
            ).stdout
        )
        if version != "2.0.3":
            raise SystemExit(f"Unexpected installed version: {version}")
        if init.get("status") != "installed" or validate.get("status") != "pass":
            raise SystemExit("Installed lifecycle smoke failed")
        if not route:
            raise SystemExit("Installed router returned no result")
        if not plan or not (
            project / ".mission-directives/reports/package-plan.json"
        ).is_file():
            raise SystemExit("Installed artifact-root resolution failed")
        if not (project / ".mission-directives/site/templates/base.html").is_file():
            raise SystemExit("Installed local viewer assets are missing")

        runtime = project / ".mission-directives"
        (runtime / "reports/smoke.md").write_text("# Package smoke\n", encoding="utf-8")
        (runtime / "outputs/smoke.json").write_text('{"status":"pass"}\n', encoding="utf-8")
        (runtime / "artifacts/smoke.bin").write_bytes(b"smoke")

        import socket

        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        server = subprocess.Popen(
            [
                str(python),
                "-m",
                "mission_directives",
                "view",
                "--port",
                str(port),
                "--no-open",
            ],
            cwd=project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        base = f"http://127.0.0.1:{port}"
        try:
            for _ in range(100):
                try:
                    response = urlopen(f"{base}/", timeout=0.25)
                    break
                except (URLError, TimeoutError):
                    if server.poll() is not None:
                        raise RuntimeError(server.communicate()[1])
                    time.sleep(0.05)
            else:
                raise RuntimeError("Viewer did not start")

            if response.status != 200:
                raise RuntimeError("Viewer home failed")
            for path in (
                "/category/reports",
                "/file/reports/smoke.md",
                "/file/outputs/smoke.json",
                "/download/artifacts/smoke.bin",
                "/settings",
            ):
                with urlopen(f"{base}{path}", timeout=2) as page:
                    if page.status != 200:
                        raise RuntimeError(f"Viewer route failed: {path}")

            with urlopen(f"{base}/settings", timeout=2) as settings:
                cookie = SimpleCookie(settings.headers["Set-Cookie"])
                token = cookie["md_viewer_csrf"].value
            config_path = runtime / "project.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            form = {
                "action": "save_config",
                "csrf_token": token,
                "schema_version": config["schema_version"],
                "revision": str(config["revision"]),
            }
            for section in (
                "project", "goals", "scope", "stack", "paths", "commands",
                "constraints", "working_agreements", "current_state", "provenance",
                "extensions",
            ):
                form[f"section_{section}_json"] = json.dumps(config[section])
            form["section_project_json"] = json.dumps(
                {**config["project"], "name": "Package Smoke"}
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": f"md_viewer_csrf={token}",
                "Origin": base,
            }
            save = Request(
                f"{base}/settings",
                data=urlencode(form).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urlopen(save, timeout=2) as saved:
                if saved.status != 200:
                    raise RuntimeError("Project Config save failed")
            if json.loads(config_path.read_text(encoding="utf-8"))["revision"] != 1:
                raise RuntimeError("Project Config revision did not advance")

            shutdown = Request(
                f"{base}/shutdown",
                data=urlencode({"csrf_token": token}).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urlopen(shutdown, timeout=2) as stopped:
                if stopped.status != 202:
                    raise RuntimeError("Viewer shutdown request failed")
            server.wait(timeout=10)
            if server.returncode != 0:
                raise RuntimeError(server.communicate()[1])
        finally:
            if server.poll() is None:
                server.terminate()
                server.wait(timeout=5)
    print(json.dumps({"status": "pass", "wheel": wheels[0].name}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
