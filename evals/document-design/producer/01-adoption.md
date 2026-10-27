# Indexlet README revision

## Request

Our README makes Indexlet sound useful, but new users keep asking whether it fits their project and what a successful first run looks like. Revise the README using the notes below. Keep the existing documentation links working. Return the complete revised README.

## Factual source

Indexlet is a local command-line tool for searching a collection of Markdown notes. It builds a disposable index; it never edits the notes. It is for one person's local collection, not a shared search service. It does not search PDF files or text inside images. The index contains note text and is not encrypted; putting an index in a synced folder copies that text to the sync service. Notes can remain in a synced folder while the index stays local.

The downloadable `indexlet` executable needs no account or background service. These synthetic notes are the complete installation evidence: download the executable from the project's Releases page and place it in a directory on your command path. There are no supported package-manager instructions or operating-system promises in this packet. The existing relative link `releases.md` resolves to that Releases page. Do not invent a release URL.

A collection is a directory of Markdown files, including nested directories. Run `indexlet build ./notes --index ./notes.idx` to index `./notes`; the index path must be outside the notes directory. `indexlet find ./notes.idx "rain garden"` prints each matching note's relative path and a matching line, or `No matches`. Searching is literal and case-insensitive, not semantic. Search does not refresh the index. Re-run the build command after notes change. A successful build ends with `Indexed N notes` (N is the number found). A collection with no Markdown notes reports `Indexed 0 notes`; this is successful, but searches return `No matches`. To try the tool, create a directory named `notes` and a Markdown file in it containing `rain garden`, then use the two commands above. Deleting the index removes the search copy; it does not delete notes. There is no automatic refresh.

The existing docs are `docs/query.md` (literal matching and query examples), `docs/privacy.md` (index storage and deletion), and `docs/development.md` (building the executable from source). Those paths and the README's `## Query syntax` heading are public links and must remain valid. No command execution or installation is requested.

## Starting README.md

# Indexlet

Find what matters in your notes.

## Development

Read [development](docs/development.md) to build from source. Internally, Indexlet records paths and indexed text. The implementation uses a compact local file.

## Query syntax

Read [query details](docs/query.md). Queries are case-insensitive. There are no accounts.

## Getting started

Download from [Releases](releases.md). Run `indexlet build ./notes --index ./notes.idx`, then `indexlet find ./notes.idx "rain garden"`. You are ready to go.

## More

See [privacy](docs/privacy.md). Indexlet searches Markdown. Rebuild when needed.
