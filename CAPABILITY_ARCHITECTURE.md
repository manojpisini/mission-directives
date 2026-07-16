# Capability Architecture

The suite uses control prompts, standalone investigations, standalone production or operations, independent gates, and genuine investigate→execute or brief→produce pairs. Pairing is a semantic decision, never a symmetry target.

## Pair test

A pair is justified only when the first prompt remains non-mutating, produces a stable reviewable handoff, the second owns a distinct production or mutation responsibility, and both share objective acceptance criteria. Compare the pair against a single full-cycle prompt periodically; remove the pair when it no longer improves safety, reviewability, parallelism, or output quality.

## Shape counts

- Control: **5**
- Investigative: **93**
- Executive: **32**
- Operational: **66**
- Gates: **3**
- Genuine pairs: **32**

## Genuine pairs

| Investigation or brief | Execution or production |
|---|---|
| `MD-25` Project Consistency, Uniformity, and Coherence — Investigation and Plan | `MD-26` Project Consistency, Uniformity, and Coherence — Authorized Execution and Verification |
| `MD-27` Code Quality and Maintainability — Investigation and Plan | `MD-28` Code Quality and Maintainability — Authorized Execution and Verification |
| `MD-29` Debugging, Root Cause, and Bug Resolution — Investigation and Plan | `MD-30` Debugging, Root Cause, and Bug Resolution — Authorized Execution and Verification |
| `MD-31` Safe Cleanup, Dead Code, and Repository Hygiene — Investigation and Plan | `MD-32` Safe Cleanup, Dead Code, and Repository Hygiene — Authorized Execution and Verification |
| `MD-33` Refactoring and Modernization — Investigation and Plan | `MD-34` Refactoring and Modernization — Authorized Execution and Verification |
| `MD-35` Testing and Verification — Investigation and Plan | `MD-36` Testing and Verification — Authorized Execution and Verification |
| `MD-37` Security Posture, Vulnerability, and Fixes — Investigation and Plan | `MD-38` Security Posture, Vulnerability, and Fixes — Authorized Execution and Verification |
| `MD-39` Dependency and Software Supply Chain Security — Investigation and Plan | `MD-40` Dependency and Software Supply Chain Security — Authorized Execution and Verification |
| `MD-41` Configuration, Environment, and Secrets Security — Investigation and Plan | `MD-42` Configuration, Environment, and Secrets Security — Authorized Execution and Verification |
| `MD-43` Identity, Authentication, Authorization, and Session Security — Investigation and Plan | `MD-44` Identity, Authentication, Authorization, and Session Security — Authorized Execution and Verification |
| `MD-45` API, CLI, and Public Contract Integrity — Investigation and Plan | `MD-46` API, CLI, and Public Contract Integrity — Authorized Execution and Verification |
| `MD-47` Data Storage, Schema, and Migration — Investigation and Plan | `MD-48` Data Storage, Schema, and Migration — Authorized Execution and Verification |
| `MD-49` Performance and Efficiency — Investigation and Plan | `MD-50` Performance and Efficiency — Authorized Execution and Verification |
| `MD-51` Reliability, Resilience, and Recovery — Investigation and Plan | `MD-52` Reliability, Resilience, and Recovery — Authorized Execution and Verification |
| `MD-53` CI, Build, Delivery, and Release Pipeline — Investigation and Plan | `MD-54` CI, Build, Delivery, and Release Pipeline — Authorized Execution and Verification |
| `MD-55` Observability, Detection, and Operations — Investigation and Plan | `MD-56` Observability, Detection, and Operations — Authorized Execution and Verification |
| `MD-57` Cloud, Container, and Infrastructure Security — Investigation and Plan | `MD-58` Cloud, Container, and Infrastructure Security — Authorized Execution and Verification |
| `MD-59` Privacy and Data Protection — Investigation and Plan | `MD-60` Privacy and Data Protection — Authorized Execution and Verification |
| `MD-61` Agent, Skill, Tool, and MCP Capability Lifecycle — Investigation and Plan | `MD-62` Agent, Skill, Tool, and MCP Capability Lifecycle — Authorized Execution and Verification |
| `MD-63` Agentic Security, Permissions, and Trust Boundaries — Investigation and Plan | `MD-64` Agentic Security, Permissions, and Trust Boundaries — Authorized Execution and Verification |
| `MD-65` Multi-Agent Architecture and Agent Definitions — Investigation and Plan | `MD-66` Multi-Agent Architecture and Agent Definitions — Authorized Execution and Verification |
| `MD-67` Model and AI System Security — Investigation and Plan | `MD-68` Model and AI System Security — Authorized Execution and Verification |
| `MD-69` Prompt Injection, Untrusted Input, and Tool-Output Security — Investigation and Plan | `MD-70` Prompt Injection, Untrusted Input, and Tool-Output Security — Authorized Execution and Verification |
| `MD-71` User Experience, Accessibility, and Localization — Investigation and Plan | `MD-72` User Experience, Accessibility, and Localization — Authorized Execution and Verification |
| `MD-73` Brand, Design System, and Content Coherence — Investigation and Plan | `MD-74` Brand, Design System, and Content Coherence — Authorized Execution and Verification |
| `MD-75` Documentation, Knowledge, Taxonomy, and Troubleshooting — Investigation and Plan | `MD-76` Documentation, Knowledge, Taxonomy, and Troubleshooting — Authorized Execution and Verification |
| `MD-77` Prompt Suite Consistency, Security, and Coherence — Investigation and Plan | `MD-78` Prompt Suite Consistency, Security, and Coherence — Authorized Execution and Verification |
| `MD-83` Research-Backed Blog, Article, and Newsletter — Investigation and Editorial Brief | `MD-84` Research-Backed Blog, Article, and Newsletter — Drafting, Editing, and Publication Package |
| `MD-85` Script, Video, Podcast, and Storyboard — Research and Production Brief | `MD-86` Script, Video, Podcast, and Storyboard — Writing and Production Package |
| `MD-87` Academic Paper and Scholarly Manuscript — Research Design and Evidence Plan | `MD-88` Academic Paper and Scholarly Manuscript — Drafting, Citation, and Revision Package |
| `MD-101` Presentation Narrative, Story Architecture, and Deck Blueprint | `MD-102` HTML, CSS, and JavaScript Slides and Presentation Production |
| `MD-117` Learning Experience, Curriculum, Course, Lesson, and Assessment — Research and Design Brief | `MD-118` Learning Experience, Curriculum, Course, Lesson, and Assessment — Material Production and Validation |

