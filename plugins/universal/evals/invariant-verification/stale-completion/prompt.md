---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 12
timeout_seconds: 180
---

Only the newest refresh may replace the displayed value. Verify this transition invariant and propose a deterministic check. Keep the answer read-only.

```js
class Screen {
  generation = 0;
  value = null;
  async refresh(fetchValue) {
    const request = ++this.generation;
    const result = await fetchValue();
    this.value = result;
  }
}
```
