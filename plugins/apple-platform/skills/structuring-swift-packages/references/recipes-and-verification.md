# Package Structure Reference

Worked examples and diagnostic tools for the package structure philosophy described in [SKILL.md](../SKILL.md).

## Boundary Crossing Recipes

Each recipe maps to a promotion strategy from SKILL.md Rule 2, ordered by preference — use the simplest one that solves the problem.

### Move to the Right Export

**Symptom:** A data type, protocol, or pure utility lives in a `*Services` or `*Feature` module but has no service dependencies. Another package imports that internal just to reach it.

**Pattern:** Relocate the code to the export module where it structurally belongs — `*Models` for data types and data-shape protocols (property-only, no service dependencies), `*Interfaces` for service-capability protocols, `*UI` for presentational views with no service binding.

```swift
// Before — protocol in *Feature, depends only on Foundation types
// Packages/User/Sources/UserFeature/PresentableUser.swift
public protocol PresentableUser: Equatable, Identifiable, Sendable {
    var fullName: String { get }
    var id: Int { get }
    var profilePhotoURL: URL? { get }
}

// After — moved to *Models, which is where pure data contracts belong
// Packages/User/Sources/UserModels/PresentableUser.swift
// (same code, different module)
```

**Tradeoff:** The simplest fix — zero new abstractions. Only works when the code genuinely has no internal dependencies. Check the file's imports: if it touches anything from a `*Services` module, this isn't the right recipe.

### Protocol in Interfaces

**Symptom:** Package A needs a capability provided by Package B's `*Services` module — fetching data, resolving values, performing transformations that require service context.

**Pattern:** Define a protocol in `*Interfaces` that describes the capability. The `*Services` module conforms. The composition root injects the concrete instance.

```swift
// 1. Define the protocol in the provider package's Interfaces
// Packages/Workspace/Sources/WorkspaceInterfaces/WorkspaceIconResolving.swift
public protocol WorkspaceIconResolving: Sendable {
    func resolveIcon(for channel: some ChannelIconDataProviding) -> WorkspaceIcon
}

// 2. Conform in Services (unchanged internal, no new exports)
// Packages/Workspace/Sources/WorkspaceServices/WorkspaceIconResolver.swift
struct WorkspaceIconResolver: WorkspaceIconResolving { ... }

// 3. Consumer imports only the Interfaces module
// Packages/Messaging/Sources/MessagingServices/SomeService.swift
import WorkspaceInterfaces

init(iconResolver: some WorkspaceIconResolving) { ... }

// 4. Composition root wires the concrete implementation
let iconResolver = WorkspaceIconResolver()
let messagingService = SomeService(iconResolver: iconResolver)
```

**Tradeoff:** Introduces a protocol and requires composition-root wiring. Appropriate when the capability genuinely belongs in Services — do not create a protocol for code that should move to Models.

### Factory in Interfaces

**Symptom:** Package A needs to *create* a coordinator, view, or service object owned by Package B. The concrete type lives in a `*Feature` or `*Services` module.

**Pattern:** Define a factory protocol in `*Interfaces` that returns a protocol type. The `*Assembly` module (or app target for single-consumer factories) provides the concrete implementation. The composition root creates and injects it.

```swift
// 1. Factory protocol in Interfaces (an export)
// Packages/MainMenu/Sources/MainMenuInterfaces/MainMenuCoordinatorCreating.swift
@MainActor
public protocol MainMenuCoordinatorCreating: Sendable {
    func makeMainMenuCoordinator(accountId: Int) -> any MainMenuCoordinating
}

// 2. Concrete factory in Assembly
// Packages/MainMenu/Sources/MainMenuAssembly/MainMenuCoordinatorFactory.swift
public struct MainMenuCoordinatorFactory: MainMenuCoordinatorCreating {
    // Dependencies accepted as protocol types
    @usableFromInline let appInfoProvider: any AppInfoProviding

    @inlinable
    public init(appInfoProvider: some AppInfoProviding, ...) { ... }

    @inlinable
    public func makeMainMenuCoordinator(accountId: Int) -> any MainMenuCoordinating {
        MainMenuCoordinator(appInfoProvider: appInfoProvider, accountId: accountId, ...)
    }
}

// 3. Composition root creates the factory once
// App/Sources/AuthenticatedCoordinator.swift
let mainMenuCoordinatorFactory = MainMenuCoordinatorFactory(
    appInfoProvider: AppInfoService.shared,
    ...
)
```

