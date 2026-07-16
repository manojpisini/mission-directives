# Root Agent Guidance and MD Keyword Routing Guide

## Purpose

This guide explains how to connect a project repository's root agent-instruction files to the Mission Directives without copying prompt bodies into those files or overwriting human-authored instructions.

The synchronization layer deliberately manages only:

- `AGENTS.md`
- `CLAUDE.md`

`CODEX.md`, `PI.md`, `HERMES.md`, `OPENCODE.md`, `GEMINI.md`, `QWEN.md`, `CURSOR.md`, `WINDSURF.md`, `COPILOT.md`, and custom filenames are intentionally excluded. This narrow scope prevents the suite from creating redundant or conflicting instruction surfaces.

The inserted section teaches an agent where MD lives, how to search it, which files are authoritative, when to invoke conditional auto-prompts, and how to avoid loading unnecessary prompts or skills.

## Design principles

### Preserve repository-owned instructions

The synchronizer owns only the text between:

```html
<!-- BEGIN MD MANAGED GUIDANCE -->
<!-- END MD MANAGED GUIDANCE -->
```

Everything before and after those markers belongs to the repository. The synchronizer does not rewrite, reorder, summarize, or remove unmanaged instructions.

### Create missing files safely

When a configured agent file does not exist, the tool creates it and inserts the managed block. When the file exists, the tool appends the block or replaces the existing managed block.

### Remain idempotent

Running the command repeatedly with the same project and suite paths produces no additional changes. There is exactly one managed block per file.

### Keep routing compact

Root agent files must not contain all 199 prompt bodies, all 110 scenarios, or the full skill registry. They contain a lookup protocol and high-frequency shortcuts. The canonical suite remains the source of truth.

## Installation into a project

From the project root, run the Python tool from the suite:

```bash
python /path/to/md/tools/sync_agent_guidance.py \
  --project-root . \
  --suite-root /path/to/md
```

On Windows PowerShell:

```powershell
& "C:\path\to\md\tools\sync-agent-guidance.ps1" `
  -ProjectRoot . `
  -SuiteRoot "C:\path\to\md"
```

The one-line CMD wrapper can also be run from the target repository root:

```bat
C:\path\to\md\tools\sync-agent-guidance.cmd
```

The tool manages exactly:

```text
AGENTS.md
CLAUDE.md
```

To synchronize only one of the supported files:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --agent-file AGENTS.md
```

`--agent-file` accepts only `AGENTS.md` or `CLAUDE.md`. Other filenames are rejected rather than silently created.

## Preview and audit

Preview without writing:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --dry-run \
  --show-diff
```

Print the generated managed block:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --print-block
```

The default receipt is written to:

```text
.prompt_suite/agent-guidance-receipt.json
```

The receipt records:

- project and suite roots;
- suite version;
- managed filenames;
- created, updated, removed, and unchanged files;
- dry-run state;
- optional unified diffs.

## Removing the integration

Remove only the managed MD blocks:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --remove
```

Human-authored content remains in place. A file that contains only the managed block becomes an empty file rather than being deleted automatically; file deletion is left to the repository owner.

## Keyword behavior

The generated guidance treats `MD` as a simple, memorable routing keyword.

### Exact target

```text
MD MD-29
MD C-108
```

The agent should inspect the exact target:

```bash
python tools/md.py explain MD-29
python tools/md.py explain C-108
```

### Natural-language lookup

```text
MD audit and fix security issues
MD academic paper review
MD visual assets for a technical report
MD personal productivity system
```

The agent treats the words after `MD` as a lookup query:

```bash
python tools/md.py lookup "audit and fix security issues" --limit 8
```

`lookup` searches:

- prompt titles, descriptions, categories, roles, tags, preferred skills, and permanent capability IDs;
- composite scenario titles and purposes;
- department discovery packs;
- skill IDs and purposes.

It returns match scores, matched terms, result type, canonical path or purpose, and the next `explain` command.

`lookup` is a discovery aid. `explain` remains authoritative for the complete selected graph.

## High-frequency productivity shortcuts

The managed block includes compact defaults:

