# Brief template

The required contents of each section of an escalation brief. Use this structure unless the user requests a different format. Every section assumes the reader has no repository access, no prior conversation, and no ability to run commands.

## 1. Executive Summary

One short paragraph with:

- Desired outcome.
- Current blocker.
- Most important evidence.
- Current best hypothesis, if any.

## 2. Problem Statement

Explain the intended behavior and why the current behavior is wrong. Include expected vs. actual behavior.

## 3. Project Context

Describe only the context needed to reason about the issue, but make it complete enough for a reader with no repository access:

- Language, framework, platform, runtime, package manager, and relevant versions if known.
- Architecture, module boundaries, data flow, lifecycle, external services, database/schema, generated code, or build/test setup.
- Any project conventions that constrain a fix.

## 4. Current Failure

Provide exact symptoms and reproduction information:

- Steps to reproduce.
- Command(s) run, inputs used, or user action taken.
- Failing test(s), assertion(s), stack trace(s), logs, UI state, screenshots, or CI link summaries.
- Whether the failure is deterministic, intermittent, local-only, CI-only, device-specific, environment-specific, or data-dependent.

If reproduction is unknown, give the best-known trigger and label gaps clearly.

## 5. Relevant Evidence

List the relevant artifacts and why each matters. Use file and line references when possible, then embed the relevant contents directly.

Include:

- Source files, functions, types, components, routes, jobs, migrations, schemas, fixtures, generated files, or configs, with the needed snippets quoted inline.
- Minimal but sufficient snippets from each relevant artifact.
- Runtime/config/dependency details that materially affect the failure.
- Any contradictory or surprising evidence.

## 6. Attempts So Far

For each meaningful attempt, include:

- What changed or was tested.
- Why it seemed plausible.
- Result observed.
- Why it did not solve the problem or what uncertainty remains.

Separate attempted fixes from passive observations. Do not include trivial or duplicate attempts unless they prevent rework.

## 7. Constraints and Non-Goals

Capture:

- User requirements and acceptance criteria.
- Compatibility requirements, dependency restrictions, API contracts, performance limits, security/privacy requirements, release deadlines, and migration constraints.
- Codebase conventions and architectural boundaries.
- Things the expert should avoid changing.

## 8. Facts vs. Hypotheses

Use two subsections.

**Confirmed facts**

- Bullet only directly supported facts.

**Ranked hypotheses**

For each hypothesis, include:

- Plausibility: high / medium / low.
- Why it fits.
- Evidence against it or missing evidence.
- Fastest decisive test or inspection.

## 9. Missing Information

List missing artifacts that would materially improve diagnosis, such as logs, repro data, failing command output, env vars, dependency versions, screenshots, schema state, CI artifact, or relevant file contents.

Only include items that matter. Do not turn this into a generic questionnaire.

If a needed artifact exists but cannot be included safely or was not inspected, list it here with the precise reason. Do not assume the expert can fetch it.

## 10. What Would Prove It Fixed

Name exact verification criteria:

- Test command(s), test names, manual checks, expected logs, screenshots, metrics, or acceptance criteria.
- Regression checks that should stay green.
- Edge cases that should be covered.

## 11. Expert Ask

End with a direct request. Be specific about what help is needed, for example:

- Diagnose the likely root cause.
- Propose the minimal safe patch.
- Identify the missing invariant or architectural mismatch.
- Design a focused test plan.
- Review whether a proposed fix violates project constraints.
