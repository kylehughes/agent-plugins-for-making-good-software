---
name: writing-technical-prose
description: "Write, edit, review, and normalize developer documentation, API comments, READMEs, design docs, runbooks, and PR descriptions. Use proactively for technical prose that needs accurate claims, clear structure, or consistent voice."
---

# Writing Technical Prose

Produce technical prose that is correct, concrete, and useful to capable readers. Prefer finished text over commentary about the text.

## Operating Rules

1. **Preserve truth.** Do not invent APIs, versions, compatibility claims, dates, benchmarks, ownership, commands, file paths, or behavior. Inspect source material when available. Mark unresolved facts with `TODO:` or an explicit assumptions/open-questions section.
2. **Preserve local convention.** Follow nearby documentation for file names, heading style, terminology, capitalization, examples, and depth before applying this guide.
3. **Optimize in this order:** technical correctness, reader usefulness, maintainability, consistency, brevity.
4. **Write the document, not a preface.** Do not include chatbot scaffolding such as `Sure`, `Here’s`, `I’ll`, `Let me`, or explanations of how the answer was produced.
5. **Prefer concrete constraints over vague confidence.** Name prerequisites, limits, failure modes, side effects, rollback paths, and trade-offs.
6. **Do not hide risk.** For decisions, migrations, destructive commands, security-sensitive work, or operational procedures, include the downside and how to detect or recover from failure.
7. **Ask only when blocked.** If a reasonable assumption lets the work proceed, state the assumption in the artifact or a short note and continue.

## Workflow

### Before Writing

- Identify the reader: maintainer, app developer, API consumer, operator, reviewer, or future decision-maker.
- Identify the job: learn, install, decide, migrate, debug, operate, review, or reference.
- Gather source of truth from the repository, existing docs, code, tests, issue text, design notes, or user-provided material.
- Reuse existing terminology. If terms conflict, choose the term used by public APIs or user-facing docs and note the mismatch if it matters.

### When Creating New Prose

- Start with the purpose or problem, not historical background.
- Put the most common path before edge cases.
- Include a minimal working example before optional configuration.
- Explain why a rule or decision exists when the reason affects future maintenance.
- Use examples that resemble the real codebase. Avoid placeholder names such as `foo`, `bar`, `MyClass`, or `doThing()` unless the surrounding project already uses them.

### When Editing Existing Prose

- Preserve meaning unless the user explicitly asks for a rewrite.
- Improve structure before polishing sentences.
- Remove duplication, filler, stale claims, and unsupported certainty.
- Keep stable anchors, heading IDs, public symbol names, and links intact unless they are wrong.
- Prefer small, reviewable edits for existing project docs.

### When Reviewing Prose

Use severity, not taste, to prioritize feedback:

1. Incorrect, misleading, unsafe, or unverifiable statements.
2. Missing prerequisites, failure modes, rollback, or compatibility constraints.
3. Structure that prevents the reader from completing the job.
4. Voice, consistency, grammar, and concision.

For deeper reviews, read the [review checklist](references/review-checklist.md). For optional automated hints or additional terminology rules, read [Linter usage](references/linter-usage.md).

## Voice

### Default Tone

- Pragmatic and direct.
- Neutral rather than enthusiastic.
- Confident when the facts support confidence.
- Honest about trade-offs and unknowns.
- Peer-to-peer: assume the reader is competent, but do not assume they know project-specific context.

### Pronouns

Use pronouns based on document type:

- **Internal team docs:** use `we` for team conventions and decisions.
- **Task instructions:** use imperative mood: “Run `make test`.”
- **External developer docs:** `you` is acceptable when speaking to the developer using an API.
- **Reference docs:** prefer third person or declaration-focused prose.

