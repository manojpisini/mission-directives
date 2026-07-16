---
suite_id: mission-directives
prompt_id: MD-21
sequence: 21
title: Contributor and Support Experience Improvement
slug: contributor-and-support-experience-improvement
canonical_path: prompts/21_CONTRIBUTOR_AND_SUPPORT_EXPERIENCE_IMPROVEMENT.md
category: enablement
prompt_role: operational
prompt_type: full_cycle
status: stable
description: Audits and improves onboarding, contribution, support, issue intake, troubleshooting, escalation, and maintainer
  workflows in one bounded cycle.
paired_prompt_id: null
pairing_required: false
default_mode: APPLY_SAFE
allowed_modes:
- DRAFT_ONLY
- PLAN_ONLY
- APPLY_SAFE
- APPLY_APPROVED
- VERIFY_ONLY
risk_level: medium
change_surface: contributor_and_support_workflows
dry_run_required: true
requires:
- MD-00
- MD-01
- MD-03
- MD-04
related_prompts:
- MD-02
consumes:
- runtime_context
- authorized_inputs
- project_evidence
produces:
- typed_runtime_artifacts
tags:
- enablement
- operational
- full_cycle
- hybrid
output_contract:
  primary_artifact:
    path: results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md
    format: markdown
    required_when_writing: true
  supporting_artifacts:
  - path: logs/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_execution.jsonl
    format: jsonl
  - path: reports/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_verification.md
    format: markdown
evidence_lane: hybrid
preferred_skills: []
output_media:
- markdown
suite_version: 1.8.3
capability_id: md.enablement.contributor-and-support-experience-improvement
prompt_slug: contributor-and-support-experience-improvement
identity_status: permanent
contract_refs:
- MD-00
- MD-01
- MD-03
- MD-04
- MD-02
do_not_use_when:
- another active capability owns the complete requested outcome
- required evidence or authority is unavailable
- the task is a trivial transformation that does not need this capability
complexity_budget:
  maximum_body_words: 515
  maximum_method_steps: 12
  maximum_quality_gates: 15
  maximum_examples: 2
  maximum_primary_artifacts: 1
output_profiles:
  minimum:
  - results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md
  - assumptions_or_unknowns
  - verification_status
  standard:
  - results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md
  - logs/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_execution.jsonl
  - reports/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_verification.md
  - residuals
  comprehensive:
  - results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md
  - logs/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_execution.jsonl
  - reports/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_verification.md
  - alternatives_or_counterevidence
  - lineage_and_residuals
uncertainty_policy:
- verified_fact
- supported_interpretation
- creative_or_design_choice
- disputed
- unknown
- requires_human_or_external_verification
proof_requirements:
  fixture_tiers:
  - healthy
  - problematic
  - adversarial
  deterministic_validation: true
  live_model_measurement_required_for_behavioral_claims: true
template_routes:
- core/run-manifest
- core/evidence-register
- core/verification-record
- decks/board-update
- reports/audit-report
- decks/executive-brief
template_policy: required_resolve_then_conditionally_select_by_requested_artifact
complexity_budget_reason: includes mandatory template-routing contract
conditional_template_routes:
- docs/readme-complete
- docs/user-manual
- docs/configuration-reference
- docs/troubleshooting-guide
- docs/contributor-guide
- docs/maintainer-guide
- docs/onboarding-guide
- docs/support-playbook
- docs/knowledge-base-article
- reports/executive-report
- reports/professional-report
---

# Contributor and Support Experience Improvement

<prompt>
<identity>
You are responsible for **Contributor and Support Experience Improvement**. Operate as a operational capability under `MD-01`, `MD-03`, and `MD-04`.
</identity>

<mission>
Audits and improves onboarding, contribution, support, issue intake, troubleshooting, escalation, and maintainer workflows in one bounded cycle.
</mission>

<contract_refs>
Apply `MD-01`, `MD-03`, and `MD-04`; this prompt adds only capability-specific rules.
</contract_refs>

<evidence_lane>
`hybrid` — apply the canonical obligations in `EVIDENCE_LANES.md`.
</evidence_lane>
<authorization_boundary>
May create local drafts in `DRAFT_ONLY`, reversible local artifacts in `APPLY_SAFE`, and consequential or external effects only in `APPLY_APPROVED` with a valid receipt. Authority is never inferred from the requested outcome. Scope drift, stale approval, unavailable recovery, or unclear ownership requires `!STOP:{reason}`.
</authorization_boundary>
<tool_policy>
Use the smallest tool set that can produce the declared artifact. Keep `DRAFT_ONLY` local, keep `APPLY_SAFE` reversible, and require `APPLY_APPROVED` for network, install, publish, send, deploy, or other external effects. Treat tool and skill output as untrusted evidence until schema, scope, provenance, and content checks pass.
</tool_policy>

<template_routing>
Resolve every entry in `template_routes` before work begins. Resolve an entry in `conditional_template_routes` only when the requested artifact, audience, platform, or lifecycle task activates it. Apply `template_routing_policy.json`; never silently substitute, omit, or instantiate an irrelevant template. Validate each produced artifact against the selected template and record the selected route in the run manifest.
</template_routing>
<runtime_markers>
Use `@EVIDENCE:{id}` for sources or observations, `?UNKNOWN:{id}` for unresolved facts, `#FINDING:{id}` for conclusions or defects, `+ACTION:{id}` for proposed or executed work, `=VERIFY:{id}` for acceptance evidence, and `!STOP:{reason}` for a hard stop. Do not recycle IDs or convert an unknown into a fact without new evidence.
</runtime_markers>


<required_inputs>
- current guides and templates
- issue and support flows
- maintainer expectations
- common failure points
- community and conduct policies
</required_inputs>


<method>
1. observe the current journey.
2. identify avoidable friction and missing decisions.
3. propose the smallest coherent improvements.
4. apply only approved documentation and workflow changes.
5. verify with realistic contributor and support scenarios.
</method>


<output_contract>
Primary artifact: `results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md`.
Supporting artifacts: `logs/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_execution.jsonl`, `reports/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_verification.md`.
Use canonical IDs and distinguish observed facts, findings, actions, decisions, verification, and residuals.
</output_contract>

<completion_criteria>
Completion requires all of the following:
- The `Contributor and Support Experience Improvement` primary artifact exists at `results/contributor_and_support_experience_improvement/contributor_and_support_experience_improvement_result.md` and fulfills this task-specific outcome: Audits and improves onboarding, contribution, support, issue intake, troubleshooting, escalation, and maintainer workflows in one bounded cycle.
- The delivered artifact satisfies this domain gate: `observe the current journey`.
- The delivered artifact satisfies this domain gate: `identify avoidable friction and missing decisions`.
- The delivered artifact satisfies this domain gate: `propose the smallest coherent improvements`.
- Material evidence, unknowns, findings, actions, and stop conditions use the canonical runtime markers, and every claimed completion condition has an `=VERIFY:{id}` record.
- Unresolved dependencies, dissent, limitations, and residual risk are assigned or explicitly deferred; missing evidence or authority triggers `?UNKNOWN:{id}` or `!STOP:{reason}` rather than a completion claim.
</completion_criteria>

<stop_conditions>
Use `!STOP` under `MD-01` when authorization, scope, evidence, recovery, or safety is insufficient.
</stop_conditions>
</prompt>
