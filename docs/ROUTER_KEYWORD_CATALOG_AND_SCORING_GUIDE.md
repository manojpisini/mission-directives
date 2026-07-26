# Router Keyword Catalog and Scoring Guide

## Purpose

This guide defines the deterministic intent-routing vocabulary, scoring model, confidence behavior, diagnostics, and extension workflow. The runtime source of truth is `config/router_keywords.json`; the implementation is `tools/intent_router.py`.

## Selection boundary

Routing selects the smallest capability owner. It does not execute a prompt, expand authority, approve an external effect, or prove completion. Selection reads prompt, scenario, department-pack, and skill metadata. Prompt bodies are loaded only after the selected target is explained.

Exact IDs are resolved before lexical scoring. Policy shortcuts are evaluated before semantic lookup, but generic shortcuts can use `match_mode: exact` so a common word cannot hijack a richer request.

## Query analysis

The router:

1. normalizes case and punctuation;
2. identifies multiword aliases before isolated aliases;
3. removes configured routing stopwords;
4. applies conservative typo correction;
5. maps vocabulary to canonical concepts;
6. retains unmatched terms for transparency.

`query_analysis` reports raw tokens, corrected tokens, concepts, and corrections. Corrections require the configured minimum token length, similarity threshold, and second-best margin. A correction that is not unambiguous is not applied.

## Candidate enrichment

Candidates are built from four catalogs:

- prompts from `catalog.json`;
- atomic and composite scenarios from `SCENARIO_CATALOG.json`;
- department packs from `config/department_packs.json`;
- skills and aliases from `skill_registry.json`.

Scenario search includes the metadata of referenced prompts. This lets a composite graph match its owned outcome without copying every synonym into the scenario title.

## Score components

The score breakdown is evidence, not a hidden aggregate:

| Component | Purpose |
| --- | --- |
| concept-field | strongest authoritative metadata field that supports each concept |
| rarity | increases the value of concepts that discriminate between candidates |
| phrase | rewards exact multiword intent evidence |
| exact | strongly rewards exact ID, title, or canonical phrase matches |
| route hint | applies narrow, checked-in boosts to established outcome owners |
| kind fit | distinguishes prompt, scenario, pack, and skill ownership |
| coverage | rewards candidates that explain more of the query concepts |

One concept receives the maximum applicable field weight, not the sum of every field occurrence. This prevents verbose metadata and repeated keywords from manufacturing rank.

## Confidence

Confidence combines:

- query concept coverage;
- absolute evidence strength;
- the top candidate's advantage over the runner-up;
- relative rank;
- configured minimum evidence.

A result below the threshold returns `no_confident_match`. Operators should add the intended artifact, decision, authority, or domain boundary and rerun. They should not force the first low-evidence candidate.

## Route hints

Route hints are narrow and reviewable. A hint declares phrases or concepts, one or more preferred targets, a boost, and optional route kinds. Use them only when the target owns the complete observable outcome. Do not use hints to conceal weak metadata or to make a broad department pack outrank a specific scenario.

## Extending coverage

1. Add aliases to an existing concept when they are true synonyms.
2. Add a concept when it has distinct routing meaning.
3. Add a route hint only for a stable ownership rule.
4. Add positive, close-alternative, typo, and no-match tests.
5. Run `python -m pytest tests/test_md.py -q`.
6. Inspect `score_breakdown`, `field_matches`, and concept coverage for regressions.
7. Rebuild the manifest after the change is accepted.

Do not add profession names without the outcomes, artifacts, and domain concepts that make them routeable. For example, `publicist` should connect to outreach, briefing, media relations, reputation, and publication controls rather than exist as an isolated token.

## Diagnostics

```bash
python tools/md.py lookup "repositry hygene cleanup" --limit 8
python tools/md.py route "MD prompt suite cleanup"
python tools/md.py compare C-25 C-04 C-108
python tools/md.py explain C-25
```

Review the explanation before loading the selected prompt body.
