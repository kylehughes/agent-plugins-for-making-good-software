# Generics, Phantom Types, and Protocol Relationships

This reference expands the generic-state side of type-driven design: phantom tags,
capability tokens, associated-type relationships, constrained existentials, and
type erasure that preserves the axes that matter.

The recurring rule: a type only proves an invariant when invalid construction is
impossible through every accessible API. A pretty generic signature is not enough
if callers can still forge the value, conform to the marker protocol, or erase
the relationship through `any`.

## Newtype vs Typealias

A `typealias` gives a better name to an existing type. It does not create a new
type, so it does not prevent accidental swaps.

Wrong but tempting:

```swift
typealias UserID = String
typealias WorkspaceID = String

func loadUser(id: UserID, in workspaceID: WorkspaceID) async throws -> User

// Compiles: both aliases are just String.
try await loadUser(id: workspaceID, in: userID)
```

Use a nominal wrapper when the compiler should distinguish values.

```swift
struct Tagged<Tag, RawValue>: RawRepresentable, Sendable {
    let rawValue: RawValue
}

enum UserTag {}
enum WorkspaceTag {}

typealias UserID = Tagged<UserTag, String>
typealias WorkspaceID = Tagged<WorkspaceTag, String>

func loadUser(id: UserID, in workspaceID: WorkspaceID) async throws -> User
```

Keep the initializer as open as the invariant permits. A public
`init(rawValue:)` is fine for identity domains where any raw ID can be passed
around. It is not fine for values that claim validation, permission, trust, or
ownership.

```swift
struct EmailAddress: Sendable {
    let value: String

    init(_ value: String) throws(ValidationError) {
        guard value.contains("@") else { throw .missingAtSign }
        self.value = value
    }
}
```

## Sealed Tags and Public Marker Caveats

Empty enum tags are useful because they cannot be instantiated:

```swift
enum Validated {}
enum Unvalidated {}

struct Form<State>: Sendable {
    let fields: [String: String]
}
```

The tag being uninhabited does not make the wrapper unforgeable. If the wrapper
initializer is accessible, any caller can construct any state.

Wrong but tempting:

```swift
public enum Sanitized {}

public struct HTML<State>: Sendable {
    public let value: String

    public init(value: String) {
        self.value = value
    }
}

// Compiles: no sanitizer ran.
let forged = HTML<Sanitized>(value: userInput)
```

Control construction for states that represent proof.

```swift
public enum RawHTML {}
public enum SanitizedHTML {}

public struct HTML<State>: Sendable {
    public let value: String

    fileprivate init(value: String) {
        self.value = value
    }

    public static func raw(_ value: String) -> HTML<RawHTML> {
        HTML<RawHTML>(value: value)
    }
}

public func sanitize(_ html: HTML<RawHTML>) -> HTML<SanitizedHTML> {
    HTML<SanitizedHTML>(value: escape(html.value))
}
```

Public marker protocols are also forgeable. Any downstream module can conform a
type unless conformance is controlled by access control or construction.

Wrong but tempting:

```swift
public protocol Sanitized {}

public func render<T: Sanitized>(_ value: T) {
    // The generic constraint does not prove escaping happened.
}

extension String: Sanitized {}
render(userInput)
```

Marker protocols prove something only when one of these is true:

- The protocol is internal or private to the module that creates all conformers.
- The conforming types have private initializers and can only be built by proof
  producing functions.
- The public API accepts a sealed wrapper, enum, or capability token instead of
  accepting arbitrary conformers.
- The protocol is not used as a proof. It is only documentation or overload
  selection.

Swift has no native sealed public protocol feature. For public closed sets,
prefer an enum or a wrapper with private initialization. For package-internal
closed sets, internal protocols and internal tag types are usually enough.

## Opaque and Capability Tokens

A capability should be modeled as possession of a value, not as a boolean.

Wrong but tempting:

```swift
struct Session {
    let token: String
    let isAdmin: Bool
}

func deleteUser(id: UserID, session: Session) async throws {
    guard session.isAdmin else { throw AuthorizationError.denied }
    // ...
}
```

This spreads authorization checks across the codebase and lets unrelated code
claim `isAdmin`.

Use a token whose initializer is not public. The token is minted only by the
policy check.

```swift
public enum AdminPermission {}

public struct Capability<Permission>: Sendable {
    fileprivate let sessionID: SessionID

    fileprivate init(sessionID: SessionID) {
        self.sessionID = sessionID
    }
}

public typealias AdminCapability = Capability<AdminPermission>

public func requireAdmin(_ session: Session) throws(AuthorizationError) -> AdminCapability {
    guard session.roles.contains(.admin) else { throw .denied }
    return AdminCapability(sessionID: session.id)
}

public func deleteUser(id: UserID, using capability: AdminCapability) async throws {
    // No authorization branch here. The function requires proof.
}
```

