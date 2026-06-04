# Algebraic and Value Modeling

This reference expands the core enum and struct patterns from `REFERENCE.md`. Use it when the shape of the data is already known, but the current model still allows incoherent combinations, forged values, stale derived fields, or boundary data to leak into the core.

The working rule is simple: raw data exists at boundaries; refined values exist in the domain. A type proves an invariant only when invalid construction is impossible through the visible API.

---

## Algebraic Data Modeling

Algebraic data modeling uses **sum types** (`enum`) for alternatives and **product types** (`struct`) for values that exist together. Count the representable states before choosing a shape.

```swift
// 16 representable states. Most are invalid.
struct RequestState<Value> {
    var isLoading: Bool
    var isRefreshing: Bool
    var value: Value?
    var error: Error?
}
```

Replace boolean axes with cases when the axes are not independent.

```swift
enum RequestState<Value, Failure: Error> {
    case idle
    case loading
    case loaded(Value)
    case refreshing(stale: Value)
    case failed(Failure)
}
```

Derived booleans are fine. Stored booleans that duplicate enum state are not.

```swift
extension RequestState {
    var isLoading: Bool {
        switch self {
        case .loading, .refreshing:
            true
        case .idle, .loaded, .failed:
            false
        }
    }
}
```

### Beyond Boolean Flags

Prefer enums over:

- Status strings: `"loading"`, `"loaded"`, `"error"`.
- Integer modes: `0`, `1`, `2`.
- `Bool?` where `nil` means "unknown" and `false` means "disabled".
- Sentinel payloads such as `error = nil` meaning success.
- Structs where exactly one optional must be present.

```swift
// Wrong but tempting: every consumer must rediscover the invariant.
struct PaymentResult {
    var receipt: Receipt?
    var failureMessage: String?
}

// Better: the compiler knows success and failure are exclusive.
enum PaymentResult {
    case succeeded(Receipt)
    case failed(message: String)
}
```

### Nested Enums

Use nested state when one finite axis is meaningful only inside another finite state. This avoids a flat cross-product enum with repeated payloads.

```swift
enum ConnectionState {
    case disconnected(reason: DisconnectReason?)
    case connecting
    case connected(ConnectedState)

    enum ConnectedState {
        case loadingProfile
        case ready(Profile)
        case refreshing(stale: Profile)
    }
}
```

If two axes truly vary independently, keep them as two fields.

```swift
struct ScreenState {
    var connection: ConnectionState
    var selectedTab: Tab
}
```

### Enum, Separate Structs, Phantom State

Use one enum when callers inspect state centrally.

```swift
enum UploadState {
    case idle
    case uploading(progress: Double)
    case completed(URL)
    case failed(UploadError)
}
```

Use separate structs when each state has distinct operations.

```swift
struct DraftUpload {
    func start() -> ActiveUpload { ActiveUpload() }
}

struct ActiveUpload {
    func cancel() -> DraftUpload { DraftUpload() }
}
```

Use phantom state when storage is mostly identical but operations differ by phase.

```swift
enum Unvalidated {}
enum Validated {}

struct Form<State> {
    private let fields: [FieldID: String]
}

extension Form where State == Unvalidated {
    func validate() throws(ValidationError) -> Form<Validated> {
        // Validate all fields.
        Form<Validated>(fields: fields)
    }
}

func submit(_ form: Form<Validated>) async throws(SubmitError) {
    // An unvalidated form cannot be passed here.
}
```

Use `~Copyable` typestate when transitions are irreversible or double-use is a resource bug.

### Recursive and Indirect Enums

Use recursive enums for trees, ASTs, route graphs, workflows, and JSON-like data.

```swift
indirect enum Expression {
    case integer(Int)
    case add(Expression, Expression)
    case multiply(Expression, Expression)
}
```

Keep recursion shallow or boxed deliberately when values can be large. `indirect` adds allocation; it trades stack safety and representability for heap nodes.

