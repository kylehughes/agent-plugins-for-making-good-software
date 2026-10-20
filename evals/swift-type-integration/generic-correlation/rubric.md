<!-- rubric-id: swift-type-generic-correlation-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Selects a closed associated-family or indexed-expression representation when it meets the need, and reserves equality-witness/GADT-style machinery for the case where one indexed form is materially necessary.
- Gives a concrete rejected counterexample, such as constructing a text literal as an expression promised to yield a boolean, and identifies construction, erasure, or public witness issuance as the boundaries to audit.
- Does not mistake the type relation for a proof of evaluator semantics, termination, optimizer correctness, or external data validity.
- Shows a successful focused local load of `references/generic-proof-recipes.md` at equality witnesses/finite indexed expressions. Loading `references/advanced-generics-and-protocols.md` is warranted only when the selected abstraction needs its specific guidance.
- Proposes a positive evaluator example and a misuse compilation control where the selected API can express it, while stating the control's exact limit and never claiming an unrun compiler result.
- Leaves the workspace unchanged.
