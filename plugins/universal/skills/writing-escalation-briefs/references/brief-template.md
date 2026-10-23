# Brief template

The required contents of each section of an escalation brief. Use this structure unless the user requests a different format. Sections 1–3 and 7–12 are shared; sections 4–6 depend on the mode chosen in SKILL.md.

Every section assumes the Vacuum Rule's cold reader: no repository, no prior conversation, no ability to run commands — only this brief and public web search.

## 1. Executive Summary

One short paragraph with: desired outcome, current blocker or decision on the table, most important evidence, and the ask in one sentence — the expert should know the question before the details.

## 2. System Context

Only the context needed to reason about the issue, but complete enough for the Vacuum Rule's cold reader: language, framework, platform, runtime, package manager, and relevant versions if known; architecture, module boundaries, data flow, lifecycle, external services, database/schema, generated code, or build/test setup; project conventions that constrain an answer.

## 3. Embedded Evidence

The relevant artifacts and why each matters, with the needed contents quoted inline per the Vacuum Rule: source, configs, schemas, fixtures, logs, runtime/dependency details, and any contradictory or surprising evidence. In Judgment mode this carries the supporting evidence — conventions, precedents, examples of liked or rejected outcomes; the artifact under review itself lives in section 4.

## 4–6 in Diagnosis Mode

**4. Problem Statement and Reproduction.** Intended behavior, why current behavior is wrong, expected vs. actual. Steps to reproduce: commands run, inputs used, or user action taken; failing tests, assertions, stack traces, logs, or UI state; whether the failure is deterministic, intermittent, local-only, CI-only, device-specific, environment-specific, or data-dependent. If reproduction is unknown, give the best-known trigger and label gaps clearly.

**5. Attempts So Far.** For each meaningful attempt: what changed or was tested, why it seemed plausible, result observed, and why it did not solve the problem or what uncertainty remains. Separate attempted fixes from passive observations. Skip trivial or duplicate attempts unless they prevent rework.

**6. Facts vs. Hypotheses.** Two subsections. **Confirmed facts:** bullet only directly supported facts. **Ranked hypotheses:** for each — plausibility (high/medium/low), why it fits, evidence against it or missing evidence, and the fastest decisive test or inspection.

## 4–6 in Judgment Mode

**4. Current Approach and Why It Falls Short.** Embed the artifact under judgment: the current design, plan, or UI transcribed into words per the Vacuum Rule. Then state the specific dissatisfaction — what feels wrong, where it breaks down, what prompted the escalation. "We have been circling" is a symptom; say what keeps pulling the work back.

**5. Quality Criteria and Taste Constraints.** Define what "good" means here, because the expert cannot infer it: product and user priorities the solution must serve; platform idioms, project conventions, and architectural values that constrain the answer; the user's stated taste, with concrete examples of outcomes they liked or rejected and the reason if known; hard criteria vs. soft preferences, labeled.

**6. Alternatives Already Considered.** For each option weighed: what it was, why it was attractive, why it was rejected or parked, and any partial attempt and what it revealed. This stops the expert from re-proposing dead ends.

## 7. Constraints and Non-Goals

User requirements and acceptance criteria; compatibility requirements, dependency restrictions, API contracts, performance limits, security/privacy requirements, deadlines, and migration constraints; codebase conventions and architectural boundaries; things the expert should avoid changing. In Judgment mode, section 5 owns the definition of "good"; this section carries only operational restrictions.

## 8. Missing Information

Missing artifacts that would materially improve the answer: logs, repro data, failing command output, env vars, dependency versions, schema state, or relevant file contents. Only items that matter — not a generic questionnaire. If a needed artifact exists but could not be included safely or was not inspected, list it here with the precise reason — including artifacts this side could still obtain, so the user can fetch them before sending the brief. This section is for what this side lacks: artifacts and data the expert cannot supply, and user-held answers that could not be obtained. Questions calling on the expert's judgment or knowledge belong in the Expert Ask, not here.

## 9. What a Good Outcome Looks Like

In Diagnosis mode: exact verification criteria — test commands, test names, manual checks, expected logs, metrics; regression checks that should stay green; edge cases that should be covered. In Judgment mode: the acceptance bar — what the user would recognize as "yes, that's it," and how a recommendation would be validated (prototype, review, metric).

## 10. Where This Account Is Least Trustworthy

This brief was written by the engineer closest to the work — the one who got stuck or whose judgment is being questioned — so it inherits that engineer's blind spots. In 2–4 bullets, tell the expert where to distrust the account:

- The claim above most likely to be wrong, and why doubt is warranted.
- Anything reported as fact that is actually interpretation or memory.
- The hypothesis the author is most invested in, so the expert can discount the attachment.

These are admissions, not hedges. Do not soften them into restatements of the open questions.

## 11. Expert Ask

This section carries the weight of the whole brief. Three parts:

**Primary request.** One or two sentences stating the help needed: diagnose the likely root cause, propose the minimal safe patch, identify the missing invariant or architectural mismatch, design a decisive test, or review an approach against the constraints.

**Questions.** Only the questions that survived the gates in Extracting Questions for the Expert, highest-stakes first. Three to seven is a useful range for a complex brief, not a quota. For each:

- The question, specific enough that a correct answer is checkable.
- Why it blocks progress (one line).
- The decision fork: what will be done differently depending on the answer.

**Standing invitations.** Close with explicit permission and instructions to the expert, in words to this effect:

> You have full license to reject this brief's framing. The problem statement, the hypotheses, and the approach are the work of the engineer who got stuck or whose judgment prompted this escalation — the section above marks where that account is least trustworthy. If you believe the real problem is different, say so and answer the questions we should have asked instead. Separately: what should we be asking that we are not?

## 12. Response Contract

Tell the expert what shape of answer is most actionable. Include this block, adapted to the brief:

> Assume there will be no follow-up round. Structure your response as:
>
> 1. Direct answers to each numbered question above, in order.
> 2. Label substantive claims as fact (supported by this brief), inference, or assumption, with confidence (high/medium/low). Where you are uncertain, name the single check that would settle it.
> 3. For any proposed change: the minimal version first. If you believe a larger redesign is warranted, argue it separately with the tradeoff.
> 4. Decisive checks: the fastest tests, commands, or inspections an engineer with repo access should run to confirm your diagnosis or recommendation before adopting it.
> 5. Explicitly flag anything you assumed about code or context not shown in this brief.
