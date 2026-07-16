# Auto-Prompts and Conditional Routing Guide

## Purpose

The auto-prompt layer resolves a small set of recurring orchestration problems that should not be reimplemented inside every domain prompt:

- clarify intent only when ambiguity can change the route or result;
- decide whether a specialist skill is genuinely necessary;
- discover, qualify, install, or create a missing skill under explicit policy;
- execute any exact installed skill through a typed contract;
- repeat any prompt, scenario, or skill only when repetition has measurable value;
- stop loops at the earliest defensible completion or failure condition.

These prompts are **conditional capabilities**, not a hidden preamble and not a background daemon. A runtime, orchestrator, or operator supplies trigger evidence to `tools/md.py auto-plan` or applies the equivalent rules from `auto_prompt_policy.json`. A prompt is injected only when its participation changes routing, safety, quality, authority, or verification.

## The eight auto-prompts

| Prompt | Responsibility | Must not do |
|---|---|---|
| `MD-191` | Interrogate route-changing ambiguity and freeze an intent brief. | Ask questions whose answers cannot change the graph or acceptance decision. |
| `MD-192` | Compare native execution, installed skills, and possible specialist capabilities. | Choose a skill because it is fashionable, available, or keyword-adjacent. |
| `MD-193` | Use `find-skills` or equivalent discovery to qualify exact candidates. | Install the first search result or treat search ranking as trust evidence. |
| `MD-194` | Install one approved exact skill into both global skill locations. | Install without authority, provenance, rollback, or post-install verification. |
| `MD-195` | Create a narrow reusable skill when discovery is genuinely empty. | Create a skill for a one-off task or broaden permissions beyond the proven gap. |
| `MD-196` | Bind and execute any exact installed skill through typed placeholders. | Silently substitute another skill or trust the skill's self-reported success. |
| `MD-197` | Coordinate a finite work queue or measurable refinement cycle. | Loop a one-shot task, unchanged failure, or repeated external effect. |
| `MD-198` | Independently decide continue, complete, plateau, rollback, escalate, or stop. | Edit the target artifact or lower the acceptance threshold mid-loop. |

## Trigger order

The default order is:

```text
clear intent?
├─ no  → MD-191
└─ yes → continue

specialist capability materially needed?
├─ no  → native target route
└─ yes → MD-192
          ├─ exact skill installed → MD-196
          ├─ skill missing → MD-193
          │                  ├─ qualified candidate → MD-194 → MD-196
          │                  └─ no suitable candidate → MD-195 → conformance → MD-196
          └─ skill redundant/prohibited → native route or stop

repetition materially useful?
├─ no  → execute once
└─ yes → MD-197 → target pass → MD-198 → earliest valid exit
```

Installation and creation are alternatives, not two actions to perform in sequence. Creation is a last-resort branch after discovery proves that no suitable candidate exists.

## Intent interrogation

`MD-191` asks only questions that can alter one or more of:

- observable outcome;
- audience or decision owner;
- scope and exclusions;
- authority or protected surfaces;
- evidence lane;
- artifact medium;
- skill requirement;
- loop eligibility;
- budget;
- completion criteria.

It must use prior conversation and project evidence first. Normally it asks one high-impact question at a time. Multiple-choice wording is useful when choices are genuine and non-leading. When urgency prevents clarification, the prompt selects the safest reversible default and records it as an assumption rather than pretending the intent is known.

### Good question

> Will this report remain an internal draft, or will it be published externally? Publication changes the legal, privacy, accessibility, and claims-verification route.

### Wasteful question

> What tone do you prefer?

That question is wasteful when the supplied brand guide already defines tone and the answer would not change routing or acceptance.

## Skill-fit classification

`MD-192` returns exactly one classification:

- **required** — native execution cannot satisfy a material acceptance criterion;
- **beneficial** — native execution is possible, but the skill offers measurable quality, efficiency, portability, or verification gain;
- **optional** — the skill may be used, but omitting it does not weaken the result;
- **redundant** — the skill duplicates the chosen primary producer or adds ceremony;
- **prohibited** — its permissions, side effects, provenance, or output contract exceed the task.

A skill already present on disk may still be unreviewed. `installed_skills_inventory.json` proves availability only. Curated registry status, source provenance, runtime probing, permissions, and conformance determine whether it may execute automatically.

