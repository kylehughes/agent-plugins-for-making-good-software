---
prompt_id: "swift-type-decoding-apple-variant-v1"
---

An iOS app restores a saved alarm whose hour must be from 0 through 23. New alarms are rejected outside that range, but a restored keyed record can contain `24`. Assess the likely gap, the smallest compatible repair, and the checks needed for confidence. Keep the assessment read-only.

```swift
struct AlarmHour: Codable {
    let hour: Int

    init?(_ hour: Int) {
        guard (0..<24).contains(hour) else { return nil }
        self.hour = hour
    }
}
```
