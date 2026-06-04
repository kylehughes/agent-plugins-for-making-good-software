# Ownership, Concurrency, and Boundary Modeling

Use this reference when the invariant is not just "which enum case is valid", but who owns a value, which isolation domain may touch it, which boundary refined it, or which authority makes an operation legal.

The recurring rule is:

```swift
// Raw at the edge.
struct UserDTO: Decodable {
    let email: String
    let id: String
}

// Refined in the core.
struct User: Sendable {
    enum ValidationError: Error {
        case invalidEmail(EmailAddress.ValidationError)
        case invalidID(String)
    }

    let email: EmailAddress
    let id: UserID

    init(dto: UserDTO) throws(User.ValidationError) {
        do {
            email = try EmailAddress(dto.email)
        } catch {
            throw .invalidEmail(error)
        }

        guard let id = UserID(rawValue: dto.id) else {
            throw .invalidID(dto.id)
        }

        self.id = id
    }
}
```

The type proves an invariant only if invalid construction is impossible through the APIs available to the caller. A public `init(rawValue:)`, mutable stored property, synthesized `Decodable`, public marker conformance, or unchecked escape hatch can erase the proof.

Feature caveat: Swift ownership, typed throws, strict concurrency, typed Foundation messages, `Span`, `RawSpan`, `~Escapable`, `BitwiseCopyable`, and strict memory safety diagnostics are toolchain and SDK sensitive. Use the spelling supported by the project's selected Swift version. When a feature is still evolving, keep the wrapper API small so the rest of the domain model is insulated from spelling or availability changes.

---

## Ownership and Lifetime

### Noncopyable Values and Generics

Swift generic parameters are copyable unless the declaration opts out. If a wrapper must accept a file descriptor, lock guard, transaction, or borrowed view that cannot be copied, model that explicitly.

```swift
protocol Closable: ~Copyable {
    consuming func close()
}

struct Owned<Value: ~Copyable>: ~Copyable {
    private var value: Value

    init(_ value: consuming Value) {
        self.value = value
    }

    consuming func take() -> Value {
        value
    }
}

extension Owned: Copyable where Value: Copyable {}
```

Use `T: ~Copyable` only where ordinary generic code must work with both copyable and noncopyable values. Keep ordinary models copyable unless copying creates a real bug.

Protocols and existentials can also participate in the noncopyable model in modern Swift toolchains:

```swift
protocol SessionResource: ~Copyable {
    borrowing var isOpen: Bool { get }
    consuming func invalidate()
}

func close(_ resource: consuming any SessionResource & ~Copyable) {
    resource.invalidate()
}
```

Caveat: noncopyable values still have practical restrictions around storage, protocol conformances, collection use, and framework APIs. Do not introduce `~Copyable` into broad app model types just to signal importance.

### Linear Guard Tokens

A linear guard token models "this capability exists exactly while this value is alive."

```swift
import Synchronization

struct Locked<Value: ~Copyable>: ~Copyable {
    private let mutex: Mutex<Value>

    init(_ value: consuming Value) {
        mutex = Mutex(value)
    }

    borrowing func withLock<Result, Failure: Error>(
        _ body: (inout Value) throws(Failure) -> Result
    ) throws(Failure) -> Result {
        try mutex.withLock { value in
            try body(&value)
        }
    }
}
```

Do not return the protected value or expose a mutable reference to it. The closure is the boundary that keeps the lock and mutation lifetime aligned.

Other useful linear tokens:

```swift
struct ActiveTransaction: ~Copyable {
    private var raw: DatabaseTransaction?

    consuming func commit() throws(DatabaseError) {
        guard let transaction = raw else { return }
        try transaction.commit()
        raw = nil
    }

    consuming func rollback() {
        raw?.rollback()
        raw = nil
    }

    deinit {
        raw?.rollback()
    }
}

struct OneShotContinuation<Success, Failure: Error>: ~Copyable {
    private let continuation: CheckedContinuation<Result<Success, Failure>, Never>

    consuming func resume(returning value: Success) {
        continuation.resume(returning: .success(value))
    }

    consuming func resume(throwing error: Failure) {
        continuation.resume(returning: .failure(error))
    }
}
```

Use this pattern for transactions, temporary files, scoped security resources, borrow tokens, one-shot callbacks, and single-use credentials.

### `deinit` for Noncopyable Structs

Noncopyable structs can use `deinit` to release a unique resource without paying for reference identity.

```swift
struct FileDescriptor: ~Copyable {
    private var rawValue: CInt?

    init(opening path: AbsolutePath) throws(FileError) {
        let fd = open(path.stringValue, O_RDONLY)
        guard fd >= 0 else { throw .openFailed(errno) }
        rawValue = fd
    }

    borrowing func read(maxBytes: Int) throws(FileError) -> Data {
        // Call read(2) and map errno into FileError.
    }

    consuming func close() throws(FileError) {
        guard let fd = rawValue else { return }
        guard Darwin.close(fd) == 0 else {
            throw .closeFailed(errno)
        }
        rawValue = nil
    }

    deinit {
        if let fd = rawValue {
            _ = Darwin.close(fd)
        }
    }
}
```

Caveats:

- Use explicit consuming methods for semantic operations like `commit`, `cancel`, or "must report failure".
- Use `deinit` as a cleanup fallback, not as the only place important business decisions happen.
- A final class is still better when the resource must have shared identity, weak references, ObjC interop, or framework-managed lifetime.

