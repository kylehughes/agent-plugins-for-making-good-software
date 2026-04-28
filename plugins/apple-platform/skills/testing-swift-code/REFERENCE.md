# Swift Testing Framework Reference

## XCTest Migration

Use this table when converting existing XCTest code to the Swift Testing framework.

| XCTest | Swift Testing |
|--------|---------------|
| `XCTestCase` | `@Suite struct` |
| `func testX()` | `@Test func x()` |
| `XCTAssertTrue(x)` | `#expect(x)` |
| `XCTAssertFalse(x)` | `#expect(!x)` |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` |
| `XCTAssertNotEqual(a, b)` | `#expect(a != b)` |
| `XCTAssertNil(x)` | `#expect(x == nil)` |
| `XCTAssertNotNil(x)` | `#expect(x != nil)` |
| `XCTAssertGreaterThan(a, b)` | `#expect(a > b)` |
| `XCTAssertLessThan(a, b)` | `#expect(a < b)` |
| `XCTAssertThrowsError(expr)` | `#expect(throws: (any Error).self) { expr }` |
| `XCTUnwrap(x)` | `try #require(x)` |
| `XCTFail("msg")` | `Issue.record("msg")` |
| `setUp()` / `setUpWithError()` | `init()` / `init() throws` |
| `tearDown()` | `deinit` |
| `XCTSkipIf(condition)` | `@Test(.enabled(if: !condition))` |
| `addTeardownBlock { }` | Use `defer` or `deinit` |
| `measure { }` | Not yet available in Swift Testing; continue using XCTest for benchmarks |

### Migration Notes

- Swift Testing test functions do not need a `test` prefix. The `@Test` macro replaces the naming convention.
- Use `struct` suites instead of `class` subclasses. Each test gets a fresh struct instance, so stored properties act as implicit per-test setup without `setUp()`.
- `@Suite(.serialized)` replaces serial test execution that XCTest provided by default. Swift Testing runs tests in parallel unless told otherwise.
- XCTest and Swift Testing can coexist in the same target during incremental migration. Do not subclass `XCTestCase` in a `@Suite` struct.

