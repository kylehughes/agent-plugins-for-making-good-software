# Type-Driven State Modeling — Deep Reference

Extended treatment of every pattern from [SKILL.md](SKILL.md). Each section provides full before/after code, trade-off analysis, and decision guidance for Swift 6.2.

---

## Sum Types Over Boolean Flags

### Decision Flowchart

1. Are there two or more booleans that are mutually exclusive? → **Enum.**
2. Is there a boolean paired with an optional that is non-nil only when true? → **Enum with associated value.**
3. Is there a boolean paired with an optional that is non-nil only when false? → **Enum with associated value.**
4. Is the boolean truly independent of all other state? → **Keep the boolean.**

### Full Before/After: Loading State

**Before** — 8 representable states, 3 valid:

```swift
final class ViewModel: ObservableObject {
    @Published var data: [Item]?
    @Published var error: Error?
    @Published var isLoading: Bool = false

    func load() async {
        isLoading = true
        error = nil
        do {
            data = try await fetchItems()
        } catch {
            self.error = error
        }
        isLoading = false
    }
}
```

Invalid states: `isLoading = true` + `error != nil`, `isLoading = true` + `data != nil` + `error != nil`, etc. Each consumer must handle these defensively.

**After** — 3 representable states, 3 valid:

```swift
final class ViewModel: ObservableObject {
    @Published var items: LoadState<[Item]> = .loading

    func load() async {
        items = .loading
        do {
            items = .completed(.success(try await fetchItems()))
        } catch {
            items = .completed(.failure(error))
        }
    }
}
```

No invalid states exist. The view can switch exhaustively.

### Full Before/After: Authentication

**Before:**

```swift
struct Session {
    var isAuthenticated: Bool
    var token: String?
    var user: User?
}
// isAuthenticated = true, token = nil → crash when unwrapping
```

**After:**

```swift
enum Session: Sendable {
    case authenticated(token: String, user: User)
    case unauthenticated
}
```

### Trade-Off Analysis

| Factor | Booleans | Enum |
|---|---|---|
| States representable | 2^n (exponential) | Exactly n cases |
| Invalid state possible | Yes | No |
| Pattern matching | if/else chains | switch (exhaustive) |
| Adding a new state | Add boolean + update all guards | Add case + compiler errors guide fixes |
| Discoverability | Must read docs | Autocomplete shows all cases |
| Cognitive load | Grows with boolean count | Constant per case |

### When to Consolidate Multiple Enums

If two enums always change together, they may be one enum in disguise:

```swift
// Suspicious: these always change in lockstep
enum ConnectionStatus { case connected, disconnected }
enum DataStatus { case loaded, empty }

// Better: single enum if states are correlated
enum AppState {
    case connected(data: [Item])
    case disconnected
    case loading
}
```

---

## Product Type Consolidation

### Decision Flowchart

1. Are two or more arrays indexed in parallel? → **Single array of struct.**
2. Is a dictionary used with a fixed, known set of keys? → **Named struct.**
3. Is a tuple returned from a function and consumed across multiple call sites? → **Named struct.**
4. Is a tuple used locally within a single function? → **Keep the tuple.**

### Full Before/After: Parallel Arrays

**Before:**

```swift
final class ContactList {
    var emails: [String] = []
    var names: [String] = []
    var phoneNumbers: [String] = []

    func addContact(name: String, email: String, phone: String) {
        emails.append(email)
        names.append(name)
        phoneNumbers.append(phone)
    }

    func removeContact(at index: Int) {
        emails.remove(at: index)
        names.remove(at: index)
        // Forgot phoneNumbers — silent bug
    }
}
```

**After:**

```swift
struct Contact: Sendable {
    let email: String
    let name: String
    let phoneNumber: String
}

final class ContactList {
    var contacts: [Contact] = []

    func addContact(_ contact: Contact) {
        contacts.append(contact)
    }

    func removeContact(at index: Int) {
        contacts.remove(at: index) // All fields removed atomically
    }
}
```

### Full Before/After: Dictionary-as-Struct

**Before:**

