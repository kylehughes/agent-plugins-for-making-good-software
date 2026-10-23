---
name: writing-escalation-briefs
description: "Prepare a standalone expert brief with evidence a reader without repository access needs. Use proactively when debugging stalls or an escalation or expert handoff is requested; skip ordinary first-pass debugging and direct reviews."
---

# Writing Escalation Briefs

## Purpose

Create an expert-ready handoff brief, not another speculative fix. The brief must let a capable engineer answer without reading the prior conversation or accessing the repository. Preserve the highest-signal facts, evidence, constraints, and history while avoiding noise, secrets, and unsupported claims.

While preparing the brief, focus on evidence compression and question extraction. Preserve any enclosing implementation request; preparing a brief does not cancel already authorized work or authorize sending the brief externally.

## When to Use

Use this skill when any of these are true:

- The agent is looping, guessing, or making repeated unsuccessful fixes.
- The root cause remains unclear after reasonable debugging.
- The user asks for a handoff, escalation, expert brief, debugging packet, or summary for another model or person.
- The user asks for a standalone brief to obtain expert judgment on a design, architecture, UI, plan, or approach. A direct request to review a plan stays a review unless a handoff is requested or needed.
- Work functions but its quality is unsatisfying and the effort keeps circling without converging.
- Continued implementation is likely to waste time without better diagnosis or direction.

Do not use this skill for ordinary first-pass debugging, simple code review, or direct implementation unless the user explicitly asks for an escalation-style brief.

## Choose the Mode

Pick one mode before drafting:

- **Diagnosis** — something is broken: failures, crashes, flaky tests, wrong output, stuck debugging.
- **Judgment** — something works or is still a plan, but may be wrong or bad: design and architecture reviews, UI critiques, plan validation, "is this approach right."

Plan review is Judgment where the artifact is the plan and a good outcome is flaws found before implementation begins. If a handoff mixes both (a bug that implies a design flaw), lead with the dominant question and borrow sections from the other mode.

## The Vacuum Rule

The expert operates in a vacuum: no local files, no repository, no prior conversation, no CI artifacts, no screenshots, no attachments, no shared environment — only this brief and public web search. Public documentation cannot substitute for project-specific code, config, logs, schemas, prompts, or examples.

Consequences:

- If the expert needs a code shape, config value, log excerpt, API payload, schema, UI state, or data example to reason about the issue, embed it directly. File paths, line numbers, commit hashes, and test names are provenance labels, never substitutes.
- Quote snippets under a file-path label with enough surrounding context (types, imports, constants, call sites) for a cold reader to interpret them. Mark omissions explicitly with comments such as `// ... unrelated setup omitted ...`. For multi-file flows, include a short call/data-flow map plus the decisive excerpt from each file.
- Transcribe visual artifacts (screenshots, mockups, UI states) into words: layout, hierarchy, exact copy, the colors and spacing that matter, and what is wrong with them.
- Never write "look at `path/to/file`," "see the screenshot," "check the logs above," or "as discussed" unless the content is embedded. Use references only as provenance labels or follow-up locations for someone who later gains access.
- Never imply evidence was inspected, commands were run, or behavior was reproduced unless that actually happened. Never reconstruct unread file contents from memory — embed only what was actually read; artifacts produced in-session may be transcribed from direct knowledge, labeled as transcriptions. If information is unavailable, say so precisely in Missing Information.

## Gathering Evidence

Prefer concrete, recent evidence over memory or narrative. Inspect the smallest useful set of artifacts before writing — a few files, tests, logs, or diffs, not a broad crawl. In priority order:

1. Current failure output: command, test, stack trace, log, or observed UI behavior.
2. Reproduction path: exact steps, inputs, environment, and expected vs. actual behavior.
3. Relevant source: functions, types, routes, components, schemas, generated code, configs.
4. Recent changes: diffs, modified files, dependency updates, migrations, config edits.
5. System context: language/runtime/framework versions, package manager, OS/container details, CI-vs-local differences.
6. Prior attempts: meaningful fixes tried, results, and why each is now weakened or disproven.

In Judgment mode the highest-value evidence shifts: the artifact under review itself (code, plan text, UI transcribed into words), the conventions and precedents it is supposed to honor, and concrete examples of outcomes the user liked or disliked.

If evidence conflicts, preserve the conflict rather than smoothing it over.

## Security and Privacy

