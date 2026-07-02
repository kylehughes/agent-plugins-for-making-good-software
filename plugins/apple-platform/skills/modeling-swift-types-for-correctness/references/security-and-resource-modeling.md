# Security and Resource Modeling

Use this reference when types represent authentication, authorization, secrets, personally identifiable information, cryptographic material, URLs, paths, files, native handles, or data trusted for a particular interpreter.

## Types Narrow Misuse; They Do Not Replace Enforcement

A nominal wrapper can prevent accidental substitution inside one process. It does not replace:

- Server-side authorization.
- Signature or certificate verification.
- Cryptographic integrity.
- Sandbox and entitlement checks.
- Database constraints and transactions.
- Runtime validation of untrusted bytes.
- Revocation, expiry, or current-policy evaluation.

State the threat model before calling a type “secure.” Distinguish accidental misuse by ordinary code from malicious input, compromised dependencies, memory inspection, replay, and privilege changes.

## Authentication State Is Correlated Data

Do not store an authentication flag separately from the session it claims exists.

```swift
enum AuthenticationState: Sendable {
    case signedOut
    case restoring
    case signedIn(SessionSnapshot)
    case reauthenticationRequired(ExpiredSession)
}
```

Keep credentials and refresh tokens out of renderable snapshots. The state machine should define what logout, token refresh failure, account switching, and keychain unavailability do to in-memory and persisted state.

Authentication proves who the current principal is according to one mechanism. It does not prove every operation is authorized.

## Authorization Capabilities Are Scoped Proofs

A capability value can remove call-site booleans and bind authority to a subject and operation:

```swift
struct DeleteAccountCapability: Sendable {
    fileprivate let accountID: AccountID
    fileprivate let authorizationRevision: Int
}
```

A useful capability records enough context to prevent confused-deputy mistakes:

- Principal/session.
- Resource ID.
- Permitted operation.
- Issuer/environment.
- Expiration, policy revision, or nonce when relevant.

A freely constructible public type or marker-protocol conformance is not a capability.

A value is normally a point-in-time proof. When permission is revocable, rapidly changing, or must be atomic with mutation, keep the final authorization check and operation in one trusted actor/service or on the server.

Do not serialize a local capability unless the protocol explicitly defines replay, integrity, audience, expiry, and revocation semantics.

## Secrets Need Controlled Exposure, Not Magical Wrappers

A `Secret<Value>` wrapper can make accidental logging or display harder by withholding public access and descriptive conformances. It cannot guarantee:

- Zeroization of arbitrary Swift values.
- Elimination of copies already made by `String`, `Data`, ARC, bridging, or the optimizer.
- Exclusion from crash dumps, debugger memory, screenshots, or third-party telemetry.
- Secure persistence.

Prefer closure-scoped access as a narrow API surface and a guard against accidental reads:

```swift
struct Secret<Value> {
    private let value: Value

    init(_ value: consuming Value) {
        self.value = value
    }

    borrowing func withValue<Result>(
        _ body: (borrowing Value) throws -> Result
    ) rethrows -> Result {
        try body(value)
    }
}
```

This is API friction, not a static nonescape proof. A copyable `Value` can still be returned from the closure, assigned to captured storage, bridged, or copied by a callee. When exposure must be mechanically constrained, expose only fixed domain operations or use a compiler-checked noncopyable/nonescapable design whose lifetime relationship has been validated. Even then, audit foreign calls and hidden copies.

Audit `CustomStringConvertible`, `CustomDebugStringConvertible`, `Codable`, `Hashable`, reflection, interpolation, and error descriptions. Do not make a secret hashable merely for convenient storage; hashes can disclose equality and may outlive the secret.

Use Keychain or the appropriate protected storage. Model accessibility, synchronizability, access group, biometric policy, and missing/locked-device behavior explicitly in the storage adapter.

## Classify Sensitive Data at the Logging Boundary

Use typed event payloads and one redacting adapter rather than allowing arbitrary dictionaries.

```swift
enum LogField<Value: Sendable>: Sendable {
    case publicValue(Value)
    case privateValue(Value)
    case sensitiveValue(Value)
}
```

The exact design may use OSLog privacy annotations directly, but classification must survive conversion into the logging backend.

Distinguish:

- Public operational metadata.
- Private user data.
- Credentials/secrets that should not be logged at all.
- Stable identifiers that become PII when correlated.

Redaction is context-specific. A value safe for local debug output may still be prohibited in analytics, remote logs, crash reports, or notification payloads.

## Trust Types Are Interpreter-Specific

