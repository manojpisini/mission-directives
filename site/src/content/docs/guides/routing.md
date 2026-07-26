---
title: Route and Score
description: How the concept dictionary, typo recovery, route hints, ranking, and confidence model select a capability.
---

The router is deterministic and metadata-first. It does not open prompt bodies while selecting an owner.

## Pipeline

1. Parse exact IDs and explicit `MD` invocation context.
2. Resolve specific policy shortcuts such as `audit fix verify`.
3. Normalize words and phrases through `config/router_keywords.json`.
4. Correct only conservative, unambiguous vocabulary typos.
5. Enrich prompt, scenario, department-pack, and skill candidates.
6. Score concept evidence by rarity, field authority, phrase evidence, route hints, kind fit, and query coverage.
7. Calibrate confidence from absolute evidence, relative rank, top margin, and concept coverage.
8. Return an honest no-match when evidence is insufficient.

## Concept catalog

Each concept has aliases. Multiword phrases are matched before isolated words so `supply chain` keeps its domain meaning. Stopwords remove routing noise but do not erase domain terms. The catalog is a runtime file, so installed projects use the same scoring vocabulary as the source repository.

## Score evidence

Every candidate exposes:

- `matched_concepts`
- `query_concept_coverage`
- `score_breakdown`
- `field_matches`
- `matched_route_hints`

A repeated concept is not multiplied across every metadata field. The strongest authoritative field wins for that concept; this limits keyword stuffing and verbose metadata bias. Rarity weighting gives discriminating concepts more influence than common concepts. Route hints provide narrow, reviewable boosts for requests whose complete outcome has an established owner.

## Typo recovery

Corrections require a token long enough to correct safely, a close match above the configured threshold, and a sufficient margin over the second-best candidate. The response records every correction. Unknown terms remain unknown rather than being force-fit.

## Diagnose routing

```powershell
python tools/md.py lookup "repositry hygene cleanup" --limit 8
python tools/md.py compare C-25 C-04 C-108
python tools/md.py explain C-25
```

Use the smallest graph that owns the observable outcome. A high lexical score does not expand authority and does not waive prerequisites, approval, evidence, or verification.
