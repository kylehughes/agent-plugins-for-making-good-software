---
name: brainstorming-design-specs
description: "Develop an implementation-ready design through research and dialogue. Use proactively when product scope, requirements, or engineering tradeoffs remain unresolved; skip specified changes ready to implement."
---

# Brainstorming Design Specs

Structured brainstorming dialogue that explores a problem space deeply enough to produce a design spec. The spec captures sufficient intent and rigor that a planning session can work from it directly without further clarification.

## Design Contract

Resolve the uncertainties that affect implementation. Record meaningful choices, their rationale, applicable invariants, failure modes, and compatibility constraints. Research existing code and relevant APIs before making technical claims; label assumptions that cannot yet be verified.

Scale the dialogue to the problem. A small design may need one focused exchange; a complex feature may need several rounds. Do not ask the user to settle routine choices that project evidence already answers.

## Invocation

When invoked without arguments, infer context from the current conversation — ticket references, feature discussions, recent messages. Fall back to asking the user if no usable context exists.

## Capabilities

The workflow leans on four capabilities. Use the runtime's native mechanism for each; when one is unavailable, fall back as described:

- **Structured questions** — ask the user through the runtime's structured question tool when it has one (up to three focused questions per round); otherwise ask directly in conversation, still bounded to three.
- **Research dispatch** — send read-only explore subagents to search the codebase, sibling implementations, and platform APIs when the runtime supports subagents; otherwise research inline. Do not guess when you can look.
- **Skills** — load the platform and language skills relevant to the problem space, when the problem first touches their scope.
- **Prose review** — before saving the spec, review it with `writing-technical-prose`, or a prose-focused auditor agent when one is available.

When the requested design requires an explicit invariant or proof, or changes an enforcement model or state transition, use [verifying-invariants](../verifying-invariants/SKILL.md) to choose bounded evidence. Do not add it to ordinary brainstorming or preload it for every design.

## The Session

A brainstorming session is a series of **rounds**. Each round follows the same rhythm:

1. **Research** — dispatch explore subagents (or research inline) informed by what you learned in the previous round.
2. **Summarize** — brief restatement of the emerging design and any constraints locked in so far. Keeps both parties synchronized and makes context compaction safe.
3. **Ask** — up to three unresolved questions. Preface each with what you found and why the answer matters. Never a wall of questions.

The agent moves between three modes throughout these rounds. Modes are vocabulary for signaling what you are doing — they describe focus, not a rigid sequence.

### ORIENT (Early Rounds)

Understand the problem space. Load skills, explore the codebase, map the relevant code and patterns. Questions target the highest-uncertainty areas: scope, intent, constraints.

### DEEPEN (Middle Rounds)

Pressure-test the emerging design. Apply each tenet as a questioning lens (see Tenet Integration). Challenge assumptions. Identify type-system opportunities, concurrency implications, edge cases. Lock in decisions as they stabilize.

### CONVERGE (Late Rounds)

Draft the spec and reconcile feedback with the established intent. Ask for confirmation only when a consequential decision remains unresolved.

### Depth Guard

Propose convergence when the outcome, material constraints, acceptance bar, and consequential tradeoffs are clear enough to implement. Surface unresolved decisions explicitly; do not manufacture rounds or questions to meet a quota.

## Tenet Integration

Tenets are questioning lenses used throughout DEEPEN — not a perfunctory checklist at the end.

If the repository declares engineering tenets or principles (a TENETS.md, or a tenets section in AGENTS.md or CLAUDE.md), load them and use each as a lens. Otherwise use this default lens set:

| Tenet | Brainstorming Question |
|---|---|
| Pragmatic, not dogmatic | Does this complexity justify itself? Simpler way? |
| Reduce cognitive load | Will a new developer find this obvious? |
| Push logic into types | Can the type system prevent misuse? What invalid states exist? |
| Align with platform | Idiomatic pattern for this platform? Inventing where the platform provides? |
| Invent empathetically | If new abstraction, is it self-explanatory? |
| Build deliberately | Need this dependency? Internal solution feasible? |

## Spec Format

The format is a modular baseline. Omit sections that don't apply. Expand heavily into areas of complexity. Invent new sections if the domain demands it. A spec may be 50 lines or 5,000 — length follows the problem.

### Required Anchors (Always Present)

- **Problem Statement** — what problem, for whom, why now
- **Design** — the solution, at whatever depth the problem demands
- **Decisions** — choices made with rationale and rejected alternatives

### Common Sections (Include When Relevant)

- **Context / Current State** — what exists, what constrains the solution
- **Data Model** — types, relationships, state representations
- **Behavior** — user-facing behavior, state transitions, edge cases
- **Architecture** — package/module structure, dependencies
- **UI** — screen structure, navigation, interactions
- **Tenet Alignment** — how the design honors each tenet
- **Open Questions** — anything deferred or unresolved
- **Scope** — what's in, what's explicitly deferred

## Completion and Handoff

1. Present the emerging design and any remaining consequential uncertainties.
2. Resolve missing user decisions when they affect the acceptable outcome; otherwise proceed from established intent.
3. Check the design against the applicable tenets.
4. Draft the spec at the requested destination or follow the repository convention. If neither exists, use an allocated scratch directory and report the path; do not create repository policy or ignore rules merely to save it. Use a descriptive filename. Keep durable decisions in the project’s established documentation when requested.
5. Review the spec for prose quality (see Capabilities). Revise as needed.
6. Hand off the spec with its unresolved decisions and acceptance bar. Continue into planning or implementation when the enclosing request already authorizes it; a design-only request ends here.

## Anti-Patterns

- **Question dump** — 10+ questions at once
- **Premature convergence** — claiming implementation readiness while consequential decisions remain unresolved
- **Blind guessing** — proposing design details for platform APIs or existing code without researching to verify
- **Silent research** — running many file reads without explaining to the user what you are looking for and why
- **Tenet theater** — checking tenets perfunctorily at the end instead of using them throughout DEEPEN
- **Monologuing** — long analysis without checking in
