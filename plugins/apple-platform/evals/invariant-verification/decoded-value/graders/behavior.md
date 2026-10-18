---
type: llm
weight: 1
---

Require all of the following; judge the full diagnosis and every proposed fix:

- Identify synthesized decoding as a route around the failable initializer and give a syntactically valid keyed payload that reaches the invalid value.
- Distinguish immutable stored state from validation of decoded input. Swift cannot prove positivity of arbitrary external bytes before runtime validation.
- Preserve the established keyed representation in any proposed implementation. A single-value/scalar decoder paired with synthesized keyed encoding fails this case, even if the diagnosis was correct. Omitting implementation code is acceptable in this read-only assessment if the proposed change is precise and preserves the format.
- Propose focused checks covering a valid historical keyed payload, invalid zero or negative input at the decoding boundary, and compatible encoding/decoding. Invalid JSON that fails before the intended predicate is not a useful negative control.
- State what those checks support and their limits without claiming execution that the trace does not show.
- Keep the assessment read-only and avoid unsolicited registries, CI changes, or proof-tool installation.

Award full credit only if every applicable requirement holds. Mentioning Codable, decoding, or synthesis alone is not evidence of a correct answer. Skill composition is scored separately from behavioral correctness.
