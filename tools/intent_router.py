#!/usr/bin/env python3
"""Explainable deterministic lookup for Mission Directives routing metadata."""

from __future__ import annotations

import difflib
import math
import re
from collections import Counter
from typing import Any, Callable


def _normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def _concept_maps(config: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    single: dict[str, str] = {}
    phrases: dict[str, str] = {}
    for concept, aliases in config.get("concepts", {}).items():
        for alias in [concept, *aliases]:
            normalized = _normalized(alias)
            parts = normalized.split()
            if len(parts) == 1:
                single[parts[0]] = concept
            elif normalized:
                phrases[normalized] = concept
    return single, phrases


def _concepts_for_text(
    value: str,
    single: dict[str, str],
    phrases: dict[str, str],
) -> set[str]:
    normalized = _normalized(value)
    concepts = {single.get(token, token) for token in normalized.split()}
    padded = f" {normalized} "
    for phrase, concept in phrases.items():
        if f" {phrase} " in padded:
            concepts.add(concept)
    return concepts


def _correct_token(
    token: str,
    vocabulary: set[str],
    typo_policy: dict[str, Any],
) -> str:
    if token in vocabulary or len(token) < int(typo_policy.get("minimum_token_length", 5)):
        return token
    threshold = float(typo_policy.get("similarity_threshold", 0.86))
    margin = float(typo_policy.get("minimum_margin", 0.04))
    ranked = sorted(
        (
            (difflib.SequenceMatcher(None, token, candidate).ratio(), candidate)
            for candidate in vocabulary
            if abs(len(candidate) - len(token)) <= 2
        ),
        reverse=True,
    )
    if not ranked or ranked[0][0] < threshold:
        return token
    runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
    return ranked[0][1] if ranked[0][0] - runner_up >= margin else token


def _analyze_query(
    query: str,
    config: dict[str, Any],
    single: dict[str, str],
    phrases: dict[str, str],
) -> dict[str, Any]:
    stopwords = set(config.get("stopwords", []))
    raw_tokens = [token for token in _tokens(query) if token not in stopwords]
    vocabulary = set(single)
    corrected_tokens: list[str] = []
    corrections: dict[str, str] = {}
    for token in raw_tokens:
        corrected = _correct_token(token, vocabulary, config.get("typo_correction", {}))
        corrected_tokens.append(corrected)
        if corrected != token:
            corrections[token] = corrected
    corrected_text = " ".join(corrected_tokens)
    concepts = [single.get(token, token) for token in corrected_tokens]
    padded = f" {_normalized(corrected_text)} "
    for phrase, concept in phrases.items():
        if f" {phrase} " in padded:
            concepts.append(concept)
    return {
        "raw_tokens": raw_tokens,
        "corrected_tokens": corrected_tokens,
        "concepts": list(dict.fromkeys(concepts)),
        "corrections": dict(sorted(corrections.items())),
        "normalized": _normalized(query),
        "scoring_version": config.get("schema_version", "unknown"),
    }


def _prompt_search_text(prompt: dict[str, Any]) -> str:
    return " ".join(
        [
            prompt.get("title", ""),
            prompt.get("description", ""),
            prompt.get("category", ""),
            prompt.get("prompt_role", ""),
            prompt.get("prompt_type", ""),
            prompt.get("change_surface", ""),
            " ".join(prompt.get("aliases", [])),
            " ".join(prompt.get("tags", [])),
            " ".join(prompt.get("preferred_skills", [])),
            " ".join(prompt.get("produces", [])),
        ]
    )


def _candidate_rows(
    *,
    cat: dict[str, Any],
    scenarios: dict[str, Any],
    packs: dict[str, Any],
    skills: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    weights: dict[str, Any],
    kind: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if kind in {"all", "prompts"}:
        prompt_weights = weights["prompt"]
        for prompt in cat["prompts"]:
            rows.append(
                {
                    "kind": "prompt",
                    "id": prompt["prompt_id"],
                    "title": prompt["title"],
                    "description": prompt.get("description"),
                    "category": prompt.get("category"),
                    "role": prompt.get("prompt_role"),
                    "default_mode": prompt.get("default_mode"),
                    "path": prompt.get("canonical_path"),
                    "aliases": prompt.get("aliases", []),
                    "fields": [
                        ("title", prompt.get("title", ""), prompt_weights["title"]),
                        ("aliases", " ".join(prompt.get("aliases", [])), prompt_weights["aliases"]),
                        ("description", prompt.get("description", ""), prompt_weights["description"]),
                        ("category", prompt.get("category", ""), prompt_weights["category"]),
                        ("role", prompt.get("prompt_role", ""), prompt_weights["role"]),
                        ("type", prompt.get("prompt_type", ""), prompt_weights["type"]),
                        ("tags", " ".join(prompt.get("tags", [])), prompt_weights["tags"]),
                        ("skills", " ".join(prompt.get("preferred_skills", [])), prompt_weights["skills"]),
                        ("capability", prompt.get("capability_id", ""), prompt_weights["capability"]),
                        ("change_surface", prompt.get("change_surface", ""), prompt_weights["change_surface"]),
                        ("outputs", " ".join(prompt.get("produces", [])), prompt_weights["outputs"]),
                    ],
                }
            )
    if kind in {"all", "scenarios"}:
        scenario_weights = weights["scenario"]
        for scenario in scenarios.get("composite_scenarios", []):
            prompt_rows = [by_id[pid] for pid in scenario.get("prompts", []) if pid in by_id]
            rows.append(
                {
                    "kind": "scenario",
                    "id": scenario["scenario_id"],
                    "title": scenario["title"],
                    "description": scenario.get("purpose"),
                    "default_mode": scenario.get("default_mode"),
                    "aliases": scenario.get("aliases", []),
                    "fields": [
                        ("title", scenario.get("title", ""), scenario_weights["title"]),
                        ("purpose", scenario.get("purpose", ""), scenario_weights["purpose"]),
                        ("prompt_titles", " ".join(p.get("title", "") for p in prompt_rows), scenario_weights["prompt_titles"]),
                        ("prompt_descriptions", " ".join(p.get("description", "") for p in prompt_rows), scenario_weights["prompt_descriptions"]),
                        ("prompt_tags", " ".join(" ".join(p.get("tags", [])) for p in prompt_rows), scenario_weights["prompt_tags"]),
                    ],
                }
            )
    if kind in {"all", "packs"}:
        pack_weights = weights["pack"]
        for pack_id, prompt_ids in packs["department_packs"].items():
            prompt_rows = [by_id[pid] for pid in prompt_ids if pid in by_id]
            title = pack_id.replace("_", " ").title()
            rows.append(
                {
                    "kind": "pack",
                    "id": pack_id,
                    "title": title,
                    "description": "Department discovery profile; compile to a smaller task-specific graph before execution.",
                    "aliases": [],
                    "fields": [
                        ("title", title, pack_weights["title"]),
                        ("prompt_titles", " ".join(p.get("title", "") for p in prompt_rows), pack_weights["prompt_titles"]),
                        ("prompt_tags", " ".join(" ".join(p.get("tags", [])) for p in prompt_rows), pack_weights["prompt_tags"]),
                    ],
                }
            )
    if kind in {"all", "skills"}:
        skill_weights = weights["skill"]
        for skill in skills["skills"]:
            prompt_rows = [by_id[pid] for pid in skill.get("prompt_routes", []) if pid in by_id]
            sid = skill["skill_id"]
            rows.append(
                {
                    "kind": "skill",
                    "id": sid,
                    "title": sid.replace("-", " ").title(),
                    "description": skill.get("purpose"),
                    "aliases": [],
                    "skill_id": sid,
                    "fields": [
                        ("id", sid, skill_weights["id"]),
                        ("purpose", skill.get("purpose", ""), skill_weights["purpose"]),
                        ("kind", skill.get("kind", ""), skill_weights["kind"]),
                        ("prompt_titles", " ".join(p.get("title", "") for p in prompt_rows), skill_weights["prompt_titles"]),
                    ],
                }
            )
    return rows


def _route_hint_boost(
    row: dict[str, Any],
    query: dict[str, Any],
    config: dict[str, Any],
) -> tuple[float, list[str]]:
    concepts = set(query["concepts"])
    normalized = f" {query['normalized']} "
    total = 0.0
    matched_hints: list[str] = []
    for hint in config.get("route_hints", []):
        if row["id"] not in hint.get("targets", []):
            continue
        if not set(hint.get("all_concepts", [])) <= concepts:
            continue
        any_concepts = set(hint.get("any_concepts", []))
        if any_concepts and not concepts & any_concepts:
            continue
        phrases = [_normalized(value) for value in hint.get("phrases", [])]
        if phrases and not any(f" {phrase} " in normalized for phrase in phrases):
            continue
        total += float(hint.get("boost", 0))
        matched_hints.append(hint["hint_id"])
    return total, matched_hints


def lookup_routes(
    query: str,
    *,
    cat: dict[str, Any],
    scenarios: dict[str, Any],
    packs: dict[str, Any],
    skills: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    config: dict[str, Any],
    skill_status: Callable[[str], dict[str, Any]],
    limit: int = 8,
    kind: str = "all",
) -> dict[str, Any]:
    """Rank metadata candidates with concept coverage and auditable score evidence."""
    if kind not in {"all", "prompts", "scenarios", "packs", "skills"}:
        raise ValueError(f"Invalid lookup kind: {kind}")
    query = query.strip()
    if not query:
        raise ValueError("lookup query cannot be empty")

    scoring = config["scoring"]
    single, phrases = _concept_maps(config)
    analysis = _analyze_query(query, config, single, phrases)
    query_concepts = set(analysis["concepts"])
    rows = _candidate_rows(
        cat=cat,
        scenarios=scenarios,
        packs=packs,
        skills=skills,
        by_id=by_id,
        weights=scoring["field_weights"],
        kind=kind,
    )

    document_frequency: Counter[str] = Counter()
    for row in rows:
        row["_field_concepts"] = [
            (name, _concepts_for_text(text, single, phrases), float(weight))
            for name, text, weight in row["fields"]
        ]
        row["_document_concepts"] = set().union(
            *(concepts for _name, concepts, _weight in row["_field_concepts"])
        )
        document_frequency.update(row["_document_concepts"])
    count = max(1, len(rows))
    idf = {
        concept: 1.0 + math.log((count + 1) / (frequency + 1))
        for concept, frequency in document_frequency.items()
    }

    results: list[dict[str, Any]] = []
    normalized_query = _normalized(query)
    for row in rows:
        identifier = row["id"]
        normalized_title = _normalized(row["title"])
        normalized_aliases = {_normalized(value) for value in row.get("aliases", [])}
        match_type = "concept"
        phrase_boost = 0.0
        if normalized_query == _normalized(identifier):
            phrase_boost += float(scoring["exact_id"])
            match_type = "exact_id"
        elif normalized_query == normalized_title:
            phrase_boost += float(scoring["exact_title"])
            match_type = "exact_title"
        elif normalized_query in normalized_aliases:
            phrase_boost += float(scoring["exact_alias"])
            match_type = "exact_alias"
        elif normalized_title and (
            normalized_query in normalized_title or normalized_title in normalized_query
        ):
            phrase_boost += float(scoring["title_phrase"])
            match_type = "title_phrase"

        matched: set[str] = set()
        field_matches: dict[str, list[str]] = {}
        best_concept_weights: dict[str, float] = {}
        for field_name, field_concepts, weight in row["_field_concepts"]:
            hits = query_concepts & field_concepts
            if not hits:
                continue
            field_matches[field_name] = sorted(hits)
            matched.update(hits)
            for hit in hits:
                best_concept_weights[hit] = max(best_concept_weights.get(hit, 0.0), weight)
        field_match = sum(
            weight * idf.get(concept, 1.0)
            for concept, weight in best_concept_weights.items()
        )
        coverage = len(matched) / len(query_concepts) if query_concepts else 0.0
        coverage_boost = float(scoring["coverage_boost"]) * coverage
        hint_boost, hint_ids = _route_hint_boost(row, analysis, config)
        kind_boost = 0.0
        if row["kind"] == "scenario" and len(query_concepts) >= 4:
            kind_boost += float(scoring.get("scenario_composition_boost", 0))
        if row["kind"] == "pack" and " department pack " in f" {normalized_query} ":
            kind_boost += float(scoring.get("department_pack_phrase_boost", 0))
        score = field_match + phrase_boost + coverage_boost + hint_boost + kind_boost

        exact = match_type in {"exact_id", "exact_title", "exact_alias", "title_phrase"}
        minimum_matches = (
            1
            if len(query_concepts) <= 2
            else int(scoring.get("minimum_long_query_matches", 2))
        )
        short_coverage_ok = (
            len(query_concepts) > 2
            or coverage >= float(scoring.get("minimum_short_query_coverage", 0.5))
        )
        if (
            score < float(scoring.get("minimum_score", 10))
            or (len(matched) < minimum_matches and not exact and hint_boost <= 0)
            or (not short_coverage_ok and not exact)
        ):
            continue

        result = {
            key: value
            for key, value in row.items()
            if key not in {"fields", "aliases", "skill_id"} and not key.startswith("_")
        }
        result.update(
            {
                "score": round(score, 3),
                "match_type": match_type,
                "matched_terms": sorted(matched),
                "matched_concepts": sorted(matched),
                "query_token_coverage": round(coverage, 3),
                "query_concept_coverage": round(coverage, 3),
                "matched_route_hints": hint_ids,
                "field_matches": field_matches,
                "score_breakdown": {
                    "field_match": round(field_match, 3),
                    "phrase_boost": round(phrase_boost, 3),
                    "route_hint_boost": round(hint_boost, 3),
                    "coverage_boost": round(coverage_boost, 3),
                    "kind_boost": round(kind_boost, 3),
                },
            }
        )
        if row["kind"] == "skill":
            result["skill_status"] = skill_status(identifier)
        results.append(result)

    kind_priority = {"scenario": 0, "prompt": 1, "skill": 2, "pack": 3}
    results.sort(
        key=lambda row: (-row["score"], kind_priority.get(row["kind"], 9), row["id"])
    )
    results = results[: max(1, min(limit, 50))]
    if not results:
        return {
            "status": "no_confident_match",
            "query": query,
            "query_analysis": analysis,
            "kind": kind,
            "results": [],
            "next_step": "Refine the terms or use MD-191 to ask one route-changing clarification question.",
        }

    top_score = results[0]["score"]
    second_score = results[1]["score"] if len(results) > 1 else 0.0
    top_margin = max(0.0, (top_score - second_score) / max(top_score, 1.0))
    for index, row in enumerate(results):
        relative = row["score"] / max(top_score, 1.0)
        margin = top_margin if index == 0 else 0.0
        confidence = (
            0.5 * row["query_concept_coverage"]
            + 0.3 * min(1.0, row["score"] / 100.0)
            + 0.15 * relative
            + 0.05 * margin
        )
        row["confidence"] = round(min(1.0, confidence), 3)
    return {
        "status": "matched",
        "query": query,
        "query_analysis": analysis,
        "kind": kind,
        "result_count": len(results),
        "results": results,
        "next_step": f"Run python tools/md.py explain {results[0]['id']} before execution.",
    }