### Borrowing, Consuming, and `inout`

| Form | Use when | Callee can | Caller after call | Example |
|---|---|---|---|---|
| `borrowing` | Inspect without taking ownership | Read, not consume | Use value again | `file.size()` |
| `consuming` | Transfer or finish a linear value | Use exactly once | Cannot use old value | `transaction.commit()` |
| `inout` | Mutate under exclusive access | Modify in place | Use updated value | `buffer.append(bytes)` |
| `sending` | Transfer across isolation | Move into another task or actor | Treat old access as ended | `await worker.ingest(batch)` |

```swift
struct UploadDraft: ~Copyable {
    private var parts: [Data] = []

    borrowing var byteCount: Int {
        parts.reduce(0) { $0 + $1.count }
    }

    mutating func append(_ part: Data) {
        parts.append(part)
    }

    consuming func seal() -> SealedUpload {
        SealedUpload(parts: parts)
    }
}
```

`borrowing` communicates "this method cannot consume me." `consuming` communicates "this operation changes the lifecycle." `inout` communicates "exclusive mutation happens inside this call."

### Closure-Scoped Access

Closure APIs are often simpler and safer than exposing a token type publicly.

```swift
struct Database {
    func withTransaction<Result, Failure: Error>(
        _ body: (inout ActiveDatabaseTransaction) throws(Failure) -> Result
    ) throws(Failure) -> Result {
        var transaction = beginTransaction()
        do {
            let result = try body(&transaction)
            try transaction.commit()
            return result
        } catch {
            transaction.rollback()
            throw error
        }
    }
}

struct TemporaryDirectory: ~Copyable {
    let path: DirectoryPath

    deinit {
        try? FileManager.default.removeItem(atPath: path.stringValue)
    }
}

func withTemporaryDirectory<Result>(
    _ body: (borrowing TemporaryDirectory) throws -> Result
) rethrows -> Result {
    let directory = TemporaryDirectory(path: makeTemporaryDirectory())
    return try body(directory)
}
```

Prefer closure-scoped access when a value must not escape: lock guards, unsafe pointers, borrowed buffers, temporary files, security-scoped resources, and database transactions.

### `Span`, `RawSpan`, Borrowed Views, and `~Escapable`

`Span` and `RawSpan` model borrowed memory views that should not outlive their owner. They are intended to replace many closure-only unsafe buffer APIs with safer, composable borrowed values. Exact API availability and spelling vary by Swift and SDK version, so keep use localized behind small helpers.

```swift
struct Packet: Sendable {
    private let storage: [UInt8]

    func withBytes<Result>(_ body: (borrowing Span<UInt8>) throws -> Result) rethrows -> Result {
        try storage.withSpan { span in
            try body(span)
        }
    }
}

func checksum(_ bytes: borrowing Span<UInt8>) -> UInt32 {
    var result: UInt32 = 0
    for byte in bytes {
        result = result &+ UInt32(byte)
    }
    return result
}
```

Use typed spans when the element type matters. Use raw spans when the boundary is byte-oriented or layout-oriented:

```swift
struct BinaryBlob: ~Copyable {
    private let storage: RawBuffer

    borrowing func withRawBytes<Result>(
        _ body: (borrowing RawSpan) throws -> Result
    ) rethrows -> Result {
        try storage.withRawSpan(body)
    }
}
```

`~Escapable` is the lifetime marker behind this style: a value can be used locally but not stored, returned, or captured by an escaping closure.

```swift
struct BorrowedCString: ~Copyable, ~Escapable {
    private let pointer: UnsafePointer<CChar>

    borrowing var string: String {
        String(cString: pointer)
    }
}
```

Caveats:

- A borrowed view proves lifetime, not semantic validity.
- A `Span<UInt8>` does not prove UTF-8, encryption state, or message framing.
- Keep unsafe pointer construction in one module. Export borrowed or refined wrappers.

### `BitwiseCopyable`

`BitwiseCopyable` is a layout promise: values can be copied or moved with direct memory operations and do not need special destruction. Use it for low-level binary-layout types only when that promise is part of the API.

```swift
@frozen
struct RGBA8: BitwiseCopyable, Sendable {
    var red: UInt8
    var green: UInt8
    var blue: UInt8
    var alpha: UInt8
}
```

Do not add public `BitwiseCopyable` conformance as a casual performance hint. In a library, it constrains future stored properties and destructor behavior.

### Strict Memory Safety Mode

Strict memory safety diagnostics are useful when a project wants compiler pressure against unchecked pointer, unsafe buffer, and lifetime patterns.

Migration recipe:

1. Enable the toolchain's strict memory safety setting in Xcode or SwiftPM for a small target first.
2. Replace raw pointer APIs with `Span`, `RawSpan`, array-backed values, or closure-scoped `withUnsafe...` wrappers.
3. Quarantine remaining unsafe operations in narrow types named after the ownership they enforce.
4. Document preconditions at the wrapper boundary.
5. Keep unsafe acknowledgements local. Do not spread suppressions through domain code.

The goal is not "no unsafe code exists." The goal is "unsafe code is small, named, reviewed, and cannot leak invalid states into safe code."

### Unsafe Interop Wrappers

Wrap every foreign ownership rule in a nominal type.

