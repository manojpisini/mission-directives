# Stale handoff refusal example

An executive prompt receives a frozen action plan tied to an older commit. The repository and dependency lock changed after the snapshot. The executor flags the stale handoff, refuses mutation, records the invalidation trigger, and routes back to investigation. It does not reinterpret the old plan as current approval.
