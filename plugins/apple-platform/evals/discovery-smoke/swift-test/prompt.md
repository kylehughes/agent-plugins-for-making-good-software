---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
timeout_seconds: 180
---

Write a small unit test suite for this Swift function. Cover positive, negative, zero, and empty input while preserving input order. Use the modern unit testing framework, keep the suite focused, and identify the failing case. Show the tests in your reply without editing files.

```swift
func oddValues(in values: [Int]) -> [Int] {
    values.filter { $0 % 2 == 1 }
}
```
