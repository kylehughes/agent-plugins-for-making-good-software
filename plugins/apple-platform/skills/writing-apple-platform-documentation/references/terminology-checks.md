# Terminology checks

When `writing-technical-prose` is installed, its linter can combine generic prose hints with this skill's [terminology rules](../assets/terminology-rules.json). Resolve both paths from the installed skill directories; pass document paths from the working repository:

```sh
python3 /path/to/writing-technical-prose/scripts/lint_technical_writing.py \
  --rules-file /path/to/writing-apple-platform-documentation/assets/terminology-rules.json \
  README.md docs Sources
```

Add `--fail-on-warnings` when warnings should return status `1`. By default, completed checks return `0` even when warnings are found. An unreadable or invalid rules file returns `2`.

The Apple rules flag `APNS`, `IOS`, `MacOS`, `OSX`, `xcode`, and `swiftui` in prose. In Markdown, the linter skips backtick-fenced code and lines starting with `|`. In Swift files, it checks documentation-comment lines. It removes single-backtick code spans in both formats. These checks do not verify availability, API contracts, concurrency behavior, or privacy claims. Review each finding in context before changing it.

Without the Universal skill, use this skill's terminology list and correction table for manual review. No script is required: compare named products with their documented capitalization, then verify caller constraints and compatibility claims against the implementation and deployment settings.
