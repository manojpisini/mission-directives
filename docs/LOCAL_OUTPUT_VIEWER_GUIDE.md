# Local Output Viewer Guide

## Purpose

The local viewer is a visual wrapper over existing generated files. It does not rename, rewrite, index, or duplicate outputs. The installed templates and CSS live in `.mission-directives/site` and are independent from the repository Astro documentation site.

## Start and stop

```bash
mission-directives view
mission-directives view --port 8765 --no-open
```

The server binds only to loopback. With no port, it selects an available local port and opens the browser. Use the POST-only Shutdown control in the site; restart from any project subdirectory by running `mission-directives view` again.

`mission-directives config open` starts the same viewer on Settings.

## Content

The home page links exactly seven categories: `results`, `reports`, `artifacts`, `plans`, `outputs`, `docs`, and `logs`. Files are scanned on request and sorted newest first.

- Markdown renders as articles with raw HTML disabled.
- JSON is pretty-printed; YAML, TOML, CSV, text, and logs use escaped text previews.
- Images, PDF, audio, and video use native browser rendering.
- Unknown or binary formats remain downloadable attachments.
- Relative Markdown links resolve only within the current allowed category root.

## Settings

Project Config is the only editable artifact surface. Saves require a matching revision and CSRF token, validate against the schema, replace the file atomically, and create bounded backups. Tracking-mode changes require separate confirmation because they update the managed `.gitignore` block.

## Security boundary

The viewer enforces loopback binding, Host and Origin checks, per-process CSRF tokens, restrictive content security headers, escaped template values, raw-HTML-disabled Markdown, MIME controls, and path and symlink containment. It is a local single-user tool; LAN hosting and account authentication are intentionally unsupported.
