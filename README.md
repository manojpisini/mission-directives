<p align="center">
  <img src="assets/readme/mission-directives-banner.svg" alt="Mission Directives" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/manojpisini/mission-directives/actions/workflows/validate.yml"><img src="https://github.com/manojpisini/mission-directives/actions/workflows/validate.yml/badge.svg" alt="Validate Mission Directives" /></a>
  <a href="https://github.com/manojpisini/mission-directives/actions/workflows/deploy-docs.yml"><img src="https://github.com/manojpisini/mission-directives/actions/workflows/deploy-docs.yml/badge.svg" alt="Deploy documentation" /></a>
</p>

<p align="center">
  <strong>Bounded, reviewable, and verifiable agent work.</strong><br />
  <a href="https://manojpisini.github.io/mission-directives/">Documentation site</a>
</p>

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

Mission Directives is a curated prompt and orchestration suite for turning natural-language requests into the smallest coherent prompt, scenario, or workflow graph needed for the outcome. It keeps selection deterministic, authority explicit, and completion tied to evidence instead of asking a model to load a whole library and guess.

Current release: **1.8.3**

<p align="center">
  <img src="assets/readme/routing-flow.svg" alt="Mission Directives routing flow: route, explain, plan, and verify." width="100%" />
</p>

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## What It Provides

- **Deterministic routing:** exact IDs, shortcuts, keyword concepts, route hints, typo recovery, metadata scoring, and calibrated no-match behavior.
- **Stable prompt contracts:** permanent `MD-*` identities, typed inputs and outputs, operating modes, risk levels, evidence lanes, and completion gates.
- **Scenario graphs:** atomic and composite workflows with phases, locks, branches, approvals, assurance requirements, and external-action boundaries.
- **Lean project install:** target projects receive only runtime files needed for routing and execution; repository-only tests, evaluation assets, validators, CI, import tooling, and site sources stay upstream.
- **Verification discipline:** every route is complete only when the requested artifact satisfies its task-specific verification contract and residuals are explicit.

<p align="center">
  <img src="assets/readme/inventory.svg" alt="Repository inventory: 257 prompts, 257 atomic routes, 110 composite scenarios, 58 manuals, and 32 reciprocal pairs." width="100%" />
</p>

Repository inventory: **257 prompts**, **257 atomic routes**, **110 composite scenarios**, **32 reciprocal investigation/execution pairs**, and **58 repository manuals**.

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## How It Works

```text
request
  -> parse MD invocation, exact IDs, intent, depth, and assurance modifiers
  -> resolve shortcut owners and candidate metadata without loading prompt bodies
  -> rank prompt, scenario, pack, and skill candidates
  -> explain the selected graph, modes, inputs, approvals, and verification duties
  -> plan or execute inside the declared authority boundary
  -> verify the exact result and record evidence, unknowns, residuals, and receipts
```

Prompt numbers are stable addresses, not lifecycle state. Department packs help discovery; they are not bundles to load in full.

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Requirements

- Python 3.12 is the CI-tested runtime.
- Git is required for normal development.
- PowerShell 7 is recommended for Windows wrappers.
- Bash is required only for POSIX wrappers.
- The documentation site uses `pnpm`.

Runtime dependencies for installed projects are in [requirements-runtime.txt](requirements-runtime.txt). Repository development and validation dependencies are in [requirements-dev.txt](requirements-dev.txt).

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Quick Start

```bash
git clone https://github.com/manojpisini/mission-directives.git
cd mission-directives
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python tools/md.py route "MD advanced audit fix verify repository"
python tools/validate_suite.py
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python tools\md.py route "MD advanced audit fix verify repository"
python tools\validate_suite.py
```

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Install Into a Project

Always preview first:

```bash
python tools/install.py /absolute/path/to/project --dry-run
python tools/install.py /absolute/path/to/project
```

Windows wrapper:

```powershell
pwsh -NoProfile -File tools/install.ps1 -ProjectPath 'C:\path\to\project' -DryRun
pwsh -NoProfile -File tools/install.ps1 -ProjectPath 'C:\path\to\project'
```

