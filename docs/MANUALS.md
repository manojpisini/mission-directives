# Manuals and Guides

This index is the human navigation layer for the Mission Directives. The suite is machine-readable, but operators and maintainers should not have to reverse-engineer JSON files or prompt bodies to understand how it works.

## Start here

| Reader | First manual | Then read |
|---|---|---|
| New user | [User Manual](USER_MANUAL.md) | [Operator Guide](OPERATOR_GUIDE.md) |
| Prompt author | [Prompt Body Authoring Guide](PROMPT_BODY_AUTHORING_GUIDE.md) | [Completion Criteria Guide](COMPLETION_CRITERIA_GUIDE.md), [Runtime Marker Protocol](RUNTIME_MARKER_PROTOCOL.md) |
| Pair author | [Pair Authoring and Verification Guide](PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md) | [Plan Review and Exact-Twin Execution Guide](PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md), [Executive Decision Rules Guide](EXECUTIVE_DECISION_RULES_GUIDE.md) |
| Runtime maintainer | [Architecture Guide](ARCHITECTURE_GUIDE.md) | [CI and Testing Guide](CI_AND_TESTING_GUIDE.md), [Prompt Body Validation Guide](PROMPT_BODY_VALIDATION_GUIDE.md) |
| Security reviewer | [Security Operations Guide](SECURITY_OPERATIONS_GUIDE.md) | [Tool Policy and Authorization Guide](TOOL_POLICY_AND_AUTHORIZATION_GUIDE.md), [Skill Supply-Chain Guide](SKILL_SUPPLY_CHAIN_GUIDE.md) |
| Evaluation engineer | [Evaluation Manual](EVALUATION_MANUAL.md) | [Model Routing Guide](MODEL_ROUTING_GUIDE.md) |
| Repository agent maintainer | [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md) | [Operator Guide](OPERATOR_GUIDE.md), [Auto-Prompts and Conditional Routing Guide](AUTO_PROMPTS_AND_CONDITIONAL_ROUTING_GUIDE.md) |
| Agent-library maintainer | [Agent Library Integration Guide](AGENT_LIBRARY_INTEGRATION_GUIDE.md) | [Compatibility and Identity Guide](COMPATIBILITY_AND_IDENTITY_GUIDE.md) |
| Contributor | [Contributor Guide](CONTRIBUTOR_GUIDE.md) | [Manual Quality Standard](MANUAL_QUALITY_STANDARD.md) |

## Complete manual set

### Operation

- [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md) — safely creating and updating root agent files, using `MD` keyword lookup, productivity shortcuts, and preserving unmanaged instructions.
- [User Manual](USER_MANUAL.md) — choosing prompts and scenarios, execution modes, evidence lanes, artifacts, examples, and closure.
- [Operator Guide](OPERATOR_GUIDE.md) — running `md.py`, reading route explanations, handling approvals, markers, failures, and residuals.
- [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) — routing errors, stale evidence, invalid handoffs, skill failures, marker defects, and validation failures.
- [Recovery and Rollback Guide](RECOVERY_AND_ROLLBACK_GUIDE.md) — failed execution, rollback, residual-open states, and honest closure.

### Prompt authoring

- [Prompt Body Authoring Guide](PROMPT_BODY_AUTHORING_GUIDE.md) — canonical tag anatomy, ordering, examples, anti-patterns, and review workflow.
- [Prompt Addition and Registration Guide](PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md) — secure script and agentic workflows for assigning identities, normalizing prompts, updating routes and registries, generating fixtures, validating, and transactionally promoting additions.
- [Completion Criteria Guide](COMPLETION_CRITERIA_GUIDE.md) — writing task-specific, observable, marker-aware completion conditions.
- [Tool Policy and Authorization Guide](TOOL_POLICY_AND_AUTHORIZATION_GUIDE.md) — separating authority from tool selection and enforcing least privilege.
- [Runtime Marker Protocol](RUNTIME_MARKER_PROTOCOL.md) — evidence, unknown, finding, action, verification, and stop record semantics.
- [Pair Authoring and Verification Guide](PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md) — true-pair test, handoff freezing, verification ownership, and de-duplication.
- [Plan Review and Exact-Twin Execution Guide](PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE.md) — mandatory user review, revision, re-freezing, explicit consent, and exact reciprocal executor enforcement.
- [Executive Decision Rules Guide](EXECUTIVE_DECISION_RULES_GUIDE.md) — action eligibility, domain prioritization, conflict resolution, budget behavior, and stop rules.
- [Scenario Authoring Guide](SCENARIO_AUTHORING_GUIDE.md) — phase-specific modes, branches, locks, required inputs, and completion gates.

