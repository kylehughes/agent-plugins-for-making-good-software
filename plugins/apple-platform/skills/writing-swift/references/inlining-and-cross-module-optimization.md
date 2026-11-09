# Inlining and Cross-Module Optimization

## Contents

- What `@inlinable` does
- Determine the distribution model first
- Decide per declaration
- Apply it correctly
- Resilient libraries
- Related attributes
- Verify
- Review checklist

## What `@inlinable` Does

A module normally exports only the signature of a `public` function. A client in another module calls it through its
entry point and cannot see the body, so it cannot inline the call, specialize generic parameters, or optimize a closure
argument together with the code that calls it. An unspecialized generic call passes type metadata and witness tables and
dispatches every protocol requirement dynamically.

`@inlinable` publishes the body as part of the module's interface. The client's optimizer may then inline or specialize
it. It is a permission, not a command: the optimizer still decides per call site, and the module still emits a callable
entry point. It changes nothing within the declaring module, and nothing in unoptimized builds.

The cost is that the body stops being private. Everything it references must be visible to clients, client builds compile
it again, and specialized copies add code size.

## Determine the Distribution Model First

The same attribute is routine in one setting and a long-term commitment in another. Before adding or reviewing it, find
out how clients receive the module.

- **Built from source with its clients**: Swift package targets and products, and framework or library targets built in
  the same workspace, without library evolution. Clients recompile whenever the module changes, so an inlinable body is
  not an ABI commitment. Its costs are build time, code size, and a wider interface.
