---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
timeout_seconds: 180
---

Review only the naming and argument labels of this Swift API. Suggest call sites that follow platform conventions while keeping the behavior the same. Do not edit files.

```swift
struct Catalog {
    func getItemWithIdentifier(identifier: String) -> String? { nil }
}
```
