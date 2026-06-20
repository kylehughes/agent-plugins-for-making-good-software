# Testing Swift

## Contents

- Choose the framework
- Swift Testing fundamentals
- Suites, setup, and state
- Async and concurrent tests
- Time, notifications, and eventual behavior
- Parameterized tests and traits
- Errors, cancellation, and process behavior
- XCTest use cases
- Migration between frameworks
- Test review checklist

## Choose the Framework

Use repository constraints first.

Choose Swift Testing when:

- Adding ordinary unit or integration tests on a supported modern toolchain.
- Parameterization, traits, tags, issue recording, or native Swift concurrency improve the suite.
- The target already imports `Testing` or the task includes an intentional migration.

Choose or retain XCTest when:

- Working in an XCTest UI test target.
- Using XCTest performance measurement APIs.
- Extending a legacy suite where mixed-framework migration would create more risk than value.
- A framework, runner, test plan, or third-party helper depends on XCTest lifecycle APIs.
- Supporting an older toolchain that does not include Swift Testing.

Swift Testing and XCTest can coexist. Do not rewrite a stable suite solely to enforce stylistic uniformity.

## Swift Testing Fundamentals

Prefer direct, behavior-focused tests:

```swift
import Testing
@testable import Checkout

@Test("Expired coupons are rejected")
func rejectsExpiredCoupon() throws {
    let coupon = Coupon(code: "SAVE", expiresAt: .distantPast)
    let validator = CouponValidator(now: { .now })

    #expect(throws: CouponError.expired) {
        try validator.validate(coupon)
    }
}
```

Use `#require` for prerequisites whose failure makes subsequent checks meaningless:

```swift
let first = try #require(results.first)
#expect(first.id == expectedID)
```

Use `#expect` for independent facts so one failure does not hide the others. Prefer comparing full values when the failure
output remains readable; otherwise compare the domain properties that explain the behavior.

Test descriptions are optional. Use one when it makes reports clearer than the function name. Backticked natural-language
function names can also be appropriate if the repository uses them. Avoid duplicating the same sentence in both places.

## Suites, Setup, and State

Swift Testing does not require class-based suites. Prefer a `struct` for ordinary tests and an `actor` only when the test
fixture itself needs isolation. Use initializers and `deinit` or scoped helper resources instead of assuming XCTest setup
semantics.

Keep fixtures local by default. Shared mutable suite state creates ordering and parallelism bugs. For expensive immutable
fixtures, use a documented shared provider and confirm it is `Sendable` and safe under concurrent access.

Avoid doing fallible work in global initialization. Surface fixture failures through test functions or throwing suite
initialization so the runner can report them accurately.

## Async and Concurrent Tests

Swift Testing runs tests in parallel by default. Treat this as a design constraint:

- Give each test unique temporary files, database names, ports, users, and defaults domains.
- Restore global process state in a guaranteed cleanup path.
- Do not depend on test order.
- Avoid static mutable mocks and singleton replacement.
- Make spies and fakes concurrency-safe when callbacks can arrive from multiple tasks.
- Use serialization only for a documented external constraint that cannot be isolated; do not use it to mask races.

Write async tests as async functions and await observable completion. Do not wrap async code in expectations or dispatch
groups merely because an older test used them.

When testing actors, assert externally visible behavior. Avoid reaching into isolation with unsafe annotations. Stress tests
can be useful for race-prone algorithms, but they supplement rather than prove synchronization correctness.

## Time, Notifications, and Eventual Behavior

Do not use arbitrary sleeps as synchronization. They make tests slow and flaky.

Prefer:

- Injected `Clock` values and controllable test clocks.
- Awaiting a task handle or async sequence element.
- A continuation or confirmation tied to the actual callback.
- A state transition exposed by the production abstraction.
- Bounded polling only when testing an external eventually consistent system, with useful timeout diagnostics.

