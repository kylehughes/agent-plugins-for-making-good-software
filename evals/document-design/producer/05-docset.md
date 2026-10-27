# Make the Finch publishing docs usable from a link

## Request

Revise these three Finch help pages. New editors get sent straight to the publishing page, and people restoring an older edition often arrive from a search result. They should be able to finish their job from there. Keep the existing file paths and section links working. Return all three complete pages, with their file names.

## Factual source

Finch is a small organization's public-news publishing tool. An article has one editable draft and a sequence of numbered published editions. A new article starts with a draft and no published edition. Saving changes only the draft. Preview shows that draft to signed-in editors; it is never the public address. Publish creates a new numbered edition from the saved draft and makes it public at the article's permanent address. An existing public edition stays visible until a new one is published. Only an editor with Publisher access can Publish or Restore. Other editors can save and preview.

Before publishing, confirm the article title, date, and body in Preview. Save must complete first; unsaved edits are not in Preview or a published edition. No approval workflow exists in Finch; any required organizational approval is outside the tool. Once Publish succeeds, the Editions panel marks the new edition Current and provides the permanent public address. Open that address in a signed-out browser to check the public result. If Publish fails, the current public edition stays as it was; keep the draft and contact the help desk with article ID and error text. Do not repeatedly Publish to fix an unclear result; check Current first.

Restore in the Editions panel copies a selected older published edition into the editable draft. It does not change the public article or create an edition. Restore replaces the current draft; save a copy of draft text outside Finch first if it must be kept. There is no draft history or undo for Restore. Before Restore, verify article ID and selected edition number. After Restore, Preview and check the restored draft. Use the normal publishing steps if you want it public. Restore cannot be used on a new article with no editions. Choosing Restore requires Publisher access even though ordinary editors can edit drafts. The only supplied related pages are the three below. All facts needed to revise them are here.

## Starting index.md

# Finch help

Finch keeps drafts and editions.

- [Publish](publish.md#publish)
- [Restore](restore.md#restore)

## Starting publish.md

# Publishing

## Publish

Check your work, then select Publish. Open the link to see it. If it failed, contact the help desk.

## Preview

Preview is useful before publishing. Finch has a permanent public address for each article.

## Starting restore.md

# Older editions

## Restore

Choose an edition in Editions and select Restore. Your article is back to that edition. See [Publish](publish.md#publish) if needed.
