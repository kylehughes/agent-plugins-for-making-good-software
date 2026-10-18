---
name: designing-swift-apis
description: "Design and review Swift API names, argument labels, signatures, and documentation contracts using Apple's API Design Guidelines."
---

# Designing Swift APIs

This skill provides guidance on designing clear, idiomatic Swift APIs following Apple's official design guidelines.

Match the requested design scope. For naming-only work, preserve types and behavior and confine recommendations to names, argument labels, and call sites. Clarify weakly typed parameters with role nouns; reserve type-modeling or architectural recommendations for a request that includes those concerns.

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

For a worked example, read [summary format](references/examples.md#summary-format).

### Documentation Markup

Use recognized symbol documentation commands to provide structured information beyond the summary:

For a worked example, read [documentation markup](references/examples.md#documentation-markup).

Key commands: `Parameter(s)`, `Returns`, `Throws`, `Complexity`, `Precondition`, `Postcondition`, `Note`, `Important`, `SeeAlso`.

## Naming for Clarity

### Include Necessary Words

Include all words needed to avoid ambiguity at the use site:

For a worked example, read [include necessary words](references/examples.md#include-necessary-words).

### Omit Needless Words

Remove words that repeat type information:

For a worked example, read [omit needless words](references/examples.md#omit-needless-words).

### Name by Role, Not Type

Name variables and parameters by their role, not their type constraints:

For a worked example, read [name by role, not type](references/examples.md#name-by-role-not-type).

### Compensate for Weak Types

When using `Any`, `AnyObject`, `Int`, or `String`, add nouns describing the role:

For a worked example, read [compensate for weak types](references/examples.md#compensate-for-weak-types).

## Fluent Usage

### Grammatical Phrases

Method names should form grammatical English phrases:

For a worked example, read [grammatical phrases](references/examples.md#grammatical-phrases).

### Factory Methods

Begin factory methods with `make`:

For a worked example, read [factory methods](references/examples.md#factory-methods).

### Initializers

First argument should not form a phrase with the base name:

For a worked example, read [initializers](references/examples.md#initializers).

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

For a worked example, read [boolean properties and methods](references/examples.md#boolean-properties-and-methods).

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

For a worked example, read [case conventions](references/examples.md#case-conventions).

### Computed Property Complexity

Document the complexity of computed properties that are not O(1).

### Method Overloading

Methods may share a base name when they have the same basic meaning and operate in distinct domains:

For a worked example, read [method overloading](references/examples.md#method-overloading).

Avoid overloading on return type alone — it causes ambiguities with type inference.

## Parameters

### Parameter Names for Documentation

Choose names that make documentation read naturally:

For a worked example, read [parameter names for documentation](references/examples.md#parameter-names-for-documentation).

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

For a worked example, read [prepositional phrases](references/examples.md#prepositional-phrases).

## Special Cases

### Tuple Members and Closure Parameters

Label tuple members and name closure parameters for clarity:

For a worked example, read [tuple members and closure parameters](references/examples.md#tuple-members-and-closure-parameters).

### Unconstrained Polymorphism

When using `Any` or unconstrained generics, be explicit to avoid ambiguity:

For a worked example, read [unconstrained polymorphism](references/examples.md#unconstrained-polymorphism).

## Reference Map

Read the relevant section of [examples](references/examples.md) when a naming, argument-label, or documentation rule needs a concrete call site. Before finishing, check the changed API against the rules above.