- **Resilient binary**: `BUILD_LIBRARY_FOR_DISTRIBUTION = YES`, `-enable-library-evolution`, an XCFramework, or anything
  shipped as a prebuilt binary with a `.swiftinterface`. Clients keep the copy of the body they were compiled with. Follow
  [Resilient libraries](#resilient-libraries).

Check the build settings and the manifest's `swiftSettings` and `unsafeFlags`; do not infer the model from the directory
layout. A package that is also vended as an XCFramework is resilient.

Know what the optimizer already does. Optimized builds of a source-built module get a conservative form of cross-module
optimization by default in current toolchains, which lets clients inline some small public functions without any
attribute. It is a heuristic, not a contract. In a check with Swift 6.4 and SwiftPM, a release build inlined a trivial
non-generic public function across modules but still called a public generic function through its unspecialized entry
point until the function was marked `@inlinable`. For generic API, state the intent with the attribute.

## Decide per Declaration

In a source-built module, apply `@inlinable` when writing the declaration; a benchmark is not required. Work through
these in order:

1. Is the declaration `public` or `package` and called from another module? If not, stop: the attribute does nothing.
2. Is the module a resilient binary? If so, use the stricter rules below.
3. Does the client gain something from seeing the body? See the table.
4. Can the body be expressed against declarations the client may see, with at most a few `@usableFromInline` additions? If
   it would drag many internals into the interface, split out a small inlinable entry point or skip the attribute.

| Declaration | Decision |
| --- | --- |
| Generic function, method, initializer, or subscript, including `some` parameters | Add. Specialization is the main benefit. |
| Member of a public generic type, such as a container, wrapper, or algorithm | Add, with `@usableFromInline` storage. |
| Function that takes a closure and calls it in its body, such as `map`-style helpers and `with…` scopes | Add. |
| Default implementation in an extension of a public protocol | Add when small or likely to be called in loops. |
| Trivial accessor, operator, forwarding method, or small initializer on a public value type | Add. |
| Small non-generic function called from hot client code | Add when the call is known to be hot; otherwise leave it to the optimizer. |
| Large or cold body: I/O, logging, error construction, setup that runs once | Skip. Keep it out of line. |
| Non-generic feature, coordinator, factory, view-model, or service code | Skip. The call is not the cost. |
| Body that names types or modules the client is not meant to see | Skip. See below. |
| Body containing logic that must change for every client at once, such as validation, security checks, or wire formats, in a resilient library | Skip. |

An inlinable body is part of the interface, so it defeats encapsulation that depends on hiding the body. A function in an
export module that constructs a concrete type from an implementation module must not be inlinable, and the modules it
references cannot be imported with `internal import` or `@_implementationOnly`. When
[package structure rules](../../structuring-swift-packages/SKILL.md) separate interfaces from implementations, inlinable
code belongs with generic utilities and value types, not with factories and assemblies.

Do not add the attribute to every public declaration in a module. Each use should match a row above.

## Apply It Correctly

An inlinable body may reference only `public` declarations and those marked `@usableFromInline` or `@inlinable`. The
compiler rejects references to plain `internal`, `package`, `fileprivate`, and `private` declarations, and rejects types
declared inside the body.

```swift
public struct RingBuffer<Element> {
    @usableFromInline var storage: [Element?]
    @usableFromInline var head = 0

    @inlinable
    public init(capacity: Int) {
        precondition(capacity > 0)
        storage = Array(repeating: nil, count: capacity)
    }

    @inlinable
    public mutating func append(_ element: Element) {
        storage[head] = element
        head = (head + 1) % storage.count
    }
}
```

- `@usableFromInline` applies to `internal` and `package` declarations. Source access is unchanged, so clients still
  cannot name the declaration, but its symbol and signature become part of the interface. This is not widening access;
  never make a member `public` only to satisfy an inlinable body.
- `private` and `fileprivate` members cannot be `@usableFromInline`. Raise them to `internal` with the attribute, and keep
  the invariant in the type's API rather than in the access level.
- `@inlinable` on an `internal` declaration already makes it usable from inline code. Adding both produces a warning.
- Mark the initializers and stored properties a generic type's inlinable members need. One unmarked helper in the middle
  of a call chain ends specialization at that call.
- On a property or subscript, the attribute covers every accessor.
- Place it with the other attributes, before access control. Follow the repository's attribute layout.

Keep the common path inlinable and the rare path out of line. This bounds code growth in clients and keeps cold code out
of the interface:

```swift
@inlinable
public func checkedIndex(_ index: Int, in count: Int) -> Int {
    if index >= 0 && index < count { return index }
    indexOutOfRange(index, count)
}

@usableFromInline
func indexOutOfRange(_ index: Int, _ count: Int) -> Never {
    fatalError("Index \(index) is out of range for count \(count)")
}
```

## Resilient Libraries

With library evolution, a client binary keeps the body it was compiled with while the framework is replaced underneath
it. One process can run the old body in one client and the new body in another.

- Treat a published inlinable body as permanent. Later versions may make it faster, but observable behavior must stay the
  same, and old and new copies must agree on anything they share, such as stored layout, hashing, and encoded formats.
- A `@usableFromInline` declaration is ABI. It cannot be removed or change signature once shipped.
- Adding `@inlinable` to an existing public declaration is compatible. Removing it is compatible only because old clients
  keep their copy, so removal does not retract the old behavior.
- A fix inside an inlinable body does not reach clients until they recompile. Keep anything that may need an urgent fix
  out of line.
- `@frozen` is the matching commitment for stored layout and enum cases. Decide it separately; an inlinable member does
  not require a frozen type.
- Record the reason for each use in a comment or the change description, and inspect the generated `.swiftinterface` to
  confirm what the change exposes.

In a resilient library, add `@inlinable` deliberately: generic algorithms and thin wrappers whose behavior is fixed by
their contract. Measure when the benefit is uncertain.

## Related Attributes

- `@inline(__always)` and `@inline(never)` direct the inliner inside whatever the optimizer can already see. They do not
  expose a body to other modules. `@inline(__always)` needs a measurement; `@inline(never)` is appropriate for cold paths
  and benchmarks.
- `@backDeployed(before:)` lets clients of an ABI-stable library call a new API on OS versions that predate it by emitting
  a fallback copy into the client. Use it for availability, not speed. Its body follows the same visibility rules.
- `package` declarations take `@inlinable` and `@usableFromInline` like `internal` ones, so targets in one package can
  specialize each other's generic code without publishing it.
- Cross-module optimization flags, `@_specialize`, `@_alwaysEmitIntoClient`, `@_transparent`, and other underscored
  attributes are unsupported or build-wide controls. Do not introduce them without a measurement and a request for that
  level of control. Never add `unsafeFlags` to a package for this purpose; it blocks use as a versioned dependency.

## Verify

- Build the client in release configuration. Debug builds do not inline or specialize, and neither do debug tests.
- Run tests in both configurations when a body is inlinable. A missing `@usableFromInline` fails at compile time, but
  behavior that differs between the inlined and out-of-line copies appears only under optimization.
- For a hot path, confirm the effect: look for the specialized symbol or the absence of the call in the client binary, or
  compare a benchmark before and after. See [Review and debugging](review-and-debugging.md#performance-investigation).
- For a resilient library, diff the `.swiftinterface` and run the project's API or ABI checker if it has one.

## Review Checklist

- Is the distribution model known, and does the decision match it?
- Does every public generic, closure-taking, or trivial value-type API in a source-built library module carry
  `@inlinable`, or have a reason not to?
- Is the attribute absent from cold, large, non-generic, and boundary-hiding code?
- Are supporting declarations `@usableFromInline` rather than widened to `public`?
- Does the inlinable call chain reach the code that matters without an unmarked helper in the middle?
- In a resilient library, can every inlinable body stay behaviorally fixed, and is the reason recorded?
- Was the result checked in an optimized build?

Primary references:

- https://github.com/swiftlang/swift-evolution/blob/main/proposals/0193-cross-module-inlining-and-specialization.md
- https://github.com/swiftlang/swift-evolution/blob/main/proposals/0376-function-back-deployment.md
- https://docs.swift.org/swift-book/documentation/the-swift-programming-language/attributes/
- https://www.swift.org/blog/library-evolution/
