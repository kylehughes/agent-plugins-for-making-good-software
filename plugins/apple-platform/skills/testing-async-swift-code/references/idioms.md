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

## Observer lifecycle — "provider stop stops emitting"

```swift
@Test("Provider stop stops emitting updates")
func providerStopStopsEmitting() async throws {
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

The order is the point: prove attachment (first `waitFor`), stop, **detach before the baseline** so the count is stable by construction, then bound the non-occurrence window.

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

Posting once after `Task.sleep` is not a subscription handshake. If production listens through `NotificationCenter`'s async sequence and exposes no readiness signal, drive the notification under a real-time deadline until the state transition is observed:

```swift
try await postUntilObserved(notificationCenter, name: .protectedDataDidBecomeAvailable) {
    authenticationState.value == .unauthenticated
}
```

The helper posts, polls the expected state through the timeout budget, sleeps a slice, and stops at the budget's exhaustion — failing with a local timeout error rather than hanging in a `for await` loop that missed the one post. Prefer adding a readiness seam when the production type can expose one without weakening the API.

## Non-occurrence — "after stop, no more X"

`detach()` first, then `expectNoEvents(for:since:)` from a post-detach baseline. Detachment proves collection-task termination; the baseline makes the stable-count assertion sound; the window is the observation bound, not a scheduler hack.

## Cancellation correctness

Wrap the test body in the serial executor. Cancel the task under test. Use the recorder to assert no further emissions (detach + bounded window). Check exit state synchronously. The test proves all three edges: the task was cancelled, the operation observed cancellation, and cleanup occurred.
