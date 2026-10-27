# Indexlet

Indexlet is a local command-line tool for searching one person's collection of Markdown notes. It builds a disposable index and never edits the notes. It needs no account or background service.

## Is it right for your notes?

Use Indexlet to search a directory of Markdown files, including nested directories. Searches are literal and case-insensitive; they do not interpret meaning. Indexlet does not search PDFs or text inside images, and it is not a shared search service.

The index contains note text and is not encrypted. Keep it outside the notes directory. If you put it in a synced folder, that text is copied to the sync service. Your notes can stay in a synced folder while the index stays local.

## Getting started

Download the `indexlet` executable from [Releases](releases.md) and place it in a directory on your command path.

To try it, create a directory named `notes` and put a Markdown file inside it containing the words `rain garden`. From the directory containing `notes`, run:

```sh
indexlet build ./notes --index ./notes.idx
```

The index path must be outside the notes directory. Here, `notes.idx` sits beside `notes`. Choose a local, unsynced location for this example if you want to keep the index off your sync service.

A successful build ends with `Indexed N notes`, where N is the number of Markdown notes found. For a collection containing only the test note, expect `Indexed 1 notes`.

Search the index:

```sh
indexlet find ./notes.idx "rain garden"
```

The result includes the matching note's relative path and a matching line. A search with no matches prints `No matches`.

A build that reports `Indexed 0 notes` also succeeded, but it found no Markdown notes, so searches return `No matches`. Check that the collection contains Markdown files if you expected results.

## Keep the index current

Search does not refresh the index, and there is no automatic refresh. After changing your notes, rebuild it:

```sh
indexlet build ./notes --index ./notes.idx
```

Deleting the index removes the search copy without deleting your notes. Read [index storage and deletion](docs/privacy.md) for privacy details.

## Query syntax

Queries match literal text without regard to case. For example, `"rain garden"` searches for those words as literal text, rather than related ideas. Read [query details](docs/query.md) for matching rules and more examples.

## Development

Read [development](docs/development.md) to build the executable from source.
