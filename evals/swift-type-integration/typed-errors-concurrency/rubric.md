<!-- rubric-id: swift-type-typed-errors-concurrency-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Selects a closed error boundary only when callers need it, and describes a concrete loss-of-precision counterexample such as erasing a parse failure to `any Error` across a task boundary.
- Preserves cancellation deliberately: it must not silently map cancellation into a domain import failure. It accounts for the async task's ownership, observation, and error transport.
- Explains that a typed failure channel does not prove which input caused a case, that work completed, or that cancellation was observed.
- Shows a successful focused local load of `references/ownership-effect-recipes.md` at typed errors. Loading `references/ownership-concurrency-errors.md` is warranted only when the selected typed-throws or cancellation boundary needs its specific guidance.
- Proposes an exact-family success/failure test plus a cancellation scenario, and qualifies compiler or runtime evidence honestly.
- Leaves the workspace unchanged.