### Public Enum Resilience

Internal enums owned by the module should be switched exhaustively without `default`.

```swift
switch state {
case .idle:
    renderIdle()
case .loading:
    renderLoading()
case .loaded(let value):
    render(value)
}
```

When the enum is public API, decide whether adding a case is a source-breaking change.

- Use a closed public enum when clients must handle every case and adding a case should break source.
- Use a resilient public enum when the library needs room to add cases.
- Use `@unknown default` when switching over resilient external enums.
- Avoid `default` for enums owned by the same module; it hides missing cases.

For server-provided finite strings, model forward compatibility explicitly.

```swift
enum SubscriptionStatus: Equatable, Sendable {
    case active
    case canceled
    case trialing
    case unknown(String)

    init(rawServerValue: String) {
        switch rawServerValue {
        case "active":
            self = .active
        case "canceled":
            self = .canceled
        case "trialing":
            self = .trialing
        default:
            self = .unknown(rawServerValue)
        }
    }
}
```

Failing decode is correct for corrupt data. Preserving `.unknown(String)` is correct when the server can roll out new cases before the client updates.

### Never and Uninhabited Types

Use `Never` when a generic axis exists but a value cannot occur.

```swift
typealias InfallibleLoad<Value> = LoadState<Value, Never>
typealias NonThrowingResult<Value> = Result<Value, Never>

func cachedProfile() throws(Never) -> Profile {
    Profile.fixture
}
```

`throws(Never)` is equivalent to nonthrowing at the call site. It matters in generic APIs that preserve a failure axis.

```swift
struct Parser<Input, Output, Failure: Error> {
    let parse: (Input) throws(Failure) -> Output
}

let integerDescription = Parser<Int, String, Never> { input in
    String(input)
}
```

Use empty enums as uninhabited tags.

```swift
enum UserIDTag {}
enum WorkspaceIDTag {}

struct ID<Tag>: RawRepresentable, Hashable, Sendable {
    let rawValue: String
}
```

The tag being uninhabited does not make the wrapper unforgeable. Access control does.

```swift
// Wrong but tempting: any caller can forge this token.
struct AccessToken {
    let rawValue: String
}

// Better: only this module can create a token.
struct AccessToken {
    private let rawValue: String

    fileprivate init(verified rawValue: String) {
        self.rawValue = rawValue
    }
}
```

### OptionSet, Enum, Struct of Booleans

Use `enum` for mutually exclusive states.

```swift
enum SelectionMode {
    case none
    case single(ItemID)
    case multiple(Set<ItemID>)
}
```

Use `OptionSet` for independently combinable flags.

```swift
struct ExportOptions: OptionSet {
    let rawValue: Int

    static let includeHeaders = ExportOptions(rawValue: 1 << 0)
    static let compress = ExportOptions(rawValue: 1 << 1)
    static let encrypt = ExportOptions(rawValue: 1 << 2)
}
```

Use a struct of booleans when flags are independent and names matter more than set algebra.

```swift
struct DebugOverlays {
    var showsLayoutBounds: Bool
    var showsHitRegions: Bool
    var showsRenderStats: Bool
}
```

Do not use `OptionSet` to encode exclusive states.

```swift
// Wrong: this permits [.loading, .failed].
struct LoadFlags: OptionSet {
    let rawValue: Int
    static let loading = LoadFlags(rawValue: 1 << 0)
    static let failed = LoadFlags(rawValue: 1 << 1)
    static let loaded = LoadFlags(rawValue: 1 << 2)
}
```

### State and Action Transitions

A reducer-style model makes transition coverage explicit.

