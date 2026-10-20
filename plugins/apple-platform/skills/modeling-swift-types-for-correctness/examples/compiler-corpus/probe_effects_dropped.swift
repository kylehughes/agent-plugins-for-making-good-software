func droppedContinuation() async -> Int {
  await withContinuation(of: Int.self) { continuation in
    // This compiles. The continuation's deinitializer traps at runtime.
  }
}