When the factory is consumed by 2+ packages, the concrete implementation lives in a `*Assembly` module. Single-consumer factories stay in the app target.

**Tradeoff:** Heavier than a protocol-in-Interfaces — requires a factory registration site and deferred creation. Use when the consumer needs to *create* instances, not just call methods on an existing one.

### Assembly

**Symptom:** A factory protocol defined in `*Interfaces` is consumed by 2+ feature packages. The concrete factory lives in the app target because it imports the package's `*Feature` or `*Services` internals. Every intermediate coordinator between the composition root and each consumer must accept and forward the factory — parameter drilling.

**Pattern:** Create a `*Assembly` module in the factory's own package. The assembly imports the package's internals to instantiate concrete types, but only exposes protocol-conforming factory types. It is an export — other packages import it freely.

```swift
// 1. Factory protocol in Interfaces (already exists)
// Packages/MainMenu/Sources/MainMenuInterfaces/MainMenuCoordinatorCreating.swift
@MainActor
public protocol MainMenuCoordinatorCreating: Sendable {
    func makeMainMenuCoordinator(accountId: Int) -> any MainMenuCoordinating
}

// 2. Concrete factory in Assembly (the new module)
// Packages/MainMenu/Sources/MainMenuAssembly/MainMenuCoordinatorFactory.swift
import MainMenuFeature       // own package's internal
import MainMenuInterfaces    // own package's export
import AuthenticationInterfaces  // cross-package exports for dependencies
// ...other *Interfaces imports

public struct MainMenuCoordinatorFactory {
    // Dependencies accepted as protocol types — no cross-package internal imports
    private let appInfoProvider: any AppInfoProviding
    // ...

    public init(appInfoProvider: some AppInfoProviding, ...) { ... }
}

extension MainMenuCoordinatorFactory: MainMenuCoordinatorCreating {
    public func makeMainMenuCoordinator(accountId: Int) -> any MainMenuCoordinating {
        MainMenuCoordinator(
            appInfoProvider: appInfoProvider,
            accountId: accountId,
            // ...
        )
    }
}

// 3. Composition root creates the factory once
// App/Sources/AuthenticatedCoordinator.swift
import MainMenuAssembly

let mainMenuCoordinatorFactory = MainMenuCoordinatorFactory(
    appInfoProvider: AppInfoService.shared,
    // ...
)
```