The same pattern works for `CSRFToken`, `AccessToken`, `RefreshToken`,
`DatabaseTransaction<Active>`, `WriteAccess<Project>`, `CameraPermission`, and
scoped security access. The important property is unforgeability. Wrapping a
string is not enough if the wrapper initializer is public.

## Trust and Taint Types

Trust boundaries should produce refined values. Raw values enter at the edge;
validated or sanitized values flow through the core.

```swift
enum Untrusted {}
enum Validated {}

struct Input<State>: Sendable {
    let value: String

    fileprivate init(_ value: String) {
        self.value = value
    }

    static func untrusted(_ value: String) -> Input<Untrusted> {
        Input<Untrusted>(value)
    }
}

func validateUsername(
    _ input: Input<Untrusted>
) throws(UsernameError) -> Input<Validated> {
    guard input.value.count >= 3 else { throw .tooShort }
    return Input<Validated>(input.value)
}
```

Common taint axes:

- `HTML<Raw>` -> `HTML<Sanitized>`
- `SQL<Raw>` -> `SQL<Parameterized>`
- `Input<Untrusted>` -> `Input<Validated>`
- `Data<Plaintext>` -> `Data<Encrypted>`
- `Password<Plaintext>` -> `Password<Hashed>`
- `FilePath<Unchecked>` -> `FilePath<Exists>`

Wrong but tempting:

```swift
func execute(sql: String) async throws -> Rows

let sql = "SELECT * FROM users WHERE id = \(userInput)"
try await execute(sql: sql)
```

Prefer a parameterized wrapper that can only be built through APIs that separate
structure from values.

```swift
enum RawSQL {}
enum ParameterizedSQL {}

struct SQL<State>: Sendable {
    let statement: String
    let bindings: [DatabaseValue]

    private init(statement: String, bindings: [DatabaseValue]) {
        self.statement = statement
        self.bindings = bindings
    }

    static func parameterized(
        _ statement: String,
        _ bindings: DatabaseValue...
    ) -> SQL<ParameterizedSQL> {
        SQL<ParameterizedSQL>(statement: statement, bindings: bindings)
    }
}

func execute(_ sql: SQL<ParameterizedSQL>) async throws(DatabaseError) -> Rows
```

## Units, Dimensions, and Money

Use phantom tags when numeric values share a representation but cannot be mixed.

Wrong but tempting:

```swift
typealias Meters = Double
typealias Seconds = Double

func speed(distance: Meters, time: Seconds) -> Double {
    distance / time
}

speed(distance: duration, time: distance) // Compiles.
```

Use a `Quantity` wrapper.

```swift
struct Quantity<Unit, Value: Sendable>: Sendable {
    let value: Value
}

enum Meters {}
enum Seconds {}
enum MetersPerSecond {}

typealias Distance = Quantity<Meters, Double>
typealias Duration = Quantity<Seconds, Double>
typealias Speed = Quantity<MetersPerSecond, Double>

func speed(distance: Distance, time: Duration) -> Speed {
    Speed(value: distance.value / time.value)
}
```

Keep operations constrained to dimensions that make sense.

```swift
extension Quantity where Value == Double {
    static func + (lhs: Self, rhs: Self) -> Self {
        Self(value: lhs.value + rhs.value)
    }
}

func convert(_ distance: Quantity<Meters, Double>) -> Quantity<Feet, Double> {
    Quantity<Feet, Double>(value: distance.value * 3.28084)
}
```

Money needs a stricter model than ordinary units:

- Do not use `Double` for stored money. Use minor units (`Int64`) or `Decimal`
  with explicit rounding rules.
- Include currency in the type when mixing currencies is a real risk.
- Make exchange rates explicit typed conversions.
- Do not add different currencies without conversion.

```swift
struct Money<Currency>: Sendable {
    let minorUnits: Int64
}

enum USD {}
enum EUR {}

func + <Currency>(lhs: Money<Currency>, rhs: Money<Currency>) -> Money<Currency> {
    Money(minorUnits: lhs.minorUnits + rhs.minorUnits)
}

struct ExchangeRate<From, To>: Sendable {
    let ratio: Decimal
}

func convert<From, To>(
    _ amount: Money<From>,
    using rate: ExchangeRate<From, To>
) -> Money<To> {
    let converted = Decimal(amount.minorUnits) * rate.ratio
    return Money<To>(minorUnits: roundedMinorUnits(converted))
}
```

Wrong but tempting:

```swift
let total = usdAmount.minorUnits + eurAmount.minorUnits
```

If the domain accepts arbitrary ISO currency codes at runtime, a pure phantom tag
may be too rigid. Use a validated `CurrencyCode` value and check equality at
runtime, or use known phantom currencies only in the layer where currencies are
statically known.

## Coordinate Spaces

Coordinate bugs are common in UIKit, SwiftUI, graphics, and image pipelines.
Local, global, screen, safe-area, point, and pixel coordinates often share the
same numeric fields.