```swift
struct OwnedCHandle: ~Copyable {
    private let raw: OpaquePointer

    init(raw: OpaquePointer) {
        self.raw = raw
    }

    borrowing func withBorrowed<Result>(_ body: (OpaquePointer) throws -> Result) rethrows -> Result {
        try body(raw)
    }

    consuming func close() {
        c_library_close(raw)
    }

    deinit {
        c_library_close(raw)
    }
}

struct BorrowedCHandle: ~Copyable, ~Escapable {
    private let raw: OpaquePointer

    borrowing func withUnsafePointer<Result>(_ body: (OpaquePointer) throws -> Result) rethrows -> Result {
        try body(raw)
    }
}
```

Name the ownership:

- `OwnedPointer<T>` closes or frees.
- `BorrowedPointer<T>: ~Escapable` does not close or free.
- `MutableBuffer<T>` owns initialized mutable storage.
- `UninitializedBuffer<T>` permits initialization but not reads.
- `CxxReference<T>: ~Escapable` cannot outlive the C++ owner.

---

## Failures and Validation

### Typed Throws Without Overclaiming

Typed throws gives the `catch` block a precise error type. It does not make every sequence of typed `catch .case` clauses an exhaustiveness proof in all forms.

Use an unconditional `catch` plus `switch` when you need exhaustive case handling:

```swift
enum LoginError: Error {
    case invalidCredentials
    case lockedOut(until: Date)
    case networkUnavailable
}

func login(_ request: LoginRequest) async throws(LoginError) -> AuthenticatedSession {
    // ...
}

do {
    session = try await login(request)
} catch {
    switch error {
    case .invalidCredentials:
        showInvalidCredentials()
    case .lockedOut(let date):
        showLockedOut(until: date)
    case .networkUnavailable:
        showRetry()
    }
}
```

If an operation composes multiple error sources, either map them into a local error type or intentionally erase:

```swift
enum ProfileLoadError: Error {
    case decoding(DecodingError)
    case network(NetworkError)
    case unauthorized
}

func loadProfile() async throws(ProfileLoadError) -> Profile {
    do {
        let data = try await client.get(profileEndpoint)
        return try decoder.decode(Profile.self, from: data)
    } catch let error as NetworkError {
        throw .network(error)
    } catch let error as DecodingError {
        throw .decoding(error)
    } catch {
        throw .network(.unknown(error))
    }
}
```

Use untyped `throws` at integration seams when the caller cannot do anything type-specific.

### `throws(Never)` and Infallible Generic APIs

`throws(Never)` models "this generic operation has the same shape as a throwing operation, but this instantiation cannot fail." Treat it like a nonthrowing operation at call sites.

```swift
protocol Loader {
    associatedtype Output
    associatedtype Failure: Error

    func load() async throws(Failure) -> Output
}

struct StaticLoader<Output: Sendable>: Loader {
    let output: Output

    func load() async throws(Never) -> Output {
        output
    }
}
```

This is useful for shared state machines such as `TaskState<Output, Failure>` where some callers are infallible.

### Layered Error Taxonomy

Avoid a single global `AppError` unless the app truly handles all failures uniformly. Model errors at the layer where they are meaningful.

```swift
enum EmailAddressError: Error {
    case empty
    case missingAtSign
}

enum HTTPError: Error {
    case transport(URLError)
    case status(code: Int, body: Data)
    case decoding(DecodingError)
}

enum SaveProfileError: Error {
    case invalidEmail(EmailAddressError)
    case offline
    case rejectedByServer(reason: String)
}
```

Good error layers:

- Validation errors describe a bad input value.
- Domain errors describe business rules.
- Infrastructure errors describe I/O, networking, persistence, decoding, and permissions.
- Presentation errors describe what the UI can show or ask next.
- Cancellation is usually not a domain failure. Preserve it separately when the caller needs cancellation semantics.

### Optional vs `Result` vs `throws`

| Shape | Use when | Do not use when |
|---|---|---|
| `Optional<Value>` | Absence is expected and needs no diagnostic | Caller must know why construction failed |
| `Result<Value, Failure>` | The outcome is stored, passed around, retried, or rendered later | Immediate control flow is clearer |
| `throws(Failure)` | Failure interrupts control flow and caller handles it now | You need to store the failure as state |
| `throws(Never)` | A generic API slot is infallible in this specialization | A plain nonthrowing API is simpler |

```swift
struct EmailAddress: Sendable {
    enum Error: Swift.Error {
        case empty
        case missingAtSign
    }

    let value: String

    init(_ value: String) throws(Error) {
        guard !value.isEmpty else { throw .empty }
        guard value.contains("@") else { throw .missingAtSign }
        self.value = value
    }
}

let optionalEmail = try? EmailAddress(rawInput)             // Diagnostic discarded intentionally.
let storedResult = Result { try EmailAddress(rawInput) }    // Diagnostic preserved as data.
let email = try EmailAddress(rawInput)                      // Diagnostic handled by control flow.
```

### Accumulating Validation

Typed throws short-circuits on the first error. Forms and batch imports often need all errors at once.