Read [the pronouns example](references/style-examples.md#pronouns) when this pattern is needed.

### Tense

Use present tense for current behavior and decisions.

Read [the tense example](references/style-examples.md#tense) when this pattern is needed.

Use future tense only for planned work, roadmap items, or explicitly time-bound changes.

## Word Choice

### Avoid by Default

Avoid words and phrases that add confidence without information:

- `just`, `simply`, `basically`, `essentially`, `obviously`, `clearly`
- `seamless`, `robust`, `powerful`, `easy`, `straightforward`, unless the claim is proved or contextualized
- `utilize` when `use` works
- `leverage` when `use`, `build on`, `call`, or `compose` is more precise
- `it should be noted that`, `it is important to note that`, `as previously mentioned`
- unsupported hedges such as `might`, `could potentially`, `may or may not`

Do not ban precise uncertainty. Use `may`, `can`, `might`, or `should` when they express real conditional behavior, permission, probability, or standards language.

### Normative Language

Use `must`, `must not`, `should`, `should not`, and `may` deliberately.

- Use `must` for requirements that break correctness, safety, compatibility, or policy.
- Use `should` for strong recommendations with valid exceptions.
- Use `may` for optional behavior.
- In formal specifications, define normative terms or reference the project’s standard before using RFC-style requirements.

## Structure Principles

Every substantial document should answer these questions in the order the reader needs them:

1. What is this?
2. When do we use it?
3. How do we use it safely?
4. What are the constraints, trade-offs, and failure modes?
5. How do we verify that it worked?
6. Where should the reader look next?

For full templates, read `references/document-patterns.md`.

### README Baseline

Read the README pattern in [document-patterns.md](references/document-patterns.md#readme).

### ADR Baseline

Use the repository’s ADR location if one exists. Otherwise prefer `docs/decisions/YYYY-MM-DD-title.md`.

Read the ADR pattern in [document-patterns.md](references/document-patterns.md#adr).

Every decision statement needs a reason. If there is no downside, state the residual risk or explain why the trade-off is negligible.

## Code and API Documentation

Document public APIs when the reader needs semantics that are not obvious from the signature.

Cover the parts that affect correct use:

- Purpose and lifecycle.
- Parameters, return values, thrown errors, and side effects.
- Threading, actor isolation, cancellation, ordering, and reentrancy.
- Preconditions and invalid states.
- Performance characteristics when they affect caller choices.
- Security, privacy, persistence, network, or filesystem effects.

Do not write comments that restate the next line of code. Use implementation comments for invariants, workarounds, surprising behavior, or bug-prone constraints.

For platform-specific documentation conventions, compose with a platform companion when one is available, and let its rules win for that platform.

## Markdown Formatting

- Use sentence-case headings unless the project uses title case.
- Keep heading levels hierarchical; do not jump from `##` to `####`.
- Include language hints on fenced code blocks.
- Use `sh` for copy-paste commands and `console` for terminal transcripts with prompts or output.
- Do not include `$` prompts in copy-paste command blocks.
- Use backticks for paths, commands, symbols, flags, environment variables, literal values, and package names when they are code identifiers.
- Use tables for dense comparisons or configuration matrices. Do not use tables for prose that would be easier to scan as headings or bullets.
- Use GitHub callouts for warnings and operational hazards:

Read [the Markdown formatting example](references/style-examples.md#markdown-formatting) when this pattern is needed.

## Links and References

- Prefer descriptive links over bare URLs.
- Prefer relative links for repository-local documents.
- Check links when tools allow it.
- Do not cite stale external behavior from memory. Verify current external facts or mark them for verification.

## Security and Safety

- Never include real credentials, tokens, private keys, customer data, or personal data in examples.
- Use realistic but fake placeholders: `sk_test_redacted`, `user@example.com`, `00000000-0000-0000-0000-000000000000`.
- Label destructive commands and include verification or rollback when available.
- Prefer least-privilege examples for permissions, entitlements, IAM policies, API scopes, and filesystem access.

## Output Rules

When asked to write or rewrite a document, output the finished artifact unless the user asked for analysis. When asked for a review, output findings plus concrete replacements. When facts are missing, include the smallest possible `TODO:` markers instead of inventing details.

## Reference Map

Read the reference that matches the deliverable or unresolved writing decision:

- [Document patterns](references/document-patterns.md): README, ADR, RFC, runbook, migration, troubleshooting, PR, and release-note structure.
- [Style examples](references/style-examples.md): examples of pronouns, tense, and Markdown callouts.
- [Review checklist](references/review-checklist.md): final checks for a substantial draft or requested review.
- [Linter usage](references/linter-usage.md): optional checks, additional rule files, and exit statuses.
