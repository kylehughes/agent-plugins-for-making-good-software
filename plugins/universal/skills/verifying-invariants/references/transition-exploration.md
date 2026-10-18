# Transition exploration

Types can constrain individual values without proving that a sequence of operations preserves a contract. State the initial states, enabled actions, transition relation, and invariant before selecting transition evidence.

## Start with the actual implementation

Prefer exercising a production reducer or transition function. If a separate model is necessary, document how model states and actions map to production, which behavior is abstracted away, and what checks detect divergence. A model passing by itself does not establish implementation correctness.

For asynchronous work, include operation identity, cancellation, replacement, completion, and delivery order when they affect the invariant. A stale completion can be legal for its original operation yet illegal for the current one. Actor or lock isolation alone does not establish that logical ordering property.

Deterministic tests should control readiness and completion through explicit synchronization. Releasing a dependency permits its consumer to resume; it does not establish that the consumer has completed its state update. Await the operation's completion or a defined acknowledgement that covers the update before observing it. Fixed sleeps, yields, or a chosen number of event-loop turns are not completion acknowledgements, even when the current implementation happens to finish within them. The relevant testing companion owns the synchronization primitives.

The proposed check must reach its observation point and terminate on both success and failure. For a partial-completion claim, observe the state after the selected completion while the other operation is still pending; waiting for all operations first cannot establish that claim. Then release or cancel outstanding work and observe its termination during cleanup. Bound failure waits, and distinguish the observation that tests the invariant from the cleanup that makes the check finish.

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

Define the expected state after each action, including partial completion. For example, if only the most recently started refresh may update a display, the oracle tracks the newest **started** operation independently of the completed operations:

| Action | Current operation | Expected display |
| --- | --- | --- |
| Start A | A | Previous value |
| Start B | B | Previous value |
| Complete A while B is pending | B | Previous value |
| Complete B | B | B's result |

Taking the highest-numbered completed operation would incorrectly allow A's result in the third row. Check the oracle itself against the contract before using it for enumeration; a correct final state can hide an invalid intermediate state. A concrete counterexample usually needs one regression and a valid control. Propose broader exploration only when it answers an additional scoped obligation, with its oracle and bounds stated.

Safety means the forbidden state is never reached. Liveness means progress eventually occurs; it requires its own scheduling, fairness, and environmental assumptions. A finite run without failure cannot establish eventual progress for all executions.

## When a dedicated model checker helps

Consider one when state-space size, temporal properties, or interleavings exceed what a small project-owned traversal can explain and maintain. Specify the model, bounds, fairness assumptions, trusted tooling, and implementation correspondence before proposing adoption. Do not install or introduce a proof engine as a side effect of an ordinary review.

For an example of an explicit-state checker and its configuration, consult the [TLC documentation](https://docs.tlapl.us/using:tlc:start) and [model configuration reference](https://docs.tlapl.us/using:tlc:config_file). Select tools according to the project; this skill does not depend on TLC.
