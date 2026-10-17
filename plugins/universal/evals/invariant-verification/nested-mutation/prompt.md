---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 12
timeout_seconds: 180
---

Our rule is that a confirmed batch always contains at least one item. Verify whether this representation makes an empty confirmed batch impossible. Assess it without editing anything.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfirmedBatch:
    items: list[str]

    def __post_init__(self):
        if not self.items:
            raise ValueError("empty batch")

items = ["one"]
batch = ConfirmedBatch(items)
items.clear()
```
