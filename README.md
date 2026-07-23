# Mission Directives

[![Validate Mission Directives](https://github.com/manojpisini/mission-directives/actions/workflows/validate.yml/badge.svg)](https://github.com/manojpisini/mission-directives/actions/workflows/validate.yml)

Mission Directives is a curated library of advanced prompts and deterministic orchestration tools for turning natural-language intent into bounded, reviewable, and verifiable agent work with minimal context use.

Instead of loading a large prompt library and hoping the model chooses well, the suite resolves a request to the smallest coherent graph of prompts, tools, skills, evidence rules, approvals, artifacts, and verification steps needed for the outcome. It supports research, engineering, security, operations, strategy, writing, reporting, design, and other professional workflows.

Current release: **1.8.3**

## Why Mission Directives

Mission Directives provides a repeatable operating contract for agentic work:

- algorithmic keyword-context routing from natural-language intent to one prompt, a composite scenario, or a bounded workflow graph;
- explicit operating modes that separate analysis, planning, drafting, execution, and verification;
- evidence lanes for factual, hybrid, and imaginative work;
- authorization boundaries and least-privileged tool policies;
- typed handoffs, approvals, execution receipts, residuals, and verification records;
- genuine investigation/execution pairs for work that needs review before mutation;
- optional skill adapters without making third-party skills part of the trusted core;
- cross-platform installation and validation on Linux, Windows, and macOS.

The repository currently contains **201 prompts**, **201 atomic routes**, **110 composite scenarios**, and **32 reciprocal investigation/execution pairs**. The generated [prompt catalog](docs/PROMPT_CATALOG.md) and [scenario catalog](SCENARIO_CATALOG.json) are the canonical inventories.

## How It Works

```text
request
  -> parse MD/md invocation, intent, modifiers, and exact IDs
  -> apply shortcut ownership and metadata-only lookup
  -> select the smallest suitable prompt, scenario, or workflow graph
  -> inspect the selected prompt or scenario
  -> plan or execute within an explicit mode
  -> preserve approvals and handoffs where required
  -> verify the exact result
  -> record unknowns, residuals, and closure evidence
```

Prompt numbers are stable addresses, not a lifecycle. Department packs are discovery aids, not bundles that should be loaded in full.

## Requirements

- Python 3.12 is the CI-tested runtime.
- Git is required for development and recommended for project installation.
- PowerShell 7 is recommended for the Windows wrappers.
- Bash is required only for the POSIX wrappers.

Runtime and test dependencies are listed in [requirements-dev.txt](requirements-dev.txt).

## Quick Start

Clone the repository and create an isolated environment:

```bash
git clone https://github.com/manojpisini/mission-directives.git
cd mission-directives
```

Create and activate the environment on Linux or macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Create and activate it on Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If your platform exposes Python 3.12 under another command, use that exact interpreter and confirm it with `python --version` after activation.

Install the development dependencies and verify the suite:

```bash
python -m pip install -r requirements-dev.txt
python tools/md.py route "MD advanced audit fix verify repository"
python tools/validate_suite.py
```

## Install Into a Project

Always preview the installation first. From this repository checkout:

### Portable Python

```bash
python tools/install.py /absolute/path/to/project --dry-run
python tools/install.py /absolute/path/to/project
```

### Linux or macOS

```bash
bash tools/install.sh /absolute/path/to/project --dry-run
bash tools/install.sh /absolute/path/to/project
```

### Windows PowerShell 7

```powershell
pwsh -NoProfile -File tools/install.ps1 -ProjectPath 'C:\path\to\project' -DryRun
pwsh -NoProfile -File tools/install.ps1 -ProjectPath 'C:\path\to\project'
```

The installer:

- stages and promotes the suite to `<project>/prompts`;
- manages one Mission Directives block in `.gitignore`;
- keeps project documentation under `docs/` tracked;
- creates internal runtime directories under `.prompt_suite/`;
- creates or updates only `AGENTS.md` and `CLAUDE.md`;
- preserves all guidance outside the managed markers;
- writes installation and guidance receipts;
- restores the previous state if promotion fails.

Use `--replace` only when intentionally updating an existing installation. The installer creates a timestamped backup before replacement.

See the [Installation and Project Integration Guide](docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md) for replacement, rollback, skill-path, and verification details.

## Usage

### 1. Route the full user request

Pass the complete request instead of guessing an ID or scanning prompt files:

```bash
python tools/md.py route "MD advanced repository mission drift and simplification audit"
python tools/md.py route "md cleanup dead code safely"
python tools/md.py route "MD in depth research report"
```

`route` uses `tools/keyword_context.py` and `policies/agent_guidance_policy.json`
to parse the invocation slug, exact IDs, intent phrases, depth, assurance, mode,
and composition modifiers. It then applies explicit shortcut ownership before
metadata-only lookup. Prompt bodies are not opened during selection.

Use raw lookup for operator discovery, or compare close candidates:

```bash
python tools/md.py lookup "cleanup dead code safely" --limit 8
python tools/md.py compare C-108 C-63
```

### 2. Inspect the selected route

`explain` is authoritative for the complete graph, required inputs, allowed modes, skills, approvals, and verification obligations:

```bash
python tools/md.py explain MD-200
python tools/md.py explain C-108
```

### 3. Plan without changing files

```bash
python tools/md.py plan C-108 --mode AUDIT_ONLY --root . --dry-run
```

### 4. Use Mission Directives through an agent

After installation, the managed guidance teaches compatible agents to route the standalone `MD` keyword:

```text
MD audit fix verify this repository
MD research report on the selected market
MD cleanup dead code safely
MD add prompt
MD C-108
```

When an exact `MD-###` or `C-###` is supplied, the router resolves it directly and the agent inspects that target before execution. When ordinary words follow `MD` or `md`, AGENTS.md and CLAUDE.md pass the full request through keyword-context parsing, lookup, and deterministic selection instead of guessing from memory or scanning prompt bodies.

### Selection Algorithm

```text
full request
  -> invocation and modifier parser
  -> exact-ID resolution
  -> longest/highest-priority shortcut owner per route family
  -> transparent metadata lookup with a confidence threshold
  -> smallest prompt, scenario, or bounded workflow graph
  -> explain every selected target before loading its body
```

Specific shortcuts suppress broader routes in the same family. For example,
`MD add prompt` selects `MD-199`, not the generic prompt-engineering scenario;
`MD in depth research report` selects the research-report owner `C-26`; and
distinct intents such as visual assets plus Strudel form a two-target workflow.

### Common Routes

| Request | Preferred route | Purpose |
| --- | --- | --- |
| Clarify route-changing ambiguity | `MD-191` | Ask only questions that alter authority, evidence, output, or acceptance criteria |
| Add or refine a prompt | `MD-199` | Review overlap, normalize, register, test, and add a prompt |
| Audit, fix, and verify | `C-108` | Run a convergent remediation workflow |
| Deep research | `C-26` | Produce an evidence-backed research report |
| Professional report | `C-95` | Build and verify a report pipeline |
| Feature delivery | `C-63` | Plan, implement, test, and document a feature |
| Prompt engineering | `C-94` | Create, optimize, evaluate, or repair prompts |
| Personal work system | `MD-138` | Organize goals, projects, tasks, notes, and decisions |

Use these as entry points, not blind dispatch rules. Confirm the route with `explain`.

## Operating Modes

| Mode | Permitted outcome |
| --- | --- |
| `AUDIT_ONLY` | Inspect, retrieve, analyze, compare, and report without mutation |
| `PLAN_ONLY` | Produce plans, specifications, decisions, or acceptance criteria |
| `DRAFT_ONLY` | Produce unapproved local drafts without implying publication or acceptance |
| `APPLY_SAFE` | Make reversible local changes inside explicit authority |
| `APPLY_APPROVED` | Perform the exact approved consequential action with receipts and recovery controls |
| `VERIFY_ONLY` | Independently verify an artifact or claimed result without changing it |

Drafting is not publication. Local implementation is not deployment. A recommendation is not approval for an external action.

## Evidence and Verification

Every canonical prompt uses the runtime marker protocol:

| Marker | Meaning |
| --- | --- |
| `@EVIDENCE:{id}` | Source, observation, or input |
| `?UNKNOWN:{id}` | Material unresolved uncertainty |
| `#FINDING:{id}` | Evidence-backed issue or conclusion |
| `+ACTION:{id}` | Bounded proposed or executed action |
| `=VERIFY:{id}` | Acceptance criterion and result |
| `!STOP:{reason}` | Mandatory stop condition |

The suite distinguishes structural proof from behavioral proof. Passing static validation proves that files, IDs, schemas, graphs, fixtures, and deterministic checks agree; it does not prove live model quality, third-party skill behavior, or external action success.

For work split into an investigative and executive pair, the plan must be reviewed, revised if necessary, re-frozen, approved, and explicitly handed to its exact reciprocal executor. See the [Plan Review and Exact-Twin Execution Guide](docs/PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md).

## Add a Prompt

Use the agentic route when semantic refinement or overlap analysis is needed:

```text
MD add prompt
```

Use the transactional tool when the source and title are already settled:

```bash
python tools/add_prompt.py --source ./candidate.md --title "Canonical Prompt Title" --dry-run
python tools/add_prompt.py --source ./candidate.md --title "Canonical Prompt Title" --approval-token <TOKEN_FROM_DRY_RUN>
```

Do not copy prompt files directly into `prompts/`. The transaction updates permanent identities, catalogs, graphs, templates, crosswalks, scenarios, fixtures, evaluations, tests, validation data, and the manifest together.

See the [Prompt Addition and Registration Guide](docs/PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md).

## Repository Layout

| Path | Purpose |
| --- | --- |
| `prompts/` | Canonical prompt bodies |
| `catalog.json` | Prompt identities, metadata, contracts, and relationships |
| `SCENARIO_CATALOG.json` | Atomic and composite routes |
| `config/` | Capability graph, taxonomy, packs, templates, models, and skills |
| `policies/` | Authorization, execution, evidence, installation, and runtime policies |
| `schemas/` | Typed artifact and runtime contracts |
| `evaluations/` | Fixtures, pair comparisons, benchmarks, and golden runs |
| `tools/` | CLI, installers, generators, validators, and platform wrappers |
| `tests/` | Deterministic regression and contract tests |
| `docs/` | User, operator, authoring, security, and maintenance manuals |
| `examples/` | Worked routing and execution examples |
| `compatibility/` | Current capability identity registry and supported agent skill destinations |
| `integrations/` | Agent, skill, template, logging, and platform crosswalks |

## Development and Contribution

Read [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), and the policy or schema that owns the behavior before editing.

The contribution path is intentionally strict:

1. Change the smallest canonical source that owns the behavior.
2. Add or update one focused regression test or adversarial fixture.
3. Run the targeted check before broad regeneration.
4. Regenerate only the artifacts owned by the changed source.
5. Review generated diffs for semantic drift.
6. Run the complete validation chain.
7. Document identity, consumer-contract, authority, security, and cross-platform impact.

Do not manually edit generated catalogs, graphs, audit reports, fixtures, validation reports, or `MANIFEST.json`. Do not commit credentials, private data, absolute personal paths, caches, local logs, runtime receipts, or unrelated refactors.

Write commit messages in past-tense declarative form without first-person pronouns, for example `Added mission audit prompt integration` or `Fixed release consistency validation`.

The repository is currently all-rights-reserved; read [LICENSE](LICENSE) before copying, redistributing, or contributing material.

## Validation

Run the focused checks that cover your change, then the full chain before committing:

The audit, test, evaluation, and suite commands may refresh tracked generated reports. Review those diffs rather than discarding them blindly. Rebuild `MANIFEST.json` only after the generated changes are accepted.

```bash
python tools/audit_prompt_bodies.py
python tools/run_tests.py
python tools/validate_templates.py
python tools/check_documentation_links.py
python tools/check_script_parity.py
python tools/check_release_consistency.py
python tools/run_evaluations.py
python tools/check_generated_reproducibility.py
python tools/build_manifest.py
python tools/build_manifest.py --check
python tools/validate_suite.py
```

GitHub Actions runs the validation workflow on `ubuntu-latest`, `windows-latest`, and `macos-latest` with Python 3.12. Platform wrappers are smoke-tested in their native jobs. Every matrix job uploads body audits, deterministic test status, evaluation status, and full validation output for review.

## Completion Status

Run the lifecycle report to see structural coverage and external evidence gaps:

```bash
python tools/md.py lifecycle
```

The routing, catalog, scenario, exact-twin, installer, schema, fixture,
cross-platform validation, and artifact-review surfaces are implemented. The
project is not honestly at 100% behavioral completion until real evidence
resolves every lifecycle blocker. At the current repository state those
blockers are:

- no human-reviewed golden run has been promoted;
- no third-party skill has a live passing conformance result;
- no installable skill lock has been resolved from a reviewed immutable source;
- no measured model profile is production eligible.

Use `tools/promote_golden_run.py`, `tools/run_skill_conformance.py`,
`tools/resolve_skill_lock.py`, and `tools/run_model_benchmarks.py` to close those
gaps with real receipts. Do not replace these measurements with fixture-only or
machine-generated claims.

## Uninstall

Preview cleanup before approving removal:

```bash
python tools/cleanup.py /absolute/path/to/project --dry-run
python tools/cleanup.py /absolute/path/to/project --yes
```

Cleanup removes only validated Mission Directives-managed paths and text blocks while preserving unrelated project content. See the [Project Cleanup and Uninstall Guide](docs/PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md) for approval-token and recovery behavior.

## Documentation

Start with the [Manuals and Guides index](docs/MANUALS.md).

- [User Manual](docs/USER_MANUAL.md)
- [Operator Guide](docs/OPERATOR_GUIDE.md)
- [Mastery Manual](docs/MD_MASTERY_MANUAL.md)
- [Architecture Guide](docs/ARCHITECTURE_GUIDE.md)
- [Prompt Catalog](docs/PROMPT_CATALOG.md)
- [Prompt Suite Conventions](docs/PROMPT_SUITE_CONVENTIONS.md)
- [Prompt Body Authoring Guide](docs/PROMPT_BODY_AUTHORING_GUIDE.md)
- [Evaluation Manual](docs/EVALUATION_MANUAL.md)
- [CI and Testing Guide](docs/CI_AND_TESTING_GUIDE.md)
- [Security Boundaries](docs/SECURITY_BOUNDARIES.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING_GUIDE.md)

## License

Copyright (c) 2026 Manoj Pisini. All rights reserved unless an explicit replacement license is adopted. See [LICENSE](LICENSE).
