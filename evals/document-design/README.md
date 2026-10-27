# Document-design evaluation

Eight synthetic packets compare competent existing writing guidance with that same guidance plus `designing-documents`. The question is whether the added skill improves a reader's ability to understand, decide, act, and find related information without creating needless structure or exceeding the requested work.

Use [the protocol](protocol.md) before running or judging outputs. [The manifest](manifest.json) identifies splits, file hashes, and freeze status. Only the selected file under `producer/` belongs in a producer's task context. Evaluator-only files must stay outside producer workspaces and prompts. These materials are not skill references or automatically loaded guidance.

| ID | Job | Split |
| --- | --- | --- |
| 01-adoption | Revise an adoption README | Development |
| 02-concept | Create a concept explanation | Development |
| 03-procedure | Revise an operational procedure | Development |
| 04-reference | Review an adequate reference without rewriting | Development control |
| 05-docset | Revise a documentation set for direct entry | Development |
| 06-short-guide | Leave a good short guide unchanged | Development control |
| 07-decision | Create a nonsoftware decision paper | Held out |
| 08-conflicting | Revise structure with incomplete, conflicting evidence | Held out |

For a small first development run, use 01, 03, 05, and 06: they cover adoption, action conditions, cross-document relationships, and restraint. Add 02 and 04 before making claims about explanation or review behavior. Run both arms for every selected packet. Do not tune on 07 or 08. All subjects and product behavior are fictional; no browsing or product installation is required.

The frozen packets include complete factual evidence for the requested work. A few facts are deliberately unresolved in 08; its complete evidence consists of the disagreement and the known limits, not a secretly preferred product behavior. No packet prescribes an output template.

## Recorded comparisons

[27 October 2026 development comparison](runs/2026-10-27/results.md) records paired outputs, editorial findings, repeats, and repository/loading checks. It includes no human or naive model-reader trials; the held-out cases remain unrun.
