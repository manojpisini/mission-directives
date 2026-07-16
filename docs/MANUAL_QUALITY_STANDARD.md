# Manual Quality Standard

## Purpose

Manuals are operational interfaces, not decorative summaries. A manual is acceptable only when a reader can understand the system, perform the task, recognize failure, reproduce validation, and distinguish implemented behavior from planned behavior.

## Required qualities

### Truth

Every factual claim must match the current package. Counts and status values should be generated or cited from canonical files where possible.

Do not describe:

- structural validation as live model proof;
- an unresolved skill as installed;
- an unmeasured model as recommended;
- a machine-reference run as human-approved golden output;
- a draft artifact as published or deployed.

### Audience

Each manual names its intended reader and assumes only the prerequisite knowledge it lists.

### Purpose and scope

The introduction states what the manual covers and what it does not cover.

### Conceptual explanation

Explain why the subsystem exists, not only which commands to run.

### Procedures

Commands and steps are complete, ordered, and reproducible. Paths and filenames match the package.

### Examples

Include at least one successful example and, where failure matters, one failure or refusal example.

### Proof level

Label whether a claim is:

- design intent;
- static validation;
- deterministic test;
- live model measurement;
- live skill conformance;
- human review.

### Failure behavior

Describe stop conditions, rollback, residuals, and common errors. Showing only the happy path is insufficient.

### Cross-references

Link to normative artifacts and related manuals. Avoid copying whole contracts into multiple guides.

### Maintenance

A manual identifies the source files that can make it stale. CI checks file existence and minimum depth, but human review remains responsible for semantic correctness.

## Recommended structure

1. Purpose
2. Audience
3. Prerequisites
4. Concepts
5. Procedure
6. Examples
7. Failure modes
8. Validation
9. Related references

## Anti-patterns

- a three-line manual that only links elsewhere;
- unexplained command dumps;
- counts copied manually without a source;
- claims of completion without verification evidence;
- historical narrative mixed into active operating instructions;
- repeating the same control contract in every guide;
- using “validated” without stating what was validated.

## Review checklist

- [ ] Purpose and audience are explicit.
- [ ] Normative sources are linked.
- [ ] Commands are current.
- [ ] Examples include outputs or interpretation.
- [ ] Failure and stop behavior is documented.
- [ ] Proof levels are honest.
- [ ] No stale counts or filenames remain.
- [ ] The manual is detailed enough to perform the task without reverse-engineering code.
