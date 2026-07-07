# Availability and Version Spanning

Reference for guarding APIs across the iOS 16 through iOS 26/27 deployment span.

## Availability and Version Spanning

The default deployment span is iOS 16 through stable iOS 26. Availability handling is mandatory for APIs introduced after iOS 16.

- Use `if #available(iOS X.Y, *)` for runtime behavior branches.
- Use `@available(iOS X.Y, *)` when an entire declaration is unusable before that OS.
- Prefer the narrowest viable availability boundary. Do not wrap an entire file when one method or helper can be isolated.
- Always provide an iOS 16-compatible path unless the enclosing declaration is explicitly unavailable before a newer OS.
- Do not use `UIDevice.current.systemVersion`, string comparisons, build numbers, or beta OS checks for API availability.
- Use `#if canImport(...)` for optional modules only, not for OS-version gating.
- Do not add `#if swift(...)` or `#if compiler(...)` branches for old Swift versions. Swift 6.3 is the target.
- Do not introduce iOS 27 beta APIs unless explicitly requested. When requested, isolate beta usage with `@available(iOS 27.0, *)` or `if #available(iOS 27.0, *)`, and keep a stable iOS 16-26 path.
- SDK-provided macros and property wrappers still obey framework availability. A Swift 6.3 compiler does not make an iOS 17+ framework API deployable to iOS 16.

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
