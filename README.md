# Mission Directives

A capability-first operating system for language-model work across an organization.

The suite converts an ambiguous request into a bounded execution graph, selects only the prompts and tools that change the result, separates evidence from action, produces typed artifacts, and verifies the exact outcome before closure.

It is designed for language-model work involving research, analysis, writing, code, documents, reports, spreadsheets, presentations, diagrams, dashboards, interfaces, planning, operations, and controlled tool workflows. Model image generation is intentionally outside this package. Code-native visual production—hand-built SVG, CSS, HTML, and vanilla JavaScript through skills such as `visual-assets`—is supported for illustrations, infographics, diagrams, presentation assets, and animated explanatory graphics.

## Install into a project

```bash
./install.sh /path/to/project
# Windows PowerShell 7:
./install.ps1 -ProjectPath C:\path\to\project
```

The installer copies the suite to `./prompts`, maintains project `.gitignore` entries for internal runtime paths, preserves tracked `docs/`, and synchronizes only `AGENTS.md` and `CLAUDE.md`. See [Installation and Project Integration](docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md).

Remove a project installation safely with `python cleanup.py /path/to/project --dry-run` followed by an approved cleanup. The cleanup removes the suite copy and managed project integrations while preserving unrelated content, uses an explicit purge commit boundary, and retains/report residual quarantine rather than performing an unsafe partial restore. See [Project Cleanup and Uninstall](docs/PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md).

## Current verified scope

The canonical package contains:

- **199 prompts** with permanent capability identities;
- **32 genuine Investigative → Executive pairs**;
- **130 standalone non-control capabilities**;
- **110 composite scenarios** plus one atomic route per prompt;
- **16 department discovery packs**;
- **8 conditional auto-prompts** for intent clarification, skill fit, discovery, governed installation or creation, generic skill execution, bounded looping, and independent exit adjudication;
- **277 registered skill adapters** plus a snapshot of **193 detected OpenCode skills**;
- factual, hybrid, imaginative, and control evidence contracts;
- six operating modes;
- FAST, STANDARD, and HIGH_ASSURANCE profiles;
- typed evidence, findings, actions, approvals, verification, residual, lineage, report, visual, learning, survey, and evaluation artifacts;
- deterministic routing and state-transition tools;
- fixture, mutation, pair, skill, model, rollback, and golden-run evaluation infrastructure;
- skill trust, lock, and quarantine controls;
- compatibility and agent-library crosswalks;
- detailed user, operator, authoring, evaluation, security, and maintenance manuals.
- root-agent guidance synchronization for exactly `AGENTS.md` and `CLAUDE.md`, with other instruction filenames intentionally excluded;
- deterministic keyword lookup across prompts, scenarios, packs, and skills through `md.py lookup`.

The package distinguishes structural proof from behavioral proof. A static pass proves that files, IDs, tags, graphs, schemas, and deterministic checks agree. It does not certify live model quality, unresolved third-party skills, or external actions.

## Prompt-body integrity

Every canonical prompt body now implements the same machine-relevant contract:

- `199 / 199` canonical `<authorization_boundary>` blocks;
- `199 / 199` least-privileged `<tool_policy>` blocks;
- `199 / 199` `<runtime_markers>` blocks containing all six record types;
- `199 / 199` task-specific `<completion_criteria>` blocks;
- `199` unique normalized completion blocks;
- `0` known boilerplate completion blocks;
- `32 / 32` executives with `<decision_rules>`;
- `32 / 32` executives with `<verification_reference>`;
- `0` duplicated investigator/executive verification blocks;
- `0` prompt self-dependencies;
- `0` legacy `<security_execution_boundary>` tags.

These metrics are generated from the prompt bodies by:

```bash
python tools/audit_prompt_bodies.py
```

Read:

- [Prompt Body Quality Audit](BODY_QUALITY_AUDIT.md)
- [Structured Prompt Design Standard](docs/PROMPT_STRUCTURE_STANDARD.md)
- [Prompt Suite Conventions](docs/PROMPT_SUITE_CONVENTIONS.md)
- [Prompt Body Authoring Guide](docs/PROMPT_BODY_AUTHORING_GUIDE.md)

