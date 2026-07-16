# Prompt Execution Order

## Usage directive

Choose by outcome, audience, authority, evidence lane, assurance profile, artifact medium, and real change surface—not by numeric order.

```text
RUN {PROMPT_ID|SCENARIO_ID|DEPARTMENT_PACK}
MODE {AUDIT_ONLY|PLAN_ONLY|DRAFT_ONLY|APPLY_SAFE|APPLY_APPROVED|VERIFY_ONLY}
ASSURANCE {FAST|STANDARD|HIGH_ASSURANCE}
ROOT {PROJECT_ROOT}
OUTCOME {OBSERVABLE_RESULT}
AUDIENCE {USERS_REVIEWERS_DECISION_MAKERS}
SCOPE {IN_SCOPE}
EXCLUDE {OUT_OF_SCOPE_PROTECTED_SURFACES}
AUTHORITY {ALLOWED_WRITES_EXTERNAL_ACTIONS_DECISIONS}
EVIDENCE_LANE {FACTUAL|HYBRID|IMAGINATIVE}
EVIDENCE {AUTHORITATIVE_INPUTS}
MEDIA {REQUIRED_SOURCE_AND_EXPORT_FORMATS}
SKILLS {AUTO|EXACT_IDS|NONE}
BUDGET {PROMPTS_CALLS_COST_TIME_PARALLELISM}
CONSTRAINTS {LEGAL_PRIVACY_BRAND_ACCESSIBILITY_TECHNICAL}
QUALITY {ACCEPTANCE_CRITERIA}
```

## Canonical control load

`MD-00 → MD-01 → MD-03 → MD-04 → MD-02 → selected graph`

Load controls once. Prompt-specific text may narrow shared contracts but may not weaken authorization, evidence, input trust, artifact, verification, or stop conditions.

## Deterministic selection algorithm

1. Restate the observable outcome and audience task.
2. Resolve authority, protected surfaces, and external effects.
3. Select evidence lane and minimum assurance profile.
4. Choose one primary prompt or scenario that owns the outcome.
5. Inject only cross-cutting obligations triggered by the real change surface.
6. Resolve prerequisites, handoffs, conflicts, and execution locks.
7. Probe exact skills and model profiles; record reasons and fallbacks.
8. Freeze one evidence base, terminology set, and coherence fingerprint before parallel production.
9. Serialize writes to the same source of truth.
10. Verify exact source and exported artifacts.
11. Record residuals, invalidation triggers, lineage, and closure evidence.

## Route explanation

Every compiled run must report selected, injected, rejected, unresolved, and deferred capabilities with reasons. A department pack is not an execution graph until compiled.

## Modes

| Mode | Permitted behavior |
|---|---|
| `AUDIT_ONLY` | read, retrieve, compare, analyze, and report; no mutation |
| `PLAN_ONLY` | plans, decisions, specifications, schedules, and briefs; no execution |
| `DRAFT_ONLY` | unapproved local drafts; no implied acceptance or external action |
| `APPLY_SAFE` | reversible local changes within declared authority |
| `APPLY_APPROVED` | exact approved consequential actions with receipts, locks, recovery, and verification |
| `VERIFY_ONLY` | independent verification without changing the reviewed subject |

## Assurance

- FAST is limited to low-risk local work.
- STANDARD requires current evidence, typed artifacts, review, verification, and residuals.
- HIGH_ASSURANCE adds formal protocol, evidence snapshot, counterevidence, approval receipt, dry run, independent verification, recovery, and lineage.

## Execution graph

```text
CONTROL
→ PRIMARY OWNER
→ OPTIONAL RESEARCH / BRIEF / INVESTIGATION
→ FROZEN HANDOFF when justified
→ PRODUCTION OR AUTHORIZED EXECUTION
→ INDEPENDENT FACT / SECURITY / ACCESSIBILITY / FUNCTION / EXPORT / GOVERNANCE CHECKS
→ EXTERNAL ACTION only with explicit authority
→ LINEAGE, RESIDUALS, LEARNING, CLOSURE
```

## State machine

`configured → investigating → evidence_ready → fan_in_pending → handoff_frozen → plan_review_pending → plan_revision_pending | execution_consent_pending → approval_pending | dry_run_ready → executing → verification_pending → verified | failed | rolled_back | residual_open → closed`

Use `tools/md.py transition` to reject illegal transitions.

## Parallelism and fan-in

