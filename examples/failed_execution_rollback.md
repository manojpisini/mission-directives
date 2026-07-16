# Failed execution, rollback, and residual example

A migration enters `executing`, fails a post-write invariant, and transitions to `failed`. The operator records partial effects, invokes the approved rollback, transitions to `rolled_back`, and independently verifies restored data. A timing uncertainty remains, so the run moves through reinvestigation and ends in `residual_open` until an authorized owner accepts or resolves it. Command success alone never closes the run.
