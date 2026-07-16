# Prompt Addition and Registration Guide

**Purpose:** Add one new prompt to Mission Directives from a Markdown source file without manually editing every catalog, graph, fixture, routing table, or integrity receipt.  
**Canonical implementations:** `tools/add_prompt.py`, `tools/add-prompt.sh`, and `tools/add-prompt.ps1`  
**Agentic equivalent:** `MD-199` — Prompt Addition, Registration, and Ecosystem Integration

## 1. What this workflow does

Prompt addition is a suite mutation, not a file-copy operation. A valid addition must create a permanent prompt identity, preserve the imported prompt's intent, satisfy the canonical prompt-body contract, and update every source of truth that makes the prompt discoverable, routable, testable, and verifiable.

The script performs the following transaction:

1. validates the source Markdown as a bounded, regular, UTF-8, non-symlink file;
2. validates the requested title, category, role, prompt type, risk, modes, prompt references, templates, skills, and department packs;
3. allocates the integer immediately after the highest canonical prompt sequence;
4. derives the permanent `MD-###` ID, slug, filename, capability ID, canonical output paths, and frontmatter;
5. preserves the source prompt under `<source_prompt>` inside a canonical Mission Directives wrapper;
6. creates healthy, problematic, and adversarial prompt fixtures;
7. adds the atomic scenario and atomic contract fixture;
8. updates template reverse routes and registered skill prompt routes;
9. creates explicit unresolved crosswalk records rather than fabricating agent or prompt-type matches;
10. optionally adds the prompt to explicitly selected department packs;
11. regenerates catalog, identity, graph, body-audit, schema-fixture, evaluation, validation, and integrity artifacts;
12. runs the full deterministic test suite by default;
13. compares the verified staging tree with the unchanged live suite under an exclusive promotion lock;
14. atomically promotes only changed and new files;
15. requires an exact approval token bound to the current preview, source digest, and catalog before mutation;
16. restores the original bytes and modes if promotion fails;
17. emits a structured receipt and telemetry event.

## 2. Choosing script versus `MD-199`

Use the script when the source prompt and required metadata are already known and a deterministic local mutation is desired. Use `MD-199` when an agent must first investigate overlap, refine the source prompt, decide whether a distinct capability is justified, or help identify templates, skills, references, risk, modes, and department-pack placement.

Both paths enforce the same identity and ecosystem rules. `MD-199` must not bypass the script's validation, and the script must not invent semantic decisions that require human or agent review.

## 3. Basic invocation

### Linux and macOS

```bash
./tools/add-prompt.sh \
  --source ./candidate-prompt.md \
  --title "Dependency Upgrade Evidence Review"
```

### Windows PowerShell

```powershell
.\tools\add-prompt.ps1 `
  --source .\candidate-prompt.md `
  --title "Dependency Upgrade Evidence Review"
```

### Direct Python

```bash
python tools/add_prompt.py \
  --source ./candidate-prompt.md \
  --title "Dependency Upgrade Evidence Review"
```

### Unified MD CLI

```bash
python tools/md.py add-prompt \
  --source ./candidate-prompt.md \
  --title "Dependency Upgrade Evidence Review"
```

### OS-aware dispatcher

```bash
python tools/platform_dispatch.py add-prompt --source ./candidate-prompt.md --title "Dependency Upgrade Evidence Review"
```

When `--source` or `--title` is omitted in an interactive terminal, the script asks for it. Non-interactive runs must provide both explicitly.


## 4. Review-bound approval

Run `--dry-run` first. The preview is validated by `schemas/prompt_addition_preview.schema.json` and includes the complete proposed identity, routing, output contract, source digest, current catalog digest, and `approval_token`. A non-interactive mutation must pass that exact token:

```bash
python tools/add_prompt.py --source ./candidate-prompt.md --title "Dependency Upgrade Evidence Review" --dry-run
python tools/add_prompt.py --source ./candidate-prompt.md --title "Dependency Upgrade Evidence Review" --approval-token <TOKEN>
```

Changing the source, title, metadata, selected routes, suite version, or catalog invalidates the token. In an interactive terminal, omitting `--approval-token` displays the current preview and asks for explicit confirmation; the confirmed preview is then bound automatically. Approval is never inferred from merely running the command.

After the complete suite is copied to staging, the importer recomputes the normalized `PreparedPrompt` from the immutable source snapshot and staged catalog. That staged contract must be exactly equal to the approved contract before any prompt or fixture is written. A different ID, sequence, filename, route, template, skill, output contract, digest, or normalized body fails closed with `suite state changed since approval`; the operator must run a new dry run and approve the newly issued token. The receipt is therefore derived only from a contract proven identical to the promoted contract.

## 5. Metadata options

```text
--category <safe-category>
--role operational|investigative|gate|control
--prompt-type <safe-type>
--risk low|medium|high|critical
--mode <MODE>                         repeatable
--related MD-###                      repeatable
--requires MD-###                     repeatable
--skill <registered-skill-id>         repeatable
--template <registered-template-id>   repeatable
--conditional-template <template-id>  repeatable
--department-pack <PACK_ID>           repeatable
--dry-run
--approval-token <TOKEN_FROM_DRY_RUN>
--skip-full-tests
```

`--skip-full-tests` is a maintainer-only acceleration for local structural work. It does not provide the same proof as the default path and must not be used to claim a release-ready addition. Release sealing must run the full suite afterward.

## 6. Identity rules

The allocator reads the release-consistent `catalog.json`, cross-checks its count and canonical paths against `prompts/`, and computes:

