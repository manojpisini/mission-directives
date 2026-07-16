# Example: Audit–Fix–Verify Convergence Loop

## Request

Audit the authorization layer, fix confirmed defects, and repeat only when verification exposes a new reachable defect class. Do not keep rerunning the same audit or retrying the same failed patch.

## Route

```text
MD-43 Identity and Access Investigation
→ frozen handoff
→ MD-44 Authorized Execution
→ independent tests and security verification
→ MD-198 decision
```

`MD-197` owns the loop plan, not the security prompt itself.

## Valid second pass

The first patch makes an integration test reachable and reveals a separate session-rotation defect. That is new evidence and a different defect class, so another bounded pass is justified.

## Invalid second pass

The same patch fails for the same reason with identical evidence. The loop must stop or form a materially different hypothesis; it may not repeat blindly.
