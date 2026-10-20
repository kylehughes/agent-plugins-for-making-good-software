// Reviewed examples for the Swift 6.4 type-modeling catalog.
// The guarantees demonstrated concern construction and composition, not arithmetic
// totality, termination, purity, or the correctness of the interpreters themselves.

// MARK: - Equality evidence without unsafe casts

struct TypeEquality<A, B> {
    private let forward: (A) -> B
    private let backward: (B) -> A

    private init(forward: @escaping (A) -> B, backward: @escaping (B) -> A) {
        self.forward = forward
        self.backward = backward
    }

    func transport(_ value: A) -> B { forward(value) }

    func reversed() -> TypeEquality<B, A> {
        TypeEquality<B, A>(forward: backward, backward: forward)
    }

    func followed<C>(by other: TypeEquality<B, C>) -> TypeEquality<A, C> {
        TypeEquality<A, C>(
            forward: { other.forward(self.forward($0)) },
            backward: { self.backward(other.backward($0)) }
        )
    }
}

extension TypeEquality where A == B {
    static var reflexive: Self {
        Self(forward: { $0 }, backward: { $0 })
    }
}

// A finite GADT-style encoding. The evidence is a required case payload;
// a String literal cannot be constructed as an expression returning Bool.
// Swift does not refine Output by inspecting a case, so evaluate explicitly
// applies a transport. There is no force cast in the trusted implementation.
indirect enum ProvenExpression<Output> {
    case text(String, TypeEquality<String, Output>)
    case flag(Bool, TypeEquality<Bool, Output>)
    case concatenate(
        ProvenExpression<String>, ProvenExpression<String>,
        TypeEquality<String, Output>
    )
    case isEmpty(ProvenExpression<String>, TypeEquality<Bool, Output>)
    case choose(ProvenExpression<Bool>, ProvenExpression<Output>, ProvenExpression<Output>)

    func evaluate() -> Output {
        switch self {
        case let .text(value, proof):
            proof.transport(value)
        case let .flag(value, proof):
            proof.transport(value)
        case let .concatenate(left, right, proof):
            proof.transport(left.evaluate() + right.evaluate())
        case let .isEmpty(value, proof):
            proof.transport(value.evaluate().isEmpty)
        case let .choose(condition, yes, no):
            condition.evaluate() ? yes.evaluate() : no.evaluate()
        }
    }
}

extension ProvenExpression where Output == String {
    static func literal(_ value: String) -> Self { .text(value, .reflexive) }
    static func joined(_ left: Self, _ right: Self) -> Self {
        .concatenate(left, right, .reflexive)
    }
}

extension ProvenExpression where Output == Bool {
    static func literal(_ value: Bool) -> Self { .flag(value, .reflexive) }
    static func empty(_ value: ProvenExpression<String>) -> Self {
        .isEmpty(value, .reflexive)
    }
}

// MARK: - Associated type families: closed typed syntax without equality witnesses

protocol TypedSyntax {
    associatedtype Value
    func evaluate() -> Value
}

protocol ExpressionSort {
    associatedtype Value
    associatedtype Syntax: TypedSyntax where Syntax.Value == Value
}

enum TextSort: ExpressionSort {
    typealias Value = String
    typealias Syntax = TextSyntax
}

enum FlagSort: ExpressionSort {
    typealias Value = Bool
    typealias Syntax = FlagSyntax
}

typealias SyntaxFor<S: ExpressionSort> = S.Syntax

indirect enum TextSyntax: TypedSyntax {
    case literal(String)
    case joined(TextSyntax, TextSyntax)
    case choose(FlagSyntax, TextSyntax, TextSyntax)

    func evaluate() -> String {
        switch self {
        case let .literal(value): value
        case let .joined(left, right): left.evaluate() + right.evaluate()
        case let .choose(condition, yes, no):
            condition.evaluate() ? yes.evaluate() : no.evaluate()
        }
    }
}

indirect enum FlagSyntax: TypedSyntax {
    case literal(Bool)
    case isEmpty(TextSyntax)
    case and(FlagSyntax, FlagSyntax)

    func evaluate() -> Bool {
        switch self {
        case let .literal(value): value
        case let .isEmpty(text): text.evaluate().isEmpty
        case let .and(left, right): left.evaluate() && right.evaluate()
        }
    }
}

struct TypedTerm<S: ExpressionSort> {
    let syntax: S.Syntax
    func evaluate() -> S.Value { syntax.evaluate() }
}

// MARK: - Variadic heterogeneous products and correlated transformations

struct HList<each Element> {
    let values: (repeat each Element)

    init(_ values: repeat each Element) {
        self.values = (repeat each values)
    }
}

protocol Transformation {
    associatedtype Input
    associatedtype Output
    func apply(_ input: Input) -> Output
}

struct Transformations<each T: Transformation> {
    private let operations: (repeat each T)

    init(_ operations: repeat each T) {
        self.operations = (repeat each operations)
    }

    func apply(_ inputs: repeat (each T).Input) -> HList<repeat (each T).Output> {
        HList(repeat (each operations).apply(each inputs))
    }
}

struct DescribeInteger: Transformation {
    func apply(_ input: Int) -> String { String(input) }
}

struct CountUTF8: Transformation {
    func apply(_ input: String) -> Int { input.utf8.count }
}

struct NegateFlag: Transformation {
    func apply(_ input: Bool) -> Bool { !input }
}

func equalProducts<each Element: Equatable>(
    _ lhs: (repeat each Element),
    _ rhs: (repeat each Element)
) -> Bool {
    for (left, right) in repeat (each lhs, each rhs) {
        if left != right { return false }
    }
    return true
}

// MARK: - Recursive products and statically typed positional evidence

struct HNil {}
struct HCons<Head, Tail> {
    let head: Head
    let tail: Tail
}

protocol Position {
    associatedtype List
    associatedtype Element
    static func get(from list: List) -> Element
}

enum Here<Head, Tail>: Position {
    typealias List = HCons<Head, Tail>
    typealias Element = Head
    static func get(from list: List) -> Head { list.head }
}

enum There<Head, Rest: Position>: Position {
    typealias List = HCons<Head, Rest.List>
    typealias Element = Rest.Element
    static func get(from list: List) -> Element { Rest.get(from: list.tail) }
}

// MARK: - Small runnable evidence

let proven: ProvenExpression<String> = .choose(
    .empty(.literal("")),
    .joined(.literal("type"), .literal(" safe")),
    .literal("unexpected")
)
precondition(proven.evaluate() == "type safe")

let family = TypedTerm<TextSort>(syntax: .choose(
    .isEmpty(.literal("")), .literal("typed family"), .literal("unexpected")
))
precondition(family.evaluate() == "typed family")

let transformations = Transformations(DescribeInteger(), CountUTF8(), NegateFlag())
let heterogeneous: HList<String, Int, Bool> = transformations.apply(42, "Swift", false)
precondition(equalProducts(heterogeneous.values, ("42", 5, true)))

let recursive = HCons(head: 42, tail: HCons(head: "second", tail: HNil()))
typealias Second = There<Int, Here<String, HNil>>
let selected: String = Second.get(from: recursive)
precondition(selected == "second")

print("All modeling examples ran successfully.")
