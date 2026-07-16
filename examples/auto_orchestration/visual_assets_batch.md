# Example: Visual Asset Batch Through a Generic Skill Loop

## Request

Create twelve deliberate vector graphics and editorial illustrations for a research report. Use `/visual-assets`. Every asset must be editable SVG or HTML/SVG, traceable to the report's claims, accessible, and visually distinct. Stop refining an asset once it passes; do not consume a fixed number of passes.

## Compiled route

```text
MD-00 → MD-01 → MD-03 → MD-04
→ MD-104 Infographic and Data Storytelling Production
→ MD-192 Skill Requirement and Capability Fit
→ MD-196 Generic Conditional Skill Execution (`visual-assets`)
→ MD-197 Bounded Prompt and Skill Loop
→ MD-198 Loop Exit Gate after every pass
→ MD-109 Visual Quality Review
→ MD-02 closure
```

## Loop contract

```yaml
mode: batch
work_queue_count: 12
maximum_outer_iterations: 12
maximum_inner_iterations: 3
maximum_no_improvement: 1
desired_result: all accepted assets satisfy their individual communication jobs
progress_metric: passed rubric criteria per asset
external_effects: none
single_writer: one source asset at a time
```

## Exit behavior

- An asset exits immediately when independently verified.
- A failed measurable criterion permits one targeted refinement hypothesis.
- Unchanged failure causes `plateau_stop` and a residual record.
- The batch completes only when every item is accepted or explicitly residualized.
