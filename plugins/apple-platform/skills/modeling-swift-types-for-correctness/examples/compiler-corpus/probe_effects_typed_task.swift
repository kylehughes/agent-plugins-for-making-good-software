enum ProbeFailure: Error { case failed }

func createsTypedTask() -> Task<Int, ProbeFailure> {
  Task<Int, ProbeFailure> {
    () async throws(ProbeFailure) -> Int in
    42
  }
}
