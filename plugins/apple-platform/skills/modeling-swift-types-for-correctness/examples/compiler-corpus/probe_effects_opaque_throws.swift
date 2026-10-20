enum ProbeFailure: Error { case failed }

func opaqueFailure() throws(some Error) -> Int {
  throw ProbeFailure.failed
}