“Sanitized string” is too broad. HTML text, HTML attributes, URLs, JavaScript, SQL, shell arguments, regular expressions, and log formats have different grammars.

Prefer APIs that avoid constructing executable text:

- SQL bind parameters instead of escaped SQL fragments.
- `Process` executable plus argument array instead of a shell command string.
- `URLComponents`/`URLQueryItem` instead of manual query concatenation.
- Framework HTML/text nodes rather than raw markup where available.
- Regex builders or escaped literal constructors rather than string interpolation.

If a trust-state wrapper is useful, name the exact sink context:

```swift
struct HTMLTextEscaped: Sendable { /* controlled construction */ }
struct URLQueryComponent: Sendable { /* controlled construction */ }
```

Do not allow implicit conversion among contexts. Encoding a string for a URL query does not make it safe as a host, path, header, HTML attribute, or shell argument.

## URLs Need Semantic Validation

`URL` proves that Foundation formed a URL value, not that the URL is allowed or points where expected.

For security-sensitive URLs, validate after parsing:

- Scheme allowlist.
- Presence and exact canonical host policy.
- Port policy.
- User/password components.
- Path shape and normalization policy.
- Query keys and multiplicity.
- Fragment policy.
- Whether relative URLs are allowed and against which trusted base.

Avoid prefix checks such as `absoluteString.hasPrefix("https://example.com")`; they are vulnerable to user-info, subdomain, escaping, and normalization confusion.

Use `URLComponents` for structured construction, but do not call it authorization. Percent encoding is component-specific, and a successfully constructed component may still violate business/security policy.

For universal links and redirects, preserve the original parsed components until policy checks complete. Decide how internationalized host names, trailing dots, default ports, and case normalization are handled by the selected Foundation/Networking APIs and backend.

## File Paths Are Not Just Strings

Use `URL` with `isFileURL` and a domain wrapper that records the intended root or role:

```swift
struct CacheFileURL: Sendable {
    let value: URL
}
```

Construction must still verify policy. Lexical standardization does not resolve every symlink, mount, race, or case-sensitivity issue.

For paths derived from untrusted input:

- Reject absolute paths when only relative names are allowed.
- Reject or normalize `..` according to a written policy.
- Validate path components, not string prefixes.
- Resolve against a trusted root.
- Consider symlinks and aliases.
- Avoid checking one path and later opening a different resolution of it.
- Prefer APIs that open or create relative to an already trusted directory handle when the platform/API permits.

A “check then use” sequence can have a time-of-check/time-of-use race. For adversarial filesystem access, operate on opened descriptors/handles and verify metadata on the object actually opened.

## Security-Scoped URLs and Bookmarks

Sandbox extension access is a resource lifetime:

```text
resolve bookmark
  -> validate staleness and intended location
  -> startAccessingSecurityScopedResource
  -> perform scoped work
  -> stopAccessingSecurityScopedResource
```

Inspect the Boolean returned by `startAccessingSecurityScopedResource()`. When it returns `true`, call `stopAccessingSecurityScopedResource()` as soon as the scoped work finishes, including throw and cancellation paths. Do not infer from a `false` result alone that the URL is unusable; the resource may already be directly accessible, so the surrounding operation still needs an explicit error policy. A stored URL does not prove the process currently has permission. Bookmark data can become stale and should be treated as untrusted persisted input.

Prefer a closure-scoped accessor that starts and stops access around the operation. This centralizes balancing but does not statically stop a copyable `URL` from being returned or captured; an escaped URL still does not carry active sandbox authority after access stops. Prefer fixed file operations inside the accessor, and do not expose a security-scoped URL as a timeless capability to arbitrary feature code.

## Native and File Handles Need One Ownership Story

For every handle, document:

- Owned, borrowed, shared, or transferred.
- Nullable or sentinel invalid values.
- Which function closes/releases it.
- Whether close can fail.
- Thread affinity and synchronization.
- Callback lifetime.
- Whether duplication is legal.
- Behavior on cancellation and process suspension.

A noncopyable wrapper is appropriate when duplicate ownership would double-close, but it does not implement cleanup automatically. A copyable reference wrapper may be correct for shared ownership if refcounting and close semantics are explicit.

A closure can centralize acquisition and cleanup when static noncopyable ownership is unnecessary or would overcomplicate the API:

```swift
func withOpenFile<Result>(
    at url: URL,
    _ body: (FileHandle) throws -> Result
) throws -> Result {
    let handle = try FileHandle(forReadingFrom: url)
    defer { try? handle.close() }
    return try body(handle)
}
```

