# Bounded Loop Orchestration Guide

## Purpose

`MD-197` can loop **any prompt, scenario, or exact skill**. The target is generic. The eligibility test—not the domain—decides whether looping is useful.

The loop exists for two distinct forms of repeated work:

1. **Outer work loop:** process a finite queue of assets, files, findings, records, test cases, locales, sections, or other independent items.
2. **Inner quality loop:** refine the current item while objective evidence shows that another pass can improve it.

Either layer may be used alone. A batch of twelve already-acceptable one-pass assets uses twelve outer iterations and one inner iteration each. A single complex diagram may use one outer item and up to three inner refinement passes. The limits are separate so queue size is not confused with quality retry count.

## Eligibility test

A loop is eligible only when all required conditions are true:

- there is a finite queue with more than one item **or** a measurable refinement objective;
- desired output and desired result are explicitly defined;
- progress can be measured or independently verified;
- each pass can produce new evidence, state, or a changed hypothesis;
- iteration, token, time, cost, and tool budgets are bounded;
- writes are serialized or isolated;
- rollback or last-known-good preservation is possible for mutations;
- repeated external effects are excluded;
- expected value exceeds loop cost and risk.

## Ineligible cases

Reject the loop when:

- one complete pass can satisfy the result;
- “keep improving until satisfied” has no rubric or threshold;
- the same failed invocation would be retried with unchanged evidence;
- the producer would repeatedly publish, send, deploy, delete, pay, or perform another irreversible effect;
- the acceptance threshold changes to make a weak result pass;
- iterations cannot be compared;
- the quality measure encourages cosmetic overfitting rather than useful improvement;
- cost or latency exceeds the likely gain.

## Loop plan

A loop plan should contain:

```yaml
loop_target:
  kind: prompt | scenario | skill
  id:
mode: batch | refinement | audit_fix_verify | mixed
work_queue: []
desired_output:
desired_result:
quality_rubric: []
progress_metric:
acceptance_threshold:
verification_method:
budgets:
  maximum_outer_iterations:
  maximum_inner_iterations:
  maximum_no_improvement:
  token_limit:
  time_limit:
  cost_limit:
  tool_call_limit:
concurrency:
  single_writer_rule:
  isolated_parallel_groups: []
rollback:
exit_precedence: []
```

Maximum limits are ceilings. The loop must stop before them when success, plateau, safety, or authority conditions require it.

## Iteration record

Each pass records:

- loop and iteration IDs;
- queue item or refinement target;
- input references and hashes;
- hypothesis or defect class addressed;
- `+ACTION:{id}`;
- output artifacts and lineage;
- score, verification result, and delta;
- new evidence;
- warnings and failures;
- budget consumed and remaining;
- residuals;
- `MD-198` decision.

A pass with no new evidence, changed input, changed hypothesis, or processed queue item is normally not a valid iteration.

## Exit precedence

`MD-198` applies this order:

1. **hard safety or authority stop**;
2. **desired result independently verified**;
3. **queue exhausted with accepted or explicitly residualized items**;
4. **quality plateau or repeated unchanged failure**;
5. **budget or iteration limit**;
6. **human stop or escalation**.

This order prevents a quality score from overriding safety and prevents maximum-iteration chasing after success.

Possible decisions:

```text
continue
complete
plateau_stop
budget_stop
safety_stop
rollback
human_escalation
```

## Batch example: visual assets

Suppose the queue contains twelve vector assets:

```text
01-market-map.svg
02-value-chain.svg
03-risk-matrix.svg
...
12-summary-illustration.svg
```

The outer loop:

1. selects one asset brief;
2. invokes `MD-196` with `visual-assets`;
3. quarantines output;
4. verifies source accuracy, communication purpose, composition, editability, accessibility, and export;
5. invokes `MD-198`;
6. marks the item accepted or residual;
7. advances to the next item.

An inner loop is added only when the current asset fails a measurable criterion and another targeted pass has a concrete hypothesis. It does not clone one template across the queue merely for efficiency.

CLI planning example:

```bash
python tools/md.py auto-plan MD-104 \
  --skill-id visual-assets \
  --skill-required \
  --loop \
  --work-items 12 \
  --measurable
```

## Audit–fix–verify convergence loop

The target may be any audit and remediation route, for example:

```text
MD-29 debugging investigation
→ MD-30 bounded fix
→ independent verification
→ MD-198
```

A new pass is justified when:

- the prior fix exposes a different reachable defect;
- verification reveals a new causal path;
- a previously blocked test becomes executable;
- the remaining risk class is different and in scope.

A new pass is **not** justified when the same failed fix would be retried unchanged. After repeated unsuccessful hypotheses, stop and question the architecture or escalate rather than thrash.

## External effects

Loops may produce local drafts, patches, previews, test runs, and dry-run manifests. They may not repeatedly:

- publish;
- send messages;
- deploy;
- merge;
- transfer funds;
- delete records;
- submit filings;
- create real accounts;
- contact targets.

The loop prepares and verifies the final consequential batch. The external effect occurs once after the appropriate approval gate.

## Concurrency

Parallel execution is allowed only when work items are isolated and do not write the same source of truth. Use:

- separate output paths;
- immutable source snapshots;
- independent branches or worktrees where relevant;
- one authoritative fan-in stage;
- deterministic conflict resolution.

Do not let parallel workers silently update the same manuscript, deck, code file, design token set, or registry.

## Plateau examples

### Quantitative

Target score: `0.90`; minimum meaningful delta: `0.01`; maximum no-improvement passes: `2`.

```text
0.700 → 0.705 → 0.710
```

Both recent deltas are below `0.01`, so the correct decision is `plateau_stop`, not another blind pass.

### Qualitative

A reviewer rubric has five independent criteria. Two consecutive passes change wording but do not resolve the failed evidence and accessibility criteria. The loop plateaus even if the producer describes the output as “more polished.”

## CLI exit examples

Plateau:

```bash
python tools/md.py loop-decision \
  --iteration 3 \
  --current-score 0.71 \
  --target-score 0.90 \
  --previous-scores 0.70,0.705 \
  --max-iterations 5 \
  --max-no-improvement 2 \
  --minimum-delta 0.01
```

Verified completion:

```bash
python tools/md.py loop-decision \
  --iteration 2 \
  --current-score 0.95 \
  --target-score 0.90 \
  --previous-scores 0.80 \
  --verified \
  --queue-remaining 0
```

## Anti-patterns

- treating `max_iterations` as a target;
- self-scoring without independent evidence;
- changing several unrelated variables per pass;
- losing the last verified artifact;
- retrying after authority expires;
- hiding unprocessed queue items;
- declaring completion because the queue is empty when items failed;
- allowing a reviewer to edit the artifact it judges at high risk;
- using a loop to compensate for unclear intent or a missing prerequisite.
