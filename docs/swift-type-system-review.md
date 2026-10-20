# Swift type-system integration rubric review

## Findings

No actionable findings.

The follow-up review found incorrect destinations for the decision matrix, release baseline and its 21 headings, and worked example 10. Those 24 mappings and the rendered ledger are corrected. The checker now distinguishes structural validation from comparison with supplied source; see the [follow-up validation](swift-type-system-validation.md#review-follow-up).

All 18 catalog families have a single destination anchor, and each destination retains the family's practical decision: when to use the model, the invariant it can enforce, construction/mutation/erasure boundaries, a concrete sketch or fallback, residual runtime obligations, cost, and a cheaper alternative. I found no family whose destination reduces the source catalog to names or keywords, and no sketch that claims a stronger guarantee than its stated boundary.

## Review boundary

This is a focused, read-only integration review of the four new references and the three changed routers requested by the parent task. The supplied source of truth was `/tmp/swift-type-system-integration-source/Swift_Type_System_Companion`, especially `Swift_6_4_Type_System_Catalog.json` and `Swift_6_4_Type_System_Reference.html`. I also inspected `docs/swift-type-system-integration-map.json` to connect every catalog family to its destination anchor.

The review assesses retained instructional content rather than keyword presence. It does not accept or rerun the archive's compiler corpus, native runtime examples, builds, or tests. Release statements are assessed only as prose with the evidence qualifications written in the new status reference.

| Family | Catalog entries | Destination | Verdict |
| --- | ---: | --- | --- |
| ALG | 14 | [Algebraic structure](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#alg) | Pass |
| VAL | 18 | [Refined values](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#val) | Pass |
| REL | 14 | [Relationships](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#rel) | Pass |
| GEN | 14 | [Generic relationships](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#gen) | Pass |
| ABS | 10 | [Abstraction and erasure](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#abs) | Pass |
| FLOW | 14 | [Workflows](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#flow) | Pass |
| ownership | 25 | [Ownership](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/ownership-effect-recipes.md#ownership) | Pass |
| isolation | 22 | [Isolation](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/ownership-effect-recipes.md#isolation) | Pass |
| effects | 18 | [Effects](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/ownership-effect-recipes.md#effects) | Pass |
| resources | 11 | [Completion and resources](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/ownership-effect-recipes.md#resources) | Pass |
| sizes-packs | 12 | [Static sizes and packs](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#sizes-packs) | Pass |
| DSL | 16 | [Typed DSLs](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#dsl) | Pass |
| ADV | 14 | [Explicit proof evidence](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#adv) | Pass |
| GAP | 9 | [Specialized encodings](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/generic-proof-recipes.md#gap) | Pass |
| representation | 9 | [Binary representation](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/ownership-effect-recipes.md#representation) | Pass |
| APP | 14 | [Applied architecture](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#app) | Pass |
| API | 15 | [Public proof boundaries](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/domain-modeling-recipes.md#api) | Pass |
| frontier | 13 | [Frontier family](../plugins/apple-platform/skills/modeling-swift-types-for-correctness/references/swift-feature-status.md#frontier) | Pass |

## 1. ALG — Algebraic structure and cardinality: Pass

- **Use and invariant:** The section tells the reader to use products for coexisting facts, sums for exclusive alternatives, and a required prefix for minimum cardinality. It states the structural guarantee precisely: the chosen case contains exactly its required payload.
- **Boundaries:** It traces construction through required fields and enum cases, mutation through filtering and exposed array setters, and erasure through collapsing a three-way patch into `Optional`. It also separates tree grammar from termination and finite map coverage from total execution.
- **Example, residual work, and cost:** `Patch` and `NonEmpty` show preservation and deliberate weakening. Serialization, payload refinement, traversal limits, enum resilience, and business semantics remain obligations. The section names case/adapter overhead and prefers `Optional` for a true two-state domain.
- **Substance retained:** Required products, closed sums, correlated flags, three-way patches, `Result`, nonempty/minimum cardinalities, finite maps, normalized derived state, recursive enums, `Never`, unit markers, and exhaustive evolution all remain actionable concepts.
- **Routing walkthrough:** “Our screen can be loading, have stale results, and show a refresh error, but the three optional properties also allow combinations we never handle. How should I model the real states?” The `modeling-swift-types-for-correctness` description matches an impossible-state assessment; its reference map routes to `domain-modeling-recipes.md#alg` without loading generic, ownership, or frontier material.

## 2. VAL — Nominal values and validated construction: Pass

- **Use and invariant:** The section selects a refined value when downstream code repeatedly relies on a runtime predicate. Successful construction carries the accepted input and every admitted instance must satisfy the predicate.
- **Boundaries:** It covers normal and generated initializers, decoding, database hydration, fixtures, wrapper projections, writable/reference storage, aggregate updates, and primitive projections that discard evidence. It explicitly warns that synthesis and public rule protocols can reopen construction.
- **Example, residual work, and cost:** `NonblankLabel` plus a separate editable draft demonstrates refinement without pretending partial UI input is invalid. Predicate correctness, normalization, freshness, numeric closure, persistence, and bypass audits remain. Costs include adapters, rejection handling, and data migration; one concrete wrapper is preferred over a generic rule framework for one predicate.
- **Substance retained:** Newtypes, smart constructors, unforgeable evidence, validated persistence, immutable storage, closed transformations and weakened results, aggregate checks, canonicalization, predicate policies, units, ordering/uniqueness, sink-specific trust types, constructive parsing, property wrappers, literal macros, and explicit drafts are all retained.
- **Routing walkthrough:** “An API sometimes sends a blank display label, and once it enters the app every caller assumes it is usable. I need decoding and in-memory creation to enforce the same rule.” The writing hub's validated-decoding route loads type modeling, which then selects `domain-modeling-recipes.md#val` and the existing decoding detail only as needed.

## 3. REL — Identity, relationships, dimensions, and provenance: Pass

- **Use and invariant:** The section selects tags and type equations when individually valid values must belong together. It distinguishes static category compatibility from runtime identity.
- **Boundaries:** It covers trusted construction of transforms/evidence, policy and revision binding, mutation/version checks, and loss of a shared axis when related values are erased separately. It calls out closures, runtime tenant identity, aliases, and mutable IDs as trust edges.
- **Example, residual work, and cost:** `Point<Space>` and `Transform<From, To>` demonstrate an intermediate-space equation. Matrix meaning, unit conversion, rounding, freshness, graph validity, cryptography, and authority remain runtime or trusted-kernel obligations. Tags are justified only for plausible mix-ups; a two-space conversion function is the simpler option when composition is rare.
- **Substance retained:** Tagged and tenant-scoped IDs, associated correlations, units and coordinates, currencies, clocks, encoding/trust stages, object-bound evidence, versioned snapshots, graph endpoints, identity wrappers, and policy-indexed data remain represented.
- **Routing walkthrough:** “We passed a point measured in camera coordinates into a renderer expecting screen coordinates because both values were pairs of doubles. Can Swift keep the spaces connected through conversions?” The request matches type relationships and routes through type modeling to `domain-modeling-recipes.md#rel`.

## 4. GEN — Generic relationships and protocol contracts: Pass

- **Use and invariant:** The section selects a generic relationship when several positions must choose compatible types. The enforced fact is the declared equality or capability requirement, not the implementation's semantics.
- **Boundaries:** It restricts evidence/policy construction, warns that mutation can replace a related component, and directs packaging before erasure. Public conformances, extension dispatch, metatypes, and stored function laws are treated as trust boundaries.
- **Example, residual work, and cost:** `Then<First, Second>` demonstrates `First.Output == Second.Input`; `Ordering<Value>` demonstrates interpretation as data. Stage meaning, ordering laws, object identity, purity, and termination remain. The guide calls for measuring generic axes, diagnostics, build time, and specialization, with a concrete adapter as rollback.
- **Substance retained:** Shared parameters, same-type and recursive associated constraints, primary associated types, refinements, intersections, conditional conformances/members, `Self` relationships, operation dictionaries, policy wrappers, metatype links, parametric algorithms, and semantic protocol requirements remain useful.
- **Routing walkthrough:** “I can connect any decoder to any repository today, and the mismatch appears as a cast deep in the pipeline. I want the composition point to reject incompatible record types.” The writing hub recognizes preservation of a generic relationship, loads type modeling, then selects `generic-proof-recipes.md#gen`.

## 5. ABS — Abstraction without losing evidence: Pass

- **Use and invariant:** The section chooses abstraction when implementation identity may be hidden but later composition still needs selected axes. Each crossing operation must retain those axes.
- **Boundaries:** It distinguishes opaque results, named generics, constrained existentials, opened existentials, enums, packaged erasers, and eliminators. Witness issuance, closure captures, ownership, isolation, error precision, invocation count, hidden casts, mutation, and lookup completeness are explicit boundaries.
- **Example, residual work, and cost:** `ImportJob<Record>` packaged into `AnyImportJob` keeps source/decoder/sink coherence before erasing the record type. Semantic agreement, cast correctness, and completeness remain trusted. A single generic operation or a closed enum is preferred until runtime storage or replacement requires erasure.
- **Substance retained:** Opaque identity, named shared parameters, constrained/opened existentials, package-before-erase, semantic-axis-preserving erasers, visitors/eliminators, finite sums, heterogeneous stores, and closed evidence behind open interfaces are all present.
- **Routing walkthrough:** “I need to store import jobs for several record types in one queue, but each job's reader, decoder, and saver must stay matched.” The relationship makes type modeling relevant; the need for runtime heterogeneity selects `generic-proof-recipes.md#abs`, rather than loading the entire generic guide set.

## 6. FLOW — Typestate, workflows, and capabilities: Pass

- **Use and invariant:** The section uses state-specific types when callable operations change, and phantom state only when stages share meaningful storage. The guarantee is local operation availability, not eventual completion.
- **Boundaries:** It covers private construction, consuming transitions, failure recovery ownership, copyable snapshots, capability minting/attenuation/revocation, state mutation, session abandonment, and erasure after related stages are packaged.
- **Example, residual work, and cost:** `Attempt<Success, Recovery, Failure>` demonstrates returning the prior noncopyable state on recoverable failure. Validator correctness, resource identity, peer behavior, retries, cancellation, fairness, progress, and deadlock remain. Separate state structs or a plain enum are preferred over generic typestate when they make switching and diagnostics clearer.
- **Substance retained:** Nominal and phantom stages, consuming transitions, required-field builders, independent capability axes, evidence-gated operations, attenuation, one-shot permits, typed branches/recovery, stage payloads, session protocols, progressive refinement, and closed transition algebras remain.
- **Routing walkthrough:** “After validation an upload may be sent, but if validation fails the caller must keep the editable draft and try again. Our current method consumes it either way.” Legal transitions and recovery ownership route through type modeling to `domain-modeling-recipes.md#flow`.

## 7. ownership — Ownership, borrowing, and lifetimes: Pass

- **Use and invariant:** The section uses noncopyability when duplicate local use is the misuse, borrowing for inspection, and consuming operations for transfer. It limits the guarantee to at-most-one consuming use inside the checked Swift boundary.
- **Boundaries:** It traces wrapper/payload/protocol capability suppression, optional slots, binding consumption, aggregate splitting, destructors, borrowed spans/references, accessors, existential packaging, iteration, aliases, foreign handles, and copyable erasure.
- **Example, residual work, and cost:** `ResourceSlot` shows transfer into an optional owner and an explicit `take`. External aliasing, release success, mandatory use, bounds, deep mutability, destructor timing, and iterator termination remain. A scoped operation or immutable value is preferred when ownership does not prevent a real misuse.
- **Substance retained:** Unique values, consuming transitions and tokens, borrow/consume/copy boundaries, exclusive reinitialization, cleanup, partial/pattern consumption, optional ownership, conditional copyability, ownership-polymorphic protocols, noncopyable conformances/existentials, lifetime views, refs/accessors, unique boxes/arrays, and borrowing iteration remain.
- **Routing walkthrough:** “A transaction lease must be transferred to exactly one finisher, and accidental copies currently let two paths attempt completion.” The ownership language in the type-modeling description selects `ownership-effect-recipes.md#ownership`; feature status is loaded only if the chosen mechanism is toolchain-sensitive.

## 8. isolation — Isolation, concurrency, and mutable authority: Pass

- **Use and invariant:** The section chooses an actor for an asynchronous consistency domain and a lock for a synchronous operation. It states the enforced property as authorized exclusive storage access, not transactionality across suspension.
- **Boundaries:** It covers actor construction and encapsulation, complete mutation operations, suspension/reentrancy, `Sendable`, region transfer, isolated parameters/callbacks, executor inheritance, public nonisolated facets, mutex/atomic boundaries, legacy adapters, distributed calls, and actor-reference erasure.
- **Example, residual work, and cost:** `Inventory.reserve()` keeps check-and-decrement in one non-suspending actor operation. Stale revisions, rollback, cancellation, publication protocols, ABA, remote authority, and interleavings remain. An immutable snapshot plus versioned write is the simpler alternative when live sharing is unnecessary.
- **Substance retained:** Actor/global-actor ownership, isolated capabilities and helpers, isolation-preserving callbacks, sendability/transfer, caller isolation and explicit departure, defaults/conformances/metatypes, weak references, locks, atomics, legacy executors, and distributed actors remain differentiated.
- **Routing walkthrough:** “Two purchases can both see stock before an awaited call and then oversell. Help me decide what state has to be reserved before suspension.” The concurrency skill owns scheduling and reentrancy; because the request also asks for an enforcement boundary, its conditional route loads type modeling and `ownership-effect-recipes.md#isolation`.

## 9. effects — Errors, effects, and typed descriptions of work: Pass

- **Use and invariant:** The section uses typed errors for a closed domain failure vocabulary or when a wrapper must preserve the callback's failure type. It limits the guarantee to the throwable type.
- **Boundaries:** It follows error construction/mapping, exhaustive handling, stored results, async sequences, unstructured tasks, `async let`, cancellation, operation protocols, command interpreters, task-local context, `noasync`, mutation of outcomes, and erasure to `any Error`.
- **Example, residual work, and cost:** `ReadFailure` and `readLabel` show a concrete typed boundary and exhaustive inner switch. Provenance, triggering inputs, completion, cancellation, multiplicity, sequence ordering/backpressure, and interpreter laws remain. Untyped `throws` or a small outcome enum is preferred when consumers do not use a closed failure contract.
- **Substance retained:** Closed and generic error channels, `Never`, stored/async results, associated operation failures, explicit sums and translations, inference seams, failure-indexed sequences, task/`async let` carriers, `rethrows`, sync/async distinction, typed commands/programs/context, and direct async restrictions remain.
- **Routing walkthrough:** “Our service exposes three recovery cases, but an async adapter turns them into `any Error`, so every caller falls back to a default branch.” Typed failure triggers the concurrency skill's type-modeling route and then `ownership-effect-recipes.md#effects`.

## 10. resources — Structured lifetime, completion, and protocol obligations: Pass

- **Use and invariant:** The section separates structured scope, consuming authority, and runtime completion. It uses each only for the corresponding child-lifetime, at-most-once, or cleanup obligation.
- **Boundaries:** It traces acquisition/release, callback escape, child and unstructured task ownership, cancellation, continuation storage/take/resume races, async cleanup, destruction, transactions, session transitions, rollback, abandonment, and erasure of authority/identity.
- **Example, residual work, and cost:** `withHandle` shows synchronous bracketed cleanup while candidly exposing that a copyable raw handle may escape. Exactly-once completion, deadlines, cleanup failure, crash recovery, idempotency, peer duality, fairness, deadlock, and durability remain. One scoped operation is preferred over public staged types when callers need a single complete action.
- **Substance retained:** Structured children, explicit unstructured outcomes, consuming continuations, callback multiplicity, bracketed use, async `defer`, cancellation shields, synchronous destruction, consuming transactions, session protocols, and atomic check-and-reserve remain distinct.
- **Routing walkthrough:** “A callback API sometimes calls us twice and sometimes never; cancellation can race the callback, and the task waiting for it must not hang silently.” The concurrency skill owns the bridge and race; mandatory completion invokes type modeling and `ownership-effect-recipes.md#resources` for the separate static and runtime obligations.

## 11. sizes-packs — Static sizes and heterogeneous packs: Pass

- **Use and invariant:** The section uses static sizes for literal dimensions in an API and packs for arbitrary positional heterogeneous relationships. It limits enforcement to declared dimension equality or pack shape.
- **Boundaries:** It covers runtime size validation, branded-index construction, fixed-storage mutation, resize/reorder identity, pack construction/iteration, shape preservation through erasure, layout, and deployment availability.
- **Example, residual work, and cost:** `Matrix<R, K>` multiplied by `Matrix<K, C>` illustrates the shared dimension, while explicitly leaving numerical correctness unproved. Runtime bounds, storage safety, arithmetic propositions, layout, and dynamic input remain. Overloads, tuples/domain structs, hidden fixed storage, or checked arrays are named as simpler alternatives.
- **Substance retained:** Integer dimensions, shape composition, inline storage, same-value operations, branded indices, size reification, heterogeneous/positional packs, variadic transforms and iteration, heterogeneous lists, and natural-number witnesses remain.
- **Routing walkthrough:** “Our image pipeline accepts buffers with incompatible channel counts and discovers the mismatch after processing starts. The supported channel counts are fixed by each stage.” Generic relationship and static shape concerns route through type modeling to `generic-proof-recipes.md#sizes-packs`, with feature status consulted for the selected compiler/runtime.

## 12. DSL — Typed languages, parsing, schemas, and structured access: Pass

- **Use and invariant:** The section selects a typed DSL when many callers build the same constrained parser, route, query, document, schema operation, patch, or command language. Constructors define the grammar and admitted contexts.
- **Boundaries:** It traces source/schema input, syntax recognition, refinement, builders, parsers, generated declarations, decoding, interpreter effects, writable key/case/optic paths, patch mutation, sink-specific encoding, macro expansion, and early `Any` erasure.
- **Example, residual work, and cost:** `ProfileUpdate` demonstrates a typed patch that distinguishes removal from no change and re-enters aggregate validation. Complete parsing, codec/optic laws, deployed schema, authorization, escaping, interpreter semantics, and document accessibility remain. An enum plus parser, checked initializer, or generated nominal model is preferred when sufficient.
- **Substance retained:** Constrained/stateful builders, parser combinators and parser-printers, typed regex/SQL/routes/schema operations, validation-preserving serialization, key/case paths and optics, typed patches/documents/interpolation, and generators with obligations remain.
- **Routing walkthrough:** “Our query builder lets a filter mention a table that was never joined, and the error arrives from the database. Can the construction API rule that out?” The constrained-language request routes through type modeling to `generic-proof-recipes.md#dsl`.

## 13. ADV — Advanced encodings and proof-carrying structures: Pass

- **Use and invariant:** The section reserves advanced encodings for evidence that must travel as a value, result-sorted closed syntax, or one typed program interpreted several ways. Each constructor carries the indices needed for the represented judgment.
- **Boundaries:** It audits equality/proof constructors, transports, enum and recursive storage, environment lookup, certificate/checker issuance, casts in higher-kinded emulation, mutation, decoding, and erasure. It explicitly rejects treating Swift as a total proof calculus.
- **Example, residual work, and cost:** `Equal<A, B>` with a private constructor and reflexive creation, plus `Expression<Output>`, demonstrates sealed evidence and explicit transport. Evaluator meaning, lawfulness, termination, effect behavior, certificate validity, and transformation preservation remain. Closed enums, associated families, concrete command trees, or runtime validation are preferred when they reject the same misuse.
- **Substance retained:** Equality witnesses, finite GADT-style syntax, associated families, typed environments, propositions-as-types, indexed derivations, higher-rank/HKT emulation, tagless-final and initial/free forms, Church/Scott/CPS encodings, departed-proof-style evidence, phase IR, and checked law witnesses remain.
- **Routing walkthrough:** “Our expression tree stores an advertised result type but the evaluator still force-casts each node. We own the finite syntax and need the result sort to survive traversal.” The request matches advanced type evidence and routes to `generic-proof-recipes.md#adv`, after simpler enum/associated-family options are considered.

## 14. GAP — Additional proof encodings and compiler boundaries: Pass

- **Use and invariant:** The section confines specialized encodings to domains that actually share their shape. It covers requirement solving, typed reconstruction, inspectable control, membership/labels, information flow, and modeled budgets without claiming a general solver.
- **Boundaries:** It traces witness/declassification/fuel construction, continuation capture, zipper reconstruction, recursive traversal, mutation, raw projections, unchecked interpreters, optimizer annotations, and index preservation through erasure.
- **Example, residual work, and cost:** The `Continuation` enum demonstrates defunctionalizing a finite callback family. Dispatch scheduling/replay, reconstruction semantics, noninterference, timing channels, and resource-cost correspondence remain. Plain enum machines, domain folds, nominal records, runtime authorization, and measured limits are the preferred lower-cost forms.
- **Substance retained:** Explicit requirement systems, variance-aware interfaces, defunctionalization, indexed zippers, specialized recursion schemes, row-like membership, security labels/declassification, indexed fuel/budgets, and underscored allocation/locking diagnostics remain bounded.
- **Routing walkthrough:** “We need confidential values to reach analytics only through one approved declassification step, but the rest of the app should not carry raw strings.” Type modeling routes the information-flow concern to `generic-proof-recipes.md#gap`; the walkthrough still treats logs, branches, timing, and raw projections as runtime audit work.

## 15. representation — Safe memory representations and binary boundaries: Pass

- **Use and invariant:** The section uses representation constraints for binary parsers and borrowed buffers when they remove unsafe operations. It separates copying bits, observing bytes, constructing from arbitrary bits, and mutating raw storage.
- **Boundaries:** It covers byte/view construction, initialization counts, raw mutation, bounds/alignment/divisibility, temporary allocation, lifetime annotations, FFI aliases, unchecked conformances, pointers/casts, validated UTF-8, and erasure back to bytes.
- **Example, residual work, and cost:** `packetVersion` shows explicit endian parsing plus independent truncation and domain checks. Wire-format stability, business validity, padding, custom conformance truth, external exclusivity/lifetime, normalization, and identifier policy remain. Ordinary array decoding or copying into a small nominal value is preferred when zero-copy benefit is unmeasured.
- **Substance retained:** Bitwise-copyability, byte observation/construction, fully inhabited raw access, typed scalar loading, initialized output buffers, scoped allocation, lifetime-aware FFI, and validated Unicode views remain clearly separated.
- **Routing walkthrough:** “A packet parser currently loads a Swift struct directly from network bytes, and we need to separate memory safety from endian and protocol validation.” The boundary and representation claim routes through type modeling to `ownership-effect-recipes.md#representation`, with status consulted only for the exact byte APIs considered.

## 16. APP — Applied architectures and domain recipes: Pass

- **Use and invariant:** The section applies types at endpoint, cache, query, command, and pipeline seams where correlations are commonly lost. It preserves declared input/output/failure/policy relationships without claiming external systems obey them.
- **Boundaries:** It covers DTO generation and refinement, decoding, heterogeneous cache casts, key/codec construction, schema/version mutation, database interpretation, route restoration, submission-time rechecks, stale request identity, pipeline combination, remote disconnects, and erasure inside one adapter.
- **Example, residual work, and cost:** `Request.Output` and `CacheKey<Value>` illustrate correlated transport and storage. Authentication, server/schema drift, nullability, transactions, query meaning/cost, expiration, delivery/idempotency, conversion math, and remote revocation remain. Named concrete services are preferred for a small operation set.
- **Substance retained:** Typed endpoints, generated DTO refinement, query shapes, form boundaries, navigation/UI phases, required dependencies, static configuration, typed caches/events, import pipelines, media relationships, stateful protocols, and staged programs remain connected to focused existing guides.
- **Routing walkthrough:** “Our cache is keyed by strings and every read force-casts the stored value; a key for thumbnails was reused for profile records.” The type-relationship problem routes to type modeling and `domain-modeling-recipes.md#app`, then to the narrower typed-key guide if implementation detail is needed.

## 17. API — Proof boundaries, API design, and build enforcement: Pass

- **Use and invariant:** The section applies when publishing an invariant-bearing type or changing its public surface. It defines the guarantee as a named set of forbidden client operations within a recorded access/build boundary.
- **Boundaries:** It covers checked and unchecked constructors, subclassing/conformance, setters, writable key paths, `inout`, wrappers, dynamic members, mutable references, raw/literal protocols, unsafe/legacy bridges, generated obligations, and packaging before erasure. Mutation and every public construction route remain part of the seal.
- **Example, residual work, and cost:** `DraftDocument` and `ReadyDocument` show separate editable and publishable APIs. Semantic laws, runtime availability, public ABI/source evolution, compiler settings, build policy, diagnostics, and liveness remain. The section directs readers to measure build/specialization/axis cost and choose a concrete representation or runtime check when proof machinery adds no useful rejection.
- **Substance retained:** Small trusted cores, non-open boundaries, conditional APIs, narrow erasure, escape-hatch inventories, unavailable-operation diagnostics, language/isolation profiles, warnings policy, language/runtime separation, negative fixtures, separate semantic laws, generated checks, restrained conformances, mutation projections, and the simplest faithful model remain.
- **Routing walkthrough:** “We want to publish a validated document type, but clients can still create one from raw text and mutate its title through a writable projection.” Public construction and mutation enforcement route through type modeling to `domain-modeling-recipes.md#api`; API-design guidance is conditional on the resulting public signature work.

## 18. frontier — Unavailable and release-sensitive capabilities: Pass

- **Use and invariant:** All 13 frontier entries state when the desired capability would matter and the exact invariant sought. The section treats the concepts as design vocabulary while distinguishing shipped, experimental, accepted-but-unavailable, declined, and unknown support.
- **Boundaries:** Every entry names relevant construction, mutation, access, decoding, ownership, erasure, FFI, or destruction surfaces. The surrounding release matrix separately records compiler support, flags, and Apple deployment evidence.
- **Example, residual work, and cost:** Each entry supplies a current fallback or isolated probe, followed by residual obligations and adoption cost. Examples include closure-scoped lifetime use, nominal noncopyable aggregates, checked bounded containers, explicit close/finish states, and nominal markers instead of unavailable value parameters.
- **Substance retained:** Custom lifetime dependencies, coroutine accessors, missing noncopyable `Optional` operations, literal/general arithmetic constraints, tuple conformances, noncopyable tuples/packs, future `InlineArray` conformances, declined rigid storage, aliased cells, scalar spans, destructor field consumption, and non-`Int` value parameters all remain individually actionable. The conflict table also retains the source archive's disputed release and performance claims with bounded evidence labels.
- **Routing walkthrough:** “Can the current Swift toolchain express a heap buffer whose capacity cannot grow, or do we still need a checked wrapper?” This is a release-sensitive type-system question. The writing hub conditionally opens feature status, and the status reference routes the concept to `swift-feature-status.md#frontier` without treating a proposal or archived probe as shipped support.

## Router and composition review

**Pass — conditional loading.** `writing-swift` routes invariant-bearing and generic-relationship work to `modeling-swift-types-for-correctness`, while opening feature status directly only for a newer type-system mechanism. `using-swift-concurrency` keeps scheduling, isolation repair, and task lifetime as its concern, then routes ownership, representable state, typed failure, and mandatory completion claims through type modeling. Its platform/build reference now consults feature status only to determine whether an API belongs to the selected preview SDK, while runtime gating follows the API's declaration. `type-driven-design-auditor` preloads only the same-plugin modeling skill and now tells the reviewer to use it as a router rather than blanket-loading advanced recipes or feature status.

**Pass — no duplicated governing rules.** The three recipe guides link to the established implementation references for language rules and keep their own role to task composition, proof boundary, and trade-off. The status guide owns release-sensitive support and evidence classifications. The changed hubs point to those owners instead of restating the 18 families.

**Pass — plugin independence.** Every new production link is relative to content inside `plugins/apple-platform`. The auditor's sole preloaded skill is also in `apple-platform`. The modeling skill's conditional composition with an installed invariant procedure remains availability-qualified, so the Apple plugin does not require a universal-plugin file to resolve its own reference map.

## Limits

- The review establishes content coverage and routing coherence for the inspected working tree. It does not establish compiler acceptance of illustrative Swift.
- The supplied archive's saved compiler reports were treated as supplied evidence only; no native or archived corpus was run.
- Time-sensitive release statements were checked for internal qualification and source attribution, not independently re-researched as part of this bounded review.