## Conditional auto-orchestration

The auto-prompt layer is deliberately small and conditional:

```text
MD-191 clarify only route-changing intent
MD-192 prove whether a skill is genuinely required
MD-193 discover and qualify a missing capability
MD-194 install one approved exact skill into both global locations
MD-195 create a reusable skill only when discovery is genuinely empty
MD-196 execute any exact installed skill through typed placeholders
MD-197 loop any prompt, scenario, or skill only when repetition has measurable value
MD-198 independently decide continue, complete, plateau, rollback, escalate, or stop
```

A loop can target any prompt or skill. It is rejected when one complete pass is sufficient, progress is not measurable, evidence and hypotheses remain unchanged, or expected cost and risk exceed the likely gain. Batch work uses an outer queue loop; optional refinement uses a separate inner quality loop. Maximum iterations are ceilings, never targets.

An installed but unmapped skill may be routed through `MD-192` and `MD-196` after runtime schema, permission, provenance, and task-fit review. Missing skills route to discovery and governed acquisition; they are never installed merely because a name resembles the request.

Examples:

```bash
python tools/md.py auto-plan MD-104 --skill-id visual-assets --skill-required --loop --work-items 12 --measurable
python tools/md.py auto-plan MD-27 --skill-id code-review --skill-required
python tools/md.py auto-plan MD-165 --skill-id missing-specialist --skill-required --allow-install --allow-create
python tools/md.py loop-decision --iteration 3 --current-score 0.71 --target-score 0.90 --previous-scores 0.70,0.705 --max-iterations 5 --max-no-improvement 2 --minimum-delta 0.01
```

See [Auto-Prompts and Conditional Routing Guide](docs/AUTO_PROMPTS_AND_CONDITIONAL_ROUTING_GUIDE.md), [Generic Skill Execution Guide](docs/GENERIC_SKILL_EXECUTION_GUIDE.md), and [Bounded Loop Orchestration Guide](docs/BOUNDED_LOOP_ORCHESTRATION_GUIDE.md).

## Personal specialist skills

- `visual-assets` is the preferred code-native route for deliberate SVG, CSS, HTML, and vanilla-JS illustrations, infographics, report exhibits, presentation assets, vector systems, and animated explanatory graphics. Its output remains editable and independently reviewed.
- `strudel` is the canonical local skill for Strudel live-coding music programs. The spelling `strudle` is retained only as an input alias.

Both are examples of the generic `MD-196` adapter, not hard-coded limits on what skill may execute.

## Auto-orchestration examples

Worked examples are available in [`examples/auto_orchestration/`](examples/auto_orchestration/):

- visual asset batch production;
- audit–fix–verify convergence;
- missing-skill acquisition;
- installed but unmapped skill execution;
- wasteful-loop rejection;
- Strudel alias resolution and refinement.

## Operating principle

```text
request
→ observable outcome and audience
→ authority and protected surfaces
→ evidence lane and assurance profile
→ smallest coherent prompt graph
→ current evidence snapshot
→ investigation or brief when required
→ frozen handoff when a genuine pair is justified
→ production or authorized execution
→ independent verification of the exact artifact or change
→ residuals, lineage, learning, and closure
```

Numeric prompt order is an address, not a lifecycle. Department packs are discovery profiles, not instructions to load every prompt they contain.

## Root agent guidance and MD keyword routing

Projects can connect their root agent-instruction files to this suite without copying prompt bodies or replacing project-owned instructions.

Preview the managed sections:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --suite-root . \
  --dry-run \
  --show-diff
```

Apply them:

```bash
python tools/sync_agent_guidance.py \
  --project-root /path/to/project \
  --suite-root .
