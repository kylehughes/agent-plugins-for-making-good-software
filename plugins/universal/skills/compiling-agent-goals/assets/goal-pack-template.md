# Goal-pack template

Use when the source cannot form one finite contract. Keep prerequisites and rationale outside paste-ready bodies unless they affect execution.

```text
Assessment: goal pack ([N])
Split rationale: [One sentence naming the independent milestones or risk boundaries.]

Goal 1 — [demonstrable milestone]
Prerequisites: [none or explicit artifact/state]
/goal
Objective: [...]
Inputs: Read [...] as implementation context. Only AC1–AC[n] below define completion.
Scope: In: [...]. Out: [...].
Done when:
- AC1: [...] Proof: [...]
- AC2: [...] Proof: [...]
Baseline and regressions: [...]
Execution rules: Keep scope fixed; surface decisive evidence; record optional discoveries without adding criteria.
Terminal outcomes:
- SUCCESS: all listed ACs pass with surfaced evidence; stop.
- BLOCKED: stop after unavailable external input, 3 no-progress turns, or [cap] turns; report state and smallest next action without claiming success.
Characters: [N] / 4000

Goal 2 — [next independently verifiable milestone]
Prerequisites: Goal 1 SUCCESS and [artifact/state]
/goal
[Repeat the finite contract. Do not duplicate Goal 1 criteria or reopen its scope except for explicit integration regressions.]
Characters: [N] / 4000
```

Recommended split order when applicable:

1. Establish or migrate a testable foundation.
2. Deliver a vertical behavior slice.
3. Complete remaining bounded variants or data migration.
4. Validate integration, compatibility, and release readiness.

Do not create a final “polish everything” goal.
