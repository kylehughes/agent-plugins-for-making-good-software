# ValueRepresentation and Structured Cross-App Transfer

`ValueRepresentation` is the iOS 27-era bridge between your private app entity and a system-understood structured value. Use it when your entity can be represented as a semantic value that another app or Siri already understands, but that value is not naturally a file, image, PDF, plain text, or other `UTType` payload.

The canonical example is a place. A travel app may have a `LandmarkEntity`. Mail can receive that landmark as text, an image, or a PDF through ordinary `Transferable` data/file representations. Maps, however, needs structured navigation input: a coordinate, address, or place descriptor. A coordinate plus common name does not have to become a fake file. Export the landmark as a system place value, such as `PlaceDescriptor` from `GeoToolbox`, using `ValueRepresentation` inside the entity’s `Transferable` conformance.

## Mental model

`Transferable` is the transport surface. Each representation says, “Here is another way the system may carry this entity.”

Use these representations together:

| Representation | Carries | Use when |
| --- | --- | --- |
| `DataRepresentation` | Bytes with a known content type | Plain text, JSON, RTF, images, small custom payloads. |
| `FileRepresentation` | A file URL with a known content type | PDF, movie, large image, archive, document export. |
| `IntentValueRepresentation` | A system intent value | Bidirectional conversion between your entity and a system-known intent value such as `IntentPerson` or `PlaceDescriptor`. |
| `ValueRepresentation` | Convenience spelling for entity value transfer | Entity can be exported as a system-understood structured value, commonly shown in Apple examples with `PlaceDescriptor`. |

`DisplayRepresentation` is not a transfer representation. It controls how the entity appears to the user. It does not give Maps a coordinate, Phone a person, or another app a usable structured value.

`@Property` is also not sufficient by itself. Properties help Siri reason about, search, filter, and speak about an entity. A receiving app still needs a value shape it understands. If the receiving system action expects `PlaceDescriptor`, `IntentPerson`, or another supported system value, expose that exact shape through a value representation.

## When to use it

Add a value representation when all of the following are true:

1. The source object is an app entity or transferable domain object.
2. The user may reasonably ask Siri to use “this” or “that” object in another app.
3. A system-known structured value accurately represents the object.
4. A data/file representation would be lossy, fake, or unusable by the destination action.
5. The app can export the value without leaking private, hidden, account-scoped, or stale information.

Good candidates:

- A place, store, trailhead, landmark, venue, pickup point, or destination exported as `PlaceDescriptor`.
- A contact-like entity exported as `IntentPerson`.
- A meeting participant, message recipient, or author exported as a person value when that is semantically accurate.
- Any app entity that conforms to a schema and also has a system value shape that another app action expects.

Poor candidates:

- Arbitrary JSON blobs.
- Private database rows with no system value equivalent.
- Another app’s private identifier, such as an Apple Music ID embedded in your own album entity.
- A URL used only because there is no better value; URLs are fine when the URL is truly the content, not when it is a workaround for missing semantic shape.
- A screenshot of visible content when the destination needs structured data.

## Place export example

Use this shape when a landmark/place entity should work with Maps or other mapping actions.

```swift
import AppIntents
import CoreLocation
import CoreTransferable
import GeoToolbox
import UniformTypeIdentifiers

struct LandmarkEntity: AppEntity, Transferable, Sendable, Identifiable {
    static let defaultQuery = LandmarkQuery()

    let id: Int
    let name: String
    let coordinate: CLLocationCoordinate2D
    let summary: String?

    static var typeDisplayRepresentation: TypeDisplayRepresentation {
        "Landmark"
    }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            subtitle: summary.map { "\($0)" },
            image: .init(systemName: "mappin.and.ellipse")
        )
    }

    static var transferRepresentation: some TransferRepresentation {
        // Structured value for Maps / navigation / Siri cross-app workflows.
        ValueRepresentation(exporting: { landmark in
            PlaceDescriptor(
                representations: [.coordinate(landmark.coordinate)],
                commonName: landmark.name
            )
        })

        // Broad compatibility for text destinations such as Mail or Messages.
        DataRepresentation(exportedContentType: .plainText) { landmark in
            let text = landmark.summary.map { "\(landmark.name)\n\($0)" } ?? landmark.name
            return Data(text.utf8)
        }

        // High-fidelity export when the receiving destination wants a document/file.
        FileRepresentation(exportedContentType: .pdf) { landmark in
            let url = try await LandmarkExporter.shared.pdf(for: landmark.id)
            return SentTransferredFile(url)
        }
    }
}
```

Use the exact initializer labels accepted by the active SDK. Apple’s WWDC sample shows `ValueRepresentation(exporting: { ... })`; prefer that spelling unless the active SDK documents another shorthand.

## Key-path export when the entity already stores the system value

If the entity already exposes the system-known value as a property, prefer the key-path form. This keeps export code declarative and reduces divergence between the entity’s properties and transfer representation.

```swift
import AppIntents
import CoreTransferable
import GeoToolbox

struct LandmarkEntity: AppEntity, Transferable, Sendable, Identifiable {
    static let defaultQuery = LandmarkQuery()

    let id: Int

    @Property(title: "Name")
    var name: String

    @Property(title: "Place")
    var placeDescriptor: PlaceDescriptor

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(
            title: "\(name)",
            image: .init(systemName: "mappin.and.ellipse")
        )
    }

    static var transferRepresentation: some TransferRepresentation {
        ValueRepresentation(exporting: \.placeDescriptor)
    }
}
```

Do not duplicate coordinate/address/name mapping in multiple places. Prefer a single domain mapper:

