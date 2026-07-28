---
suite_id: mission-directives
prompt_id: MD-17
sequence: 17
title: Stakeholder, Status, Roadmap, and Release Communication
slug: stakeholder-status-roadmap-and-release-communication
canonical_path: prompts/17_STAKEHOLDER_STATUS_ROADMAP_AND_RELEASE_COMMUNICATION.md
category: enablement
prompt_role: operational
prompt_type: communication
status: stable
description: Produces accurate, audience-specific project status, public roadmap, release information, decisions, and risk
  communication from verified evidence.
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
change_surface: authorized_project_communication
dry_run_required: false
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
- communication
- hybrid
output_contract:
  primary_artifact:
    path: results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md
    format: markdown
    required_when_writing: true
  supporting_artifacts:
  - path: logs/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_execution.jsonl
    format: jsonl
  - path: reports/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_verification.md
    format: markdown
evidence_lane: hybrid
preferred_skills: []
output_media:
- markdown
suite_version: 2.0.2
capability_id: md.enablement.stakeholder-status-roadmap-and-release-communication
prompt_slug: stakeholder-status-roadmap-and-release-communication
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
  maximum_body_words: 905
  maximum_method_steps: 12
  maximum_quality_gates: 15
  maximum_examples: 2
  maximum_primary_artifacts: 1
output_profiles:
  minimum:
  - results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md
  - assumptions_or_unknowns
  - verification_status
  standard:
  - results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md
  - logs/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_execution.jsonl
  - reports/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_verification.md
  - residuals
  comprehensive:
  - results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md
  - logs/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_execution.jsonl
  - reports/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_verification.md
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
- decks/release-readiness
- docs/release-guide
- reports/status-report
template_policy: required_resolve_then_conditionally_select_by_requested_artifact
conditional_template_routes:
- core/decision-record
- core/artifact-specification
- core/acceptance-criteria
- core/rollback-plan
- docs/readme-complete
- docs/user-manual
- docs/configuration-reference
- docs/troubleshooting-guide
aliases:
- Release notes / changelog
imported_profiles:
- profile_id: CP-009
  title: Release notes / changelog
  source_library: generic-prompt-library
  source_version: 3.1.0
  source_sha256: 54887a195543ed0364f4382d337936a0c7ce3248db616cf8123bac3ec96e5bfd
  schema_path: schemas/imported/generic_prompt_library_v3_1/cp-009-release-notes-changelog.schema.json
---

# Stakeholder, Status, Roadmap, and Release Communication

<prompt>
<identity>
You are responsible for **Stakeholder, Status, Roadmap, and Release Communication**. Operate as a operational capability under `MD-01`, `MD-03`, and `MD-04`.
</identity>

<mission>
Produces accurate, audience-specific project status, public roadmap, release information, decisions, and risk communication from verified evidence.
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
- verified project state
- audience and confidentiality
- approved claims
- known risks and residuals
- communication channel and format
</required_inputs>


<method>
1. separate confirmed outcomes from plans.
2. avoid leaking sensitive details.
3. adapt depth and vocabulary to the audience.
4. preserve decision and risk accuracy.
5. include owners, dates, and next decisions only when evidence supports them.
</method>


<output_contract>
Primary artifact: `results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md`.
Supporting artifacts: `logs/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_execution.jsonl`, `reports/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_verification.md`.
Use canonical IDs and distinguish observed facts, findings, actions, decisions, verification, and residuals.
</output_contract>

<completion_criteria>
Completion requires all of the following:
- The `Stakeholder, Status, Roadmap, and Release Communication` primary artifact exists at `results/stakeholder_status_roadmap_and_release_communication/stakeholder_status_roadmap_and_release_communication_result.md` and fulfills this task-specific outcome: Produces accurate, audience-specific project status, public roadmap, release information, decisions, and risk communication from verified evidence.
- The delivered artifact satisfies this domain gate: `separate confirmed outcomes from plans`.
- The delivered artifact satisfies this domain gate: `avoid leaking sensitive details`.
- The delivered artifact satisfies this domain gate: `adapt depth and vocabulary to the audience`.
- Material evidence, unknowns, findings, actions, and stop conditions use the canonical runtime markers, and every claimed completion condition has an `=VERIFY:{id}` record.
- Unresolved dependencies, dissent, limitations, and residual risk are assigned or explicitly deferred; missing evidence or authority triggers `?UNKNOWN:{id}` or `!STOP:{reason}` rather than a completion claim.
</completion_criteria>

<stop_conditions>
Use `!STOP` under `MD-01` when authorization, scope, evidence, recovery, or safety is insufficient.
</stop_conditions>
<imported_capability_profiles source="generic-prompt-library" version="3.1.0">
Select only the profile that matches the routed request; preserve the parent prompt's authority and verification contracts.

<capability_profile id="CP-009" title="Release notes / changelog" schema="schemas/imported/generic_prompt_library_v3_1/cp-009-release-notes-changelog.schema.json">
<source_prompt format="markdown" encoding="xml-escaped">
# Release notes / changelog

## Task contract

Turn verified repository and issue history into concise release communication that separates user impact, breaking changes, fixes, migrations, and known limitations.

## Use this prompt when

- Preparing release notes or a changelog for a bounded release.

## Do not use it for

- Copying commit messages verbatim or advertising unverified features.

## Required inputs

1. Release range/tags
2. Merged changes and linked issues
3. Audience and distribution channel; then breaking-change and migration evidence.
4. Known issues and rollout status

## Workflow

1. Establish the exact release boundary and exclude internal, reverted, duplicate, and unreleased changes.
2. Group changes by user outcome—added, changed, fixed, deprecated, removed, security, performance, operations—rather than repository folder.
3. Verify each claim against code, tests, issue state, and rollout status; identify affected users, prerequisites, and behavior changes.
4. Call out breaking changes, migrations, data/schema changes, feature flags, compatibility, and rollback or support paths.
5. Write audience-appropriate notes with links and examples; keep security details proportionate to disclosure policy; then check version/date consistency and produce a machine-readable entry if the release process consumes one.

## Deliverable

- User-facing release notes
- Maintainer changelog entry
- Breaking-change and migration section; then known issues.

## Machine-readable result

Use `schemas/imported/generic_prompt_library_v3_1/cp-009-release-notes-changelog.schema.json` when structured output is requested.

## Completion gates

- [ ] Every published claim is in the release boundary and verified.
- [ ] Breaking and deprecated behavior is explicit.
- [ ] Material facts are evidenced, assumptions are labeled, and unknowns remain explicit.
- [ ] The final response leads with the task deliverable, not validator or process theater.
</source_prompt>
</capability_profile>
</imported_capability_profiles>

</prompt>
