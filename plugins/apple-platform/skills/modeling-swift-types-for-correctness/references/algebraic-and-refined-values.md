# Algebraic and Refined Value Modeling

Use this reference for enums, correlated data, validated wrappers, collection invariants, units, money, intervals, canonicalization, and `Codable` design.

## Sum Types: Model Alternatives Directly

Use an enum when a value is exactly one of a finite set of variants.

```swift
enum AuthenticationState: Sendable {
    case anonymous
    case authenticating
    case authenticated(UserSession)
    case failed(AuthenticationFailure)
}
```

This is stronger than:

```swift
struct AuthenticationState {
    var isAuthenticated: Bool
    var isAuthenticating: Bool
    var session: UserSession?
    var error: AuthenticationFailure?
}
```

The struct permits contradictory booleans, a session while unauthenticated, and an error during success. The enum permits only named cases.

### Associated values bind correlated data

```swift
enum DownloadState: Sendable {
    case idle
    case downloading(progress: Double, resumeData: Data?)
    case complete(URL)
    case failed(DownloadFailure, resumeData: Data?)
}
```

Payloads exist only in the cases where they make sense. Avoid copying associated values into separate stored properties. The enum proves case/payload correlation, not every invariant inside a payload: `Double` still permits negative values, values above one, infinities, and `NaN`. Refine the payload type or validate at construction when those states are invalid.

### Derived convenience is fine

```swift
extension DownloadState {
    var isActive: Bool {
        if case .downloading = self { true } else { false }
    }
}
```

A computed property cannot drift. A stored `isActive` can.

### Avoid `default` for owned closed enums

When the module owns every case, exhaustive switches turn new cases into useful compiler errors. Use `@unknown default` for imported nonfrozen enums where a future case is possible.

For external string domains, preserve unknown values when forward compatibility matters:

```swift
enum ServerStatus: Equatable, Sendable {
    case pending
    case active
    case disabled
    case unknown(String)
}
```

Fail decoding instead when an unknown value means the payload is unsafe to use. Choose deliberately.

### Absence, removal, and structural cardinality

```swift
enum Patch<Value> {
    case unchanged
    case remove
    case set(Value)
}

struct NonEmpty<Element> {
    let head: Element
    let tail: [Element]

    func map<Output>(_ transform: (Element) -> Output) -> NonEmpty<Output> {
        NonEmpty<Output>(head: transform(head), tail: tail.map(transform))
    }

    func filter(_ keep: (Element) -> Bool) -> [Element] {
        ([head] + tail).filter(keep)
    }
}
```