```swift
enum PlaceMapping {
    static func descriptor(for landmark: Landmark) -> PlaceDescriptor {
        PlaceDescriptor(
            representations: [.coordinate(landmark.coordinate)],
            commonName: landmark.name
        )
    }
}
```

Then use the same mapper for entity properties, transfer export, search result previews, and tests.

## Contact export and import example

`IntentValueRepresentation` is the explicit name Apple shows for bidirectional conversion between an app entity and a system intent value. Use importing when incoming content should create a new entity in your app.

```swift
import AppIntents
import CoreTransferable

struct ContactEntity: AppEntity, Transferable, Sendable, Identifiable {
    static let defaultQuery = ContactQuery()

    let id: UUID

    @Property(title: "Person")
    var person: IntentPerson

    static var typeDisplayRepresentation: TypeDisplayRepresentation { "Contact" }

    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(person.displayName)")
    }

    static var transferRepresentation: some TransferRepresentation {
        IntentValueRepresentation(exporting: \.person, importing: { incomingPerson in
            let contact = try await ContactImporter.shared.createContact(from: incomingPerson)
            return contact.entity
        })
    }
}
```

Use an import closure when the incoming value is new content. Use `IntentValueQuery` when the incoming value should resolve to an existing entity.

## Resolving incoming values to existing entities

If another app hands your intent a system value, decide whether it refers to an existing entity before creating anything.

```swift
import AppIntents

struct ContactQuery: EntityQuery, IntentValueQuery {
    func entities(for identifiers: [ContactEntity.ID]) async throws -> [ContactEntity] {
        try await ContactStore.shared.entities(for: identifiers)
    }

    func values(for input: [IntentPerson]) async throws -> [ContactEntity] {
        try await ContactStore.shared.contacts(matching: input).map(\.entity)
    }
}
```

Use this for commands like “message this person in my app” when “this person” may already exist in your database. Use import only when creating a new app object is the intended behavior.

## Onscreen awareness plus value transfer

Cross-app Siri workflows usually need both context and transfer.

1. Annotate the visible object so Siri can resolve “this landmark.”
2. Ensure the resolved entity has a query and stable ID.
3. Add `Transferable` representations.
4. Add `ValueRepresentation` for the system value the destination app needs.
5. Test the full chain through Siri/Shortcuts, not only entity compilation.

UIKit example:

```swift
final class LandmarkViewController: UIViewController {
    private let landmark: Landmark

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)

        let entity = LandmarkEntity(landmark: landmark)
        let activity = NSUserActivity(activityType: "com.example.landmarks.view")
        activity.title = landmark.name
        activity.appEntityIdentifier = EntityIdentifier(for: entity)
        activity.isEligibleForSearch = true
        activity.isEligibleForPrediction = true
        view.window?.windowScene?.userActivity = activity
    }
}
```

With that annotation and the `ValueRepresentation` above, the system has a path from “this landmark” to `LandmarkEntity`, then from `LandmarkEntity` to `PlaceDescriptor`, then into a Maps-style destination action.

SwiftUI uses different annotation syntax, but the entity, query, and transfer code is identical.

## Decision tree

When exposing an entity for Siri and Apple Intelligence:

```text
Can Siri find or resolve the entity?
  -> Add EntityQuery / IndexedEntity / onscreen annotations.

Can the destination act on the entity ID directly?
  -> Return/pass the AppEntity.

Does the destination need bytes or a known file format?
  -> Add DataRepresentation or FileRepresentation.

Does the destination need a structured system value?
  -> Add ValueRepresentation / IntentValueRepresentation.

Does incoming structured content refer to an existing entity?
  -> Add IntentValueQuery.

Should incoming structured content create a new entity?
  -> Add importing: on IntentValueRepresentation / ValueRepresentation where supported.

Is there no matching system value?
  -> Do not fake one. Improve schema conformance, indexed properties, display representations,
     onscreen annotations, and domain-specific intents instead.
```

## Validation checklist

- The system value is semantically true, not merely convenient.
- The entity still has a normal query; transfer is not a substitute for resolution.
- The entity is indexed or queryable if Siri needs to find it without onscreen context.
- The value export works from every process that may execute the intent or transfer, including App Intents extensions and WidgetKit extensions.
- The export rechecks authorization at export time.
- Location precision, names, notes, and metadata are redacted according to the user’s current permission and account state.
- File/data representations remain available for destinations that want bytes.
- Value representations are availability-gated for the SDK/OS version that introduced them.
- Tests cover the mapper from private model to system value.
- Manual Siri/Shortcuts tests cover the end-to-end destination action, such as getting directions to an onscreen landmark.

## Anti-patterns

- Adding a `String` property named `address` and assuming Maps will infer navigation behavior.
- Exporting another app’s ID and expecting Siri to use it as that app’s entity.
- Creating a throwaway file that contains coordinates just to satisfy `Transferable`.
- Treating `ValueRepresentation` as arbitrary cross-app object serialization.
- Returning hidden or premium data because the entity was visible in a list.
- Letting UIKit drag export, Share sheet export, and Siri transfer use three different mappers.
- Forgetting that the export may be invoked without the original view controller alive.
- Compiling iOS 27 symbols into an iOS 26 deployment path without availability gates.

## Agent instruction

When auditing a codebase, search every entity that represents a person, place, event, document, message, media item, route, payment destination, or external-world object. For each one, ask:

1. Is there a system App Schema for this object or its actions?
2. Is there a system intent value that accurately represents it?
3. Would another app reasonably need that value in a Siri workflow?
4. Does the app currently export only text/PDF/image when it should export structured value too?
5. Does UIKit/SwiftUI onscreen annotation point at the same entity that owns the transfer representation?

If yes, add `Transferable` plus `ValueRepresentation`/`IntentValueRepresentation` next to the entity, not in the UI layer.
