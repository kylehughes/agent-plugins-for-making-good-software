# UI State, Navigation, and Effects

Use this reference when modeling SwiftUI feature state, loading and refresh phases, forms, navigation, modal presentation, asynchronous effects, cancellation, or observation across an iOS 16 deployment baseline.

## Keep Domain State Independent From the Observation Mechanism

A feature's semantic state should not depend on whether the presentation layer uses Observation, `ObservableObject`, UIKit callbacks, or a reducer framework.

Prefer:

```text
Sendable domain state + explicit actions/transitions
    -> iOS 17+ @Observable adapter
    -> iOS 16 ObservableObject adapter
    -> UIKit adapter if needed
```

This keeps availability, actor isolation, and framework storage out of the domain model. The Observation framework and `@Observable` require iOS 17+. An app that deploys to iOS 16 needs an `ObservableObject`/`@Published` or manual-observation adapter for the older lane.

Do not put both mechanisms on one core model merely to share code. Share the state and transition logic; keep observation wrappers thin.

## Model UI Phases as Data

Replace correlated flags and optionals:

```swift
var isLoading: Bool
var value: Item?
var error: Error?
var isRefreshing: Bool
```

with one finite state:

```swift
enum LoadState<Value: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case loading(previous: Value?)
    case loaded(Value)
    case failed(Failure, previous: Value?)
}
```

The payload belongs to the case whose meaning it supports. Derive conveniences such as `isLoading`; do not persist a second flag that can drift.

Choose cases from product behavior, not from implementation steps. For example, distinguish initial loading from refresh only when the UI, retry behavior, telemetry, or cancellation policy differs.

## Give Asynchronous Work an Identity

An enum alone does not prevent an old response from overwriting newer state. Associate each effect with a request identity or generation.

```swift
import Foundation

struct LoadRequestID: Hashable, Sendable {
    let rawValue: UUID
}

enum ItemsState: Sendable {
    case idle
    case loading(id: LoadRequestID, previous: [Item])
    case loaded([Item])
    case failed(LoadFailure, previous: [Item])
}

enum ItemsAction: Sendable {
    case reload
    case response(id: LoadRequestID, Result<[Item], LoadFailure>)
}
```

When reducing `.response`, accept it only if its ID matches the currently active request. This models supersession explicitly and prevents stale effects even when cancellation arrives late or is ignored by a dependency.

Use a monotonically increasing revision when UUID identity is unnecessary. Avoid timestamps as identity unless clock semantics are part of the domain.

## Keep Effects Outside Persistent State

State should describe durable, renderable facts. An effect describes work to start, cancel, or delegate.

Avoid storing:

- `Task` handles inside values that must be `Equatable`, `Codable`, or restored.
- Closures in domain state merely to execute later.
- Raw service objects in navigation state.
- A mutable "is request running" flag separate from the phase that owns the request.

A transition can return commands:

```swift
struct ItemsCommand: Sendable {
    let id: LoadRequestID
    let operation: @Sendable () async -> ItemsAction
}

func reduce(
    state: inout ItemsState,
    action: ItemsAction
) -> [ItemsCommand] {
    // Pure state transition plus descriptions of work.
    []
}
```

The exact command representation may be an enum, closure-based witness, dependency call, or framework effect type. Preserve these properties:

- State transitions are testable without starting work.
- Every effect has an ownership and cancellation policy.
- Responses carry enough identity to reject stale work.
- Domain state does not retain mutable non-Sendable dependencies.

Do not force a reducer architecture onto a small feature. A `@MainActor` model with private tasks can obey the same rules.

## Cancellation Is Not Completion

A cancelled task may already have produced a remote side effect, and a dependency may not observe cancellation promptly. Decide separately:

1. Whether the local task should stop waiting.
2. Whether its eventual response may update current state.
3. Whether a remote operation needs compensation or reconciliation.
4. Whether cancellation is visible to the user.

Request identity is usually more reliable than assuming cancellation prevents all later callbacks.

Keep task ownership explicit. A view disappearing does not automatically mean the business operation should be cancelled; conversely, a screen-scoped search request usually should be.

## Forms Need Raw Editing State and Validated Submission State

Text entry must represent invalid intermediate values. Do not bind a `TextField` directly to a type whose initializer rejects an empty or partial value.

```swift
struct ProfileDraft: Equatable, Sendable {
    var displayName = ""
    var ageText = ""
}

struct ValidProfile: Equatable, Sendable {
    let displayName: NonEmptyString
    let age: AdultAge
}
```

The submit boundary converts `ProfileDraft` to `ValidProfile` and returns field-specific issues.

```swift
enum ProfileField: Hashable, Sendable {
    case displayName
    case age
}

struct FieldIssue: Equatable, Sendable {
    let field: ProfileField
    let message: String
}
```

Use stable error codes or typed reasons below the presentation layer when localization, analytics, or accessibility needs more than a message string.

Distinguish:

- Parsing: can text become the primitive representation?
- Validation: does the value satisfy domain policy?
- Canonicalization: which equivalent form is stored?
- Presentation: how is a failure explained in the current locale?

Do not encode every keystroke as a typestate axis. UI drafts are intentionally dynamic; the validated boundary is where the strong type pays off.

## Navigation Is a Closed Domain When the App Owns It

Use enums for routes the feature owns:

```swift
enum AppRoute: Hashable, Sendable {
    case account(AccountID)
    case order(OrderID)
    case settings(SettingsRoute)
}

enum SettingsRoute: Hashable, Sendable {
    case profile
    case privacy
    case notifications
}
```

