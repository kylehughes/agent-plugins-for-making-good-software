# Blinded editorial comparison of development cases 01–06

This is an editorial comparison against the frozen development sources and evaluator keys. I saw those sources and keys before the outputs, so I am not a naive reader. I read only outputs 01–06 A/B, not run.json or held-out packet/key contents. Arm identities remain unknown. Labels below describe document support and predicted task risks, not observed reader success, confidence, timing, or comprehension. No human or independent model-reader trials were conducted. Each arm generated one six-case batch; cases are not independent production trials. No composite or pooled score is calculated.

Line locations refer to evals/document-design/runs/2026-10-27/<case>-<label>.md. Word counts are whitespace-delimited counts of raw output, including Markdown. Review/no-change responses are commentary; their delivered reader artifacts remain the original source documents.

## Case 01: adoption README

Authorized completion: complete for both. Both return a full README, preserve Query syntax and all four supplied link destinations, and perform no installation. A has 335 words; B has 362. Neither invents platform support, package-manager commands, semantic search, encryption, or refresh behavior.

| Key task path | A | B |
| --- | --- | --- |
| Adoption at top | Supported: lines 3–5 identify local single-person Markdown use and explicitly exclude a shared service, PDFs, and image text. | Supported: lines 3–5 provide the same distinctions and literal matching. |
| First successful match | Supported: lines 9–25 provide installation, a Markdown sample containing the phrase, build/find commands, successful count, and expected path/line. Lines 3 and 27 distinguish unchanged notes from an empty but successful build. | Supported: lines 9–25 supply the sample, working directory, commands, count, and matching path/line. Line 3 preserves nonmutation. |
| Edited note, direct Query syntax entry | Supported with a short onward scan: lines 29–41 retain the anchor, immediately followed by a rebuild section and no-automatic-refresh statement. Outside-notes constraint is at line 11, so retrieving that placement requirement requires looking back. | Supported: lines 27–39 retain the anchor and immediately follow with rebuild behavior, command, no automatic refresh, and the outside-notes condition. |
| First storage-path choice | Concern: line 11 tells the reader to build outside the notes directory, but the unencrypted-text and sync-copy conditions do not appear until line 45, after the first build. A reader following setup before reading later sections could create a synced index before seeing the consequence. This is a predicted sequencing defect, not an observed disclosure. | Supported: line 11 places unencrypted text and sync-copy conditions at index selection, before the build, and permits synced notes with a local index. Line 43 covers deletion without deleting notes. |

Minimal remedy for A: move or repeat the short sync/privacy condition beside step 3; retain the fuller privacy account. B's 27 extra words include useful explicit working-directory and local-condition detail rather than a new factual claim. Both make supplied facts explicit and add supported explanatory connections. B has a local sequencing advantage for the storage task; no reader improvement has been measured.

## Case 02: search explanation

Authorized completion: complete for both. Both deliver a short explanation without operator commands. A has 338 words; B has 291. B's continuous paragraphs and A's two internal headings are both acceptable; no outline preference determines the judgment.

| Key task path | A | B |
| --- | --- | --- |
| Closed request missing from search | Supported: lines 3–5 establish stored record versus search, and line 11 explains the open-only filter, retained closed record, Include closed limitation, and link/number check. | Supported: lines 3–7 establish lag and the filter/closure distinction; line 11 gives the authoritative permitted-record check. |
| Search result, Request not found, browser refresh | Supported: line 9 denies forced refresh; line 13 explains temporary stale deletion results and indistinguishable permission failure. | Supported: lines 5 and 9 provide the same limitations and permission ambiguity. |
| Three-minute discrepancy and help | Supported: line 3 preserves normal versus maximum delay; line 17 gives request number and observed times, private-content exclusion, service-desk role, and no recovery promise. | Supported: lines 5 and 13 give the same limits and escalation information. |
| Authority at load time | Supported: line 5 explicitly qualifies current values by access and load time, allowing later edits. | Supported: line 11 qualifies page status by access and load time, allowing later edits. |

Both preserve the source's conditions and make the lag-to-symptom relationship explicit. A adds a supported newly-created-but-not-yet-visible example at line 11; B explicitly includes closure and deletion in the lag model at line 3. These are supported applications, not new product guarantees. No material drift or organizational defect found. Editorial tie on required task support; A's headings may help scanning and B is 47 words shorter, but neither advantage is measured here.

## Case 03: digest procedure

Authorized completion: complete for both. Both return rewritten procedures and perform no operations. A has 369 words; B has 357. Both preserve commander authority, no catch-up behavior, no manual-send scope, exact success states, and UTC scheduling.

| Key task path | A | B |
| --- | --- | --- |
| Direct pause entry with Running job | Concern: the complete top-to-bottom route is supported by lines 3–16, including ID and Running branch. However, the independently named Pause and confirm section begins at line 18 with Select Pause at line 20. Direct arrival there bypasses the earlier ID/job-state checks; no link or instruction requires completing them first. This is a plausible direct-entry route left open by the artifact, not an observed operator error. | Supported: the Pause section itself begins with ticket and numeric-ID checks at line 9, then the Running/escalation branch at lines 10–13 before the control at line 14. |
| Eligible Pending pause and proof | Supported on the sequential route: lines 9–24 cover correct ID, Pending, ticket/confirmation, Schedule/Paused, recording, and stop/escalation. The direct-entry caveat above remains. | Supported: lines 9–16 include the whole prerequisite/action/verification/stopping route within one section. |
| Direct resume without approval | Supported: line 28 puts approval before actions; lines 30–35 recheck ID, verify Active/next UTC time, record, stop on failure, and deny catch-up. Line 35 places the catch-up reminder after the action, but the approval barrier prevents the stated unapproved action and the top line 5 already explains behavior. | Supported: line 20 gives approval and no-catch-up before actions; lines 22–25 supply ID, controls, verification, recording, and stop/escalation. |
| Completed or Failed, prevent next run | Supported: line 16 distinguishes irreversible current job from next scheduled job. | Supported: line 13 provides the same distinction. |