```swift
struct Point<Space>: Sendable {
    let x: Double
    let y: Double
}

struct Size<Unit>: Sendable {
    let width: Double
    let height: Double
}

struct Rect<Space>: Sendable {
    let origin: Point<Space>
    let size: Size<Space>
}

enum ScreenSpace {}
enum ViewSpace<ViewTag> {}
enum ImagePixels {}
enum LayoutPoints {}
```

Conversion functions should produce the proof.

```swift
func convert<ViewTag>(
    _ point: Point<ViewSpace<ViewTag>>,
    toScreenUsing view: ViewReference<ViewTag>
) -> Point<ScreenSpace> {
    let converted = view.convertToScreen(x: point.x, y: point.y)
    return Point<ScreenSpace>(x: converted.x, y: converted.y)
}
```

Wrong but tempting:

```swift
func draw(handleCenter: CGPoint, imagePixelSize: CGSize) {
    // Both values look geometric, but one may be in view points and one in pixels.
}
```

Use phantom coordinate tags when values cross helper, rendering, or module
boundaries. For values used in one local drawing expression, raw `CGPoint` and
`CGSize` are usually clearer.

## Image, Buffer, and Format Tags

Image and buffer APIs often need several independent invariant axes: pixel
format, color space, orientation, initialization state, ownership, and sample
rate.

```swift
enum RGBA8 {}
enum BGRA8 {}
enum DisplayP3 {}
enum SRGB {}
enum Initialized {}
enum Uninitialized {}

struct Image<PixelFormat, ColorSpace>: Sendable {
    let width: Int
    let height: Int
    private let bytes: Data
}

struct Buffer<State, Element>: ~Copyable {
    private let storage: UnsafeMutableBufferPointer<Element>

    fileprivate init(storage: UnsafeMutableBufferPointer<Element>) {
        self.storage = storage
    }
}
```

Expose operations only for states and formats where they are valid.

```swift
extension Buffer where State == Uninitialized {
    consuming func initialize(repeating value: Element) -> Buffer<Initialized, Element> {
        storage.initialize(repeating: value)
        return Buffer<Initialized, Element>(storage: storage)
    }
}

extension Buffer where State == Initialized {
    borrowing func read(at index: Int) -> Element {
        storage[index]
    }
}
```

Wrong but tempting:

```swift
struct Image {
    let format: String
    let colorSpace: String
    let bytes: Data
}

func uploadRGBA(_ image: Image) {
    precondition(image.format == "RGBA8")
}
```

If the valid set is small and closed, prefer tags or enums over strings. If the
format is discovered dynamically from user files, decode into a runtime enum,
then refine into format-specific wrappers only for code paths that need static
format guarantees.

## Integer Generic Parameters

Integer generic parameters carry small literal integer facts in the type. They
are useful for sizes, dimensions, fixed capacities, channel counts, and key
lengths.

```swift
struct Vector<let count: Int, Element> {
    private var storage: InlineArray<count, Element>
}

struct Matrix<let rows: Int, let columns: Int, Scalar> {
    private var values: InlineArray<rows, InlineArray<columns, Scalar>>
}

func multiply<let m: Int, let n: Int, let p: Int>(
    _ lhs: Matrix<m, n, Double>,
    _ rhs: Matrix<n, p, Double>
) -> Matrix<m, p, Double> {
    // The shared n dimension is enforced by the type signature.
}
```

Good uses:

- `Vector<3, Double>` for 3D math.
- `Matrix<4, 4, Float>` for transforms.
- `InlineArray<16, UInt8>` for cryptographic key bytes.
- `Image<RGBA8>` or `Pixel<4, UInt8>` for channel counts.
- Fixed-capacity buffers where the capacity is part of the API contract.

Wrong but tempting:

```swift
func normalize(_ values: [Double], expectedCount: Int) -> [Double] {
    precondition(values.count == expectedCount)
    // ...
}
```

Use integer generics only when the size is static enough to appear in the type.
Swift is not dependently typed: a runtime `Int` from JSON, a database, or user
input does not become a compile-time integer generic argument. Validate runtime
sizes at the boundary, then either keep a runtime-sized collection or switch over
known sizes into statically sized cases.

## Typestate with Constrained Extensions

Typestate removes invalid operations by making them absent from the type.

```swift
enum Unvalidated {}
enum Validated {}
enum Submitted {}

struct Registration<State>: Sendable {
    private let fields: [String: String]

    private init(fields: [String: String]) {
        self.fields = fields
    }

    static func editing(fields: [String: String]) -> Registration<Unvalidated> {
        Registration<Unvalidated>(fields: fields)
    }
}

extension Registration where State == Unvalidated {
    func validate() throws(ValidationError) -> Registration<Validated> {
        try validateFields(fields)
        return Registration<Validated>(fields: fields)
    }
}

extension Registration where State == Validated {
    func submit() async throws(NetworkError) -> Registration<Submitted> {
        try await upload(fields)
        return Registration<Submitted>(fields: fields)
    }
}
```

Wrong but tempting:

```swift
struct Registration {
    var fields: [String: String]
    var isValidated: Bool

    func submit() async throws {
        precondition(isValidated)
    }
}
```

