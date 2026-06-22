# Finding Quality

## Contents

- Evidence gate
- Severity calibration
- Confidence
- Anchoring and deduplication
- Writing effective comments
- Questions versus findings
- Examples

## Evidence Gate

A review comment is a defect finding only when the reviewer can defend all of these:

1. **Location**: The root cause is tied to a specific file and useful line range.
2. **Reachability**: A supported input, state, call sequence, deployment condition, or attacker capability reaches the code.
3. **Violation**: The behavior contradicts a requirement, invariant, established contract, safe platform behavior, or the change's stated intent.
4. **Impact**: The failure produces a concrete consequence: wrong output, crash, data/security loss, compatibility break, hang, leak, or material cost.
5. **Causality**: In a change review, the patch introduces or materially worsens the issue.
6. **No existing prevention**: Callers, validation, types, synchronization, framework behavior, or configuration do not already rule it out.
7. **Actionability**: The author can understand the class of fix without reverse-engineering the reviewer's concern.

When one of these is unknown, investigate it. If it remains unknown and materially affects the claim, ask a question or omit the candidate.

### Evidence patterns by issue type

- **Correctness**: Show the input/state, branch taken, produced value, and expected value.
- **Concurrency**: Name the actors/tasks/threads and the exact interleaving or ownership violation.
- **Security**: Trace source to sink across the trust boundary and state the attacker's required capability.
- **Compatibility**: Identify the old and new producer/consumer, version mix, stored value, request, or configuration that fails.
- **Performance**: Identify the hot path, plausible scale, and complexity, allocation, I/O, query, or network amplification.
- **Resource/lifecycle**: Identify where ownership begins, which exit path skips release/cancellation, and the resulting leak or stale callback.
- **Testing**: Show how the test passes while the implementation is broken, or which claimed behavior is not exercised by any meaningful assertion.
- **Architecture**: Show the concrete consequence of split ownership, inverted dependency, duplicated policy, or incomplete migration. Novelty alone is not a defect.

## Severity Calibration

Severity is based on **impact × likelihood × blast radius**, adjusted for detectability and recoverability.

### P0 — Critical

Use sparingly. Typical properties:

- Exploitable remotely or automatically with little precondition.
- Causes broad outage, irreversible data loss, systemic compromise, or prevents release/build for all users.
- No practical mitigation outside reverting or immediately fixing the change.

### P1 — High

Use when a realistic path can cause severe harm:

- Authorization bypass, sensitive-data exposure, corruption, duplicate financial effects, deadlock, or common-path crash.
- Breaks an externally consumed contract or rolling deployment in a way likely to affect production.
- Failure is difficult to recover from or affects many users.

### P2 — Medium

Use for a definite, plausible defect with contained impact:

- Incorrect edge-case behavior, recoverable resource leak, limited compatibility break, stale state, or meaningful operational blind spot.
- Conditions are less common but supported and realistic.
- A workaround or recovery exists, but merging knowingly still creates product or operational debt.

### P3 — Low

Use only for a real defect with small impact:

- Narrowly scoped incorrect behavior, minor resource waste, or a low-risk contract mismatch.
- Do not use P3 as a container for preferences, cleanup, or style.

### Calibration checks

- Do not raise severity because the fix is hard.
- Do not lower severity because the diff is small.
- Account for existing mitigations, feature flags, rollout percentage, and monitoring.
- A theoretical security primitive is not automatically P1; prove exposure and attacker reachability.
- A crash in an impossible or unsupported state is not a finding.

## Confidence

- **High**: Directly demonstrated by code, tests, a minimal reproduction, or an authoritative contract.
- **Medium**: The code path and impact are strong, but one environment, version, configuration, or caller fact remains unresolved. State it.
- **Low**: Depends on multiple assumptions or uncertain framework behavior. Investigate, ask a question, or omit it.

Do not use a confidence label to launder speculation into a finding.

## Anchoring and Deduplication

- Anchor to the smallest range that explains the defect, usually no more than a few lines.
- Prefer changed lines in change-review mode. If the root cause is unchanged but newly exercised by the patch, anchor the changed integration point and explain the relationship.
- Use one finding per root cause. Mention all affected paths in that finding instead of repeating comments.
- When a defect spans files, anchor the primary cause and cite the other locations in the body.
- Do not anchor a general module-level concern to an arbitrary line.

## Writing Effective Comments

A strong title names the failure and distinguishes it from nearby code:

- Good: `Retries can create duplicate orders`
- Good: `Keep old readers compatible during the schema rollout`
- Weak: `Concurrency issue`
- Weak: `Improve error handling`

A strong body answers four questions in two to five sentences:

1. Under what condition does this occur?
2. What does the code do incorrectly?
3. Why does that matter?
4. What class of change resolves it?

Use direct, neutral language. Avoid praise, rhetorical questions, lectures, broad rewrites, and uncertain words such as “maybe” or “possibly” unless the finding is explicitly medium confidence.

Recommend a repair direction, not a mandatory implementation, unless only one implementation is safe. Keep code snippets minimal.

## Questions Versus Findings

Use a question when intent or an external fact determines whether behavior is wrong:

```markdown
### Question: Is `accountId` guaranteed to be tenant-scoped here?

The query filters only by `accountId`. If IDs are unique only within a tenant, this can return
another tenant's row; if they are globally unique, the current query is sufficient.
```

Questions:

- Stay separate from severity-ranked findings.
- State why the answer matters.
- Do not imply a defect when evidence is incomplete.
- Should be few; investigate locally first.

## Examples

### Unsupported speculation

Bad:

```markdown
### [P1] This may race

Multiple calls could happen at once.
```

Better:

```markdown
### [P1] Serialize the stock check with the decrement
`inventory.ts:44-51` — High confidence

Two requests can both read `stock == 1` before either update commits, then both decrement and
return success. That oversells the final item. Perform the check and decrement atomically in the
database or under the same lock/transaction.
```

### Style disguised as correctness

Bad:

```markdown
### [P3] Replace this loop with `map`

`map` is more idiomatic.
```

Omit it unless the loop has a concrete behavioral or material performance defect.

### Generic missing test

Bad:

```markdown
### [P2] Add tests
```

Better:

```markdown
### [P2] Make the regression test exercise the failure path
`tests/retry.test.ts:28-35` — High confidence

The assertion checks that `send` exists, so it still passes when the retry path never calls it.
Assert the call count and stable idempotency key; otherwise the duplicate-send regression this
change claims to fix is not covered.
```

### No actionable defect

Use:

```markdown
No actionable findings.

Validation: `make test-unit` passed. I did not run integration tests because they require the
external test environment. The review covered the changed service and its direct callers.
```