When the factory requires no external service dependencies (e.g., validators that only need their own package's internals), the assembly type has a zero-argument init:

```swift
// Packages/Form/Sources/FormAssembly/FormValidatorFactory.swift
import FormInterfaces
import FormServices

public struct FormValidatorFactory {
    public init() {}
}

extension FormValidatorFactory: FormValidatorCreating {
    @MainActor public func makeFormValidator(validators: [any FieldValidating]) -> any FormValidating {
        FormValidator(validators: validators)
    }
}
```

**When to create an assembly:** The factory protocol is consumed by 2+ feature packages. Single-consumer factories stay in the app target — the assembly overhead isn't justified.

**Rules:**

1. An assembly imports exactly one package's internals (`*Feature` and/or `*Services`) — its own. Cross-package dependencies use protocol types from `*Interfaces` exports.
2. An assembly exports only protocol-conforming factory types. Concrete internal types never appear in the public API.
3. Naming: `<Noun>Factory` for the concrete type (e.g., `MainMenuCoordinatorFactory` for `MainMenuCoordinatorCreating`).

**Tradeoff:** Adds a module per package. Justified when it eliminates parameter drilling across multiple features. Strictly better build graph than the app target approach — changes to `*Feature` rebuild only `*Assembly` and its consumers, not the entire app target.

### Delegate for Navigation

**Symptom:** A feature screen needs to navigate to another feature's screen. Direct import of the target `*Feature` module would violate the cross-package rule.

**Pattern:** The presenting feature defines a delegate protocol. A parent coordinator — which already has access to both features — implements it and performs the navigation.

```swift
// 1. Delegate protocol defined by the feature that needs navigation
// Packages/Dashboard/Sources/DashboardFeature/DashboardCoordinatorDelegate.swift
@MainActor
protocol DashboardCoordinatorDelegate: AnyObject {
    func dashboardCoordinator(
        _ coordinator: DashboardCoordinator,
        didSelectWorkspace workspaceId: Int
    )
}

// 2. Parent coordinator implements the delegate
// App/Sources/Coordinators/TabCoordinator.swift
extension TabCoordinator: DashboardCoordinatorDelegate {
    func dashboardCoordinator(_ coordinator: DashboardCoordinator, didSelectWorkspace workspaceId: Int) {
        let workspaceCoordinator = WorkspaceCoordinator(workspaceId: workspaceId, ...)
        coordinator.present(workspaceCoordinator)
    }
}
```

**Tradeoff:** The delegate protocol is internal to the defining package — it does not need to be an export. The parent coordinator imports both features' internals because it lives in a composition root (the app target); parent coordinators are not themselves roots. The two features never import each other.

### Observable Service

**Situation:** A new `@MainActor ObservableObject` contains business logic (Combine subscriptions, state aggregation, network coordination) and consumers in other packages need it as `@StateObject`. The concrete class belongs in Services, but `@StateObject` requires a concrete type — not an existential.

**Pattern:** Five types across two modules. Each has a deterministic home.

**In Interfaces (export):**

```swift
// 1. Protocol — the contract
// Packages/Form/Sources/FormInterfaces/FormValidating.swift
@MainActor
public protocol FormValidating: ObservableObject {
    var isValid: Bool { get }
    func replaceValidators(_ validators: [any FieldValidating])
}

// 2. Type-erasing wrapper — concrete ObservableObject for @StateObject
// Packages/Form/Sources/FormInterfaces/AnyFormValidator.swift
@MainActor
public final class AnyFormValidator: FormValidating {
    private let base: any FormValidating
    private var cancellable: AnyCancellable?

    @Published public private(set) var isValid: Bool

    public init(_ base: any FormValidating) {
        self.base = base
        self.isValid = base.isValid
        // Subscribe to base.objectWillChange, forward to self
    }

    public func replaceValidators(_ validators: [any FieldValidating]) {
        base.replaceValidators(validators)
    }
}

// 3. Factory protocol — creation contract
// Packages/Form/Sources/FormInterfaces/FormValidatorCreating.swift
public protocol FormValidatorCreating {
    @MainActor func makeFormValidator(
        validators: [any FieldValidating]
    ) -> any FormValidating
}
```

**In Services (internal):**

```swift
// 4. Concrete implementation — the business logic
// Packages/Form/Sources/FormServices/FormValidator.swift
@MainActor
public final class FormValidator: FormValidating {
    @Published public private(set) var isValid: Bool = false
    // Combine subscriptions, state management, etc.
}
```

**In Assembly (export) — when consumed by 2+ packages:**

```swift
// 5. Concrete factory
// Packages/Form/Sources/FormAssembly/FormValidatorFactory.swift
import FormInterfaces
import FormServices

public struct FormValidatorFactory: FormValidatorCreating {
    public init() {}

    @MainActor public func makeFormValidator(
        validators: [any FieldValidating]
    ) -> any FormValidating {
        FormValidator(validators: validators)
    }
}
```

If the factory is consumed by only one package, the default factory stays in `*Services` instead.

**At the consumer:**

```swift
// The consumer depends only on Interfaces — never sees FormValidator or FormServices.
@StateObject private var formValidator: AnyFormValidator

init(formValidatorFactory: some FormValidatorCreating) {
    _formValidator = StateObject(
        wrappedValue: AnyFormValidator(
            formValidatorFactory.makeFormValidator(validators: [])
        )
    )
}
```

**At the composition root:**

```swift
// App/Sources/ — the app target imports FormAssembly
import FormAssembly

let factory = FormValidatorFactory()
```

**Why the wrapper exists:** Swift existentials (`any FormValidating`) cannot be used as `@StateObject` because SwiftUI requires a concrete `ObservableObject` type. The `Any*` wrapper is a concrete class that forwards protocol requirements to the underlying existential and bridges `objectWillChange` notifications. This is the same pattern as any `Any*` type-erasing wrapper.

**Why a separate factory protocol:** Keep each factory focused on one concept. A form validator factory creates form validators; a field validator factory creates field validators. Combining unrelated creation responsibilities into a single protocol couples concepts that change independently.

**When to use this pattern:** When all three conditions hold — (1) the type is an `ObservableObject`, (2) it contains business logic that belongs in Services, and (3) consumers in other packages need it as `@StateObject`. If any condition is missing, a simpler recipe applies: if it has no business logic, it belongs in Models or Interfaces directly; if consumers don't need `@StateObject`, a plain protocol-in-Interfaces suffices; if it stays within the package, no abstraction is needed.

## Smell Catalog

Quick-reference table. When you encounter a symptom, the diagnosis and first fix point you to the right recipe.

| Smell | Diagnosis | Fix |
|---|---|---|
| `*UI` imports a `*Services` module | Module is a misnamed Feature | Rename to `*Feature`, or split presentational code into a separate `*UI` export |
| Cross-package import of `*Feature` or `*Services` | Direct dependency on an internal | Factory in Interfaces, or delegate in the presenting Feature (see recipes above) |
| Two `*Interfaces` modules import each other | Cyclic coupling between exports | Extract shared concepts to a lower-level `*Models` module, or merge the packages |
| Low-level package imports a feature package | Misclassified — it contains domain logic | Apply suffix conventions and promotion rules |
| Export module A depends on export B which depends on A | DAG violation among exports | Extract shared types to a lower-level module that both depend on |
| Protocol in `*Models` that references service types | Protocol is in the wrong export | Move to `*Interfaces`, which may depend on `*Models` |
| `*Services` imports a `*UI` module | Structural violation — Services must not depend on UI | Move needed types to `*Models` or `*Interfaces` |
| Production module imports `*Testing` | Test code leaking into production | Move shared utilities to the appropriate production module |
| `*Feature` module with no `*Services` dependency | Module may be a misnamed `*UI` | Verify — if it truly has no service binding, rename to `*UI` |

## Verifying Module Classification

Walk through any `Package.swift` to confirm each module's suffix matches its dependency profile.

### The Structural Test

For each module in a package, check its target dependencies:

1. **`*Models`** — should depend only on Foundation-level types, other `*Models` modules, and third-party data libraries. No `*Services`, no `*Feature`, no `*UI`, no `*Assembly`.
2. **`*Interfaces`** — should depend only on `*Models` modules and other `*Interfaces` modules. May reference protocol types from other Interfaces if no cycle is introduced.
3. **`*UI`** — should depend on `*Models`, `*Interfaces`, and design system packages. Must not depend on any `*Services`, `*Feature`, or `*Assembly` module. Third-party image/formatting libraries are fine.
4. **`*Assembly`** — must depend on its own package's `*Feature` and/or `*Services` (the internals it wires), plus `*Interfaces` and `*Models` from its own and other packages. Must not depend on other packages' `*Feature`, `*Services`, or `*Assembly` modules.
5. **`*Services`** — expected to depend on `*Models`, `*Interfaces`, and networking and data-access libraries. Must not depend on `*UI`, `*Feature`, or `*Assembly`.
6. **`*Feature`** — the composition point within the package. May depend on `*Models`, `*Interfaces`, `*UI`, and `*Services` from the same package. Must not depend on `*Assembly`.

The suffix is the contract. Rename or split to make it honest.

### Reading a Package.swift

Walk through each `.target(name:dependencies:)` entry:

```
MessagingModels     → [Foundation]                                     ✓ Models: leaf, no service deps
MessagingInterfaces → [MessagingModels, WorkspaceModels]               ✓ Interfaces: depends on Models only
MessagingUI         → [MessagingModels, DesignSystemSwiftUI]           ✓ UI: Models + design system, no Services
MessagingServices   → [MessagingModels, NetworkingModels, ...]        ✓ Services: expected deps
MessagingFeature    → [MessagingServices, MessagingUI, MessagingModels] ✓ Feature: composition point
```

If `MessagingUI` had `MessagingServices` in its dependencies, it would fail the structural test and need renaming to `MessagingFeature` (or splitting its presentational content into a true `*UI` export).

## When to Merge or Split Packages

### Merge

Two packages should merge when their separation creates more friction than value:

- **Cyclic Interfaces dependencies.** Each defines protocols that reference types from the other. This means the concepts are inseparable at the contract level.
- **Frequent coordinated changes.** Modifying one package always requires modifying the other in the same PR. The boundary is artificial.
- **Protocols with entangled associated types.** A protocol in Package A has an associated type constrained to a protocol from Package B, and vice versa.

**Alternative to merging:** Extract the shared concepts into a lower-level package that both depend on. This works when the coupling is limited to a few types rather than pervasive.

### Split

A package should split when it mixes concerns that have different consumption patterns:

- **A module contains both export and internal concerns.** Presentational utilities (color mappings, format styles) sit alongside service-bound code (subscribed models, cache writers). The presentational code should be a `*UI` export; the service-bound code belongs in `*Services` or `*Feature`.
- **Two distinct feature areas share a package.** They don't share models and rarely change together. Separate packages reduce build times and make ownership boundaries clearer.
- **A `*UI` module has grown views that need service wiring.** Rather than renaming the entire module to `*Feature` (losing the export), split: keep presentational components in `*UI`, move wired screens to a new `*Feature` module.

## Edge Cases

Recurring questions about where the lines are drawn.

### Can `*UI` use image loading or caching libraries?

Yes. Third-party image libraries are not services. A `*UI` module that uses one remains a `*UI` module. The test is whether the library performs domain-specific business logic, not whether it does I/O.

### When does a closure in `*UI` become service binding?

When the closure performs service-layer work: network calls, cache writes, analytics tracking, or mutations. Action callbacks that emit user intent — `onTap`, `onSelect`, `onDismiss` — are fine. The `*UI` module says *what happened*; the `*Feature` layer decides *what to do about it*.

A practical test: could this closure's body be replaced with a no-op in a SwiftUI preview without breaking the component's visual contract? If yes, it's an action callback. If no, the component is secretly service-bound.

### Do `*Testing` modules obey the export-only import rule?

No. `*Testing` modules are consumed only by test targets and exist outside the production dependency graph. They may import any module — including internals — from any package. Conversely, any test target may import `*Testing` modules from other packages to reuse test doubles. The cross-package export rule does not apply to test-only consumption.

### Factory vs. protocol vs. delegate — when which?

- **Factory:** The consumer needs to *create* instances of a type it can't see. Returns `any ProtocolType` or `AnyView`. Wired at the composition root.
- **Protocol:** The consumer needs to *use* a capability. Defined in Interfaces, conformed to in Services, injected via initializer.
- **Delegate:** The consumer needs to *navigate* to a screen it can't see. Defined in the presenting feature, implemented by a parent coordinator that has visibility into both features.
- **Observable service:** The consumer needs to *create and observe* an `ObservableObject` from another package as `@StateObject`. Combines a protocol, a type-erasing wrapper, and a factory protocol — all in Interfaces. See the "Observable Service" recipe above.

If the verb is "create," use a factory. If the verb is "call" or "query," use a protocol. If the verb is "navigate" or "present," use a delegate. If the verb is "create and observe," use the observable service pattern.