Use constrained extensions for operations that are truly state-specific. If most
operations are shared and the state changes frequently during design, an enum
state field may be easier to maintain.

## Multi-Axis Typestate and Scaling

Phantom axes compose:

```swift
enum MissingAuth {}
enum HasAuth {}
enum NoBody {}
enum HasBody {}
enum Undecoded {}
enum Decoded {}

struct Request<AuthState, BodyState, ResponseState>: Sendable {
    private let url: URL
    private let body: Data?
}

extension Request where AuthState == MissingAuth {
    func authenticated(with token: AccessToken) -> Request<HasAuth, BodyState, ResponseState> {
        Request<HasAuth, BodyState, ResponseState>(url: url, body: body)
    }
}

extension Request where BodyState == NoBody {
    func body(_ data: Data) -> Request<AuthState, HasBody, ResponseState> {
        Request<AuthState, HasBody, ResponseState>(url: url, body: data)
    }
}

func send(_ request: Request<HasAuth, HasBody, Undecoded>) async throws -> Response
```

This is powerful but can become a generic cross-product. Collapse to an enum or
a runtime validator when:

- The number of axes grows beyond what call sites can read.
- Requirements change often.
- Invalid combinations are rare or low impact.
- Most APIs need to accept many states.
- The generic parameters start leaking into unrelated types.

Group related axes when possible:

```swift
enum RequestReadiness {
    case missingAuth
    case missingBody
    case ready
}

struct Request<State>: Sendable {
    // Fewer generic axes, simpler diagnostics.
}
```

## Phantom Builders and Required Fields

A staged phantom builder can make `build()` unavailable until required fields
are present.

```swift
enum MissingName {}
enum HasName {}
enum MissingEmail {}
enum HasEmail {}

struct UserBuilder<NameState, EmailState> {
    private let name: String?
    private let email: EmailAddress?

    private init(name: String?, email: EmailAddress?) {
        self.name = name
        self.email = email
    }

    static func start() -> UserBuilder<MissingName, MissingEmail> {
        UserBuilder<MissingName, MissingEmail>(name: nil, email: nil)
    }
}

extension UserBuilder where NameState == MissingName {
    func name(_ name: String) -> UserBuilder<HasName, EmailState> {
        UserBuilder<HasName, EmailState>(name: name, email: email)
    }
}

extension UserBuilder where EmailState == MissingEmail {
    func email(_ email: EmailAddress) -> UserBuilder<NameState, HasEmail> {
        UserBuilder<NameState, HasEmail>(name: name, email: email)
    }
}

extension UserBuilder where NameState == HasName, EmailState == HasEmail {
    func build() -> User {
        User(name: name!, email: email!)
    }
}
```

The forced unwraps are acceptable only because all stored properties are private,
all transitions are controlled, and no public initializer can create
`UserBuilder<HasName, HasEmail>` with nil fields. If those conditions are not
true, the type does not prove the invariant.

Phantom builders scale poorly with many required fields: five independent fields
can imply 32 states. Use them when missing fields are a common bug and the set is
stable. Otherwise prefer:

- A validating initializer with a typed error.
- Grouped required structs, such as `UserIdentity` plus `ContactInfo`.
- A result builder that returns a validating output type.
- A macro that generates the staged boilerplate while keeping the generated code
  inspectable.

## Result Builder Required-Field Caveats

A result builder does not automatically prove required fields. Most simple
builders collect values into an array, which accepts missing, duplicated, or
conditional fields unless the builder API prevents them.

Wrong but tempting:

```swift
@resultBuilder
struct FormBuilder {
    static func buildBlock(_ fields: Field...) -> [Field] {
        fields
    }
}

struct Form {
    let fields: [Field]

    init(@FormBuilder _ fields: () -> [Field]) {
        self.fields = fields()
    }
}

let form = Form {
    TextField("Name")
    // Missing email compiles.
}
```

Builders can help when paired with another proof mechanism:

- Staged APIs for required fields, then a builder for repeated optional content.
- Overloads that only form a complete output for known required combinations.
- Phantom state in the builder output.
- A validating initializer that returns a refined type.
- A macro that generates the overloads or staged builder.

Control flow weakens compile-time structure. `buildOptional`, `buildEither`, and
`buildArray` allow values to be absent, mutually exclusive, or repeated based on
runtime conditions.

```swift
let form = Form {
    if includeEmail {
        EmailField()
    }
}
```

If `EmailField` is required, the builder must reject that grammar or return a
type that still needs validation.

## Macro and Literal Validation Caveats

Macros are useful for generating repetitive proof plumbing: newtypes, typed IDs,
controlled `Codable`, case paths, staged builders, and literal diagnostics. They
should not hide the domain rule.

Good use:

```swift
let route = #RouteLiteral("/users/:id")
let regex = #RegexLiteral("[A-Z]{3}-[0-9]{4}")
```

Literal validation macros can reject static mistakes at compile time. They
cannot validate a string that arrives at runtime.