`Patch` distinguishes unchanged, removed, and replaced values; serialization must retain all three cases. `NonEmpty` requires a head by construction. Mapping preserves its cardinality, while filtering returns an ordinary array because it may remove every element. Exposing an array setter would reopen the invariant. For collection adapters and mutation rules, see [collection invariants](#collection-invariants).

## Product Types: Bind Values That Form One Fact

A struct is a product: every stored property is present together.

```swift
struct PostalAddress: Hashable, Sendable {
    let street: NonEmptyString
    let locality: NonEmptyString
    let region: RegionCode
    let postalCode: PostalCode
}
```

Use a struct to replace parallel arrays, loosely related tuples, repeated parameter lists, and dictionaries with fixed keys.

### Do not store redundant facts casually

Avoid storing both:

- Array and count.
- Start, end, and duration.
- Enum state and matching booleans.
- Raw value and normalized value when one can be canonical storage.
- Child collection and a separately mutable summary.

If denormalization is required for performance, centralize mutation in one type or actor and test consistency as an invariant.

## Optional Is a Two-Case Sum Type

Use `Optional` when the only meaningful distinction is present versus absent and absence needs no reason.

Prefer a richer enum when `nil` conflates cases:

```swift
enum AvatarState: Sendable {
    case notRequested
    case loading
    case unavailable
    case image(ImageData)
    case failed(AvatarFailure)
}
```

Do not replace every optional with a custom enum. Optional remains the clearest model for ordinary absence.

## Validated Newtypes

A refined value wraps a raw representation and only exposes values that passed validation.

```swift
enum NonEmptyStringError: Error, Equatable, Sendable {
    case empty
    case tooLong(maximum: Int)
}

struct NonEmptyString: Hashable, Sendable {
    static let maximumLength = 200

    private let storage: String

    init(_ raw: String) throws(NonEmptyStringError) {
        let canonical = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !canonical.isEmpty else { throw .empty }
        guard canonical.count <= Self.maximumLength else {
            throw .tooLong(maximum: Self.maximumLength)
        }
        storage = canonical
    }

    var value: String { storage }
}
```

The bound is part of this type's fixed meaning, so callers cannot select a weaker policy than decoding uses. State the unit of every string bound: `String.count` measures extended grapheme clusters, while protocols and storage systems may constrain Unicode scalars, UTF-8 bytes, or another encoded representation. Canonicalize first, then measure the representation the external contract actually limits. If limits differ by field, define separate domain types/policies or make the policy explicit in the surrounding validator rather than pretending one type has one guarantee. The current Swift 6 baseline supports the typed-throws spelling; use it only when the closed failure set improves callers.

The checked initializer proves only what its implementation and access control preserve. For a struct, a custom initializer declared in the primary type body suppresses the synthesized memberwise initializer; an initializer declared only in an extension preserves memberwise synthesis. Confirm which declarations exist before reporting a memberwise bypass. A visible `let` property permits reading, not post-initialization assignment. These rules do not suppress synthesized `Decodable`, which is a separate construction path.

Audit all construction and mutation routes with the [skill construction checklist](../SKILL.md#close-swift-construction-and-mutation), including canonicalization and reference-backed storage.

### Keep editable input separate

```swift
struct NonblankLabel {
    let text: String

    init?(_ text: String) {
        guard text.contains(where: { !$0.isWhitespace }) else { return nil }
        self.text = text
    }
}

// Editable input remains a legitimate separate representation.
struct LabelDraft { var text: String }
```

Successful construction retains the checked input; a boolean validation result does not. A read-only primitive projection discards evidence for downstream calls without mutating the wrapper. A writable projection or referenced class can reopen it. For cross-field policies and rule-indexed values, use [compound refinement decisions](domain-modeling-recipes.md#val).

### Validation versus canonicalization

Validation rejects invalid input. Canonicalization maps multiple acceptable representations to one stored form. They are related but not interchangeable.

Examples:

- Trim UI whitespace before creating a display name.
- Lowercase an ASCII-only protocol token when the protocol defines case insensitivity.
- Do not lowercase arbitrary user identifiers using a locale-sensitive transform unless the domain specifies it.
- Normalize Unicode only when equality and interoperability rules demand a specific normalization form.
- Preserve original presentation separately when round-tripping matters.

Name policy explicitly when reasonable teams could choose differently:

```swift
struct EmailAddress {
    enum CanonicalizationPolicy { case preserve, lowercaseDomain }
}
```

Do not pretend that a simplistic regex fully validates a complex internet standard. Model the guarantee you actually provide, such as “nonempty address-like input accepted by our backend.”

## Failable, Throwing, or Result-Producing Construction

### Failable initializer

Use `init?` when failure needs no diagnostics and the validation is simple.

```swift
struct Percentage: Hashable, Sendable {
    let value: Double

    init?(_ value: Double) {
        guard value.isFinite, (0...100).contains(value) else { return nil }
        self.value = value
    }
}
```

### Throwing initializer

Use when callers need a reason, field context, or localized mapping.

### `Result` or accumulating validation

Use when validation is stored, transformed, composed, or must report all failures instead of stopping at the first.

Do not expose several construction forms without a reason. One obvious checked path is easier to audit.

## `RawRepresentable` Is Not Automatic Safety

This is safe only if `init(rawValue:)` enforces the invariant or raw construction is intentionally unrestricted.

```swift
struct FeatureName: RawRepresentable, Hashable, Sendable {
    let rawValue: String

    init?(rawValue: String) {
        guard !rawValue.isEmpty else { return nil }
        self.rawValue = rawValue
    }
}
```

Be aware that adopting `RawRepresentable` advertises raw conversion as a central semantic. For many domain values, an ordinary `init(_:)` and `value` property are clearer.

## String-Literal Conformance Cannot Report Validation Failure

`ExpressibleByStringLiteral.init(stringLiteral:)` is nonthrowing. Therefore use literal conformance only when:

- Every string literal is valid by definition.
- A macro validates literals at compile time.
- Invalid literals intentionally trap and that policy is acceptable.

Do not add it merely for prettier call sites on a fallibly validated type.

## Collection Invariants

### Nonempty collection

```swift
struct NonEmptyArray<Element> {
    private var storage: [Element]

    init(head: Element, tail: [Element] = []) {
        storage = [head] + tail
    }

    init?(_ elements: [Element]) {
        guard !elements.isEmpty else { return nil }
        storage = elements
    }

    var first: Element { storage[0] }
    var elements: [Element] { storage }
}
```

Do not expose mutation such as `removeAll()` that can violate nonemptiness. Provide operations whose result type reflects possible emptiness, or reject the final removal.

### Bounded collection

```swift
struct BoundedArray<Element> {
    let elements: [Element]
    let limit: ClosedRange<Int>

    init(_ elements: [Element], limit: ClosedRange<Int>) throws {
        guard limit.contains(elements.count) else { throw CardinalityError.outOfRange }
        self.elements = elements
        self.limit = limit
    }
}
```

When the bounds are domain constants, put them in the type's implementation rather than storing a caller-selected range. When bounds vary at runtime, they cannot generally be encoded as Swift type parameters.

### Sorted or unique collection

Decide whether construction:

- Rejects unsorted or duplicate input.
- Canonicalizes by sorting/deduplicating.
- Preserves first occurrence or last occurrence.
- Uses a comparator or identity policy.

Expose mutation only through operations that preserve the chosen semantics.

### Fixed cardinality versus fixed layout

A business invariant such as exactly three coordinates does not require `InlineArray`.

```swift
struct Triangle<Vertex> {
    let a: Vertex
    let b: Vertex
    let c: Vertex
}
```

This is available on all deployment targets and gives fields meaning. Use `InlineArray` only when its contiguous inline layout or generic fixed count is valuable and iOS 26+ availability is acceptable or isolated.

## Numeric Bounds and Floating-Point Traps

Always decide how to treat:

- `NaN`.
- Positive and negative infinity.
- Signed zero when it matters.
- Overflow and underflow.
- Closed versus half-open bounds.
- Unit conversion and rounding.

```swift
struct UnitInterval: Hashable, Sendable {
    let value: Double

    init(_ value: Double) throws {
        guard value.isFinite, (0...1).contains(value) else {
            throw UnitIntervalError.outOfRange
        }
        self.value = value
    }
}
```

Clamping and validation are different APIs. Name clamping explicitly; do not silently clamp in an initializer whose callers expect rejection.

## Intervals and Ordering

```swift
struct DateIntervalValue: Hashable, Sendable {
    let start: Date
    let end: Date

    init(start: Date, end: Date) throws {
        guard start <= end else { throw IntervalError.reversed }
        self.start = start
        self.end = end
    }

    var duration: TimeInterval { end.timeIntervalSince(start) }
}
```

Decide whether zero-length intervals are valid. Decide whether endpoints are closed, open, or half-open for discrete domains. Use domain names such as `SubscriptionPeriod` when those semantics matter more than generic reuse.

## Money

Do not use binary floating point for exact monetary amounts unless the domain explicitly tolerates approximation.

A practical model often stores minor units and currency:

```swift
struct Money: Hashable, Sendable {
    let minorUnits: Int64
    let currency: CurrencyCode
}
```

Model and test:

- Currency scale and rounding policy.
- Overflow.
- Whether different currencies can be compared or added.
- Locale is presentation, not identity.
- Exchange rates have source, timestamp, and direction.

Do not overload `+` across currencies with an implicit conversion.

## Units and Dimensions

Nominal wrappers are often enough:

```swift
struct Meters: Hashable, Sendable { let value: Double }
struct Seconds: Hashable, Sendable { let value: Double }
```

A generic quantity reduces repetition:

```swift
struct Quantity<Unit, Scalar>: Sendable where Scalar: Sendable {
    let value: Scalar
}

enum MeterUnit {}
enum SecondUnit {}

typealias Distance = Quantity<MeterUnit, Double>
typealias DurationValue = Quantity<SecondUnit, Double>
```

Do not build a full dimensional-analysis system unless multiplication, division, exponentiation, and generic algorithms need it. Explicit conversion functions are usually clearer for app code.

## Dates, Time Zones, and Calendars

`Date` is an instant, not a civil date, local time, or calendar component set. Use separate types for:

- Instant in time.
- Calendar date.
- Local wall-clock time.
- Zoned date-time.
- Recurrence rule.
- Duration versus calendar offset.

Do not derive identity from a formatted localized string. Inject calendar, locale, and time zone into parsing/presentation policies where reproducibility matters.

## `Codable` and Refined Types

Synthesized `Decodable` is safe only when synthesized initialization cannot bypass the invariant. Private stored properties do not by themselves guarantee this; synthesis has access inside the type.

Choose the container from the existing wire contract, not from the number of stored properties. For an existing synthesized keyed shape such as `{"storage":"name"}`, preserve that shape while adding validation:

```swift
extension NonEmptyString: Codable {
    private enum CodingKeys: String, CodingKey {
        case storage
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let raw = try container.decode(String.self, forKey: .storage)
        do {
            try self.init(raw)
        } catch {
            throw DecodingError.dataCorruptedError(
                forKey: .storage,
                in: container,
                debugDescription: "Expected a nonempty string within the type's fixed maximum length."
            )
        }
    }
}
```

Use `singleValueContainer()` only when the established format is a scalar, with matching encoding. Changing keyed data to a scalar is a schema migration, not a validation fix. Exercise historical valid payloads, round trips, and syntactically valid invalid values that fail at the intended predicate.

When server payloads need field-specific errors, decode a DTO first and map into the domain model with context. Do not leak `DecodingError` or raw backend strings through every domain layer unless that is intentional.

### Versioned persistence

A previously valid value may become invalid after rules change. Decide among:

- Keep old rules for persisted schema versions.
- Migrate to a new canonical form.
- Quarantine and request user correction.
- Treat corruption as recoverable and discard cache data.

Never assume that “we only encode valid values” proves all future decoded bytes are valid.

## Hashing and Equality

Use the [public contract laws](domain-modeling-recipes.md#equality-and-hashing) when choosing identity, canonical storage, and hash-key mutation rules.

## Public API Resilience

Use [public evolution](domain-modeling-recipes.md#public-evolution) when changing enum cases, layout, validation, canonicalization, or unchecked construction.

## Review Checklist

Use the [Swift checklist](../SKILL.md#checklist) for boundary closure and evidence; use [public contracts](domain-modeling-recipes.md#api) for equality, evolution, and conformance obligations.
