func demonstrateWrongIdentifierDomain() throws {
    let workspaceID = WorkspaceID(rawValue: .init())
    let displayName = try NonEmptyString("Taylor")
    _ = User(id: workspaceID, displayName: displayName)
}
