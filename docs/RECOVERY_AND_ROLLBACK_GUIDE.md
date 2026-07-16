# Recovery and Rollback Guide

## Purpose

Recovery is a designed and verified capability, not a sentence in an action plan. This guide explains how consequential runs prepare, exercise, select, and verify rollback, roll-forward, containment, or restoration.

## Recovery vocabulary

- **Rollback:** return to a previous known-good state.
- **Roll-forward:** complete or repair the transition to a new good state.
- **Restore:** recover data or systems from backup or replica.
- **Containment:** limit impact while investigation continues.
- **Compensation:** apply an inverse business operation when technical rollback is impossible.
- **Residual:** known unresolved impact or uncertainty remaining after recovery.

## Pre-execution recovery contract

Before `APPLY_APPROVED`, record:

- recovery unit;
- baseline state and hash;
- backup or reverse operation;
- responsible operator;
- maximum acceptable data loss;
- recovery-time target;
- validation commands;
- monitoring views;
- decision authority;
- stop thresholds;
- communication route.

A rollback command that has not been rehearsed is a proposal, not proof.

## Recovery selection

Choose the response based on evidence.

### Rollback when

- the prior state remains compatible;
- partial effects can be reversed safely;
- no irreversible downstream consumer depends on the new state;
- data loss is within approved limits.

### Roll-forward when

- backward compatibility is no longer available;
- rollback would corrupt data or violate contracts;
- the remaining repair is smaller and safer than reversal;
- the new state can be verified quickly.

### Contain when

- the failure mechanism is unknown;
- action could destroy evidence;
- neither rollback nor roll-forward is safe;
- affected traffic or features can be isolated.

### Restore when

- current data or state is corrupted;
- backup integrity and recovery point are verified;
- restore procedures are rehearsed.

## Failure path

```text
executing
→ failed
→ rolled_back or containment
→ investigation reopened if assumptions changed
→ verification_pending
→ verified or residual_open
→ closed only after authorized resolution
```

Partial success never becomes full completion silently.

## Drill procedure

1. Use an isolated environment and synthetic or approved data.
2. Bind the drill to an evidence snapshot.
3. Record the initial state.
4. Execute the exact test batch.
5. Inject a controlled failure.
6. Measure detection and stop time.
7. Perform rollback, roll-forward, containment, or restore.
8. Verify system state and data independently.
9. Record damage, uncertainty, and residuals.
10. Update runbooks and actions.

## Evidence package

A complete recovery package includes:

- baseline evidence;
- recovery artifact or command;
- exact operator and time;
- logs;
- restored or resulting state;
- data reconciliation;
- smoke, integration, and domain checks;
- rollback duration;
- unmet objectives;
- residual owner and expiry.

## Marker use

```text
@EVIDENCE:rollback-01 pre-change database checksum
+ACTION:rollback-01 restore snapshot and replay approved events
=VERIFY:rollback-01 row counts, checksums, and application reads reconcile
?UNKNOWN:rollback-02 downstream cache invalidation status
!STOP:restore-integrity-unverified
```

## Residual-risk acceptance

Residual acceptance is an authorized human decision. It records:

- remaining risk;
- impact and likelihood;
- affected users or systems;
- compensating controls;
- owner;
- expiry;
- review trigger;
- reason closure is acceptable.

## Common failures

- rollback script references the wrong environment;
- backup exists but cannot be restored;
- schema is backward-incompatible;
- partial external side effects cannot be reversed;
- verification checks only process status, not data;
- operator closes after rollback without reopening changed assumptions;
- failure evidence is overwritten during retry.

## Validation

The evaluation suite includes a failed-execution → rollback → residual-open drill. High-risk live systems still require environment-specific rehearsal.
