from __future__ import annotations

import html
import hmac
import inspect
import json
import mimetypes
import secrets
import socket
import threading
import time
import webbrowser
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from string import Template
from typing import Any
from urllib.parse import parse_qs, quote, urlsplit, urlunsplit

from markdown_it import MarkdownIt

from . import installer, project_config

SchemaHook = Callable[[Path, Any], str | None]
ShutdownHook = Callable[[], None | Awaitable[None]]

RUNTIME_DIR = ".mission-directives"
CATEGORY_DIRS = (
    "results",
    "reports",
    "artifacts",
    "plans",
    "outputs",
    "docs",
    "logs",
)
PROJECT_SITE_DIRNAME = "site"
PROJECT_STATE_DIRNAME = "state"
CONFIG_BACKUP_DIRNAME = "config-backups"
CONFIG_BACKUP_LIMIT = 10
INLINE_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
INLINE_AUDIO_SUFFIXES = {".aac", ".flac", ".m4a", ".mp3", ".oga", ".ogg", ".wav"}
INLINE_VIDEO_SUFFIXES = {".m4v", ".mov", ".mp4", ".ogv", ".webm"}
INLINE_DOCUMENT_SUFFIXES = {".pdf"}
TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".log",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
DEFAULT_ALLOWED_HOSTS = {"127.0.0.1", "localhost", "[::1]"}
MAX_TEXT_BYTES = 1_000_000
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]"}
CONFIG_JSON_SECTIONS = (
    "project",
    "goals",
    "scope",
    "stack",
    "paths",
    "commands",
    "constraints",
    "working_agreements",
    "current_state",
    "provenance",
    "extensions",
)


@dataclass(slots=True)
class Request:
    scope: Mapping[str, Any]
    method: str
    path: str
    headers: dict[str, str]
    query: dict[str, list[str]]
    body: bytes
    host: str

    @property
    def scheme(self) -> str:
        return str(self.scope.get("scheme", "http"))


@dataclass(slots=True)
class Response:
    status: int
    body: bytes
    content_type: str = "text/html; charset=utf-8"
    headers: list[tuple[str, str]] | None = None


@dataclass(slots=True)
class CategoryEntry:
    category: str
    path: Path
    relative_path: PurePosixPath
    size: int
    modified_at: float