```swift
enum LoadState<Value, Failure: Error> {
    case idle
    case loading
    case loaded(Value)
    case failed(Failure)
}

enum LoadAction<Value, Failure: Error> {
    case start
    case succeed(Value)
    case fail(Failure)
    case retry
}

func reduce<Value, Failure>(
    state: LoadState<Value, Failure>,
    action: LoadAction<Value, Failure>
) -> LoadState<Value, Failure> {
    switch (state, action) {
    case (.idle, .start), (.failed, .retry):
        .loading
    case (.loading, .succeed(let value)):
        .loaded(value)
    case (.loading, .fail(let error)):
        .failed(error)
    case (.idle, .retry), (.loaded, .start), (.loaded, .retry), (.failed, .start),
         (.idle, .succeed), (.idle, .fail), (.loading, .start), (.loading, .retry),
         (.loaded, .succeed), (.loaded, .fail), (.failed, .succeed), (.failed, .fail):
        state
    }
}
```

This is total because every `(State, Action)` pair returns a state. It still permits invalid actions at runtime; it handles them consistently. If invalid transitions must be impossible to call, split the states into distinct types and expose only valid methods.

```swift
struct IdleRequest {
    func start() -> LoadingRequest { LoadingRequest() }
}

struct LoadingRequest {
    func succeed(_ value: Response) -> LoadedRequest { LoadedRequest(value: value) }
    func fail(_ error: LoadError) -> FailedRequest { FailedRequest(error: error) }
}

// IdleRequest has no succeed method.
```

### Case Focusing

When a codebase repeatedly extracts associated values, centralize the focus instead of scattering `if case let`.

```swift
extension LoadState {
    var loadedValue: Value? {
        guard case .loaded(let value) = self else { return nil }
        return value
    }
}
```

For larger SwiftUI or reducer architectures, case paths or prisms can make enum payload access composable. The invariant remains the same: focus on a case without weakening the enum into loosely related optionals.

---

## Product and Value Modeling

A product type is correct when every stored field is valid in every instance. If some fields are only valid together in certain modes, the type is not a product; use an enum or split the type.

### Access Control Enforces Invariants

Validation belongs at construction. Keep stored properties private when raw mutation would break invariants.

```swift
struct EmailAddress: Hashable, Sendable {
    private let normalizedValue: String

    init(_ rawValue: String) throws(ValidationError) {
        let normalized = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
        guard normalized.contains("@") else {
            throw .invalidEmail
        }
        self.normalizedValue = normalized
    }
}
```

`private(set)` protects assignment from outside the type, but methods inside the type can still desynchronize fields. Private storage plus small mutation APIs is stronger.

### Memberwise Initializer Hazards

The synthesized memberwise initializer can bypass validation inside the module when validation lives outside the primary type declaration.

```swift
struct Percentage {
    let value: Double
}

extension Percentage {
    init(_ value: Double) throws {
        guard (0...1).contains(value) else { throw ValidationError.outOfRange }
        self.value = value
    }
}

let invalid = Percentage(value: 3) // Compiles inside the module through the memberwise initializer.
```

Suppress the hazardous memberwise initializer by using private storage or defining the validating initializer in the primary type declaration.

```swift
struct Percentage {
    private let value: Double

    init(_ value: Double) throws {
        guard value.isFinite, (0...1).contains(value) else {
            throw ValidationError.outOfRange
        }
        self.value = value
    }
}

// let invalid = Percentage(value: 3)
// Does not compile: 'Percentage' has no accessible initializer named 'init(value:)'.
```

### Canonicalization

Normalize once at construction. Do not spread `lowercased()`, trimming, sorting, clamping, or rounding across call sites.

```swift
struct CurrencyCode: RawRepresentable, Hashable, Codable, Sendable {
    let rawValue: String

    init?(rawValue: String) {
        let canonical = rawValue.trimmingCharacters(in: .whitespacesAndNewlines).uppercased()
        guard canonical.count == 3, canonical.allSatisfy(\.isLetter) else {
            return nil
        }
        self.rawValue = canonical
    }
}
```

Canonicalize:

- Emails and usernames according to product rules.
- Names by trimming, not by changing user-visible casing unless the domain owns that rule.
- Ranges by sorting endpoints when order is not semantically meaningful.
- URLs by resolving relative components at the boundary.
- Currency and locale codes by fixed casing.
- Decimal values by rounding to the domain precision.

