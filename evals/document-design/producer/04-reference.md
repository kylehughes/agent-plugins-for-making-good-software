# Review a retention-code reference

## Request

Review this reference for publication. Report concrete reader-facing problems if you find any, with the affected text and a proposed correction. If it is already sound, say so. Please do not rewrite the document or add a tutorial.

## Factual source

Parcel is an internal document archive. Every stored item has exactly one retention code. Codes affect automated cleanup only, not who may read the item. Keep means no scheduled cleanup. Review means the archive flags the item on its review date; it never deletes automatically. Expire means the archive deletes the item on its expiry date only if no hold is active. An active hold blocks deletion for any code. Removing a hold does not delete the item immediately; cleanup evaluates it at the next daily run. The date is a calendar date in the archive's configured time zone, displayed in Archive settings. Users with the Records role can change codes and dates. Other users can read the code if they can read the item. Review and Expire both require a date; Keep has no date. This reference is intentionally limited to code meaning; assigning codes is covered by a separate policy, whose link resolves. The document below is current and complete for that scope.

## Starting retention-codes.md

# Retention codes

Use this reference to interpret an item's code. A code controls automated cleanup; it does not grant or remove access. For choosing a code, follow the [records policy](records-policy.md).

| Code | Required date | Result |
| --- | --- | --- |
| Keep | None | No scheduled cleanup. |
| Review | Review date | Flags the item for review on that date; does not delete it. |
| Expire | Expiry date | Deletes the item on that date only if no hold is active. |

Dates use the archive's configured time zone, shown in Archive settings. An active hold blocks deletion regardless of code. Removing a hold makes the item eligible for evaluation at the next daily cleanup run; it does not delete the item immediately.

Only users with the Records role can change codes or dates. Anyone who can read an item can read its code.
