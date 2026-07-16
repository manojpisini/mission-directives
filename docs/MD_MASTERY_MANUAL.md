# Mission Directives Mastery Manual

**Version:** 1.8.3  
**Audience:** users, operators, prompt authors, maintainers, reviewers, and integrators  

This manual is the authoritative learning path for the suite. Start with [README](../README.md), use the [Template System Guide](TEMPLATE_SYSTEM_GUIDE.md) for artifact routing, and use the [Installation Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md) for project integration.

## How to use this manual

Read chapters 1–5 before operating a run. Read Exact Twin Review before any paired workflow. Read Installation and Cross-Platform Tooling before integrating a project. Maintainers should also read Schemas, Evaluation and Proof, and Release Engineering. Each chapter below includes commands, decision rules, verification, and failure checks specific to that subject.

## 1. Mental Model

Mission Directives is a compiled control plane for bounded language-model work. Prompts provide capability contracts; scenarios compose them; templates shape outputs; policies constrain authority; schemas make handoffs testable; tools compile and verify the graph. A run is complete only when its selected capability criteria and verification records pass.

### Operator procedure

1. Name the observable outcome and the authority boundary.
2. Select the smallest capability graph that owns that outcome.
3. Keep evidence, action, and verification as separate records.

### Verification evidence

- Confirm the mental model decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim mental model is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 2. Repository Map

The root holds canonical registries and policies. `prompts/` contains 199 permanent capability bodies. `templates/` contains reusable artifact contracts. `schemas/` defines machine-readable records. `evaluations/` stores fixtures and mutation definitions. `tools/` contains deterministic routing, validation, telemetry, skill, and platform utilities. `docs/` is the human learning layer.

### Operator procedure

1. Use `find prompts -maxdepth 1 -name "*.md"` to inspect capability bodies.
2. Use registries for lookup; do not edit generated catalogs directly.
3. Trace any output field back to its canonical source file.

### Verification evidence

- Confirm the repository map decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim repository map is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 3. Prompt Anatomy

Every prompt combines YAML identity metadata with an XML-like body. The frontmatter defines permanent ID, role, modes, evidence lane, dependencies, outputs, skills, exact twin, and required or conditional templates. The body defines identity, mission, authorization, tools, method, runtime markers, output contract, verification, stop conditions, and task-specific completion.

### Operator procedure

1. Run `python tools/md.py explain MD-124`.
2. Compare frontmatter dependencies with body contracts.
3. Reject a prompt whose declared outputs or templates do not match the request.

### Verification evidence

- Confirm the prompt anatomy decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim prompt anatomy is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 4. Control Prompts

The control layer establishes runtime context, evidence discipline, authorization, action-risk classification, and closure. Load control contracts once per run, then load only the selected capability graph. This prevents policy drift while avoiding the cost of injecting all prompts.

### Operator procedure

1. Load MD-00 through MD-04 once.
2. Record mode, assurance, evidence lane, and authority.
3. Do not repeat control prose in every downstream prompt context.

### Verification evidence

- Confirm the control prompts decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim control prompts is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 5. Scenario Runtime

A scenario is a precompiled graph for an end-to-end outcome. Use `python tools/md.py lookup "<terms>"`, inspect with `explain`, then generate a dry-run plan. Prefer a scenario when it already owns the complete outcome; otherwise select one primary prompt and only its declared dependencies.

### Operator procedure

1. Run lookup and inspect confidence.
2. Prefer exact IDs and complete scenarios over keyword guesses.
3. Generate a dry-run plan before mutation.

### Verification evidence

- Confirm the scenario runtime decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim scenario runtime is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 6. Exact Twin Review

Thirty-two investigative prompts have one reciprocal executive twin. The planner freezes a handoff, presents it for review, incorporates changes, invalidates old approval, re-freezes, requests review again, and separately asks for execution consent. The executor rejects any handoff whose planner ID, hash, review receipt, or consent does not match its declared twin.