```swift
struct NonEmptyArray<Element: Sendable>: Sendable {
    let first: Element
    let rest: [Element]

    var values: [Element] { [first] + rest }
}

enum Validated<Value: Sendable, Failure: Sendable>: Sendable {
    case invalid(NonEmptyArray<Failure>)
    case valid(Value)
}

struct SignupDraft: Sendable {
    let email: String
    let password: String
}

enum SignupValidationError: Sendable {
    case email(EmailAddress.Error)
    case passwordTooShort
}

func validate(_ draft: SignupDraft) -> Validated<SignupRequest, SignupValidationError> {
    var errors: [SignupValidationError] = []

    let email: EmailAddress?
    do {
        email = try EmailAddress(draft.email)
    } catch {
        errors.append(.email(error))
        email = nil
    }

    if draft.password.count < 12 {
        errors.append(.passwordTooShort)
    }

    if let first = errors.first {
        return .invalid(NonEmptyArray(first: first, rest: Array(errors.dropFirst())))
    }

    return .valid(SignupRequest(email: email!, password: draft.password))
}
```

For production code, avoid force unwraps by accumulating partial validated fields in local variables or using a small validation builder.

### Failure-Parameterized State

Put the failure axis in the type when downstream code needs it.

```swift
enum LoadState<Value: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case loading(previous: Value?)
    case loaded(Value)
    case failed(Failure, previous: Value?)
}

extension LoadState where Failure == Never {
    var value: Value? {
        switch self {
        case .idle, .loading:
            nil
        case .loaded(let value):
            value
        }
    }
}

struct RetryPolicy<Failure: Error> {
    let shouldRetry: @Sendable (Failure) -> Bool
}
```

Use `Failure == Never` for states that can never fail. Use a concrete failure type when retry, presentation, or recovery depends on the case.

### Validate at Trust Boundaries

Validate once at the boundary, then pass refined values internally.

```swift
struct RawInviteDTO: Decodable {
    let email: String
    let role: String
}

struct Invite: Sendable {
    let email: EmailAddress
    let role: Role

    init(dto: RawInviteDTO) throws(InviteError) {
        do {
            email = try EmailAddress(dto.email)
        } catch {
            throw .invalidEmail(error)
        }

        guard let role = Role(rawValue: dto.role) else {
            throw .unknownRole(dto.role)
        }
        self.role = role
    }
}
```

Do not revalidate `Invite.email` at every call site. The type is the proof.

---

## Concurrency-Aware Type Modeling

### Sendable by Construction

Make `Sendable` a natural consequence of the stored properties.

```swift
struct AccountSnapshot: Sendable {
    let displayName: String
    let id: AccountID
    let plan: Plan
}

struct Parser<Input: Sendable, Output: Sendable, Failure: Error & Sendable>: Sendable {
    let parse: @Sendable (Input) throws(Failure) -> Output
}

extension Page: Sendable where Resource: Sendable {}
```

Avoid `@unchecked Sendable` unless the type has an audited synchronization invariant.

```swift
final class ImageCache: @unchecked Sendable {
    private let lock = Mutex<[ImageID: Data]>([:])

    func data(for id: ImageID) -> Data? {
        lock.withLock { storage in
            storage[id]
        }
    }
}
```

Document the invariant next to the unchecked conformance: all mutable state is reachable only through the lock, actor, queue, or immutable snapshot.

### Isolation as a Type Property

Actor annotations are part of a type's contract.

```swift
@MainActor
final class ProfileViewModel: ObservableObject {
    @Published private(set) var state: LoadState<ProfileSnapshot, ProfileLoadError> = .idle

    private let service: ProfileService

    init(service: ProfileService) {
        self.service = service
    }

    func load() {
        state = .loading(previous: nil)
        Task {
            do {
                let snapshot = try await service.loadProfile()
                state = .loaded(snapshot)
            } catch {
                state = .failed(error, previous: nil)
            }
        }
    }
}
```

Use global actors when the model belongs to a specific subsystem:

```swift
@globalActor
actor PersistenceActor {
    static let shared = PersistenceActor()
}

@PersistenceActor
final class MigrationCoordinator {
    func migrate() async throws(MigrationError) {
        // Serialized by PersistenceActor.
    }
}
```

Use `nonisolated` only for members that truly need no isolated state.

### Swift 6.2 Concurrency Options

Swift 6.2-era toolchains introduced or refined options such as default actor isolation for modules, `@concurrent` on functions, and additional diagnostics. Treat these as project-level choices, not local style.

```swift
@MainActor
final class SearchViewModel: ObservableObject {
    private let index: SearchIndex

    func search(_ query: SearchQuery) {
        Task {
            let results = await performSearch(query)
            self.results = results
        }
    }

    @concurrent
    private func performSearch(_ query: SearchQuery) async -> [SearchResult] {
        await index.search(query)
    }
}
```

The type signature should make isolation visible:

- Main-actor UI model: mark the type `@MainActor`.
- Background work that may run concurrently: make the boundary explicit with the current toolchain's supported spelling.
- Shared mutable identity: use an actor or audited lock wrapper.
- Cross-isolation values: prefer immutable `Sendable` snapshots.

### `sending` Ownership Transfer

Use `sending` when a value is handed to another isolation domain and the caller should not continue using the same logical object.

```swift
actor ImportWorker {
    private var batches: [ImportBatch] = []

    func enqueue(_ batch: sending ImportBatch) {
        batches.append(batch)
    }
}

struct ImportController {
    let worker: ImportWorker

    func submit(_ draft: ImportDraft) async throws(ImportError) {
        let batch = try ImportBatch(draft)
        await worker.enqueue(batch)
    }
}
```

This is most useful for values with non-Sendable internals, unique ownership, or expensive buffers. It is not a replacement for making ordinary DTOs `Sendable`.

