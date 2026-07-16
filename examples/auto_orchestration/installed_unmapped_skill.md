# Example: Explicitly Requested Installed but Unmapped Skill

## Request

Use `/code-review` for this change review.

The supplied inventory shows `code-review` on disk, but it has no curated MD registry route.

## Behavior

```text
skill_status = installed_unmapped
→ MD-192 checks task fit
→ runtime reads SKILL.md and probes tools, permissions, provenance, inputs, outputs, and side effects
→ MD-196 executes only if the probe and authority pass
→ raw output remains quarantined
→ target code-quality prompt independently verifies the review
```

The system does not route to `find-skills`, because the requested skill is already installed. It also does not auto-trust the skill merely because it exists.
