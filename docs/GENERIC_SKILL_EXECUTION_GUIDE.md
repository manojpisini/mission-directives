# Generic Skill Execution Guide

## Purpose

`MD-196` is a universal typed adapter for **any exact installed skill**. It is not limited to design skills, personal skills, or skills already curated in `skill_registry.json`. The adapter exists so a domain prompt can gain a specialist capability without copying that skill's instructions, permissions, or output assumptions into every prompt body.

Availability does not equal genuine need. `MD-192` must first establish that the skill is required or materially beneficial.

## Placeholder contract

A skill execution request binds:

```yaml
skill_id: <canonical exact ID>
skill_requirement_spec: <why native execution is insufficient or materially weaker>
inputs:
  trusted: []
  untrusted: []
expected_artifacts:
  - path:
    format:
    schema:
authority:
  allowed_actions: []
  prohibited_actions: []
budget:
  tokens:
  time:
  cost:
  tool_calls:
acceptance_criteria: []
fallback:
  native_prompt_route:
  stop_condition:
```

The adapter does not pass an unbounded conversation dump. It binds only the inputs and files needed for the exact operation.

## Eligibility

A skill is eligible when all applicable conditions pass:

1. its capability matches a material acceptance criterion;
2. its schema and invocation are understood;
3. required permissions fit the run authority;
4. external effects are absent or separately approved;
5. provenance and trust state are acceptable for the assurance profile;
6. output can be quarantined and independently verified;
7. the expected gain exceeds integration cost and risk;
8. a fallback exists.

A skill is ineligible when it is merely relevant, duplicates the primary producer, requests excessive access, produces an incompatible artifact, lacks a safe verification path, or adds no measurable benefit.

## Curated, local, and unmapped skills

### Curated and approved

A curated skill has explicit prompt routes, trust metadata, and conformance expectations in `skill_registry.json`. It may be auto-selected only when all lock and maturity controls pass.

### User-owned local

`visual-assets` and `strudel` are registered as user-owned local skills. Their presence in the supplied OpenCode inventory supports availability; task-specific verification remains required.

### Installed but unmapped

An installed skill such as `code-review` may not yet have a curated MD route. An explicit request can still route through `MD-192` and `MD-196`, but the runtime must first inspect:

- `SKILL.md` triggers and scope;
- required tools and permissions;
- network and filesystem access;
- input and output shape;
- mutation and external effects;
- source provenance;
- failure and stop behavior;
- overlap with the target prompt.

It is classified `installed_unmapped`, remains experimental, and cannot be silently auto-selected from keyword similarity.

## Execution lifecycle

```text
frozen task and acceptance criteria
→ skill-fit decision
→ canonical alias resolution
→ schema and permission probe
→ dry run when mutation is possible
→ exact invocation
→ raw output quarantine
→ schema validation
→ evidence, safety, accessibility, and artifact review
→ release to downstream prompt or fallback
```

### Quarantine

Raw skill output is never immediately trusted as downstream evidence. Quarantine preserves:

- exact invocation;
- input hashes or references;
- source and revision information;
- raw stdout/stderr or artifact locations;
- tool calls and external effects;
- cost and latency;
- failure status;
- produced files.

Only verified artifacts are promoted.

## Failure handling

Do not blindly rerun a failed skill. First classify the failure:

- missing input;
- incompatible schema;
- permission denial;
- tool failure;
- unsafe side effect;
- invalid artifact;
- quality failure;
- stale source;
- task mismatch.

A retry requires a changed hypothesis, corrected input, repaired skill, different approved capability, or altered target plan. Repeated unchanged failure routes to `!STOP:{reason}` or, when genuinely iterative, the bounded loop gate.

## Acquisition

When a required skill is not detected locally, route to `MD-193`. A qualified and approved candidate may be installed with:

```powershell
npx skills add <source> --skill <skill-id> -g -a cline -a opencode --copy -y
```

Expected locations:

```text
~/.agents/skills/<skill-id>
~/.config/opencode/skills/<skill-id>
```

`MD-195` creates a new skill only when discovery finds no suitable candidate and recurring demand justifies maintenance.

## Example: visual asset

```yaml
skill_id: visual-assets
inputs:
  trusted:
    - approved article brief
    - verified data table
    - brand tokens
expected_artifacts:
  - path: assets/retention-cohort.svg
    format: svg
acceptance_criteria:
  - every value matches the source table
  - visual hierarchy supports the stated insight
  - labels remain readable at export size
  - asset is keyboard- and screen-reader-compatible where interactive
  - SVG remains editable and contains no raster screenshot
fallback:
  native_prompt_route: MD-104
```

## Example: Strudel composition

```yaml
skill_id: strudel
inputs:
  trusted:
    - mood, duration, tempo range, and structural brief
expected_artifacts:
  - path: audio/intro-theme.strudel.js
    format: javascript
acceptance_criteria:
  - code parses in the target Strudel environment
  - arrangement fits the declared duration and sections
  - no unlicensed sampled material is assumed
  - result is reproducible from code
fallback:
  native_prompt_route: MD-91
```

## Quality flags

Words such as **advanced**, **cutting-edge**, or **production-grade** are translated into testable requirements. They never override fit analysis or authorize broader access.

- Advanced: robust contracts, error handling, efficiency, tests, portability.
- Cutting-edge: current evidence-backed methods, comparative evaluation, experimental labeling, safe fallback.
- Production-grade: least privilege, observability, recovery, conformance, maintainership, documentation.
