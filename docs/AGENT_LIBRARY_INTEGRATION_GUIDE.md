# Agent Library Integration Guide

## Purpose

This guide explains how MD capabilities connect to a separate agent library without duplicating the same ontology, prompt bodies, or governance rules in two places.

MD defines **what work is performed** and how it is evidenced, authorized, executed, verified, and closed. The agent library defines **which persistent agent role performs it**, with model, tool, memory, limits, routing, guardrails, and observability configuration.

## Separation of responsibilities

### MD owns

- capability identity;
- evidence lane;
- task method;
- output and completion contract;
- runtime markers;
- authorization boundary;
- tool-policy requirements;
- scenarios and gates;
- verification and residual semantics.

### Agent library owns

- agent name and organizational role;
- model primary and fallback;
- tool permission tiers;
- memory policy and exclusions;
- runtime ceilings;
- routing triggers;
- prompt-file paths;
- agent-specific handoffs;
- observability and alerts;
- personality or communication style where useful.

Neither system should copy the other's complete definition.

## Relationship model

```text
request
→ MD prompt or scenario
→ required capability IDs
→ candidate agent archetypes
→ agent configuration and permissions
→ canonical prompt and artifact contracts
→ execution and verification
```

The relationship is many-to-many:

- one agent may implement several capabilities;
- one capability may be implemented by several agent types depending on environment, assurance, and specialization;
- some capabilities may be fulfilled without a persistent agent.

## Generated crosswalks

The package includes:

```text
integrations/
  agent_catalog_snapshot.json
  prompt_type_catalog_snapshot.json
  md_to_agent_library_crosswalk.json
  md_to_prompt_type_library_crosswalk.json
```

Mappings contain candidate links, rationale, confidence, duplication risk, and review status.

Machine-proposed similarity is not approval.

## Mapping review

Review each candidate against:

- mission fit;
- required evidence;
- authority and tool permissions;
- evidence lane;
- artifact outputs;
- assurance minimum;
- memory needs and exclusions;
- prohibited actions;
- handoff responsibilities;
- organizational ownership.

Reject a link based only on similar words. A generic “security agent” may not be appropriate for exploit reproduction, security remediation, threat intelligence, and policy governance.

## Agent-folder generation

An approved mapping can populate an agent folder with references:

```yaml
capabilities:
  - capability_id: md.debugging.debugging-root-cause-and-bug-resolution-investigation-and-plan
    prompt_id: MD-29
    role: investigative
```

The agent folder should reference canonical prompt files rather than copy them. Agent-specific system instructions may summarize role behavior but must not redefine output, authorization, or verification contracts inconsistently.

## Prompt-kit relationship

The agent's prompt kit may include:

- `system.md`;
- report templates;
- clarification;
- refusal;
- escalation;
- tool usage;
- examples;
- self-review;
- handoff context;
- glossary.

MD provides task capabilities and can supply the deliverable contract. The agent kit supplies persistent operating behavior and presentation for the specific agent.

## Routing integration

A router can use:

1. MD scenario compilation;
2. required capability IDs;
3. assurance and action risk;
4. approved crosswalks;
5. agent availability and permissions;
6. model and tool eligibility.

The selected agent must satisfy the capability's authorization and tool policy. Agent permissions cannot broaden prompt authority.

## Synchronization procedure

When either catalog changes:

1. materialize the current catalogs;
2. run the crosswalk builder;
3. compare proposals to approved mappings;
4. review new, removed, and changed links;
5. update stable external IDs;
6. run drift checks;
7. update manuals and fixtures;
8. promote mappings only after review.

```bash
python tools/build_crosswalk.py \
  --agent-catalog /path/to/universal_agent_type_catalog.md \
  --prompt-type-catalog /path/to/universal_prompt_type_catalog.md
```

## Drift detection

Flag:

- agent configurations pointing to missing capability IDs;
- active capabilities with missing required agent families;
- copied prompt bodies drifting from canonical files;
- agents with permissions below or above capability requirements;
- output templates incompatible with schemas;
- duplicated archetypes claiming the same exclusive responsibility;
- retired prompts used by live agent routing.

## Ownership boundary example

A financial analyst agent may implement forecasting, variance analysis, and report production capabilities. The financial action policy, approval gate, and output verification remain canonical MD/runtime concerns. The agent library defines the analyst's model fallback, spreadsheet tool access, memory retention, and escalation route.

## Validation

Crosswalk completeness is structurally validated. Mapping correctness still requires human review because lexical similarity cannot prove operational equivalence.
