# API Design and Style

## Contents

- Design from call sites
- Naming
- Choosing types and abstractions
- Optionals and errors
- Generics, existentials, and ownership
- Access control and library evolution
- Documentation
- Formatting, comments, and files
- Performance and allocation
- API review checklist

## Design from Call Sites

Write representative call sites before finalizing an API. Optimize for clarity at use sites, not declaration cleverness.
Make common operations concise and uncommon or dangerous operations explicit.

Prefer domain operations over exposing storage. A type that publishes mutable collections, implementation queues, or raw
state often makes its invariants impossible to maintain.

Use strong types when values have different meanings despite sharing a representation:

```swift
struct UserID: Hashable, Sendable, Codable {
    let rawValue: UUID
}
```

Do not wrap every primitive automatically. Add a type when it enforces validation, prevents argument confusion, carries
behavior, or defines a stable API boundary.

## Naming

Follow the Swift API Design Guidelines:

- Types and protocols use `UpperCamelCase`.
- Functions, properties, variables, argument labels, and enum cases use `lowerCamelCase`.
- Include every word needed to make a call site grammatical and unambiguous; omit words that merely repeat type information.
- Name mutating operations with imperative verbs and nonmutating counterparts with noun or past-participle forms when the
  distinction is useful, such as `sort()` and `sorted()`.
- Name Boolean values as assertions: `isReady`, `hasCachedValue`, `canRetry`.
- Name protocols for what a conforming type is (`Collection`) or a capability (`Sendable`, `ProgressReporting`). Do not
  force an `-able` suffix when a domain noun is clearer.
- Use terminology consistently with the platform and domain. Avoid unexplained abbreviations.
- Give closure parameters labels when the roles are not obvious.

Do not preserve a poor name solely because it is local if a safe focused rename materially improves correctness. Do not
rename public API without considering source compatibility and migration aliases.

## Choosing Types and Abstractions

Use a `struct` when independent value semantics fit the domain. Use an `enum` for a closed set of states or alternatives.
Use a `class` for identity, shared ownership, Objective-C interoperability, or framework requirements. Mark classes `final`
unless subclassing is an intentional supported design.

Prefer composition over inheritance, but do not create protocols for every concrete dependency. A useful protocol:

- Represents a stable semantic capability.
- Has requirements a conformer can satisfy coherently.
- Enables multiple meaningful implementations, generic algorithms, or a boundary worth substituting.
- Does not expose implementation accidents solely for mocking.

Keep protocol requirements minimal. Put universally correct derived behavior in protocol extensions; avoid defaults that
silently change semantics for conformers.

Use enums with associated values to model mutually exclusive states. Do not replace a small clear state machine with
parallel optionals and Boolean flags.

## Optionals and Errors

Use an optional when absence is expected and needs no failure detail. Use `throws` when callers may need context or distinct
recovery. Use a result enum when success/failure is stored, transported, or composed as data.

At call sites:

- Use `guard` to establish prerequisites and keep the main path visible.
- Use `if let` when both branches are peer behavior.
- Use `map`, `flatMap`, and optional chaining when they clarify transformation, not to avoid straightforward control flow.
- Use `??` only when the fallback is semantically valid; do not hide missing required data with a convenient default.

Design error types around caller decisions. Preserve underlying errors when they contain diagnostics or recovery data. Use
`LocalizedError` for user-facing or operator-facing text where appropriate, but do not make localized strings the only
machine-readable distinction.

Typed throws can improve a constrained API, especially at module boundaries, but it also commits the API to an error set.
Use untyped `throws` when implementation flexibility or composition with multiple failure sources matters more.

Never use `try?` merely to silence a failure. It is appropriate only when all failures intentionally collapse to absence.

## Generics, Existentials, and Ownership

Use generics when the implementation preserves type relationships or benefits from static specialization. Use `some
Protocol` when callers should see one hidden concrete type. Use `any Protocol` when heterogeneous runtime storage or dynamic
substitution is required.

Do not introduce `Any...` wrappers until an actual storage or API boundary requires type erasure. Prefer primary associated
types and constrained existentials when they express the needed relationship directly.

Use opaque result types, noncopyable types, borrowing/consuming parameters, `Span`, and `InlineArray` only where ownership,
layout, or performance constraints justify the complexity. Keep such code behind a small, well-tested boundary and document
lifetime assumptions. Ordinary collections and value types remain the default.

## Access Control and Library Evolution

Start with the narrowest access that satisfies the design:

