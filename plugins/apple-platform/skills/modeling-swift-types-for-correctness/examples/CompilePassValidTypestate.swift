func demonstrateValidTypestate(_ draft: Registration<DraftRegistration>) throws {
    _ = try draft.validate().emailCandidate
}