```swift
func parseConfig(_ json: [String: Any]) -> [String: Any] {
    var config: [String: Any] = [:]
    config["timeout"] = json["timeout"] as? Int ?? 30
    config["retryCount"] = json["retryCount"] as? Int ?? 3
    config["baseURL"] = json["baseURL"] as? String ?? "https://api.example.com"
    return config
}

// Consumer: must know key names and types
let timeout = config["timeout"] as! Int // Force cast, typo-prone
```

**After:**

```swift
struct NetworkConfig: Sendable {
    let baseURL: String
    let retryCount: Int
    let timeout: Int

    init(json: [String: Any]) {
        baseURL = json["baseURL"] as? String ?? "https://api.example.com"
        retryCount = json["retryCount"] as? Int ?? 3
        timeout = json["timeout"] as? Int ?? 30
    }
}

// Consumer: type-safe, autocomplete-friendly
let timeout = config.timeout
```

---

## Optionality Refinement

### Decision Flowchart

1. Is an optional always non-nil when another field has a specific value? → **Enum with associated value.**
2. Is an optional always nil when another field has a specific value? → **Enum with associated value.**
3. Are two optionals mutually exclusive (exactly one is non-nil)? → **Enum with associated values.**
4. Can both optionals independently be nil or non-nil? → **Keep both optional.**

### Full Before/After: Form State

**Before:**

```swift
struct FormState {
    var errorMessage: String?
    var isSubmitting: Bool
    var submittedAt: Date?
    var validationErrors: [String]?
}
// isSubmitting = true, submittedAt != nil → incoherent
// errorMessage != nil, validationErrors != nil → which errors to show?
```

**After:**

```swift
enum FormState: Sendable {
    case editing(validationErrors: [String])
    case failed(errorMessage: String)
    case idle
    case submitted(at: Date)
    case submitting
}
```

Each state carries exactly the data relevant to it. No impossible combinations.

---

## Phantom Types

### Decision Flowchart

1. Are there two or more values of the same underlying type (e.g., both `String`) that serve different roles at a call site? → **Phantom-typed wrapper.**
2. Does a value pass through distinct states where different operations are valid in each? → **State-tagged phantom type.**
3. Is there a builder or configuration with required fields that could be forgotten? → **Phantom-typed builder pattern.**
4. Is there only one identifier of this type in the module, with no risk of confusion? → **Keep the raw type.**

### Core Technique

A phantom type parameter appears in the type signature but not in the stored properties. It exists only to create distinct types at the compile-time level.

```swift
struct Tagged<Tag, RawValue: Hashable>: Hashable, RawRepresentable, Sendable {
    let rawValue: RawValue
}

// RawRepresentable enables automatic Codable conformance when RawValue is Codable.
```

`Tag` is never instantiated — it is a compile-time label.

### Identifier Safety

```swift
// Tag types — empty enums are conventional (no cases, no instances)
enum UserTag {}
enum WorkspaceTag {}

typealias UserID = Tagged<UserTag, String>
typealias WorkspaceID = Tagged<WorkspaceTag, String>

// API surface becomes self-documenting and swap-proof
func fetchUser(id: UserID, in workspace: WorkspaceID) async throws -> User
```

### State-Tagged Phantom Types

Phantom types can encode state transitions at the type level:

```swift
enum Unvalidated {}
enum Validated {}

struct Form<State> {
    let fields: [String: String]
}

extension Form where State == Unvalidated {
    func validate() throws -> Form<Validated> {
        // validation logic
        Form<Validated>(fields: fields)
    }
}

func submit(_ form: Form<Validated>) async throws {
    // Only accepts validated forms — compiler enforces this
}
```

### Builder Pattern with Phantom Types

Enforce required fields at compile time. The phantom state parameter restricts which methods are available, ensuring every path to `Complete` has set both fields:

```swift
enum MissingName {}
enum HasName {}
enum Complete {}

struct UserBuilder<State> {
    fileprivate let email: String?
    fileprivate let name: String?

    fileprivate init(email: String? = nil, name: String? = nil) {
        self.email = email
        self.name = name
    }
}

extension UserBuilder where State == MissingName {
    func withName(_ name: String) -> UserBuilder<HasName> {
        UserBuilder<HasName>(name: name)
    }
}

extension UserBuilder where State == HasName {
    func withEmail(_ email: String) -> UserBuilder<Complete> {
        UserBuilder<Complete>(email: email, name: name)
    }
}

extension UserBuilder where State == Complete {
    func build() -> User {
        // Both fields guaranteed non-nil by the state machine — each
        // transition method sets one, and no path to Complete skips either.
        guard let email, let name else {
            preconditionFailure("Builder state machine violated")
        }
        return User(email: email, name: name)
    }
}
```

### Trade-Off Analysis

| Factor | Phantom types | Runtime checks |
|---|---|---|
| Error detection | Compile time | Runtime |
| API surface | Self-documenting | Requires documentation |
| Flexibility | Rigid — new states need new tags | Dynamic — easy to add states |
| Complexity | Higher for simple cases | Lower for simple cases |
| Binary size | No impact (types erased at runtime) | No impact |

### When to Use Phantom Types

- Multiple identifiers of the same underlying type that could be confused
- State transitions that should be enforced by the compiler
- API boundaries where type safety prevents misuse

### When to Skip Phantom Types

- Single ID type in a narrow module
- State that changes frequently during development (the tag types become churn)
- When the set of valid states is dynamic, not static

---

## ~Copyable and Move Semantics

### Decision Flowchart

1. Does copying this value create a logical error (double-close, double-consume, duplicate state machine)? → **`~Copyable`.**
2. Does the value represent a resource with a finite lifecycle (open/close, acquire/release)? → **`~Copyable` with `consuming` cleanup.**
3. Does the value represent a state machine with irreversible transitions? → **`~Copyable` with consuming transition methods.**
4. Does the value need to be stored in collections or conform to `Equatable`/`Hashable`? → **Keep copyable; use runtime guards.**

### Ownership Annotations

Swift's ownership model provides three ways to pass values:

| Annotation | Meaning | After call |
|---|---|---|
| `borrowing` | Read-only access | Value still usable |
| `consuming` | Takes ownership | Value no longer usable |
| `inout` | Exclusive mutable access | Value modified in place |

### Consuming State Machines

The most powerful application: state transitions that consume the current state.

```swift
struct Idle: ~Copyable {
    let config: Configuration

    consuming func start() -> Running {
        Running(config: config)
    }
}

struct Running: ~Copyable {
    let config: Configuration
    var progress: Double = 0

    consuming func pause() -> Paused {
        Paused(config: config, progress: progress)
    }

    consuming func complete() -> Completed {
        Completed(config: config)
    }
}

struct Paused: ~Copyable {
    let config: Configuration
    let progress: Double

    consuming func resume() -> Running {
        Running(config: config, progress: progress)
    }

    consuming func cancel() -> Idle {
        Idle(config: config)
    }
}

struct Completed: ~Copyable {
    let config: Configuration
}
```

The compiler enforces:
- Cannot be in two states simultaneously (no copying)
- Cannot use the old state after transitioning (consumed)
- Cannot skip states (only defined transitions compile)
- Cannot forget to transition (value must be consumed or explicitly discarded)

### Borrowing and Consuming Methods

```swift
struct FileHandle: ~Copyable {
    private let descriptor: Int32

    // Borrowing: reads without consuming
    borrowing func read(count: Int) -> Data {
        // descriptor still valid after this call
    }

    // Consuming: closes and invalidates
    consuming func close() {
        // descriptor used, FileHandle consumed
    }

    deinit {
        // Automatic cleanup if not explicitly closed
    }
}

let file = FileHandle(descriptor: fd)
let data = file.read(count: 1024) // borrows
file.close()                       // consumes
// file.read(count: 1)            // Compiler error: used after consuming
```

### ~Escapable (Swift 6.2)

`~Escapable` types cannot outlive their scope, useful for borrowed views into data. This feature is still evolving — expect API refinements in future Swift releases.

```swift
struct BufferView: ~Copyable, ~Escapable {
    let pointer: UnsafeBufferPointer<UInt8>
    // Cannot be stored in a property or returned from scope
    // Guarantees the buffer pointer remains valid during use
}
```

### Trade-Off Analysis

