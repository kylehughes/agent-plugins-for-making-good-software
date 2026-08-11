---
name: structuring-swift-packages
description: >
  Applies Swift package and module structure rules with correct dependency boundaries:
  export vs. internal module classification, suffix conventions, composition roots,
  factory patterns in interface modules, and promotion recipes for crossing boundaries.
  Use when creating packages or modules, resolving circular dependencies, promoting types
  across package boundaries, wiring cross-package dependencies, or deciding where new
  code belongs. Do not use for app-level architecture questions that do not involve
  package or module boundaries.
---

# Structuring Swift Packages

## Philosophy

**Only depend on what's designed to be depended upon.**

Every production module is either an **export** or an **internal** (`*Testing` modules stand outside the classification):

- **Exports** are stable, abstract, and designed for cross-package consumption. They define **what** a package provides.
- **Internals** are volatile, concrete, and private to the package (plus the app target). They define **how** a package implements what it provides.

**The fundamental rule: cross-package, only import exports.**

## Module Suffixes

The module suffix determines classification. Every suffix is deterministic — no ambiguity:

| Suffix | Classification | Content |
|---|---|---|
| `*Models` | Always export | Pure data types and data-shape protocols, minimal dependencies |
| `*Interfaces` | Always export | Service-capability protocols and contracts |
| `*UI` | Always export | Presentational components, no service binding |
| `*Assembly` | Always export | Pre-wired factory conformances for cross-package consumption |
| `*Feature` | Always internal | Coordinators, view models, and views wired to services |
| `*Services` | Always internal | Business logic, service dependencies |
| `*Testing` | Neither | Test targets only |

These suffixes apply to **every package** in a project. There are no exceptions — every module is classified by its suffix, and every classification carries the same dependency rules regardless of how "infrastructure-like" a package feels.

### The `*UI` / `*Feature` Boundary

`*UI` and `*Feature` are the critical distinction. `*UI` modules provide reusable presentational components — views that accept data and emit user actions. `*Feature` modules contain feature screens — coordinators, view models, and views wired to services.

The line is strict: a `*UI` module must not depend on any `*Services` or `*Feature` module. It must not accept closures or callbacks that perform service-layer work (network calls, cache writes, analytics). If a component needs to trigger a service operation, it emits an action through a delegate or callback and the `*Feature` layer handles the side effect. This prevents `*UI` modules from becoming secretly service-bound through injected closures.

Third-party image loading, caching, and formatting libraries are not services. A `*UI` module that uses such a library remains a `*UI` module.

If a `*UI` module needs a Services dependency, rename it to `*Feature`. The rename is the architectural decision — it should be visible in the diff.

A package may have both a `*UI` export and a `*Feature` internal — e.g., `ProfileUI` for presentational card components alongside `ProfileFeature` for detail screens with service wiring.

### Verification

The naming convention encodes the structural constraint. To verify a module is correctly named, check its `Package.swift` dependencies:

- A `*UI` module must not depend on any `*Services` or `*Feature` module. If it does, it should be a `*Feature` module.
- A `*Feature` module is expected to depend on `*Services` modules.

## Three Categories

### Exports

The shareable surface of every package. Models, Interfaces, `*UI`, and `*Assembly` modules. May be imported by any module in any package.

### Internals

The private implementation of each package. `*Services` and `*Feature` modules. May only be imported within the same package, by the app target, or by composition roots.

### Composition Roots

Terminal modules that no non-root module depends on. In the app process: the app target and its initialization orchestrator when one exists (for example an `AppBootstrapServices` module the app target imports). May import anything — exports and internals — because only other composition roots may depend on them.

Composition roots are pressure points. Every cross-feature factory and protocol wiring flows through them. As the app grows, a single composition root becomes a merge-conflict magnet and build bottleneck — every internal module change forces its recompilation.