```text
sequence      = highest existing sequence + 1
prompt_id     = MD-<sequence>
slug          = lowercase ASCII kebab case derived from title
filename      = <zero-padded sequence>_<UPPER_SNAKE_TITLE>.md
capability_id = md.<category>.<slug>
```

Identifiers are permanent. The tool does not fill historical gaps, reuse deleted IDs, renumber prompts, or create aliases automatically. A collision is a hard failure.

## 7. Source normalization

A raw Markdown source is captured once, newline-normalized, SHA-256 hashed, and placed under `<source_prompt format="markdown" encoding="xml-escaped">`. XML-significant characters are escaped so source text cannot close the quarantine block or inject canonical control sections. The hash and byte length are recorded in prompt frontmatter and the mutation receipt. Existing YAML frontmatter is removed because the script creates authoritative suite frontmatter. The wrapper adds the standard identity, mission, evidence, authorization, tool, template, marker, skill, method, quality, output, stop, and completion contracts.

This strategy preserves task-specific intent while ensuring every imported prompt remains compatible with the suite runtime. The source remains untrusted input and cannot override `MD-00`, `MD-01`, `MD-02`, `MD-03`, or `MD-04`.

## 8. Skills

A skill may be added through `--skill` only when its exact ID exists in `skill_registry.json`. The script also detects slash-prefixed references such as `/visual-assets` when they match a registered skill.

Prompt addition does not install, approve, or execute a skill. It only records a preferred route and adds the prompt ID to that skill's `prompt_routes`. Unknown skills fail closed. Use `MD-193` through `MD-195` and the governed acquisition tools for missing skills.

## 9. Templates

Every new prompt receives the three core required templates by default:

- `core/run-manifest`
- `core/evidence-register`
- `core/verification-record`

The default conditional templates are:

- `core/decision-record`
- `core/artifact-specification`
- `core/acceptance-criteria`

Exact template IDs are validated against `template_registry.json`. Reverse routing lists are updated so template coverage remains complete. Unknown template IDs are rejected rather than substituted.

## 10. Pair safety

The generic script creates one unpaired prompt. It rejects `executive`, `paired_execution`, and `paired_investigation` classifications because those require an exact reciprocal twin; it never silently creates an investigative/executive pair. Pair creation requires two deliberately authored prompts with reciprocal `paired_prompt_id` values, distinct planning and execution responsibilities, user plan review, re-freezing after revisions, separate execution consent, and exact-twin runtime enforcement.

Use the pair-authoring workflow and guide when a true pair is required. Do not use the generic script twice and manually approximate a pair without pair validation.

## 11. Staging and promotion

The live suite is snapshotted before staging. Runtime logs, caches, and advisory lock files are excluded from canonical diff accounting. The staging copy is fully regenerated and validated. Promotion acquires `.prompt_suite/prompt-addition.lock`, rechecks the live snapshot for concurrent modification, and writes each changed file atomically.

Expected additions are allowed. Unexpected deletions are prohibited. If a write fails, every previously written path is restored from its original bytes and mode, and newly created paths are removed.

The expensive proof run does not hold the promotion lock. This avoids blocking unrelated readers while still preventing a stale staged tree from overwriting a concurrently changed suite.

## 12. Generated and updated surfaces

A normal prompt addition can update:

- `prompts/<canonical-file>.md`
- `catalog.json`
- `PROMPT_CATALOG.md`
- `compatibility/capability_identity_registry.json`
- `capability_graph.json`
- `SCENARIO_CATALOG.json`
- `template_registry.json`
- `integrations/template_to_prompt_crosswalk.json`
- `category_taxonomy.json`
- `skill_registry.json`
- `department_packs.json` when explicitly requested
- both integration crosswalks
- `evaluations/prompts/MD-###/{healthy,problematic,adversarial}.json`
- `evaluations/atomic_contract_fixtures.json`
- schema contract fixtures when schemas changed
- `BODY_QUALITY_AUDIT.json` and `.md`
- `EVALUATION_STATUS.json`
- `TEST_RESULTS.json` when full tests run
- `VALIDATION.json`
- `MANIFEST.json`

The exact list is returned in `changed_files`. A schema-valid receipt is also written to `.prompt_suite/results/prompt-addition/MD-###-<nonce>.json`; this runtime surface is intentionally excluded from the release manifest.

## 13. Failure behavior

The script returns exit code `2` with a structured error for invalid user input or a failed staged proof. It must not leave a partial prompt, fixture directory, catalog entry, route, or manifest update in the live suite.

Common failures include:

- source is missing, oversized, not UTF-8, not Markdown, or symlinked;
- title cannot produce a safe slug or filename;
- prompt, skill, template, mode, or department-pack reference is unknown;
- an operational or executive prompt omits `DRAFT_ONLY`;
- body quality, template coverage, scenario coverage, evaluation coverage, tests, generated reproducibility, links, release consistency, or manifest validation fails;
- the live suite changes while staging is underway;
- a destination cannot be written atomically.

## 14. Review checklist

After success, review:

1. the canonical prompt file and preserved source body;
2. the assigned ID, slug, category, role, modes, risk, and output paths;
3. related and required prompt references;
4. selected template routes;
5. preferred skill routes;
6. department-pack placement;
7. unresolved crosswalk placeholders;
8. healthy, problematic, and adversarial fixtures;
9. the final test, evaluation, validation, and manifest receipts.

A passing deterministic suite proves structural and runtime-contract integration. It does not by itself prove live model quality. Promote a real run through the existing evaluation workflow before making behavioral quality claims.