```

The only managed target files are `AGENTS.md` and `CLAUDE.md`. Missing files are created. Existing files retain all content outside the MD managed markers. Repeated runs are idempotent. Other agent instruction filenames are intentionally excluded.

The generated section teaches agents to recognize the `MD` keyword:

```text
MD research report on the selected market
MD audit fix verify this repository
MD visual assets for the presentation
MD productivity system
MD C-108
```

Natural-language terms are resolved with the deterministic lookup command:

```bash
python tools/md.py lookup "audit fix verify repository" --limit 8
python tools/md.py explain C-108
```

Lookup searches prompts, scenarios, department packs, and skills. It is a discovery aid; `explain` remains authoritative for the complete graph, authority, evidence, skills, and verification obligations.

See [Root Agent Guidance and Keyword Routing Guide](docs/ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md).

## Add a prompt safely

Use the agentic route when overlap analysis or semantic refinement is needed:

```text
MD add prompt
```

Use the deterministic transaction when the source file and title are ready:

```bash
python tools/add_prompt.py --source ./candidate.md --title "Canonical Prompt Title" --dry-run
python tools/add_prompt.py --source ./candidate.md --title "Canonical Prompt Title" --approval-token <TOKEN_FROM_DRY_RUN>
python tools/md.py add-prompt --source ./candidate.md --title "Canonical Prompt Title" --dry-run
python tools/platform_dispatch.py add-prompt --source ./candidate.md --title "Canonical Prompt Title" --dry-run
```

The tool assigns the next permanent `MD-*` identity, normalizes the prompt, updates catalogs, graph, templates, skills, crosswalks, scenarios, fixtures, evaluations, tests, validation, and manifest, then promotes only a verified staged diff. See [Prompt Addition and Registration Guide](docs/PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md).

## Quick start

### 1. Find the smallest relevant route

```bash
python tools/md.py lookup "<user terms>" --limit 8
```

Use the returned prompt or scenario as a candidate, then confirm it with `explain`.

### 2. Describe the run

```text
RUN C-63
MODE DRAFT_ONLY
ASSURANCE STANDARD
ROOT /path/to/project
OUTCOME Implement the approved customer export feature with tests and release evidence
AUDIENCE product owner, maintainers, support, and release approver
SCOPE API, UI, authorization, data export, tests, telemetry, documentation
EXCLUDE unrelated refactoring, deployment, public announcement
AUTHORITY local reversible files only
EVIDENCE_LANE FACTUAL
EVIDENCE approved requirements, architecture decision, repository, test environment
SKILLS AUTO
BUDGET prompts=15 external_calls=20 parallel_workers=3
QUALITY acceptance tests pass; no privilege bypass; export is accurate; rollback is documented
```

### 3. Inspect the route

```bash
python tools/md.py explain C-63
```

The route explanation reports:

- selected prompts;
- injected cross-cutting prompts;
- rejected prompts;
- unresolved questions;
- deferred capabilities;
- route confidence;
- skill and model status;
- required approvals and locks.

### 4. Plan without writing

```bash
python tools/md.py plan C-63 \
  --mode DRAFT_ONLY \
  --root . \
  --dry-run
```

### 5. Validate the run manifest

```bash
python tools/md.py validate-run .prompt_suite/runs/feature.json
```

## Execution modes

| Mode | Meaning |
|---|---|
| `AUDIT_ONLY` | Inspect, retrieve, analyze, compare, and report; no mutation |
| `PLAN_ONLY` | Produce plans, specifications, decisions, or acceptance criteria; no execution |
| `DRAFT_ONLY` | Produce unapproved local drafts; no implied acceptance, publication, submission, or deployment |
| `APPLY_SAFE` | Make reversible local changes within explicit authority |
| `APPLY_APPROVED` | Perform the exact approved consequential action with receipt, locks, recovery, and verification |
| `VERIFY_ONLY` | Independently verify an artifact or claimed outcome without changing the subject |

Drafting is not publishing. Local code is not deployment. A recommendation is not an employment, legal, financial, intelligence, or governance decision.

## Assurance profiles

### FAST

For low-risk local work:

- minimum sufficient context;
- native or trusted tools;
- deterministic checks;
- no external effects.

### STANDARD

For normal professional work:

- current evidence;
- typed artifacts;
- independent review where material;
- exact verification;
- residual tracking.

### HIGH_ASSURANCE

For security, production, regulated, employment, legal, financial, intelligence, public, or high-impact work:

- formal evidence protocol;
- snapshot binding;
- counterevidence;
- approval receipts;
- dry runs;
- independent verification;
- recovery proof;
- lineage and audit trail.

## Evidence lanes

### Factual

Claims, quotations, dates, calculations, and decisions must trace to current authoritative evidence.

### Hybrid

Factual claims remain traceable while interpretation, recommendation, narrative, and design choices are visibly separate.

### Imaginative

Originality, craft, and internal coherence are primary. The prompt must not invent citations or imply factual verification.

See [Evidence Lanes](docs/EVIDENCE_LANES.md).

## Runtime marker protocol

Every prompt instructs the model and runtime to use:

| Marker | Record |
|---|---|
| `@EVIDENCE:{id}` | source or observation |
| `?UNKNOWN:{id}` | material unresolved uncertainty |
| `#FINDING:{id}` | evidence-backed issue, opportunity, or conclusion |
| `+ACTION:{id}` | bounded proposed or executed action |
| `=VERIFY:{id}` | acceptance criterion and result |
| `!STOP:{reason}` | mandatory halt condition |

