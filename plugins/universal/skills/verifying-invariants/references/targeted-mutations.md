# Targeted mutation checks

Use a targeted mutation to answer a narrow question: would this check detect the specific invariant being broken? It is useful when a passing test might be asserting too little or exercising the wrong boundary.

## Procedure

1. Identify the invariant and the check claimed to protect it.
2. In an isolated temporary copy, make one plausible change that reopens the forbidden path: bypass a decoder's validation, expose an unchecked constructor, remove an operation-identity guard, or allow mutation of validated storage.
3. Run the focused check against that copy and capture the failure. Confirm it failed for the intended reason, rather than a syntax error, missing dependency, timeout, or unrelated assertion.
4. Verify that the unmodified control passes under the same settings. Keep the production worktree unchanged and discard only the temporary copy you created.

Never mutate a live deployment, shared environment, or a user's uncommitted work to carry out this procedure. In read-only work, inspect existing mutation results or propose the check instead of making edits. Project-specific mutations belong with the project's tests; this skill does not install a mutation framework.

## Interpret the result

A killed mutation supports sensitivity to that change. A surviving mutation may mean the test misses the path, the assertion is weak, the change is equivalent in the scoped domain, or the mutation failed to alter the intended behavior. Inspect which explanation applies.

If a validation bypass survives because every fixture contains valid data, add a case that enters through that boundary with invalid data when test edits are authorized. Do not count an unrelated failing test as detection. Report “the check missed this mutation,” rather than “the implementation violates the invariant,” unless separate evidence establishes the latter.

Do not maximize a mutation score as a substitute for choosing meaningful obligations. One well-chosen mutation can expose a critical blind spot; a perfect score over an incomplete set says nothing about untested fault classes.
