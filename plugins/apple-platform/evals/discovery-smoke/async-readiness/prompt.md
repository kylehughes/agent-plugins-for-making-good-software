---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
timeout_seconds: 180
---

This Swift test sometimes sends its notification before the observer is attached. Explain how to make the test wait reliably for subscription and finish cleanup, without changing the production model. Keep the answer read-only.

```swift
@Test func receivesNotification() async {
    let task = Task {
        for await _ in NotificationCenter.default.notifications(named: .init("Refresh")) {
            return
        }
    }
    await Task.yield()
    NotificationCenter.default.post(name: .init("Refresh"), object: nil)
    await task.value
}
```
