import Synchronization

enum ProbeFailure: Error { case failed, cancelled }

func typedOperation() throws(ProbeFailure) -> Int { 42 }

func forward<Value, Failure: Error>(
  _ body: () throws(Failure) -> Value
) throws(Failure) -> Value {
  try body()
}

func returnsTypedResult() async -> Result<Int, ProbeFailure> {
  await Result<Int, ProbeFailure> {
    () async throws(ProbeFailure) -> Int in
    try typedOperation()
  }
}

func createsThrowingTask() -> Task<Int, any Error> {
  Task<Int, any Error> {
    () async throws(ProbeFailure) -> Int in
    try typedOperation()
  }
}

func newContinuation() async throws(ProbeFailure) -> Int {
  try await withContinuation(of: Int.self, throwing: ProbeFailure.self) {
    continuation in
    continuation.resume(returning: 42)
  }
}

func cleanup() async {}

func asynchronousCleanup() async {
  defer {
    await withTaskCancellationShield {
      await cleanup()
    }
  }
  await cleanup()
}

struct DeliberatelyNotSendable: ~Sendable { let value: Int }

final class Shareable: Sendable {}
final class WeakOwner: Sendable {
  weak let target: Shareable?
  init(_ target: Shareable) { self.target = target }
}

@MainActor
final class Panel: @MainActor Equatable {
  var title: String = ""
  static func == (lhs: Panel, rhs: Panel) -> Bool {
    lhs.title == rhs.title
  }
}

protocol StaticProvider { static func get() -> Int }

func useMetatype<T: StaticProvider & SendableMetatype>(_: T.Type) -> Task<Int, Never> {
  Task.detached { T.get() }
}

final class LocalBox { var value: Int = 0 }

nonisolated(nonsending)
func useLocalBox(_ box: LocalBox) async { box.value += 1 }

@concurrent
func performAwayFromActor() async -> Int { 1 }

actor BoxOwner {
  private let box = LocalBox()
  func perform() async { await useLocalBox(box) }
}

struct IsolatedWork: Sendable {
  let body: @Sendable @isolated(any) () async -> Void
  func run() async { await body() }
}

func inheritIsolation(isolation: isolated (any Actor)? = #isolation) async {}

final class Counter: Sendable {
  private let state = Mutex(0)
  func increment() -> Int {
    state.withLock { value in
      value += 1
      return value
    }
  }
}