### Actor-Bound Snapshots

Keep mutable, reference-heavy, non-Sendable state inside an actor. Export immutable snapshots.

```swift
actor DocumentStore {
    private var document: MutableDocument

    init(document: MutableDocument) {
        self.document = document
    }

    func apply(_ edit: DocumentEdit) {
        document.apply(edit)
    }

    func snapshot() -> DocumentSnapshot {
        DocumentSnapshot(
            id: document.id,
            title: document.title,
            paragraphs: document.paragraphs.map(ParagraphSnapshot.init)
        )
    }
}

struct DocumentSnapshot: Sendable {
    let id: DocumentID
    let title: String
    let paragraphs: [ParagraphSnapshot]
}
```

Do not leak actor-owned mutable references as `nonisolated` properties.

### Task State

Model task lifecycle instead of storing an optional task plus booleans.

```swift
struct RequestID: Hashable, Sendable {
    private let rawValue = UUID()
}

enum TaskState<Output: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case running(id: RequestID)
    case succeeded(Output)
    case failed(Failure)
    case cancelled
}

@MainActor
final class SearchController: ObservableObject {
    @Published private(set) var state: TaskState<[SearchResult], SearchError> = .idle
    private var currentRequestID: RequestID?

    func search(_ query: SearchQuery) {
        let requestID = RequestID()
        currentRequestID = requestID
        state = .running(id: requestID)

        Task {
            do {
                let results = try await fetchResults(query)
                guard currentRequestID == requestID else { return }
                state = .succeeded(results)
            } catch is CancellationError {
                guard currentRequestID == requestID else { return }
                state = .cancelled
            } catch {
                guard currentRequestID == requestID else { return }
                state = .failed(.network(error))
            }
        }
    }
}
```

The request ID prevents stale task results from overwriting newer state.

### MainActor View Models

For SwiftUI or UIKit-facing observable objects, prefer marking the whole view model `@MainActor`.

```swift
@MainActor
final class SettingsViewModel: ObservableObject {
    @Published private(set) var snapshot: SettingsSnapshot

    private let service: SettingsService

    func refresh() {
        Task {
            let snapshot = await service.loadSnapshot()
            self.snapshot = snapshot
        }
    }
}

struct SettingsSnapshot: Sendable {
    let enabledFeatures: [FeatureFlag]
    let username: String
}
```

Background services should return `Sendable` DTOs or snapshots. Do not pass managed objects, mutable caches, or UI-bound references back from background work.

### Lock Wrappers

A lock wrapper should expose operations, not storage.

```swift
import Synchronization

struct Protected<Value: Sendable>: Sendable {
    private let mutex: Mutex<Value>

    init(_ value: Value) {
        mutex = Mutex(value)
    }

    func withValue<Result, Failure: Error>(
        _ body: (inout Value) throws(Failure) -> Result
    ) throws(Failure) -> Result {
        try mutex.withLock { value in
            try body(&value)
        }
    }
}
```

Caveats:

- Returning `Value` may copy stale state. That can be fine for snapshots but not for live mutation.
- Never return `inout`, pointers, or references that outlive the lock.
- Use `@unchecked Sendable` only around a wrapper whose entire mutable surface is guarded.

---

## App, Network, Persistence, and Interop Boundaries

### Typed NotificationCenter Messages

Prefer typed notification messages over string names and `[AnyHashable: Any]` dictionaries when the deployment target provides them.

```swift
struct AccountDidChange: NotificationCenter.Message {
    static let name = Notification.Name("AccountDidChange")

    let accountID: AccountID
    let snapshot: AccountSnapshot
}

extension NotificationCenter {
    func post(_ message: AccountDidChange) {
        post(name: AccountDidChange.name, object: nil, userInfo: [
            "accountID": message.accountID.rawValue,
            "snapshot": message.snapshot
        ])
    }
}
```

Exact Foundation APIs and actor semantics vary by SDK. The modeling rule does not: put the payload in a named type, make isolation explicit, and confine legacy notification dictionaries to the boundary.

### Routes, Sheets, and Alerts

Navigation state is state. Avoid parallel booleans such as `isShowingSheet`, `selectedUser`, and `alertMessage`.

```swift
enum AppRoute: Hashable, Sendable {
    case account(AccountID)
    case project(ProjectID)
    case settings
}

enum PresentedSheet: Identifiable, Sendable {
    case editProfile(AccountID)
    case inviteMember(ProjectID)

    var id: String {
        switch self {
        case .editProfile(let id): "edit-profile-\(id.rawValue)"
        case .inviteMember(let id): "invite-member-\(id.rawValue)"
        }
    }
}

enum AlertState: Sendable {
    case destructiveConfirmation(title: String, action: ConfirmedAction)
    case error(message: String)
}
```

`NavigationPath` is useful for heterogeneous runtime storage, but it erases relationships. Prefer typed route arrays where the app can own the route set.

### Typed Endpoints

Encode request, response, failure, auth, idempotency, content type, and retry assumptions near the endpoint.