Example:

```text
@EVIDENCE:bug-01 failing test at commit 72ad1c
#FINDING:bug-01 refresh-token replay remains possible after password reset
+ACTION:bug-01 revoke all refresh-token families after password reset
=VERIFY:bug-01 original replay test fails before the fix and passes after the fix
?UNKNOWN:bug-02 legacy mobile client compatibility is untested
!STOP:production-approval-missing
```

Read the [Runtime Marker Protocol](docs/RUNTIME_MARKER_PROTOCOL.md).

## Prompt roles

### Control

Shared context, safety, routing, artifacts, and input trust. Control prompts are loaded once per run.

### Investigative

Read-only evidence, analysis, findings, plan, brief, or acceptance design.

### Executive

Approved action based on a frozen handoff. Every executive has task-specific decision rules and references the investigator's acceptance criteria rather than duplicating them.

### Operational

A bounded end-to-end artifact or workflow that does not require a separate investigative twin.

### Gate

An independent readiness or quality decision. Gates do not repair or approve their own work.

## Genuine-pair architecture

A pair exists only when:

1. investigation can remain non-mutating;
2. it produces a stable handoff;
3. execution owns a distinct responsibility;
4. the pair shares objective acceptance criteria;
5. the split improves safety, reviewability, parallelism, or quality.

The investigator owns `<verification_design>` and the acceptance-criteria artifact. The executive uses `<verification_reference>` and writes `=VERIFY:{id}` results against the same IDs.

Read:

- [Capability Architecture](docs/CAPABILITY_ARCHITECTURE.md)
- [Pair Authoring and Verification Guide](docs/PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md)
- [Executive Decision Rules Guide](docs/EXECUTIVE_DECISION_RULES_GUIDE.md)

## Completion semantics

A prompt is complete only when its task-specific conditions are met. Completion criteria must identify:

- the exact artifact or changed state;
- domain success conditions;
- verification records;
- unknown and residual treatment;
- stop behavior for missing evidence or authority.

Generic slogans do not satisfy the contract. Read the [Completion Criteria Guide](docs/COMPLETION_CRITERIA_GUIDE.md).

## Tool and skill behavior

Every prompt has a `<tool_policy>` block. The runtime selects the smallest sufficient tool set, respects the operating mode, binds state-changing calls to `+ACTION:{id}`, and treats output as untrusted until verified.

Third-party skills are optional adapters. They require:

- exact source identification;
- locked revision and checksum for high-assurance use;
- permission review;
- output quarantine;
- conformance testing;
- native fallback.

Read:

- [Tool Policy and Authorization Guide](docs/TOOL_POLICY_AND_AUTHORIZATION_GUIDE.md)
- [Skill Routing](docs/SKILL_ROUTING.md)
- [Skill Supply-Chain Guide](docs/SKILL_SUPPLY_CHAIN_GUIDE.md)

## Department discovery packs