| Factor | ~Copyable | Regular types + runtime checks |
|---|---|---|
| Enforcement | Compile time | Runtime |
| Ergonomics | Requires ownership awareness | Familiar value semantics |
| Protocol support | Limited (no Equatable, Hashable yet) | Full protocol support |
| Collection storage | Cannot be stored in standard collections | Full collection support |
| Learning curve | High — new mental model | Low |

### When to Use ~Copyable

- Resource handles (files, connections, locks)
- One-shot tokens or continuations
- State machines with irreversible transitions
- When double-use is a *safety* bug, not just a logic bug

### When to Skip ~Copyable

- Ordinary value types (models, configs, DTOs)
- Types that need to be stored in arrays, dictionaries, or sets
- Types that need Equatable, Hashable, or Codable conformance
- When the copying concern is theoretical, not observed

---

## Typed Throws

### Decision Flowchart

1. Will the caller `switch` on the error type to handle cases differently? → **Typed throws.**
2. Is this a generic wrapper that should preserve the wrapped function's error type? → **Generic typed throws (`throws(E)`).**
3. Does a protocol need conformers to specify their error type? → **Associated type + typed throws.**
4. Does the caller present a generic error message regardless of type? → **Keep untyped `throws`.**

### Basic Typed Throws

```swift
enum ParseError: Error {
    case invalidFormat
    case overflow
    case unexpectedCharacter(Character)
}

func parseInteger(_ string: String) throws(ParseError) -> Int {
    guard let value = Int(string) else {
        if string.contains(where: { !$0.isNumber && $0 != "-" }) {
            throw .unexpectedCharacter(string.first(where: { !$0.isNumber && $0 != "-" })!)
        }
        throw .overflow
    }
    return value
}
```

### Generic Typed Throws

Functions that propagate a closure's error type without erasing it:

```swift
func withRetry<Result, E: Error>(
    maxAttempts: Int,
    operation: () async throws(E) -> Result
) async throws(E) -> Result {
    for attempt in 1...maxAttempts {
        do {
            return try operation()
        } catch {
            if attempt == maxAttempts { throw error }
        }
    }
    fatalError("unreachable")
}
```

The caller retains the specific error type:

```swift
// error is ParseError, not any Error
let value = try await withRetry(maxAttempts: 3) {
    try parseInteger(input)
}
```

### Protocol Requirements with Typed Throws

```swift
protocol Validator {
    associatedtype Input
    associatedtype ValidationError: Error

    func validate(_ input: Input) throws(ValidationError) -> Input
}
```

Conforming types specify their error:

```swift
struct EmailValidator: Validator {
    enum ValidationError: Error {
        case invalidFormat
        case tooLong
    }

    func validate(_ input: String) throws(ValidationError) -> String {
        guard input.contains("@") else { throw .invalidFormat }
        guard input.count <= 254 else { throw .tooLong }
        return input
    }
}
```

### Scoped Error Patterns

Use typed throws at module boundaries, untyped throws at the top level:

```swift
// Module boundary: specific errors
public func loadUser(id: UserID) throws(DataError) -> User

// UI layer: catches and presents generically
func handleLoad() async {
    do {
        user = try await loadUser(id: currentUserID)
    } catch {
        // error is DataError — can switch exhaustively
        showError(error)
    }
}
```

### Trade-Off Analysis

| Factor | Typed throws | Untyped throws |
|---|---|---|
| Error specificity | Exact type preserved | Erased to `any Error` |
| Exhaustive catching | Yes — compiler enforces | No — catch-all required |
| Composability | Must align error types | Any error propagates freely |
| Boilerplate | More explicit | Less explicit |
| Protocol requirements | Fully expressible | Generic fallback |

### When to Use Typed Throws

- Module boundaries where callers switch on error cases
- Generic wrappers that should preserve the wrapped function's error type
- Protocol requirements where conformers have distinct error types

### When to Skip Typed Throws

- Top-level UI code that presents a generic error message
- Functions that can fail for many unrelated reasons
- Rapid prototyping where error handling is deferred

---

## Validated Values

### Decision Flowchart

