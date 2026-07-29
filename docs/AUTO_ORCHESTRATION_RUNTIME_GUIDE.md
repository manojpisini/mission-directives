# Auto-Orchestration Runtime Guide

## Purpose

The automatic layer is a conditional compiler. It never loads all auto-prompts by default. It evaluates route-changing intent ambiguity, genuine skill need, missing capability, acquisition authority, skill fit, and loop eligibility before adding a node.

## Compile from a context file

Create JSON conforming to `schemas/auto_orchestration_request.schema.json`, then run:

```bash
python tools/md.py auto-compile request.json
```

The result separates active prompts, conditional branch prompts, rejected capabilities, skill status, and loop eligibility.

## Existing output preflight

Scenario planning checks each selected prompt's declared primary output path before execution. Existing output is withheld by default and reported in `artifact_reuse.existing_outputs`; `execution_prompts` contains only nodes that may run immediately. Ask the returned question, then re-plan with `--existing-output reuse` after current-scope verification or `--existing-output rerun` after explicit user approval. Never infer validity from file presence alone.

## Questioning behavior

`MD-191` may wrap any task but asks only questions whose answers change the graph, authority, evidence lane, output medium, budget, skill need, loop eligibility, or acceptance decision. It reuses answered context and normally asks one question at a time.

## Missing skill flow

1. `MD-192` proves a material capability gap.
2. `MD-193` invokes `find-skills` or native discovery and qualifies exact candidates without installing.
3. `MD-194` installs a qualified candidate to both global locations when policy permits.
4. `MD-195` creates a narrow skill only when discovery is empty, native execution is insufficient, and reusable demand justifies maintenance.
5. `MD-196` executes the exact skill once, quarantines output, and verifies the target artifact.

Installation and creation are mutually exclusive conditional branches.

## Loop flow

`MD-197` may wrap any prompt, scenario, or exact skill. It must prove a finite queue or measurable refinement objective. `MD-198` independently decides continue, complete, plateau, budget stop, safety stop, rollback, or human escalation after every pass.

## Safety

Automatic does not mean ungoverned. External effects, unpinned acquisition, permission expansion, deployment, publication, sending, deletion, and irreversible mutation still require the applicable policy and authority.