For Swift Testing confirmation APIs, specify expected occurrence semantics and ensure the confirmed event is causally tied
to the action under test. A confirmation that can be fulfilled by stale or unrelated work is not a valid assertion.

Notification tests should use typed messages where the supported platform and design permit them, or isolate the
`NotificationCenter` instance. Remove observers and finish streams deterministically.

## Parameterized Tests and Traits

Use parameterized tests when the behavior is identical across inputs:

```swift
@Test(
    "Whitespace is normalized",
    arguments: [
        ("a  b", "a b"),
        ("  a", "a"),
        ("a\n\tb", "a b"),
    ]
)
func normalizesWhitespace(input: String, expected: String) {
    #expect(normalize(input) == expected)
}
```

Keep cases readable and small. Introduce a named case type when tuple fields become ambiguous or when individual cases
need labels.

Use tags to support meaningful cross-suite selection such as feature ownership or test level. Use traits for supported
behavior such as conditions, time limits, or serialization. Do not create a tag taxonomy that CI does not consume.

On Swift 6.3, tests can record warning-severity issues, cancel themselves explicitly, and attach images on supported
Apple and Windows platforms. Use these features when they improve diagnostics; do not turn ordinary assertions into
attachments or warnings without a reason.

## Errors, Cancellation, and Process Behavior

Test both the error type and information callers rely on. Avoid brittle full-string comparison unless the string is the
public contract.

For cancellation:

- Start the operation under test.
- Establish that it reached the cancellable state without sleeping.
- Cancel through the public lifetime owner.
- Assert prompt completion and the documented cancellation result.
- Verify cleanup of callbacks, tasks, files, and other resources.

Do not swallow `CancellationError` in test helpers; doing so can make a cancelled test appear to pass.

Use exit tests for code that intentionally terminates the process when the supported Swift Testing version and platform
permit it. Otherwise isolate process-level behavior in a helper executable instead of crashing the test runner.

## XCTest Use Cases

Retain XCTest for UI automation:

```swift
final class CheckoutUITests: XCTestCase {
    func testCompletingCheckoutShowsReceipt() {
        let app = XCUIApplication()
        app.launch()
        // Interact through stable accessibility identifiers.
    }
}
```

Use XCTest performance APIs for performance tests and choose metrics relevant to the regression. Warm up when appropriate,
control input size, and avoid asserting exact timing thresholds on noisy shared CI unless the infrastructure is designed
for it.

For callback-based XCTest code, prefer async test methods when APIs can be bridged naturally. If expectations remain
necessary, use specific fulfillment counts and bounded waits with diagnostic messages.

## Migration between Frameworks

Migrate incrementally and preserve behavior:

1. Confirm the minimum toolchain and runner support Swift Testing.
2. Convert one coherent suite, not scattered assertions across many files.
3. Map setup/teardown semantics explicitly; do not assume identical instance lifetime.
4. Replace assertions with `#expect` or `#require` according to control-flow needs.
5. Replace data-driven loops with parameterized tests where each case should be reported independently.
6. Audit tests that depended on serial execution or shared mutable state.
7. Preserve tags, test-plan selection, CI filters, attachments, and failure diagnostics.
8. Run the migrated suite repeatedly and under parallel execution.
9. Keep UI and performance targets on XCTest unless a supported equivalent meets the same need.

## Test Review Checklist

Check that each changed test:

- Fails against the broken or prior implementation for the intended reason.
- Asserts behavior rather than implementation details.
- Is deterministic and parallel-safe.
- Has no arbitrary sleep or unbounded wait.
- Cleans up global state and resources on every path.
- Uses realistic boundary, error, cancellation, and availability cases.
- Does not overmock value types or pure functions.
- Produces actionable failure output.
- Runs in the intended target, scheme, test plan, and CI selection.

Primary references:

- https://developer.apple.com/documentation/testing
- https://developer.apple.com/documentation/testing/migratingfromxctest
- https://developer.apple.com/documentation/xctest
- https://github.com/swiftlang/swift-testing
