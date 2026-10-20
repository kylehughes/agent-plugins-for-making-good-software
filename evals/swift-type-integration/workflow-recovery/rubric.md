<!-- rubric-id: swift-type-workflow-recovery-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Chooses a lightest adequate state representation: separate phases or a state-indexed wrapper only if the shared storage warrants it, with a result that carries either a submitted receipt or the still-usable draft on recoverable verification failure.
- Names concrete rejected misuses, including submitting the same local authority twice and losing the draft after a recoverable failure. A bare boolean state flag or an optional result with no recovery path is insufficient.
- Explains that consuming local authority does not establish eventual submission, remote idempotency, cancellation behavior, or crash recovery; those remain runtime and service obligations.
- Shows a successful focused local load of `references/domain-modeling-recipes.md` at the workflow/recovery section, with advice grounded in that section. Loading completion/ownership guidance is warranted only if the chosen design uses those facilities.
- Offers focused evidence: a valid transition, a compile-time misuse control where the chosen representation supports one, and a runtime recovery/cancellation scenario. It labels each proof limit honestly and does not invent execution.
- Leaves the workspace unchanged.
