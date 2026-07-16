# Installed Skills Inventory Guide

## Purpose

`installed_skills_inventory.json` records a snapshot of skills detected in the user's OpenCode global skill directory. The supplied snapshot was normalized from the OpenCode global skill directory and is distributed using the portable logical location:

```text
${MD_OPENCODE_SKILLS_DIR}
```

At runtime this resolves through `compatibility/agent_skill_paths.json` for Windows, Linux, or macOS. The distributable inventory never records a personal home-directory path.

The snapshot contains 193 skill directories, all represented in the suite registry with explicit routing or exclusion status. Presence on disk means **available for inspection**. It does not by itself mean:

- trusted;
- source-pinned;
- conformant;
- compatible with the current runtime;
- safe for automatic selection;
- authorized for the current task.

## Inventory, registry, and lockfile

These files have different responsibilities:

| File | Meaning |
|---|---|
| `installed_skills_inventory.json` | What was observed on disk in the supplied snapshot. |
| `installed_skills_inventory.runtime.json` | A fresh filesystem scan generated on the current machine. |
| `skill_registry.json` | Skills with explicit MD metadata, routes, maturity, and verification policy. |
| `skill_aliases.json` | Canonical spelling and compatibility aliases. |
| `skills.lock.json` | Exact external-source revision and content lock state for installable third-party skills. |
| `evaluations/skill_conformance/` | Expected adapter behavior and live conformance status. |

A newly observed runtime skill can be installed but unmapped until the next inventory synchronization; the supplied snapshot is fully registered. It can be mapped but blocked by an unresolved lock. It can be local and approved but still require task-level output verification.

## Runtime statuses

`tools/md.py` can return:

- `usable_local` — approved user-owned local skill detected in the inventory;
- `usable` — curated third-party skill with acceptable maturity and resolved lock;
- `native_alias` — runtime capability that does not depend on an external install command;
- `installed_unmapped` — detected on disk but not curated; explicit runtime probing is required;
- `installed_review_required` — curated entry detected locally, but source lock or promotion is incomplete;
- `blocked_pending_lock_or_review` — known skill unavailable for automatic use;
- `local_missing_or_review_required` — local registry entry not confirmed as approved and present;
- `unknown` — not detected and not registered.

## Personal skills

### `visual-assets`

Registered as a first-class user-owned local skill. It is routed for code-native vector, illustration, infographic, presentation, report, and explanatory-visual work. Output remains quarantined until target-specific verification passes.

### `strudel`

Registered as a first-class user-owned local skill for Strudel music code. The spelling `strudle` resolves to `strudel` through `skill_aliases.json`.

## Refreshing the inventory

Scan all supported global locations:

```bash
python tools/sync_installed_skills.py
```

Default logical locations:

```text
${MD_AGENTS_SKILLS_DIR}
${MD_CLAUDE_SKILLS_DIR}
${MD_OPENCODE_SKILLS_DIR}
```

They resolve to `%USERPROFILE%`-relative paths on Windows, `$HOME`/XDG-relative paths on Linux and macOS, or explicit environment overrides.

The command writes `installed_skills_inventory.runtime.json`. It does not automatically promote, trust, or register newly detected skills.

Custom locations should be supplied through portable environment overrides:

```text
MD_AGENTS_SKILLS_DIR
MD_CLAUDE_SKILLS_DIR
MD_OPENCODE_SKILLS_DIR
```

Use `python tools/agent_paths.py all --logical` to inspect the logical locations and `python tools/agent_paths.py all --platform <windows|linux|macos>` to inspect platform defaults.

## Multi-application global installation

Use the governed installer only after qualification and approval. The historical `*_dual` filenames are retained as compatibility aliases, but installation verifies `.agents`, Claude Code, and OpenCode destinations:

```powershell
.\tools\install_skill_dual.ps1 \
  -Source "https://github.com/OWNER/REPOSITORY" \
  -SkillId "exact-skill-id" \
  -AcquisitionMode approved_unpinned
```

`approved_unpinned` is an explicit risk acceptance. The default `locked_auto` mode reads `skills.lock.json`, requires a resolved approved commit, and installs from that pinned revision.

## Installed but unmapped skill flow

When a user requests an installed skill that is not curated:

1. canonicalize the requested ID through `skill_aliases.json`;
2. confirm that the directory and `SKILL.md` exist;
3. run `MD-192` to establish genuine task fit;
4. inspect schema, permissions, provenance, tools, network access, output shape, and side effects;
5. route conditionally through `MD-196`;
6. quarantine output;
7. record conformance evidence;
8. promote to the registry only after repeated justified use and review.

Do not route such a skill to `find-skills`; it is already present. Discovery is for a genuinely missing capability.

## Image-generation exclusion

The supplied inventory includes skills whose names indicate model image generation. Those entries remain visible in the inventory but are marked excluded from automatic MD routing because this suite's visual-production path is code-native. `visual-assets`, SVG/HTML diagrams, frontend artifacts, and presentation assets remain supported.

## Review and maintenance

Periodically:

- compare all supported global directories;
- detect missing or divergent copies;
- review changed `SKILL.md` files;
- resolve or update source locks;
- rerun conformance fixtures;
- quarantine unexpected permission growth;
- remove deprecated or unused duplicate skills;
- update aliases only when canonical identity is unambiguous.
