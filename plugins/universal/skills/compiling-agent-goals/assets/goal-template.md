# Paste-ready single-goal template

Delete bracketed guidance and any unused lines. Count only the body after `/goal`.

```text
/goal
Objective: [One concrete outcome stated as an observable end state.]

Inputs: Read [literal paths/issues/logs] as implementation context. For deciding when to stop, only AC1–AC[n] below define completion.

Scope:
- In: [bounded files/components/behaviors]
- Out: [adjacent work that must not expand this goal]

Done when:
- AC1: [Binary observable result.] Proof: [`exact command` and expected result, or named artifact/inspection.]
- AC2: [Binary observable result.] Proof: [...]
- AC3: [Binary observable result.] Proof: [...]

Baseline and regressions: [Capture relevant pre-change results when practical. Failures introduced or worsened by this work block success; evidenced unrelated pre-existing failures do not.]

Execution rules:
- Keep changes within scope and preserve [named invariants].
- Do not add completion criteria. Record optional discoveries as follow-ups.
- In the final turn, surface each AC's evidence: commands, exit status, concise results, measurements, and artifact paths.

Terminal outcomes:
- SUCCESS: AC1–AC[n] all pass and their evidence is surfaced. Stop immediately even if more improvements are possible.
- BLOCKED: Stop without claiming success if required external input is unavailable, no new evidence or material AC progress occurs for 3 consecutive goal turns, or [10/20/30] turns elapse. Report passed and remaining ACs, evidence, blocker, and the smallest next action.
```
