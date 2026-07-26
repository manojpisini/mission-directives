---
title: Quick Start
description: Install, route, inspect, and dry-run Mission Directives in a few commands.
---

Mission Directives maps natural-language outcomes to stable prompt capabilities and bounded scenario graphs. Start with the full request, not a guessed prompt ID.

## Requirements

- Python 3.10 or newer.
- `jsonschema`, installed from `requirements-runtime.txt` for an installed runtime.
- A shell that can invoke Python.
- Node.js 24 only when developing this documentation site.

## Route from the repository

```powershell
python tools/md.py route "audit the repository, fix confirmed defects, and verify the result"
```

Read these fields first:

| Field | Meaning |
| --- | --- |
| `status` | `selected` or `no_confident_match` |
| `selection.targets` | Exact prompt, scenario, pack, or graph IDs |
| `selection.reason` | Why the router chose this surface |
| `query_analysis` | Corrected tokens, concepts, and typo corrections |
| `candidates` | Ranked alternatives with score evidence |

Inspect the winner before execution:

```powershell
python tools/md.py explain C-108
python tools/md.py plan C-108 --mode AUDIT_ONLY --root . --dry-run
```

## Install into a working project

```powershell
python tools/install.py D:\path\to\project
python D:\path\to\project\prompts\tools\md.py route "MD cleanup dead code safely"
```

The installer copies the declared runtime payload into `<project>/prompts`. It does not copy tests, evaluations, imports, CI, or this website.

## Route through an agent

Use the standalone `MD` keyword and preserve the complete outcome:

```text
MD review the authentication change for attack paths, patch confirmed findings,
run targeted tests, and report residual risk
```

Use an exact ID only when you intentionally want that contract:

```text
MD-37 audit the repository security posture in AUDIT_ONLY mode
```

:::tip
Run `lookup` when learning the catalog, `route` when selecting an owner, `compare` when two routes are close, and `explain` before execution.
:::
