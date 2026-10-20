<!-- rubric-id: swift-type-decoding-main-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Identifies restored keyed data as a construction route that can bypass the checked initializer, and supplies a concrete keyed payload such as `{"percent":0}` that reaches the predicate.
- Selects a representation and boundary repair that preserves the existing keyed wire shape and routes restored values through the same range check. A scalar decoder or a solution that only changes the initializer fails.
- Calls out the distinct controls: a fixed valid historical payload, predicate-reaching invalid values at both bounds, and a current encode/decode round trip.
- Shows a successful local load of the focused `references/algebraic-and-refined-values.md` Codable/refined-value guidance in the trace; the response uses its decoder-boundary guidance rather than merely naming it. Loading interop guidance is warranted only if the answer selects an interop boundary.
- States that runtime checks support this decoding path and do not prove arbitrary external bytes valid or every uninspected interop route safe. It must not claim checks ran unless the trace establishes that fact.
- Leaves the workspace untouched despite write-capable tools.

Skill composition is graded separately. All requirements apply.
