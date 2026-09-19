# Swift API examples

Read only the example section relevant to the current task.

## Contents

- [Summary Format](#summary-format)
- [Documentation Markup](#documentation-markup)
- [Include Necessary Words](#include-necessary-words)
- [Omit Needless Words](#omit-needless-words)
- [Name by Role, Not Type](#name-by-role-not-type)
- [Compensate for Weak Types](#compensate-for-weak-types)
- [Grammatical Phrases](#grammatical-phrases)
- [Factory Methods](#factory-methods)
- [Initializers](#initializers)
- [Boolean Properties and Methods](#boolean-properties-and-methods)
- [Case Conventions](#case-conventions)
- [Method Overloading](#method-overloading)
- [Parameter Names for Documentation](#parameter-names-for-documentation)
- [Prepositional Phrases](#prepositional-phrases)
- [Tuple Members and Closure Parameters](#tuple-members-and-closure-parameters)
- [Unconstrained Polymorphism](#unconstrained-polymorphism)

## Summary Format

```swift
/// Returns a "view" of `self` containing the same elements in reverse order.
func reversed() -> ReverseCollection

/// Inserts `newHead` at the beginning of `self`.
mutating func prepend(_ newHead: Int)

/// Accesses the `index`th element.
subscript(index: Int) -> Element { get set }

/// Creates an instance containing `n` repetitions of `x`.
init(count n: Int, repeatedElement x: Element)
```

## Documentation Markup

```swift
/// Returns the element at the specified position.
///
/// - Parameter index: The position of the element to access. `index`
///   must be a valid index of the collection that is not equal to the
///   `endIndex` property.
/// - Returns: The element at the specified index.
/// - Throws: `CollectionError.outOfBounds` if the index is invalid.
/// - Complexity: O(1)
subscript(index: Int) -> Element { get }
```

## Include Necessary Words

```swift
// Good: clear what 'at' means
employees.remove(at: x)

// Bad: unclear if removing x or element at x
employees.remove(x)
```

## Omit Needless Words

```swift
// Bad: Element is redundant
func removeElement(_ member: Element) -> Element?

// Good: role is clear from context
func remove(_ member: Element) -> Element?
```

## Name by Role, Not Type

```swift
// Bad: type names as variable names
var string = "Hello"
func restock(from widgetFactory: WidgetFactory)

// Good: role-based names
var greeting = "Hello"
func restock(from supplier: WidgetFactory)
```

## Compensate for Weak Types

```swift
// Bad: vague with NSObject parameter
func add(_ observer: NSObject, for keyPath: String)

// Good: role is explicit
func addObserver(_ observer: NSObject, forKeyPath path: String)
```

## Grammatical Phrases

```swift
// Good: reads naturally
x.insert(y, at: z)          // "x, insert y at z"
x.subviews(havingColor: y)  // "x's subviews having color y"
x.capitalizingNouns()       // "x, capitalizing nouns"

// Bad: awkward reading
x.insert(y, position: z)
x.subviews(color: y)
```

## Factory Methods

```swift
x.makeIterator()
factory.makeWidget(gears: 42, spindles: 14)
```

## Initializers

```swift
// Good: arguments don't continue the name
let foreground = Color(red: 32, green: 64, blue: 128)
let ref = Link(target: destination)

// Bad: forced grammatical continuity
let foreground = Color(havingRGBValuesRed: 32, green: 64, andBlue: 128)
```

## Boolean Properties and Methods

```swift
x.isEmpty
line1.intersects(line2)
```

## Case Conventions

```swift
var utf8Bytes: [UTF8.CodeUnit]
var isRepresentableAsASCII = true
var userSMTPServer: SecureSMTPServer
```

## Method Overloading

```swift
// Good: same concept, distinct domains
extension Shape {
    func contains(_ other: Shape) -> Bool { ... }
    func contains(_ point: CGPoint) -> Bool { ... }
}
```

## Parameter Names for Documentation

```swift
// Good: reads well in docs
func filter(_ predicate: (Element) -> Bool) -> [Element]
mutating func replaceRange(_ subRange: Range, with newElements: [E])

// Bad: awkward in docs
func filter(_ includedInResult: (Element) -> Bool) -> [Element]
```

## Prepositional Phrases

```swift
// Good: single abstraction
a.moveTo(x: b, y: c)
a.fadeFrom(red: b, green: c, blue: d)

// Not: broken abstraction
a.move(toX: b, y: c)
```

## Tuple Members and Closure Parameters

```swift
mutating func ensureUniqueStorage(
  minimumCapacity requestedCapacity: Int,
  allocate: (_ byteCount: Int) -> UnsafePointer<Void>
) -> (reallocated: Bool, capacityChanged: Bool)
```

## Unconstrained Polymorphism

```swift
// Ambiguous when Element is Any
func append(_ newElement: Element)
func append(_ newElements: S) where S.Element == Element

// Clear: explicit naming
func append(_ newElement: Element)
func append(contentsOf newElements: S) where S.Element == Element
```