The installer copies the explicit runtime payload, manages the Mission Directives block in `.gitignore`, creates `.prompt_suite/` runtime directories, updates only managed `AGENTS.md` and `CLAUDE.md` blocks, writes receipts, and restores the previous state if promotion fails. Use `--replace` only for intentional updates; it creates a timestamped backup first.

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Daily Usage

Route the full request:

```bash
python tools/md.py route "MD advanced repository mission drift and simplification audit"
python tools/md.py lookup "cleanup dead code safely" --limit 8
python tools/md.py compare C-108 C-63
python tools/md.py explain C-108
python tools/md.py plan C-108 --mode AUDIT_ONLY --root . --dry-run
```

Common entry points:

| Request | Route | Purpose |
| --- | --- | --- |
| Clarify route-changing ambiguity | `MD-191` | Ask only questions that alter authority, evidence, output, budget, or acceptance criteria. |
| Add or refine a prompt | `MD-199` | Review overlap, normalize, register, test, and add one prompt. |
| Audit, fix, and verify | `C-108` | Run a convergent remediation workflow. |
| Deep research | `C-26` | Produce an evidence-backed research report. |
| Professional report | `C-95` | Build and verify a report pipeline. |
| Feature delivery | `C-63` | Plan, implement, test, and document a feature. |
| Prompt engineering | `C-94` | Create, optimize, evaluate, or repair prompts. |
| Personal work system | `MD-138` | Organize goals, projects, tasks, notes, and decisions. |

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Operating Modes

| Mode | Boundary |
| --- | --- |
| `AUDIT_ONLY` | Inspect, retrieve, analyze, compare, and report without mutation. |
| `PLAN_ONLY` | Produce plans, specifications, decisions, or acceptance criteria. |
| `DRAFT_ONLY` | Produce local drafts without implying publication or acceptance. |
| `APPLY_SAFE` | Make reversible local changes inside explicit authority. |
| `APPLY_APPROVED` | Perform the exact approved consequential action with receipts and recovery controls. |
| `VERIFY_ONLY` | Independently verify an artifact or claimed result without changing it. |

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Documentation Site

The documentation site is a static Astro build that uses the checked-in landing/documentation HTML, CSS, and JS shell. The generator publishes a sectioned documentation hub: `docs.html` for overview, `guides.html` for task guides, `manuals.html` for the generated manual library, `reference.html` for runtime contracts, `prompts.html` for every prompt, `scenarios.html` for atomic and composite scenarios, `pairs.html` for reciprocal pairs, and every root `docs/*.md` file as a static manual page under `reference/manuals/`.

```bash
cd site
pnpm install
pnpm run generate
pnpm run build
pnpm run check
```

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Repository Layout

| Path | Purpose |
| --- | --- |
| `prompts/` | Canonical prompt bodies. |
| `catalog.json` | Prompt identities, metadata, and relationships. |
| `SCENARIO_CATALOG.json` | Atomic and composite route graphs. |
| `config/` | Router keywords, runtime payload allowlist, templates, packs, and capability graph. |
| `policies/` | Authorization, evidence, routing, install, loop, and agent guidance policies. |
| `schemas/` | Typed contracts and imported source schemas. |
| `tools/` | Router, installer, generators, validators, and wrappers. |
| `docs/` | User, operator, authoring, security, and maintenance manuals. |
| `site/` | Static documentation site source. |
| `tests/` / `evaluations/` | Repository-only validation and evaluation assets. |

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## Validation

Before committing runtime, manifest, prompt, schema, docs, or site changes, run the smallest checks that cover the touched surface. For broad changes:

```bash
python tools/build_manifest.py
python -m pytest
python tools/validate_suite.py
cd site && pnpm run check
```

`tools/validate_suite.py` checks structural contracts, deterministic runtime tests, fixture coverage, identity contracts, CI configuration, lock safety, generated artifact reproducibility, and manifest integrity. It does not certify live model quality or external-world outcomes.

<p align="center">
  <img src="assets/readme/divider.svg" alt="" width="100%" />
</p>

## License

See [LICENSE](LICENSE).