### Single Source of Truth

Derive values that can be computed from stored fields.

```swift
// Wrong: count can disagree with items.
struct Section {
    var count: Int
    var items: [Item]
}

// Better.
struct Section {
    var items: [Item]

    var count: Int { items.count }
    var isEmpty: Bool { items.isEmpty }
}
```

Avoid storing:

- `count` beside a collection.
- `isEmpty` beside contents.
- `duration` beside `start` and `end`.
- `isValid` beside raw fields.
- `selectedIndex` beside `selectedID` unless both are independently needed and reconciled.

Store duplicated data only when it is a cache with explicit invalidation rules.

### Equality, Hashing, Entity, and Value

Use value semantics when equality means all significant fields are equal.

```swift
struct PostalAddress: Hashable, Sendable {
    var city: String
    var line1: String
    var postalCode: String
}
```

Use entity identity when equality means "same domain object" even if attributes differ.

```swift
struct User: Identifiable, Sendable {
    let id: UserID
    var displayName: String

    static func == (lhs: User, rhs: User) -> Bool {
        lhs.id == rhs.id
    }

    func hash(into hasher: inout Hasher) {
        hasher.combine(id)
    }
}
```

Synthesized `Equatable` and `Hashable` are wrong when the domain has custom equality. Normalize first when equality is case-insensitive or precision-limited.

Use:

- `struct` for immutable values and snapshots.
- `final class` for identity with reference semantics.
- `actor` for concurrent identity with isolated mutation.
- Sendable snapshots when crossing isolation or module boundaries.

### Codable Invariants

Synthesized `Decodable` can bypass intended construction when stored properties expose raw values or memberwise construction is available. Decode into raw DTOs at the boundary, then refine.

```swift
private struct UserDTO: Decodable {
    var email: String
    var id: String
}

struct User: Sendable {
    let email: EmailAddress
    let id: UserID

    init(dto: UserDTO) throws(ValidationError) {
        guard let id = UserID(rawValue: dto.id) else {
            throw .invalidID
        }
        self.id = id
        self.email = try EmailAddress(dto.email)
    }
}
```

When the domain type itself conforms to `Decodable`, implement `init(from:)` and call the validating initializer.

```swift
extension EmailAddress: Decodable {
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        let rawValue = try container.decode(String.self)
        do {
            try self.init(rawValue)
        } catch {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Invalid email address."
            )
        }
    }
}
```

Preserve unknown external enum cases when forward compatibility matters.

### Literal and RawRepresentable Caveats

`ExpressibleByStringLiteral` cannot fail. Do not use it for validated values unless a macro checks literals at compile time or the conformance is restricted to tests/internal fixtures.

```swift
// Wrong for production validation: invalid literals still compile.
extension EmailAddress: ExpressibleByStringLiteral {
    init(stringLiteral value: String) {
        try! self.init(value)
    }
}
```

`RawRepresentable` is useful for bridging and persistence, but `init(rawValue:)` must validate or be inaccessible.

```swift
struct FeatureFlag: RawRepresentable, Hashable, Sendable {
    let rawValue: String

    init?(rawValue: String) {
        guard rawValue.allSatisfy({ $0.isLetter || $0 == "." }) else {
            return nil
        }
        self.rawValue = rawValue
    }
}
```

Public unrestricted raw initializers turn wrappers into typealiases with extra syntax.

### Non-Empty and Bounded Values

Use non-empty wrappers when an empty collection is a different state, not a valid value.

```swift
struct NonEmptyArray<Element>: RandomAccessCollection {
    private var storage: [Element]

    init?(_ elements: [Element]) {
        guard !elements.isEmpty else { return nil }
        self.storage = elements
    }

    var startIndex: Int { storage.startIndex }
    var endIndex: Int { storage.endIndex }

    subscript(position: Int) -> Element {
        storage[position]
    }
}
```