### Operator procedure

1. Freeze the handoff hash.
2. Present the full plan and collect changes.
3. After approval, request separate consent for the named twin only.

### Verification evidence

- Confirm the exact twin review decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim exact twin review is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 7. Template System

`template_routes` contains unconditional contracts. `conditional_template_routes` contains compatible artifact templates activated only by requested output, audience, platform, or lifecycle task. Resolve routes with `python tools/template_router.py MD-76 --artifact user-manual`. Never load all compatible templates by default.

### Operator procedure

1. Resolve required routes.
2. Activate conditional templates from explicit artifact triggers.
3. Validate all instantiated templates and record the route receipt.

### Verification evidence

- Confirm the template system decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim template system is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 8. Documentation Production

MD-75 investigates the repository, audiences, build, configuration, interfaces, releases, binaries, and existing docs. MD-76 produces the reviewed documentation system. Documentation pages require parent backlinks, prerequisites, forward links, canonical references, ownership, freshness triggers, tested commands, and explicit unknowns.

### Operator procedure

1. Run MD-75 read-only.
2. Review and refine the documentation architecture.
3. Authorize MD-76 only after the final handoff is approved.

### Verification evidence

- Confirm the documentation production decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim documentation production is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 9. Decks and Visual Assets

Deck templates define slide-level decisions, evidence, speaker notes, visual hierarchy, and accessibility. Code-native diagrams, vectors, infographics, and animated illustrations route through `visual-assets` only when a visual artifact is genuinely needed. Editable SVG/HTML/CSS/JS source and text alternatives are part of completion.

### Operator procedure

1. Choose the deck template for audience and decision.
2. Route visual primitives through visual-assets when necessary.
3. Check readability, source editability, text alternatives, and export integrity.

### Verification evidence

- Confirm the decks and visual assets decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim decks and visual assets is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 10. Skill Governance

Skill selection begins with capability need, not installation status. Existing skills are matched through MD-192 and executed through MD-196. Missing capabilities route through discovery, qualification, locked installation, or local creation. Outputs remain quarantined until verified. Global paths are resolved per application and OS, never stored with personal usernames.

### Operator procedure

1. Resolve paths with `python tools/agent_paths.py all`.
2. Prove task fit and provenance.
3. Verify identical SKILL.md hashes across selected applications.

### Verification evidence

- Confirm the skill governance decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim skill governance is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 11. Bounded Loops

MD-197 wraps a prompt, scenario, or skill only when a finite queue or measurable improvement exists. MD-198 adjudicates continuation independently. A loop stops on verified success, completed queue, plateau, budget exhaustion, stale evidence, lost authority, unsafe side effects, repeated failure without a changed hypothesis, or human stop.

### Operator procedure

1. Define queue or score and budget.
2. Execute one isolated iteration.
3. Use independent exit adjudication and stop on plateau or loss of authority.

### Verification evidence

- Confirm the bounded loops decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim bounded loops is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 12. Daily TOML Logging

Every suite event appends to `.prompt_suite/logs/YYYY-MM-DD.toml`. Events include run and span IDs, local and UTC timestamps, action, status, duration, prompt or scenario, tool, metrics, context, references, and sanitized error text. Sensitive keys and secret-like values are redacted before serialization. Runtime logs are excluded from the integrity manifest.

### Operator procedure

1. Set or capture a run ID.
2. Use span IDs to correlate start and finish.
3. Query the daily file and verify redaction before sharing logs.

### Verification evidence

- Confirm the daily toml logging decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim daily toml logging is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 13. Cross-Platform Tooling

Canonical behavior lives in Python. Bash and PowerShell wrappers expose equivalent arguments, progress, exit codes, receipts, and telemetry. `tools/platform_dispatch.py` selects PowerShell on Windows and Bash on Linux or macOS. CI executes supported wrappers on all three operating-system families.

