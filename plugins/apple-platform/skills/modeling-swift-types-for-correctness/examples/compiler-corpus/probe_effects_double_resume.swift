func doubleResume() async -> Int {
  await withContinuation(of: Int.self) { continuation in
    continuation.resume(returning: 1)
    continuation.resume(returning: 2)
  }
}
