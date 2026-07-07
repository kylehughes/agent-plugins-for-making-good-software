# UI Frameworks

Preserve SwiftUI state, identity, and lifecycle, and UIKit/AppKit ownership and layout semantics when simplifying UI code.

## SwiftUI

SwiftUI simplification must preserve identity, state, lifecycle, layout, and accessibility.

### State and Identity

- Use the right state owner: `@State` for view-owned value state, `@Binding` for parent-owned state, `@StateObject` for view-owned reference models, `@ObservedObject` for externally owned models, environment wrappers for injected app context, and focus/storage wrappers when appropriate.
- Do not replace a persistent model owner with a recreated model in `body` or an initializer that runs repeatedly.
- Remove mirrored state when it can be derived safely, but preserve state that intentionally captures user edits, in-flight input, focus, selection, scroll position, animation phase, or presentation state.
- Preserve stable identity in `ForEach`, lists, grids, navigation paths, matched geometry, scroll targets, and diffing. Do not use indices or random IDs unless identity is truly positional or ephemeral.
- Avoid `.id(...)` as a reset hammer unless reset semantics are intentional.
- Preserve `EquatableView`, `.equatable()`, and memoization only when they protect meaningful performance or behavior; remove them when they are obsolete and safe.

### Lifecycle and Effects

- Keep `body` pure and cheap. Do not start network requests, database writes, subscriptions, timers, task creation, or analytics events directly from `body`.
- Prefer `.task(id:)` for async effects tied to view identity/input. Preserve cancellation when the view disappears or input changes.
- Use `.onAppear`/`.onDisappear` carefully; they can run multiple times. Do not move one-time app logic there unless repeats are harmless or guarded.
- Preserve scene lifecycle, app lifecycle, deep links, handoff, restoration, notification routing, and background behavior.
- Keep presentation state coherent. Sheets, alerts, confirmation dialogs, popovers, navigation destinations, and full-screen covers should not be driven by duplicated boolean/item state that can conflict.

### Layout, Navigation, and Rendering

- Preserve Dynamic Type, layout direction, safe areas, keyboard avoidance, scroll behavior, focus, edit mode, selection, hover/pointer, split-view behavior, and platform idioms.
- Avoid `GeometryReader` for simple layout when stacks, grids, layout priorities, view-that-fits, container-relative frames, or custom layout primitives already fit.
- Avoid `AnyView` unless required for storage, ABI, or type erasure at a real boundary.
- Break very large views into named subviews only when it improves identity, state ownership, reuse, or readability. Do not fragment views into wrappers that add no behavior.
- Preserve navigation path types, deep-link restoration, destination availability, back behavior, and programmatic navigation semantics.
- Be cautious when replacing older navigation APIs with newer ones in apps that support older OS versions.
- Avoid expensive formatting, sorting, filtering, image work, or allocation inside `body`; move stable work into models, cached derived values, or local constants with clear invalidation.

### Accessibility and Localization in SwiftUI

- Preserve `accessibilityLabel`, `accessibilityValue`, `accessibilityHint`, `accessibilityIdentifier`, traits, sort priority, focus behavior, Dynamic Type, reduced motion, high contrast, color-blind safety, and VoiceOver grouping.
- Do not replace localized `Text` or `LocalizedStringKey` usage with raw `String` interpolation if it changes localization extraction, pluralization, formatting, or grammar.
- Use project localization wrappers and design-system text styles when present.

### Observation

- Use Observation or observable-object patterns according to the repository's deployment target and architecture. Do not migrate `ObservableObject` to newer observation mechanisms unless availability, architecture, and test coverage support the change.
- Preserve dependency injection and testability when simplifying observable models.
- Avoid broad `@MainActor` or observation annotations on pure data types if it creates unnecessary isolation; prefer the narrowest correct isolation.

## UIKit, AppKit, and Representables

### Lifecycle and Ownership

- Preserve view/controller lifecycle semantics. Do not move setup between `init`, `loadView`, `viewDidLoad`, `viewWillAppear`, `viewDidAppear`, `viewWillDisappear`, `deinit`, or SwiftUI representable hooks unless repeat behavior and timing are correct.
- UI work must stay on the main thread/actor.
- Avoid retain cycles in closures, delegates, display links, timers, notifications, Combine subscriptions, and async tasks. Use weak captures only when losing work is acceptable; otherwise create an explicit owner/cancellation path.
- Clean up observers, tasks, timers, gesture recognizers, display links, KVO, delegates, and data sources according to their ownership model.
- Preserve responder chain, target/action behavior, first responder, keyboard commands, menus, focus engine, undo manager, state restoration, and scene/window ownership.

### Reuse, Data Sources, and Layout

- Preserve cell/view reuse semantics. Cancel image/network/task work on reuse and avoid stale async updates.
- Preserve diffable data source identity, section/item IDs, snapshot ordering, animation choices, and reload/reconfigure semantics.
- Do not simplify Auto Layout constraints by removing priority, hugging/compression, safe area, readable content, or intrinsic-size behavior that protects real layouts.
- Avoid adding constraints repeatedly in lifecycle methods that can run multiple times.
- Preserve layout invalidation, preferred content size, trait collection handling, size class behavior, rotation behavior, and content inset adjustment.
- Avoid doing heavy work in scrolling, layout, drawing, or display callbacks.

### SwiftUI Bridges

For `UIViewRepresentable`, `UIViewControllerRepresentable`, `NSViewRepresentable`, and `NSViewControllerRepresentable`:

- Keep coordinator ownership and delegate lifetimes correct.
- Preserve `make*` versus `update*` responsibilities. Do not recreate platform views/controllers in update paths unless intentional.
- Preserve binding propagation, feedback-loop prevention, focus/first-responder behavior, intrinsic size, layout invalidation, and environment changes.
- Cancel or detach work when the represented view/controller is dismantled.