### Operator procedure

1. Use `platform_dispatch.py` for supported tools.
2. Compare wrapper exit code and receipt with canonical Python behavior.
3. Test paths with spaces and Unicode.

### Verification evidence

- Confirm the cross-platform tooling decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim cross-platform tooling is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 14. Installation

Run `install.sh`, `install.ps1`, or `install.py` with a project path. The installer stages the copy, promotes it to `./prompts`, maintains a `.gitignore` block, keeps `docs/` tracked, creates runtime directories, and synchronizes only AGENTS.md and CLAUDE.md. Existing unmanaged instructions are never overwritten.

### Operator procedure

1. Run installer with `--dry-run`.
2. Install or update with an explicit project path.
3. Verify gitignore markers, tracked docs, guidance blocks, and receipts.

### Verification evidence

- Confirm the installation decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim installation is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

### Cleanup and uninstall

Use `cleanup.py`, `cleanup.sh`, or `cleanup.ps1` from the distribution or installed `prompts/` copy. Start with `--dry-run`; review removed and preserved paths; then confirm interactively, use `--yes` for the current preview, or pass the preview's approval token. Cleanup revalidates the installed suite identity, binds approval to the current tree and managed-file hashes, removes only managed text blocks, quarantines managed paths, restores the project if a pre-purge step fails, and preserves nonempty `docs/` or any generic directory not proven to be installer-owned. Destructive purge is a commit boundary: if deletion has already changed quarantine data, cleanup never performs an unsafe partial restoration; it reports a residual quarantine and exits distinctly for operator recovery.

Verify that `prompts/` and `.prompt_suite/` are absent, unmanaged instructions remain byte-equivalent, `.gitignore` no longer contains the managed block, preexisting directories remain, and no `.md-cleanup-*` staging or lock artifact remains. See [Project Cleanup and Uninstall](PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md).

## 15. Daily Operation

Start with keyword lookup, inspect the candidate, choose mode and assurance, resolve required templates, produce a dry-run, obtain approval where required, execute within authority, validate artifacts and schemas, record residuals, and close only with evidence. Keep the selected graph minimal.

### Operator procedure

1. Lookup, explain, and plan.
2. Resolve evidence, authority, templates, and skills.
3. Execute, verify, log residuals, and close honestly.

### Verification evidence

- Confirm the daily operation decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim daily operation is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 16. Evidence and Runtime Markers

Use `@EVIDENCE` for traceable sources, `?UNKNOWN` for unresolved facts, `#FINDING` for gaps or contradictions, `+ACTION` for bounded changes, `=VERIFY` for objective acceptance evidence, and `!STOP` for hard authority or safety boundaries. Preserve IDs across handoffs.

### Operator procedure

1. Create stable IDs at discovery.
2. Carry the same IDs through plan and execution.
3. Never convert UNKNOWN or STOP into a positive claim.

### Verification evidence

- Confirm the evidence and runtime markers decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim evidence and runtime markers is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 17. Schemas and Contracts

Schemas are executable boundaries, not decorative documentation. Producers declare the schema they emit; consumers validate before use. Test healthy and invalid examples. A schema mismatch blocks execution rather than being silently coerced.

### Operator procedure

1. Run JSON Schema validation before consumption.
2. Test one healthy and one invalid sample.
3. Block on mismatches and preserve the error evidence.

### Verification evidence

- Confirm the schemas and contracts decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim schemas and contracts is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 18. Evaluation and Proof

Deterministic tests prove structure, graph consistency, templates, tools, links, schemas, path hygiene, and manifest integrity. Fixtures and mutations test expected failure modes. Live-model and human-reviewed golden runs remain separate evidence surfaces and must not be inferred from structural success.

### Operator procedure

1. Run deterministic tests.
2. Review mutation and fixture failures.
3. Separate structural proof from live-model and human proof.

### Verification evidence

