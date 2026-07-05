# Structured Value Mapping and Future ValueRepresentation

## Availability correction

In the iPhoneOS 26.5 SDK verified on 2026-07-03:

- `IntentPerson` exists in `AppIntents` and is available since iOS 16.
- `PlaceDescriptor` exists in `GeoToolbox` and is present in the iOS 26 SDK, with `_GeoToolbox_AppIntents` overlay support.
- `ValueRepresentation` and `IntentValueRepresentation` are absent.

That split matters. The structured value types are real and useful today. The transfer-representation plumbing described in iOS 27-era material is not available to source compiled with iPhoneOS 26.5.

Do not write production code that references `ValueRepresentation` or `IntentValueRepresentation` unless the selected SDK declares those symbols. A runtime `#available` check cannot fix a missing compile-time declaration.

## Mental model

Your app entity is private app identity. A structured system value is a shape another app or system action already understands. A transfer representation is the bridge that lets the system carry your entity as that value.

For iOS 26.5-compatible code, implement the first two parts now:

```text
LandmarkEntity
  → pure mapper
  → PlaceDescriptor
```

```text
ContactEntity
  → pure mapper
  → IntentPerson
```

When a selected SDK later provides `ValueRepresentation` / `IntentValueRepresentation`, the adoption should be a thin wrapper around the mapper:

```text
Transferable.transferRepresentation
  → future ValueRepresentation wrapper
  → existing mapper
```

Do not put this logic in UIKit view controllers, SwiftUI views, snippets, drag delegates, or share-sheet adapters. It belongs beside the entity/value layer.

## What structured values solve

Use structured value mapping when your entity can be expressed as a system-known semantic value that is not naturally a file or byte payload:

- A place, store, trailhead, landmark, venue, pickup point, or destination as `PlaceDescriptor`.
- A contact, team member, sender, attendee, author, or assignee as `IntentPerson`.

A fake coordinate JSON file is not equivalent to a `PlaceDescriptor`. A display name string is not equivalent to an `IntentPerson`. `DisplayRepresentation` is also not enough; it helps the system speak and show your entity, but it is not a cross-app value shape.

## iOS 26.5-compatible place mapper

Keep the mapper pure, synchronous or cheaply async, and independent of UI. Verify initializer labels and supported fields against the selected `GeoToolbox` SDK.

```swift
import GeoToolbox

extension LandmarkEntity {
    var systemPlaceDescriptor: PlaceDescriptor {
        // Pseudocode: use the exact initializer labels from the selected SDK.
        fatalError("Use the PlaceDescriptor initializer from the selected GeoToolbox SDK.")
    }
}
```

Design rules:

- Prefer precise but privacy-appropriate coordinates.
- Include a human-readable name when available.
- Include address components only if the user can see/disclose them.
- Avoid exporting internal place IDs from your service as if another app could resolve them.
- Do not synthesize misleading coordinates for approximate places.

## iOS 26.5-compatible person mapper

`IntentPerson` is available since iOS 16. Use it for participant-like values today. Verify initializer labels against the selected `AppIntents` SDK.

```swift
import AppIntents

extension TeamMemberEntity {
    var systemPerson: IntentPerson {
        // Pseudocode: use the exact initializer labels from the selected SDK.
        fatalError("Use the IntentPerson initializer from the selected AppIntents SDK.")
    }
}
```

Design rules:

- Do not disclose hidden email addresses, phone numbers, handles, or directory IDs.
- Keep account/workspace boundaries intact.
- Use `IntentPerson` for people-like values, not for arbitrary named resources.
- Preserve ambiguity when two people share the same display name; do not guess silently.

## Future transfer wrapper shape

The following illustrates the intended future shape only. It is not buildable with the iPhoneOS 26.5 SDK because `ValueRepresentation` is absent.

```swift
// Forward-looking / selected-SDK-gated; not buildable with iPhoneOS 26.5.
import AppIntents
import CoreTransferable
import GeoToolbox

extension LandmarkEntity: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        ValueRepresentation(exporting: \.systemPlaceDescriptor)

        DataRepresentation(exportedContentType: .plainText) { landmark in
            Data(landmark.name.utf8)
        }
    }
}
```

When a selected SDK declares an explicit bidirectional API such as `IntentValueRepresentation`, use importing only when incoming content should create or update an entity in your app. If incoming content should match an existing entity, prefer `IntentValueQuery`.

## Import vs query decision

Use `IntentValueQuery` when the system has semantic input and the app should resolve it to existing app entities. `IntentValueQuery` is present in the iPhoneOS 26.5 SDK. `SemanticContentDescriptor` comes from `VisualIntelligence`.

