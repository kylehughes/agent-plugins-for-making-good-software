# Canonical Idioms

One worked shape per category from the decision table. Examples use the contract names from [primitive-contracts.md](primitive-contracts.md) (`EventRecorder`, `TimeoutBudget`, `withAsyncCleanup`, a `TestClock`-style virtual clock); substitute your project's equivalents.

## Timing-operator semantics — debounce / throttle

Test rate-limiting operators through a **marble-diagram harness**: drive a test-supplied input `AsyncSequence` through backpressure (`AsyncChannel` works), advance a virtual clock one tick at a time, and record emissions at the virtual tick they occurred. The happens-before edge between "value enqueued" and "operator observed the value" is explicit inside the harness, so no yield budgets, no drain helpers, no guessing.

Diagram grammar: `-` is silence, `|` completion, any other single character is a value at that tick, `[abc]` is a burst of several values at the same tick. Input and expected must have the same tick length.

```swift
@Suite(.serialized)
struct DebounceTests {
    @Test("Coalescing rapid values delivers only the final value after the interval")
    @MainActor
    func coalescesRapidValues() async throws {
        try await validateRateLimit(
            input: "[12345]---|",
            expected: "---5|",
            intervalSteps: 3
        ) { input, clock, interval in
            input.debounce(for: interval, clock: clock)
        }
    }
}
```

