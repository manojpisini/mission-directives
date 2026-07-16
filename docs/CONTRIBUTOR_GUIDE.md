# Contributor Guide

## Purpose

This guide explains how to change the suite without creating duplicate capabilities, weakening safety, breaking permanent identities, or allowing generated artifacts to drift.

## Before adding a prompt

Confirm that the requested outcome is not already owned by:

- an existing prompt;
- a composite scenario;
- a department pack plus routing;
- a reusable gate;
- an existing prompt with a new output profile;
- a skill adapter.

Add a prompt only when the outcome, evidence surface, method, action boundary, artifact, or verification contract is materially distinct.

## Permanent identity rules

- Do not reuse `prompt_id`.
- Do not change `capability_id` after publication.
- Do not repurpose a slug for a different capability.
- Use aliases and redirects for renames or merges.
- Update compatibility mappings when consolidating capabilities.

## Prompt-body requirements

Every prompt must include canonical authorization, tool policy, runtime markers, output contract, and completion criteria.

Every executive must include decision rules and verification reference.

Do not use `<security_execution_boundary>` or other synonyms.

Do not copy investigative verification into the executive.

Read:

- `PROMPT_STRUCTURE_STANDARD.md`
- `PROMPT_SUITE_CONVENTIONS.md`
- `docs/PROMPT_BODY_AUTHORING_GUIDE.md`

## Tests-first workflow

### Defect

1. Add a failing regression test.
2. Confirm expected failure.
3. Make the smallest correction.
4. Run focused and full tests.

### New capability

Add together:

- prompt file and permanent identity;
- catalog entry;
- atomic scenario;
- relevant composite scenario or routing rule;
- capability graph edges;
- healthy/problematic/adversarial fixtures;
- output schemas if required;
- department pack discovery;
- skill mappings if relevant;
- manuals and examples;
- manifest.

### New pair

Also add:

- reciprocal pair metadata;
- frozen handoff artifacts;
- contaminated-handoff fixture;
- pair-versus-single definition;
- executive decision rules;
- verification reference;
- justification in capability architecture.

## Derived artifacts

The following should be generated rather than hand-maintained where tools exist:

- `capability_graph.json`;
- `BODY_QUALITY_AUDIT.json` and `.md`;
- `MANIFEST.json`;
- test and validation status files.

## Documentation requirements

A change that alters behavior must update the relevant manual. Do not rely on a README paragraph alone when the subsystem has operational detail.

Manual claims must identify proof level and limitations.

## Review checklist

- [ ] Outcome is distinct.
- [ ] Identity is permanent.
- [ ] Role and evidence lane are correct.
- [ ] Authorization and tools are least-privileged.
- [ ] Runtime markers are active.
- [ ] Method is domain-specific.
- [ ] Completion is task-specific.
- [ ] Pair verification is not duplicated.
- [ ] Executive decisions cover conflicts and budgets.
- [ ] Fixtures include adversarial behavior.
- [ ] Generated artifacts are current.
- [ ] Manuals are updated.
- [ ] Full validation passes.

## Commands

```bash
pytest -q
python tools/build_capability_graph.py
python tools/audit_prompt_bodies.py
python tools/run_evaluations.py
python tools/run_tests.py
python tools/build_manifest.py
python tools/validate_suite.py
```

## Documentation links

Use relative links for repository manuals and artifacts. Before submitting a documentation change, run `python tools/check_documentation_links.py`. A link to a renamed or deleted local file is a blocking defect because manuals are part of the executable operating contract.
