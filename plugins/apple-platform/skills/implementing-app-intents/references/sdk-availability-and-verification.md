# SDK Availability and Verification

Treat this file as the local ground-truth layer for the package. The verified facts below came from the iPhoneOS 26.5 SDK Swift interfaces from Xcode 26.5, checked on 2026-07-03. Future beta or GA SDKs may add, remove, rename, or move declarations. Always verify against the SDK selected by the project before generating load-bearing code.

## Verified iPhoneOS 26.5 SDK availability

| Symbol or family | Status in iPhoneOS 26.5 SDK | Declaring module / location |
| --- | --- | --- |
| `AppIntent`, `AppEntity`, `AppShortcutsProvider`, `EntityQuery` family | iOS 16.0 | `AppIntents` |
| `IntentPerson` | iOS 16.0 | `AppIntents` |
| `PredictableIntent` | iOS 16.0 | `AppIntents` |
| `AppIntentsPackage` | iOS 17.0 | `AppIntents` |
| `ProgressReportingIntent` | iOS 17.0 | `AppIntents` |
| `DeprecatedAppIntent`, `IntentDeprecation` | iOS 17.0 | `AppIntents` |
| `IndexedEntity` | iOS 18.0 | `AppIntents` |
| `AppEntityAnnotatable`, `NSUserActivity.appEntityIdentifier` | iOS 18.2 | `AppIntents` |
| `SnippetIntent`, `ShowInAppSearchResultsIntent`, `IntentValueQuery`, `@UnionValue`, `UndoableIntent`, `ForegroundContinuableIntent`, `TargetContentProvidingIntent`, SwiftUI `onAppIntentExecution`, view-based `requestConfirmation` / `requestChoice` | Present in the iPhoneOS 26.5 SDK or earlier | `AppIntents` / `_AppIntents_SwiftUI` as applicable |
| `UISceneAppIntent`, `AppIntentSceneDelegate`, `SiriTipUIView`, `ShortcutsUIButton` | Present in iOS 26 SDK | `_AppIntents_UIKit` cross-import overlay; available when `UIKit` and `AppIntents` are imported |
| `SemanticContentDescriptor` | Present in iOS 26 SDK | `VisualIntelligence`, not `AppIntents` |
| `PlaceDescriptor` | Present in iOS 26 SDK | `GeoToolbox` plus `_GeoToolbox_AppIntents` overlay |

## Absent from the iPhoneOS 26.5 SDK

Do not generate code using these symbols for a project compiling with the iPhoneOS 26.5 SDK. A runtime `#available` check is not enough when the compiler cannot see the declaration.

- `ValueRepresentation`
- `IntentValueRepresentation`
- `RelevantEntities`
- AppIntents `EntityCollection` — ignore unrelated RealityKit search hits with the same name.
- `SyncableEntity`
- `SyncableEntityIdentifier`
- `LongRunningIntent`
- `ExecutionTargets`
- `CancellableIntent`
- `AppIntentsTesting`
- `UITableViewAppIntentsDataSource`
- `UICollectionViewAppIntentsDataSource`
- `AppEntityUIElement`
- `UIView.appEntityUIElementProvider`
- SwiftUI per-view `.appEntityIdentifier(...)`
- SwiftUI `.appEntityIdentifier(forSelectionType:)`
- Notification-content `appEntityIdentifiers`

When discussing these APIs, mark them as forward-looking / selected-SDK-dependent. Keep examples quarantined in documentation or in files compiled only by an SDK that actually declares the symbol.

## Assistant Schemas domains verified in iPhoneOS 26.5

The verified schema-domain set is:

```text
journal, photos, visualIntelligence, reader, system, wordProcessor,
presentation, spreadsheet, browser, files, camera, mail, whiteboard, books
```

Do not describe `messages`, `calendar`, `tasks`, `audio/media`, or `clock/alarm/timer` as shipping App Schema domains for iPhoneOS 26.5. Apps in those product categories can still expose strong custom entities/intents, use verified domains where they fit, use `IntentPerson` for people, use `IndexedEntity`, donate interactions, and support system search/open flows.

## Important split: structured value types vs transfer representations

`IntentPerson` and `PlaceDescriptor` are buildable value types in the iPhoneOS 26.5 SDK. The transfer-representation APIs previously described as `ValueRepresentation` / `IntentValueRepresentation` are not present in that SDK.

For iOS 26.5-compatible code, write and test pure mapping helpers now:

```swift
import AppIntents
import GeoToolbox

extension LandmarkEntity {
    var systemPlaceDescriptor: PlaceDescriptor {
        // Use the initializer labels from the selected GeoToolbox SDK.
        // Keep this conversion pure and UI-independent.
        fatalError("Use the PlaceDescriptor initializer from the selected GeoToolbox SDK.")
    }
}

extension ContactEntity {
    var systemPerson: IntentPerson {
        // Use the initializer accepted by the selected AppIntents SDK.
        fatalError("Use the IntentPerson initializer from the selected AppIntents SDK.")
    }
}
```

When a future or beta SDK declares the structured transfer representation API, the adoption should be a thin wrapper around these existing mappers rather than new business logic inside a view controller.

## Verify against the selected SDK

Use the project’s selected SDK, not memory, this package, a blog post, or a beta session transcript.

```bash
SDK=$(xcrun --sdk iphoneos --show-sdk-path)

# Which frameworks declare a symbol:
find "$SDK/System/Library/Frameworks" -name "arm64e-apple-ios.swiftinterface" \
  | xargs grep -l -w "SymbolName"

# Its @available annotation, when the declaration is in AppIntents:
grep -B4 "public protocol SymbolName" \
  "$SDK/System/Library/Frameworks/AppIntents.framework/Modules/AppIntents.swiftmodule/arm64e-apple-ios.swiftinterface"

# Assistant Schemas domains in this SDK:
grep -o -E "public static var [a-zA-Z]+: some AppIntents\.AssistantSchemas\.[A-Za-z]+" \
  "$SDK/System/Library/Frameworks/AppIntents.framework/Modules/AppIntents.swiftmodule/arm64e-apple-ios.swiftinterface" | sort -u
```

Verification caveats:

- Cross-import overlays hold framework-pairing APIs. Check `_AppIntents_UIKit`, `_AppIntents_SwiftUI`, and overlays such as `_GeoToolbox_AppIntents`, not only `AppIntents.framework`.
- Name collisions exist. `EntityCollection` search hits may refer to RealityKit, not AppIntents.
- Absence from the current GA SDK does not prove absence from a beta SDK. Audit the SDK actually selected by the Xcode project.
- Runtime availability and compile-time visibility are different. If a symbol is absent from the selected SDK, `@available` cannot make source code using that symbol compile.
