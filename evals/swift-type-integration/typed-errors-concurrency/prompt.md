---
prompt_id: "swift-type-typed-errors-concurrency-v1"
---

Our document import operation has a small, public failure vocabulary. An async adapter currently launches work and returns a broad error, so clients can no longer exhaustively handle the documented import failures. Recommend a Swift design that preserves useful failures across the asynchronous seam, accounts for cancellation, and says what remains outside the type guarantee. Do not edit files.