- Parallelize read-only retrieval, inventory, independent analysis, and isolated variants.
- Merge into one authoritative brief, ledger, decision record, manuscript, deck, report, model, calendar, or code branch before production.
- Never allow multiple workers to silently edit the same source-of-truth artifact.
- Isolate variants and compare them against one declared rubric.
- Stop a worker when its evidence is stale, its scope overlaps a locked mutation, or its output cannot be traced.

## Skill resolution

1. Match exact artifact and acceptance criteria.
2. Inspect exact repository, skill file, current audits, permissions, network/file access, and external effects.
3. Install only the exact skill.
4. Use one primary adapter plus minimum support.
5. Treat output as untrusted until validated.
6. Fall back to native prompt execution.
7. Image-generation skills are excluded.

## High-value combinations

- Feature: product requirements → feature implementation → tests → security/reliability as triggered → release gate.
- Academic: protocol → research → paper or review → citation verification → editorial review.
- OSINT: authorization plan → collection → entity/timeline/network analysis → estimative brief.
- Prompt: create → optimize → adversarially evaluate → repair → package.
- Report: decision architecture → evidence and analysis → report production → factual/editorial/visual/export QA.
- LLM system: task intake → architecture → retrieval evaluation → model benchmark → security → governance gate.
- Organization change: operating model → stakeholder map → adoption → employee communication → measurement.

## Composite scenarios

