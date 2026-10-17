---
name: brainstorming-design-specs
description: "Develop an implementation-ready design through research and dialogue when scope, requirements, or tradeoffs are unresolved. Use for ambiguous product or engineering work, not a specified change ready to implement."
---

# Brainstorming Design Specs

Structured brainstorming dialogue that explores a problem space deeply enough to produce a design spec. The spec captures sufficient intent and rigor that a planning session can work from it directly without further clarification.

## Core Principle: Leave No Stone Unturned

Every brainstorming session should produce a spec where:

- **Every design choice is deliberate** — no "this seemed fine" defaults. Every meaningful decision has a rationale and considered alternatives.
- **Invalid states are identified and bounded** — the spec calls out what the type system should prevent, what invariants must hold, what error states exist, and which boundary enforces each one.
- **Edge cases are surfaced, not deferred** — concurrency implications, failure modes, migration paths, backward compatibility. If it matters, it's in the spec.
- **Nothing is assumed** — you research the codebase, sibling implementations on other platforms when the project has them, and platform APIs rather than guessing. The user articulates intent rather than leaving it implicit.

Front-load the thinking so implementation is confident and correct.

## Invocation

When invoked without arguments, infer context from the current conversation — ticket references, feature discussions, recent messages. Fall back to asking the user if no usable context exists.

## Capabilities

The workflow leans on four capabilities. Use the runtime's native mechanism for each; when one is unavailable, fall back as described:

- **Structured questions** — ask the user through the runtime's structured question tool when it has one (2–4 questions per round); otherwise ask directly in conversation, still bounded to 2–4.
- **Research dispatch** — send read-only explore subagents to search the codebase, sibling implementations, and platform APIs when the runtime supports subagents; otherwise research inline. Do not guess when you can look.
- **Skills** — load the platform and language skills relevant to the problem space, proactively at the start and again as the domain clarifies.
- **Prose review** — before saving the spec, review it with `writing-technical-prose`, or a prose-focused auditor agent when one is available.

When the requested design requires an explicit invariant or proof, or changes an enforcement model or state transition, use [verifying-invariants](../verifying-invariants/SKILL.md) to choose bounded evidence. Do not add it to ordinary brainstorming or preload it for every design.

## The Session

A brainstorming session is a series of **rounds**. Each round follows the same rhythm:

1. **Research** — dispatch explore subagents (or research inline) informed by what you learned in the previous round.
2. **Summarize** — brief restatement of the emerging design and any constraints locked in so far. Keeps both parties synchronized and makes context compaction safe.
3. **Ask** — 2–4 questions. Preface each with what you found and why the answer matters. Never a wall of questions.

The agent moves between three modes throughout these rounds. Modes are vocabulary for signaling what you are doing — they describe focus, not a rigid sequence.

### ORIENT (Early Rounds)

Understand the problem space. Load skills, explore the codebase, map the relevant code and patterns. Questions target the highest-uncertainty areas: scope, intent, constraints.

### DEEPEN (Middle Rounds)

Pressure-test the emerging design. Apply each tenet as a questioning lens (see Tenet Integration). Challenge assumptions. Identify type-system opportunities, concurrency implications, edge cases. Lock in decisions as they stabilize.

### CONVERGE (Late Rounds)

Draft the spec, present for review, refine until both parties confirm it captures intent.

### Depth Guard

Minimum **3 rounds** before proposing convergence. Track rounds explicitly. The agent naturally moves from ORIENT toward DEEPEN as the problem space clarifies — early convergence is the most common failure mode.

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

1. Propose convergence with confidence level and remaining concerns.
2. Ask the user if any areas feel underexplored.
3. Final tenet sweep.
4. Draft the spec. Save to a gitignored scratch or spec location in the repository (create it if needed; confirm the location with the user if the project has no convention). Name it `YYYY-MM-DDTHHMM Title.md` — timestamped with date and time to avoid collisions across parallel worktrees. No ticket reference in the filename. Specs are local-only — they serve the brainstorm and implementation sessions, not as permanent documentation. Decisions that outlive the feature branch belong in the PR description, ADRs, or agent skills.
5. Review the spec for prose quality (see Capabilities). Revise as needed.
6. Suggest the user proceed to plan mode or their planning flow, referencing the spec. Do NOT start planning or implementation yourself.

## Anti-Patterns

- **Question dump** — 10+ questions at once
- **Premature convergence** — spec before 3 rounds
- **Blind guessing** — proposing design details for platform APIs or existing code without researching to verify
- **Silent research** — running many file reads without explaining to the user what you are looking for and why
- **Tenet theater** — checking tenets perfunctorily at the end instead of using them throughout DEEPEN
- **Monologuing** — long analysis without checking in