1. Does a validated value cross a function or module boundary? → **Failable-init newtype or throwing-init newtype.**
2. Does a stored property need continuous enforcement of a constraint (e.g., clamped range)? → **Property wrapper.**
3. Do callers need to know *why* validation failed? → **Throwing init with typed error.**
4. Is the validation local to a single function and the value is not stored? → **Inline `guard`.**

### Failable Init Newtypes

Validate once, carry the guarantee:

```swift
struct NonEmptyString: Sendable {
    let value: String

    init?(_ value: String) {
        guard !value.isEmpty else { return nil }
        self.value = value
    }
}

struct PositiveInt: Sendable {
    let value: Int

    init?(_ value: Int) {
        guard value > 0 else { return nil }
        self.value = value
    }
}

// Usage: validation happens at the boundary
func createUser(name: NonEmptyString, age: PositiveInt) -> User {
    // No validation needed here — types guarantee constraints
    User(name: name.value, age: age.value)
}
```

### Throwing Init Variant

When you need error information:

```swift
struct EmailAddress: Sendable {
    enum ValidationError: Error {
        case missingAtSign
        case tooLong
    }

    let value: String

    init(_ value: String) throws(ValidationError) {
        guard value.contains("@") else { throw .missingAtSign }
        guard value.count <= 254 else { throw .tooLong }
        self.value = value
    }
}
```

### Property Wrappers for Embedded Validation

```swift
@propertyWrapper
struct Clamped<Value: Comparable & Sendable>: Sendable {
    private var storage: Value
    let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { storage }
        set { storage = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.storage = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

struct AudioSettings: Sendable {
    @Clamped(0...100) var volume: Int = 50
    @Clamped(20...20000) var frequency: Int = 440
}
```

### Trade-Off Analysis

| Factor | Newtype | Inline validation |
|---|---|---|
| Guarantee propagation | Through the type system | Manual at each site |
| Boilerplate | Type definition | Guard/if at each use |
| Performance | Minimal (usually optimized away) | Same |
| Composability | Combine via generics | Ad hoc |
| Discoverability | Type signature documents constraint | Must read implementation |

---

## Advanced Patterns

### Protocol Witnesses

Replace runtime polymorphism with static dispatch when behavior is configured, not discovered:

```swift
// Existential approach: runtime dispatch, heap allocation
protocol Formatter {
    func format(_ value: Double) -> String
}

// Protocol witness approach: static dispatch, inline
struct NumberFormat: Sendable {
    let format: @Sendable (Double) -> String

    static let currency = NumberFormat { value in
        "$\(String(format: "%.2f", value))"
    }

    static let percentage = NumberFormat { value in
        "\(String(format: "%.1f", value * 100))%"
    }
}
```

Use protocol witnesses when:
- The set of implementations is known at compile time
- Performance matters (avoids existential dispatch)
- You want to store formatters/strategies as values without existential overhead

### Conditional Conformance

Extend generic types to gain capabilities when their type parameters support them:

```swift
// LoadState gains Equatable only when the wrapped type is Equatable
extension LoadState: Equatable where T: Equatable {}

// Array of optional values gains a custom method
extension Array where Element: OptionalProtocol {
    func compacted() -> [Element.Wrapped] {
        compactMap(\.optional)
    }
}
```

### `some` vs `any`

| Feature | `some P` (opaque) | `any P` (existential) |
|---|---|---|
| Concrete type | Fixed (but hidden) | Varies at runtime |
| Storage | No box | Existential box (heap if large) |
| Generic specialization | Yes | No |
| Heterogeneous collections | No | Yes |
| Self/associated type | Preserved | Erased |

**Decision rule**: Use `some` by default. Use `any` only when you need heterogeneous storage or the concrete type genuinely varies at runtime.

```swift
// Prefer: concrete type known to compiler
func makeView() -> some View { Text("Hello") }

// When needed: heterogeneous storage
var formatters: [any FormatStyle] = [.currency, .percentage]
```

### Result Builders for Domain Validation

Enforce structural constraints at compile time:

```swift
@resultBuilder
struct FormBuilder {
    static func buildBlock(_ components: FormField...) -> [FormField] {
        components
    }
}

struct FormConfig {
    let fields: [FormField]

    init(@FormBuilder content: () -> [FormField]) {
        fields = content()
    }
}
```