Why a harness at all: AsyncAlgorithms' time operators use internal `TaskGroup`s and do not expose "the operator observed this value" as a public event when driven through a black-box `send()` API. Fixed "megaYield" drains paper over that gap — a flake budget, not a semantic guarantee. AsyncAlgorithms' own internal [`Validator`](https://github.com/apple/swift-async-algorithms/blob/main/Tests/AsyncAlgorithmsTests/Support/Validator.swift) test support is the model: a principled sequence seam owned by the test harness. The factory closure applies the operator directly; don't add production-only sequence seams just to make the harness convenient.

## Timing-operator wrapper lifecycle — start / stop / restart / send-after-stop

Separate from semantics. When production wraps an operator (a `Debouncer`-style type), use its clock-taking initializer and a zero interval to prove wrapper lifecycle — starts once, cancels on stop, creates a fresh stream on restart, ignores sends after stop. The operator semantics are already covered by the marble harness.

```swift
@Test("Calling start() again while already running does not spawn a second task")
func startIsIdempotent() async throws {
    let (source, continuation) = AsyncStream<Int>.makeStream()
    let events = await EventRecorder<Int>.consuming(source)
    var debouncer = Debouncer<Int>(interval: .zero) { value in
        continuation.yield(value)
    }

    debouncer.start()
    debouncer.start()
    debouncer.send(42)

    try await events.waitForEventCount(1)
    #expect(await events.events == [42])

    debouncer.stop()
    continuation.finish()
    await events.detach()
}
```

## Observer lifecycle — recorder detachment after provider stop

```swift
@Test("Recorder detachment prevents further collection")
func recorderDetachmentPreventsFurtherCollection() async throws {
    let harness = await Harness()
    let events = await EventRecorder<Thread>.consuming(harness.provider.data)

    await harness.start()
    _ = try await events.waitFor { $0.name == "Test Channel" }

    await harness.stop()      // awaits lifecycle drain
    await events.detach()     // awaits collection-task termination

    let baseline = await events.events.count
    provokeExternalEmission() // potentially racy external event
    try await events.expectNoEvents(for: .milliseconds(50))
    #expect(await events.events.count == baseline)
}
```

This example proves attachment and recorder detachment. Its post-detach count is stable by construction, so it does not independently prove that `harness.stop()` stopped production emissions. To test that claim, keep a separate observer attached while provoking the external event, or assert producer-owned completion evidence before taking the final snapshot.

## State transition — "view model reaches loaded state"

```swift
@MainActor
@Test("View model reaches .loaded on first emission")
func reachesLoadedOnFirstEmission() async throws {
    let viewModel = makeViewModel()
    viewModel.start()

    let loaded = try await waitForValue(timeout: .seconds(2)) {
        guard case let .loaded(content) = viewModel.state else { return nil }
        return content
    }

    #expect(loaded.items.count == 1)
    viewModel.stop()
}
```

Budgeted polling on published state is acceptable here because view-model state is the event surface.

## Synchronous main-actor callbacks — "effect applied"

If the system invokes a synchronous `@MainActor` callback inside the awaited operation, record into local state and assert after the operation returns. An `AsyncStream` collector would make the test wait on a separate task that has no bearing on whether the callback ran.

```swift
@MainActor
@Test("Observers apply reconciled effects while active")
func appliesReconciledEffectsWhileActive() async throws {
    var appliedEffects: [Effect] = []
    let observer = makeObserver { effect in
        appliedEffects.append(effect)
    }

    observer.start()
    await reconciler.reconcile(.insert("inserted"))

    #expect(appliedEffects == [.insert("inserted")])
}
```

## Refreshable subscriptions — "refresh emits the data this test requested"

When a test verifies a watched query, cache-observed subscription, or a view model fed by one, drive the system through the same **awaitable refresh handle** production uses (`refreshAndWait()`-shaped). The handle is the operation boundary; it must represent the refresh that was requested, not an unrelated future emission.

```swift
@Test("Refresh preserves fresher fields")
func refreshPreservesFresherFields() async throws {
    let refreshable = client.executeRefreshable(ItemsSubscription(scopeId: 1))
    let events = await EventRecorder<Response<[Item]>>.consuming(refreshable.sequence)

    _ = try await events.waitFor { $0.model.first?.name == "Read item" }

    await refreshable.refreshAndWait()

    let refreshed = try await events.waitFor { $0.model.first?.updatedAt == newerDate }
    #expect(refreshed.model.first?.readAt == expectedReadTimestamp)
    await events.detach()
}
```

Do not mutate the backing store or cache directly when the behavior under test is "the subscriber observes a refresh" — that bypasses the observation path the test exists to prove. For view models, prefer a package-internal seam that calls the production refresh handle for the specific stream under test.

The production side must keep the contract too: an outer refreshable awaits the active inner `refreshAndWait()` directly — never forwards through fire-and-forget `refresh()` or a spawned task and then waits for "some emission." If the outer refresh must wait for an inner refreshable to be created, check cancellation before each wait, immediately after each wait returns, and immediately before forwarding. A cancelled caller must not spin a readiness loop or start stale refresh work. For cache-observed queries whose store-change callbacks are scheduler-driven, force a cache read after the fetch so refresh completion does not depend on those callbacks arriving promptly.

## NotificationCenter async sequences — "notification observed"

Posting once after `Task.sleep` is not a subscription handshake. If production listens through `NotificationCenter`'s async sequence and exposes no readiness signal, make the listener's completion observable, then post under a real-time deadline until that observation arrives:

```swift
let observed = await EventRecorder<Void>.recording()
let listener = Task {
    for await _ in notificationCenter.notifications(named: .protectedDataDidBecomeAvailable) {
        await observed.record(())
        return
    }
}

try await withAsyncCleanup(
    operation: {
        try await postUntilObserved(notificationCenter, name: .protectedDataDidBecomeAvailable) {
            await observed.events.count == 1
        }
    },
    cleanup: {
        listener.cancel()
        await listener.value
    }
)
```

`postUntilObserved` posts, checks the supplied observable completion, and spends a timeout-budget slice before trying again. It fails locally when the budget is exhausted. Do not infer completion from `Task` state or await `listener.value` inside the retry loop: either can leave the loop waiting forever after the only event was missed. The awaited cleanup cancels and joins the listener on every path. Prefer a readiness seam when production can expose one without weakening the API.

## Non-occurrence — "after stop, no more X"

Prove attachment, take a baseline, provoke the action, and keep observation live for the bounded no-event window. Detach during cleanup before reading a final collected transcript. A post-detach stable-count assertion establishes recorder detachment only; source-stop correctness needs independent live observation or producer-owned completion evidence.

## Cancellation correctness

Use the serial executor only when the test relies on Swift task ordering. Cancel the task under test, await its termination, and assert evidence that the operation observed cancellation and completed cleanup. If checking for later source emissions, keep an independent observer live for the bounded window. Detaching that observer before the window proves only recorder termination.
