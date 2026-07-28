# Mission Directives

Mission Directives is a curated prompt and orchestration runtime for deterministic routing, pinned project context, and verifiable agent workflows.

## Install or run

Recommended persistent installation:

```bash
uv tool install mission-directives
```

Supported alternatives:

```bash
pipx install mission-directives
python -m pip install --user mission-directives
```

Run without persistent installation:

```bash
uvx mission-directives --help
```

After a pip installation, the module entry point is also available:

```bash
python -m mission_directives --help
```

## Quick start

```bash
mission-directives init --tracking ignored
mission-directives config validate
mission-directives route "MD advanced audit fix verify repository"
mission-directives view
```

An initialized project receives a pinned runtime and project workspace under `.mission-directives/`. Existing Markdown, reports, logs, and attachments remain unchanged and can be viewed through the local Uvicorn-based output viewer.

## Links

- [Homepage](https://manojpisini.github.io/mission-directives/index.html)
- [Documentation](https://manojpisini.github.io/mission-directives/docs.html)
- [Source](https://github.com/manojpisini/mission-directives)
- [Issues](https://github.com/manojpisini/mission-directives/issues)

## License

Licensed under either MIT or Apache-2.0, at your option.