```swift
enum PublicAuth {}
enum RequiresUserAuth {}
enum Idempotent {}
enum NonIdempotent {}

struct Endpoint<Request, Response, Failure: Error, Auth, Idempotency>: Sendable {
    let method: HTTPMethod
    let path: PathTemplate
    let encode: @Sendable (Request) throws(EncodingError) -> HTTPBody
    let decode: @Sendable (Data) throws(Failure) -> Response
}

extension Endpoint where Auth == RequiresUserAuth {
    func authorized(by token: AccessToken) -> AuthorizedEndpoint<Request, Response, Failure, Idempotency> {
        AuthorizedEndpoint(endpoint: self, token: token)
    }
}

extension Endpoint where Idempotency == Idempotent {
    var retryPolicy: RetryPolicy<Failure> {
        RetryPolicy { _ in true }
    }
}
```

Do not pass untyped path strings, raw JSON dictionaries, or optional auth tokens through the core networking layer. Put raw request/response shapes at the transport edge and refine immediately.

### Pagination and Cursors

Cursors are scoped to a resource and query. A user cursor should not compile when used for workspace pages.

```swift
struct Cursor<Resource, Query>: Hashable, Sendable {
    private let rawValue: String

    init(rawValue: String) {
        self.rawValue = rawValue
    }
}

struct Page<Resource: Sendable, Query: Sendable>: Sendable {
    let items: [Resource]
    let next: Cursor<Resource, Query>?
}

enum PaginationState<Resource: Sendable, Query: Sendable, Failure: Error & Sendable>: Sendable {
    case idle
    case loadingFirstPage
    case pageLoaded([Resource], next: Cursor<Resource, Query>?)
    case loadingNextPage([Resource], cursor: Cursor<Resource, Query>)
    case failed(Failure, existingItems: [Resource])
    case endReached([Resource])
}
```

Include stale page states when queries can change while a page load is in flight.

### Cache Freshness

Do not encode cache freshness as an untyped `Date?` beside the value.

```swift
enum Freshness: Sendable {
    case fresh(expiresAt: Date)
    case stale(expiredAt: Date)
    case unknown
}

struct Cached<Value: Sendable, Resource>: Sendable {
    let etag: ETag<Resource>?
    let freshness: Freshness
    let value: Value
}

struct ETag<Resource>: Hashable, Sendable {
    let rawValue: String
}
```

APIs that require fresh data can accept `Fresh<Value>` instead of `Cached<Value, Resource>`:

```swift
struct Fresh<Value: Sendable>: Sendable {
    let value: Value
    let expiresAt: Date
}
```

Optimistic updates need their own state. Do not use a stale `isSaving` boolean beside the cached value.

```swift
enum CachedMutation<Value: Sendable, Failure: Error & Sendable>: Sendable {
    case clean(Value)
    case optimistic(current: Value, rollback: Value)
    case rejected(Failure, rollback: Value)
}
```

The rollback value is present only in states that can roll back.

### URL, Path, Query, and Route Parameters

URLs are often built from independently validated pieces. Model those pieces instead of passing interpolated strings through the core.

```swift
struct URLPath<ComponentTag>: RawRepresentable, Hashable, Sendable {
    let rawValue: String

    init?(rawValue: String) {
        guard rawValue.first == "/", !rawValue.contains("//") else { return nil }
        self.rawValue = rawValue
    }
}

struct QueryParameter<Value>: Sendable {
    let name: String
    let encode: @Sendable (Value) -> String
}

struct RouteParameter<Route, Value>: Sendable {
    let name: String
}

enum UserDetailRoute {}

extension RouteParameter where Route == UserDetailRoute, Value == UserID {
    static let userID = RouteParameter(name: "userID")
}
```

Typed route and query parameters prevent a workspace ID, raw search string, or unescaped path component from being substituted where a user ID or encoded query value is required.

### Persistence Lifecycle

Draft, saved, deleted, and migrated records have different legal operations.

```swift
enum Draft {}
enum Saved {}
enum Deleted {}

struct PersistentID<Entity>: Hashable, Sendable {
    let rawValue: UUID
}

struct Record<Entity, State>: Sendable {
    let id: PersistentID<Entity>?
    let value: Entity
}

extension Record where State == Draft {
    func save(into store: Store) throws(PersistenceError) -> Record<Entity, Saved> {
        let id = try store.insert(value)
        return Record<Entity, Saved>(id: id, value: value)
    }
}

extension Record where State == Saved {
    func markDeleted() -> Record<Entity, Deleted> {
        Record<Entity, Deleted>(id: id, value: value)
    }
}
```

If the lifecycle becomes too generic or hard to read, collapse it to an enum:

```swift
enum PersistentRecord<Value: Sendable>: Sendable {
    case draft(Value)
    case saved(id: PersistentID<Value>, value: Value)
    case deleted(id: PersistentID<Value>)
}
```

### Database, SwiftData, and Core Data

Persistent model classes are often mutable, reference-typed, context-bound, and not safely Sendable. Map them to immutable domain snapshots before crossing concurrency or module boundaries.

```swift
@Model
final class ProjectModel {
    var id: UUID
    var name: String
    var ownerID: UUID
}

struct ProjectSnapshot: Sendable {
    let id: ProjectID
    let name: NonEmptyString
    let ownerID: UserID

    init(model: ProjectModel) throws(ProjectMappingError) {
        id = ProjectID(rawValue: model.id)
        ownerID = UserID(rawValue: model.ownerID)
        name = try NonEmptyString(model.name)
    }
}
```

For SQL, model tables, columns, predicates, and parameters instead of interpolating strings.