- Confirm the evaluation and proof decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim evaluation and proof is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 19. Security and Privacy

Use least privilege, explicit authority, secret redaction, safe examples, quarantine for third-party outputs, and fail-closed behavior for unknown locks or mismatched twins. Do not log credentials, embed personal home paths, execute unknown binaries, or convert a drafting request into an external action.

### Operator procedure

1. Minimize permissions and retained data.
2. Redact both sensitive keys and secret-like values.
3. Quarantine untrusted skill and binary output.

### Verification evidence

- Confirm the security and privacy decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim security and privacy is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 20. Release Engineering

The active version comes only from `VERSION`. Generated catalogs are rebuilt from canonical prompt and template metadata. A release runs tests, audits, generated-file comparison, link checking, schema validation, manifest sealing, ZIP integrity, and clean-extraction verification. Historical compatibility records remain immutable.

### Operator procedure

1. Read VERSION once.
2. Rebuild generated artifacts and compare for drift.
3. Seal manifest, archive, extract, and rerun non-mutating proof.

### Verification evidence

- Confirm the release engineering decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim release engineering is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 21. Troubleshooting

Begin with the observable symptom. Check the selected prompt and mode, missing required inputs, template resolution, schema errors, exact-twin receipts, authority, platform dispatch, tool exit code, and daily log span. Reproduce with TUI disabled in CI-style output, then isolate the smallest failing contract.

### Operator procedure

1. Capture symptom and failing command.
2. Locate the run/span in telemetry.
3. Fix the smallest violated contract and rerun its focused test.

### Verification evidence

- Confirm the troubleshooting decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim troubleshooting is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## 22. Mastery Checklist

A proficient operator can route a request without loading the suite, explain evidence and authority, choose a scenario or prompt, resolve templates selectively, review exact-twin plans, govern skills and loops, inspect TOML telemetry, run cross-platform tools, validate schemas, and prove a release from a clean extraction.

### Operator procedure

1. Complete one read-only scenario.
2. Complete one reviewed exact-twin pair.
3. Install into a disposable project and verify clean extraction.

### Verification evidence

- Confirm the mastery checklist decision is represented in the run manifest or applicable receipt.
- Record the exact command, exit code, artifact path, and evidence timestamp.
- List unresolved unknowns, skipped platform checks, and human-review requirements explicitly.

### Failure checks

- Do not claim mastery checklist is complete when only file presence was checked.
- Reject stale versions, personal machine paths, silent substitutions, and unreviewed external effects.
- Re-run the focused validator after any change and inspect the corresponding TOML span.

## Command reference

```bash
python tools/md.py lookup "research report" --limit 8
python tools/md.py explain C-26
python tools/md.py plan C-26 --mode PLAN_ONLY --root . --dry-run
python tools/template_router.py MD-76 --artifact user-manual --artifact configuration-reference
python tools/agent_paths.py all
python tools/validate_templates.py
python tools/audit_prompt_bodies.py
python tools/check_documentation_links.py
python tools/check_script_parity.py
python tools/check_skill_lock.py
python tools/run_tests.py
python tools/validate_suite.py
python tools/build_manifest.py --check
```

## Linked manuals

- [README](../README.md)
- [Template System Guide](TEMPLATE_SYSTEM_GUIDE.md)
- [Logging and Telemetry Guide](LOGGING_AND_TELEMETRY_GUIDE.md)
- [Cross-Platform Tooling Guide](CROSS_PLATFORM_TOOLING_GUIDE.md)
- [TUI Guide](TUI_AND_OPERATOR_EXPERIENCE_GUIDE.md)
- [Installation and Project Integration](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md)
- [Project Cleanup and Uninstall](PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md)

## Glossary and invariant reference

### Capability

A permanent prompt identity with an owned observable outcome.

### Scenario

A compiled graph of capabilities for an end-to-end workflow.

### Required template

An artifact contract loaded for every invocation of a prompt.

### Conditional template

