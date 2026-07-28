from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mission_directives import installer, project_config, viewer


def _make_project(root: Path) -> None:
    runtime = root / ".mission-directives"
    for name in (*viewer.CATEGORY_DIRS, "site", "state"):
        (runtime / name).mkdir(parents=True, exist_ok=True)

    (runtime / "results" / "old.txt").write_text("old", encoding="utf-8")
    (runtime / "results" / "summary.md").write_text(
        "# Summary\n\n[PDF](report.pdf)\n\n![Chart](chart.png)\n\n<script>alert(1)</script>\n",
        encoding="utf-8",
    )
    (runtime / "results" / "report.pdf").write_bytes(b"%PDF-1.7\n")
    (runtime / "results" / "chart.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (runtime / "reports" / "payload.json").write_text(
        '{"status":"ok","items":[1,2]}',
        encoding="utf-8",
    )
    system_config = {
        "created_by": "mission-directives",
        "tracking_mode": "ignored",
        "viewer": {"auto_open": True, "port": 0},
    }
    (runtime / "config.json").write_text(
        json.dumps(system_config, indent=2),
        encoding="utf-8",
    )

    saved = project_config.save_project_config(
        root,
        project_config.seed_project_config(root),
        expected_revision=0,
    )
    assert saved["revision"] == 0

    old_path = runtime / "results" / "old.txt"
    summary_path = runtime / "results" / "summary.md"
    old_stat = old_path.stat()
    summary_stat = summary_path.stat()
    old_path.touch()
    summary_path.touch()
    old_path = runtime / "results" / "old.txt"
    summary_path = runtime / "results" / "summary.md"
    old_mtime = min(old_stat.st_mtime, summary_stat.st_mtime) - 100
    summary_mtime = max(old_stat.st_mtime, summary_stat.st_mtime) + 100
    old_path.touch()
    summary_path.touch()
    import os

    os.utime(old_path, (old_mtime, old_mtime))
    os.utime(summary_path, (summary_mtime, summary_mtime))


async def _request(
    app,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
):
    sent: list[dict[str, object]] = []
    received = False

    async def receive():
        nonlocal received
        if received:
            return {"type": "http.request", "body": b"", "more_body": False}
        received = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "query_string": b"",
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1"))
            for key, value in (headers or {}).items()
        ],
    }
    await app(scope, receive, send)
    start = next(message for message in sent if message["type"] == "http.response.start")
    body_message = next(message for message in sent if message["type"] == "http.response.body")
    response_headers = {
        key.decode("latin-1").lower(): value.decode("latin-1")
        for key, value in start["headers"]
    }
    return start["status"], response_headers, body_message["body"]


def _csrf_from_headers(headers: dict[str, str]) -> str:
    cookie = headers["set-cookie"].split(";", 1)[0]
    return cookie.split("=", 1)[1]


def _settings_form(config: dict[str, object], csrf_token: str, **overrides: str) -> bytes:
    data = {
        "action": "save_config",
        "csrf_token": csrf_token,
        "schema_version": str(config["schema_version"]),
        "revision": str(config["revision"]),
    }
    for section in viewer.CONFIG_JSON_SECTIONS:
        data[viewer._section_field_name(section)] = json.dumps(
            config[section], indent=2, ensure_ascii=False
        )
    data.update(overrides)
    return urlencode(data).encode("utf-8")


def test_home_markdown_and_seven_category_exclusion(tmp_path: Path) -> None:
    _make_project(tmp_path)
    app = viewer.create_app(tmp_path, host_allowlist=("127.0.0.1",))

    status, headers, body = asyncio.run(
        _request(app, "GET", "/", headers={"Host": "127.0.0.1:8765"})
    )
    text = body.decode("utf-8")
    assert status == 200
    assert "Mission Directives Viewer" in text
    assert "site" not in text
    assert "state" not in text
    assert "set-cookie" in headers

    status, _, body = asyncio.run(
        _request(app, "GET", "/category/results", headers={"Host": "127.0.0.1:8765"})
    )
    text = body.decode("utf-8")
    assert status == 200
    assert text.index("summary.md") < text.index("old.txt")

    status, _, body = asyncio.run(
        _request(app, "GET", "/file/results/summary.md", headers={"Host": "127.0.0.1:8765"})
    )
    text = body.decode("utf-8")
    assert status == 200
    assert "/file/results/report.pdf" in text
    assert '/content/results/chart.png' in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert "<script>alert(1)</script>" not in text

    status, _, body = asyncio.run(
        _request(app, "GET", "/category/site", headers={"Host": "127.0.0.1:8765"})
    )
    assert status == 404
    assert body == b"Unknown category"


def test_project_site_template_and_static_override(tmp_path: Path) -> None:
    _make_project(tmp_path)
    template_dir = tmp_path / ".mission-directives" / "site" / "templates"
    static_dir = tmp_path / ".mission-directives" / "site" / "static"
    template_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    (template_dir / "base.html").write_text(
        "<html><body><div>project-template</div>$nav<main>$content</main></body></html>",
        encoding="utf-8",
    )
    (static_dir / "viewer.css").write_text("body{color:#123456;}", encoding="utf-8")

    app = viewer.create_app(tmp_path, host_allowlist=("127.0.0.1",))

    status, _, body = asyncio.run(
        _request(app, "GET", "/", headers={"Host": "127.0.0.1:8765"})
    )
    assert status == 200
    assert "project-template" in body.decode("utf-8")

    status, _, body = asyncio.run(
        _request(app, "GET", "/static/viewer.css", headers={"Host": "127.0.0.1:8765"})
    )
    assert status == 200
    assert body == b"body{color:#123456;}"


