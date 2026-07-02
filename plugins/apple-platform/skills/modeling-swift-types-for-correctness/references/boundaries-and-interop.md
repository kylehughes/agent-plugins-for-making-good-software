# Boundaries, Persistence, Notifications, and Interop

Use this reference when domain types meet JSON, databases, UserDefaults, notifications, Objective-C, C/C++, logging, public frameworks, or security-sensitive data.

## Boundary Principle

Keep permissive representations at the edge and strict representations in the core.

```text
foreign bytes or objects
    -> permissive raw shape
    -> parsing and validation
    -> canonical domain value
    -> explicit projection back outward
```

A raw DTO may contain optionals, strings, integer codes, and malformed combinations because it represents what arrived. A domain model should contain only states the application is prepared to use.

## Networking: DTO to Domain

```swift
struct UserDTO: Decodable {
    let id: String
    let displayName: String?
    let status: String
}

struct User: Sendable {
    let id: UserID
    let displayName: NonEmptyString?
    let status: UserStatus
}

extension User {
    init(dto: UserDTO) throws(UserMappingFailure) {
        guard let uuid = UUID(uuidString: dto.id) else { throw .invalidID(dto.id) }
        id = UserID(rawValue: uuid)

        if let name = dto.displayName {
            do { displayName = try NonEmptyString(name) }
            catch { throw .invalidDisplayName }
        } else {
            displayName = nil
        }

        status = UserStatus(serverValue: dto.status)
    }
}
```

The mapping layer can attach field names, payload identifiers, server version, and recovery policy without polluting the domain type.

### Unknown external cases

Choose among:

- Preserve `.unknown(rawValue)` for display or forward compatibility.
- Reject the object if unknown means behavior cannot be safe.
- Map to a conservative semantic such as `.unavailable` only when product policy defines it.

Never silently map every unknown status to an existing case merely to make a switch exhaustive.

## Typed Endpoints

Preserve request/response relationships without forcing transport details into domain values.

```swift
protocol Endpoint {
    associatedtype Request: Encodable & Sendable
    associatedtype Response: Decodable & Sendable
    associatedtype Failure: Error & Sendable

    var path: String { get }
    func makeBody(_ request: Request) throws(Failure) -> Data
    func decode(_ data: Data, response: HTTPURLResponse) throws(Failure) -> Response
}
```

The current Swift 6 baseline supports `throws(Failure)` directly. Use ordinary `throws` when transport failures are intentionally open-ended, then perform narrow error translation at the domain-service boundary.

Be cautious with public typed failure enums for network layers: servers, authentication, connectivity, decoding, and cancellation evolve independently. It is often better for the transport to throw broadly and for a domain service to map a narrow subset.

Model pagination and freshness explicitly when they matter:

```swift
struct Page<Item: Sendable, Cursor: Sendable>: Sendable {
    let items: [Item]
    let nextCursor: Cursor?
}

struct Cached<Value: Sendable>: Sendable {
    let value: Value
    let fetchedAt: Date
    let policy: FreshnessPolicy
}
```

Do not use an untyped string cursor for every endpoint if cursors are not interchangeable.

## Custom `Decodable`

A refined type's decoder must call its checked initializer.

Do not rely on:

- Private storage alone.
- A validating public initializer that synthesis does not invoke.
- “The server never sends that.”
- Encoding only valid values in the current app version.

For complex payloads, prefer DTO mapping over embedding transport field names and error policy into the domain model.

### Partial and lossy decoding

If an array may contain some invalid elements, choose explicitly:

- Fail the entire payload.
- Return valid values plus indexed issues.
- Quarantine invalid elements.
- Ignore invalid elements only with metrics/logging and a documented product policy.

Avoid generic “lossy decoding” helpers that silently erase data in security-, finance-, or user-content-sensitive paths.

## Persistence

Persistence records are another untrusted boundary. They may be stale, migrated, partially written, manually edited, or produced by older code.

### Core Data and SwiftData

Keep persistence-managed reference objects separate from immutable domain snapshots when practical.

```text
managed object / @Model
    -> mapper on the owning context or actor
    -> Sendable domain snapshot
```

Do not pass managed objects across actors merely because a generated type can be annotated. Use stable IDs and refetch on the correct context, or produce immutable snapshots.

SwiftData itself requires iOS 17+. This is independent of whether a domain newtype or enum can deploy to iOS 16.