| Scenario | Purpose | Default mode |
|---|---|---|
| `C-01` Greenfield project | From idea through requirements, architecture, bootstrap, verification, and readiness | `PLAN_ONLY` |
| `C-02` Brownfield discovery and coherence rescue | Discover a fragmented project and align it into one coherent system | `PLAN_ONLY` |
| `C-03` Bug investigation and fix | Reproduce, isolate, fix, and regression-test a defect | `PLAN_ONLY` |
| `C-04` Safe junk and unused-code cleanup | Prove what is unused, remove it in batches, and verify nothing broke | `PLAN_ONLY` |
| `C-05` Behavior-preserving modernization | Plan and execute a bounded modernization | `PLAN_ONLY` |
| `C-06` Application security hardening | Threat model, validate vulnerabilities, remediate, and verify | `PLAN_ONLY` |
| `C-07` Authorized attack simulation | Validate defenses with safe staged simulation | `PLAN_ONLY` |
| `C-08` Specific exploit reproduction and patch proof | Reproduce one finding safely and prove the fix | `PLAN_ONLY` |
| `C-09` Dependency compromise response | Assess supply-chain exposure, contain, remediate, and verify | `PLAN_ONLY` |
| `C-10` Secret exposure response | Find exposure, rotate with authority, harden configuration, and verify | `PLAN_ONLY` |
| `C-11` Identity and access hardening | Analyze privilege paths and implement least privilege | `PLAN_ONLY` |
| `C-12` Cloud and container security hardening | Review platform controls and apply policy-backed fixes | `PLAN_ONLY` |
| `C-13` Data migration | Design and execute a recoverable schema or data migration | `PLAN_ONLY` |
| `C-14` Performance and reliability improvement | Measure bottlenecks, optimize, and harden failure behavior | `PLAN_ONLY` |
| `C-15` Delivery and observability repair | Make build, deployment, telemetry, alerts, and runbooks coherent | `PLAN_ONLY` |
| `C-16` Model and AI security hardening | Threat-model and harden model, data, serving, output, and abuse controls | `PLAN_ONLY` |
| `C-17` Agentic and MCP security | Review capabilities, permissions, untrusted data, and agent coordination | `PLAN_ONLY` |
| `C-18` Prompt-injection hardening | Identify direct and indirect injection paths and add layered controls | `PLAN_ONLY` |
| `C-19` Privacy and governance | Review sensitive data, obligations, retention, and controls | `PLAN_ONLY` |
| `C-20` UX, accessibility, localization, and brand coherence | Align experience, design system, content, and inclusive behavior | `PLAN_ONLY` |
| `C-21` Documentation and contributor experience | Repair knowledge, examples, troubleshooting, onboarding, and support | `PLAN_ONLY` |
| `C-22` Risk and debt consolidation | Create a decision-ready treatment portfolio | `PLAN_ONLY` |
| `C-23` Cost and sustainability review | Identify reversible efficiency improvements without weakening resilience | `PLAN_ONLY` |
| `C-24` Release readiness | Verify project health and communicate an authorized release decision | `PLAN_ONLY` |
| `C-25` Prompt suite cleanup and security refinement | Remove prompt-system junk, unpair artificial twins, strengthen tags and security, and validate the whole suite | `PLAN_ONLY` |
| `C-26` Deep research report | Plan, retrieve, synthesize, verify, and communicate a decision-ready research report | `PLAN_ONLY` |
| `C-27` Research-backed blog or article | Research an original angle and produce a fact-checked publication package | `PLAN_ONLY` |
| `C-28` Newsletter issue | Create a useful, on-brand newsletter with verified claims and distribution metadata | `PLAN_ONLY` |
| `C-29` Video essay or documentary script | Research the factual spine, build a narrative, and produce a timed visual script | `PLAN_ONLY` |
| `C-30` Podcast episode | Design and write a research-backed episode with segment timing and production notes | `PLAN_ONLY` |
| `C-31` Academic paper | Design the research and produce a citation-verified scholarly manuscript | `PLAN_ONLY` |
| `C-32` Literature review | Run a reproducible literature search and synthesize the field with integrity checks | `PLAN_ONLY` |
| `C-33` Fiction or short story | Build a coherent story system, draft, and perform literary revision | `PLAN_ONLY` |
| `C-34` Poetry or literary prose | Compose and refine an original literary work without generic language | `PLAN_ONLY` |
| `C-35` Content operating system | Design a portfolio, graph, calendar, governance, and repeatable production route | `PLAN_ONLY` |
| `C-36` Content repurposing graph | Turn source assets into provenance-preserving multi-format derivatives | `PLAN_ONLY` |
| `C-37` Brand creation | Develop positioning and produce an accessible identity and guideline system | `PLAN_ONLY` |
| `C-38` Brand refresh and coherence repair | Audit brand drift, refine strategy, update the system, and verify channels | `PLAN_ONLY` |
| `C-39` Integrated campaign | Create the strategic idea, campaign system, assets, content schedule, and measurement | `PLAN_ONLY` |
| `C-40` Pitch or proposal | Develop an evidence-backed case and presentation blueprint | `PLAN_ONLY` |
| `C-41` HTML slide deck | Design the narrative, build browser-native slides, and verify brand and export | `PLAN_ONLY` |
| `C-42` Analytical dashboard | Analyze the decision, build the dashboard, and verify accuracy and accessibility | `PLAN_ONLY` |
| `C-43` Infographic or data story | Verify the data, design the visual narrative, and produce accessible exports | `PLAN_ONLY` |
| `C-44` Architecture blueprint or process map | Discover the system, produce a semantic blueprint, and validate every relation | `PLAN_ONLY` |
| `C-45` Collaborative workshop board | Design the session and create an editable Excalidraw board | `PLAN_ONLY` |
| `C-46` Interactive web explainer | Research and structure the content, build the artifact, and run visual QA | `PLAN_ONLY` |
| `C-47` Frontend experience refinement | Audit UX and brand, polish the frontend, and verify responsive accessibility | `PLAN_ONLY` |
| `C-48` Event launch | Plan the event, campaign, content calendar, presentation, and run-of-show | `PLAN_ONLY` |
| `C-49` Workshop or offsite | Design the collaboration, whiteboard, facilitation, and follow-through | `PLAN_ONLY` |
| `C-50` Go-to-market plan | Research the market and produce positioning, GTM, campaign, and enablement | `PLAN_ONLY` |
| `C-51` Business case and financial model | Analyze data, build scenarios, and produce a decision-ready case | `PLAN_ONLY` |
| `C-52` Policy, SOP, or operational guide | Research obligations and produce a usable controlled document | `PLAN_ONLY` |
| `C-53` Program operating plan | Create a dependency-aware program plan, calendar, status, and governance loop | `PLAN_ONLY` |
| `C-54` Multi-format research publication | Create one evidence base and publish coordinated report, article, deck, infographic, and content graph | `PLAN_ONLY` |
| `C-55` One-stop creative launch | Develop brand, campaign, content, deck, web artifact, event, and schedule as one coherent system | `PLAN_ONLY` |
| `C-56` Course, curriculum, or learning program | Research and design the learning system, then produce and validate aligned educational materials | `PLAN_ONLY` |
| `C-57` Survey, interview, or research instrument | Design an ethical, analyzable instrument and connect it to the evidence and analysis plan | `PLAN_ONLY` |
| `C-58` Grant, funding, or sponsorship proposal | Research the opportunity and produce a compliant evidence-backed submission package | `PLAN_ONLY` |
| `C-59` Professional application or portfolio | Build a truthful target-specific professional package and verify cross-artifact coherence | `PLAN_ONLY` |
| `C-60` Executive or public communication | Create and review a high-clarity message, letter, announcement, speech, or response | `PLAN_ONLY` |
| `C-61` Social and community content series | Transform approved source material into platform-fit accessible short-form assets and schedule | `PLAN_ONLY` |
| `C-62` Learning launch and workshop | Create the curriculum, materials, deck, interactive artifact, event plan, and participant communications | `PLAN_ONLY` |
| `C-63` Feature delivery | Implement an approved feature across product, engineering, tests, security, documentation, and release evidence. | `DRAFT_ONLY` |
| `C-64` Product experiment | Design a product hypothesis, controlled experiment, instrumentation, analysis, and decision record. | `PLAN_ONLY` |
| `C-65` Multilingual launch | Translate and transcreate an approved product or campaign package with accessibility, brand, claim, and locale verification. | `DRAFT_ONLY` |
| `C-66` Media post-production system | Turn an approved script into a rights-aware editing, motion, audio, caption, export, and distribution blueprint. | `DRAFT_ONLY` |
| `C-67` Content optimization loop | Connect content evidence, audience performance, editorial hypotheses, experiments, calendar changes, and verified derivatives. | `PLAN_ONLY` |
| `C-68` Academic review and rebuttal | Review an academic paper, verify citations and methods, then prepare a constructive review or evidence-backed rebuttal. | `PLAN_ONLY` |
| `C-69` SEO, AEO, and information architecture | Improve discoverability without compromising user value, factual accuracy, accessibility, or editorial quality. | `PLAN_ONLY` |
| `C-70` Vendor selection and onboarding | Run requirements, RFP, diligence, security, cost, proof-of-concept, contract, and implementation readiness. | `PLAN_ONLY` |
| `C-71` Workforce and organization plan | Connect strategy, operating model, capacity, roles, decision rights, workforce scenarios, and adoption. | `PLAN_ONLY` |
| `C-72` Hiring and onboarding system | Create a fair structured hiring, selection, onboarding, competency, learning, and employee communication system. | `DRAFT_ONLY` |
| `C-73` Customer support and success system | Align support, knowledge, escalation, customer success, retention, product feedback, and lifecycle measurement. | `PLAN_ONLY` |
| `C-74` Negotiation preparation | Prepare evidence, interests, alternatives, objective criteria, contract questions, scenarios, and approval boundaries. | `PLAN_ONLY` |
| `C-75` Personal knowledge and work system | Build a minimal maintainable workflow for goals, projects, tasks, notes, learning, decisions, and reviews. | `DRAFT_ONLY` |
| `C-76` OSINT investigation | Plan lawful collection, validate and preserve public sources, resolve entities and timelines, and issue an estimative brief. | `PLAN_ONLY` |
| `C-77` Cyber threat intelligence | Collect authorized defensive threat intelligence, analyze tactics and relevance, and convert it into detections and risk actions. | `PLAN_ONLY` |
| `C-78` Legal issue and contract review | Research a legal issue, review related clauses or policy, map obligations and uncertainty, and prepare counsel questions. | `PLAN_ONLY` |
| `C-79` Finance planning and board reporting | Reconcile actuals, forecast drivers and liquidity, then produce a decision-ready executive and board report. | `PLAN_ONLY` |
| `C-80` Accounting close and controls | Design or review close, reconciliations, evidence, controls, exceptions, and independent assurance. | `PLAN_ONLY` |
| `C-81` Operations excellence | Map processes, improve flow and controls, govern quality, automate stable work, and track benefits. | `PLAN_ONLY` |
| `C-82` Supply-chain resilience | Analyze multi-tier supply, inventory, logistics, disruptions, continuity, and executive decisions. | `PLAN_ONLY` |
| `C-83` Product operating system | Connect discovery, strategy, requirements, roadmap, feature delivery, experiments, release, and lifecycle learning. | `PLAN_ONLY` |
| `C-84` Data governance and RAG quality | Align data ownership, lineage, retrieval, freshness, permissions, grounding, and model application quality. | `PLAN_ONLY` |
| `C-85` Competitive intelligence and strategy | Create competitive scenarios, warning indicators, corporate portfolio choices, and executive decisions. | `PLAN_ONLY` |
| `C-86` Crisis and media response | Establish a verified crisis fact pattern, stakeholder communication system, media briefing, updates, and retrospective. | `DRAFT_ONLY` |
| `C-87` Partnership and ecosystem decision | Evaluate partnership fit, economics, governance, legal terms, risk, negotiation, milestones, and exit. | `PLAN_ONLY` |
| `C-88` Board and executive reporting | Design and produce recurring board, executive, investor, finance, risk, strategy, and action reporting. | `DRAFT_ONLY` |
| `C-89` Meeting-to-execution loop | Convert meetings into prepared decisions, accountable records, commitments, follow-through, and status reporting. | `DRAFT_ONLY` |
| `C-90` Policy and regulatory response | Monitor policy, perform legal and public-affairs analysis, map stakeholders, and prepare authorized response options. | `PLAN_ONLY` |
| `C-91` ESG and impact report | Define materiality, data, controls, impact, rights, claims, narrative, exhibits, and exact reporting QA. | `DRAFT_ONLY` |
| `C-92` Responsible AI review | Assess model use, data, rights, safety, security, evaluation, human oversight, monitoring, and deployment decision. | `PLAN_ONLY` |
| `C-93` Inclusive content transformation | Transform technical or public content into accessible, plain-language, localized, and brand-consistent variants. | `DRAFT_ONLY` |
| `C-94` Prompt creation pipeline | Create, optimize, test, repair, document, and approve a production prompt pack. | `DRAFT_ONLY` |
| `C-95` Professional report pipeline | Design a decision narrative, produce the report and exhibits, run factual and editorial QA, and verify exact exports. | `DRAFT_ONLY` |
| `C-96` Organization change program | Design operating model, stakeholder engagement, adoption, employee communication, learning, and outcome tracking. | `PLAN_ONLY` |
| `C-97` Continuity exercise | Prepare, run, observe, and remediate a business continuity or disaster recovery tabletop exercise. | `PLAN_ONLY` |
| `C-98` Enterprise strategy and innovation | Connect corporate strategy, portfolio allocation, competitive scenarios, innovation experiments, and operating plans. | `PLAN_ONLY` |
| `C-99` Department operating plan | Create a complete department plan with mandate, outcomes, portfolio, capacity, budget, risks, governance, and reporting. | `PLAN_ONLY` |
| `C-100` LLM application lifecycle | Design, evaluate, secure, govern, and prepare deployment of an LLM, RAG, memory, tool, or agent application. | `PLAN_ONLY` |
| `C-101` Revenue operations system | Align marketing, pipeline, forecast, customer success, lifecycle measurement, automation, and management reporting. | `PLAN_ONLY` |
| `C-102` Fraud and abuse defense | Model fraud and abuse, identify signals and controls, test fairness and privacy, and design investigation and response. | `PLAN_ONLY` |
| `C-103` Executive support operating system | Design calendar, travel, briefing, correspondence, records, decision capture, confidentiality, and contingency workflows. | `DRAFT_ONLY` |

