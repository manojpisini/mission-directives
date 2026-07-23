#!/usr/bin/env python3
"""Parse MD invocation text into deterministic routing context.

This module only inspects the user request and routing policy metadata. It never
opens prompt bodies, which keeps intent detection fast, explainable, and cheap.
"""

from __future__ import annotations

import re
from typing import Any


TARGET_PATTERN = re.compile(r"\b(?:MD-\d{2,3}|C-\d{1,3}|[A-Z][A-Z0-9_]+)\b")


def _normalized(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_phrase = _normalized(phrase)
    return bool(
        normalized_phrase
        and re.search(rf"(?:^| )({re.escape(normalized_phrase)})(?: |$)", text)
    )


def _strip_phrase(text: str, phrase: str) -> str:
    normalized_phrase = _normalized(phrase)
    return re.sub(
        rf"(?:^| )({re.escape(normalized_phrase)})(?= |$)",
        " ",
        text,
    ).strip()


def target_ids(value: str) -> list[str]:
    """Return ordered prompt/scenario/pack identifiers from policy text."""
    return list(dict.fromkeys(TARGET_PATTERN.findall(value)))


def parse_keyword_context(request: str, policy: dict[str, Any]) -> dict[str, Any]:
    """Parse an invocation slug, exact target, modifiers, and shortcut matches."""
    original = request.strip()
    if not original:
        raise ValueError("intent request cannot be empty")

    invocation_slugs = policy.get("invocation_slugs", [policy.get("keyword", "MD")])
    slug_pattern = "|".join(re.escape(slug) for slug in invocation_slugs)
    invocation_match = re.match(rf"^(?:{slug_pattern})(?:\s+|:\s*)", original, re.I)
    bare_invocation = re.fullmatch(rf"(?:{slug_pattern})", original, re.I)
    invoked = invocation_match is not None or bare_invocation is not None
    intent_text = original[invocation_match.end() :] if invocation_match else original
    if bare_invocation:
        intent_text = ""
    intent_text = intent_text.strip()
    exact_match = re.fullmatch(r"(?:MD-\d{2,3}|C-\d{1,3})", intent_text, re.I)
    exact_target = exact_match.group(0).upper() if exact_match else None

    normalized_intent = _normalized(intent_text)
    modifiers: dict[str, str] = {}
    modifier_matches: list[dict[str, str]] = []
    lookup_text = normalized_intent
    for dimension, values in policy.get("context_modifiers", {}).items():
        ranked = sorted(
            values,
            key=lambda row: len(_normalized(row["phrase"]).split()),
            reverse=True,
        )
        for row in ranked:
            if _contains_phrase(normalized_intent, row["phrase"]):
                modifiers[dimension] = row["value"]
                modifier_matches.append(
                    {
                        "dimension": dimension,
                        "phrase": row["phrase"],
                        "value": row["value"],
                    }
                )
                lookup_text = _strip_phrase(lookup_text, row["phrase"])
                break

    shortcut_candidates = []
    for order, row in enumerate(policy.get("shortcut_routes", [])):
        if _contains_phrase(normalized_intent, row["keyword"]):
            shortcut_candidates.append(
                {
                    **row,
                    "targets": target_ids(row["target"]),
                    "priority": int(row.get("priority", 0)),
                    "route_family": row.get("route_family", row["keyword"]),
                    "_order": order,
                }
            )
    shortcut_candidates.sort(
        key=lambda row: (
            -row["priority"],
            -len(_normalized(row["keyword"]).split()),
            row["_order"],
        )
    )
    shortcuts = []
    claimed_families = set()
    for row in shortcut_candidates:
        if row["route_family"] in claimed_families:
            continue
        claimed_families.add(row["route_family"])
        row.pop("_order", None)
        shortcuts.append(row)

    return {
        "original": original,
        "invoked": invoked,
        "invocation_slug": (
            original[: invocation_match.end()].strip(" :")
            if invocation_match
            else original if bare_invocation else None
        ),
        "intent": intent_text,
        "normalized_intent": normalized_intent,
        "lookup_query": lookup_text or normalized_intent,
        "exact_target": exact_target,
        "modifiers": modifiers,
        "modifier_matches": modifier_matches,
        "shortcuts": shortcuts,
    }
