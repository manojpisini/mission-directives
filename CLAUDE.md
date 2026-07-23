<!-- BEGIN MD MANAGED GUIDANCE -->
## MD prompt routing and productivity guidance

This managed section connects **CLAUDE.md** to Mission Directives **1.8.3** at `.`. Preserve instructions outside this block. Regenerate this block with `python tools/sync_agent_guidance.py --project-root .` instead of editing it manually.

**Scope note:** Only AGENTS.md and CLAUDE.md are managed. Other agent instruction filenames are intentionally excluded.

### When to invoke MD

- Treat the standalone keyword `MD` as an explicit request to use this suite.
- Pass the full user request to the deterministic keyword-context router. It handles exact IDs, natural intent, depth and assurance modifiers, shortcuts, combinations, scenarios, and bounded workflow graphs without opening prompt bodies.
- If the user supplies an exact `MD-###` or `C-###`, the router resolves that identifier directly; inspect the selected target with `explain` before execution.
- If `MD` or `md` is followed by ordinary words, preserve the full wording for context parsing. Do not guess a prompt ID from memory or scan the prompt directory.
- Even without the keyword, use MD when the request clearly benefits from its evidence, authorization, skill, loop, artifact, or verification contracts.
- Use `MD-191` only for ambiguities whose answers change routing, authority, evidence lane, output medium, budget, or acceptance criteria. Do not interrogate the user about details that can be safely inferred or deferred.

### Fast intent-routing workflow

```bash
python tools/md.py route "<full user request>"
python tools/md.py lookup "<operator discovery terms>" --limit 8
python tools/md.py compare <TARGET_A> <TARGET_B>
python tools/md.py explain <MD-ID|C-ID|DEPARTMENT_PACK>
python tools/md.py plan <target> --mode <MODE> --root . --dry-run
```

The router performs keyword-context parsing, policy shortcuts, metadata lookup, and deterministic selection in that order. Use `compare` when close routes need an authority or verification-cost decision. If no route meets the confidence threshold, ask one route-changing question and rerun `route`.

### Productivity shortcuts

| Keyword after `MD` | Preferred route | Purpose |
|---|---|---|
| `clarify` | `MD-191` | ask only route-changing questions |
| `skill` | `MD-192 -> MD-196` | prove genuine skill need and execute an exact skill |
| `find skill` | `MD-193 -> MD-194 or MD-195` | discover, qualify, install, or create a missing reusable skill |
| `loop` | `MD-197 -> MD-198` | bounded repeat execution with independent exit adjudication |
| `audit fix verify` | `C-108` | convergent audit, remediation, and verification |
| `research` | `C-26` | deep research report |
| `report` | `C-95` | professional report pipeline |
| `add prompt` | `MD-199 / tools/add_prompt.py` | review, normalize, register, test, and transactionally add one prompt |
| `prompt` | `C-94` | prompt creation, optimization, evaluation, and repair |
| `feature` | `C-63` | feature delivery |
| `visual assets` | `C-109` | code-native vector, illustration, infographic, and presentation-asset production |
| `strudel` | `C-110` | Strudel composition and bounded refinement |
| `productivity` | `MD-138` | personal knowledge, productivity, and work system |

These shortcuts are defaults, not blind dispatch rules. Confirm that the route owns the requested outcome and that its authority and evidence assumptions fit.

### Adding a prompt

- Use `MD-199` when the prompt needs overlap analysis, refinement, routing decisions, or agentic review.
- Use `python tools/add_prompt.py --source <file.md> --title "<title>"` for a deterministic transactional addition.
- Never copy a prompt into the prompts directory manually; the catalog, identity registry, graph, templates, skills, fixtures, evaluations, tests, validation, and manifest must remain synchronized.

### Canonical selection order

1. Run `python tools/md.py route "<full user request>"`.
2. If needed, compare close candidates with `python tools/md.py compare <targets...>`.
3. Inspect every selected target with `python tools/md.py explain <target>`.
4. Use `catalog.json` for prompt metadata and `SCENARIO_CATALOG.json` for composite workflows.
5. Use `PROMPT_EXECUTION_ORDER.md` for phase order, modes, branches, locks, and completion semantics.
6. Load only the selected bodies from `prompts/` plus their declared prerequisites.
7. Consult schemas, policies, `skill_registry.json`, `policies/auto_prompt_policy.json`, and `policies/loop_execution_policy.json` only when triggered.

