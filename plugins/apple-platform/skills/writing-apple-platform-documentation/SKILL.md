---
name: writing-apple-platform-documentation
description: "Write or review Swift doc comments, DocC, and Apple-platform developer docs. Use for API contracts, terminology, availability, and lifecycle wording; compose with writing-technical-prose when available."
---

# Writing Apple Platform Documentation

Run this as the Apple-platform companion to the universal `writing-technical-prose` skill. It layers Apple-specific documentation rules — terminology, doc comments, DocC fields, availability, and privacy wording — on top of the universal voice, structure, and truth rules. When this guidance conflicts with a generic prose rule for Apple-platform prose, this guidance wins. Keep it subordinate to project conventions and Apple's current terminology when verified.

## Terminology and Capitalization

Prefer precise platform names:

- `Apple platforms` for behavior shared across iOS, iPadOS, macOS, watchOS, tvOS, and visionOS.
- `iOS`, `iPadOS`, `macOS`, `watchOS`, `tvOS`, `visionOS` when behavior is platform-specific.
- `Swift`, `SwiftUI`, `UIKit`, `AppKit`, `Foundation`, `Combine`, `Observation`, `Core Data`, `CloudKit`, `StoreKit`, `WidgetKit`, `XCTest`, `XCUITest`, `DocC`, `Xcode`, `TestFlight`, `App Store Connect`.
- `Swift Package Manager` on first use if readers may not know `SwiftPM`.
- `APNs`, not `APNS`.
- `In-App Purchase` for the Apple commerce feature; `in-app purchase` for a generic phrase when not naming the feature.
- `MainActor`, `Sendable`, `async`/`await`, `Task`, `actor`, `nonisolated`, and other Swift keywords or symbols in backticks when referring to code.

Do not use `iOS` as a synonym for every Apple platform. If an API behaves differently on macOS or visionOS, say so.

## Swift Doc Comments

Use `///` comments for declarations unless the project uses block comments for long DocC articles.

The first sentence should be a complete summary of the declaration’s purpose. Do not start with “This method” or restate the symbol name.

```swift
/// Fetches the cached image for a request or loads it from the remote source.
public func image(for request: ImageRequest) async throws -> Image
```

For complex APIs, add paragraphs in this order when relevant:

1. Purpose and high-level behavior.
2. Lifecycle, ownership, or state changes.
3. Concurrency, cancellation, and actor/thread requirements.
4. Parameters, returns, throws, and examples.
5. Important caveats or platform differences.

```swift
/// Coordinates image loading, decoding, and memory-backed caching.
///
/// `ImagePipeline` coalesces identical in-flight requests and stores decoded images
/// in memory until the configured cache evicts them.
///
/// Calls are safe from any actor. Completion handlers run on the actor that awaits
/// the result; UI updates still belong on the main actor.
public actor ImagePipeline { }
```

## DocC Fields and Callouts

Use DocC fields when they improve correct API use.

```swift
/// Creates a thumbnail for the image at the specified URL.
///
/// - Parameters:
///   - url: The local file URL of the source image.
///   - size: The target size in points.
/// - Returns: A decoded thumbnail image.
/// - Throws: `ThumbnailError.unsupportedFormat` when the file type cannot be decoded.
public func thumbnail(for url: URL, size: CGSize) async throws -> Image
```

Use callouts for semantics that affect correctness:

```swift
/// - Important: Call this method from the main actor when the result updates UIKit state.
/// - Warning: This method overwrites any existing file at `destinationURL`.
/// - Note: Cancellation stops future retries but does not cancel a request already sent by `URLSession`.
```

Do not overuse callouts for ordinary details. A document full of notes is harder to scan than a direct paragraph.

## What to Document for Apple APIs

Document these when they affect callers:

- `@MainActor` requirements and main-thread UI constraints.
- `Sendable` requirements and whether values cross concurrency domains.
- Cancellation behavior for `async` APIs.
- Reentrancy and ordering when using actors, delegates, notifications, or streams.
- Ownership and lifetime of delegates, coordinators, tasks, observers, cancellables, and closures.
- SwiftUI state ownership: `@State`, `@Binding`, `@ObservedObject`, `@StateObject`, `@Environment`, and `@Observable`.
- UIKit/AppKit lifecycle boundaries: view loading, appearance callbacks, responder chain, window/scene lifecycle.
- Platform availability and behavior differences.
- Entitlements, privacy prompts, background modes, and App Store review-sensitive behavior.
- Persistence, keychain, local files, iCloud, CloudKit, and data migration behavior.
- Accessibility, localization, dynamic type, right-to-left layout, and privacy-sensitive logging.

## Availability and Compatibility

State availability only when verified from code, package manifests, deployment targets, or current Apple documentation.

```markdown
Requires iOS 17.0+ and Xcode 16.0+.
```

Use `iOS 17.0+`, not `iOS17+`. If availability is conditional, name the condition.

```swift
@available(iOS 17.0, macOS 14.0, *)
public struct SearchConfiguration { }
```

Do not promise behavior on betas, future OS versions, or unreleased SDKs unless the source material explicitly supports it.

## Swift Examples

Examples should be close to compile-ready. Include enough context for the reader to understand ownership, actor isolation, and error handling.

```swift
let pipeline = ImagePipeline(cache: .shared)
let image = try await pipeline.image(for: ImageRequest(url: avatarURL))
```

Avoid examples like this unless the surrounding text is explicitly abstract:

```swift
let result = try await manager.doThing(foo: "bar")
```

## Comments Inside Swift Implementations

Prefer comments that explain invariants or platform workarounds.

```swift
// UIKit sends a second layout pass after trait changes. Keep the cached size until
// `viewDidLayoutSubviews()` observes the final bounds.
```

Avoid comments that restate the code.

```swift
// Bad: Increment the count.
count += 1
```

## Common Apple-Specific Corrections

| Weak | Better |
|------|--------|
| APNS | APNs |
| OSX | macOS |
| MacOS | macOS |
| IOS | iOS |
| app store | App Store |
| xcode | Xcode |
| swiftui | SwiftUI |
| ui kit | UIKit |
| in app purchase, when naming Apple’s feature | In-App Purchase |
| push notifications service | Apple Push Notification service, then APNs |

## Privacy and Security Wording

For Apple-platform docs, name the user-visible permission, entitlement, or data class when relevant. Do not bury privacy behavior in setup instructions.

```markdown
The app requests Photos access only when the user imports an image. Denying access leaves the existing project unchanged.
```

For logs and diagnostics, specify what is redacted.

```markdown
Diagnostics include request timing and HTTP status codes. They do not include access tokens, image contents, or user-entered text.
```
