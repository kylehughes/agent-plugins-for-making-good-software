# Availability and Version Spanning

Reference for guarding APIs from the iOS 16 baseline through the selected current SDK.

## Availability and Version Spanning

Inspect the target’s deployment span and selected Xcode/SDK first. The iOS 16 examples below illustrate a compatibility lane, not a required minimum. Availability handling is mandatory for APIs introduced after the actual minimum. When a compiler feature or SDK channel affects the choice, consult the shared [feature-status guidance](../../modeling-swift-types-for-correctness/references/swift-feature-status.md#swift-64-release-matrix).

- Use `if #available(iOS X.Y, *)` for runtime behavior branches.
- Use `@available(iOS X.Y, *)` when an entire declaration is unusable before that OS.
- Prefer the narrowest viable availability boundary. Do not wrap an entire file when one method or helper can be isolated.
- Provide a path compatible with the target’s actual deployment minimum unless the enclosing declaration explicitly requires a newer OS.
- Do not use `UIDevice.current.systemVersion`, string comparisons, build numbers, or beta OS checks for API availability.
- Use `#if canImport(...)` for optional modules only, not for OS-version gating.
- Preserve the selected compiler and supported language modes. Add `#if swift(...)` or `#if compiler(...)` only when the project deliberately supports multiple language/compiler configurations.
- Use a preview compiler or SDK only after an explicit project decision. Isolate APIs by their documented introduction versions with `@available` or `if #available`, and retain a compatible path for the project’s actual deployment minimum.
- SDK-provided macros and property wrappers still obey framework availability. A newer compiler does not make an iOS 17+ framework API deployable to iOS 16.

Stored properties need special care. If a stored property has a type that is only available on iOS 17+, the containing type effectively cannot be used on iOS 16. Isolate the newer type in an available helper or erase the storage behind an iOS-16-safe abstraction.

```swift
// ❌ BAD: newer API used with no iOS 16 path
func configure() {
    useFeatureIntroducedAfterIOS16()
}

// ✅ GOOD: newer API is guarded and the fallback remains explicit
func configure() {
    if #available(iOS 17.0, *) {
        useFeatureIntroducedAfterIOS16()
    } else {
        useIOS16Fallback()
    }
}
```
