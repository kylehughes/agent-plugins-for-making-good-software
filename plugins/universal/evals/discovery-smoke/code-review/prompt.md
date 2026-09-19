---
allowed_tools: [Read, Glob, Grep, Skill]
max_turns: 10
timeout_seconds: 180
---

Review this JavaScript function for the contract "return the user with this id, or null when none matches." Work read-only: report the finding, explain a likely failure, and suggest a focused fix without editing files.

```js
function findUser(users, id) {
  return users.find(user => user.id = id) ?? null;
}

console.log(findUser([{ id: 1, name: "Ada" }], 2));
```