Redact secrets before including evidence: tokens, API keys, passwords, cookies, private keys, credentials, authorization headers, session IDs, personal data, and internal-only URLs when sharing externally.

Preserve debugging value while redacting. Keep field names, shapes, prefixes/suffixes, error classes, status codes, host categories, and variable names when safe. Use placeholders such as `<REDACTED_API_KEY>`, `<USER_ID>`, or `<INTERNAL_HOST>`.

Never recommend sharing proprietary code, customer data, or private logs externally unless the user has authorized it. When external sharing risk exists, include a sanitized version and note what was removed.

## Reasoning Rules

Separate facts, observations, inferences, and hypotheses.

- **Fact:** directly confirmed from code, output, docs, or user-provided evidence.
- **Observation:** behavior seen in a run, test, log, screenshot, or trace.
- **Inference:** a conclusion drawn from facts; explain the bridge.
- **Hypothesis:** a plausible root cause not yet proven; include supporting and contradicting evidence.

In Judgment mode, additionally separate the user's stated preferences from the agent's inferences about their preferences; label the latter as inference.

Do not invent prior attempts. If the conversation suggests an attempt but details are unclear, write "Reported/unclear attempt" and explain what is known.

Rank hypotheses by plausibility and diagnostic value, not by confidence alone. Prefer hypotheses that explain all observed symptoms and suggest a decisive next check.

## Ask the User First

Before drafting, check for gaps only the user can fill: what specifically they dislike, the acceptance bar, which constraints are hard versus soft, priorities among competing goals. If any exist and the user is available, ask up to three targeted questions now — their answers become brief content instead of open questions. If question extraction later surfaces more user-held gaps, ask those too; user-answerable questions never go to the expert. Never ask the user anything answerable from the repository or the conversation. If nothing user-held is missing, skip this step. If the user is unavailable, list the unanswered user-held questions in Missing Information, labeled as user-held.

## Extracting Questions for the Expert

The questions at the end of the brief are usually its highest-value content and the easiest part to do badly. Do this exercise after gathering evidence but before writing; its results feed the Least Trustworthy section and the Expert Ask, whose numbered questions the Response Contract refers back to.

Adopt this stance: you may ask a perfect genius who is guaranteed to answer correctly no matter how complex, ambiguous, or cross-domain the question. The only way to waste the opportunity is to ask something you could answer yourself. Ask exactly the questions whose answers would make the work obvious, safe, robust, and verifiable.

Generate candidate questions from three sources:

1. **Friction audit.** You are usually writing this brief because the work got stuck. Name where it actually spun: what was retried more than once, what surprised you each time, what you flip-flopped between, which belief you had to abandon midway. Each recurring friction point conceals a question you have been unable to answer for yourself — state that question explicitly.
2. **Load-bearing assumptions.** List the assumptions your current understanding or plan silently depends on but that were never verified, including every fork where multiple plausible approaches existed and one was picked without decisive evidence. Each unverified assumption and arbitrary fork is a candidate question.
3. **Self-audit.** You are the engineer closest to the work — the one who got stuck or whose judgment is being second-guessed — and a brief written by that engineer naturally justifies its choices. Counter that: What am I most likely wrong about? Which statement above is narrative or memory rather than observation? Which hypothesis am I attached to mainly because I invested in it? The answers become candidate questions and the content of the Least Trustworthy output section.

Filter every candidate through these gates; delete any question that fails one:

- **Not self-answerable.** If it can be settled from the evidence embedded in this brief or by a documentation lookup alone, answer it yourself and delete it. A question that requires applying expertise or judgment to this specific context survives even when public docs are adjacent to it. If the user could answer it, ask the user instead (see Ask the User First).
- **Not the problem restated.** "What is the root cause?" is the whole brief, not a question. Questions must target specific uncertainties beneath the problem.
- **Forks a decision.** You must be able to state what you would do differently depending on the answer: "if A, we do X; if B, we do Y." If every plausible answer leads to the same next action, the question is decorative — delete it.
- **No missing inputs.** The expert must be able to answer from the brief plus their own expertise. If they would need an artifact you have not embedded, embed it, or drop the question and list the missing artifact in Missing Information.

Then run a premortem: imagine the expert's answer arrives, you implement it, and the problem persists. What question do you now wish you had asked? Add it and gate it like the others.

Keep only surviving questions, ordered by stakes; three to seven is a useful range for a complex escalation, not a quota. If none survive, report that the evidence supports a next action rather than inventing questions.

