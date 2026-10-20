---
prompt_id: "swift-type-decoding-main-v1"
---

We persist discount rules for offline orders. A rule's percentage must be from 1 through 100, but a restored file recently produced `0` even though new rules are checked when created. Assess the model below and recommend the smallest safe repair and evidence plan. Keep this review read-only.

```swift
struct DiscountRule: Codable {
    let percent: Int

    init?(_ percent: Int) {
        guard (1...100).contains(percent) else { return nil }
        self.percent = percent
    }
}
```