A compatible contract loaded only when an explicit output trigger applies.

### Evidence lane

The rules governing factual, hybrid, imaginative, or control claims.

### Handoff

A typed, frozen transfer between planner and executor.

### Exact twin

The only reciprocal executor a paired planner may offer.

### Receipt

A machine-readable record of review, approval, consent, installation, or verification.

### Residual

An unresolved risk, unknown, limitation, or incomplete external dependency.

### Quarantine

A state preventing unverified third-party output from becoming authoritative.

## Artifact inspection matrix

| Artifact | Canonical source | Primary validator | Human review question |
|---|---|---|---|
| Prompt body | `prompts/*.md` | `audit_prompt_bodies.py` | Does the method own the requested outcome? |
| Prompt catalog | `catalog.json` | `rebuild_suite_metadata.py` | Is this a generated view only? |
| Scenario | `SCENARIO_CATALOG.json` | `validate_suite.py` | Does it form the smallest coherent graph? |
| Template | `templates/**` | `validate_templates.py` | Does each section give domain-specific direction? |
| Skill | `skill_registry.json` | `check_skill_lock.py` | Is the capability genuinely required and trusted? |
| Daily log | `.prompt_suite/logs/*.toml` | `tests/test_logging.py` | Are secrets redacted and spans correlated? |
| Agent guidance | `AGENTS.md / CLAUDE.md` | `tests/test_agent_guidance.py` | Was unmanaged text preserved? |
| Installation receipt | `.prompt_suite/installation-receipt.json` | `tests/test_installer.py` | Did prompts, ignores, docs, and guidance match policy? |
| Manifest | `MANIFEST.json` | `build_manifest.py --check` | Does a fresh extraction match every hash? |

## Operational walkthrough 1: Repository research to verified report

This walkthrough applies the existing Mission Directives contracts to **repository research to verified report** without introducing a new capability.

### Steps

1. Run keyword lookup for the research outcome.
2. Inspect C-26 and its evidence assumptions.
3. Resolve the report template and only triggered supporting templates.
4. Create a source plan with freshness and authority requirements.
5. Collect evidence with stable IDs and contradiction records.
6. Draft findings separately from recommendations.
7. Validate citations, calculations, links, and residual unknowns.
8. Record verification and close without overstating behavioral proof.

### Required evidence

- Lookup receipt for `C-26` and the selected report template.
- Source register with freshness timestamps, authority classification, and contradiction handling.
- Claim-to-source matrix, calculation checks, citation validation, and final residual register.
- Report export hashes and reviewer disposition.

### Common failure modes

- Searching before defining the research decision or audience.
- Combining evidence and recommendation without showing the inference boundary.
- Using stale or circular sources as independent corroboration.
- Closing with unsupported certainty when material unknowns remain.


## Operational walkthrough 2: Full documentation system

This walkthrough applies the existing Mission Directives contracts to **full documentation system** without introducing a new capability.

### Steps

1. Run MD-75 in AUDIT_ONLY or PLAN_ONLY.
2. Inventory code, configuration, interfaces, builds, binaries, and existing docs.
3. Design hubs, canonical pages, backlinks, forward links, redirects, owners, and freshness triggers.
4. Present the plan and incorporate user changes.
5. Re-freeze and obtain approval.
6. Request consent for MD-76 only.
7. Generate the selected manual family and verify every command and link.
8. Publish only within authorized scope.

### Required evidence

- `MD-75` repository evidence map and frozen documentation-tree handoff.
- User review notes, revision history, final handoff hash, and explicit consent for `MD-76`.
- Per-page template conformance, link graph, command test results, and binary/configuration evidence.
- Documentation package manifest with owners and freshness triggers.

### Common failure modes

- Writing manuals before code, configuration, interfaces, and binaries are inventoried.
- Invoking an executor other than `MD-76`.
- Producing isolated pages with no hubs, backlinks, forward links, or ownership.
- Documenting commands or defaults from convention rather than verified behavior.


