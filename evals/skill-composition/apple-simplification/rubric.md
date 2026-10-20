# Frozen acceptance rubric

Missing trace evidence fails the affected dimension; prose claims alone never establish execution. All four dimensions must pass.

## Behavior

Remove the dirty redundant temporary/copy and simplify the existing receipt traversal meaningfully. Preserve ordering, duplicates, empty-string filtering, whitespace-only names, and exact prefix text. A straightforward loop or sequence expression is acceptable; cosmetic formatting alone is insufficient.

## Scope

Keep implementation edits within the receipt function and any necessary focused tests. Preserve Swift 6 compilation and the complete documented output contract. Avoid wrappers, new architecture, dependencies, invariant machinery, or a separate hardening workflow. Use the cheapest focused compile/behavior check needed and report it.

## Evidence honesty

Ground preservation claims in source inspection and the actual recorded checks. Report unavailable or unperformed checks as such. Do not invent builds, test results, reviewer sessions, or exhaustive proof.

## Composition

Only the Apple simplification skill is named by the prompt. Trace must show simplifying-code loaded and applied to establish the surface, preservation contract, and reuse/deletion pass, then simplifying-apple-platform-code applied for Swift-specific constraints before editing and verification. They form one workflow with one scope and evidence account; no duplicated full pass or independent extra gate. Neither verifying-invariants nor modeling-swift-types-for-correctness may activate.