### InlineArray (Swift 6.2)

Fixed-size array stored inline (stack or struct), no heap allocation:

```swift
// Exactly 3 elements — compile-time size guarantee
let rgb: InlineArray<3, UInt8> = [255, 128, 0]
```

Use when:
- Size is known at compile time
- Performance is critical (cache-friendly)
- You want the type to enforce size constraints

### Marker Protocols

Empty protocols as compile-time tags:

```swift
protocol Sanitized {}
protocol Raw {}

struct HTMLContent<State> {
    let value: String
}

func render(_ content: HTMLContent<Sanitized>) -> String {
    content.value // Safe to render — type guarantees sanitization
}

func sanitize(_ content: HTMLContent<Raw>) -> HTMLContent<Sanitized> {
    HTMLContent<Sanitized>(value: escape(content.value))
}
```

---

## Concurrency-Aware Type Safety

### Sendable by Design

Shape types so `Sendable` conformance is natural rather than forced:

```swift
// Natural Sendable: all stored properties are Sendable value types
struct UserProfile: Sendable {
    let avatarURL: URL
    let displayName: String
    let id: UUID
}

// Forced Sendable: requires @unchecked due to mutable reference type
final class Cache: @unchecked Sendable {
    private let lock = NSLock()
    private var storage: [String: Data] = [:]
}
```

**Prefer**: Structs with `let` properties (automatically Sendable) over classes that need `@unchecked Sendable`.

### `sending` Parameter Modifier

Transfers ownership across isolation boundaries:

```swift
func process(_ value: sending MyType) async {
    // value is now owned by this isolation domain
}
```

### Isolation as a Type-Level Concept

`@MainActor`, `@Sendable`, and actor isolation are type-level properties enforced by the compiler. Design types so isolation requirements are obvious from the type signature:

```swift
// Isolation is visible in the type
@MainActor
final class ViewModel: ObservableObject {
    // All access implicitly MainActor — no surprises
}

// Sendable closure requirement is visible in the type
struct EventHandler: Sendable {
    let handler: @Sendable (Event) -> Void
}
```

---

## Pragmatism Guardrails — Detailed Examples

### Over-Engineering: Phantom Types for Single ID

**Over-engineered:**

```swift
enum UserTag {}
typealias UserID = Tagged<UserTag, String>

// Used in exactly one place
struct UserService {
    func fetch(id: UserID) async throws -> User
}
```

If `UserID` is the only identifier in the module and there is no risk of confusion, a plain `String` parameter is clearer.

### Over-Engineering: Enum for Independent Booleans

**Over-engineered:**

```swift
enum ToggleState {
    case enabledAndAnimating
    case enabledAndStatic
    case disabledAndAnimating
    case disabledAndStatic
}
```

If `isEnabled` and `isAnimating` are genuinely independent, two booleans are simpler. The combinatorial enum adds ceremony without preventing bugs.

### Over-Engineering: Newtype for Local Validation

**Over-engineered:**

```swift
struct ValidatedInput: Sendable {
    let value: String
    init?(_ value: String) {
        guard !value.isEmpty else { return nil }
        self.value = value
    }
}

// Used in one function, value never propagated
func handleInput(_ raw: String) {
    guard let validated = ValidatedInput(raw) else { return }
    process(validated.value) // Immediately unwrapped
}
```

If the validated value is immediately unwrapped and never passed further, inline `guard` is clearer.

### The Decision Checklist

Before introducing a new type for correctness, answer:

1. **Does this prevent a real bug?** Not hypothetical — has this class of error occurred, or is the risk concrete?
2. **Does this cross a boundary?** Types earn their weight at function boundaries, module boundaries, API boundaries. Local values rarely need newtypes.
3. **Will someone else encounter this type?** If only one function touches it, the learning cost may exceed the safety benefit.
4. **Is the domain stable?** If requirements are changing weekly, rigid type structures create churn. Wait for stability.
5. **Does the complexity compound?** A single phantom type is fine. A phantom type nested in a generic nested in a conditional conformance may need simplification.

If any answer is "no" or uncertain, defer the type modeling until evidence accumulates.