Finally, reverse the direction: predict the first two or three clarifying questions the expert would ask you before answering, and answer them now inside the appropriate brief sections. Round trips are expensive. If you cannot answer one, list it in Missing Information with the reason.

## Output Format

Unless the user requests a different format, write these twelve sections. Sections 1–3 and 7–12 are shared; sections 4–6 depend on the mode.

1. **Executive Summary** — outcome wanted, blocker or decision, key evidence, and the ask in one sentence.
2. **System Context** — versions, architecture, and conventions a cold reader needs.
3. **Embedded Evidence** — the artifacts that matter, quoted inline per the Vacuum Rule.
4. **Problem Statement and Reproduction** (Diagnosis) / **Current Approach and Why It Falls Short** (Judgment).
5. **Attempts So Far** (Diagnosis) / **Quality Criteria and Taste Constraints** (Judgment).
6. **Facts vs. Hypotheses** (Diagnosis) / **Alternatives Already Considered** (Judgment).
7. **Constraints and Non-Goals** — operational restrictions and what not to change.
8. **Missing Information** — what this side lacks, and why.
9. **What a Good Outcome Looks Like** — verification criteria or the acceptance bar.
10. **Where This Account Is Least Trustworthy** — admissions, not hedges.
11. **Expert Ask** — primary request, the gated questions with decision forks, standing invitations.
12. **Response Contract** — the shape of answer that is most actionable.

Read [the brief template](references/brief-template.md) for the full contents required in each section, including the standing-invitation and response-contract blocks to reproduce.

## Density

Write for a senior engineer: concise, factual, specific, with bullets, tables, and snippets where they improve scanability. Avoid vague phrasing like "it doesn't work" without exact supporting evidence, and avoid conversational filler or speculation presented as fact.

If compactness conflicts with standalone completeness, choose standalone completeness. Preserve failed attempts and contradictions — they are diagnostic constraints. Deduplicate repeated stack traces, logs, and attempts; quote only the decisive lines; put bulky but necessary detail in an appendix. If the available context is thin, produce a useful partial brief with a clearly labeled Missing Information section rather than blocking on clarification.

## The Vacuum Test

After drafting, verify standalone-ness by rereading the entire brief as the cold reader the Vacuum Rule defines: only this text and public web search. Every referent the brief does not itself define is a defect:

- A file path or symbol whose contents matter but are not quoted.
- A term of art from this session ("the old approach," "the flaky test," "the refactor") never explained.
- A screenshot, diff, log, ticket, or attachment referenced but not transcribed.
- A claim that depends on knowing what happened earlier in the conversation.
- A question the expert would have to ask before they could start.

Fix each defect by embedding the missing content or deleting the reference. Then confirm the cold reader can answer four things: what is wanted, what is known versus hypothesized, what is being asked of them, and what a good answer looks like.

If your runtime supports subagents, delegate the cold read: give a subagent only the brief text — no file paths to open, no conversation context — and have it list every undefined referent and every question it cannot answer from the brief alone. Fix what it finds. Otherwise perform the pass yourself as a deliberately fresh read, top to bottom.

## Delivery

Honor the user’s requested format and destination. By default, write the finished brief to a single self-contained markdown file — one contiguous document with no links to other local files — named `handoff-<topic-slug>.md` in your runtime's scratch or temporary directory. In chat, give the user the file path and the Executive Summary; do not duplicate the brief.

Copy to the clipboard only when requested, using an available platform tool. If file writing is unavailable or denied, emit the brief as one contiguous markdown message with nothing after it.

## Applying the Expert's Answer

When the expert's response comes back (usually pasted in by the user), treat it as strong hypotheses from someone who never saw the repository — not as instructions.

- Verify every factual claim about the code against the actual code before acting on it.
- Run the expert's decisive checks first; do not apply broad changes on trust.
- Expect wrong identifiers, paths, and API names — the expert reasoned from excerpts. Adapt the idea to the codebase; do not transplant text verbatim.
- Check the recommendation against the brief's Constraints and Non-Goals; the expert may not have honored all of them.
- Where repo reality contradicts an expert assumption, tell the user and consider a short follow-up brief rather than silently patching around it.

## Reference Map

Load only what the current step needs:

- [Brief template](references/brief-template.md): the required contents of all twelve sections in both modes, plus the standing-invitation and response-contract blocks. Read it before writing the brief.