## Missing-skill acquisition

A missing capability follows this sequence:

1. freeze a machine-readable skill requirement;
2. search for exact candidates with `find-skills` or equivalent discovery;
3. inspect the candidate's `SKILL.md`, source, revision, requested permissions, tool use, files, network access, outputs, and failure behavior;
4. compare the candidate against native execution and other candidates;
5. request or verify installation authority;
6. install one exact skill into both global locations;
7. quarantine the result;
8. run conformance fixtures;
9. enable automatic selection only after promotion.

Canonical dual-location installation:

```powershell
npx skills add <source> --skill <skill-id> -g -a cline -a opencode --copy -y
```

The expected destinations are:

```text
~/.agents/skills/<skill-id>/SKILL.md
~/.config/opencode/skills/<skill-id>/SKILL.md
```

Use `tools/install_skill_dual.ps1` for Windows execution and destination verification. Unpinned acquisition requires explicit authorization and remains subject to the suite's skill-lock policy.

## Skill creation

`MD-195` may invoke `skill-creator`, `writing-skills`, or an equivalent approved capability only when:

- discovery found no suitable candidate;
- native prompts cannot satisfy the recurring requirement cleanly;
- the need is reusable rather than one-off;
- a maintenance owner exists;
- permissions can be narrowly bounded;
- healthy, problematic, and adversarial fixtures can be defined;
- the skill has an explicit native fallback.

Terms such as **advanced**, **cutting-edge**, and **production-grade** are requirement profiles, not magical flags:

| Label | Concrete meaning |
|---|---|
| Advanced | robust error handling, typed contracts, efficient context use, tests, portability, and useful diagnostics |
| Cutting-edge | current evidence-backed techniques, comparative evaluation, explicit experimental status where evidence is incomplete, and safe fallback |
| Production-grade | least privilege, observability, deterministic validation where possible, recovery, maintenance documentation, and conformance evidence |

The created skill stays in staging until verification passes. Novelty claims must be supported, not inferred from wording.

## Automatic routing examples

### Installed personal skill and batch loop

```bash
python tools/md.py auto-plan MD-104 \
  --skill-id visual-assets \
  --skill-required \
  --loop \
  --work-items 12 \
  --measurable
```

Expected auto-prompts:

```text
MD-192 → MD-196 → MD-197 → MD-198
```

### Installed but unmapped skill

```bash
python tools/md.py auto-plan MD-27 \
  --skill-id code-review \
  --skill-required
```

The skill is not treated as missing. It routes through `MD-192` and conditionally through `MD-196` after runtime schema, permission, provenance, side-effect, and task-fit review.

### Missing specialist capability

```bash
python tools/md.py auto-plan MD-165 \
  --skill-id missing-specialist \
  --skill-required \
  --allow-install \
  --allow-create
```

The resulting graph contains alternative acquisition branches. `MD-194` runs only if discovery qualifies a candidate. `MD-195` runs only if discovery is genuinely empty and reusable demand justifies creation.

### Wasteful loop request

```bash
python tools/md.py auto-plan MD-165 --loop
```

Without a finite queue or measurable refinement objective, the router rejects `MD-197` and executes once or asks for a meaningful rubric.

## Evidence and records

Auto-prompt decisions use the normal marker protocol:

- `@EVIDENCE:{id}` — installed inventory, skill schema, source, benchmark, or observed result;
- `?UNKNOWN:{id}` — unresolved permission, provenance, input, or acceptance condition;
- `#FINDING:{id}` — skill gap, route ambiguity, loop eligibility, or conformance finding;
- `+ACTION:{id}` — question, discovery, installation, execution, or iteration;
- `=VERIFY:{id}` — route-ready intent, dual-location installation, artifact acceptance, or loop exit proof;
- `!STOP:{reason}` — authority, safety, budget, plateau, missing evidence, or invalid loop.

## Failure behavior

The correct result may be:

- no clarification needed;
- no skill needed;
- installed skill rejected after probing;
- native fallback selected;
- acquisition blocked pending approval;
- creation rejected as one-off or redundant;
- loop rejected as wasteful;
- loop stopped with residual items;
- human escalation.

These are valid outcomes. The auto layer exists to prevent unnecessary work as much as to enable useful automation.
