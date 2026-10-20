<!-- rubric-id: swift-type-ownership-lifetime-behavior-v1 -->

# Behavioral acceptance

Require all of the following:

- Distinguishes a scoped borrowed view from ownership transfer and uses a scoped callback, owned copy, or supported lifetime-restricted projection according to what must survive. It identifies retaining a borrowed view after the buffer's scope as the concrete misuse.
- Uses noncopyability only if duplicating the decoder authority itself is invalid; it does not present it as proof of deep immutability, external-buffer uniqueness, or lifetime safety for arbitrary aliases.
- Audits escaping closures, raw handles, erasure, and foreign/aliasing boundaries, and states that the actual decoder/storage lifetime remains an implementation obligation.
- Shows a successful focused local load of `references/ownership-effect-recipes.md` at ownership/lending. Loading `references/ownership-concurrency-errors.md` is warranted only when the selected ownership syntax or concurrency boundary needs it.
- Separates a compile-time use-after-consume or escape control, where supported, from runtime buffer/lifetime tests, and reports their proof limits without fabricating runs.
- Leaves the workspace unchanged.
