---
name: designing-swift-apis
description: Apply Apple's Swift API design guidelines for naming, documentation comments, argument labels, and conventions. Use when writing or reviewing Swift APIs, choosing method or property names, designing function signatures, picking between mutating and nonmutating variants, naming protocols, writing doc comments, deciding when to use argument labels, or ensuring call sites read as grammatical English phrases.
---

# Designing Swift APIs

This skill provides guidance on designing clear, idiomatic Swift APIs following Apple's official design guidelines.

## Core Principle

**Clarity at the point of use** is the most important goal. APIs are declared once but used repeatedly—optimize for the reader at the call site.

## Documentation Comments

Write a documentation comment for every declaration. If describing functionality is difficult, the API may need redesign.

### Summary Format

- Begin with a single sentence fragment ending with a period
- Describe what functions/methods **do** and **return** (omit void returns)
- For subscripts: describe what they **access**
- For initializers: describe what they **create**
- For properties/types: describe what they **are**

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

### Documentation Markup

Use recognized symbol documentation commands to provide structured information beyond the summary:

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

Key commands: `Parameter(s)`, `Returns`, `Throws`, `Complexity`, `Precondition`, `Postcondition`, `Note`, `Important`, `SeeAlso`.

## Naming for Clarity

### Include Necessary Words

Include all words needed to avoid ambiguity at the use site:

```swift
// Good: clear what 'at' means
employees.remove(at: x)

// Bad: unclear if removing x or element at x
employees.remove(x)
```

### Omit Needless Words

Remove words that repeat type information:

```swift
// Bad: Element is redundant
func removeElement(_ member: Element) -> Element?

// Good: role is clear from context
func remove(_ member: Element) -> Element?
```

### Name by Role, Not Type

Name variables and parameters by their role, not their type constraints:

```swift
// Bad: type names as variable names
var string = "Hello"
func restock(from widgetFactory: WidgetFactory)

// Good: role-based names
var greeting = "Hello"
func restock(from supplier: WidgetFactory)
```

### Compensate for Weak Types

When using `Any`, `AnyObject`, `Int`, or `String`, add nouns describing the role:

```swift
// Bad: vague with NSObject parameter
func add(_ observer: NSObject, for keyPath: String)

// Good: role is explicit
func addObserver(_ observer: NSObject, forKeyPath path: String)
```

## Fluent Usage

### Grammatical Phrases

Method names should form grammatical English phrases:

```swift
// Good: reads naturally
x.insert(y, at: z)          // "x, insert y at z"
x.subviews(havingColor: y)  // "x's subviews having color y"
x.capitalizingNouns()       // "x, capitalizing nouns"

// Bad: awkward reading
x.insert(y, position: z)
x.subviews(color: y)
```

### Factory Methods

Begin factory methods with `make`:

```swift
x.makeIterator()
factory.makeWidget(gears: 42, spindles: 14)
```

### Initializers

First argument should not form a phrase with the base name:

```swift
// Good: arguments don't continue the name
let foreground = Color(red: 32, green: 64, blue: 128)
let ref = Link(target: destination)

// Bad: forced grammatical continuity
let foreground = Color(havingRGBValuesRed: 32, green: 64, andBlue: 128)
```

## Side Effects and Naming

### Noun vs Verb Phrases

- **No side effects**: noun phrases (`x.distance(to: y)`, `x.successor()`)
- **Has side effects**: imperative verb phrases (`print(x)`, `x.sort()`, `x.append(y)`)

### Mutating/Nonmutating Pairs

When a verb describes the operation:

| Mutating | Nonmutating |
|----------|-------------|
| `x.sort()` | `z = x.sorted()` |
| `x.append(y)` | `z = x.appending(y)` |
| `x.reverse()` | `z = x.reversed()` |
| `x.stripNewlines()` | `z = x.strippingNewlines()` |

Use past participle (`-ed`) when grammatical, present participle (`-ing`) otherwise.

When a noun describes the operation:

| Nonmutating | Mutating |
|-------------|----------|
| `x = y.union(z)` | `y.formUnion(z)` |
| `j = c.successor(i)` | `c.formSuccessor(&i)` |

## Boolean Properties and Methods

Should read as assertions about the receiver:

```swift
x.isEmpty
line1.intersects(line2)
```

## Protocol Naming

- **Describes what something is**: nouns (`Collection`, `Sequence`)
- **Describes a capability**: `-able`, `-ible`, or `-ing` suffixes (`Equatable`, `ProgressReporting`)

## Terminology

- Avoid obscure terms when common words suffice — don't say "epidermis" when "skin" works
- If using a term of art, use it precisely according to its accepted meaning — don't repurpose established terms with new definitions
- Avoid abbreviations unless commonly understood (e.g., `URL` is fine, `bg` is not)
- Embrace precedent: prefer `Array` over `List`, `sin(x)` over verbose alternatives — match what experienced developers expect

## Conventions

### Case Conventions

- Types and protocols: `UpperCamelCase`
- Everything else: `lowerCamelCase`
- Acronyms follow case conventions uniformly:

```swift
var utf8Bytes: [UTF8.CodeUnit]
var isRepresentableAsASCII = true
var userSMTPServer: SecureSMTPServer
```

### Computed Property Complexity

Document the complexity of computed properties that are not O(1).

### Method Overloading

Methods may share a base name when they have the same basic meaning and operate in distinct domains:

```swift
// Good: same concept, distinct domains
extension Shape {
    func contains(_ other: Shape) -> Bool { ... }
    func contains(_ point: CGPoint) -> Bool { ... }
}
```

Avoid overloading on return type alone — it causes ambiguities with type inference.

## Parameters

### Parameter Names for Documentation

Choose names that make documentation read naturally:

```swift
// Good: reads well in docs
func filter(_ predicate: (Element) -> Bool) -> [Element]
mutating func replaceRange(_ subRange: Range, with newElements: [E])

// Bad: awkward in docs
func filter(_ includedInResult: (Element) -> Bool) -> [Element]
```

### Default Parameters

- Use defaults for commonly-used values
- Place parameters with defaults toward the end
- Prefer defaults over method families—one method is simpler than four overloads

## Argument Labels

### When to Omit Labels

- Arguments that can't be usefully distinguished: `min(number1, number2)`
- Value-preserving type conversions: `Int64(someUInt32)`

### When to Include Labels

- Narrowing conversions: `UInt32(truncating: source)`
- First argument forms prepositional phrase: `x.removeBoxes(havingLength: 12)`
- First argument doesn't form grammatical phrase with base name: `view.dismiss(animated: false)`

### Prepositional Phrases

Start label at the preposition, except when arguments represent a single abstraction:

```swift
// Good: single abstraction
a.moveTo(x: b, y: c)
a.fadeFrom(red: b, green: c, blue: d)

// Not: broken abstraction
a.move(toX: b, y: c)
```

## Special Cases

### Tuple Members and Closure Parameters

Label tuple members and name closure parameters for clarity:

```swift
mutating func ensureUniqueStorage(
  minimumCapacity requestedCapacity: Int,
  allocate: (_ byteCount: Int) -> UnsafePointer<Void>
) -> (reallocated: Bool, capacityChanged: Bool)
```

### Unconstrained Polymorphism

When using `Any` or unconstrained generics, be explicit to avoid ambiguity:

```swift
// Ambiguous when Element is Any
func append(_ newElement: Element)
func append(_ newElements: S) where S.Element == Element

// Clear: explicit naming
func append(_ newElement: Element)
func append(contentsOf newElements: S) where S.Element == Element
```