Associated values bind the destination to the data it requires. A route should carry stable identity or immutable input, not an entire mutable view model.

For presentation slots, use one optional enum rather than independent booleans:

```swift
enum AccountSheet: Identifiable, Sendable {
    case rename(AccountID)
    case deleteConfirmation(AccountID)

    var id: String {
        switch self {
        case .rename(let id): "rename-\(id.rawValue)"
        case .deleteConfirmation(let id): "delete-\(id.rawValue)"
        }
    }
}
```

One slot means at most one sheet. Use separate slots only when simultaneous presentation is genuinely legal.

## Deep Links Are Untrusted Input

Do not decode an external URL directly into an internal route and assume it is valid.

```text
URL
  -> syntactic deep-link components
  -> validated identifiers and allowlisted route
  -> authorization/current-data check
  -> AppRoute
```

Parsing proves shape, not authority or existence. An account route still needs access checks and current data. Preserve unknown or future links as explicit failures rather than silently routing somewhere unrelated.

## Navigation Restoration Is a Persistence Boundary

A codable route path can outlive releases, account changes, feature flags, and deleted entities. Version and validate it like any persisted schema.

Decide:

- Whether unknown historical cases are dropped, migrated, or make restoration fail.
- Whether restored IDs are still visible to the current user.
- Whether modal state should be restored at all.
- How logout clears account-bound routes.
- How old app versions behave after a downgrade.

Do not equate `Hashable` with stable persistence identity. Hash values are not serialization formats.

## Recursive and Nested State

Use nested enums to keep local state spaces understandable:

```swift
enum CheckoutState: Sendable {
    case editing(EditState)
    case submitting(SubmissionState)
    case completed(Receipt)

    enum EditState: Sendable {
        case cart(CartDraft)
        case shipping(ShippingDraft)
        case payment(PaymentDraft)
    }
}
```

Use `indirect` recursive enums for genuinely recursive domains such as expression trees, outline navigation, or nested filters:

```swift
indirect enum Filter: Sendable {
    case predicate(FieldPredicate)
    case all([Filter])
    case any([Filter])
    case not(Filter)
}
```

Validate semantic constraints that the recursive shape alone cannot prove, such as empty groups, depth limits, or forbidden cycles introduced through references.

## `OptionSet` Is for Independent Combinable Flags

Use `OptionSet` when multiple options may coexist independently:

```swift
struct ExportOptions: OptionSet, Sendable {
    let rawValue: UInt8

    static let includeMetadata = Self(rawValue: 1 << 0)
    static let compress = Self(rawValue: 1 << 1)
    static let encrypt = Self(rawValue: 1 << 2)
}
```

Do not use `OptionSet` for mutually exclusive phases, ordered transitions, or combinations with different payloads. If some bit combinations are invalid, a closed enum or validated wrapper is often clearer.

For persisted or public option sets, reserve unknown bits and define whether they are preserved or rejected. Changing bit assignments is a wire-format change.

## Main-Actor Ownership

Presentation models with mutable UI state should normally be `@MainActor`.

```swift
@MainActor
final class ItemsModel {
    private(set) var state: ItemsState = .idle
    private var task: Task<Void, Never>?
}
```

Keep service dependencies `Sendable` or actor-isolated. Pass immutable snapshots into detached or concurrent work. Do not mark the entire domain model `@MainActor` merely because one presentation adapter owns it.

When default actor isolation is enabled for a module, inspect generated and inferred isolation rather than assuming an unannotated declaration is nonisolated.

## Observation Compatibility Lane

For an iOS 16–26 app:

- Keep `FeatureState` and actions deployment-neutral.
- Use an `@available(iOS 17, *) @Observable @MainActor` wrapper for Observation.
- Keep an iOS 16 `ObservableObject` wrapper when that deployment path remains supported.
- Share transition code rather than subclassing one wrapper from the other.
- Avoid exposing either wrapper as the domain service API.
- Test both wrappers against the same semantic state-transition suite.

The compiler macro may be available because of the SDK/toolchain while the generated framework references still require runtime availability. Treat `@Observable` as an iOS 17 framework lane, not as deployment-neutral syntax.

## Testing UI State Models

Test transitions, not only rendered snapshots:

- Every action in every meaningful state.
- Stale response rejection by request ID.
- Cancellation before and after suspension.
- Refresh failure preserving or discarding prior data according to policy.
- Form parsing, field issue accumulation, and successful refinement.
- Route parsing, authorization, unknown cases, and restoration migration.
- Logout or account switch clearing account-scoped state.
- Semantic parity between iOS 16 and newer observation adapters.

Property tests are useful for transition systems: generate action sequences and assert that forbidden combinations never appear.

## Review Checklist

- Does one value represent each mutually exclusive UI phase?
- Are correlated payloads stored in the case that owns them?
- Can a stale asynchronous response overwrite newer state?
- Is effect identity distinct from cancellation?
- Are tasks, closures, and mutable services kept out of persistent state?
- Can form state represent invalid intermediate input without weakening the submitted domain type?
- Are routes typed with stable IDs rather than mutable models?
- Are deep links and restored navigation validated at boundaries?
- Is `OptionSet` used only for independent combinations?
- Is mutable presentation state main-actor owned?
- Are Observation and `ObservableObject` compatibility wrappers separated from the domain model?
- Do transition tests cover failures, cancellation, restoration, and stale effects?
