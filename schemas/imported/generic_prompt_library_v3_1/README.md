# Imported Schema Namespace

Files retain their `CP-*` names because `CP-*` is the Generic Prompt Library's canonical identity and is embedded in each schema's `$id` and `prompt_id` constraint.

Mission Directives assigns separate `MD-*` routing identities. The active mapping is stored in prompt frontmatter and `catalog.json`.

Renaming these schemas to `MD-*` would not improve invocation and would break direct source checksums, upstream traceability, and deterministic re-import comparison. User-facing routing should use the owning `MD-*` prompt or its aliases; `CP-*` identifies the imported source contract.
