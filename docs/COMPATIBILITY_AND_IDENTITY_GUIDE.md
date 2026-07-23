# Identity and Runtime Path Guide

## Purpose

Mission Directives exposes current, permanent capability identities and current
agent skill destinations. The repository does not ship historical release maps,
redirect tables, or retired project snapshots.

## Current identity contract

`compatibility/capability_identity_registry.json` is the generated registry for
every prompt in `catalog.json`. Each row binds:

- `capability_id`: permanent semantic machine identity;
- `prompt_id`: permanent prompt identifier;
- `prompt_slug`: stable human-readable identity;
- `canonical_path`: current prompt body location;
- `identity_status`: current identity state.

Consumers should store `capability_id` and `prompt_id`. Do not route by filename,
display title, or sequence number.

## Current agent path contract

`compatibility/agent_skill_paths.json` defines supported skill installation
destinations for Agents, Claude Code, and OpenCode. Installers load this file
through `tools/agent_paths.py`; shell wrappers delegate to the same Python
implementation so platform behavior remains aligned.

## Change procedure

1. Preserve an identity when its observable capability remains the same.
2. Add a new permanent identity when authority or observable outcome changes.
3. Update prompt metadata, catalogs, scenarios, crosswalks, fixtures, and docs.
4. Regenerate the capability identity registry.
5. Run identity, reproducibility, installer-path, and manifest validation.
6. Publish breaking consumer guidance outside the runtime repository when a
   downstream system requires a transition record.

## Validation failures

The suite fails when:

- an active capability identity disappears;
- prompt IDs, capability IDs, or slugs are duplicated;
- the identity registry count differs from the catalog;
- a registry row points to a missing canonical prompt;
- a scenario or crosswalk references an unknown current identity;
- agent skill destinations diverge across installer entry points.

## Review checklist

- [ ] Permanent identity was preserved where meaning was preserved.
- [ ] New authority or outcomes received a new identity.
- [ ] Scenarios, crosswalks, fixtures, and docs use current IDs.
- [ ] Agent path changes were made in the canonical path policy.
- [ ] Generated identity and manifest artifacts were refreshed.
- [ ] Focused and full validation passed.
