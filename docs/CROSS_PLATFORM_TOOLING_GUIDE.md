# Cross-Platform Tooling Guide

[Back to Mastery Manual](MD_MASTERY_MANUAL.md) · [Manual index](../MANUALS.md)

This guide is the authoritative operational reference for **Cross-Platform Tooling Guide** in MD 1.8.3.

## 1. Canonical Python layer

Canonical Python layer is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 2. Bash and PowerShell parity

Bash and PowerShell parity is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 3. Platform dispatch

Platform dispatch is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 4. Arguments and exit codes

Arguments and exit codes is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 5. Receipts and logging

Receipts and logging is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 6. Safety and non-interactive operation

Safety and non-interactive operation is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 7. Testing parity

Testing parity is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 8. Adding a tool pair

Adding a tool pair is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 9. Windows notes

Windows notes is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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

## 10. Linux and macOS notes

Linux and macOS notes is governed by explicit machine-readable policies and validated artifacts. Operators must preserve evidence, authority, compatibility, deterministic exit behavior, and honest limitations.

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


## Portable skill destinations

Resolve `.agents`, Claude Code, and OpenCode global locations through `tools/agent_paths.py`; do not embed usernames or absolute home directories in canonical artifacts.

## Project cleanup entry points

The cleanup workflow uses the same Python-core and shell-wrapper model as installation:

```text
cleanup.py     canonical transactional implementation
cleanup.sh     Linux/macOS launcher
cleanup.ps1    Windows PowerShell launcher
```

The platform dispatcher exposes it as:

```bash
python tools/platform_dispatch.py cleanup-project -- /path/to/project --dry-run
```

The Python implementation owns validation, approval binding, quarantine, rollback, TUI output, and the final summary. Shell wrappers perform only interpreter discovery, argument forwarding, status rendering, and exit-code propagation.
