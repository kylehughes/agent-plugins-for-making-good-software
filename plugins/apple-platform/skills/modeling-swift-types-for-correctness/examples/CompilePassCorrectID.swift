func demonstrateCorrectIdentifierDomain(_ userID: UserID) throws {
    let displayName = try NonEmptyString("Taylor")
    _ = User(id: userID, displayName: displayName)
}
