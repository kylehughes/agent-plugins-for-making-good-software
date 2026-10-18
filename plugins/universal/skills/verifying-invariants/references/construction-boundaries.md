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

For an immutability claim, inspect the backing storage as well as its public accessor. A read-only getter, omitted setter, storage-layout restriction, or private-looking name does not necessarily prevent ordinary assignment through another path. Establish the language's actual access and mutation rules before recommending such a repair; otherwise describe it as a convention or a partial restriction. Apply the original mutation counterexample to the proposed representation before claiming that the path is closed.

## Keep raw and validated representations distinct

A useful pipeline is raw input → checked domain value → derived presentation. The raw stage can represent malformed or incomplete input; that is often necessary. The contract is that such input cannot enter the validated stage unchecked.

Test valid input, each independent rejection rule, boundary values, and the paths that could bypass the intended constructor. If a decoder assigns fields directly, constructor tests alone do not cover decoding. If a validated object holds a mutable child, freezing the outer reference alone does not preserve the child's predicate.

Keep the logical form of the contract intact. Rejecting a comparison's apparent opposite does not establish the desired predicate when the domain permits unordered, unknown, or exceptional outcomes. Inspect the language's comparison semantics and check representative cases before treating those forms as equivalent. State the exact established rule in maintained artifacts; a stronger guarantee needs an authorized boundary and evidence for it. Do not silently strengthen input restrictions merely to make a broader statement true.

Separate the successful-return postcondition from a total input-to-error contract. Trace three outcomes through the boundary: a validated result, an explicit rejection, and failure while obtaining or checking the input. The rejection branch's error describes only executions that reach it; comparisons, conversions, accessors, and called code can fail earlier. “Only validated values return” does not imply “every other input produces the rejection error.” A named-error claim needs its own input domain and path evidence, including any failure normalization the contract requires. Keep incidental outcomes with their input representations in the evidence record; they need not become additional maintained promises.

For example, this language-neutral boundary checks a value before returning it. The predicate either produces a Boolean or fails; the returned value is the checked value.

```text
value = read(source)                 // may fail
holds: Boolean = predicate(value)    // may fail before producing a Boolean
if holds == false:
    raise Rejection
return value
```

Supported: “Every successful result passed the predicate. Inputs that reach the predicate and for which it completes with false raise Rejection.” Unsupported: “Every input that does not return a valid value raises Rejection.” The latter assigns the branch's error to earlier read or evaluation failures. Keep the conditions in maintained wording instead of replacing them with the complement of success.


Include supported representations of the same domain value when a repair introduces a runtime type or category test. A language's nominal category may omit another valid representation of a quantity. Gating validation on that category can leave invalid values unchecked; rejecting everything outside it can break compatible positive inputs. Prefer the established domain predicate unless the contract independently requires the narrower category. Do not infer that untested representations are unsupported. Adding exclusions to a manifest or tests cannot supply missing authority for a contract change.

Inspect mutation through both incoming aliases and the stored child itself. A defensive copy severs an incoming alias, but an exposed mutable copy can still be changed after validation. Preserve the invariant with immutable owned values or access boundaries that route every permitted mutation through the checking authority. Apply this reasoning recursively when a collection contains mutable elements.

Check every proposed repair against the same boundary inventory, including alternative suggestions. Removing the demonstrated bypass is only a partial repair if another scoped path still invalidates the value. State that limitation instead of presenting the alternative as sufficient.

After finding a bypass, trace the invalid value through downstream operations within scope. Copying, serialization, and immutability can preserve an invalid value just as faithfully as a valid one. When a downstream guarantee assumes valid input, establish that assumption on every incoming path; a checked constructor elsewhere is insufficient.

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
