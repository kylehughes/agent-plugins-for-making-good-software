func demonstrateWrongTypestate(_ ready: Registration<ReadyRegistration>) throws {
    _ = try ready.validate()
}