Wrong but tempting:

```swift
func route(from serverValue: String) -> Route {
    #RouteLiteral(serverValue) // A macro cannot prove a dynamic value.
}
```

Runtime values still need validating initializers:

```swift
struct Route: Sendable {
    let pattern: String

    init(_ pattern: String) throws(RouteError) {
        try validateRoutePattern(pattern)
        self.pattern = pattern
    }
}
```

Literal protocols have the same caveat. `ExpressibleByStringLiteral` cannot
fail, so it is a poor public initializer for validated values unless a macro
checks the literal before expansion or the conformance is limited to tests.

Wrong but tempting:

```swift
struct EmailAddress: ExpressibleByStringLiteral {
    let value: String

    init(stringLiteral value: String) {
        self.value = value // Cannot reject invalid literals.
    }
}
```

Generated boilerplate must preserve access control. A macro that creates a
public memberwise initializer for `HTML<Sanitized>` or `Capability<Admin>` has
destroyed the invariant it was supposed to protect.

## Associated-Type Relationships

Protocols with associated types model relationships between roles. The point is
not abstraction by itself; the point is preserving which input, output, ID, and
failure types belong together.

```swift
protocol Identified {
    associatedtype ID: Hashable & Sendable

    var id: ID { get }
}

protocol Repository<Entity> {
    associatedtype Entity: Identified & Sendable

    func load(id: Entity.ID) async throws(RepositoryError) -> Entity
    func save(_ entity: Entity) async throws(RepositoryError)
}
```

Other useful relationship protocols:

```swift
protocol Parser<Input, Output, Failure> {
    associatedtype Input
    associatedtype Output
    associatedtype Failure: Error

    func parse(_ input: Input) throws(Failure) -> Output
}

protocol Endpoint<Request, Response, Failure> {
    associatedtype Request: Sendable
    associatedtype Response: Sendable
    associatedtype Failure: Error

    func perform(_ request: Request) async throws(Failure) -> Response
}

protocol Store<Key, Value> {
    associatedtype Key: Hashable
    associatedtype Value

    subscript(key: Key) -> Value? { get set }
}

protocol Validator<Input, Failure> {
    associatedtype Input
    associatedtype Failure: Error

    func validate(_ input: Input) throws(Failure) -> Input
}
```

Wrong but tempting:

```swift
protocol Repository {
    func load(id: AnyHashable) async throws -> Any
    func save(_ entity: Any) async throws
}
```

This erases the relationship between entity and ID. The compiler cannot stop a
workspace ID from being used to load a user.

## Same-Type Constraints

Same-type constraints are one of Swift's strongest tools for proving
relationships between generic values.

```swift
func mirror<A: Repository, B: Repository>(
    id: A.Entity.ID,
    from source: A,
    to destination: B
) async throws
where A.Entity == B.Entity {
    let entity = try await source.load(id: id)
    try await destination.save(entity)
}
```

Use same-type constraints for:

- `A.Entity.ID == B.Entity.ID` when two APIs must share an ID domain.
- `Element == User` when a generic collection operation is only valid for users.
- `Failure == Never` when a value cannot fail.
- `State == Validated` when an operation requires a refined state.
- `Root == User` for key-path, predicate, or form-field APIs.
- `Request == Endpoint.Request` and `Response == Endpoint.Response` in networking
  pipelines.

```swift
extension Parser where Failure == Never {
    func parseInfallibly(_ input: Input) -> Output {
        try! parse(input)
    }
}

func attach<UserFields: Collection>(
    _ fields: UserFields,
    to user: User
) where UserFields.Element == Field<User> {
    // Every field belongs to User.
}
```

Avoid runtime casts when a same-type constraint can express the relationship.

Wrong but tempting:

```swift
func connect(_ output: any Parser, to input: any Parser) {
    // Runtime casts needed because Output and Input relationships are gone.
}
```

## Primary Associated Types and Constrained Existentials

Primary associated types let call sites constrain the important axes of a
protocol existential.

```swift
let parser: any Parser<Substring, Int, ParseError>
let validator: any Validator<EmailAddress, EmailValidationError>
```

This is safer than fully erasing the protocol:

```swift
let parsers: [any Parser<Substring, Int, ParseError>]
```

Every stored parser accepts `Substring`, returns `Int`, and throws
`ParseError`. The concrete parser implementation can vary.

Wrong but tempting:

```swift
let parsers: [any Parser]

for parser in parsers {
    // What Input does this parser accept?
    // What Output does it return?
    // What Failure can it throw?
}
```

Constrained existentials are useful for heterogeneous storage after the
relationship axes are fixed. If the caller must choose the concrete type and the
function should preserve that type, use a generic parameter instead.

```swift
func run<P: Parser>(_ parser: P, input: P.Input) throws(P.Failure) -> P.Output {
    try parser.parse(input)
}
```

## Conditional Conformance

Do not over-constrain the base type. Add capabilities only when stored values
support them.