### Schema migrations

When tightening an invariant:

1. Identify persisted values accepted by old versions.
2. Decide whether to transform, preserve under a legacy type, quarantine, or reject.
3. Make migration idempotent.
4. Test from every supported schema version.
5. Preserve rollback compatibility when releases may downgrade.

A new nonfailable domain initializer can turn historical data into a crash if migration is not considered.

## UserDefaults and Preferences

Use typed keys and validate decoded values.

```swift
struct DefaultsKey<Value> {
    let name: String
    let defaultValue: Value
}
```

A typed key does not by itself make the backing bytes valid. The store must define:

- Encode/decode strategy.
- Behavior for wrong-type or corrupt values.
- Migration of renamed keys.
- App-group/process synchronization.
- Main-actor or lock/actor isolation.
- Whether secrets are prohibited; UserDefaults is not a secret store.

## Notifications Across iOS 16–26

Foundation's typed `NotificationCenter.MainActorMessage` and `AsyncMessage` APIs are iOS 26+. Do not expose them unconditionally from a library that deploys to iOS 16.

Define one domain event and adapt both implementations:

```swift
struct AccountDidChange: Sendable {
    let accountID: AccountID
    let revision: Int
}

protocol AccountEventStream: Sendable {
    func events() -> AsyncStream<AccountDidChange>
}
```

An iOS 16–25 adapter can use `Notification.Name`, a private payload key set, and checked conversion. An iOS 26 adapter can use typed notification messages. Keep raw `Notification` and `userInfo` out of consumers.

Availability shape:

```swift
func makeAccountEventStream() -> any AccountEventStream {
    if #available(iOS 26, *) {
        return TypedNotificationAccountEventStream()
    } else {
        return LegacyNotificationAccountEventStream()
    }
}
```

Annotate the modern implementation type `@available(iOS 26, *)`. Ensure both paths define the same delivery ordering, isolation, buffering, and subject filtering semantics.

### Traditional notifications

For the fallback:

- Use a namespaced static `Notification.Name`.
- Centralize `userInfo` keys and conversion.
- Validate object and payload types.
- Specify delivery actor/queue.
- Tie observation lifetime to a token or async stream.
- Avoid global notifications when direct dependency or actor streams are clearer.

A typed notification still represents broadcast coupling; type safety does not make broadcasting the right architecture.

## Objective-C Interop

Objective-C boundaries can weaken Swift invariants through nullable references, `Any`, `NSNumber`, KVC/KVO, dynamic dispatch, and generated initializers.

Use an adapter:

```swift
@objc final class ObjCAccountAdapter: NSObject {
    @objc static func makeAccount(
        identifier: NSString,
        displayName: NSString?,
        error: NSErrorPointer
    ) -> ObjCAccount? {
        do {
            guard let uuid = UUID(uuidString: String(identifier)) else {
                throw ObjCBridgeFailure.invalidIdentifier
            }

            let validatedName = try displayName.map {
                try NonEmptyString(String($0))
            }
            let account = Account(
                id: AccountID(rawValue: uuid),
                displayName: validatedName
            )
            return ObjCAccount(account)
        } catch {
            error?.pointee = mapToNSError(error)
            return nil
        }
    }
}
```

The exact bridge should fit the project; the principle is to validate before constructing the Swift domain value.

Audit:

- `@objcMembers` accidentally exposing setters or initializers.
- `NSObject` subclasses whose invariants can be altered through KVC.
- `NSCopying` duplicating a logically unique resource.
- `NSSecureCoding` decoders bypassing checked paths.
- Nullability imported as implicitly unwrapped optionals.
- `NSNumber` ambiguity among Boolean and numeric values.
- `NSError` domain/code stability.

Prefer a separate Objective-C façade rather than weakening a pure Swift domain type.

## C and C++ Interop

Foreign pointers and handles require explicit ownership, lifetime, nullability, and thread-affinity rules.

For a C handle, record:

- Who creates and destroys it.
- Whether ownership is transferred, borrowed, or shared.
- Whether null is valid.
- Whether calls are thread-safe or thread-confined.
- Whether callbacks may outlive the Swift wrapper.
- Whether destruction can occur on any thread.
- What error convention is used.

A wrapper shape:

```swift
final class DatabaseHandle: @unchecked Sendable {
    private let raw: OpaquePointer
    private let lock: LockAdapter

    init(takingOwnershipOf raw: OpaquePointer) {
        self.raw = raw
        self.lock = LockAdapter()
    }

    deinit {
        close_database(raw)
    }
}
```