Use this for validation errors, recipients, selected items, permissions, and form sections.

```swift
struct ValidationErrors: Error, Sendable {
    let errors: NonEmptyArray<ValidationError>
}
```

Use bounded wrappers for numeric constraints.

```swift
struct PositiveInt: RawRepresentable, Hashable, Sendable {
    let rawValue: Int

    init?(rawValue: Int) {
        guard rawValue > 0 else { return nil }
        self.rawValue = rawValue
    }
}

struct Probability: RawRepresentable, Hashable, Sendable {
    let rawValue: Double

    init?(rawValue: Double) {
        guard rawValue.isFinite, (0...1).contains(rawValue) else { return nil }
        self.rawValue = rawValue
    }
}
```

Common bounded values:

- Positive, nonnegative, nonzero integers.
- Finite doubles.
- Percentages and probabilities.
- Timeout and retry counts.
- Page sizes.
- Closed intervals.
- Date intervals with sorted endpoints.

### Typed Ranges

Use domain-specific interval types when raw `Range` semantics are easy to misread.

```swift
struct DateIntervalValue: Hashable, Sendable {
    let start: Date
    let end: Date

    init(start: Date, end: Date) throws {
        guard start <= end else { throw ValidationError.invalidRange }
        self.start = start
        self.end = end
    }

    var duration: TimeInterval {
        end.timeIntervalSince(start)
    }
}
```

Choose `Range` for half-open indexes and `ClosedRange` for inclusive domain values. Do not use a raw range when empty ranges, sorted endpoints, or inclusive/exclusive behavior are domain-significant.

### Typed Indices and Keys

Raw `Int` indices are easy to cross between sections, rows, arrays, and generations.

```swift
struct RowIndex: RawRepresentable, Hashable, Sendable {
    let rawValue: Int

    init?(rawValue: Int) {
        guard rawValue >= 0 else { return nil }
        self.rawValue = rawValue
    }
}

struct SectionIndex: RawRepresentable, Hashable, Sendable {
    let rawValue: Int
}

func select(row: RowIndex, in section: SectionIndex) {}

// select(row: SectionIndex(rawValue: 0), in: RowIndex(rawValue: 2)!)
// Does not compile: cannot convert 'SectionIndex' to expected 'RowIndex'.
```

IDs are usually safer than indices after mutation. Use generation-checked indices only when index identity is tied to a specific collection snapshot.

Use typed keys for heterogeneous storage.

```swift
struct Key<Value>: Hashable, Sendable {
    let name: String
}

struct SettingsStore {
    private var storage: [String: Any] = [:]

    subscript<Value>(key: Key<Value>) -> Value? {
        get { storage[key.name] as? Value }
        set { storage[key.name] = newValue }
    }
}

extension Key where Value == Bool {
    static let hasSeenOnboarding = Key<Bool>(name: "hasSeenOnboarding")
}
```

This pattern applies to UserDefaults, environment values, feature flags, analytics properties, notification payloads, localization keys, and dictionaries that would otherwise become `[String: Any]`.

### Weak and Unowned Semantics

Ownership is part of the model. Avoid optional weak fields that mean only "maybe alive" without saying what relationship is being represented.

```swift
struct Weak<Object: AnyObject> {
    weak var object: Object?
}
```

Use `Weak<T>` for observer lists and caches where disappearance is normal. Use `unowned` only when the parent outlives the child by construction and a crash is preferable to silently ignoring a broken invariant.

```swift
final class Child {
    private unowned let parent: Parent

    init(parent: Parent) {
        self.parent = parent
    }
}
```

If the relationship can end independently, model that state directly instead of relying on an implicitly nil weak reference.

---

## Domain Recipe Cards

These recipes are starting points. Keep the proof boundary narrow: raw input enters, construction validates or canonicalizes it, and the rest of the program accepts the refined type.

### Loading, Refresh, and Pagination