```swift
struct Tagged<Tag, RawValue> {
    let rawValue: RawValue
}

extension Tagged: Equatable where RawValue: Equatable {}
extension Tagged: Hashable where RawValue: Hashable {}
extension Tagged: Sendable where RawValue: Sendable {}
extension Tagged: Codable where RawValue: Codable {}
extension Tagged: BitwiseCopyable where RawValue: BitwiseCopyable {}
```

Wrong but tempting:

```swift
struct Tagged<Tag, RawValue: Codable & Hashable & Sendable> {
    let rawValue: RawValue
}
```

That forces every use of `Tagged` to meet constraints needed only by some
operations.

Conditional conformance also applies to domain protocols:

```swift
protocol Redactable {
    var redactedDescription: String { get }
}

struct Secret<Value> {
    private let value: Value
}

extension Secret: Redactable where Value: CustomStringConvertible {
    var redactedDescription: String { "<redacted>" }
}
```

## Constrained Methods Over Constrained Types

Put constraints where the operation needs them, not necessarily on the whole
type.

```swift
struct Envelope<Value> {
    let value: Value
}

extension Envelope {
    func encoded() throws -> Data where Value: Encodable {
        try JSONEncoder().encode(value)
    }

    func hashValue() -> Int where Value: Hashable {
        value.hashValue
    }
}
```

Wrong but tempting:

```swift
struct Envelope<Value: Codable & Hashable> {
    let value: Value
}
```

If only `encoded()` needs `Encodable`, requiring `Codable & Hashable` on the
entire type leaks implementation needs into every caller.

Constrained methods are also useful for typestate:

```swift
struct EndpointSpec<Request, Response, Failure: Error> {
    let path: Path
    let request: Request
}

extension EndpointSpec where Request == EmptyRequest {
    static func get(_ path: Path) -> EndpointSpec<EmptyRequest, Response, Failure> {
        EndpointSpec(path: path, request: EmptyRequest())
    }
}
```

## Type Erasure That Preserves Invariant Axes

Type erasure is not the same as giving up type safety. Erase the concrete
implementation, not the semantic axes.

```swift
struct AnyParser<Input, Output, Failure: Error>: Parser {
    private let parseValue: @Sendable (Input) throws(Failure) -> Output

    init<P: Parser & Sendable>(_ parser: P)
    where P.Input == Input, P.Output == Output, P.Failure == Failure {
        self.parseValue = { input in
            try parser.parse(input)
        }
    }

    func parse(_ input: Input) throws(Failure) -> Output {
        try parseValue(input)
    }
}

struct AnyValidator<Input, Failure: Error>: Validator {
    private let validateValue: @Sendable (Input) throws(Failure) -> Input

    init<V: Validator & Sendable>(_ validator: V)
    where V.Input == Input, V.Failure == Failure {
        self.validateValue = { input in
            try validator.validate(input)
        }
    }

    func validate(_ input: Input) throws(Failure) -> Input {
        try validateValue(input)
    }
}
```

Wrong but tempting:

```swift
struct AnyParser {
    let parse: (Any) throws -> Any
}
```

This loses input, output, and failure relationships. Callers now need runtime
casts, and the compiler cannot prove composition.

For endpoints, preserve request, response, failure, and auth axes if those axes
encode correctness:

```swift
struct AnyEndpoint<Request, Response, Failure: Error>: Endpoint {
    private let performValue: @Sendable (Request) async throws(Failure) -> Response

    init<E: Endpoint & Sendable>(_ endpoint: E)
    where E.Request == Request, E.Response == Response, E.Failure == Failure {
        self.performValue = { request in
            try await endpoint.perform(request)
        }
    }

    func perform(_ request: Request) async throws(Failure) -> Response {
        try await performValue(request)
    }
}
```

Closure-field witnesses still call closures and may capture or allocate. They
avoid existential relationship loss, but they are not automatically faster than
protocols. Measure if performance is the reason.

## `some` vs `any`

Use the construct that matches who chooses the concrete type and whether
heterogeneous storage is required.

Use a generic parameter or opaque parameter when the caller chooses one concrete
type and the function should preserve its relationships:

```swift
func validate<V: Validator>(
    _ value: V.Input,
    using validator: V
) throws(V.Failure) -> V.Input {
    try validator.validate(value)
}

func validate(
    _ value: some Sendable,
    using logger: some Logger
) {
    // Each `some` parameter is a hidden generic parameter.
}
```

Use `some P` as a return type when the implementation chooses one fixed concrete
type but wants to hide it:

```swift
func makeEmailValidator() -> some Validator<EmailAddress, EmailValidationError> {
    EmailValidator()
}
```

Use `any P` when values of different concrete types must live in the same
storage and the required associated types are constrained:

```swift
let validators: [any Validator<EmailAddress, EmailValidationError>] = [
    DNSValidator(),
    SyntaxValidator()
]
```

Use an enum when heterogeneity is finite and owned by the module:

```swift
enum LoginValidator {
    case email(EmailValidator)
    case phone(PhoneValidator)
}
```

