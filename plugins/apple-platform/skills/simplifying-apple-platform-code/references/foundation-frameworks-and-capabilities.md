# Foundation Frameworks and Capabilities

Preserve Foundation, networking, persistence, framework-specific, localization, accessibility, and design-system behavior when simplifying Apple SDK usage.

## Foundation, Data, Networking, and Persistence

### Formatting, Localization, and Calendrical Logic

- Use project formatting/localization wrappers when present.
- Prefer `URLComponents`, `URLQueryItem`, `URL`, and platform path APIs over string concatenation for URLs and paths.
- Preserve `Locale`, `Calendar`, `TimeZone`, numbering system, capitalization, measurement units, currency, pluralization, and grammar behavior.
- Be careful when caching formatters. Mutable `Formatter` subclasses and shared instances need thread/actor safety; value-style formatters may be safer when available and compatible.
- Preserve date parsing strategies, fractional seconds, timezone assumptions, default dates, server/client clock behavior, and user-visible formatting.

### Encoding, Decoding, and Models

- Preserve `CodingKeys`, optionality, default values, lossy decoding, unknown case handling, unknown-field tolerance, snake/camel-case strategies, date/data strategies, and backwards/forwards compatibility.
- Do not simplify models by removing seemingly unused fields that are required for decoding, persistence, analytics, debugging, equality, hashing, or future migrations.
- Preserve identity semantics for models used in SwiftUI, diffable data sources, caches, persistence, and network updates.

### Networking

- Preserve request construction, query encoding, headers, auth, content type, caching policy, timeout, retry policy, cancellation, redirect behavior, status-code handling, error mapping, rate limits, and background-session behavior.
- Do not log secrets, tokens, cookies, personal data, or full request/response bodies unless the project has a redaction policy.
- Prefer project clients and endpoint abstractions over local `URLSession` calls if the project has them.
- Preserve offline behavior, cache invalidation, pagination, ETags, idempotency keys, and duplicate-request suppression.

### Persistence

- Preserve migrations, schema versions, model identifiers, store locations, app-group containers, encryption, backups/exclusions, conflict policy, and data-retention behavior.
- For Core Data, preserve context confinement, merge policy, parent/child context behavior, batch operation side effects, faulting, fetch predicates, sort descriptors, fetch limits, relationship delete rules, and persistent history behavior.
- For SwiftData, verify deployment availability and model/migration implications before replacing Core Data or custom persistence. Do not use it in code paths that must run on unsupported OS versions without guards.
- For `UserDefaults`, preserve keys, suites, registration defaults, migration, reset behavior, and app-extension sharing.
- For Keychain and secure storage, use existing wrappers and preserve access groups, accessibility class, synchronizable behavior, and migration.
- For files, preserve atomic writes, file protection, coordination, security-scoped resource access, sandbox/container paths, temporary-file cleanup, and backup behavior.

## Apple Framework and Capability Pitfalls

When touched code uses these areas, apply extra caution:

- **App extensions/widgets/intents:** preserve extension-safe APIs, timeline reload policy, shared containers, privacy, performance budgets, and process lifetime assumptions.
- **StoreKit/subscriptions:** preserve transaction verification, entitlement refresh, restore behavior, product identifiers, subscription group logic, server notification assumptions, and idempotency.
- **Notifications/background work:** preserve authorization state, scheduling identifiers, background modes, expiration handlers, task identifiers, and main-thread handoff.
- **Location/Bluetooth/Health/Photos/Camera/Microphone/Contacts/Calendars:** preserve permissions, purpose strings, privacy prompts, background behavior, delegate lifetime, and restricted/denied states.
- **AVFoundation/media:** preserve session configuration ordering, interruption handling, audio session categories, thread usage, permissions, and cleanup.
- **CloudKit/iCloud:** preserve container identifiers, zones, subscriptions, conflict handling, account status, retries, and offline behavior.
- **MapKit/CoreLocation:** preserve authorization, accuracy, region monitoring limits, background modes, and user-location privacy.
- **SF Symbols/assets/colors/fonts:** verify symbol and asset availability across deployment targets; preserve rendering mode, dynamic color behavior, contrast, high contrast, and variable color semantics.
- **Entitlements/privacy manifests:** treat them as behavioral/security configuration. Do not remove or alter them as cleanup without a concrete reason.

## Localization, Accessibility, and Design System

Apple UI cleanup should actively protect user-visible behavior:

- Preserve localized keys and extraction behavior. Do not change keys casually; key changes can break translations.
- Preserve pluralization, formatted interpolation, grammatical agreement, bundle/table selection, comments for translators, and string-catalog compatibility.
- Prefer project text, spacing, color, typography, icon, haptics, animation, and component tokens over literal values.
- Preserve accessibility identifiers used by UI tests.
- Preserve VoiceOver order, grouping, headings, traits, values, actions, adjustable controls, focus restoration, Switch Control behavior, Dynamic Type, reduced motion, differentiate-without-color, high contrast, and content size categories.
- Do not simplify colors, images, labels, or gestures in a way that makes state available only by color, motion, or visual layout.
