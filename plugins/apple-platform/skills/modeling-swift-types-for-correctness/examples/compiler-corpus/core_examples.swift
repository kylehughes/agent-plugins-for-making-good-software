import Foundation

// A. Distinct domain identities. Identity tags do not prove server existence.
struct ID<Entity>: Hashable, Sendable {
    let rawValue: UUID
    init(_ rawValue: UUID) { self.rawValue = rawValue }
}
enum UserEntity {}
enum OrderEntity {}
typealias UserID = ID<UserEntity>
typealias OrderID = ID<OrderEntity>

func loadUser(_ id: UserID) -> UUID { id.rawValue }

// B. A validated scalar, including the decoding entry point.
struct Percentage: Hashable, Sendable, Codable {
    let value: UInt8

    init?(_ value: Int) {
        guard (0...100).contains(value) else { return nil }
        self.value = UInt8(value)
    }

    init(from decoder: any Decoder) throws {
        let container = try decoder.singleValueContainer()
        let raw = try container.decode(Int.self)
        guard let validated = Self(raw) else {
            throw DecodingError.dataCorruptedError(
                in: container, debugDescription: "Expected an integer from 0 to 100"
            )
        }
        self = validated
    }

    func encode(to encoder: any Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(value)
    }
}

// C. Nonemptiness represented structurally, without a force unwrap.
struct NonEmpty<Element> {
    let head: Element
    let tail: [Element]

    init(_ head: Element, tail: [Element] = []) {
        self.head = head
        self.tail = tail
    }

    func map<T>(_ transform: (Element) throws -> T) rethrows -> NonEmpty<T> {
        try NonEmpty<T>(transform(head), tail: tail.map(transform))
    }

    // Filtering can remove every element, so the output admits emptiness.
    func filter(_ predicate: (Element) throws -> Bool) rethrows -> [Element] {
        try ([head] + tail).filter(predicate)
    }
}

// D. Correlated alternatives instead of independent optional fields.
enum LoadState<Value, Failure: Error> {
    case idle
    case loading(previous: Value?)
    case loaded(Value)
    case failed(Failure, previous: Value?)
}

enum Patch<Value> {
    case unchanged
    case remove
    case set(Value)
}

// E. Preserve input/output relationships through generic composition.
protocol Stage<Input, Output> {
    associatedtype Input
    associatedtype Output
    func run(_ input: Input) -> Output
}

struct Then<First: Stage, Second: Stage>: Stage
where First.Output == Second.Input {
    let first: First
    let second: Second

    func run(_ input: First.Input) -> Second.Output {
        second.run(first.run(input))
    }
}

struct UTF8Encode: Stage {
    func run(_ input: String) -> [UInt8] { Array(input.utf8) }
}
struct ByteCount: Stage {
    func run(_ input: [UInt8]) -> Int { input.count }
}

// F. A consuming workflow. Successful validation changes the available API.
enum Draft {}
enum Ready {}
enum Complete {}

struct Submission<State>: ~Copyable {
    private let body: String

    private init(body: String) { self.body = body }
}

extension Submission where State == Draft {
    static func draft(_ text: String) -> Self { Self(body: text) }

    consuming func validate() -> Submission<Ready>? {
        guard !body.isEmpty else { return nil }
        return Submission<Ready>(body: body)
    }
}

extension Submission where State == Ready {
    consuming func finish() -> Submission<Complete> {
        // A real effectful submission belongs in the audited implementation.
        Submission<Complete>(body: body)
    }
}

// G. Return a still-owned resource on failure using a noncopyable sum.
enum Attempt<Success: ~Copyable, Recovery: ~Copyable, Failure: Error>: ~Copyable {
    case success(Success)
    case failure(Failure, Recovery)
}

enum ValidationFailure: Error { case empty }

extension Submission where State == Draft {
    consuming func validateRecovering()
      -> Attempt<Submission<Ready>, Submission<Draft>, ValidationFailure> {
        if body.isEmpty {
            return .failure(.empty, self)
        }
        return .success(Submission<Ready>(body: body))
    }
}

// H. Shape equality in the type. Index arithmetic remains runtime arithmetic.
struct Matrix<let rows: Int, let columns: Int> {
    var storage: InlineArray<rows, InlineArray<columns, Double>>

    init(repeating value: Double) {
        storage = .init(repeating: .init(repeating: value))
    }
}

func multiplied<let r: Int, let k: Int, let c: Int>(
    _ a: Matrix<r, k>, _ b: Matrix<k, c>
) -> Matrix<r, c> {
    var out = Matrix<r, c>(repeating: 0)
    for i in 0..<r {
        for j in 0..<c {
            for inner in 0..<k {
                out.storage[i][j] += a.storage[i][inner] * b.storage[inner][j]
            }
        }
    }
    return out
}

// I. A dynamic bounds proof is minted once and then carried by a type.
struct BoundedIndex<let size: Int> {
    let value: Int

    init?(_ value: Int) {
        guard value >= 0, value < size else { return nil }
        self.value = value
    }
}

func element<let size: Int, Element>(
    _ values: borrowing InlineArray<size, Element>,
    at index: BoundedIndex<size>
) -> Element {
    values[index.value]
}

// J. Coordinate spaces and directed transformation composition.
struct Point<Space> { let x: Double; let y: Double }
struct Transform<From, To> {
    let apply: (Point<From>) -> Point<To>
}

func followed<A, B, C>(
    _ first: Transform<A, B>, _ second: Transform<B, C>
) -> Transform<A, C> {
    Transform { second.apply(first.apply($0)) }
}

// K. A finite map can require a value for every case structurally.
enum TrafficLight { case red, yellow, green }
struct TrafficLightMap<Value> {
    let red: Value
    let yellow: Value
    let green: Value

    subscript(_ key: TrafficLight) -> Value {
        switch key {
        case .red: red
        case .yellow: yellow
        case .green: green
        }
    }
}

func coreExamples() {
    _ = loadUser(UserID(UUID()))
    _ = Percentage(75)
    _ = NonEmpty(1, tail: [2, 3]).map(String.init)
    let bytes = Then(first: UTF8Encode(), second: ByteCount())
    _ = bytes.run("hello")
    let draft = Submission<Draft>.draft("payload")
    if let ready = draft.validate() {
        _ = ready.finish()
    }
    let a = Matrix<2, 3>(repeating: 2)
    let b = Matrix<3, 4>(repeating: 3)
    let _: Matrix<2, 4> = multiplied(a, b)
    let vector: InlineArray<3, Int> = [10, 20, 30]
    if let index = BoundedIndex<3>(1) {
        _ = element(vector, at: index)
    }
}