Use a type eraser when storage needs to hide concrete types but preserve
associated-type axes:

```swift
let parser: AnyParser<Substring, UserID, UserIDParseError>
```

Wrong but tempting:

```swift
func process(_ validators: [any Validator]) {
    // Associated types are erased. You have lost the type-level proof.
}
```

## Existential Loss Hazards

An existential stores a value whose concrete type is known only at runtime. That
can erase `Self` and associated-type relationships that were proving
correctness.

```swift
protocol Cloner {
    func clone() -> Self
}

func duplicate<C: Cloner>(_ value: C) -> C {
    value.clone()
}

func duplicateExistential(_ value: any Cloner) -> any Cloner {
    value.clone()
}
```

The generic version returns the same concrete type. The existential version can
only promise "some `Cloner` value" because the concrete `Self` relationship is no
longer visible to the caller.

Existentials are fine at boundaries where dynamic dispatch is the point. They
are risky in core logic that depends on relationships such as:

- Parser output must equal the next parser input.
- Repository ID must match entity ID.
- Validator failure must match UI error mapping.
- Endpoint response must match decoder output.
- Fluent builder methods must return the concrete builder type.

Prefer generics, constrained existentials, enums, or type erasers that keep the
relationship in the signature.

## Sealed Protocol Pattern

Use protocols for open sets. Use enums or sealed wrappers for closed sets.

Wrong but tempting:

```swift
public protocol AuthState {}

public struct Authenticated: AuthState {}
public struct Unauthenticated: AuthState {}

public struct Session<State: AuthState> {
    public init() {}
}
```

Downstream modules can add `struct PretendAdmin: AuthState {}` if the protocol
is public. That may be fine for extension points. It is not proof.

For internal closed sets:

```swift
protocol AuthState {}

enum Authenticated: AuthState {}
enum Unauthenticated: AuthState {}

struct Session<State: AuthState> {
    private init() {}
}
```

For public closed sets, prefer:

```swift
public enum SessionState: Sendable {
    case authenticated(AuthenticatedSession)
    case unauthenticated
}
```

or:

```swift
public struct AuthenticatedSession: Sendable {
    public let userID: UserID
    private let token: AccessToken

    internal init(userID: UserID, token: AccessToken) {
        self.userID = userID
        self.token = token
    }
}
```

Do not rely on naming conventions, underscored protocol names, or documentation
as sealing. They may discourage conformance, but they do not prevent it.

## Protocol Extension Default Hazards

Default implementations can accidentally let conformers claim an invariant
without providing the logic that establishes it.

Wrong but tempting:

```swift
protocol Sanitizer {
    func sanitize(_ html: HTML<RawHTML>) -> HTML<SanitizedHTML>
}

extension Sanitizer {
    func sanitize(_ html: HTML<RawHTML>) -> HTML<SanitizedHTML> {
        // Placeholder default that accidentally ships.
        HTML<SanitizedHTML>.unsafeAssumingSanitized(html.value)
    }
}

struct MarkdownSanitizer: Sanitizer {}
```

If the method is the proof-producing operation, require the witness. Defaults
are better for derived convenience that cannot violate the invariant.

```swift
protocol Sanitizer {
    func sanitize(_ html: HTML<RawHTML>) -> HTML<SanitizedHTML>
}

extension Sanitizer {
    func sanitizeAll(_ values: [HTML<RawHTML>]) -> [HTML<SanitizedHTML>] {
        values.map(sanitize)
    }
}
```

## F-Bounded and `Self` APIs

Use `Self` when an API must preserve the concrete conforming type.

```swift
protocol Configurable {
    func setting(_ key: SettingKey, to value: SettingValue) -> Self
}

struct HTTPClientBuilder: Configurable {
    func setting(_ key: SettingKey, to value: SettingValue) -> HTTPClientBuilder {
        var copy = self
        copy.settings[key] = value
        return copy
    }
}
```

`Self` keeps fluent APIs precise in generic code:

```swift
func configure<B: Configurable>(_ builder: B) -> B {
    builder.setting(.timeout, to: .seconds(30))
}
```

F-bounded designs constrain a relationship back to the conforming family:

```swift
protocol Node: AnyObject {
    associatedtype Parent: Node
    associatedtype Child: Node

    var parent: Parent? { get }
    var children: [Child] { get }
}
```

Use this sparingly. F-bounded APIs can become difficult to satisfy and often
break down when stored as existentials.

Wrong but tempting:

```swift
let builders: [any Configurable] = [HTTPClientBuilder()]

// Calls returning Self are hard to use after existential erasure.
let configured = builders[0].setting(.timeout, to: .seconds(30))
```

If heterogeneous storage is required, provide a type eraser whose methods return
the eraser type, or use an enum for the finite set of builders.

## Parameter Packs

Parameter packs replace fixed-arity overloads when the arity is statically known
but not fixed by the library author.

