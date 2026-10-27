# Indexlet

Search one person's local collection of Markdown notes from the command line. Indexlet builds a disposable index and never edits your notes. It needs no account or background service.

## Is Indexlet a fit?

Use Indexlet for literal, case-insensitive searches across a directory of Markdown files, including nested directories. It does not provide semantic search, search PDF files or text inside images, or act as a shared search service.

Searches use a snapshot of your notes. After notes change, rebuild the index; searching does not refresh it automatically.

## Install

Download the `indexlet` executable from [Releases](releases.md) and place it in a directory on your command path.

## Try a first search

Create a directory named `notes` and a Markdown file inside it containing the text `rain garden`.

Choose an index path outside the notes directory. The index contains note text and is not encrypted. Keep it outside synced folders if you do not want that text copied to a sync service. Your notes can stay in a synced folder while the index stays local.

From the directory containing `notes`, build the index:

```sh
indexlet build ./notes --index ./notes.idx
```

A successful build ends with `Indexed N notes`, where `N` is the number of notes found. If your sample is the only note, expect `Indexed 1 notes`.

Search it:

```sh
indexlet find ./notes.idx "rain garden"
```

Each match prints the note's relative path and a matching line. For the sample, expect the path of your Markdown file and the line containing `rain garden`. A search with no matches prints `No matches`.

`Indexed 0 notes` is also a successful build, but the collection has no Markdown notes to search. Check that your sample file is a Markdown file inside `notes`, then rebuild.

## Query syntax

Search is literal and case-insensitive. For example, `"rain garden"` searches for that text rather than related ideas. See [query details](docs/query.md) for matching rules and more examples.

Search does not refresh the index. After changing notes, rerun the build command before searching:

```sh
indexlet build ./notes --index ./notes.idx
indexlet find ./notes.idx "rain garden"
```

The index path must remain outside the notes directory.

## Index storage and deletion

The index is a disposable, unencrypted copy of note text. Placing it in a synced folder copies that text to the sync service, even if the original notes are elsewhere. Delete the index to remove the search copy; deleting it does not delete your notes. See [privacy](docs/privacy.md) for storage and deletion details.

## Development

Read [development](docs/development.md) to build the executable from source.