class ViewerApp:
    def __init__(
        self,
        project_root: str | Path | None = None,
        *,
        allow_shutdown: bool = True,
        allowed_hosts: Sequence[str] | None = None,
        schema_hooks: Mapping[str, SchemaHook] | None = None,
        on_shutdown: ShutdownHook | None = None,
        template_root: str | Path | None = None,
        static_root: str | Path | None = None,
    ) -> None:
        self.project_root = Path(project_root or Path.cwd()).resolve()
        self.runtime_root = self.project_root / RUNTIME_DIR
        packaged_site = Path(__file__).resolve().parent / "site"
        project_site = self.runtime_root / PROJECT_SITE_DIRNAME

        self.template_root = Path(
            template_root
            or self._resolve_site_dir(project_site / "templates", packaged_site / "templates")
        )
        self.static_root = Path(
            static_root
            or self._resolve_site_dir(project_site / "static", packaged_site / "static")
        )
        self.allow_shutdown = allow_shutdown
        self.allowed_hosts = {
            _normalize_host(value)
            for value in (allowed_hosts or tuple(DEFAULT_ALLOWED_HOSTS))
            if _normalize_host(value)
        }
        self.schema_hooks = dict(schema_hooks or {})
        self.on_shutdown = on_shutdown
        self._csrf_secret = secrets.token_bytes(32)
        self._layout = Template(
            (self.template_root / "base.html").read_text(encoding="utf-8")
        )
        self._markdown = MarkdownIt("commonmark", {"html": False, "linkify": True})

    async def __call__(
        self,
        scope: Mapping[str, Any],
        receive: Callable[..., Any],
        send: Callable[..., Any],
    ) -> None:
        scope_type = scope.get("type")
        if scope_type == "lifespan":
            await self._handle_lifespan(receive, send)
            return
        if scope_type != "http":
            await self._send(
                send,
                Response(500, b"Unsupported ASGI scope", "text/plain; charset=utf-8"),
            )
            return

        request = await self._build_request(scope, receive)
        if not self._host_allowed(request.host):
            await self._send(send, self._plain(400, "Blocked host header"))
            return

        response = await self._dispatch(request)
        if request.method == "HEAD":
            response = Response(
                status=response.status,
                body=b"",
                content_type=response.content_type,
                headers=response.headers,
            )
        await self._send(send, response)

    async def _handle_lifespan(
        self, receive: Callable[..., Any], send: Callable[..., Any]
    ) -> None:
        while True:
            message = await receive()
            message_type = message.get("type")
            if message_type == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message_type == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    async def _build_request(
        self, scope: Mapping[str, Any], receive: Callable[..., Any]
    ) -> Request:
        body_parts: list[bytes] = []
        while True:
            message = await receive()
            if message.get("type") != "http.request":
                continue
            body_parts.append(message.get("body", b""))
            if not message.get("more_body", False):
                break

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        query = parse_qs(
            scope.get("query_string", b"").decode("latin-1"),
            keep_blank_values=True,
        )
        return Request(
            scope=scope,
            method=str(scope.get("method", "GET")).upper(),
            path=str(scope.get("path", "/")),
            headers=headers,
            query=query,
            body=b"".join(body_parts),
            host=headers.get("host", ""),
        )

    async def _dispatch(self, request: Request) -> Response:
        if request.method not in {"GET", "HEAD", "POST"}:
            return self._plain(
                405,
                "Method not allowed",
                [("Allow", "GET, HEAD, POST")],
            )

        path = request.path.rstrip("/") or "/"
        if path == "/":
            return self._html(request, "Viewer", self._render_home())
        if path == "/settings":
            if request.method == "POST":
                if not self._same_origin(request):
                    return self._plain(403, "Blocked cross-origin request")
                return await self._handle_settings_post(request)
            return self._html(
                request,
                "Settings",
                self._render_settings_page(
                    values=self._settings_form_values(self._load_project_config()),
                    tracking_mode=self._current_tracking_mode(),
                    host=request.host,
                ),
            )
        if path == "/shutdown":
            if request.method != "POST":
                return self._plain(
                    405,
                    "Method not allowed",
                    [("Allow", "POST")],
                )
            if not self._same_origin(request):
                return self._plain(403, "Blocked cross-origin request")
            return await self._handle_shutdown(request)
        if path.startswith("/category/") and request.method in {"GET", "HEAD"}:
            return self._handle_category(request, path)
        if path.startswith("/file/") and request.method in {"GET", "HEAD"}:
            return self._handle_file(request, path)
        if path.startswith("/download/") and request.method in {"GET", "HEAD"}:
            return self._handle_download(path)
        if path.startswith("/content/") and request.method in {"GET", "HEAD"}:
            return self._handle_content(path)
        if path.startswith("/static/") and request.method in {"GET", "HEAD"}:
            return self._handle_static(path)
        return self._plain(404, "Not found")

    def _render_home(self) -> str:
        rows: list[str] = []
        for category in CATEGORY_DIRS:
            entries = self._list_files(category)
            newest = _format_timestamp(entries[0].modified_at) if entries else "n/a"
            rows.append(
                "".join(
                    [
                        "<tr>",
                        f'<td><a href="{self._route("category", category)}">{html.escape(category)}</a></td>',
                        f"<td>{len(entries)}</td>",
                        f"<td>{html.escape(newest)}</td>",
                        f"<td>{html.escape((self.runtime_root / category).as_posix())}</td>",
                        "</tr>",
                    ]
                )
            )
        return "".join(
            [
                '<header class="page-head"><h1>Mission Directives Viewer</h1><p>Operational browser for local runtime outputs.</p></header>',
                '<section class="panel"><h2>Categories</h2><div class="table-wrap"><table class="listing"><thead><tr><th>Category</th><th>Files</th><th>Newest</th><th>Root</th></tr></thead><tbody>',
                "".join(rows),
                "</tbody></table></div></section>",
            ]
        )

    def _handle_category(self, request: Request, path: str) -> Response:
        category = path.removeprefix("/category/")
        if category not in CATEGORY_DIRS:
            return self._plain(404, "Unknown category")

        rows: list[str] = []
        for entry in self._list_files(category):
            rows.append(
                "".join(
                    [
                        "<tr>",
                        f'<td><a href="{self._route("file", category, entry.relative_path)}">{html.escape(entry.relative_path.as_posix())}</a></td>',
                        f"<td>{html.escape(_format_size(entry.size))}</td>",
                        f"<td>{html.escape(_format_timestamp(entry.modified_at))}</td>",
                        f'<td><a href="{self._route("download", category, entry.relative_path)}">download</a></td>',
                        "</tr>",
                    ]
                )
            )
        content = "".join(
            [
                f'<header class="page-head"><h1>{html.escape(category)}</h1><p>{html.escape((self.runtime_root / category).as_posix())}</p></header>',
                '<section class="panel"><div class="table-wrap"><table class="listing"><thead><tr><th>Path</th><th>Size</th><th>Modified</th><th>Action</th></tr></thead><tbody>',
                "".join(rows)
                or '<tr><td colspan="4" class="muted">No files found.</td></tr>',
                "</tbody></table></div></section>",
            ]
        )
        return self._html(request, category, content)

    def _handle_file(self, request: Request, path: str) -> Response:
        resolved = self._resolve_runtime_path(path, "/file/")
        if resolved is None:
            return self._plain(404, "Not found")
        category, rel_path, file_path = resolved
        if not file_path.is_file():
            return self._plain(404, "Not found")

        mime = mimetypes.guess_type(str(file_path))[0]
        stat = file_path.stat()
        content = "".join(
            [
                f'<header class="page-head"><h1>{html.escape(rel_path.as_posix())}</h1><p>{html.escape(category)}</p></header>',
                '<section class="panel"><dl class="meta">',
                f"<div><dt>Type</dt><dd>{html.escape(mime or 'application/octet-stream')}</dd></div>",
                f"<div><dt>Size</dt><dd>{html.escape(_format_size(stat.st_size))}</dd></div>",
                f"<div><dt>Modified</dt><dd>{html.escape(_format_timestamp(stat.st_mtime))}</dd></div>",
                "</dl>",
                '<div class="actions">',
                f'<a class="button-link" href="{self._route("download", category, rel_path)}">Download</a>',
                f'<a class="button-link" href="{self._route("content", category, rel_path)}">Open raw</a>',
                "</div></section>",
                self._render_file_body(category, rel_path, file_path, mime),
            ]
        )
        return self._html(request, rel_path.name, content)

    def _render_file_body(
        self,
        category: str,
        rel_path: PurePosixPath,
        file_path: Path,
        mime: str | None,
    ) -> str:
        suffix = file_path.suffix.lower()
        raw_url = self._route("content", category, rel_path)
        if suffix == ".md":
            text, truncated = _read_text(file_path)
            rendered = self._render_markdown(text, category, rel_path)
            note = "<p class=\"muted\">Preview truncated.</p>" if truncated else ""
            return f'<section class="panel">{note}<article class="markdown">{rendered}</article></section>'
        if suffix == ".json":
            text, truncated = _read_text(file_path)
            note = "<p class=\"muted\">Preview truncated.</p>" if truncated else ""
            return f'<section class="panel">{note}<pre>{html.escape(_pretty_json(text))}</pre></section>'
        if suffix in INLINE_IMAGE_SUFFIXES and (mime or "").startswith("image/"):
            return f'<section class="panel"><figure class="media-frame"><img alt="{html.escape(rel_path.name)}" src="{raw_url}"></figure></section>'
        if suffix in INLINE_DOCUMENT_SUFFIXES or mime == "application/pdf":
            return "".join(
                [
                    '<section class="panel">',
                    f'<object class="document-frame" data="{raw_url}" type="application/pdf">',
                    f'<p>Inline PDF preview unavailable. <a href="{self._route("download", category, rel_path)}">Download the file</a>.</p>',
                    "</object>",
                    "</section>",
                ]
            )
        if suffix in INLINE_AUDIO_SUFFIXES or (mime or "").startswith("audio/"):
            return f'<section class="panel"><audio controls preload="metadata" src="{raw_url}"></audio></section>'
        if suffix in INLINE_VIDEO_SUFFIXES or (mime or "").startswith("video/"):
            return f'<section class="panel"><video controls preload="metadata" src="{raw_url}"></video></section>'
        if suffix in TEXT_SUFFIXES or (mime or "").startswith("text/"):
            text, truncated = _read_text(file_path)
            note = "<p class=\"muted\">Preview truncated.</p>" if truncated else ""
            return f'<section class="panel">{note}<pre>{html.escape(text)}</pre></section>'
        return '<section class="panel"><p class="muted">Binary preview disabled. Use Download or Open raw.</p></section>'

    def _handle_download(self, path: str) -> Response:
        return self._serve_runtime_file(path, "/download/", attachment=True)

    def _handle_content(self, path: str) -> Response:
        return self._serve_runtime_file(path, "/content/", attachment=False)

    def _serve_runtime_file(
        self, path: str, prefix: str, *, attachment: bool
    ) -> Response:
        resolved = self._resolve_runtime_path(path, prefix)
        if resolved is None:
            return self._plain(404, "Not found")
        _, rel_path, file_path = resolved
        if not file_path.is_file():
            return self._plain(404, "Not found")
        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        headers = [
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
        ]
        disposition = "attachment" if attachment else "inline"
        headers.append(
            (
                "Content-Disposition",
                f'{disposition}; filename="{_quoted_filename(rel_path.name)}"',
            )
        )
        return Response(200, file_path.read_bytes(), mime, headers)

    def _handle_static(self, path: str) -> Response:
        relative = path.removeprefix("/static/")
        target = _safe_join(self.static_root, relative)
        if target is None or not target.is_file():
            return self._plain(404, "Not found")
        mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        return Response(
            200,
            target.read_bytes(),
            mime,
            [("Cache-Control", "public, max-age=300"), ("X-Content-Type-Options", "nosniff")],
        )

    async def _handle_settings_post(self, request: Request) -> Response:
        form = parse_qs(request.body.decode("utf-8"), keep_blank_values=True)
        csrf_error = self._validate_csrf(request, form)
        if csrf_error is not None:
            return self._plain(403, csrf_error)
        action = form.get("action", [""])[0]
        if action == "save_config":
            status, messages, values = self._save_project_config(form)
        elif action == "update_tracking":
            status, messages, values = self._update_tracking(form)
        else:
            status = 400
            messages = [("error", "Unknown settings action.")]
            values = self._settings_form_values(self._load_project_config())
        content = self._render_settings_page(
            values=values,
            tracking_mode=self._current_tracking_mode(),
            host=request.host,
            messages=messages,
        )
        return self._html(request, "Settings", content, status=status)

    def _save_project_config(
        self, form: Mapping[str, list[str]]
    ) -> tuple[int, list[tuple[str, str]], dict[str, str]]:
        current = self._load_project_config()
        values = self._settings_values_from_form(form, current)
        try:
            expected_revision = int(values["revision"])
        except ValueError:
            return 400, [("error", "Revision must be an integer.")], values

        if expected_revision != int(current["revision"]):
            fresh = self._settings_form_values(self._load_project_config())
            return (
                409,
                [("error", "Project config changed since this page loaded. Refresh and retry.")],
                fresh,
            )

        candidate: dict[str, Any] = {
            "schema_version": values["schema_version"],
            "revision": expected_revision,
        }
        for section in CONFIG_JSON_SECTIONS:
            field_name = _section_field_name(section)
            try:
                candidate[section] = json.loads(values[field_name] or "{}")
            except json.JSONDecodeError as exc:
                label = section.replace("_", " ")
                return (
                    400,
                    [("error", f"{label.title()} JSON is invalid: {exc.msg}.")],
                    values,
                )

        try:
            validated = project_config.validate_project_config(
                candidate,
                project_root=self.project_root,
            )
        except project_config.ProjectConfigError as exc:
            return 400, [("error", str(exc))], values

        self._backup_project_config()
        try:
            saved = project_config.save_project_config(
                self.project_root,
                validated,
                expected_revision=expected_revision,
            )
        except project_config.StaleProjectConfigError as exc:
            fresh = self._settings_form_values(self._load_project_config())
            return 409, [("error", str(exc))], fresh
        except project_config.ProjectConfigError as exc:
            return 400, [("error", str(exc))], values

        return (
            200,
            [("success", "Project config saved.")],
            self._settings_form_values(saved),
        )

    def _update_tracking(
        self, form: Mapping[str, list[str]]
    ) -> tuple[int, list[tuple[str, str]], dict[str, str]]:
        values = self._settings_form_values(self._load_project_config())
        selected = form.get("tracking_mode", [""])[0]
        if selected not in installer.TRACKING_MODES:
            return 400, [("error", "Tracking mode is invalid.")], values
        if selected == self._current_tracking_mode():
            return 200, [("success", "Tracking mode unchanged.")], values
        if form.get("confirm_tracking", [""])[0] != "yes":
            return (
                400,
                [("error", "Confirm the tracking change before updating.")],
                values,
            )
        try:
            result = installer.update_tracking(self.project_root, selected)
        except Exception as exc:
            return 400, [("error", str(exc))], values
        return (
            200,
            [("success", f"Tracking mode updated to {result['tracking_mode']}.")],
            values,
        )

    def _render_settings_page(
        self,
        *,
        values: Mapping[str, str],
        tracking_mode: str,
        host: str,
        messages: Sequence[tuple[str, str]] | None = None,
    ) -> str:
        notice_html = []
        for level, message in messages or ():
            notice_html.append(
                f'<div class="notice notice--{html.escape(level)}">{html.escape(message)}</div>'
            )
        config_hook = self._render_hook(
            "project.json",
            project_config.project_config_path(self.project_root),
            self._load_project_config(),
        )
        return "".join(
            [
                '<header class="page-head"><h1>Project Config</h1><p>Edit the local project config and tracking mode.</p></header>',
                "".join(notice_html),
                '<section class="panel"><h2>Project config</h2>',
                '<form action="/settings" class="form-grid" method="post">',
                f'<input type="hidden" name="csrf_token" value="{html.escape(self._csrf_token(host))}">',
                '<input type="hidden" name="action" value="save_config">',
                self._field_input("Schema version", "schema_version", values["schema_version"], readonly=True),
                self._field_input("Revision", "revision", values["revision"], readonly=True),
                self._field_input("Project root", "project_root_display", self.project_root.as_posix(), readonly=True),
                "".join(
                    self._field_textarea(
                        section.replace("_", " ").title(),
                        _section_field_name(section),
                        values[_section_field_name(section)],
                        f"JSON for the {section.replace('_', ' ')} section.",
                        rows=12 if section in {"project", "extensions"} else 8,
                    )
                    for section in CONFIG_JSON_SECTIONS
                ),
                '<div class="form-actions"><button type="submit">Save project config</button></div>',
                "</form>",
                config_hook,
                "</section>",
                '<section class="panel"><h2>Tracking mode</h2>',
                '<form action="/settings" class="form-grid" method="post">',
                f'<input type="hidden" name="csrf_token" value="{html.escape(self._csrf_token(host))}">',
                '<input type="hidden" name="action" value="update_tracking">',
                self._field_select(
                    "Tracking mode",
                    "tracking_mode",
                    tracking_mode,
                    installer.TRACKING_MODES,
                ),
                '<label class="field checkbox-field"><span>Confirmation</span><span><input name="confirm_tracking" type="checkbox" value="yes"> I understand this updates .gitignore and runtime tracking.</span></label>',
                '<div class="form-actions"><button type="submit">Update tracking</button></div>',
                "</form></section>",
                self._render_shutdown_panel(host),
            ]
        )

    def _render_shutdown_panel(self, host: str) -> str:
        if not self.allow_shutdown:
            return ""
        return "".join(
            [
                '<section class="panel"><h2>Shutdown</h2><form action="/shutdown" method="post">',
                f'<input type="hidden" name="csrf_token" value="{html.escape(self._csrf_token(host))}">',
                '<div class="form-actions"><button type="submit">Stop viewer</button></div>',
                "</form></section>",
            ]
        )

    def _field_input(
        self, label: str, name: str, value: str, *, readonly: bool = False
    ) -> str:
        readonly_attr = " readonly" if readonly else ""
        return (
            f'<label class="field"><span>{html.escape(label)}</span>'
            f'<input name="{html.escape(name)}" type="text" value="{html.escape(value)}"{readonly_attr}></label>'
        )

    def _field_textarea(
        self,
        label: str,
        name: str,
        value: str,
        hint: str,
        *,
        rows: int = 5,
    ) -> str:
        return (
            f'<label class="field field--wide"><span>{html.escape(label)}</span>'
            f'<textarea name="{html.escape(name)}" rows="{rows}">{html.escape(value)}</textarea>'
            f'<small>{html.escape(hint)}</small></label>'
        )

    def _field_select(
        self,
        label: str,
        name: str,
        selected: str,
        options: Sequence[str],
    ) -> str:
        rendered = []
        for option in options:
            selected_attr = " selected" if option == selected else ""
            rendered.append(
                f'<option value="{html.escape(option)}"{selected_attr}>{html.escape(option)}</option>'
            )
        return (
            f'<label class="field"><span>{html.escape(label)}</span>'
            f'<select name="{html.escape(name)}">{"".join(rendered)}</select></label>'
        )

    async def _handle_shutdown(self, request: Request) -> Response:
        if not self.allow_shutdown:
            return self._plain(403, "Shutdown disabled")
        form = parse_qs(request.body.decode("utf-8"), keep_blank_values=True)
        csrf_error = self._validate_csrf(request, form)
        if csrf_error is not None:
            return self._plain(403, csrf_error)

        if self.on_shutdown is not None:
            result = self.on_shutdown()
            if inspect.isawaitable(result):
                await result
        return self._plain(202, "Shutdown requested")

    def _validate_csrf(
        self, request: Request, form: Mapping[str, list[str]]
    ) -> str | None:
        form_token = form.get("csrf_token", [""])[0]
        cookie_token = _parse_cookie(request.headers.get("cookie", "")).get(
            "md_viewer_csrf", ""
        )
        expected = self._csrf_token(request.host)
        if not (form_token and cookie_token):
            return "Missing CSRF token"
        if not (
            hmac.compare_digest(form_token, cookie_token)
            and hmac.compare_digest(form_token, expected)
        ):
            return "Invalid CSRF token"
        return None

    def _resolve_runtime_path(
        self, path: str, prefix: str
    ) -> tuple[str, PurePosixPath, Path] | None:
        relative = path.removeprefix(prefix)
        pieces = [piece for piece in relative.split("/") if piece]
        if len(pieces) < 2:
            return None
        category = pieces[0]
        if category not in CATEGORY_DIRS:
            return None
        rel_path = PurePosixPath(*pieces[1:])
        if any(part in {"", ".."} for part in rel_path.parts):
            return None
        root = self.runtime_root / category
        target = _safe_join(root, rel_path.as_posix())
        if target is None:
            return None
        return category, rel_path, target

    def _render_hook(self, hook_key: str, path: Path, data: Any) -> str:
        hook = self.schema_hooks.get(hook_key)
        if hook is None:
            return ""
        return hook(path, data) or ""

    def _html(
        self, request: Request, title: str, content: str, *, status: int = 200
    ) -> Response:
        body = self._layout.safe_substitute(
            title=html.escape(title),
            content=content,
            nav=self._render_nav(),
        ).encode("utf-8")
        headers = [
            ("Cache-Control", "no-store"),
            (
                "Content-Security-Policy",
                "default-src 'self'; img-src 'self' data:; media-src 'self'; object-src 'self'; style-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            ),
            ("Referrer-Policy", "no-referrer"),
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            (
                "Set-Cookie",
                f"md_viewer_csrf={self._csrf_token(request.host)}; Path=/; HttpOnly; SameSite=Strict",
            ),
        ]
        return Response(status, body, headers=headers)

    def _render_nav(self) -> str:
        links = ['<a href="/">Home</a>', '<a href="/settings">Settings</a>']
        links.extend(
            f'<a href="{self._route("category", category)}">{html.escape(category)}</a>'
            for category in CATEGORY_DIRS
        )
        return "".join(links)

    def _plain(
        self,
        status: int,
        message: str,
        headers: list[tuple[str, str]] | None = None,
    ) -> Response:
        body = message.encode("utf-8")
        default_headers = [
            ("Cache-Control", "no-store"),
            (
                "Content-Security-Policy",
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
            ),
            ("X-Content-Type-Options", "nosniff"),
        ]
        if headers:
            default_headers.extend(headers)
        return Response(status, body, "text/plain; charset=utf-8", default_headers)

    async def _send(self, send: Callable[..., Any], response: Response) -> None:
        headers = [
            (b"content-type", response.content_type.encode("latin-1")),
            (b"content-length", str(len(response.body)).encode("ascii")),
        ]
        for key, value in response.headers or []:
            headers.append((key.encode("latin-1"), value.encode("latin-1")))
        await send(
            {"type": "http.response.start", "status": response.status, "headers": headers}
        )
        await send({"type": "http.response.body", "body": response.body})

    def _list_files(self, category: str) -> list[CategoryEntry]:
        root = self.runtime_root / category
        if not root.exists():
            return []
        entries: list[CategoryEntry] = []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            stat = path.stat()
            entries.append(
                CategoryEntry(
                    category=category,
                    path=path,
                    relative_path=PurePosixPath(path.relative_to(root).as_posix()),
                    size=stat.st_size,
                    modified_at=stat.st_mtime,
                )
            )
        entries.sort(key=lambda item: (-item.modified_at, item.relative_path.as_posix()))
        return entries

    def _csrf_token(self, host: str) -> str:
        host_value = host or "localhost"
        return hmac.new(
            self._csrf_secret,
            host_value.encode("utf-8"),
            "sha256",
        ).hexdigest()

    def _host_allowed(self, host: str) -> bool:
        normalized = _normalize_host(host)
        return bool(normalized and normalized in self.allowed_hosts)

    def _same_origin(self, request: Request) -> bool:
        origin = request.headers.get("origin", "")
        if not origin:
            return False
        parsed = urlsplit(origin)
        return (
            parsed.scheme == request.scheme
            and parsed.netloc.lower() == request.host.lower()
            and self._host_allowed(request.host)
        )

    def _route(
        self,
        prefix: str,
        category: str | None = None,
        rel_path: PurePosixPath | None = None,
    ) -> str:
        pieces = [prefix]
        if category is not None:
            pieces.append(quote(category, safe=""))
        if rel_path is not None:
            pieces.extend(quote(part, safe="") for part in rel_path.parts)
        return "/" + "/".join(pieces)

    def _load_project_config(self) -> dict[str, Any]:
        try:
            return project_config.load_project_config(self.project_root)
        except project_config.ProjectConfigNotFoundError:
            return project_config.seed_project_config(self.project_root)

    def _current_tracking_mode(self) -> str:
        system_config = self._load_system_config()
        tracking = system_config.get("tracking_mode", "ignored")
        return tracking if tracking in installer.TRACKING_MODES else "ignored"

    def _load_system_config(self) -> dict[str, Any]:
        path = self.runtime_root / "config.json"
        if not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _settings_form_values(self, config: Mapping[str, Any]) -> dict[str, str]:
        values = {
            "schema_version": str(config.get("schema_version", "")),
            "revision": str(config.get("revision", "")),
        }
        for section in CONFIG_JSON_SECTIONS:
            values[_section_field_name(section)] = json.dumps(
                config.get(section, {}),
                indent=2,
                ensure_ascii=False,
            )
        return values

    def _settings_values_from_form(
        self, form: Mapping[str, list[str]], current: Mapping[str, Any]
    ) -> dict[str, str]:
        values = self._settings_form_values(current)
        for key in (
            "schema_version",
            "revision",
        ):
            values[key] = form.get(key, [values[key]])[0]
        for section in CONFIG_JSON_SECTIONS:
            field_name = _section_field_name(section)
            values[field_name] = form.get(field_name, [values[field_name]])[0]
        return values

    def _backup_project_config(self) -> None:
        source = project_config.project_config_path(self.project_root)
        if not source.is_file():
            return
        backup_root = (
            self.runtime_root / PROJECT_STATE_DIRNAME / CONFIG_BACKUP_DIRNAME
        )
        backup_root.mkdir(parents=True, exist_ok=True)
        revision = self._load_project_config()["revision"]
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup_path = backup_root / f"project-r{int(revision):04d}-{stamp}.json"
        backup_path.write_bytes(source.read_bytes())
        backups = sorted(
            backup_root.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        for extra in backups[CONFIG_BACKUP_LIMIT:]:
            extra.unlink(missing_ok=True)

    def _render_markdown(
        self, text: str, category: str, rel_path: PurePosixPath
    ) -> str:
        env = {"category": category, "rel_path": rel_path}
        tokens = self._markdown.parse(text, env)
        self._rewrite_markdown_tokens(tokens, category, rel_path)
        return self._markdown.renderer.render(tokens, self._markdown.options, env)

    def _rewrite_markdown_tokens(
        self, tokens: Sequence[Any], category: str, rel_path: PurePosixPath
    ) -> None:
        for token in tokens:
            if token.type == "link_open":
                href = token.attrGet("href")
                if href:
                    token.attrSet("href", self._rewrite_markdown_url(href, category, rel_path))
            if token.type == "image":
                src = token.attrGet("src")
                if src:
                    token.attrSet(
                        "src",
                        self._rewrite_markdown_url(
                            src,
                            category,
                            rel_path,
                            image=True,
                        ),
                    )
            children = getattr(token, "children", None)
            if children:
                self._rewrite_markdown_tokens(children, category, rel_path)

    def _rewrite_markdown_url(
        self,
        target: str,
        category: str,
        rel_path: PurePosixPath,
        *,
        image: bool = False,
    ) -> str:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return target

        resolved = _resolve_markdown_relative(rel_path.parent, parsed.path)
        if resolved is None:
            return target
        target_path = _safe_join((self.runtime_root / category), resolved.as_posix())
        if target_path is None:
            return target
        suffix = target_path.suffix.lower()
        if image:
            route = self._route("content", category, resolved)
        elif suffix == ".md" or suffix in TEXT_SUFFIXES:
            route = self._route("file", category, resolved)
        elif suffix in INLINE_DOCUMENT_SUFFIXES or suffix in INLINE_AUDIO_SUFFIXES or suffix in INLINE_VIDEO_SUFFIXES:
            route = self._route("file", category, resolved)
        else:
            route = self._route("download", category, resolved)
        return urlunsplit(("", "", route, "", parsed.fragment))

    def _resolve_site_dir(self, preferred: Path, fallback: Path) -> Path:
        return preferred if preferred.is_dir() else fallback


def create_app(
    project_root: str | Path | None = None,
    *,
    allow_shutdown: bool = True,
    host_allowlist: Sequence[str] | None = None,
    schema_hooks: Mapping[str, SchemaHook] | None = None,
    on_shutdown: ShutdownHook | None = None,
) -> ViewerApp:
    return ViewerApp(
        project_root,
        allow_shutdown=allow_shutdown,
        allowed_hosts=host_allowlist,
        schema_hooks=schema_hooks,
        on_shutdown=on_shutdown,
    )


def run_viewer(
    project_root: str | Path | None = None,
    *,
    host: str = "127.0.0.1",
    port: int | None = 8765,
    allow_shutdown: bool = True,
    host_allowlist: Sequence[str] | None = None,
    schema_hooks: Mapping[str, SchemaHook] | None = None,
    open_browser: bool = True,
    open_path: str = "/",
    **uvicorn_kwargs: Any,
) -> int | bool:
    if uvicorn_kwargs.get("reload"):
        raise ValueError("run_viewer does not support reload; use uvicorn directly.")
    normalized_host = _normalize_loopback_host(host)
    if normalized_host not in {"127.0.0.1", "::1"}:
        raise ValueError("run_viewer binds loopback hosts only.")
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - runtime boundary
        raise RuntimeError("uvicorn is required to run the local viewer.") from exc

    requested_port = 0 if port in (None, 0) else int(port)
    app_holder: dict[str, Any] = {}

    def request_shutdown() -> None:
        server = app_holder.get("server")
        if server is not None:
            server.should_exit = True

    app = create_app(
        project_root,
        allow_shutdown=allow_shutdown,
        host_allowlist=host_allowlist or ("127.0.0.1", "localhost", "[::1]"),
        schema_hooks=schema_hooks,
        on_shutdown=request_shutdown,
    )
    config = uvicorn.Config(app, host=normalized_host, port=requested_port, **uvicorn_kwargs)
    server = uvicorn.Server(config)
    app_holder["server"] = server
    sock = _bind_loopback_socket(normalized_host, requested_port)
    actual_port = sock.getsockname()[1]
    viewer_url = f"http://127.0.0.1:{actual_port}{_normalize_open_path(open_path)}"
    print(f"Mission Directives viewer: {viewer_url}", flush=True)
    if open_browser:
        _open_browser_when_ready(server, viewer_url)
    try:
        result = server.run(sockets=[sock])
    finally:
        sock.close()
    if isinstance(result, bool):
        return result
    return 0 if getattr(server, "started", False) or getattr(server, "should_exit", False) else 1


def _bind_loopback_socket(host: str, port: int) -> socket.socket:
    family = socket.AF_INET6 if host == "::1" else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if family == socket.AF_INET6:
        sock.bind(("::1", port))
    else:
        sock.bind(("127.0.0.1", port))
    sock.listen(socket.SOMAXCONN)
    return sock


def _open_browser_when_ready(server: Any, url: str) -> None:
    def opener() -> None:
        for _ in range(200):
            if getattr(server, "started", False):
                webbrowser.open(url)
                return
            time.sleep(0.05)

    thread = threading.Thread(target=opener, daemon=True)
    thread.start()


def _normalize_open_path(path: str) -> str:
    if not path:
        return "/"
    return path if path.startswith("/") else f"/{path}"


def _normalize_host(value: str) -> str:
    if not value:
        return ""
    candidate = value.strip().lower()
    if candidate.startswith("["):
        end = candidate.find("]")
        return candidate[: end + 1] if end != -1 else candidate
    if ":" in candidate:
        return candidate.rsplit(":", 1)[0]
    return candidate


def _normalize_loopback_host(value: str) -> str:
    normalized = _normalize_host(value)
    if normalized not in LOOPBACK_HOSTS:
        return normalized
    if normalized in {"localhost", "127.0.0.1"}:
        return "127.0.0.1"
    return "::1"


def _section_field_name(section: str) -> str:
    return f"section_{section}_json"


def _safe_join(root: Path, relative: str) -> Path | None:
    rel_path = PurePosixPath(relative)
    if any(part in {"", ".."} for part in rel_path.parts):
        return None
    try:
        root_resolved = root.resolve(strict=False)
        target = root.joinpath(*rel_path.parts).resolve(strict=False)
        target.relative_to(root_resolved)
    except (OSError, ValueError):
        return None
    return target


def _parse_cookie(header: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for chunk in header.split(";"):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _read_text(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    truncated = len(data) > MAX_TEXT_BYTES
    if truncated:
        data = data[:MAX_TEXT_BYTES]
    return data.decode("utf-8", errors="replace"), truncated


def _split_lines(value: str) -> list[str]:
    return [item.strip() for item in value.splitlines() if item.strip()]


def _pretty_json(text: str) -> str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _format_size(size: int) -> str:
    value = float(size)
    units = ["B", "KB", "MB", "GB"]
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _quoted_filename(name: str) -> str:
    return name.replace("\\", "_").replace('"', "_")


def _resolve_markdown_relative(
    base: PurePosixPath, target: str
) -> PurePosixPath | None:
    parts: list[str] = []
    raw = PurePosixPath(base, target)
    for part in raw.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    if not parts:
        return None
    return PurePosixPath(*parts)


__all__ = ["SchemaHook", "ViewerApp", "create_app", "run_viewer"]
