# Indexlet

Indexlet is a local command-line tool for searching one person's collection of Markdown notes. It builds a disposable index and never edits your notes. It needs no account or background service.

Use Indexlet for literal, case-insensitive searches across Markdown files, including files in nested directories. It is not a shared search service and does not search PDFs or text inside images. Searches are not semantic.

## Getting started

Download the `indexlet` executable from [Releases](releases.md) and place it in a directory on your command path.

To try it, create a directory named `notes` and a Markdown file inside it containing the text `rain garden`. From the directory containing `notes`, run:

```sh
indexlet build ./notes --index ./notes.idx
indexlet find ./notes.idx "rain garden"
```

The index path must be outside the notes directory. Here, `notes.idx` sits beside `notes`.

A successful build ends with `Indexed N notes`, where N is the number of notes found. With the sample note, the search prints the note's relative path and a matching line. A search with no matches prints `No matches`.

A build that reports `Indexed 0 notes` also succeeds, but searches return `No matches`. Check that the collection directory contains Markdown files if you expected notes to be indexed.

## Keep the index current

Search does not refresh the index. After changing your notes, run the build command again:

```sh
indexlet build ./notes --index ./notes.idx
```

There is no automatic refresh.

## Query syntax

Queries match literal text without regard to case. For example, `"rain garden"` searches for those words as written, rather than notes about related ideas. See [query details](docs/query.md) for matching rules and examples.

## Index storage and privacy

The index contains note text and is not encrypted. Putting it in a synced folder copies that text to the sync service. You can keep your notes in a synced folder while storing the index locally, outside the notes directory.

Delete the index to remove the search copy. Deleting it does not delete your notes; you can rebuild it when needed. See [privacy](docs/privacy.md) for index storage and deletion details.

## Development

Read [development](docs/development.md) to build the executable from source.