## CLI examples

```bash
python tools/md.py explain C-63
python tools/md.py plan C-94 --mode DRAFT_ONLY --root . --out .prompt_suite/runs/prompt-pipeline.json
python tools/md.py list --kind packs
python tools/md.py validate-run .prompt_suite/runs/prompt-pipeline.json
```

## Failure and resume semantics

- A failed stage records evidence, partial artifacts, and whether rollback is required.
- Resume only from a legal state with current evidence and valid approvals.
- Partial success never becomes full completion silently.
- Any changed source, requirement, metric, brand token, permission, model, dependency, or approval invalidates affected downstream artifacts.
- A run closes only after verification or explicit residual-risk acceptance by an authorized human.
## Proof-layer execution requirements

A compiled route is not behaviorally trusted merely because its prompt IDs and schemas are valid. Before making a quality claim, resolve the applicable proof surface:

```text
structural validation
→ deterministic routing and state tests
→ prompt/scenario fixtures
→ live model benchmarks when model behavior matters
→ skill conformance when a third-party adapter is used
→ human-reviewed golden evidence for high-impact acceptance
```

`EVALUATION_STATUS.json` is the authoritative statement of completed and pending proof. Machine reference runs may be used to test artifact contracts, but they may not be described as human-reviewed golden runs.

