---
prompt_id: "swift-type-decoding-combined-variant-v1"
---

A shared app restores a saved seat count that must be at least one. The initializer used by new bookings rejects zero, yet a historical keyed payload with zero has reached the UI. Give a read-only assessment of the construction paths, a compatible repair direction, and narrowly targeted evidence.

```swift
struct SeatCount: Codable {
    let count: Int

    init?(_ count: Int) {
        guard count > 0 else { return nil }
        self.count = count
    }
}
```