- `private` for implementation details of one declaration scope.
- `fileprivate` for intentional same-file collaboration.
- `internal` for module implementation.
- `package` for cross-target package implementation that is not public API.
- `public` for supported consumer API.
- `open` only when external subclassing or overriding is a designed extension point.

Review a public declaration for naming, availability, concurrency annotations, `Sendable`, error behavior, generic
constraints, and documentation before shipping it. Public stored properties and enum cases can constrain future evolution.

For resilient libraries, understand `@frozen`, `@inlinable`, `@usableFromInline`, and implementation-only import behavior
before using them. These attributes expose layout or implementation details to clients and should not be added as generic
performance advice.

Use SPI only when the distribution model and clients explicitly support it. Treat access-controlled imports and exported
imports as API-surface decisions.

## Documentation

Write DocC comments for public library API and for internal behavior whose contract is not evident.

A good documentation comment starts with a concise summary fragment or sentence suitable for generated quick help, then
adds only useful detail:

```swift
/// Returns the cached value, loading it when necessary.
///
/// Concurrent callers share one in-flight load. A cancelled caller stops waiting
/// without cancelling a load still needed by other callers.
///
/// - Parameter key: The key whose value should be loaded.
/// - Returns: The cached or newly loaded value.
/// - Throws: `CacheError.missing` when the loader produces no value.
func value(for key: Key) async throws -> Value
```

Document:

- Preconditions and invariants not expressed by the type system.
- Parameters whose meaning is not obvious at the call site.
- Return and error semantics.
- Ownership, mutation, caching, thread safety, actor isolation, cancellation, and ordering.
- Availability and performance characteristics when callers must design around them.
- Examples for subtle workflows, not every trivial property.

Use symbol links and code formatting supported by DocC. Test documentation builds when docs are part of the deliverable.
Do not force every comment into one grammatical template; clarity in generated documentation is the goal.

## Formatting, Comments, and Files

Repository automation is authoritative. Detect `.swift-format`, `.swiftformat`, `.swiftlint.yml`, build plugins,
pre-commit hooks, and CI commands before formatting. Apple `swift-format` and Nick Lockwood's `SwiftFormat` are different
tools with different configuration files and rules; do not pass one tool's configuration to the other.

Defaults when no project rule exists:

- Four-space indentation is conventional, but preserve the file's consistent style.
- Use trailing commas in multiline literals and argument lists when supported by the formatter.
- Keep one statement per line and break long expressions at semantic boundaries.
- Prefer formatter output over hand-aligned columns that churn with renames.
- Use `// MARK:` to divide a genuinely long declaration or group protocol conformances when it improves navigation.
- Keep a primary type and tightly coupled private helpers together. Split files around ownership and comprehension, not an
  absolute one-type rule.
- Keep conformance extensions near the type or in focused files according to repository convention.
- Preserve legal headers already required by the project. Do not add personalized copyright headers.
- Do not reorder members or imports solely for aesthetics unless the formatter/linter requires it.

Comments should explain rationale, invariants, surprising platform behavior, or temporary workarounds with a removal
condition. Delete commented-out code; version control already preserves history. Avoid stale TODOs without an owner or
tracking reference where the repository expects one.

## Performance and Allocation

Do not guess. Establish a workload and measure release builds with an appropriate profiler or benchmark.

Start with algorithmic complexity, I/O behavior, task fan-out, copying, and allocation patterns. Then consider specialized
storage, ownership, inlining, or atomics.

Review common Swift costs without assuming each is a bug:

- Copy-on-write uniqueness checks and accidental large value copies.
- Bridging between Swift and Objective-C collections or strings.
- Existential boxing and type erasure in hot paths.
- Repeated formatter, decoder, regex, or date-component construction.
- Unbounded task creation or stream buffering.
- Actor hops in fine-grained loops.
- Retain cycles in closures and long-lived tasks.

Use `@inline(always)`, `@specialize`, `@inlinable`, `withoutActuallyEscaping`, unsafe pointers, or manual memory management
only with measurements, comments explaining the invariant, and tests covering the boundary.

## API Review Checklist

- Do representative call sites read naturally?
- Does the type encode required states and distinguish semantically different values?
- Are reference identity and mutation intentional?
- Is every protocol earning its abstraction cost?
- Are absence and failure modeled distinctly?
- Are concurrency isolation, transfer, and cancellation visible in the API?
- Is access no wider than required?
- Are public compatibility and availability implications understood?
- Does documentation explain contracts rather than syntax?
- Is performance complexity justified by evidence?

Primary references:

- https://www.swift.org/documentation/api-design-guidelines/
- https://docs.swift.org/swift-book/documentation/the-swift-programming-language/
- https://www.swift.org/documentation/docc/
