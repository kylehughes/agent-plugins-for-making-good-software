# Identity, Typestate, and Capabilities

Use this reference for nominal IDs, phantom tags, staged APIs, capability construction, trust-state APIs, and builders. For compound relationships, go directly to [relationship recipes](domain-modeling-recipes.md#rel); for recoverable consuming transitions, use [workflow outcomes](domain-modeling-recipes.md#flow). Protocol and erasure mechanics belong to [advanced generics](advanced-generics-and-protocols.md).

## Nominal Identity

A `typealias` creates vocabulary, not a distinct type:

```swift
typealias UserID = UUID
typealias WorkspaceID = UUID
```

A `WorkspaceID` can still be passed where `UserID` is expected because both are exactly `UUID`.

Use nominal wrappers when substitution is invalid:

```swift
struct UserID: Hashable, Codable, Sendable {
    let rawValue: UUID
}

struct WorkspaceID: Hashable, Codable, Sendable {
    let rawValue: UUID
}
```

Remove raw overloads after migration. Keeping both `loadUser(_ id: UserID)` and `loadUser(_ id: UUID)` preserves the bypass.

### Phantom-tagged identifiers

When many identifiers share the same storage and behavior:

```swift
struct Identifier<Domain>: Hashable, Codable, Sendable {
    let rawValue: UUID
}

enum UserDomain {}
enum WorkspaceDomain {}

typealias UserID = Identifier<UserDomain>
typealias WorkspaceID = Identifier<WorkspaceDomain>
```

The tag has no runtime storage. The generic specialization creates a static distinction.

Prefer separate wrappers when domains differ in:

- Validation or canonicalization.
- Visibility or redaction.
- Database/wire representation.
- Domain methods.
- Availability or module ownership.

### Tag sealing

An uninhabited enum is a convenient namespace-level tag, but a public client can use a public generic wrapper with its own tag. That is normally fine: the wrapper distinguishes domains, not authority.

If creating a particular tag carries privilege or trusted meaning, do not expose a freely constructible generic state. Use a type with controlled initialization or keep the tag and relevant constructors nonpublic.

## Same-Repr Parameters Beyond IDs

Nominal wrappers are useful for:

- Email subject versus body.
- Latitude versus longitude.
- Source versus destination path.
- Ciphertext versus plaintext bytes.
- User-entered query versus escaped query.
- Pixels versus points.
- Retry count versus timeout seconds.

Do not wrap every primitive. Prioritize values that cross modules, appear together at call sites, carry security meaning, or have caused real swaps.

## Typed Keys

Replace string keys when the key determines a value type.

```swift
struct PreferenceKey<Value: Sendable>: Sendable {
    let name: String
    let defaultValue: Value
}

extension PreferenceKey where Value == Bool {
    static let analyticsEnabled = Self(name: "analyticsEnabled", defaultValue: false)
}
```

A complete typed-key store should decide:

- Serialization format.
- Namespacing and migrations.
- Whether defaults are persisted or synthesized.
- Concurrency/isolation of the backing store.
- What happens when stored bytes have the wrong type.

`KeyPath<Root, Value>` is preferable when fields are known members of a Swift type. A custom key is preferable for external stores, analytics schemas, localization catalogs, or feature flags.

## Typestate

Typestate encodes a phase in the static type so methods exist only in legal phases.

A payload-per-state design avoids force unwraps:

```swift
protocol RegistrationState: Sendable {}

struct DraftRegistration: RegistrationState {
    let rawEmail: String
    let acceptedTerms: Bool
}

struct ReadyRegistration: RegistrationState {
    let email: EmailAddress
}

struct Registration<State: RegistrationState>: Sendable {
    fileprivate let state: State
}

extension Registration where State == DraftRegistration {
    init(rawEmail: String, acceptedTerms: Bool) {
        state = DraftRegistration(rawEmail: rawEmail, acceptedTerms: acceptedTerms)
    }

    func validate() throws -> Registration<ReadyRegistration> {
        guard state.acceptedTerms else { throw RegistrationError.termsNotAccepted }
        return Registration<ReadyRegistration>(
            state: ReadyRegistration(email: try EmailAddress(state.rawEmail))
        )
    }
}

extension Registration where State == ReadyRegistration {
    var email: EmailAddress { state.email }
}
```

This pattern is useful when generic algorithms or shared storage justify one generic shell. Otherwise, use the simpler concrete transition:

```swift
struct RegistrationDraft {
    func validate() throws -> ValidRegistration
}

struct ValidRegistration {
    func submit() async throws -> SubmittedRegistration
}
```

### Typestate limits

Typestate is less suitable when:

- State changes repeatedly and must be stored heterogeneously.
- UI rendering switches over runtime state.
- The graph has many independent axes.
- Persistence must restore arbitrary states.
- Protocols or framework APIs erase the state immediately.
- Callers spend more effort naming generic combinations than understanding the domain.

An enum is often the right runtime state representation even when individual operations use state-specific helper types.

## Transition Design

A state transition should make ownership and failure explicit. A consuming method on an ordinary copyable struct does **not** prove single use: the caller may retain or create another copy. Use ordinary value semantics unless duplication is itself invalid.

When the compiler must reject reuse, combine a noncopyable state value with a consuming transition:

```swift
struct SingleUseRegistration<State: RegistrationState>: ~Copyable, Sendable {
    fileprivate let state: State

    fileprivate init(state: State) {
        self.state = state
    }
}

extension SingleUseRegistration where State == ReadyRegistration {
    consuming func submit(
        using client: RegistrationClient
    ) async throws -> Receipt {
        try await client.submit(email: state.email)
    }
}
```

This requires a complete destruction and error story. A fixed operation on a service that keeps the mutable state private is often simpler. An ordinary closure-scoped API can centralize sequencing and cleanup, but it does not prove that a copyable value was not retained or submitted elsewhere. If resubmission or inspection is valid, keep the type copyable and omit `consuming`.

Avoid a generic `transition(to:)` that accepts any state. Define only legal edges. For a transition that must return a usable prior state on failure, use [recovering workflows](domain-modeling-recipes.md#flow); that recipe owns success, recovery, cancellation, and completion obligations.

## Staged Builders

A conventional builder with optional fields moves missing-required-field errors to runtime:

```swift
struct RequestBuilder {
    var method: HTTPMethod?
    var url: URL?
}
```

Use staged concrete types when required order is small and stable:

```swift
struct EmptyRequestBuilder {
    func method(_ value: HTTPMethod) -> MethodRequestBuilder
}

struct MethodRequestBuilder {
    func url(_ value: URL) -> ReadyRequestBuilder
}

struct ReadyRequestBuilder {
    func build() -> URLRequest
}
```

Use phantom states when order is flexible but required-field combinations remain manageable. Do not use a result builder alone as proof that a required child appeared; result builders transform syntax, not arbitrary semantic constraints.

A validating final `build()` is often the best tradeoff for UI forms and dynamic configuration.

## Capability Tokens

A capability is a value required to perform an operation whose construction is restricted to a trusted issuer within the intended module and access-control boundary.

```swift
struct DeleteAccountCapability: Sendable {
    fileprivate let accountID: AccountID
    fileprivate init(accountID: AccountID) {
        self.accountID = accountID
    }
}

actor AuthorizationService {
    func authorizeDeletion(of accountID: AccountID) async throws -> DeleteAccountCapability {
        try await verifyCurrentSessionCanDelete(accountID)
        return DeleteAccountCapability(accountID: accountID)
    }
}

func deleteAccount(
    using capability: DeleteAccountCapability,
    client: AccountClient
) async throws {
    try await client.delete(capability.accountID)
}
```

The capability prevents ordinary call sites from passing `true` or constructing a mismatched account authorization. It does not replace server-side authorization.

### Scope capabilities narrowly

Bind relevant facts into the token:

- Subject/account ID.
- Permitted operation.
- Issuer or environment.
- Expiration or nonce when replay matters.

Do not create one global `AdminCapability` that silently authorizes every future operation.

### Revocation and time

A plain value cannot guarantee that authority remains valid after issuance. For revocable or time-sensitive permission:

- Keep the final check and protected mutation in one actor/service operation when possible.
- Store a token identifier and validate it at use.
- Treat ordinary closure scope as API structure, not proof that a copyable token cannot escape.
- Make expiration explicit and test clock behavior.

## Marker Protocols Are Forgeable by Default

This does not create an unforgeable proof:

```swift
public protocol Authorized {}
public func perform<T: Authorized>(_ value: T) { ... }
```

Any client can declare a conformance unless access control prevents it. Prefer:

- A concrete issuer-created capability with a nonpublic initializer.
- An internal protocol when the extension point is module-private.
- A public protocol only for behavioral extensibility; conformance alone must never grant authority. Carry the proof in a separate concrete token or validate it in the trusted service.
- Runtime validation by a trusted issuer when authority can expire, be revoked, or depend on external state.

A private protocol requirement does not generally produce a clean “sealed protocol” abstraction across public modules; use concrete wrappers when sealing matters.

## Trust and Taint States

Distinct types can prevent unsafe composition:

```swift
struct RawHTML: Sendable { let value: String }
struct SanitizedHTML: Sendable {
    fileprivate let value: String
}

struct HTMLSanitizer: Sendable {
    func sanitize(_ input: RawHTML) -> SanitizedHTML { ... }
}
```

Generic trust states reduce repetition:

```swift
struct Text<State>: Sendable {
    fileprivate let value: String
}

enum Untrusted {}
enum HTMLSanitized {}
enum SQLParameter {}
```

Use these only when operations genuinely differ by state. Do not imply that escaping for one context is safe for another: HTML text, HTML attributes, URLs, JavaScript, SQL, shell, and regex each have different rules.

Parameterized APIs are usually stronger than escaped-string APIs. For SQL, prefer bind parameters rather than a “sanitized SQL string.” For shell commands, prefer argument arrays and direct process APIs rather than concatenation.

## Generic Machinery: Escalate Deliberately

Phantom tags and typestate already rely on generics, but they rarely require a protocol hierarchy. Add protocols, associated types, existentials, type erasure, parameter packs, or macros only when an open implementation set or reusable static relationship justifies them.

For dispatch hazards, associated types, `some` versus `any`, conditional conformance, witness structs, packs, key paths, and macro audits, use [advanced generics and protocols](advanced-generics-and-protocols.md).

## Generic Explosion Control

Before adding a generic axis, ask:

1. Does it remove an actual invalid operation?
2. Will multiple algorithms remain generic over it?
3. Will it survive storage, framework, and module boundaries?
4. Is the state set stable?
5. Is the resulting diagnostic understandable?

If several answers are no, use an enum, concrete wrapper, or runtime validator.

Useful simplifications:

- Type aliases for common specializations, while remembering aliases do not add safety beyond the specialization.
- State payload types instead of multiple boolean phantom parameters.
- One generic trust axis rather than separate generic flags.
- Type erasure at a deliberate outer boundary.
- Concrete façade methods around generic internals.

## Review Checklist

- Are same-representation values that can be swapped nominally distinct?
- Are raw overloads preserving a bypass?
- Does a phantom tag represent identity rather than pretend to confer authority?
- Are tags and constructors sealed where privileged meaning requires it?
- Would separate concrete state types be simpler than typestate?
- Are only legal transitions defined?
- Is consuming a transition necessary?
- Does a builder prove required fields or merely validate at the end?
- Can clients forge a marker protocol or capability?
- Is trust context-specific?
- Are generic relationships preserved across protocols and erasure?
- Are macro-generated construction and conformances audited?
- Is each generic axis earning its complexity?
