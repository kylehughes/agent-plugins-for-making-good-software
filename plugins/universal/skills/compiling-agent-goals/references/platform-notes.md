# Platform notes

Checked against official documentation on 2026-08-10. Goal and skill behavior is evolving; re-check the linked pages when platform versions change.

## Cross-harness rules

The safest contract for both Claude Code and Codex is:

1. Keep the complete, finite closure set inline in the goal.
2. Use referenced files as execution context, not as an unbounded definition of “done.”
3. Name one outcome, fixed acceptance criteria, exact proof, meaningful constraints, and explicit stop states.
4. Require decisive command results and artifact evidence to be surfaced in the conversation.
5. Add a turn/no-progress escape clause.
6. Keep the body at or below 4,000 characters; target 3,000 or fewer as this skill's conservative headroom heuristic.

Codex documentation permits putting longer instructions in a file and pointing the goal at it. That is useful for implementation context, but a pointer-only completion condition is not portable: Claude Code's evaluator cannot independently read the file, and a large document often has no finite closure boundary. Keep the spec external and the closure contract inline.

The 3,000-character target, 3-turn stagnation rule, and 10/20/30-turn caps in this skill are conservative authoring defaults, not documented platform limits. The only shared hard length limit currently documented is 4,000 characters.

## Claude Code `/goal`

Current documented behavior:

- Requires Claude Code 2.1.139 or newer.
- One goal can be active per session; setting a new one replaces the old one.
- Setting a goal immediately starts a turn with the condition as the directive.
- A separate small, fast model evaluates the condition after each turn.
- The evaluator receives the condition and conversation. It does not run commands or read files independently.
- Effective conditions have one measurable end state, a stated check, and constraints that must hold.
- The condition limit is 4,000 characters.
- Anthropic explicitly recommends a turn or time clause to bound the run.
- A goal does not change tool permissions; unattended work may also require auto mode.
- An active goal is restored when its session is resumed, but the turn, time, and token counters reset.
- A Stop hook is preferable when completion must be decided by deterministic custom logic rather than a model reading the transcript.

Practical implication: make the worker print the exact test/build/inspection evidence in its final turn. “The file now contains X” is weaker than a surfaced command or bounded inspection result. Claude Code records a condition as achieved when its evaluator answers yes; it does not document a separate blocked state, so a terminal BLOCKED branch must be labeled in the transcript.

Official source: <https://code.claude.com/docs/en/goal>

## Codex `/goal`

Current documented behavior:

- `/goal <objective>` attaches a durable objective to the active chat.
- `/goal`, `/goal edit`, `/goal pause`, `/goal resume`, and `/goal clear` inspect or control it.
- Goal objectives must be non-empty and no more than 4,000 characters.
- The goals feature may need to be enabled through `features.goals` or `codex features enable goals`.
- OpenAI recommends work bigger than one prompt but smaller than an open-ended backlog.
- A good goal defines what to achieve, what not to change, how to validate progress, and when to stop.
- OpenAI recommends one objective and one stopping condition, initial source files or plans, proof commands or artifacts, checkpoints, and a short progress log.
- Loose lists of unrelated work are poor goal candidates.

Practical implication: a `PLAN.md` or spec can guide implementation, but the goal should freeze the subset of outcomes that closes this particular run. For a large plan, create sequential goal contracts rather than one “implement the plan completely” loop.

Official sources:

- <https://learn.chatgpt.com/use-cases/follow-goals>
- <https://learn.chatgpt.com/docs/developer-commands?surface=cli>

## Agent Skill packaging

The skill follows the open Agent Skills directory format:

```text
compiling-agent-goals/
├── SKILL.md
├── agents/openai.yaml
├── assets/
├── references/
└── scripts/
```

SKILL.md stays under the recommended 500-line/5,000-token ceiling, while detailed material is loaded progressively from one-level-deep references.

This copy ships inside the `universal` plugin of the `making-good-software` marketplace, so installing the plugin is the only install step. Claude Code invokes it as `/universal:compiling-agent-goals` and Codex as `$universal:compiling-agent-goals`; both may also select it implicitly from its description. A standalone copy dropped into `~/.claude/skills/`, `.claude/skills/`, `~/.agents/skills/`, or `.agents/skills/` works the same way, minus the plugin prefix.

Official sources:

- <https://agentskills.io/specification>
- <https://agentskills.io/skill-creation/best-practices>
- <https://code.claude.com/docs/en/skills>
- <https://learn.chatgpt.com/docs/build-skills>
