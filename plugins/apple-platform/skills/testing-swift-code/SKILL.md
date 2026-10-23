---
name: testing-swift-code
description: "Plan or write Swift unit tests with Swift Testing. Use proactively for regression coverage, assertions, suites, traits, or migration; async timing has its own skill and UI tests use XCTest."
---

# Testing Swift Code

Write tests using the Swift `Testing` framework (Swift 6 / Xcode 16+). It provides macro-based annotations and expression-level assertions for unit and integration tests. Preserve existing XCTest suites unless migration is requested; UI and performance tests still use XCTest.

Ordinary function-output regression tests stay here. Positive, negative, empty, or boundary inputs do not by themselves call for type modeling or invariant verification; those skills address representations and enforcement boundaries.

For a test plan, give each test a clear behavior-based name and concrete input/expected-output assertions. A parameterized table can share one named test; identify that test as well as what its rows cover. Mark planned checks as unrun.

## Quick Start

```swift
import Testing

@Suite("Calculator Tests")
struct CalculatorTests {
    @Test("Addition")
    func addition() {
        #expect(2 + 2 == 4)
    }

    @Test(arguments: [1, 2, 3])
    func isPositive(i: Int) {
        #expect(i > 0)
    }
}
```

## Assertions

Use `#expect` for non-fatal checks that let the test continue, and `#require` for preconditions that should stop the test immediately if they fail. `#require` throws on failure, so the test function must be marked `throws`.

```swift
@Test func checking() throws {
    let x: Int? = 42
    let y = try #require(x) // Unwraps or stops the test
    #expect(y == 42)        // Records failure but continues
}
```

### Error Testing

```swift
// Expect a specific error type
#expect(throws: MyError.self) { try risky() }

// Expect any error
#expect(throws: (any Error).self) { try risky() }

// Expect no error
#expect(throws: Never.self) { try safe() }
```

## Test Organization

Use `struct` suites by default. Each test gets a fresh instance, providing natural isolation without explicit setup/teardown. Use `init` for shared setup.

```swift
@Suite("Networking")
struct NetworkingTests {
    let client: APIClient

    init() {
        client = APIClient(baseURL: .test)
    }

    @Test func fetchUser() async throws {
        let user = try await client.fetchUser(id: 1)
        #expect(user.name == "Alice")
    }
}
```

## Traits

Control test execution with traits passed to `@Test` or `@Suite`:

```swift
@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] != nil))
func ciOnly() { ... }

@Test(.timeLimit(.minutes(1)))
func bounded() async { ... }

@Test(.tags(.integration))
func networkTest() { ... }

@Suite(.serialized) // Serialize this suite’s tests; unrelated suites may still run in parallel
struct SerialTests { ... }

@Test(.disabled("Blocked by #1234"))
func pendingFeature() { ... }
```

## Parameterized Tests

Run the same logic over multiple inputs. Each argument combination runs as a separate test case in the results.

```swift
@Test(arguments: [1, 2, 3])
func isPositive(i: Int) {
    #expect(i > 0)
}

// Combinatorial: runs all pairs (4 tests)
@Test(arguments: [1, 2], ["a", "b"])
func combinations(i: Int, s: String) { ... }

// Zipped: runs matched pairs (2 tests)
@Test(arguments: zip([1, 2], ["a", "b"]))
func pairs(i: Int, s: String) { ... }
```

## Async Testing

Mark the test function `async`. A `confirmation` checks the callback count when its body returns; it does not wait for future callbacks. Await the operation’s completion inside the body and remove any retained callback during cleanup:

```swift
@Test func callbacks() async {
    await confirmation("Called 3 times", expectedCount: 3) { confirm in
        stream.onReceive = { confirm() }
        await stream.start()
    }
}
```

## Known Issues

Mark tests with known failures using `withKnownIssue` so they do not count as unexpected failures:

```swift
@Test func knownBug() {
    withKnownIssue {
        #expect(buggyFunction() == 42)
    }
}
```

## Detailed Reference

See [REFERENCE.md](REFERENCE.md) for the XCTest migration table mapping `XCTAssert*` calls to their Swift Testing equivalents.
