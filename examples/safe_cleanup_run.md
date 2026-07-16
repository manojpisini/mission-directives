# Safe Cleanup Example

```text
RUN C-04
MODE APPLY_APPROVED
ROOT {PROJECT_ROOT}
OUTCOME Remove proven unused code and artifacts without behavior change
SCOPE src/, tests/, docs/, package manifests
EXCLUDE vendor/, generated/, data/, release archives
AUTHORITY local repository changes; no deployment
EVIDENCE build graph, symbol references, tests, runtime entry points
CONSTRAINTS one reversible batch at a time
```

Expected route: `MD-00 → MD-01 → MD-03 → MD-04 → MD-02 → MD-10 → MD-31 → MD-32 → MD-35`.