| Keyword | Default route | Use |
|---|---|---|
| `MD clarify` | `MD-191` | ask only route-changing questions |
| `MD skill` | `MD-192 → MD-196` | prove skill fit and execute an exact skill |
| `MD find skill` | `MD-193 → MD-194 or MD-195` | discover, install, or create a missing reusable skill |
| `MD loop` | `MD-197 → MD-198` | bounded repetition and independent exit adjudication |
| `MD audit fix verify` | `C-108` | convergent audit, remediation, and verification |
| `MD research` | `C-26` | deep research report |
| `MD report` | `C-95` | professional report pipeline |
| `MD prompt` | `C-94` | prompt creation and optimization pipeline |
| `MD feature` | `C-63` | feature delivery |
| `MD visual assets` | `C-109` | code-native visual-asset batch production |
| `MD strudel` | `C-110` | Strudel composition and refinement |
| `MD productivity` | `MD-138` | personal knowledge and work system |

These routes are defaults, not unconditional dispatch. The agent must still confirm that the route owns the requested outcome.

## Efficient lookup order

A connected agent should follow this order:

1. Run `tools/md.py lookup` with the user's terms.
2. Run `tools/md.py explain` for the selected prompt, scenario, or pack.
3. Read `catalog.json` or `SCENARIO_CATALOG.json` for machine metadata.
4. Read `PROMPT_EXECUTION_ORDER.md` for phases, modes, branches, locks, and completion semantics.
5. Load only selected prompt bodies and their declared prerequisites from `prompts/`.
6. Load schemas, policies, skill registry entries, or loop policies only when triggered.

This order keeps context small and avoids scanning all prompts for routine work.

## Inquisitive behavior

The agent should not turn MD into a long questionnaire.

Use `MD-191` when an answer changes one of the following:

- selected prompt or scenario;
- authorization boundary;
- evidence lane;
- assurance level;
- output medium;
- budget;
- acceptance criteria;
- whether an external action is allowed.

Do not ask about details that can be safely inferred, recorded as an assumption, or deferred until the relevant phase.

## Skill behavior

The guidance teaches agents that an installed skill is not automatically required.

A skill should be invoked only when:

- its declared capability genuinely matches the requested result;
- it materially improves an acceptance criterion;
- its input and output contracts are understood;
- its permissions and external effects are within authority;
- its output can be independently verified.

Use `visual-assets` for deliberate code-native SVG, HTML, CSS, JavaScript, vector, illustration, infographic, diagram, and presentation-asset work when appropriate. Use `strudel` for Strudel music code. These are first-class examples, not exceptions to the generic skill policy.

## Loop behavior

A connected agent may invoke the generic loop only when repetition has a measurable purpose:

- a finite queue of independent items;
- a remaining defect or finding;
- a changed hypothesis;
- a declared quality metric;
- an independent verification step.

It must stop on verified success, quality plateau, budget exhaustion, stale evidence, lost authority, unsafe effects, repeated failure without a new hypothesis, or human stop.

## Managed-block update behavior

When the suite moves, rerun the synchronizer with the new `--suite-root`. The tool updates only the managed block, including relative paths and version information.

When the suite version changes, rerun the tool to update the version shown in each root agent file.

Do not manually edit path or version values inside the managed block. Manual edits will be replaced on the next synchronization.

## Failure handling

The synchronizer stops without writing when:

- the suite root lacks the catalog, scenario catalog, prompt directory, or tools directory;
- an agent target is absolute, escapes the project root, or is not Markdown;
- begin and end markers are unmatched;
- multiple managed blocks are present in one file;
- a JSON policy file is malformed;
- an atomic write fails.

Fix the structural problem and rerun. Do not remove user content to make the tool pass.

## Validation

Run the focused tests:

```bash
pytest -q tests/test_agent_guidance.py
pytest -q tests/test_md.py
```

Run the full deterministic chain:

```bash
python tools/check_documentation_links.py
python tools/run_tests.py
python tools/build_manifest.py --check
python tools/validate_suite.py
```

## Security and privacy

The synchronization tool performs local file reads and writes only. It does not:

- call a language model;
- install skills;
- access the network;
- inspect secrets;
- execute a selected prompt;
- publish or send content.

The generated agent guidance grants no additional authority. It points to the suite's existing authorization, evidence, tool, skill, loop, and verification contracts.