Model initial load, refresh, stale data, page load, and terminal failures separately.

```swift
enum PagedLoadState<PageValue, Cursor, Failure: Error> {
    case notRequested
    case loadingFirstPage
    case loaded(items: [PageValue], next: Cursor?)
    case refreshing(staleItems: [PageValue], next: Cursor?)
    case loadingNextPage(items: [PageValue], cursor: Cursor)
    case failed(Failure)
    case failedWithStaleData(Failure, staleItems: [PageValue], next: Cursor?)
}
```

Use typed cursors so a cursor for one resource cannot be reused for another.

```swift
struct Cursor<Resource>: RawRepresentable, Hashable, Sendable {
    let rawValue: String
}

typealias UserCursor = Cursor<User>
typealias WorkspaceCursor = Cursor<Workspace>
```

Wrong but tempting:

```swift
struct PaginationState {
    var cursor: String?
    var hasMore: Bool
    var isLoading: Bool
    var items: [Item]
}
```

This permits `hasMore == false` with a non-nil cursor and `isLoading == true` with no way to know whether the first page or next page is loading.

### Forms

Separate editing, validating, submitting, submitted, and failed states. Use accumulated validation errors when the UI should show all field problems at once.

```swift
enum FormState<Fields, Output, Failure: Error> {
    case editing(Fields)
    case invalid(Fields, NonEmptyArray<ValidationError>)
    case validating(Fields)
    case submitting(Validated<Fields>)
    case submitted(Output)
    case failed(Validated<Fields>, Failure)
}

struct Validated<Value>: Sendable where Value: Sendable {
    let value: Value
}
```

Make `Validated` construction internal to the validation pipeline.

```swift
struct FormValidator<Fields> {
    func validate(_ fields: Fields) -> Result<Validated<Fields>, NonEmptyArray<ValidationError>> {
        // Accumulate all errors, then produce Validated only on success.
    }
}
```

### Navigation Routes, Sheets, and Alerts

Use route enums with typed payloads instead of string paths and loosely typed dictionaries.

```swift
enum AppRoute: Hashable {
    case inbox
    case userDetail(UserID)
    case workspaceSettings(WorkspaceID)
}

enum SheetRoute: Identifiable {
    case editProfile(UserID)
    case shareDocument(DocumentID)

    var id: String {
        switch self {
        case .editProfile(let id):
            "editProfile:\(id)"
        case .shareDocument(let id):
            "shareDocument:\(id)"
        }
    }
}

enum AlertState {
    case discardDraft(confirm: () -> Void)
    case deleteDocument(DocumentID, confirm: () -> Void)
}
```

For SwiftUI `NavigationPath`, keep type erasure at the UI boundary. Store typed routes in domain state when possible.

Wrong but tempting:

```swift
var activeSheetName: String?
var selectedUserID: String?
var selectedDocumentID: String?
```

This permits `activeSheetName == "editProfile"` with a document ID.

### Money and Currency

Do not use `Double` for money. Model amount precision and currency explicitly.

```swift
struct Currency<Tag>: Hashable, Sendable {
    let code: CurrencyCode
}

enum USDTag {}
enum EURTag {}

typealias USD = Currency<USDTag>
typealias EUR = Currency<EURTag>

struct Money<CurrencyTag>: Hashable, Sendable {
    private let minorUnits: Int64

    init(minorUnits: Int64) {
        self.minorUnits = minorUnits
    }

    static func + (lhs: Money<CurrencyTag>, rhs: Money<CurrencyTag>) -> Money<CurrencyTag> {
        Money<CurrencyTag>(minorUnits: lhs.minorUnits + rhs.minorUnits)
    }
}

let usd = Money<USDTag>(minorUnits: 100)
let eur = Money<EURTag>(minorUnits: 100)
// let total = usd + eur
// Does not compile: currency tags differ.
```

Represent exchange rates as typed conversions.

