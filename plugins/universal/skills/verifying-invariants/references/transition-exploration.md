# Transition exploration

Types can constrain individual values without proving that a sequence of operations preserves a contract. State the initial states, enabled actions, transition relation, and invariant before selecting transition evidence.

## Start with the actual implementation

Prefer exercising a production reducer or transition function. If a separate model is necessary, document how model states and actions map to production, which behavior is abstracted away, and what checks detect divergence. A model passing by itself does not establish implementation correctness.

For asynchronous work, include operation identity, cancellation, replacement, completion, and delivery order when they affect the invariant. A stale completion can be legal for its original operation yet illegal for the current one. Actor or lock isolation alone does not establish that logical ordering property.

Deterministic tests should control readiness and completion through explicit synchronization. The relevant testing companion owns those primitives. Fixed sleeps and lucky scheduling are not evidence of exploring the relevant orders.

## Finite exploration

A small breadth-first or depth-first traversal may be enough:

```text
frontier = initial states
seen = empty set
while frontier is not empty:
    state = take one
    if state was seen: continue
    assert invariant(state)
    remember state
    for each enabled action and modeled environment outcome:
        successor = transition(state, action, outcome)
        record enough history to reproduce a counterexample
        add successor to frontier
```

This is exhaustive only over the specified reachable model when traversal finishes without truncation and state equality preserves every distinction relevant to the property. A depth cutoff, state cap, timeout, partial action list, or bounded input domain limits the claim. Record each bound explicitly, including queue sizes, retries, operation counts, numeric domains, and environment outcomes as applicable.

Distinguish a **complete traversal of a finite model** from a **bounded prefix**. Record visited states/transitions and whether the frontier was exhausted or truncated. Reaching a resource budget is an incomplete run, even if no counterexample was found. Do not silently discard states to fit a budget.

## Test the transition contract

Check both permitted transitions and rejected actions. Include overlapping operations, duplicate completions, cancellation before and after readiness, and stale completions only when those events are possible in the scoped system. Derive expected behavior from the contract, not by calling the same implementation twice.

Safety means the forbidden state is never reached. Liveness means progress eventually occurs; it requires its own scheduling, fairness, and environmental assumptions. A finite run without failure cannot establish eventual progress for all executions.

## When a dedicated model checker helps

Consider one when state-space size, temporal properties, or interleavings exceed what a small project-owned traversal can explain and maintain. Specify the model, bounds, fairness assumptions, trusted tooling, and implementation correspondence before proposing adoption. Do not install or introduce a proof engine as a side effect of an ordinary review.

For an example of an explicit-state checker and its configuration, consult the [TLC documentation](https://docs.tlapl.us/using:tlc:start) and [model configuration reference](https://docs.tlapl.us/using:tlc:config_file). Select tools according to the project; this skill does not depend on TLC.
