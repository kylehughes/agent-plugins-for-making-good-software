# Technical Writing Review Checklist

Use this reference when reviewing documentation, editing a large document, or deciding whether a draft is ready to land.

## Review Output

Prefer this structure for reviews:

```markdown
## Blocking

- Issue, why it matters, and concrete fix.

## Accuracy and Risk

- Unverified claim, missing prerequisite, unsafe command, stale version, or ambiguous behavior.

## Structure

- Reordering or section changes that help the reader complete the job.

## Style Edits

- Concision, terminology, grammar, and voice consistency.

## Suggested Rewrite

Provide replacement text for the highest-value section.
```

Skip empty sections.

## Correctness Checklist

- Claims match code, tests, configuration, release state, and platform behavior.
- Commands exist and run from the documented working directory.
- File paths, target names, schemes, package names, flags, and environment variables are exact.
- Version and availability claims are verified.
- Examples use real symbols or marked placeholders.
- Links point to the intended target.
- Screenshots, diagrams, and prose agree.
- Known limitations are not framed as solved.
- Security, privacy, data retention, and destructive side effects are explicit.

## Reader-Task Checklist

- The opening tells the reader whether the document is relevant to them.
- Prerequisites appear before steps that require them.
- The happy path is complete.
- Edge cases do not interrupt the happy path.
- Troubleshooting maps symptoms to fixes.
- Verification tells the reader how to know the work succeeded.
- Rollback exists for migrations, deployments, and destructive operations.

## Structure Checklist

- Headings form a useful outline when read alone.
- Sections appear in task order, not author discovery order.
- Related concepts are grouped together.
- Tables compare structured attributes; prose explains causality and trade-offs.
- Lists are parallel and not overloaded with multi-paragraph items.
- Repeated concepts link back to one source of truth.

## Voice Checklist

- Direct present-tense prose.
- No chatbot prefaces.
- No marketing adjectives without proof.
- No filler confidence words: `just`, `simply`, `basically`, `essentially`, `obviously`, `clearly`.
- No fake certainty. Conditional behavior is named as conditional behavior.
- Trade-offs use plain labels: cost, risk, limitation, workaround, follow-up.
- Instructions use imperative mood.

## Code Example Checklist

- Code blocks have language hints.
- Examples are realistic and minimal.
- Copy-paste command blocks omit shell prompts.
- Terminal transcript blocks use `console` and may include prompts/output.
- Placeholders are named after their role: `apiBaseURL`, `userID`, `thumbnailSize`.
- Secrets are redacted or fake.
- Error handling is included when omitting it would teach unsafe use.
- Async/concurrency examples show actor or cancellation semantics when relevant.

## Common Replacements

| Replace | With |
|---------|------|
| simply use | use |
| just run | run |
| utilize | use |
| leverage | use, call, compose, build on, depending on meaning |
| easy / straightforward | describe the actual prerequisite or number of steps |
| robust | name the failure mode it handles |
| seamless | name what does not require manual work |
| it should be noted that | delete or make the point directly |
| may or may not | state the condition |
| APNS | APNs |

## Optional Local Lint

Run the bundled linter when checking Markdown or Swift prose:

```sh
python3 scripts/lint_technical_writing.py README.md docs Sources
```

The linter reports style warnings only. Treat it as a review aid, not a source of truth. Override it when project terminology or technical accuracy requires the flagged wording.

## Ready-to-Land Criteria

A document is ready when:

- A target reader can tell whether it applies to them.
- The primary task can be completed from the document alone or from explicitly linked prerequisites.
- Risk, limitations, and verification are explicit.
- The document does not rely on invented or unverifiable facts.
- Examples are realistic enough to transfer to the actual project.
