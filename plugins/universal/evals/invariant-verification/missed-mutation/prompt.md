---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 12
timeout_seconds: 180
---

We require every imported quantity to be positive. The original suite passes. In a temporary copy we removed the import validation, and the same suite still passes; its fixtures all contain positive quantities. What does this evidence establish about the invariant and the checks? Keep the review read-only.
