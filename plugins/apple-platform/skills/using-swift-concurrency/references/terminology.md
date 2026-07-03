# Terminology

Use this reference to resolve Swift Concurrency vocabulary quickly.

## Core keywords and attributes

| Term | Meaning |
|---|---|
| `async` | Function may suspend. Callers use `await`. |
| `await` | Marks a possible suspension point. State assumptions can become stale after it. |
| `throws` | Function can throw. Cancellation is often represented by throwing `CancellationError`. |
| `actor` | Reference type that serializes access to actor-isolated mutable state. Reentrant at suspension points. |
| `@MainActor` | Global actor for main/UI isolation. Use for UI state and UI APIs. |
| `@globalActor` | Defines a custom global actor for a broad serial domain. |
| `nonisolated` | Opts a declaration out of actor isolation or default actor inference. For async functions with modern settings, often inherits caller isolation. |
| `nonisolated(nonsending)` | Explicit spelling for nonisolated async functions that run on caller isolation without sending arguments/results over an actor boundary by default. |
| `@concurrent` | Async function explicitly switches off the caller actor and may run concurrently with it. Requires safe transfers. |
| `isolated` parameter | Gives a function scoped access to an actor’s isolation. The parameter cannot escape. |
| `#isolation` | Macro representing the caller’s current isolation, often used as a default argument. |
| `Sendable` | Protocol for types safe to transfer/use across concurrency domains. |
| `@Sendable` | Function type/closure safe to transfer/use across concurrency domains. Captures are checked. |
| `sending` | Transfer marker for values crossing isolation; caller must not keep using the transferred region unsafely. |
| `nonsending` | Describes non-transfer behavior for isolation/async function semantics. |
| `@unchecked Sendable` | Manual Sendable conformance. Compiler does not verify the safety proof. |
| `@preconcurrency` | Migration attribute for declarations/imports/conformances from before full concurrency checking. |
| `nonisolated(unsafe)` | Escape hatch that bypasses isolation checking. Last resort only. |
| `MainActor.run` | Dynamically executes a synchronous closure on MainActor. Prefer static `@MainActor` APIs. |
| `assumeIsolated` | Runtime assertion/recovery of actor isolation. Traps if wrong. Last resort. |
| `isolated deinit` | Deinitializer isolation support for actor/global-actor isolated types. Use when cleanup must access isolated state. |

## Task terms

| Term | Meaning |
|---|---|
| Task | Unit of asynchronous work. |
| Structured task | Child task with lexical lifetime and cancellation relationship, e.g. `async let`, task group. |
| Unstructured task | `Task {}` or `Task.immediate {}`. Has a handle but no lexical parent-child lifetime. |
| Detached task | `Task.detached {}`. Does not inherit actor context; use sparingly. |
| Immediate task | `Task.immediate {}`. Begins on caller context synchronously until first actual suspension. |
| Task group | Dynamic structured child-task collection. |
| `async let` | Fixed structured child task binding. |
| Cancellation | Cooperative flag plus cancellation propagation in structured tasks. Work must observe it. |
| Priority | Scheduling hint. Usually inherited; explicit priority needs justification. |
| Task-local values | Values scoped to a task hierarchy; detached tasks do not inherit the same way. |

## Isolation terms

| Term | Meaning |
|---|---|
| Isolation domain | Actor, global actor, task region, or nonisolated context that controls access. |
| Actor-isolated | Accessible synchronously only on that actor. Outside callers need `await` or isolated access. |
| Global-actor-isolated | Isolated to a global actor such as MainActor. |
| Nonisolated | Not isolated to a specific actor by the declaration. |
| Default actor isolation | Per-module setting that infers MainActor or nonisolated for unannotated declarations. |
| Split isolation | One type mixes multiple isolation domains. Usually confusing. |
| Reentrancy | Actor can process other work while an actor method is suspended. |
| Critical section | Synchronous region that must not be interleaved. Ends at `await` or lock release. |
| Region-based isolation | Compiler model that can allow safe transfer of non-Sendable values when no unsafe aliases remain. |

## Build settings

| Setting | Meaning |
|---|---|
| Swift Language Mode = 6 | Enforces Swift 6 language rules. |
| Strict Concurrency = Complete | Checks concurrency issues across the module; Swift 6 mode enforces many as errors. |
| Default Actor Isolation = MainActor | Unannotated declarations in the module tend to infer MainActor isolation. Good for UI targets. |
| Default Actor Isolation = nonisolated / nil | Unannotated declarations are nonisolated by default. Good for domain packages. |
| `NonisolatedNonsendingByDefault` | Upcoming feature flag changing nonisolated async defaults to caller-isolated nonsending behavior. |
| `InferIsolatedConformances` | Upcoming feature flag allowing global-actor isolated conformance inference. |
| Approachable Concurrency | Xcode grouping around MainActor defaults and related upcoming features. Check actual underlying settings. |

## Availability terms

| Term | Meaning |
|---|---|
| Deployment target | Lowest OS version the app must run on, e.g. iOS 16. |
| SDK availability | Whether a symbol exists in the SDK used to build. |
| Runtime availability | Whether the symbol exists on the user’s OS. |
| `#available` | Runtime availability check. |
| `@available` | Declaration availability annotation. |
| `#if canImport` | Compile-time module availability check. Not a runtime OS check. |
| `#if compiler` | Compile-time compiler version check. Not an SDK/OS check. |
| Beta SDK | Unstable API surface; isolate and gate usage. |

## Common protocols

| Protocol | Concurrency considerations |
|---|---|
| `Identifiable` | `id` is synchronous. Prefer immutable nonisolated Sendable ID. |
| `Equatable` | `==` is synchronous. Compare immutable identity or use isolated conformance. |
| `Hashable` | Hash must be stable. Do not hash mutable UI state. |
| `Codable` | Prefer DTOs. Synthesis and `CodingKeys` may need nonisolated handling under MainActor defaults. |
| `CustomStringConvertible` | `description` is synchronous and may be called anywhere. Prefer snapshots. |
| `ObservableObject` | iOS 16-compatible baseline for SwiftUI view models. Usually `@MainActor`. |
| `Observable` / `@Observable` | Observation framework. Availability-gate for iOS 16 support. Usually `@MainActor` for UI. |
| Delegate protocols | Often legacy/nonisolated. Use adapters or isolated conformances. |

## Escape hatches ranked from safer to riskier

1. Change the design: value snapshot, actor, MainActor, lock, async requirement, protocol isolation.
2. Isolated conformance.
3. Localized `@preconcurrency` import/conformance.
4. Documented `@unchecked Sendable` with synchronization proof.
5. `assumeIsolated` with runtime proof.
6. `nonisolated(unsafe)`.

If a lower option is chosen, explain why every safer option is unavailable.
