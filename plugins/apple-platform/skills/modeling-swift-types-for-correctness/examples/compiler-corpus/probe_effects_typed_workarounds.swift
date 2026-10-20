enum DetailFailure: Error { case first, second }

func throwDetailed() throws(DetailFailure) -> Int { 42 }

func catchesPrecisely() {
  do {
    _ = try throwDetailed()
  } catch {
    switch error {
    case .first: break
    case .second: break
    }
  }
}

func asyncLetPreservesErrorViaResult() async throws(DetailFailure) -> Int {
  async let result = Result(catching: throwDetailed)
  return try await result.get()
}

func startsTypedResultTask() -> Task<Result<Int, DetailFailure>, Never> {
  Task {
    await Result<Int, DetailFailure> {
      () async throws(DetailFailure) -> Int in
      try throwDetailed()
    }
  }
}

func typedStream() -> some AsyncSequence<Int, Never> {
  AsyncStream<Int> { continuation in
    continuation.yield(1)
    continuation.finish()
  }
}

func iterateTyped<S: AsyncSequence>(over sequence: S) async throws(S.Failure) {
  for try await _ in sequence {}
}

func mappingTyped() throws(DetailFailure) -> [Int] {
  try [1, 2].map { (value: Int) throws(DetailFailure) -> Int in
    value
  }
}