```swift
struct Table<Row> {
    let name: SQLIdentifier
}

struct Column<Row, Value> {
    let name: SQLIdentifier
}

struct SQL<Parameters> {
    fileprivate let text: String
    fileprivate let parameters: Parameters
}

func equal<Row, Value>(_ column: Column<Row, Value>, _ value: Value) -> SQL<[Value]> {
    SQL(text: "\(column.name.escaped) = ?", parameters: [value])
}
```

The type `SQL<[Value]>` does not prove the query is correct by itself. It proves callers cannot bypass parameter binding if raw SQL initializers are private.

### Objective-C Boundaries

Objective-C and legacy Cocoa APIs frequently expose nullable references, `Any`, `NSDictionary`, string constants, and `NSError`.

```swift
struct PasteboardPayload: Sendable {
    let string: NonEmptyString
    let sourceApplication: BundleIdentifier?

    init(userInfo: NSDictionary) throws(PasteboardPayloadError) {
        guard let rawString = userInfo["string"] as? String else {
            throw .missingString
        }
        string = try NonEmptyString(rawString)

        if let rawBundleID = userInfo["source"] as? String {
            sourceApplication = BundleIdentifier(rawBundleID)
        } else {
            sourceApplication = nil
        }
    }
}
```

Map `NSError` into local typed errors at the boundary when callers can recover by case. Keep `NSError` when the API is only forwarding platform diagnostics.

### C and C++ Boundaries

Quarantine pointers, callbacks, and ownership conventions.

```swift
struct DecoderHandle: ~Copyable {
    private let handle: OpaquePointer

    init(config: DecoderConfig) throws(DecoderError) {
        guard let handle = decoder_create(config.rawValue) else {
            throw .creationFailed
        }
        self.handle = handle
    }

    borrowing func decode(_ bytes: borrowing RawSpan) throws(DecoderError) -> Frame {
        // Bridge borrowed bytes to the C API inside this method only.
    }

    deinit {
        decoder_destroy(handle)
    }
}
```

Use `BitwiseCopyable` only for Swift types whose binary layout promise is intentional. Use `Span` or closure-scoped unsafe buffers for borrowed memory. Use `~Copyable` for ownership.

### File and Path Modeling

Paths carry more invariants than `String`.

```swift
enum Exists {}
enum Unchecked {}

struct AbsolutePath<State>: Hashable, Sendable {
    let stringValue: String

    init?(_ stringValue: String) {
        guard stringValue.hasPrefix("/") else { return nil }
        self.stringValue = stringValue
    }
}

struct DirectoryPath<State>: Hashable, Sendable {
    let path: AbsolutePath<State>
}

extension AbsolutePath where State == Unchecked {
    func requireExistingFile() throws(FileError) -> AbsolutePath<Exists> {
        guard FileManager.default.fileExists(atPath: stringValue) else {
            throw .notFound(stringValue)
        }
        return AbsolutePath<Exists>(stringValue)!
    }
}

struct TemporaryFile: ~Copyable {
    let path: AbsolutePath<Exists>

    deinit {
        try? FileManager.default.removeItem(atPath: path.stringValue)
    }
}
```

Model sandbox and security-scoped access as capabilities:

```swift
struct SecurityScopedAccess: ~Copyable {
    private let url: URL

    init?(url: URL) {
        guard url.startAccessingSecurityScopedResource() else { return nil }
        self.url = url
    }

    borrowing func withURL<Result>(_ body: (URL) throws -> Result) rethrows -> Result {
        try body(url)
    }

    deinit {
        url.stopAccessingSecurityScopedResource()
    }
}
```

### Platform Availability as Capability

Avoid scattering `if #available` through core logic. Create a capability value at the boundary.

```swift
struct LiveTextCapability: Sendable {
    private init() {}

    static func current() -> LiveTextCapability? {
        guard #available(iOS 16, macOS 13, *) else { return nil }
        return LiveTextCapability()
    }
}

func scanText(in image: ImageSnapshot, using capability: LiveTextCapability) async throws(ScanError) -> [RecognizedText] {
    // This function can assume the platform capability exists.
}
```

The capability type proves the availability check happened. It does not prove user permission, hardware availability, or runtime service success unless those are also encoded.

---

## Security and Privacy Modeling

### Authentication State

Avoid `isLoggedIn` plus optional tokens.

```swift
enum Session: Sendable {
    case unauthenticated
    case authenticated(AuthenticatedSession)
    case expired(ExpiredSession)
}

struct AuthenticatedSession: Sendable {
    let accessToken: Secret<AccessToken>
    let refreshToken: Secret<RefreshToken>
    let userID: UserID

    func elevate(with challenge: MFAChallenge) async throws(AuthError) -> ElevatedSession {
        // ...
    }
}

struct ElevatedSession: Sendable {
    fileprivate let base: AuthenticatedSession
}

struct ExpiredSession: Sendable {
    let refreshToken: Secret<RefreshToken>
}
```

Operations that need auth should accept `AuthenticatedSession` or a narrower capability, not `Session`.

### Authorization Capabilities

Represent authorization by possession of a value whose initializer is private.

```swift
struct CanEdit<Project>: Sendable {
    private let projectID: ProjectID

    private init(projectID: ProjectID) {
        self.projectID = projectID
    }

    static func issue(
        for projectID: ProjectID,
        policy: AuthorizationPolicy,
        session: AuthenticatedSession
    ) throws(AuthorizationError) -> CanEdit<Project> {
        guard policy.canEdit(projectID, userID: session.userID) else {
            throw .denied
        }
        return CanEdit<Project>(projectID: projectID)
    }
}

func updateProject(_ project: ProjectDraft, using capability: CanEdit<Project>) async throws(ProjectError) {
    // No isAdmin boolean check needed here.
}
```

