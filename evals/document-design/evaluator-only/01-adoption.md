# Evaluator key: 01-adoption

Development. Keep this file out of producer context. Grade the document against the source, not against a preferred outline.

## Reader trials and answers

Use two fresh readers; give each the produced README, not the factual source or this key.

1. **Adoption / first entry.** Reader has a collection of Markdown and PDF notes, wants shared team search, and asks whether Indexlet suits that need. Start at README top. Correct answer: Markdown only, local single-person tool; no shared service, PDFs, or image text. It may serve the local Markdown subset, not the whole stated need. A vague 'searches notes' claim is insufficient.
2. **First success / first entry.** Reader has the executable on their command path and an empty working directory. Ask how to demonstrate a match, how to know indexing succeeded, and what changes their original notes. Correct answer: create `notes` and a Markdown file containing `rain garden`; build with `indexlet build ./notes --index ./notes.idx`; success is `Indexed N notes` with N at least 1 for the demonstration; find with `indexlet find ./notes.idx "rain garden"`; expect path and matching line. Neither command edits notes. An empty build may succeed but does not demonstrate a match.
3. **Stale results / direct entry.** Start at retained `Query syntax` heading. Reader edited a note after building, refreshes their query, and cannot find the new phrase. Correct answer: rebuild the index, then search; no automatic refresh. The index belongs outside the notes directory. The answer may follow a local link to a nearby setup/update section.
4. **Storage choice.** Reader wants the notes synced but does not want a second copy of their text sent to the sync service. Correct answer: keep index local outside synced storage; notes may remain synced. Index is unencrypted text-bearing data. Deleting it does not delete notes. This condition must be discoverable before or alongside the first storage-path choice, not solely in an unexplained privacy link.

## Context, inference, and acceptable forms

Readers know how to create a text file and run a shell command; they do not know Indexlet. Installation can remain a short download-and-command-path instruction; do not penalize absence of unsupported package-manager commands. Numbered steps, short prose, or a compact example are all valid. The exact initial file name is open. No performance, platform, or semantic-search claims can be inferred. Source-build detail can remain linked.

## Preservation and completion

Full README is authorized and required. Preserve all four supplied link destinations and the `Query syntax` heading anchor. Existing maintainer guidance may move later. No external installations or command execution are needed. Fail completion separately if only advice is returned; do not score that as an organizational failure. Penalize a large tutorial or invented setup dependency under proportionality, even if the commands remain correct.

## Decisive evidence

Record locations for fit, first verifiable success, refresh dependency, and storage constraint. A high score requires these relations to be findable; counting headings or presence of the terms alone does not establish success.
