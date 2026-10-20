<!-- rubric-id: swift-type-static-dimensions-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Uses a static dimension relationship only for literal/API-known shapes when supported by the selected toolchain, and a checked runtime construction path for decoded dimensions. It identifies an incompatible inner dimension such as 4 versus 5 as a counterexample.
- Keeps the representation proportional: a checked array/domain wrapper is acceptable when compiler feature availability, diagnostic cost, or public signature complexity outweigh static dimensions.
- Separates shape compatibility from arithmetic correctness, dynamic-index bounds, layout, and decoded-input validation.
- Shows a successful focused local load of `references/generic-proof-recipes.md` at static sizes. Loading `references/swift-feature-status.md` is required only if the answer recommends feature-sensitive spelling or another newer facility.
- Requests a same-settings valid compilation control and incompatible-shape compilation control, plus runtime construction and numeric-result tests; it gives their limits honestly.
- Leaves the workspace unchanged.