## Phase-specific scenario modes

Each machine-readable scenario declares `phases`. The phase mode controls permission for that stage and is not replaced by the scenario's historical `default_mode` summary.

Typical route:

```text
AUDIT_ONLY discovery
→ PLAN_ONLY plan or frozen handoff
→ DRAFT_ONLY artifact draft
→ APPLY_SAFE reversible local implementation
→ APPLY_APPROVED exact consequential batch
→ VERIFY_ONLY independent verification
```

The compiler must reject a phase mode that is not permitted by its prompt. Publishing, sending, deploying, submitting, filing, merging, financial transfers, employment decisions, and production mutations remain separately authorized actions.

## Conditional branch rules

Every scenario contains explicit branch contracts for at least:

- insufficient or stale evidence;
- consequential action requiring approval;
- verification failure;
- unavailable or unresolved skill;
- invalid model profile;
- rollback or residual handling.

A branch must record the condition, the selected path, the rejected path, and the evidence that justified the decision.

## Model selection directive

Automatic model selection is permitted only when a profile is measured and production eligible. Run:

```bash
python tools/md.py select-model MD-29 --assurance HIGH_ASSURANCE
```

A `no_selection` result is a valid safety result. Do not substitute reputation, model naming, or unmeasured assumptions for fixture evidence.