| Pack | Typical work |
|---|---|
| `EXECUTIVE_AND_STRATEGY` | strategy, portfolio, operating model, intelligence, executive decisions |
| `PRODUCT` | discovery, requirements, experiments, roadmap, lifecycle |
| `ENGINEERING` | architecture, features, debugging, testing, delivery, reliability |
| `SECURITY_RISK_AND_INTELLIGENCE` | security, OSINT, threat intelligence, fraud, incidents |
| `AI_AND_AGENTIC` | prompts, models, RAG, memory, tools, agents, governance |
| `RESEARCH_AND_ACADEMIC` | research protocols, synthesis, analytics, manuscripts, peer review |
| `DESIGN_BRAND_AND_CONTENT` | brand, editorial, slides, dashboards, diagrams, web artifacts |
| `MARKETING_PR_AND_PUBLIC_AFFAIRS` | marketing, SEO/AEO, campaigns, PR, policy monitoring |
| `SALES_REVENUE_AND_PARTNERSHIPS` | pipeline, enablement, forecasting, partnerships |
| `FINANCE_ACCOUNTING_AND_AUDIT` | FP&A, close, treasury, controls, audit |
| `LEGAL_COMPLIANCE_AND_GOVERNANCE` | legal research, contracts, privacy, ethics, governance |
| `PEOPLE_AND_ORGANIZATION` | workforce, hiring, onboarding, learning, change |
| `OPERATIONS_SUPPLY_CHAIN_AND_ADMIN` | process, quality, procurement, continuity, administration |
| `CUSTOMER_SUPPORT_AND_SUCCESS` | support, escalation, retention, voice of customer |
| `REPORTING_KNOWLEDGE_AND_RECORDS` | reports, meetings, documentation, records, taxonomy |
| `PERSONAL_WORK_SYSTEMS` | goals, projects, tasks, notes, decisions, learning |

A pack must still be compiled to the smallest task-specific graph.

## Evaluation and proof

The suite contains:

- healthy, problematic, and adversarial prompt fixtures;
- healthy, problematic, and adversarial composite-scenario fixtures;
- contaminated-handoff fixtures for every genuine pair;
- pair-versus-single benchmark definitions;
- skill-conformance contracts;
- model benchmark ingestion;
- rollback drills;
- machine-reference runs and human-promotion workflow;
- prompt-body static audit;
- runtime unit tests;
- manifest integrity validation.

Proof levels are separate:

| Level | What it proves |
|---|---|
| Static validation | files, tags, IDs, schemas, catalogs, and graphs agree |
| Deterministic tests | reference runtime functions behave as tested |
| Fixture coverage | expected and prohibited behavior is specified |
| Live model benchmark | a named model produced measured results on fixtures |
| Live skill conformance | an installed skill produced output matching its adapter contract |
| Human golden review | a complete run was reviewed and promoted by an accountable human |

Read the [Evaluation Manual](docs/EVALUATION_MANUAL.md).

## Permanent identity and compatibility

Every prompt has:

```yaml
capability_id: permanent semantic identity
prompt_id: permanent suite identifier
prompt_slug: stable human-readable identity
sequence: current ordering address
identity_status: permanent
```

Compatibility mappings preserve original capabilities and redirects outside the active runtime. See [Compatibility and Identity Guide](docs/COMPATIBILITY_AND_IDENTITY_GUIDE.md).

## Agent-library bridge

The package includes proposed crosswalks between MD capabilities, agent archetypes, and prompt types. Mappings are machine-generated candidates until reviewed.

See [Agent Library Integration Guide](docs/AGENT_LIBRARY_INTEGRATION_GUIDE.md).

## Directory map