## Operational walkthrough 3: Feature implementation

This walkthrough applies the existing Mission Directives contracts to **feature implementation** without introducing a new capability.

### Steps

1. Route to the smallest feature scenario or MD-124.
2. Confirm acceptance criteria, affected files, platform support, and rollback.
3. Resolve only required technical and documentation templates.
4. Write failing tests before behavior changes.
5. Implement bounded changes and preserve compatibility.
6. Run focused and full tests.
7. Update documentation and telemetry within the same task.
8. Record residuals and exact verification evidence.

### Required evidence

- Requirement-to-test traceability and affected-file map.
- Failing test output captured before implementation and passing output after the change.
- Compatibility, migration, rollback, telemetry, and documentation diffs.
- Focused and full-suite verification receipts.

### Common failure modes

- Editing implementation before acceptance criteria and failure reproduction are stable.
- Bundling unrelated refactors with the feature.
- Passing unit tests while skipping integration, compatibility, or rollback checks.
- Updating code without updating the user-facing or operator-facing contract.


## Operational walkthrough 4: Audit-fix-verify loop

This walkthrough applies the existing Mission Directives contracts to **audit-fix-verify loop** without introducing a new capability.

### Steps

1. Use C-108 when repeated passes can reveal remaining findings.
2. Define the finite surface and severity model.
3. Audit without mutating.
4. Convert each validated finding into a bounded action.
5. Fix one coherent batch.
6. Verify original symptoms and adjacent behavior.
7. Re-audit only remaining surfaces.
8. Stop on verified closure, plateau, budget, or authority loss.

### Required evidence

- Initial finding register with severity, evidence, and affected surface.
- Action IDs linked one-to-one with verified findings.
- Before/after reproduction, adjacent regression results, and remaining-surface audit.
- Loop-exit decision with progress metric, plateau evidence, and residuals.

### Common failure modes

- Repeating the same audit without new evidence or a changed hypothesis.
- Fixing unvalidated scanner output.
- Counting iterations rather than measuring closed findings.
- Continuing after quality plateau, authority loss, or exhausted budget.


## Operational walkthrough 5: Visual asset batch

This walkthrough applies the existing Mission Directives contracts to **visual asset batch** without introducing a new capability.

### Steps

1. Create a finite asset inventory with dimensions, purpose, audience, and acceptance criteria.
2. Select visual templates and the visual-assets skill only when needed.
3. Use one outer loop item per asset.
4. Use an inner refinement loop only with a measurable rubric.
5. Preserve SVG/HTML/CSS/JS editable sources.
6. Check text alternatives, labels, contrast, responsive behavior, and export dimensions.
7. Verify each item independently.
8. Stop after the queue and quality thresholds pass.

### Required evidence

- Asset inventory containing purpose, placement, dimensions, format, and acceptance rubric.
- Per-asset source files, export files, and visual verification records.
- Accessibility checks for contrast, labels, text alternatives, motion, and responsive behavior.
- Queue completion and refinement-loop exit receipts.

### Common failure modes

- Generating assets without a finite inventory or placement context.
- Using visual polish as a substitute for communication accuracy.
- Flattening editable vectors into screenshots without need.
- Applying identical composition to every asset regardless of information structure.


## Operational walkthrough 6: Skill acquisition

This walkthrough applies the existing Mission Directives contracts to **skill acquisition** without introducing a new capability.

### Steps

1. Prove native prompts cannot meet the acceptance criteria cleanly.
2. Run find-skills and compare exact candidates.
3. Inspect provenance, permissions, source, lock, and expected outputs.
4. Install only the approved exact skill.
5. Resolve `.agents`, Claude Code, and OpenCode destinations per platform.
6. Verify identical SKILL.md hashes in all selected locations.
7. Keep outputs quarantined.
8. Promote only after conformance and artifact verification.

### Required evidence