## Skill-selection directive

Installable skills require a resolved lock, code and permission review, conformance execution in quarantine, and routed verification. The delivered unresolved locks disable automatic use. Native prompt execution is the fallback.

## Evaluation and closure directive

Before release or distribution:

```bash
python tools/check_skill_lock.py
python tools/run_evaluations.py
pytest -q
python tools/build_manifest.py
python tools/validate_suite.py
python tools/build_manifest.py --check
```

Closure claims must state whether evidence is structural, deterministic, live-model, live-skill, or human-reviewed. Unrun proof surfaces remain pending rather than silently passing.

## Conditional auto-prompt routes

| Trigger | Route |
|---|---|
| Route-changing intent ambiguity | `MD-191` |
| Skill request or suspected capability gap | `MD-192` |
| Required skill unavailable | `MD-193` |
| Qualified candidate approved for acquisition | `MD-194` |
| No suitable candidate and reusable gap | `MD-195` |
| Exact installed skill genuinely required | `MD-196` |
| Finite queue or measurable iterative refinement | `MD-197 → MD-198 after every pass` |

The generic loop target may be any prompt, scenario, or skill. The generic skill adapter may invoke any exact installed skill. Both routes are rejected when their participation does not materially improve the result.

## Added composite scenarios

| Scenario | Purpose | Default mode |
|---|---|---|
| `C-104` Conditional intent refinement | Clarify only route-changing ambiguity, freeze intent, and compile the smallest graph. | `PLAN_ONLY` |
| `C-105` Missing skill discovery, installation, or creation | Prove a skill gap, discover and qualify candidates, install an approved exact skill in both global locations, or create one only when discovery is genuinely empty. | `PLAN_ONLY` |
| `C-106` Generic conditional skill execution | Resolve skill fit, execute an exact installed skill through a typed placeholder, quarantine output, and verify it against the target task. | `DRAFT_ONLY` |
| `C-107` Bounded prompt or skill loop | Run any eligible prompt, scenario, or skill over a finite queue or measurable refinement cycle and stop at the earliest valid exit. | `PLAN_ONLY` |
| `C-108` Audit, fix, and verify convergence loop | Repeat an arbitrary audit-fix-verify route only while each pass yields new evidence or measurable progress and safe residual work remains. | `PLAN_ONLY` |
| `C-109` Visual asset batch production | Use the generic skill adapter with `visual-assets` and bounded outer/inner loops to produce a verified list of SVG, HTML, CSS, or vanilla-JS assets. | `DRAFT_ONLY` |
| `C-110` Strudel composition and refinement | Use the generic skill adapter with `strudel` for bounded composition, arrangement, and verification passes. | `DRAFT_ONLY` |

## Mandatory pair review checkpoint

A paired planning phase never flows directly into execution. After `handoff_frozen`, the runtime enters `plan_review_pending`. Requested changes enter `plan_revision_pending`; the revised handoff must be re-verified, re-frozen, and reviewed again. Approved plans enter `execution_consent_pending`. Only explicit consent may authorize the exact reciprocal executor declared in `paired_prompt_id`.

## Governed prompt addition

Use `MD-199` when an agent must investigate overlap, refine a candidate prompt, or propose routing metadata. Use `tools/add_prompt.py` (or `md.py add-prompt`) as the sole deterministic mutation engine. A dry run and user review precede promotion. The tool allocates only the next permanent ID, creates one unpaired prompt, updates canonical/generated surfaces in staging, runs validation, and promotes only a verified diff. Pair creation remains a separate exact-twin authoring workflow.
