# Worked examples

These are synthetic calibration fixtures adapted from the supplied design report. Their facts are stipulated, not product claims or hidden evaluation cases. Inferences are identified below; no example establishes a measured reader benefit.

## Explain the persistence boundary before the acceptance choice

A competent developer knows imports but is unfamiliar with RowPreview. The source says `preview(file)` returns valid rows and row-identified validation errors, saves nothing, and leaves saving to the application. Saving valid rows while errors remain produces a partial import. It makes no transaction, rollback, retry, or performance guarantee.

The starting README separates returns under Features, the example under Usage, no-save behavior under Concepts, and partial acceptance under Advanced. The missing connection is why inspection precedes the application's acceptance decision.

Finished passage:

````markdown
# RowPreview

Use RowPreview when an application needs to inspect validation results
before deciding whether to save an import. `preview(file)` returns valid
rows and validation errors without saving anything. The application owns
the save operation.

## Preview a file and decide what to accept

```text
result = preview(file)
display(result.valid_rows, result.errors)
```

The displayed result lets the application present the validation outcome
before making a persistence decision. Choose the acceptance policy before
calling the application's save operation.

### Reject an import with errors

If every row must pass validation, reject the import when errors are
present. Previewing itself has saved nothing.

### Accept the valid rows

Save the valid rows only if an incomplete import satisfies the application's
requirement. When errors remain, saving valid rows produces a partial import.

## Locate a validation error

Validation errors identify source rows. Use those identifiers to locate
the entries that failed validation.
````

The pseudocode is unchanged. The benefit follows from the supplied no-save contract. Rejection is a conditional recommendation under an explicit all-rows-valid requirement, not a new capability. Both acceptance branches belong under the same workflow, and the partial-import condition remains visible on direct arrival.

If the source omitted persistence behavior, the missing proposition would be “Does previewing mutate persistent data?” The method name cannot answer it.

## Keep a good shallow guide

This document already serves a neighborhood member borrowing shared equipment:

```markdown
# Borrow the neighborhood projector

Neighborhood members can borrow the projector for one day at no charge.
Reserve it before arranging collection.

## Reserve a day

Email the equipment coordinator with your preferred date. Your booking is
confirmed when the coordinator replies; sending a request does not reserve it.

## Collect and return it

Collect the projector from the community room between 9 and 10 a.m. on your
reserved day. The case contains the projector, power cable, and HDMI cable.

Return the complete case to the same room by 10 a.m. the following day.
Agree on any later return with the coordinator before collecting it.

## If something is missing

Check the case when you collect it. Tell the coordinator immediately if an
item is missing or damaged.
```

Leave it unchanged. Its peer sections answer distinct questions. Moving the case check beside the contents list is defensible, but without evidence of a missed check it is an optional alternative. A new “Borrowing process” parent and concluding summary would supply no missing relationship.

## Preserve a good reference schema

A returning visitor seeks a timeout value. These synthetic facts are complete for that lookup:

```markdown
# Relay options

These options apply to Relay's command-line client.

| Option | Default | Meaning |
| --- | --- | --- |
| `--timeout` | 30 seconds | Maximum wait for one connection attempt; zero disables the limit. |
| `--format` | `text` | Output encoding: `text` or `json`. |
```

Keep the table. Stable keys, units, scope, and the exceptional value are local. A connection tutorial, examples for every row, or nested headings would obstruct this visit. A review can return no substantive defect without editing.

## Explain why an expired worker cannot write

The fictional Ledger source gives a paused-worker scenario, lease deadlines, increasing generations on acquisition, renewal without a new generation, and an atomic store check. It scatters atomicity and the guarantee's boundary under Advanced.

Finished explanatory passage:

```markdown
# Why an expired Ledger worker cannot commit

A paused worker can resume after another worker takes over its record.
Expiry does not stop the old process. Ledger checks authority at the
protected store when the write occurs.

## What a lease permits

A lease permits commits to one record until its deadline. Expiry allows
another worker to acquire that record; it does not terminate the old worker.

### Acquisition and renewal

Each acquisition receives a generation greater than the previous one for
that record. Renewal before expiry keeps the generation and extends the
deadline. Renewal continues a grant; acquisition identifies a new grant.

## How the store rejects an obsolete write

Every protected write carries the worker's generation. The store accepts
it only when that generation is current and the lease is unexpired.

The check and write are atomic. A separate check followed by an unguarded
write would leave a gap for takeover between them.

### Follow a takeover

A holds generation 17 and pauses. After its lease expires, B acquires 18
and commits. A resumes with 17; the store rejects the write because that
generation is no longer current. Rejection does not depend on stopping A.

## Where the guarantee ends

The rule covers writes through the protected store. It does not stop
computation, undo completed effects, or protect an external email send.
```

The process/authority distinction prepares the write rule. Atomicity explains enforcement, and the example instantiates it. Both current-generation and unexpired-lease conditions remain. A nearby transfer case is expiry with no new acquisition: the unexpired condition still fails. The source supplies that answer; no new behavior is inferred.

## Keep recovery conditions on the arrival page

Suppose an export error page links to Recovery, which says to unlock and retry, while another page says only orphaned locks may be removed. The synthetic contract also supplies a read-only status command, an atomic orphan-state check during unlock, and escalation for unknown status or a persistent error.

Finished operational entry:

```markdown
# Export blocked by LOCK_HELD

An existing workspace lock blocks the export. Remove it only when its
status is `orphaned`.

## Check before choosing a recovery action

Run `status WORKSPACE`. This command is read-only.

| Status | Action |
| --- | --- |
| `active` | A running export owns the lock. Wait; do not unlock. |
| `orphaned` | Run `unlock WORKSPACE`. If it succeeds, retry the export. |
| `unknown` | Contact the service owner; do not unlock. |

Unlock checks the current state atomically with removal and refuses if the
lock is no longer orphaned. If the error persists after a successful unlock
and retry, contact the service owner.
```

Keep the complete authoritative contract in reference and extended mechanism in explanation. Link to their real destinations when available. A separate unlock reference should repeat the short orphan-only condition and link back to recovery. Check both restatements when the contract changes. Preserve old anchors using the actual platform's supported mechanism; do not invent a redirect or URL.

## Recognize polished failures

A table of contents can improve access without repairing a fragmented explanation. Putting every heading under “Overview” does not establish a meaningful parent. A roadmap that merely lists Features, Usage, and Advanced may leave value and applicability unexplained. A lesson can obstruct a reference lookup. Repeated conclusions can add cost without a new task.

None of those layouts is prohibited. A real overview, a useful roadmap, a coherent long explanation, or an independently used executive summary can justify the same form. Name the failed task before changing it.
