enum ProbeFailure: Error { case first, second }

func typedOperation() throws(ProbeFailure) -> Int { 42 }

func typedCatch() {
  do {
    _ = try typedOperation()
  } catch .first {
  } catch .second {
  }
}