Decompose a composition root internally into domain-specific dependency graphs (e.g., the app target's `SignedInDependencyGraph`) so cross-feature wiring is grouped by area instead of accreting in one type. The root set itself stays fixed within the app process — the app target and its initialization orchestrator — so new wiring lands inside an existing root, never as a new root module.

An app extension target (e.g., a `NotificationServiceExtension`) is the composition root of its own process and imports only the internal module it composes.

## Intra-Package Dependencies

The cross-package rules govern which modules can be imported from other packages. Within a single package, a strict layering also applies:

| From ↓ / To → | Models | Interfaces | UI | Assembly | Services | Feature |
|---|---|---|---|---|---|---|
| Models | — | ✗ | ✗ | ✗ | ✗ | ✗ |
| Interfaces | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| UI | ✓ | ✓ | — | ✗ | ✗ | ✗ |
| Assembly | ✓ | ✓ | ✗ | — | ✓ | ✓ |
| Services | ✓ | ✓ | ✗ | ✗ | — | ✗ |
| Feature | ✓ | ✓ | ✓ | ✗ | ✓ | — |

Models is the leaf. Feature is the intra-package composition point — it pulls together UI and Services to wire full features. Assembly is the cross-package composition point — it imports its own package's internals to provide pre-wired factory conformances that other packages can consume. No within-package cycles are permitted.

## Testing Modules

`*Testing` modules provide test doubles, fixtures, and utilities. They are consumed by test targets and by `#if DEBUG`-guarded code such as previews — never by production code paths. SwiftPM cannot make a dependency debug-only, so a production module whose previews use test doubles declares the `*Testing` product unconditionally; the import and usage stay inside `#if DEBUG`. `*Testing` modules may import any module from any package, including internals. Conversely, any test target may import `*Testing` modules from other packages to reuse test doubles — the cross-package export rule does not apply to test-only consumption.

## Rules

### Rule 1: Cross-Package, Only Import Exports

`*Services` and `*Feature` modules are internals — do not import them from another package. The only modules permitted to import internals cross-package are **composition roots** (the app target, its initialization orchestrator, and app extension targets within their own process) and **test targets**. Everything else must go through exports. For shared domain data, keep one source of truth — do not introduce a second state-management layer for cross-feature data synchronization.

### Rule 2: When You Need Something from an Internal, Promote It

In order of preference:

1. **Move the code** to the correct export module. Often the code is in the wrong place — a protocol in a Feature module that belongs in Interfaces, a data type in Services that belongs in Models, a presentational view in Feature that belongs in UI.
2. **Define a protocol** in Interfaces and have the internal module conform. Inject the concrete implementation at the composition root.
3. **Define a factory** in Interfaces when you need another feature's view or coordinator. The factory returns an opaque type (`AnyView`, `any Coordinating`). Wire at the composition root.
4. **Define a delegate** when you need navigation to another feature. The presenting feature defines the delegate protocol. A parent coordinator implements it. Cross-feature navigation always uses coordinator delegates — do not introduce a centralized router or routing intents.

### Rule 3: Exports Must Form a DAG

If two export modules would need to depend on each other, extract the shared concepts to a lower-level Models module or merge the packages. Use primitive types (IDs, strings) at boundaries to minimize coupling.

### Rule 4: No Exceptions

Every package follows the same suffix rules and the same dependency constraints. There is no "foundational" or "infrastructure" escape hatch that lets a package bypass the export/internal discipline. A package that provides platform-level utilities (design tokens, networking, logging, coordination patterns) is governed by the same rules as a package that provides domain features. Its `*Services` modules are internal; its `*Models` and `*Interfaces` modules are exports.

This eliminates judgment calls. You never need to decide whether a package is "foundational enough" to warrant special treatment — the suffix determines the classification, the classification determines the dependency rules, and nothing overrides that.

## Decision Flowchart

When you need Type X from Package B in your module in Package A:

1. Is X in `PackageBModels`? → Import it. Done.
2. Is X in `PackageBInterfaces`? → Import it. Done.
3. Is X in `PackageBUI`? → Only `*UI` and `*Feature` consumers may import it (`*Models`, `*Interfaces`, and `*Services` must not depend on `*UI`). Verify it is a true export (run the structural test from the reference). If so, import it. Done.
4. Is X a data type or protocol in the wrong module? → Move it to Models or Interfaces. Then import that.
5. Is X a service? → Define a protocol in `PackageBInterfaces`. Have `PackageBServices` conform. Inject at the composition root.
6. Is X a view or coordinator in `PackageBFeature`? → Define a factory in `PackageBInterfaces`. Have `PackageBFeature` implement it. Wire at the composition root.
7. Is X a navigation target? → Define a delegate in YOUR package. The parent coordinator wires it.

## Factory Patterns

Two factory forms are used in Interfaces modules to break cross-package dependencies on concrete types.

### Factory Closures

A closure typealias that returns a protocol type. Use when the factory has a single creation path with fixed parameters.

```swift
// In ActivityInterfaces (an export)
public typealias ActivityFeedProviderFactory =
    @Sendable (
        _ accountId: Int,
        _ context: RequestContext
    ) -> any ActivityFeedProviding
```

The concrete implementation lives in the corresponding Services module. The composition root wires the concrete implementation to the factory.

### Factory Protocols

A protocol with one or more factory methods. Use when the factory creates a family of related types or when a single closure cannot express the creation surface.

```swift
// In FormInterfaces (an export)
public protocol FieldValidatorCreating {
    func makeDateValidator(...) -> any DateUpdatableFieldValidating
    func makeTextValidator(...) -> any TextUpdatableFieldValidating
    // ...
}

public protocol FormValidatorCreating {
    @MainActor func makeFormValidator(validators: [any FieldValidating]) -> any FormValidating
}
```

A concrete implementation struct lives in `*Assembly` when consumed by 2+ packages (e.g., `FieldValidatorFactory` in `FormAssembly`), or in `*Services` when consumed only within the package. Consumers depend on the protocol; the composition root or assembly provides the default.

Keep each factory protocol focused on one concept. `FieldValidatorCreating` creates field validators; `FormValidatorCreating` creates form validators. Do not combine unrelated creation responsibilities into a single protocol.

Both forms apply whenever one feature needs to create instances owned by another feature — coordinators, view controllers, view models, or service objects. This includes `UIViewController` subclasses embedded as children: define a protocol for the view controller's cross-package surface in `*Interfaces`, have the concrete class conform in `*Feature`, and provide a factory in `*Assembly`. For the full pattern when the created type is an `ObservableObject` that consumers need as `@StateObject`, see the "Observable Service" recipe in [the reference](references/recipes-and-verification.md).

## Reference Map

Load only what the task needs:

- For worked examples of each boundary-crossing technique, a diagnostic smell table, module verification walkthroughs, and edge cases, see [recipes and verification](references/recipes-and-verification.md).