### Efficiency and anti-bloat rules

- Select the **smallest coherent graph** that owns the observable outcome.
- **Do not load every prompt**, every department pack entry, or every skill into context.
- Do not read prompt bodies during intent selection; `tools/keyword_context.py`, policy metadata, catalogs, and scenarios own that stage.
- Load the five control prompts once per run, then only selected capabilities and required handoffs.
- Prefer a composite scenario when it already expresses the complete workflow; otherwise start from one primary prompt.
- Invoke a skill through `MD-192` and `MD-196` only when its genuine capability is needed. Installed does not mean required.
- Discover, install, or create a skill through `MD-193` to `MD-195` only when native execution cannot satisfy the acceptance criteria cleanly.
- Loop through `MD-197` and `MD-198` only for a finite queue or measurable improvement. Stop on verified success, plateau, budget exhaustion, stale evidence, lost authority, or human stop.
- Keep skill output quarantined until the routed verification step accepts the exact artifact.
- Route code-native illustrations, vectors, infographics, diagrams, and presentation assets through the exact local `visual-assets` skill when genuinely required; route Strudel music code through `strudel`.
- Do not imply publication, sending, submission, deployment, merging, purchasing, or other external action from a draft or plan.
- For every genuine planning/execution pair, present the completed plan for user review, incorporate requested changes, re-verify and re-freeze it, request review again, then ask for explicit consent to invoke only the exact execution twin declared in `paired_prompt_id`. Never substitute another executor or infer consent from the original task.

### Git and workflow safety

- Write commit messages in past tense, declarative form without first-person pronouns: `Fixed ...`, `Updated ...`, `Removed ...`.
- Before committing workflow, wrapper, manifest, generated artifact, or guidance changes, run the smallest local checks that cover the touched path and rerun `python tools/build_manifest.py` when any tracked file changed.
- Do not seal ignored or machine-local outputs into `MANIFEST.json`; generated receipts such as `BODY_QUALITY_AUDIT.*`, `EVALUATION_STATUS.json`, `TEST_RESULTS.json`, `VALIDATION.json`, `.prompt_suite/results/`, `.prompt_suite/runtime/`, and `.venv/` must remain out of the manifest.
- Keep GitHub Actions on Node 24-compatible action versions; do not downgrade `actions/checkout` or `astral-sh/setup-uv` to versions that emit Node 20 deprecation warnings, and keep `astral-sh/setup-uv` configured with `activate-environment: 'true'` when later steps call `python` or `uv pip` directly.
- For Python workflow wrappers, prefer the active virtual environment's Python before PATH fallbacks so smoke tests use the same dependencies installed by CI.
- Before claiming workflow success, verify the pushed GitHub Actions run completed successfully on ubuntu-latest, windows-latest, and macos-latest.

### Paired plan review workflow

- Inspect the exact reciprocal twin with `python tools/md.py pair-status <PLANNING-MD-ID> --handoff-ready --review-status approved`.
- Requested changes invalidate prior approval and consent; revise, re-freeze under a new hash, and request review again.
- Execute only after the user approves the final frozen plan and explicitly consents to the named exact execution twin.

### Project cleanup

- Preview removal with `python tools/cleanup.py . --dry-run`.
- Run approved cleanup with `python tools/cleanup.py . --yes` or a reviewed approval token.
- Cleanup removes only validated Mission Directives-managed paths and text blocks; preserve unrelated project content and nonempty docs.

### Core locations

- Prompt bodies: `prompts/`
- Prompt catalog: `catalog.json`
- Scenario catalog: `SCENARIO_CATALOG.json`
- Execution guide: `PROMPT_EXECUTION_ORDER.md`
- Skill registry: `skill_registry.json`
- CLI: `tools/md.py`
- Manuals: `docs/MANUALS.md` and `docs/`

### Honest completion

A route is not complete merely because a prompt or skill ran. Completion requires the selected prompt's task-specific criteria, `=VERIFY:{id}` evidence, explicit unknowns and residuals, and the applicable human approval or external-action gate.
<!-- END MD MANAGED GUIDANCE -->
