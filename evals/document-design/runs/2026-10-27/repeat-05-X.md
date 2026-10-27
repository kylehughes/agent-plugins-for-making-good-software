File: `index.md`

```markdown
# Finch help

Finch publishes public-news articles. Each article has one editable draft and a sequence of numbered published editions. A new article starts with a draft and no published edition.

Saving changes only the draft. Preview shows the saved draft to signed-in editors; it is never the public address. Publishing creates a new numbered edition from the saved draft and makes it public at the article's permanent address. An existing public edition stays visible until another edition is published.

- [Publish an article](publish.md#publish): save, check Preview, publish, and verify the public result.
- [Restore an older edition](restore.md#restore): replace the draft with an older published edition, then decide whether to publish it.

All editors can save and preview. Only editors with Publisher access can Publish or Restore. Finch has no approval workflow; any required organizational approval happens outside the tool.
```

File: `publish.md`

```markdown
# Publishing

## Publish

Publish creates a new numbered edition from an article's saved draft and makes it public at the article's permanent address. It requires Publisher access. Other editors can save and preview.

A new article has no published edition until you publish it. For an article already published, the current public edition stays visible while you edit the draft.

1. Complete any required organizational approval outside Finch. Finch has no approval workflow.
2. Save your draft and wait for Save to complete. Unsaved edits are not included in Preview or the published edition.
3. Open Preview and confirm the article title, date, and body. Preview is visible only to signed-in editors; it is never the public address. If you make corrections, save and check Preview again.
4. Select Publish.
5. In the Editions panel, confirm that the new edition is marked Current. Use the permanent public address provided there and open it in a signed-out browser to check the public result.

If Publish fails, the current public edition stays as it was. Keep the draft and contact the help desk with the article ID and error text. If the result is unclear, check Current in Editions first; do not repeatedly Publish to try to fix it.

## Preview

Preview shows the saved draft to signed-in editors. It does not show unsaved edits and is never the public address. All editors can save and preview; Publisher access is required to publish.

Save and wait for completion before opening Preview. Confirm the title, date, and body. If anything needs changing, edit the draft, save, and preview again.

To make the checked draft public, follow [Publish](#publish). To bring an older published edition into the draft, see [Restore](restore.md#restore).
```

File: `restore.md`

```markdown
# Older editions

## Restore

Restore copies an older published edition into the article's editable draft. It does not change the public article or create an edition. The current public edition stays visible until you publish a new one.

Restore requires Publisher access, even though other editors can edit drafts. It is unavailable for a new article with no published editions.

> [!WARNING]
> Restore replaces the current draft. There is no draft history or undo for Restore. Before restoring, save a copy of the draft text outside Finch if you need to keep it.

1. Verify the article ID.
2. In the Editions panel, select the older edition you want and verify its edition number.
3. Select Restore.
4. Open Preview and check the restored draft's title, date, and body. Preview is visible only to signed-in editors and is never the public address. If you edit the restored draft, save and wait for completion before previewing again.

You can leave the restored text as a draft. To make it public, follow [Publish](publish.md#publish), including saving, checking Preview, and completing any required organizational approval outside Finch. After publishing, confirm the new edition is Current in Editions and check its permanent public address in a signed-out browser.
```