- Capability-gap decision proving a skill is genuinely required.
- Candidate comparison, source provenance, permissions, lock state, and approval record.
- Resolved platform destinations and identical `SKILL.md` hashes.
- Quarantine and conformance records for first use.

### Common failure modes

- Installing a skill because it is popular or already mentioned.
- Treating presence on disk as trust or task fit.
- Writing to only one agent application while claiming global availability.
- Promoting output before provenance and artifact verification pass.


## Operational walkthrough 7: Project installation

This walkthrough applies the existing Mission Directives contracts to **project installation** without introducing a new capability.

### Steps

1. Run the installer with --dry-run and an absolute project path.
2. Review the copy, ignore, runtime-directory, and guidance actions.
3. Install to ./prompts through staging.
4. Verify the managed .gitignore block excludes prompts and internal runtime outputs but not docs.
5. Confirm AGENTS.md and CLAUDE.md preserve unmanaged content.
6. Run lookup and validation from the installed prompts directory.
7. Inspect installation and guidance receipts.
8. Retain the backup until the updated installation passes.

### Required evidence

- Installer dry-run JSON and reviewed action list.
- Pre-install hashes or backups for existing managed files.
- Post-install tree, `.gitignore` managed block, and guidance synchronization receipt.
- Validation run executed from `<project>/prompts` and rollback readiness record.

### Common failure modes

- Running replacement without retaining a recoverable backup.
- Ignoring `docs/` or overwriting unmanaged agent instructions.
- Copying runtime logs, caches, or machine receipts into the project.
- Assuming installation succeeded without executing lookup and validation in the installed location.


## Operational walkthrough 8: Cross-platform release

This walkthrough applies the existing Mission Directives contracts to **cross-platform release** without introducing a new capability.

### Steps

1. Read the active version from VERSION.
2. Regenerate canonical derived files.
3. Run Linux, Windows, and macOS CI jobs.
4. Exercise Bash and PowerShell wrappers with spaces and Unicode paths.
5. Compare exit codes, output, logs, and receipts.
6. Remove caches and runtime logs.
7. Build and check the manifest.
8. Archive, extract, and rerun non-mutating proof.

### Required evidence

- Version and release-ID consistency report.
- Linux, Windows, and macOS job outputs with wrapper-level exit codes.
- Generated-artifact reproducibility comparison and path-hygiene scan.
- Manifest check, archive checksum, ZIP test, and clean-extraction verification.

### Common failure modes

- Using an Ubuntu-only run to claim PowerShell or Windows parity.
- Sealing a manifest before regenerating catalogs and test receipts.
- Including caches, telemetry logs, or local receipts in the archive.
- Reporting success from the working tree without checking the extracted package.


## Operational walkthrough 9: Incident investigation

This walkthrough applies the existing Mission Directives contracts to **incident investigation** without introducing a new capability.

### Steps

1. Classify severity and containment authority.
2. Collect immutable evidence and preserve timestamps.
3. Separate facts, inferences, disputed claims, and unknowns.
4. Build a timeline with source lineage.
5. Identify affected components and trust boundaries.
6. Recommend reversible containment before permanent repair.
7. Verify recovery and monitor recurrence indicators.
8. Document residual risk and escalation ownership.

### Required evidence

- Incident scope, severity, containment authority, and evidence-preservation record.
- Immutable timeline with source lineage and confidence labels.
- Affected component and trust-boundary analysis.
- Recovery verification, recurrence indicators, and residual-risk ownership.

### Common failure modes

- Changing evidence during collection or losing timestamp context.
- Presenting hypotheses as confirmed facts.
- Implementing permanent changes before reversible containment is evaluated.
- Closing the incident when service is restored but root cause and recurrence controls remain unknown.


## Operational walkthrough 10: Configuration manual

This walkthrough applies the existing Mission Directives contracts to **configuration manual** without introducing a new capability.

### Steps

