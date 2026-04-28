# Isolation and Protocol Conformances

Use this reference to resolve protocol conformance isolation mismatches in Swift 6+. If you control the protocol definition, also read `protocol-design.md` before fixing only the conforming type.

Source: Matt Massicotte, "Concurrency Step-by-Step: Conforming to Protocols", <https://www.massicotte.org/step-by-step-conforming-to-protocols/>, accessed 2025-11-24.

## Contents

- [The Core Problem](#the-core-problem)
- [Solution Selection](#solution-selection)
- [Solution 1: Nonisolated Type (Preferred)](#solution-1-nonisolated-type-preferred)
- [Solution 2: Isolated Conformance (Swift 6.2+)](#solution-2-isolated-conformance-swift-62)
- [Solution 3: Preconcurrency Conformance](#solution-3-preconcurrency-conformance)
- [Solution 4: Dynamic Isolation (Last Resort)](#solution-4-dynamic-isolation-last-resort)
- [Swift 6.2 Compiler Settings](#swift-62-compiler-settings)
- [Decision Flowchart](#decision-flowchart)
- [Common Protocols Affected](#common-protocols-affected)
- [Non-Sendable First Design](#non-sendable-first-design)

## The Core Problem

When a MainActor-isolated type conforms to a nonisolated protocol (like `Equatable`), the compiler reports:

```
Conformance of 'MyType' to protocol 'Equatable' crosses into main actor-isolated code and can cause data races
```

This happens because:
- The protocol expects nonisolated methods callable from any thread
- The type's methods are MainActor-isolated, callable only from the main thread
- These requirements conflict

## Solution Selection

Choose the appropriate solution based on context:

| Solution | When to Use |
|----------|-------------|
| **Nonisolated type** | Type doesn't need actor isolation; uses non-Sendable for safety |
| **Isolated conformance** | Type needs MainActor; protocol is compatible with isolation |
| **Preconcurrency conformance** | Protocol incompatible with isolated conformances |
| **nonisolated-assumeIsolated** | Last resort; non-global actor types |

## Solution 1: Nonisolated Type (Preferred)

Before adding isolation, question whether the type actually needs it.

```swift
@Observable
nonisolated class ImageModel {
    private var state: Bool = true

    var imageName: String {
        state ? "star" : "star.fill"
    }

    func toggle() {
        state.toggle()
    }
}

extension ImageModel: Equatable {
    static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        lhs.state == rhs.state
    }
}
```

**Why this works**: Non-Sendable types cannot leave their isolated context. When instantiated on the MainActor (e.g., in a SwiftUI View), they remain stuck there—no explicit isolation needed.

**When to use**:
- Type doesn't perform internal async operations
- Safety comes from usage context, not type definition
- Maximum flexibility across different actors

**Limitation**: Difficult when the type itself needs to use concurrency features internally.

## Solution 2: Isolated Conformance (Swift 6.2+)

Constrain the conformance to a specific global actor:

```swift
@MainActor @Observable
class ImageModel {
    private var state: Bool = true
    // ...
}

extension ImageModel: @MainActor Equatable {
    static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        lhs.state == rhs.state
    }
}
```

**How it works**: Creates a MainActor-specific variant of the protocol. The type is `Equatable`, but only from the MainActor context.

**Implicit inference** (Swift 6.2 with `InferIsolatedConformances`):
```swift
// With default-isolation: MainActor and InferIsolatedConformances: enabled
extension ImageModel: Equatable {  // Implicitly @MainActor
    static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        lhs.state == rhs.state
    }
}
```

**When to use**:
- Type genuinely needs MainActor isolation
- Protocol is compatible with isolated conformances
- Using Swift 6.2+

**Limitation**: Not all protocols support isolated conformances. Some have inherently concurrent behaviors.

## Solution 3: Preconcurrency Conformance

Use when isolated conformances aren't compatible:

```swift
@MainActor @Observable
class ImageModel {
    // ...
}

extension ImageModel: @preconcurrency Equatable {
    static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        lhs.state == rhs.state
    }
}
```

**How it works**: Tells the compiler "treat this protocol as if it should be MainActor-isolated". Prevents calling `==` off the MainActor.

**When to use**:
- Isolated conformances cause compatibility issues
- Need compile-time safety without isolated conformance complexity

**Limitation**: Semantically implies the protocol *should* be isolated but isn't—which isn't always accurate.

## Solution 4: Dynamic Isolation (Last Resort)

The pre-Swift 6.0 approach using `assumeIsolated`:

```swift
extension ImageModel: Equatable {
    nonisolated static func == (lhs: ImageModel, rhs: ImageModel) -> Bool {
        MainActor.assumeIsolated {
            lhs.state == rhs.state
        }
    }
}
```

**How it works**:
1. Mark method `nonisolated` to match protocol requirement
2. Use `assumeIsolated` to assert runtime isolation
3. Crashes if called from wrong thread

**When to use**:
- Non-global actor types
- No other solution works

**Limitations**:
- Verbose boilerplate
- Runtime crashes instead of compile-time errors
- Sendable restrictions at actor boundaries

## Swift 6.2 Compiler Settings

Understanding these flags is critical:

| Flag | Effect |
|------|--------|
| `default-isolation: MainActor` | All declarations default to MainActor |
| `InferIsolatedConformances` | Automatically infer isolated conformances for global actor types |

**Important**: These are independent settings. "Approachable Concurrency" in Xcode controls both, but they can be configured separately.

**Note**: Enabling `default-isolation: MainActor` implicitly enables `InferIsolatedConformances`.

## Decision Flowchart

```
Does the type actually need actor isolation?
├─ No → Use nonisolated type (Solution 1)
└─ Yes → Is the protocol compatible with isolated conformances?
         ├─ Yes → Use isolated conformance (Solution 2)
         └─ No/Unsure → Use preconcurrency (Solution 3)
                        └─ Still failing? → Use assumeIsolated (Solution 4)
```

## Common Protocols Affected

These nonisolated protocols frequently trigger isolation mismatches:
- `Equatable`
- `Hashable`
- `Comparable`
- `Codable` (`Encodable`, `Decodable`)
- `CustomStringConvertible`
- `Identifiable`

## Non-Sendable First Design

A powerful pattern: keep types nonisolated and non-Sendable by default.

**Principle**: Instead of isolating the type definition, let the usage context provide isolation. Non-Sendable types cannot cross actor boundaries, so they're "stuck" wherever they're created.

```swift
// The type is nonisolated
nonisolated class Model { ... }

struct ContentView: View {
    // Created on MainActor, stuck on MainActor
    @State private var model = Model()
}
```

**Benefits**:
- Simpler protocol conformances
- More flexible—works with any actor
- Entire object graphs can share this pattern

**Challenge**: Complex when the type needs internal async operations.