Capability tokens are only meaningful if callers cannot forge them. Keep initializers private or internal to the authorization module.

### Secrets

Secrets should not accidentally print, log, encode, compare, or appear in crash metadata.

```swift
struct Secret<Value: Sendable>: Sendable {
    private let value: Value

    init(_ value: Value) {
        self.value = value
    }

    func reveal<Result>(_ body: (Value) throws -> Result) rethrows -> Result {
        try body(value)
    }
}

extension Secret: CustomStringConvertible, CustomDebugStringConvertible {
    var description: String { "<redacted>" }
    var debugDescription: String { "<redacted>" }
}
```

Do not add `Codable`, `Equatable`, or `Hashable` to `Secret` unless the security review says those operations are acceptable for that specific value.

### PII and Logging

Type signatures can prevent raw personally identifiable information from reaching analytics and logs.

```swift
struct PII<Value: Sendable>: Sendable {
    fileprivate let value: Value
}

struct Redacted<Value: Sendable>: Sendable, CustomStringConvertible {
    let original: PII<Value>
    let description: String
}

struct PublicAnalyticsValue: Sendable {
    let value: String
}

func redactEmail(_ email: PII<EmailAddress>) -> Redacted<EmailAddress> {
    Redacted(original: email, description: "<email>")
}

func log(_ value: PublicAnalyticsValue) {
    analytics.log(value.value)
}
```

Do not let analytics APIs accept `String` when some strings are private. Accept `PublicAnalyticsValue`, `Redacted<Value>`, or a typed event payload whose fields have already been classified.

### Crypto States

Model cryptographic state transitions explicitly.

```swift
enum Plaintext {}
enum Encrypted<Algorithm> {}
enum Hashed<Algorithm> {}
enum Signed<Key> {}
enum Verified<Signature> {}

struct CryptoData<State>: Sendable {
    fileprivate let bytes: Data
}

struct AESGCM {}
struct PasswordHashAlgorithm {}

func encrypt(_ data: CryptoData<Plaintext>, with key: Secret<SymmetricKey>) throws(CryptoError) -> CryptoData<Encrypted<AESGCM>> {
    // ...
}

func hashPassword(_ password: Secret<Password>) throws(CryptoError) -> CryptoData<Hashed<PasswordHashAlgorithm>> {
    // ...
}

func verify(_ signed: CryptoData<Signed<SigningKey>>) throws(CryptoError) -> CryptoData<Verified<Signature>> {
    // ...
}
```

The type tracks which operation happened. It does not prove the algorithm is appropriate, the key was generated correctly, or a nonce was unique. Model those too when the risk is high:

```swift
struct Nonce<Algorithm>: Sendable {
    fileprivate let bytes: Data
}

struct UniqueNonceGenerator<Algorithm>: ~Copyable {
    mutating func next() -> Nonce<Algorithm> {
        // Centralized uniqueness policy.
    }
}
```

### HTML, SQL, and Shell Safety

Use state tags for raw versus safe text. Make rendering or execution APIs require the safe state.

```swift
enum Raw {}
enum EscapedHTML {}
enum ParameterizedSQL {}
enum ShellArgumentEscaped {}

struct HTML<State>: Sendable {
    fileprivate let value: String
}

func escapeHTML(_ raw: HTML<Raw>) -> HTML<EscapedHTML> {
    HTML<EscapedHTML>(value: raw.value.htmlEscaped())
}

func render(_ html: HTML<EscapedHTML>) -> String {
    html.value
}
```

SQL should prefer parameterization over escaping:

```swift
struct Query<State, Parameters>: Sendable {
    fileprivate let text: String
    fileprivate let parameters: Parameters
}

func selectUser(id: UserID) -> Query<ParameterizedSQL, [UUID]> {
    Query(text: "select * from users where id = ?", parameters: [id.rawValue])
}

func execute(_ query: Query<ParameterizedSQL, [UUID]>) throws(DatabaseError) -> [Row] {
    // Bind parameters through the database driver.
}
```

Shell execution should avoid shell strings entirely when possible:

```swift
struct ExecutablePath: Sendable {
    let path: AbsolutePath<Exists>
}

struct ProcessArguments: Sendable {
    let values: [String]
}

func run(_ executable: ExecutablePath, arguments: ProcessArguments) throws(ProcessError) {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: executable.path.stringValue)
    process.arguments = arguments.values
    try process.run()
}
```

If a shell string is unavoidable, require a distinct escaped or quoted type and centralize construction. Do not let arbitrary `String` flow into execution.

---

## Boundary Checklist

Before introducing one of these types, answer:

1. What invariant does this type prove: ownership, lifetime, isolation, validation, authority, trust, freshness, persistence lifecycle, or platform capability?
2. Where is the raw boundary: JSON, database, Objective-C, C, C++, files, notifications, analytics, user input, or network?
3. Which initializer or factory produces the proof?
4. Can callers bypass that factory through public mutable storage, raw initializers, synthesized decoding, marker conformances, or unchecked casts?
5. Does the type need to cross concurrency domains? If yes, is it `Sendable` by construction or transferred with `sending`?
6. Is the safety worth the complexity? If the value is local to one function, inline validation is usually clearer.
