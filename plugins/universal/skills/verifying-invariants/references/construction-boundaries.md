# Construction boundaries

A representation excludes an invalid state only if every relevant way of obtaining and updating it preserves the invariant. Start with an explicit predicate and a supported context; do not infer a business contract from today's implementation.

## Inspect the whole path

For each affected type or representation, trace:

1. Public, internal, generated, and privileged constructors; factories and convenience overloads.
2. Decoding, database hydration, migrations, foreign interfaces, and reflection where supported.
3. Copies, replacements, setters, builder finalization, and deserialization into existing objects.
4. Mutable children and aliases that can change the value after validation.
5. Test-only entry points, unsafe escape hatches, and cross-module visibility.

Use language-specific guidance for what is actually enforceable. A type annotation in one language may enforce nothing at runtime; a restricted initializer in another may still be available to same-module code. Name the access context of a compiler claim.

## Keep raw and validated representations distinct

A useful pipeline is raw input → checked domain value → derived presentation. The raw stage can represent malformed or incomplete input; that is often necessary. The contract is that such input cannot enter the validated stage unchecked.

Test valid input, each independent rejection rule, boundary values, and the paths that could bypass the intended constructor. If a decoder assigns fields directly, constructor tests alone do not cover decoding. If a validated object holds a mutable child, freezing the outer reference alone does not preserve the child's predicate.

For a negative boundary fixture, keep unrelated syntax and structure valid so the input reaches the predicate being tested. Confirm rejection comes from that predicate. Malformed JSON failing before a quantity check does not establish that the quantity check works. Preserve the established wire format when proposing a validation fix unless the task explicitly calls for a format migration.

When two fields must agree, consider whether a single authoritative value can determine the other. When alternatives have different required data, consider whether each alternative can carry its own data. The companion for the implementation language owns the concrete representation.

## Compile rejection with a control

A negative compilation fixture needs a corresponding positive control, the same relevant compiler settings, and an expected diagnostic tied to the forbidden operation. A syntax error, missing import, unavailable compiler, compiler crash, or timeout cannot substantiate the invariant.

Compile against the production module or shared production sources. Include client and privileged contexts only where the claim covers them. Do not replace a production type with an idealized copy and transfer the result back to production.

Compiler rejection establishes only the property encoded by the checked language rules. It cannot establish that the predicate expresses the right domain rule, that every runtime boundary validates correctly, or that external facts remain true.

## Questions that expose gaps

- Can decoding obtain a value that normal construction rejects?
- Can mutation invalidate a previously valid object, including through an alias?
- Does an unchecked escape hatch exist in a context included in the claim?
- Are identity domains distinct or merely similarly named primitives?
- Is a cached flag being treated as evidence of a current external condition?
- Does a refactor create a second source of truth?

Report the specific path and consequence. A missing test is an evidence gap until inspection or a counterexample establishes an implementation defect.