```swift
struct Field<Value> {
    let name: String
    let parse: @Sendable (String) throws(FieldError) -> Value
}

struct Row<each Value> {
    let fields: (repeat Field<each Value>)
}

func row<each Value>(
    _ fields: repeat Field<each Value>
) -> Row<repeat each Value> {
    Row(fields: (repeat each fields))
}
```

This preserves the type of each field without collapsing to `[Any]`.

Wrong but tempting:

```swift
struct Row {
    let fields: [Any]
}
```

Use parameter packs for:

- Heterogeneous tuples where each position has a known type.
- DSL nodes with statically known children.
- Replacing `zip2`, `zip3`, `zip4` overload families.
- Avoiding `[Any]` in fixed-shape APIs.

Do not use packs to model dynamic user data. If the number of elements comes
from JSON or a database row discovered at runtime, use a collection plus runtime
validation.

## Key Paths, Predicates, and Type-Safe Reflection

Use `KeyPath<Root, Value>` when code needs to refer to a field without turning
that field into a string.

```swift
struct SortDescriptor<Root>: Sendable {
    let compare: @Sendable (Root, Root) -> ComparisonResult
}

func sort<Root, Value: Comparable>(
    by keyPath: KeyPath<Root, Value>
) -> SortDescriptor<Root> {
    SortDescriptor { lhs, rhs in
        let left = lhs[keyPath: keyPath]
        let right = rhs[keyPath: keyPath]
        if left < right { return .orderedAscending }
        if left > right { return .orderedDescending }
        return .orderedSame
    }
}

let descriptor = sort(by: \User.lastName)
```

Key paths are useful for sorting, diffing, form fields, bindings, query
predicates, analytics fields, and table columns. The `Root` and `Value` axes keep
fields from crossing domains.

Wrong but tempting:

```swift
struct SortDescriptor {
    let fieldName: String
}

let descriptor = SortDescriptor(fieldName: "lastNmae")
```

For query DSLs, model predicates with typed roots and fields.

```swift
struct Field<Root, Value>: Sendable {
    let keyPath: KeyPath<Root, Value>
    let columnName: SQLIdentifier
}

struct Predicate<Root>: Sendable {
    fileprivate let sql: SQL<ParameterizedSQL>
}

func == <Root, Value: DatabaseBindable>(
    lhs: Field<Root, Value>,
    rhs: Value
) -> Predicate<Root> {
    Predicate(sql: .parameterized("\(lhs.columnName.escaped) = ?", rhs.databaseValue))
}
```

A `Predicate<User>` should not compile when applied to a `Workspace` query.

Regex typed captures are the same idea: replace capture indexes and force casts
with named output.

```swift
struct OrderCode: Sendable {
    let prefix: String
    let number: Int
}

func parseOrderCode(_ rawValue: String) throws(OrderCodeError) -> OrderCode {
    // Use the project's typed Regex support when available, then map named
    // captures into a domain type at the boundary.
}
```

Avoid `@dynamicMemberLookup` when it turns arbitrary strings into fields.

```swift
@dynamicMemberLookup
struct JSONValue {
    subscript(dynamicMember member: String) -> JSONValue {
        // Typos compile. Type relationships are gone.
    }
}
```

Use dynamic member lookup only when it is backed by typed key paths,
compiler-known members, or constrained keys. Otherwise it recreates the
stringly-typed API this skill is trying to remove.

## Typed Function Fields

Function fields are model types. Include the concurrency and failure contracts in
the field type.

```swift
struct Effect<Input, Output, Failure: Error>: Sendable {
    let run: @Sendable (Input) async throws(Failure) -> Output
}

struct Decoder<Input, Output, Failure: Error>: Sendable {
    let decode: @Sendable (Input) throws(Failure) -> Output
}

struct EventHandler<Event>: Sendable {
    let handle: @Sendable (Event) async -> Void
}
```

The type says:

- `@Sendable`: the closure can safely cross concurrency domains if captures also
  satisfy sendability.
- `async`: the operation may suspend.
- `throws(Failure)`: callers know the exact failure type.
- `Input` and `Output`: composition can be checked by the compiler.

Wrong but tempting:

```swift
struct Effect {
    let run: (Any) async throws -> Any
}
```

This erases input, output, failure, and sendability. It usually moves errors from
the compiler to runtime casts.

Typed function fields are useful for protocol witnesses, dependency injection,
reducers, parser pipelines, and test doubles. They still invoke closures and may
capture state; they are not a magic performance optimization.

## Review Checklist

For each generic, phantom, or protocol model, ask:

1. What invariant is encoded by the type parameter, associated type, or
   constraint?
2. Can any accessible initializer, mutable property, `Decodable` conformance, or
   raw-value API bypass that invariant?
3. Is a public marker protocol being treated as proof? If yes, how is conformance
   controlled?
4. Would `any` erase a relationship that the rest of the code relies on?
5. Does type erasure preserve every semantic axis callers need?
6. Is a staged builder proving required fields, or merely collecting values?
7. Are macros generating inspectable code that preserves access control?
8. Is the generic design simpler than the runtime checks it replaces?
