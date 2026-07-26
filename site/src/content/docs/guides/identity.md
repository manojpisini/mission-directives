---
title: Identity and Compatibility
description: Why prompt IDs use MD, how imported CP identities remain traceable, and how compatibility avoids contamination.
---

## Canonical identity

Mission Directives owns the `MD-###` capability namespace. It is stable across filenames, catalogs, scenarios, templates, fixtures, and evaluation records.

`C-###` identifies a composite scenario. Department-pack IDs identify curated capability sets, not prompts. Skill IDs identify execution adapters or native aliases.

## CP provenance

`CP-###` names belong to the imported Generic Prompt Library provenance layer. They are not Mission Directives prompt identities. Imported CP profiles and schemas preserve source traceability, compatibility, and migration evidence while their adopted capabilities receive permanent MD identities.

This separation prevents:

- imported IDs from masquerading as canonical MD capabilities;
- schemas from being confused with executable prompts;
- stale source references from leaking into runtime routing;
- future imports from renumbering established MD contracts.

## Identity checks

The compatibility identity registry maps permanent capabilities and legacy references. Catalog records declare `capability_id`, `prompt_slug`, `identity_status`, and canonical paths. Validators check reciprocal pairs, crosswalks, scenarios, fixtures, and manifests against those identities.

## Rules for additions

Use `MD-199` or `tools/add_prompt.py`. Never place a prompt body directly into `prompts/`; transactional addition keeps the catalog, identity registry, graph, templates, skills, fixtures, evaluations, tests, and manifest synchronized.
