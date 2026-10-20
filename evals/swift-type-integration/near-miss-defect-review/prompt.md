---
prompt_id: "swift-type-near-miss-defect-review-v1"
---

Review this function for its stated behavior: return the matching user, or `nil` when no user has that id. Report a concrete defect and a focused fix; do not edit files.

```swift
func user(withID id: Int, in users: [(id: Int, name: String)]) -> (id: Int, name: String)? {
    users.first { $0.id = id }
}
```