## Standalone design rules

- Use a standalone investigation when its decision or brief may feed many different downstream actions.
- Use a standalone operational prompt when it owns a bounded end-to-end artifact or workflow with its own verification.
- Use a gate when independence from the producer is material.
- Do not split research, review, simulation, incident response, communication, reporting, or planning merely to create visual symmetry.

## New organizational capabilities

The organizational expansion remains standalone by default. Feature delivery, experiments, localization, media post-production, academic review, department operations, OSINT, legal, finance, people, procurement, product, reporting, prompt engineering, and LLM governance compose with existing prompts through scenarios rather than artificial twins.
## Permanent capability identity

Each prompt has a permanent `capability_id`, stable `prompt_slug`, current `prompt_id`, and presentation `sequence`. Integrations route by `capability_id`; sequence is never an integration key. Current prompt IDs are not reassigned after this release. Historical numeric IDs are namespaced and resolved through `compatibility/`.

## Proof obligations by shape

- **Control:** requires deterministic contract and policy tests.
- **Investigation:** requires healthy, problematic, and adversarial evidence fixtures.
- **Executive:** additionally requires contaminated-handoff refusal tests, dry-run checks, and rollback behavior.
- **Operational:** requires artifact-shape, authorization, and verification fixtures.
- **Gate:** requires independence, false-pass, and false-block evaluation.
- **Genuine pair:** requires pair-vs-single evidence and periodic rejustification.

A structurally valid prompt remains behaviorally unproven until representative model executions are measured.

## Reusable gates instead of prompt inflation

The gate registry provides independent evidence, publication, human-decision, production-change, and multi-artifact-coherence checks. These are policy-level reusable reviewers and do not increase the prompt count merely to create symmetric files.


## Prompt-body role contract

Role selection changes the body contract, not only metadata:

- Every role declares a canonical authorization boundary, tool policy, runtime markers, output contract, and task-specific completion criteria.
- Investigators remain read-only and create evidence, findings, proposed actions, and acceptance criteria.
- Executives contain domain-specific decision rules and reference the frozen acceptance criteria instead of copying verification lists.
- Operational prompts own bounded full-cycle artifacts and use mode-aware tool policies.
- Gates remain independent and do not repair the subject they judge.

The generated `BODY_QUALITY_AUDIT.json` and focused regression tests enforce these invariants.


## Conditional auto-orchestration

`MD-191` through `MD-198` are standalone conditional capabilities. They are not a forced pair family and do not run as a universal preamble. Each has an explicit trigger and non-trigger. Generic skill execution and generic looping are separated from acquisition and exit adjudication so availability cannot silently become authority.

## Conditional auto-orchestration shape

`MD-191` through `MD-198` form a conditional control layer, not a new twin family. Intent clarification, skill-fit analysis, discovery, acquisition, creation, execution, looping, and exit adjudication remain distinct because each has different authority and evidence. Any prompt, scenario, or exact installed skill may be the target of `MD-197`; eligibility depends on measurable value, not domain. Any exact installed skill may be bound through `MD-196`; availability alone never establishes genuine need.

## Paired review and exact-twin control

True investigative/executive pairs include an explicit human review layer between `handoff_frozen` and execution preparation. The planner presents the plan, incorporates requested revisions, re-verifies and re-freezes the handoff, and obtains review again. Explicit execution consent then authorizes only the reciprocal `paired_prompt_id`; the runtime rejects substitute executors.

## Prompt-ingestion mutation boundary

`MD-199` owns agentic prompt-addition analysis. `tools/add_prompt.py` owns canonical mutation. The boundary separates semantic judgment from deterministic identity allocation and registry updates: the agent may refine and propose, but only the transaction tool may write the prompt ecosystem. Unknown routes fail closed, skill references never imply installation, and paired capabilities cannot be synthesized by the generic importer.
