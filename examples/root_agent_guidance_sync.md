# Example — Root Agent Guidance Synchronization

## Existing repository state

```text
project/
  AGENTS.md      # contains human-authored repository rules
  src/
  tests/
```

## Preview

```bash
python /opt/md/tools/sync_agent_guidance.py \
  --project-root . \
  --suite-root /opt/md \
  --dry-run \
  --show-diff
```

The diff shows one managed section appended to each configured file. No existing lines are removed.

## Apply

```bash
python /opt/md/tools/sync_agent_guidance.py \
  --project-root . \
  --suite-root /opt/md
```

Only the supported files are created when missing:

```text
AGENTS.md
CLAUDE.md
```

Other agent instruction filenames are intentionally excluded.

## Agent use

A user writes:

```text
MD visual assets for six architecture diagrams and verify every SVG
```

The connected agent runs:

```bash
python /opt/md/tools/md.py lookup \
  "visual assets for six architecture diagrams and verify every SVG" \
  --limit 8
```

It then inspects the selected route with `explain`, uses `visual-assets` only after the skill-fit check, applies a finite outer queue of six items, and uses the loop-exit gate for verification and plateau detection.

## Idempotency

Running the synchronization command again reports `unchanged`. It does not append a second managed block.

## Removal

```bash
python /opt/md/tools/sync_agent_guidance.py \
  --project-root . \
  --remove
```

Only the managed block is removed. Existing repository instructions remain.