This is safe only if every operation is synchronized appropriately, the C library permits destruction as shown, callbacks cannot use the handle after deinit, and ownership was actually transferred. The annotation is not the proof.

Use noncopyable wrappers when duplicate ownership would double-close a resource. A closure can centralize owner lifetime and cleanup when static ownership machinery would overcomplicate the API, but an ordinary closure parameter does not by itself make a copyable handle or pointer statically nonescapable. Keep raw handles private or use a compiler-visible lifetime relationship when nonescape is part of the guarantee.

## Unsafe Pointers and Buffers

Keep unsafe operations in small wrappers with explicit preconditions. Validate:

- Binding and alignment.
- Initialized versus uninitialized memory.
- Capacity and index arithmetic.
- Owner lifetime.
- Mutability/exclusivity.
- Integer overflow in byte counts.
- Foreign callback escape.

A safe-looking `Span` or buffer view is not a license to ignore the originating allocation's lifetime or mutation rules.

## Analytics and Logging

String dictionaries are common at analytics boundaries, but domain code should construct typed events.

```swift
struct CheckoutCompleted: Sendable {
    let orderID: OrderID
    let amount: Money
    let itemCount: Int
}
```

One adapter converts the event to vendor keys and primitive values. This provides one place to enforce:

- Stable event names and schemas.
- Unit/currency formatting.
- Optional-field policy.
- PII and secret redaction.
- Cardinality limits.
- Versioning.

Do not make every analytics event conform to one protocol with a raw `[String: Any]` requirement if that simply spreads untyped dictionaries.

## Secrets and Sensitive Values

Use wrappers to prevent accidental display or logging:

```swift
struct Secret<Value>: Sendable where Value: Sendable {
    private let value: Value

    init(_ value: consuming Value) {
        self.value = value
    }

    func withValue<Result>(_ body: (borrowing Value) throws -> Result) rethrows -> Result {
        try body(value)
    }
}
```

The closure narrows routine access but does not prevent a copyable value from being returned or captured. Be conservative about custom `CustomStringConvertible`, `CustomDebugStringConvertible`, `Codable`, and `Hashable` conformances. A wrapper cannot guarantee zeroization for arbitrary Swift values or eliminate copies already made by strings, logging frameworks, crash reports, or foreign APIs.

Use Keychain or an appropriate secure storage mechanism; a nominal type alone does not secure storage.

## Public Libraries and ABI

Before changing a public model, determine whether library evolution is enabled and what clients compile against.

Consider:

- Public enum case additions.
- `@frozen` commitments.
- Struct layout and inlinable code.
- Generic constraints and conditional conformances.
- Actor isolation changes.
- `Sendable` changes under Swift 6 clients.
- Typed error case additions.
- Availability annotations.
- Changing a raw type or canonicalization.
- Exposing a new standard-library type unavailable on older deployment targets.

For a package compiled from source, source compatibility may dominate. For a binary framework, ABI and module stability also matter. Do not use `@frozen`, `@inlinable`, or `@usableFromInline` casually; they expose implementation choices.

## Availability Adapters

Keep modern and legacy implementations behind one stable domain protocol or façade.

Good:

```text
Domain API
  -> availability-selected adapter
      -> iOS 26 typed API
      -> iOS 16 legacy API
```

Weak:

```text
Every caller contains if #available and handles two payload models
```

Test semantic parity between paths. Availability is part of behavior, not only compilation.

## Review Checklist

- Is raw external data separated from the domain model?
- Does DTO mapping preserve field context and unknown-case policy?
- Does decoding call checked construction?
- Are lossy behaviors explicit and observable?
- Can historical persisted data satisfy tightened invariants?
- Are managed persistence objects kept on their owning isolation domain?
- Are UserDefaults values still validated despite typed keys?
- Are iOS 26 typed notifications hidden behind an iOS 16-compatible adapter?
- Do legacy and modern paths share ordering and isolation semantics?
- Does Objective-C exposure add setters or initializers that bypass the model?
- Are C ownership, lifetime, callback, and thread rules documented and enforced?
- Are unsafe buffer counts and lifetimes checked?
- Are analytics and logs typed before vendor conversion and redacted?
- Are public source, ABI, isolation, error, and availability changes identified?