### Architecture and validation

- [Architecture Guide](ARCHITECTURE_GUIDE.md) — control plane, roles, artifacts, graph, policies, state machine, skills, models, and proof layers.
- [Prompt Body Validation Guide](PROMPT_BODY_VALIDATION_GUIDE.md) — static body checks, semantic lint, report interpretation, and regression testing.
- [CI and Testing Guide](CI_AND_TESTING_GUIDE.md) — local checks, pre-commit, CI order, deterministic proof, and manifest integrity.
- [Evaluation Manual](EVALUATION_MANUAL.md) — healthy, problematic, adversarial, pair, skill, model, rollback, and golden-run evaluations.
- [Telemetry and Observability Guide](TELEMETRY_AND_OBSERVABILITY_GUIDE.md) — run metrics, privacy, dashboards, drift, and outcome-linked learning.

### Security, models, and skills

- [Security Operations Guide](SECURITY_OPERATIONS_GUIDE.md) — defensive boundaries, approvals, isolation, exploit reproduction, incident work, and verification.
- [Skill Supply-Chain Guide](SKILL_SUPPLY_CHAIN_GUIDE.md) — lockfiles, trust tiers, quarantine, conformance, upgrades, and fail-closed behavior.
- [Model Routing Guide](MODEL_ROUTING_GUIDE.md) — measured profiles, no-selection behavior, benchmark ingestion, cost, latency, and assurance.

### Governance and integration

- [Compatibility and Identity Guide](COMPATIBILITY_AND_IDENTITY_GUIDE.md) — permanent capability IDs, aliases, redirects, original-area coverage, and deprecation.
- [Agent Library Integration Guide](AGENT_LIBRARY_INTEGRATION_GUIDE.md) — MD-to-agent and MD-to-prompt-type crosswalks, ownership boundaries, and regeneration.
- [Contributor Guide](CONTRIBUTOR_GUIDE.md) — safe changes, tests-first workflow, catalog updates, documentation requirements, and review evidence.
- [Manual Quality Standard](MANUAL_QUALITY_STANDARD.md) — truth, depth, examples, reproducibility, and maintenance requirements for documentation.

## Normative versus explanatory documents

The following are normative:

- `PROMPT_SUITE_CONVENTIONS.md`
- `PROMPT_STRUCTURE_STANDARD.md`
- prompt frontmatter and body contracts
- schemas and policies
- `run_state_machine.json`
- `skill_registry.json` and `skills.lock.json`
- validators and tests

Manuals explain those sources and provide examples. When explanatory prose conflicts with a machine-enforced contract, the normative artifact wins and the documentation must be corrected.

## Documentation truth rule

A manual must state whether a claim is:

- designed;
- statically validated;
- deterministically tested;
- measured against live models;
- verified against a live skill;
- reviewed by a human.

Do not collapse those proof levels into the word “validated.”

### Auto-orchestration and specialist integrations

- [Auto-Prompts and Conditional Routing Guide](AUTO_PROMPTS_AND_CONDITIONAL_ROUTING_GUIDE.md)
- [Generic Skill Execution Guide](GENERIC_SKILL_EXECUTION_GUIDE.md)
- [Bounded Loop Orchestration Guide](BOUNDED_LOOP_ORCHESTRATION_GUIDE.md)
- [Visual Assets Integration Guide](VISUAL_ASSETS_INTEGRATION_GUIDE.md)
- [Installed Skills Inventory Guide](INSTALLED_SKILLS_INVENTORY_GUIDE.md)

- [Auto-Orchestration Runtime Guide](AUTO_ORCHESTRATION_RUNTIME_GUIDE.md)
- [Local Skill Registration Guide](LOCAL_SKILL_REGISTRATION_GUIDE.md)

## Complete mastery and platform guides

- [MD Mastery Manual](MD_MASTERY_MANUAL.md) — comprehensive end-to-end reference for every suite subsystem.
- [Template System Guide](TEMPLATE_SYSTEM_GUIDE.md) — template registry, routing, conformance, and extension.
- [Logging and Telemetry Guide](LOGGING_AND_TELEMETRY_GUIDE.md) — daily append-only TOML events and metrics.
- [Cross-Platform Tooling Guide](CROSS_PLATFORM_TOOLING_GUIDE.md) — Python core, Bash/PowerShell parity, and dispatch.
- [TUI and Operator Experience Guide](TUI_AND_OPERATOR_EXPERIENCE_GUIDE.md) — progress, status, accessibility, and CI fallback.

- [Installation and Project Integration Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md)
- [Project Cleanup and Uninstall Guide](PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md) — transactional removal, approval-bound preview, preservation rules, rollback, TUI, and receipts.