Real code must decide whether close errors may be ignored; the example shows runtime-scoped cleanup, not a universal error policy or a static lifetime proof. `FileHandle` is a copyable reference, so the closure can return or capture it; the wrapper will still close it on exit, leaving any escaped reference closed but present. When escape must be impossible, keep the handle private behind fixed domain operations or use a verified noncopyable/nonescapable borrowing API. Async cleanup cannot be guaranteed by a synchronous destructor.

## Cryptographic State Must Encode Protocol Facts

Do not invent cryptography to obtain nicer types. Use platform or vetted libraries and model their protocol-level requirements.

Potential distinctions include:

- Signing key versus verification key.
- Encryption key versus key-encryption key.
- Plaintext versus authenticated ciphertext.
- Nonce generated but unused versus consumed.
- Algorithm/suite identifier.
- Key version and rotation epoch.
- Associated data schema.
- Unverified versus verified payload.

A wrapper can prevent calling decrypt on plaintext bytes or verify with a signing-only API. It cannot prove nonce uniqueness across crashes/devices unless generation and persistence enforce it.

Avoid exposing raw key bytes unless interoperability requires it. When export is necessary, make the operation explicit, scoped, auditable, and unavailable for nonextractable keys.

Never make algorithm choice an unconstrained user string. Use a closed set owned by the protocol implementation, while preserving unknown wire identifiers at the decoding boundary when forward compatibility requires it.

## Verification Is a Transition

Keep unverified data distinct from verified claims:

```swift
struct UnverifiedToken: Sendable { let compact: String }
struct VerifiedClaims: Sendable { /* parsed, verified claims */ }

protocol TokenVerifier: Sendable {
    func verify(_ token: UnverifiedToken) async throws -> VerifiedClaims
}
```

The transition must include every relevant check: signature/MAC, algorithm allowlist, issuer, audience, expiry, not-before, key selection, and replay policy as required by the protocol.

Parsing a token is not verification. Decoding a certificate is not trust evaluation. A successful TLS connection does not automatically authorize application-level data.

## Randomness and Nonces

Model whether a value requires unpredictability, uniqueness, or only collision resistance; these are different properties.

Do not use `UUID`, timestamps, counters, or general-purpose pseudo-random APIs as cryptographic randomness without a protocol-specific argument. Use system cryptographic random generation or the cryptographic library's nonce/key APIs.

A type named `Nonce` does not prove uniqueness. The issuer/storage protocol must prevent reuse where reuse is catastrophic.

## Sensitive Conformances and Bridging

Audit automatic conformances:

- `Codable` may persist or transmit a value unexpectedly.
- `Hashable` and `Equatable` expose equality relationships and may have timing implications in specialized protocols.
- `CustomStringConvertible` and reflection can leak contents.
- Objective-C bridging can copy into `NSString`, `NSData`, collections, KVC, or logs.
- `NSCopying` is incompatible with logically unique resources unless it duplicates safely.
- `NSSecureCoding` is input validation, not authorization.

Keep foreign-language façades separate from the strongest Swift type when Objective-C or C cannot express its ownership or construction rules.

## Strict Memory Safety as an Audit Tool

Current Swift's opt-in strict memory safety checking identifies unsafe constructs and APIs. It does not prove that every marked `unsafe` expression is correct.

For modules that handle untrusted bytes, cryptography, codecs, or C interop:

- Enable `-strict-memory-safety` in a dedicated CI lane.
- Treat warnings in the `StrictMemorySafety` group as audit inventory.
- Keep `unsafe` expressions small and adjacent to written preconditions.
- Prefer safe wrappers with narrow signatures.
- Avoid `-Ounchecked`, disabled exclusivity, or incomplete concurrency checking in security-sensitive release builds.
- Use `#if hasFeature(StrictMemorySafety)` only for source adaptation, not to weaken semantics.

Review every unsafe boundary for lifetime, bounds, type, initialization, and thread safety.

## Security Review Questions

- What attacker or misuse class is this type intended to stop?
- Which checks remain dynamic or remote?
- Can a client forge, serialize, replay, copy, or retain the proof?
- Does authority expire or revoke between construction and use?
- Is sensitive data exposed through description, coding, hashing, bridging, analytics, or errors?
- Is text safe for one exact interpreter context only?
- Are URL scheme, host, port, path, query, and redirect policies explicit?
- Can symlinks or TOCTOU defeat a path check?
- Is resource access scoped and cleanup complete on throws/cancellation?
- Are cryptographic algorithm, nonce, key version, verification, and replay states modeled where they matter?
- Are unsafe operations centralized and checked under strict memory safety?
- Does the server or operating system remain the authoritative enforcement point?
