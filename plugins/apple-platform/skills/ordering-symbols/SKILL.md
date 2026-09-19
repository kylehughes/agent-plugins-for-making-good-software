---
name: ordering-symbols
description: "Order members within Swift types by declaration kind, access level, and name. Use when adding or moving members or reviewing their order; preserve order-dependent behavior."
---

# Swift Lexicographic Symbol Ordering

## Objective

Maintain deterministic, lexicographic ordering of Swift declarations wherever reordering is semantics-preserving. Consistent member ordering removes subjective placement decisions and makes types scannable: readers should know where to find a symbol without knowing its implementation.

This skill enforces the existing preference: order by declaration category, access level, static-vs-instance, and name. It does not introduce semantic grouping as an alternative to lexicographic ordering.

## Version and Platform Assumptions

- Use current Swift syntax and language behavior. Swift 6.3 is the relevant language version.
- iOS projects commonly span iOS 16 through the latest stable SDKs, with newer/beta APIs guarded as needed. Availability gates are safety boundaries, not sorting keys.
- Do not preserve old Swift-era conventions for compatibility with versions below the stated deployment target.
- Do not remove, weaken, or reorder availability fallbacks merely to improve symbol ordering.

## Non-Negotiable Safety Rule

Only reorder sibling declarations or sibling statements when it is safe to do so. Never reorder if the change could affect compilation, overload resolution, initialization order, synthesized API shape, runtime behavior, UI order, availability behavior, reflection, serialization, generated code, or tests.

When editing existing code, move a declaration together with all directly attached documentation comments, attributes, property wrappers, macros, conditional-compilation directives that guard only that declaration, and inline comments that describe that declaration.

If safety is uncertain, preserve the current order rather than guessing.

## Canonical Sort Keys

When a declaration is safe to reorder, compare it using these keys in order:

1. Major declaration category.
2. Access level, where applicable.
3. Static/type member before instance member, where applicable.
4. Declaration kind, where applicable.
5. Lexicographic name/signature.
6. Original order as a stable tie-breaker.

### Access-Level Order

Use this access order, from broadest to narrowest:

1. `open`
2. `public`
3. `package`
4. `internal` / omitted access modifier
5. `fileprivate`
6. `private`

Rules:

- Omitted access is `internal`, unless inherited from an enclosing `private`, `fileprivate`, `package`, `public`, or `open` declaration/extension.
- Sort a declaration by its getter/access level, not by setter-only access. For example, `public private(set) var title` belongs in the `public` bucket, and `private(set) var count` belongs in the `internal` bucket.
- Access modifiers on extensions affect unannotated members inside the extension.
- Access level is primary only where the ordering rules below say it is primary. Do not globally sort every declaration by access before category.

### Name Comparison

Use deterministic code-point lexicographic ordering for the comparison string.

- For properties and enum cases, compare the declared identifier.
- For type aliases, associated types, nested types, classes, structs, actors, enums, and protocols, compare the declared type name.
- For methods, compare the base name first. Use the full signature only as a tie-breaker among overloads.
- For initializers, compare the canonical initializer signature, such as `init()`, `init(coder:)`, `init(from:)`, `init(id:name:)`.
- For subscripts, compare `subscript` signatures after named computed properties and before methods.
- For operator functions, compare the operator token as the method base name.
- Ignore backticks around escaped identifiers for comparison, but otherwise treat every character literally. `_`, `$`, digits, and capitalization participate in the sort.
- Attributes and modifiers are not sort keys unless they change access level or static/type-member status. Ignore `@MainActor`, `@objc`, `@IBAction`, `@IBOutlet`, `@Published`, `@State`, `@Environment`, `@Observable`, `@discardableResult`, `final`, `override`, `required`, `convenience`, `mutating`, `nonmutating`, `async`, `throws`, `rethrows`, `isolated`, `nonisolated`, and similar annotations for ordering.

## Application Strategy

When writing or editing Swift code:

1. Identify the smallest declaration scope or statement block that can be safely reordered.
2. Classify each sibling declaration by category.
3. Apply the relevant access-level, static-vs-instance, kind, and name keys.
4. Preserve comments, attributes, wrappers, macros, and conditional guards with their declarations.
5. Check safety boundaries: initialization, enum order, property-wrapper order, availability, generated code, UI/result-builder order, and side effects.
6. Apply multi-line braced formatting.
7. Preserve original order for anything not proven safe.

## Reference Map

Load only the reference relevant to the task:

- [Type declaration order](references/type-declaration-order.md): ordering rules inside `class`, `struct`, `actor`,
  `enum`, and concrete extension bodies, including type-level declarations, enum cases, stored properties,
  initializers/deinitializers, and implementation details.
- [Protocols, extensions, and availability](references/protocols-extensions-and-availability.md): protocol
  requirement order, file-level extension order, and the safety boundaries around conditional compilation and
  availability.
- [Parameters and body ordering](references/parameters-and-body-ordering.md): semantic parameter ordering and the
  narrow cases where statements inside function/initializer/closure bodies may be sorted.
- [Formatting and comments](references/formatting-and-comments.md): multi-line brace formatting and how comments,
  MARKs, and documentation interact with reordering.
- [Complete type example](references/complete-type-example.md): a full type applying every ordering rule together.