```text
README.md
AGENTS.md
CLAUDE.md
docs/MANUALS.md
docs/PROMPT_CATALOG.md
PROMPT_EXECUTION_ORDER.md
docs/PROMPT_SUITE_CONVENTIONS.md
docs/PROMPT_STRUCTURE_STANDARD.md
docs/PROMPT_ENGINEERING_METHODS.md
docs/RESEARCH_BASIS.md
docs/CAPABILITY_ARCHITECTURE.md
docs/EVIDENCE_LANES.md
docs/SKILL_ROUTING.md
docs/SECURITY_BOUNDARIES.md
BODY_QUALITY_AUDIT.md
catalog.json
SCENARIO_CATALOG.json
capability_graph.json
skill_registry.json
installed_skills_inventory.json
skill_aliases.json
skills.lock.json
model_profiles.json
run_state_machine.json
auto_prompt_policy.json
loop_execution_policy.json
skill_acquisition_policy.json
policies/
compatibility/
integrations/
schemas/
evaluations/
prompts/
examples/
docs/
tests/
tools/
agent_guidance_policy.json
MANIFEST.json
VALIDATION.json
```

## Validation commands

### Focused prompt-body checks

```bash
python tools/audit_prompt_bodies.py --check
pytest -q tests/test_prompt_body_quality.py
python tools/build_capability_graph.py --check
```

### Complete deterministic chain

```bash
python tools/check_skill_lock.py
python tools/run_evaluations.py
python tools/run_tests.py
python tools/build_manifest.py --check
python tools/validate_suite.py
```

### Regeneration after an intentional change

```bash
python tools/refine_prompt_bodies.py        # only when intentionally applying the canonical body transformation
python tools/build_capability_graph.py
python tools/audit_prompt_bodies.py
python tools/run_tests.py
python tools/build_manifest.py
python tools/validate_suite.py
```

Do not regenerate artifacts blindly. Review the semantic diff before committing.

## Definition of done

The suite is healthy when it:

- selects the smallest complete graph;
- uses current evidence or explicitly imaginative inputs;
- respects human and runtime authority;
- uses least-privileged tools;
- produces medium-appropriate typed artifacts;
- preserves stable marker IDs through handoffs;
- verifies the exact result;
- records unknowns, failures, rollback, and residuals honestly;
- remains coherent without generic prompt bloat;
- distinguishes static proof from live behavioral proof.

## Documentation

Start with [Manuals and Guides](docs/MANUALS.md).

## Reviewed plans and exact execution twins

All 32 genuine planning/execution pairs now use a mandatory review-before-execution contract. A planner presents its completed plan, accepts requested changes and refinements, re-verifies and re-freezes the handoff, requests review of the revised version, and then asks for explicit consent to invoke only its canonical reciprocal executor. Alternate twins and inferred consent are rejected. See [Plan Review and Exact-Twin Execution Guide](docs/PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md).

## Template, tooling, and telemetry platform

MD 1.8.3 hardens the approval-bound project cleanup workflow. Destructive purge now has an explicit commit boundary: failures before deletion restore the complete project, while failures after quarantine data changes retain and report the residual quarantine instead of performing an unsafe partial restoration. Interactive decline uses a distinct exit code, cleanup receipts include measured duration, and the canonical test runner counts tests from structured JUnit XML rather than scraping human-readable pytest summaries. Every existing prompt, template, skill, exact twin, telemetry, evaluation, installer, and cross-platform capability is preserved.

- [Mastery Manual](docs/MD_MASTERY_MANUAL.md)
- [Template System Guide](docs/TEMPLATE_SYSTEM_GUIDE.md)
- [Logging and Telemetry Guide](docs/LOGGING_AND_TELEMETRY_GUIDE.md)
- [Cross-Platform Tooling Guide](docs/CROSS_PLATFORM_TOOLING_GUIDE.md)
- [TUI and Operator Experience Guide](docs/TUI_AND_OPERATOR_EXPERIENCE_GUIDE.md)
- [Template Registry](config/template_registry.json)

Resolve a prompt's templates with:

```bash
python tools/template_router.py MD-76 --profile comprehensive
```

Use the platform-native wrapper with:

```bash
python tools/platform_dispatch.py validate
python tools/platform_dispatch.py test
python tools/platform_dispatch.py cleanup-project -- /path/to/project --dry-run
```

## Deterministic generated views

Run `python tools/check_generated_reproducibility.py` to regenerate catalogs, the capability graph, and prompt-body audits in a clean temporary copy and compare them byte-for-byte with the distributed views.
