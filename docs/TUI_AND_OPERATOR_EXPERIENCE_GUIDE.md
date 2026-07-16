# TUI and Operator Experience Guide

[Back to Mastery Manual](MD_MASTERY_MANUAL.md) · [Manual index](../MANUALS.md)

This guide is the authoritative operational reference for **TUI and Operator Experience Guide** in MD 1.8.3.

## 1. Progress model

Progress model is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 2. Known and unknown totals

Known and unknown totals is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 3. Status and duration

Status and duration is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 4. CI fallback

CI fallback is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 5. NO_COLOR and accessibility

NO_COLOR and accessibility is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 6. Error presentation

Error presentation is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 7. Log links

Log links is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 8. Testing TUI behavior

Testing TUI behavior is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 9. Script integration

Script integration is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.

## 10. Operator conventions

Operator conventions is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

### Required behavior

- Resolve canonical sources before acting.
- Record the selected contract and any exception.
- Use least privilege and deterministic verification.
- Emit telemetry without storing secrets.
- Preserve cross-links, ownership, and review triggers.

### Verification

- [ ] Static structure is valid.
- [ ] Runtime behavior matches the documented contract.
- [ ] Failure behavior is explicit and fail-closed.
- [ ] Cross-platform or cross-format parity is checked where applicable.
- [ ] Residual unknowns are visible.
## Project installer lifecycle

The root installer uses the shared TUI on stderr and keeps its JSON result on stdout. Its progress stages are project validation, source verification, staging, promotion, project-file integration, runtime-directory creation, agent-guidance synchronization, receipt creation, and telemetry recording. A dry run completes after validation and preview preparation without changing project files.

Successful and failed runs both terminate with an explicit outcome panel. Failures return a nonzero exit code and include the bounded reason without an uncontrolled traceback. The PowerShell launcher mirrors the outcome with parse-safe `[SUCCESS]` or `[FAILURE]` status text.


## Cleanup TUI

`cleanup.py` uses a ten-stage progress model covering validation, discovery, preview binding, locking, approval verification, managed-text cleanup, quarantine, result verification, purge, and final summary. Interactive terminals receive a live bar; `--no-tui`, CI, and redirected output receive deterministic `PROGRESS n/10` lines. Panels distinguish explicit user decline, Ctrl-C interruption, rollback-safe failure, successful cleanup, and purge-incomplete recovery. A purge-incomplete panel reports the residual quarantine path and never claims that a partially deleted tree was restored.