Minimal remedy for A: at the start of Pause and confirm, require the ticket, numeric-ID match and job-state decision, with an explicit link to Decide whether to pause; alternatively merge those sections. No wholesale duplication is needed. B consolidates those dependencies at the action entry and is 12 words shorter. B has a predicted direct-entry advantage; no actual operator outcome was tested. The fictional tool behavior itself is preserved in both.

## Case 04: retention-code review control

Authorized completion: complete for both. A's 40-word and B's 39-word responses accept the existing reference, provide a brief source-grounded reason, and do not rewrite or add a tutorial. The reader artifact is the unchanged starting retention-codes.md in both arms.

| Key task path | A and B |
| --- | --- |
| Review today, Expire under hold, removing hold | Supported by the unchanged code table and following hold paragraph: Review never automatically deletes; active holds block deletion; removal triggers next daily evaluation, not immediate deletion. |
| Access, change permissions, policy and date zone | Supported by the unchanged introduction/policy link, time-zone paragraph, and final permissions paragraph. Neither response asserts that codes change access or that all items delete on the next run. |
| Review restraint | Supported by A line 1 and B line 1: both explicitly say no changes are needed and avoid false-positive defects. |

No drift or unnecessary growth. Editorial tie and successful positive-control restraint. This says nothing about measured reader lookup speed.

## Case 05: Finch page set

Authorized completion: complete for both. Both return index.md, publish.md and restore.md with the supplied Publish, Preview and Restore headings and usable cross-links. No operations occur. A has 556 words; B has 609. Filenames are presented as separators around complete page contents; they are not intended extra headings within each file.

| Key task path | A | B |
| --- | --- | --- |
| Direct publish anchor | Supported for access, save, title/date/body check, publish, Current and signed-out verification at lines 21–27. Concern for the private-preview distinction on this exact arrival: the explicit signed-in/never-public condition appears only in the later Preview section at line 35, while the action at line 24 merely says Open Preview. A reader can retrieve it by scanning onward, but it is not at the decision/action entry and the Publish section contains no Preview link. This is a local-context cost, not a false publication instruction; the signed-out public check remains explicit. | Supported: lines 21–29 include the draft/public distinction, Publisher access, save completion, and private-preview condition at line 26 before Publish, followed by Current and signed-out verification. |
| Direct restore, keep draft, make edition public | Supported: lines 45–54 put access, copy-to-draft-only semantics, no undo/history, backup, ID/edition checks and Preview before the explicit link to normal publishing. Line 54 repeats the save/check/public-result sequence. | Supported: lines 47–57 provide the same conditions, a local warning before Restore and an explicit publishing route. Line 56 locally distinguishes private Preview from public address. |
| Publication failure and repeated Publish | Supported: line 29 preserves existing edition, draft, article ID/error escalation and Current check before further action. | Supported: line 31 supplies the same behavior and stopping guidance. |
| Index orientation and task choice | Supported: lines 5–11 connect draft, public editions, saving/previewing and task links; new articles have no editions. No in-tool approval workflow at line 21. | Supported: lines 5–13 establish the same model and task routes, including no in-tool approval workflow directly on index. |

A's local-preview gap can be remedied by adding a short condition to step 2 or linking explicitly to Preview; no new product fact is required. B's 53 extra words buy more repeated local context at publish/restore/preview arrivals; this is useful repetition under the keys rather than automatic evidence of overlength. Both add supplied facts to repair severely incomplete starting pages. Both also make the supported restore-then-publish dependency explicit. A adds the sensible supported instruction to save/recheck after further edits at line 24; it does not invent undo or approval behavior. No fabricated guarantees found. B offers more immediate direct-entry support for the private-preview distinction; an actual navigation/comprehension difference remains untested.

## Case 06: short-guide control

Authorized completion: complete for both. A returns 26 words and B 31; both explicitly leave the document unchanged. The delivered reader artifact is the original guest-scan-session.md.

| Key task path | A and B |
| --- | --- |
| First arrival, correct session and failures | Supported by original paragraphs 1–2: email/drive, reception badge, Reading Room signs and booked access, six-digit code, name/time verification, reception failure path, wrong-name sign-out/no scanning. |
| Direct departure at final paragraph | Supported by original paragraph 3: only Guest scans, copy to own drive before End session, ending signs out and clears the folder. |
| Scope and restraint | Supported by both line-1 responses: neither rewrites, invents transfer methods, expands into reservations/admin work, or adds scan instruction. |

Editorial tie and successful no-change control. Neither response claims a measured reader result.

## Findings and evidence limits

The material editorial concerns are placement of the sync-copy condition in 01-A, the bypassable pause prerequisites in 03-A, and the weaker local private-preview explanation in 05-A. Each artifact retains the relevant underlying facts somewhere; the concerns distinguish access/sequence from factual correctness. The strongest operational concern is 03-A because a directly reachable action section omits an unavoidable route through identity and Running-state checks. No observed user harm or task failure is asserted.

Cases 02, 04 and 06 are editorial ties on required task support. Both no-change/review controls preserve mode. All twelve outputs deliver their requested artifact or acceptance response, with no external action and no concrete fabricated product guarantee identified. The comparison does not pool cases or infer arm identity from labels. Reading sources/keys, use of one batch per arm, one producer configuration, absence of independent readers, and lack of measured routes/timing limit conclusions to these documents and predicted editorial risks. These results do not validate general human benefit or isolate any particular internal skill stage.
