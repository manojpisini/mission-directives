# Compatibility and Identity Guide

## Purpose

This guide explains how prompts and capabilities retain stable meaning while files, titles, sequences, scenarios, and architecture evolve.

The suite previously reused numeric identifiers during major restructuring. Permanent semantic identities and a compatibility registry prevent future integrations from silently routing to a different capability.

## Identity fields

### `capability_id`

Permanent semantic machine identity.

Example:

```yaml
capability_id: md.debugging.debugging-root-cause-and-bug-resolution-investigation-and-plan
```

Consumers should prefer this field for durable references.

### `prompt_id`

Permanent identifier within the current namespace. It is not reassigned after publication.

### `prompt_slug`

Stable human-readable identifier. Renames require an alias rather than silent replacement.

### `sequence`

Presentation order only. It is not a routing key and may change without changing capability identity.

### `identity_status`

Current identities use `permanent`. A future retirement must use explicit compatibility records rather than deleting history.

## Legacy namespaces

An old numeric ID may have a different meaning from a current ID. Historical references therefore require a namespace:

```text
legacy:v5.2:MD-12
```

A bare current `MD-12` refers only to the current catalog.

## Compatibility registry

```text
compatibility/
  aliases.json
  capability_identity_registry.json
  original_66_to_current.json
  deprecated_prompt_ids.json
  scenario_redirects.json
```

### Original-area coverage

`original_66_to_current.json` maps every original capability area to current prompt IDs and classifies the relationship:

- preserved;
- renamed;
- merged;
- split;
- expanded;
- intentionally retired.

A mapping should explain whether current coverage is equivalent, stronger, narrower, or redistributed.

## Rename procedure

1. Keep the existing capability ID.
2. Add the old slug to aliases.
3. Update the title and canonical path if required.
4. Update catalogs, scenarios, crosswalks, docs, and fixtures.
5. Verify external consumers can resolve the alias.

## Merge procedure

1. Identify the surviving capability or new composite owner.
2. Map every old capability to the replacement set.
3. Preserve output and behavior compatibility where promised.
4. Add redirects or explicit failure for unsupported behavior.
5. Update dependent scenarios and agent mappings.
6. Do not reuse retired prompt IDs.

## Split procedure

A split may create:

- investigation and executive pair;
- several specialist capabilities;
- a primary prompt plus reusable gates.

The compatibility record must specify which replacement owns each old outcome.

## Retirement procedure

Retire only when:

- usage and dependencies are known;
- replacement or reason is documented;
- scenarios and integrations are migrated;
- aliases return a clear deprecation result;
- artifacts remain readable;
- the ID is permanently reserved.

## Consumer guidance

External tools should store:

```json
{
  "capability_id": "...",
  "prompt_id": "MD-29",
  "prompt_slug": "...",
  "catalog_revision": "..."
}
```

Do not route by filename or sequence.

## Cross-catalog implications

Agent and prompt-type mappings use permanent capability IDs. A title similarity match is not sufficient to update an approved mapping.

## Validation failures

The suite should fail when:

- an active capability ID disappears;
- IDs or slugs are duplicated;
- a current prompt ID is reused;
- a legacy mapping points to missing prompts;
- a scenario references a retired capability without redirect;
- identity registry count differs from the catalog;
- original-area coverage becomes incomplete.

## Review checklist

- [ ] Change type is rename, merge, split, replacement, or retirement.
- [ ] Permanent identity is preserved where meaning is preserved.
- [ ] Aliases and redirects are explicit.
- [ ] Original coverage remains provable.
- [ ] Scenarios and crosswalks are updated.
- [ ] No numeric ID is repurposed.
- [ ] Fixtures and manuals reflect the current route.
