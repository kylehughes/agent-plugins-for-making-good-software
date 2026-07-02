import Foundation

struct Identifier<Domain>: RawRepresentable {
    let rawValue: UUID
}

enum UserDomain {}
enum WorkspaceDomain {}

typealias UserID = Identifier<UserDomain>
typealias WorkspaceID = Identifier<WorkspaceDomain>

func loadUser(_ id: UserID) {}

func demonstrateWrongIdentifierDomain() {
    let workspaceID = WorkspaceID(rawValue: UUID())
    // expected-error: cannot convert value of type
    loadUser(workspaceID)
}