1. Inventory every config source, field, default, type, allowed value, and secret status.
2. Document precedence across flags, environment, files, profiles, and defaults.
3. Provide Windows, Linux, and macOS paths where behavior differs.
4. Use safe examples with no real credentials.
5. Document reload requirements and side effects.
6. Include validation errors and troubleshooting.
7. Test examples against the implementation.
8. Link to deployment, security, and upgrade guides.

### Required evidence

- Configuration-source inventory and precedence matrix.
- Field-level reference with types, defaults, allowed values, secret classification, and restart behavior.
- Platform-specific path resolution and validated safe examples.
- Error-message, validation, reload, and troubleshooting test results.

### Common failure modes

- Documenting only one configuration source while flags or environment variables override it.
- Publishing real secrets in examples.
- Assuming defaults from library conventions.
- Omitting whether a change is dynamic, restart-bound, destructive, or migration-sensitive.


## Operational walkthrough 11: Built binary manual

This walkthrough applies the existing Mission Directives contracts to **built binary manual** without introducing a new capability.

### Steps

1. Inventory executable and package names.
2. Record version, platform, architecture, source revision, checksum, signature, SBOM, and provenance.
3. Document installation and companion files.
4. Document commands, flags, environment, exit codes, signals, logs, sockets, and permissions.
5. Record dynamic dependencies and runtime paths.
6. Provide debug, crash, rollback, update, uninstall, and cleanup procedures.
7. Use only safe binary inspection or authorized execution.
8. Verify every platform claim or mark it unknown.

### Required evidence

- Binary inventory with product, executable, package, version, revision, platform, and architecture.
- Checksums, signatures, SBOM/provenance references, companion-file layout, and dynamic dependencies.
- Verified command tree, exit codes, signals, logs, sockets, permissions, and runtime paths.
- Update, rollback, crash-debug, uninstall, and cleanup walkthrough results.

### Common failure modes

- Running an unknown binary merely to fill documentation gaps.
- Confusing package metadata with observed runtime behavior.
- Claiming architecture or platform support from filenames alone.
- Omitting residual files, services, state, or permissions from uninstall guidance.


## Operational walkthrough 12: Prompt authoring

This walkthrough applies the existing Mission Directives contracts to **prompt authoring** without introducing a new capability.

### Steps

1. Choose one observable outcome and permanent identity.
2. Declare role, evidence lane, modes, risk, dependencies, outputs, skills, and template routes.
3. Keep required templates minimal and conditional templates trigger-based.
4. Write task-specific method and completion criteria.
5. Add authorization, tool, marker, stop, and verification contracts.
6. For pairs, declare one reciprocal exact twin.
7. Add healthy, problematic, adversarial, and mutation coverage.
8. Rebuild catalogs and prove no self-dependency or collision.

### Required evidence

- Capability identity and ownership rationale.
- Frontmatter/schema validation and dependency graph result.
- Healthy, problematic, adversarial, and mutation fixtures tied to completion criteria.
- Catalog regeneration, self-dependency scan, and exact-pair reciprocity evidence where applicable.

### Common failure modes

- Creating a new prompt when an existing capability owns the outcome.
- Using generic completion criteria or unbounded tool authority.
- Making many templates required to avoid explicit conditional routing.
- Changing generated catalogs directly or declaring a non-reciprocal pair.
## Governed prompt addition

A prompt becomes part of Mission Directives only after identity allocation, canonical normalization, structural source quarantine, routing integration, taxonomy and crosswalk updates, fixtures, deterministic proof, and manifest sealing. Use `MD-199` when an agent must assess overlap or refine the prompt; use `tools/add_prompt.py` when the source and title are already resolved. The implementation stages the complete suite, validates all prompt/template/skill/pack references, regenerates derived artifacts, runs tests by default, and promotes only a verified diff under a short exclusive lock. Full operational details and failure recovery are in [Prompt Addition and Registration Guide](PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md).