```swift
struct ExchangeRate<SourceCurrency, TargetCurrency> {
    let decimalMultiplier: Decimal

    func convert(_ source: Money<SourceCurrency>) -> Money<TargetCurrency> {
        // Apply rounding rules for TargetCurrency minor units.
    }
}
```

### Units, Dimensions, and Coordinate Spaces

Use phantom tags for units that share the same storage.

```swift
struct Quantity<Unit, Value: Sendable>: Sendable {
    let value: Value
}

enum Meters {}
enum Feet {}
enum Seconds {}
enum Milliseconds {}

typealias DistanceInMeters = Quantity<Meters, Double>
typealias DurationInSeconds = Quantity<Seconds, Double>
```

Coordinate spaces deserve the same treatment.

```swift
struct Point<Space>: Sendable {
    let x: Double
    let y: Double
}

enum ScreenSpace {}
enum ViewSpace {}
enum ImagePixelSpace {}

func draw(at point: Point<ViewSpace>) {}

let screenPoint = Point<ScreenSpace>(x: 20, y: 40)
// draw(at: screenPoint)
// Does not compile: expected ViewSpace, got ScreenSpace.
```

Differentiate pixels and points, radians and degrees, Celsius and Fahrenheit, percentages and fractions, and local/global/safe-area coordinate spaces.

### Dates and Time

Use distinct types for distinct temporal concepts.

```swift
struct Instant: Hashable, Sendable {
    let date: Date
}

struct CalendarDay: Hashable, Sendable {
    let components: DateComponents
    let calendar: Calendar
}

struct Deadline: Hashable, Sendable {
    let instant: Instant
}

struct MonotonicDuration: Hashable, Sendable {
    let seconds: Double
}
```

Do not pass `Date` everywhere. A birthday, a cache expiration instant, a monotonic timeout, and a calendar day have different rules.

Validate intervals at construction.

```swift
struct ValidDateRange: Sendable {
    let interval: DateInterval

    init(start: Instant, end: Instant) throws {
        guard start.date <= end.date else { throw ValidationError.invalidRange }
        self.interval = DateInterval(start: start.date, end: end.date)
    }
}
```

### Images and Buffers

Model format, color space, dimensions, and initialization state when misuse is expensive.

```swift
struct ImageBuffer<PixelFormat, ColorSpace>: ~Copyable {
    let width: PositiveInt
    let height: PositiveInt
    private var bytes: [UInt8]
}

enum RGBA8 {}
enum BGRA8 {}
enum DisplayP3 {}
enum SRGB {}
```

Use state tags for initialized buffers.

```swift
enum Uninitialized {}
enum Initialized {}

struct Buffer<State>: ~Copyable {
    private var storage: UnsafeMutableRawBufferPointer
}

extension Buffer where State == Uninitialized {
    consuming func initialize() -> Buffer<Initialized> {
        // Initialize all bytes.
    }
}

extension Buffer where State == Initialized {
    borrowing func read() -> Data {
        // Safe to read initialized bytes.
    }
}

// Buffer<Uninitialized>.read()
// Does not compile: read exists only for Buffer<Initialized>.
```

### Typed Keys

Replace string keys with typed keys when the value type matters.

```swift
struct AnalyticsKey<Value>: Hashable, Sendable {
    let name: String
}

extension AnalyticsKey where Value == UserID {
    static let userID = AnalyticsKey<UserID>(name: "user_id")
}

extension AnalyticsKey where Value == Int {
    static let itemCount = AnalyticsKey<Int>(name: "item_count")
}

struct AnalyticsProperties {
    private var properties: [String: Any] = [:]

    mutating func set<Value>(_ value: Value, for key: AnalyticsKey<Value>) {
        properties[key.name] = value
    }
}

var event = AnalyticsProperties()
event.set(UserID(rawValue: "u_123"), for: .userID)
// event.set("u_123", for: .userID)
// Does not compile: expected UserID.
```

