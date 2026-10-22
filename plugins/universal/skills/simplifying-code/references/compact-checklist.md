# Compact Checklist

Before finalizing, confirm:

- The review surface included staged, unstaged, and relevant untracked files.
- Existing utilities and adjacent patterns were searched before keeping new code.
- Behavior, compatibility, public API, persistence, localization, accessibility, analytics, and security semantics were preserved.
- Redundant state, duplicate logic, wrapper code, unused imports, dead code, no-op updates, and hot-path waste were removed where safe.
- Concurrency, lifecycle, cancellation, resource ownership, and cleanup remain correct.
- Platform compatibility checks are precise and fallbacks remain for declared minimum versions.
- Generated/vendor/build artifacts were not hand-edited.
- The cheapest relevant verification was run or a specific blocker was reported.