```swift
import AppIntents
import VisualIntelligence

@UnionValue
enum ExistingContentMatch {
    case landmark(LandmarkEntity)
    case collection(LandmarkCollectionEntity)
}

struct LandmarkValueQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [ExistingContentMatch] {
        guard let pixelBuffer = input.pixelBuffer else { return [] }
        return try await LandmarkIndex.shared.matches(pixelBuffer).prefix(10).map { .landmark($0) }
    }
}
```

Use a future import representation only when the app should accept a system value and create a new entity:

```text
Incoming PlaceDescriptor
  → create a saved place / trip stop / delivery address in this app
```

Do not import when the correct behavior is lookup:

```text
Incoming image/text/location
  → find an existing LandmarkEntity
```

## Onscreen awareness plus structured value mapping

The current shipping chain for “get directions to this landmark” should be designed like this:

```text
Visible screen
  → NSUserActivity.appEntityIdentifier
  → LandmarkEntity.ID
  → LandmarkEntityQuery.entities(for:)
  → LandmarkEntity
  → systemPlaceDescriptor mapper
  → future transfer wrapper when selected SDK supports it
```

The first four steps are buildable in iPhoneOS 26.5. The final transfer wrapper is selected-SDK-gated.

UIKit example for the buildable part:

```swift
let activity = NSUserActivity(activityType: "com.example.landmark.view")
activity.title = "Viewing \(landmark.name)"
activity.appEntityIdentifier = EntityIdentifier(
    for: LandmarkEntity.self,
    identifier: landmark.id
)
viewController.userActivity = activity
activity.becomeCurrent()
```

## UIKit guidance

UIKit does not change the representation model.

- Publish the primary onscreen entity with `NSUserActivity.appEntityIdentifier`.
- Route opens/actions through `UISceneAppIntent` or `AppIntentSceneDelegate`.
- Keep structured value mappers in the entity/value layer.
- Share export services between App Intents, drag/drop, and share sheets where appropriate.
- Do not build `PlaceDescriptor` or `IntentPerson` in a cell, view controller, or context-menu delegate.

## Decision tree

```text
Can another system/app use a known file or data format?
  → Add DataRepresentation or FileRepresentation.

Can the entity map to a system-known structured value shipping in this SDK?
  → Add a pure mapper, e.g. PlaceDescriptor or IntentPerson.

Does the selected SDK declare ValueRepresentation / IntentValueRepresentation?
  → Add a thin Transferable wrapper around the mapper.

Does the selected SDK lack those transfer APIs?
  → Keep the mapper and file/data representations; do not reference absent symbols.

Should incoming content match an existing entity?
  → Use IntentValueQuery.

Should incoming content create a new entity?
  → Use a future import representation only if the selected SDK declares it.
```

## Validation checklist

- [ ] The app compiles against the selected SDK without referencing absent symbols.
- [ ] `IntentPerson` and `PlaceDescriptor` initializer labels are verified in the selected SDK.
- [ ] Structured value mappers are pure, testable, and UI-independent.
- [ ] `Transferable` file/data representations re-check authorization at export time.
- [ ] Future `ValueRepresentation` / `IntentValueRepresentation` code is isolated from 26.5-compiled targets.
- [ ] `NSUserActivity.appEntityIdentifier` resolves through the entity query after app relaunch.
- [ ] Precision and privacy of exported location/person data are intentionally bounded.

## Anti-patterns

- Treating `ValueRepresentation` as available in iPhoneOS 26.5.
- Treating `PlaceDescriptor` or `IntentPerson` as unavailable merely because the transfer wrappers are absent.
- Using fake JSON files for places or contacts when a system-known value type exists.
- Exporting another app’s private IDs.
- Assuming `DisplayRepresentation` or `@Property` is enough to pass structured content to another app.
- Compiling iOS 27-era symbols into an iOS 26.5 SDK deployment path without source isolation.
- Building structured values in UIKit/SwiftUI view code instead of the entity/value layer.

## Agent instruction

When asked to add structured cross-app transfer:

1. Verify the selected SDK for `ValueRepresentation`, `IntentValueRepresentation`, `PlaceDescriptor`, and `IntentPerson`.
2. If only the value types exist, create pure mappers and tests, then stop before referencing absent transfer wrappers.
3. If transfer wrappers exist, add them beside the entity’s `Transferable` conformance.
4. Explain the build split in generated code comments so future maintainers do not mistake SDK absence for a design decision.