Use the same approach for UserDefaults, environment values, feature flags, localization keys, notification names, and payload dictionaries.

### Analytics Events and Payloads

Analytics payloads are usually heterogeneous dictionaries at the vendor boundary. Keep that boundary narrow and make event construction typed.

```swift
struct AnalyticsEvent<Name>: Sendable {
    fileprivate let name: String
    fileprivate var properties: [String: AnalyticsValue]
}

struct AnalyticsProperty<Event, Value>: Sendable {
    let name: String
}

struct AnalyticsValue: Sendable {
    let rawValue: String
}

enum SignupCompleted {}

extension AnalyticsProperty where Event == SignupCompleted, Value == AnalyticsValue {
    static let userID = AnalyticsProperty(name: "user_id")
    static let plan = AnalyticsProperty(name: "plan")
}

extension AnalyticsEvent where Name == SignupCompleted {
    static func signupCompleted(userID: UserID, plan: Plan) -> AnalyticsEvent<SignupCompleted> {
        var event = AnalyticsEvent<SignupCompleted>(name: "signup_completed", properties: [:])
        event.set(userID, for: .userID)
        event.set(plan.analyticsValue, for: .plan)
        return event
    }
}

extension AnalyticsEvent {
    mutating func set(_ value: AnalyticsValue, for property: AnalyticsProperty<Name, AnalyticsValue>) {
        properties[property.name] = value
    }
}
```

Wrong but tempting:

```swift
analytics.track("signup_complete", ["usr": user.id.rawValue, "plan": plan.rawValue])
```

Typed event names and typed properties prevent misspelled event names, wrong property value types, and raw PII from entering analytics without an explicit conversion.

### Validation Pipelines

Use `Optional` for absence without diagnostics, `throws` for control-flow failure, `Result` for stored outcomes, and accumulating validation for forms or batches.

```swift
struct Validator<Input, Output, Failure: Error> {
    let validate: (Input) -> Result<Output, NonEmptyArray<Failure>>
}

extension Validator {
    func map<NewOutput>(
        _ transform: @escaping (Output) -> NewOutput
    ) -> Validator<Input, NewOutput, Failure> {
        Validator<Input, NewOutput, Failure> { input in
            validate(input).map(transform)
        }
    }
}
```

Validate at trust boundaries, then pass refined values internally.

```swift
struct RegistrationForm {
    var email: String
    var password: String
}

struct ValidRegistration {
    let email: EmailAddress
    let password: NonEmptyString
}

func register(_ registration: ValidRegistration) async throws(RegistrationError) {
    // No email or password revalidation here.
}
```

Wrong but tempting:

```swift
func register(email: String, password: String) async throws {
    guard email.contains("@") else { throw RegistrationError.invalidEmail }
    guard !password.isEmpty else { throw RegistrationError.emptyPassword }
    // Every caller repeats or trusts this logic.
}
```

---

## Checklist

- Count representable states; replace invalid combinations with enums or refined structs.
- Avoid stored booleans and optionals that duplicate state; derive them from the source of truth.
- Keep owned enum switches exhaustive; reserve `@unknown default` for resilient external enums.
- Preserve unknown server cases when forward compatibility matters.
- Use `Never` for impossible generic axes and empty enums for tags, but rely on access control for unforgeability.
- Choose `enum` for exclusive states, `OptionSet` for combinable flags, and named boolean fields for independent options.
- Validate and canonicalize once at construction; keep raw values at boundaries.
- Hide memberwise and raw initializers that bypass invariants.
- Implement `Decodable` through validating constructors or DTO-to-domain refinement.
- Avoid failing literal conformances for validated production values.
- Use non-empty, bounded, range, index, key, unit, money, date, image, and buffer wrappers when raw primitives can be confused.
- Decide whether a model is an entity, value, actor-owned identity, or Sendable snapshot before deriving equality and concurrency behavior.
- Make ownership relationships explicit; use weak and unowned only when their lifetime semantics match the domain.
