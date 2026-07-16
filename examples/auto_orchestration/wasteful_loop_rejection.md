# Example: Wasteful Loop Rejection

## Request

Run the prompt creator repeatedly until it is perfect.

## Result

`MD-197` is rejected because:

- there is no finite work queue;
- “perfect” has no measurable rubric;
- no acceptance threshold is defined;
- repeated execution would not necessarily create new evidence;
- one complete prompt-creation and review pipeline is sufficient.

The router executes once, or invokes `MD-191` to ask for a real quality rubric if iteration would materially change the result.
