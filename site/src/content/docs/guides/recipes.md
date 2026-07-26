---
title: Operator Recipes
description: High-signal request patterns for engineering, security, creative, management, data, and communications work.
---

Use these as request shapes, not fixed templates. Preserve the real constraints and expected evidence.

## Repository hygiene

```text
MD inspect the repository for dead code, stale references, duplicate implementations,
identity contamination, broken integrations, and generated junk; preserve core behavior,
fix confirmed issues, run targeted and full validation, and report residual risk
```

## Security hardening

```text
MD threat-model the authentication boundary, map attack paths, validate exploitable
findings in a controlled environment, patch confirmed defects, add regressions,
and produce a remediation report with remaining exposure
```

## Data cleaning and analysis

```text
MD profile this dataset, define quality rules, preserve lineage, clean reproducibly,
quantify changes, analyze decision-relevant patterns, visualize uncertainty,
and deliver the transformed data plus a validation report
```

## Project planning

```text
MD interrogate the brief, identify missing decisions and dependencies, construct a
milestone plan with owners, critical path, risk register, schedule assumptions,
review gates, and a status-reporting cadence
```

## Creative preproduction

```text
MD interrogate the audience, message, medium, constraints, references, and desired
emotion; produce an idea board, moodboard brief, narrative options, previz plan,
shot or asset list, schedule, approvals, and production handoff
```

## PR and media operations

```text
MD define the communications objective, stakeholders, proof points, risk boundaries,
media angles, outreach sequence, spokesperson materials, content calendar,
measurement plan, and crisis escalation rules
```

## Narrowing a close route

```powershell
python tools/md.py lookup "your outcome" --limit 8
python tools/md.py compare <candidate-a> <candidate-b>
python tools/md.py explain <winner>
```
