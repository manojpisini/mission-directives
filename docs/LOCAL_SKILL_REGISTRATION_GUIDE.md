# Local Skill Registration Guide

## Purpose

This guide governs skills created locally rather than installed from a reviewed remote repository. Local creation is a fallback for a genuine capability gap, not a shortcut around native prompt composition, an excuse to create a skill for one trivial task, or permission to bypass supply-chain controls.

## When local creation is justified

Create a local skill only when all of the following are true:

1. The requested capability is materially reusable.
2. Native prompt composition cannot satisfy the acceptance criteria cleanly.
3. `find-skills` found no sufficiently trustworthy and task-fit candidate.
4. The skill has a narrow, testable input/output contract.
5. Required permissions and external effects are explicitly bounded.
6. A native fallback remains documented.

Do not create a skill merely because a user mentions a technique, because a skill name sounds convenient, or because repeated execution could instead be handled by the generic loop orchestrator.

## Creation workflow

Use `MD-195` with `skill-creator` and, where available, `writing-skills`. The resulting package must be created in a staging directory and include at minimum:

- `SKILL.md` with identity, trigger conditions, required inputs, method, outputs, permissions, failure behavior, and examples;
- a machine-readable capability and permission declaration;
- healthy, problematic, and adversarial fixtures;
- prohibited actions and stop conditions;
- a conformance contract describing the artifact expected by MD;
- provenance for any copied or adapted material.

The created package remains a draft until review and deterministic conformance checks pass.

## Dual registration

Register an approved staged package with:

```powershell
.\tools\register_local_skill_dual.ps1 `
  -SourceDirectory ".\staging\my-skill" `
  -SkillId "my-skill"
```

The script validates the presence of `SKILL.md`, copies the complete skill directory to both locations, computes hashes, and verifies that the registered copies match:

```text
%USERPROFILE%\.agents\skills\{skill_id}
%USERPROFILE%\.config\opencode\skills\{skill_id}
```

Use `-Reinstall` only for an explicitly approved replacement. Registration failure at either destination is a failed operation; do not treat a one-sided copy as success.

## Trust and quarantine

Presence is not trust. A newly registered local skill remains quarantined until:

- its source and permission declaration are reviewed;
- its fixtures pass;
- the generic skill adapter verifies the real output shape;
- the target artifact passes independent domain verification;
- its registry entry is promoted according to governance policy.

A local skill must not auto-select solely because it exists in both directories.

## Updating a local skill

Treat every material update as a new candidate revision. Re-run fixtures and conformance checks, compare permissions and external effects, then replace both registered copies together. Record the old and new hashes in the registration receipt or change record.

## Removal and rollback

To retire a skill, first remove or redirect every registry and prompt route that depends on it. Preserve the last approved source and receipt when audit or rollback requirements apply. Delete both registered copies only after confirming that no active run references the skill.

## Failure conditions

Stop and record `!STOP:{reason}` when:

- the staged package lacks `SKILL.md`;
- the skill requests undeclared access;
- the two destination hashes differ;
- fixtures or conformance tests fail;
- the requested identifier collides with another capability;
- the task can be completed more safely through native prompt execution.

## Verification checklist

Registration is complete only when the source package is reviewed, both destinations contain identical verified copies, the registry entry reflects the exact skill identity, the conformance fixture passes, and downstream use remains subject to the normal MD verification gates.