def test_settings_save_creates_backup_and_stale_revision_is_blocked(tmp_path: Path) -> None:
    _make_project(tmp_path)
    app = viewer.create_app(tmp_path, host_allowlist=("127.0.0.1",))

    status, headers, body = asyncio.run(
        _request(app, "GET", "/settings", headers={"Host": "127.0.0.1:8765"})
    )
    assert status == 200
    csrf_token = _csrf_from_headers(headers)
    current = project_config.load_project_config(tmp_path)

    status, _, body = asyncio.run(
        _request(
            app,
            "POST",
            "/settings",
            headers={
                "Host": "127.0.0.1:8765",
                "Origin": "http://127.0.0.1:8765",
                "Cookie": f"md_viewer_csrf={csrf_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body=_settings_form(
                current,
                csrf_token,
                section_project_json=json.dumps(
                    {**current["project"], "name": "Viewer Edited Project"},
                    indent=2,
                    ensure_ascii=False,
                ),
            ),
        )
    )
    text = body.decode("utf-8")
    assert status == 200
    assert "Project config saved." in text
    saved = project_config.load_project_config(tmp_path)
    assert saved["project"]["name"] == "Viewer Edited Project"
    assert saved["revision"] == 1
    backups = list(
        (tmp_path / ".mission-directives" / "state" / "config-backups").glob("*.json")
    )
    assert backups

    status, headers, _ = asyncio.run(
        _request(app, "GET", "/settings", headers={"Host": "127.0.0.1:8765"})
    )
    stale_token = _csrf_from_headers(headers)
    stale_current = project_config.load_project_config(tmp_path)
    project_config.save_project_config(
        tmp_path,
        {
            **stale_current,
            "project": {**stale_current["project"], "name": "External Change"},
        },
        expected_revision=stale_current["revision"],
    )

    status, _, body = asyncio.run(
        _request(
            app,
            "POST",
            "/settings",
            headers={
                "Host": "127.0.0.1:8765",
                "Origin": "http://127.0.0.1:8765",
                "Cookie": f"md_viewer_csrf={stale_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body=_settings_form(
                stale_current,
                stale_token,
                section_project_json=json.dumps(
                    {**stale_current["project"], "name": "Stale Write"},
                    indent=2,
                    ensure_ascii=False,
                ),
            ),
        )
    )
    text = body.decode("utf-8")
    assert status == 409
    assert "Refresh and retry" in text
    assert project_config.load_project_config(tmp_path)["project"]["name"] == "External Change"


def test_tracking_requires_confirmation_and_calls_update(tmp_path: Path, monkeypatch) -> None:
    _make_project(tmp_path)
    app = viewer.create_app(tmp_path, host_allowlist=("127.0.0.1",))
    calls: list[tuple[Path, str]] = []

    def fake_update_tracking(project: Path | str, mode: str):
        calls.append((Path(project), mode))
        config_path = Path(project) / ".mission-directives" / "config.json"
        payload = json.loads(config_path.read_text(encoding="utf-8"))
        payload["tracking_mode"] = mode
        config_path.write_text(json.dumps(payload), encoding="utf-8")
        return {"status": "updated", "tracking_mode": mode}

    monkeypatch.setattr(viewer.installer, "update_tracking", fake_update_tracking)

    status, headers, _ = asyncio.run(
        _request(app, "GET", "/settings", headers={"Host": "127.0.0.1:8765"})
    )
    assert status == 200
    csrf_token = _csrf_from_headers(headers)

    status, _, body = asyncio.run(
        _request(
            app,
            "POST",
            "/settings",
            headers={
                "Host": "127.0.0.1:8765",
                "Origin": "http://127.0.0.1:8765",
                "Cookie": f"md_viewer_csrf={csrf_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body=urlencode(
                {
                    "action": "update_tracking",
                    "csrf_token": csrf_token,
                    "tracking_mode": "outputs",
                }
            ).encode("utf-8"),
        )
    )
    assert status == 400
    assert "Confirm the tracking change" in body.decode("utf-8")
    assert calls == []

    status, _, body = asyncio.run(
        _request(
            app,
            "POST",
            "/settings",
            headers={
                "Host": "127.0.0.1:8765",
                "Origin": "http://127.0.0.1:8765",
                "Cookie": f"md_viewer_csrf={csrf_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body=urlencode(
                {
                    "action": "update_tracking",
                    "csrf_token": csrf_token,
                    "tracking_mode": "outputs",
                    "confirm_tracking": "yes",
                }
            ).encode("utf-8"),
        )
    )
    assert status == 200
    assert "Tracking mode updated to outputs." in body.decode("utf-8")
    assert calls == [(tmp_path, "outputs")]
