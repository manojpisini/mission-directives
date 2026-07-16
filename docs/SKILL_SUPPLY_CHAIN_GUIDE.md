# Skill Supply-Chain Guide

## Purpose

Third-party skills can improve specialized work, but they are executable supply-chain dependencies. This guide defines how skills are discovered, locked, reviewed, tested, quarantined, promoted, upgraded, and retired.

## Fail-closed default

A skill is not automatically trusted because:

- it appears on Skills.sh;
- the repository is popular;
- installation succeeds;
- its name matches the task;
- another agent recommended it.

Unresolved locks, excessive permissions, failed conformance, or unknown external effects block automatic use.

## Registry and lock responsibilities

### `skill_registry.json`

Defines:

- skill ID and purpose;
- install command;
- mapped prompts;
- trust tier;
- maturity status;
- required permissions;
- output quarantine;
- fallback;
- conformance contract.

### `skills.lock.json`

Pins:

- repository;
- exact skill name or path;
- commit SHA;
- downloaded archive SHA-256;
- resolution time;
- review and auto-install state.

The delivered third-party locks are unresolved because the build environment did not resolve GitHub commits. Automatic install remains disabled. No fake SHA is inserted.

## Trust tiers

- `native`: package-owned code or alias.
- `verified`: source and behavior reviewed with current evidence.
- `community_reviewed`: meaningful external review, but not locally verified to the highest standard.
- `unreviewed`: no sufficient trust evidence.

Trust describes provenance evidence, not guaranteed quality.

## Maturity states

- recommended;
- approved;
- experimental;
- quarantined;
- deprecated.

A skill can have a resolved lock and remain experimental or quarantined.

## Lock resolution

In a trusted networked environment:

```bash
python tools/resolve_skill_lock.py --skill frontend-design
python tools/check_skill_lock.py
```

Review the exact resulting revision before promotion.

## Source review

Inspect:

- installation scripts;
- dependencies;
- shell and subprocess calls;
- network requests;
- filesystem access;
- secret and credential access;
- telemetry;
- update behavior;
- external actions;
- license;
- generated code or content handling.

## Permission comparison

The skill permissions must be a subset of the effective prompt `<tool_policy>` and runtime authority.

A skill that needs network access cannot be selected for a read-only local prompt unless the route explicitly authorizes that access.

## Output quarantine

All skill output begins quarantined. Promotion requires the applicable checks:

- schema;
- provenance;
- factual integrity;
- code tests;
- security;
- accessibility;
- brand;
- visual quality;
- exact export;
- external-effect confirmation.

The skill cannot approve its own output.

## Conformance testing

```bash
python tools/run_skill_conformance.py \
  --skill-id <SKILL_ID> \
  --artifact <OUTPUT_PATH>
```

A conformance result should record:

- locked revision;
- fixture;
- sandbox permissions;
- raw output;
- expected and actual artifact shape;
- validation results;
- prohibited effects;
- reviewer;
- status.

## Skill selection

Prefer:

1. one primary producer;
2. one independent reviewer when needed;
3. one fallback;
4. optional specialist adapters only when they change quality.

Do not chain several overlapping design or prompt-optimization skills merely because they are available.

## Conflict examples

- two primary frontend design skills should not edit the same source concurrently;
- `polish` may refine an artifact but not silently replace approved information architecture;
- a prompt optimizer may transform a prompt, but an independent prompt reviewer must evaluate the transformed result;
- a report generator may format content but may not rewrite verified numbers without a new finding.

## Upgrade procedure

1. Resolve a new revision.
2. Diff code, permissions, dependencies, and outputs.
3. Keep the prior lock available for rollback.
4. Rerun healthy and adversarial conformance fixtures.
5. Review mapped prompts and policies.
6. Promote explicitly.
7. Update manifests and documentation.

Never silently track a floating branch in high-assurance use.

## Incident response

If a skill is suspected of compromise:

- disable automatic selection;
- quarantine outputs;
- preserve lock and execution evidence;
- identify affected runs;
- rotate exposed credentials if authorized;
- revert to native fallback;
- add detections and a regression fixture;
- review downstream artifacts produced by the skill.

## Retirement

Deprecate when the skill is unmaintained, redundant, unsafe, or no longer improves over native execution. Preserve the lock and affected-run references for audit.

## Proof boundary

A resolved lock proves byte identity. A conformance pass proves behavior on tested fixtures. Neither guarantees safety on every input or environment.
