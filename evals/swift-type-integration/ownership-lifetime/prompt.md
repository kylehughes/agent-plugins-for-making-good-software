---
prompt_id: "swift-type-ownership-lifetime-v1"
---

Our media decoder lends a view into its buffer to a callback. A caller wants to retain that view for work after the callback returns, and another team wants to make the decoder handle noncopyable. Recommend the smallest API boundary that addresses the real misuse, with clear limits and checks. Keep this review read-only.
