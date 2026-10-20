enum ProbeFailure: Error { case failed }

func typedOperation() throws(ProbeFailure) -> Int { 42 }

func asyncLetTyped() async throws(ProbeFailure) -> Int {
  async let value = typedOperation()
  return try await value
}
