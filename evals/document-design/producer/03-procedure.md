# Pause the nightly digest

## Request

Rewrite this procedure for our on-call operator. They may land directly on it during a late digest incident and need to know whether to pause, how to confirm it took effect, and how to resume safely. Keep the procedure usable without the incident handbook. Do not perform any operations.

## Factual source

Harbor sends one nightly email digest per workspace. The following controls are in the internal Digest console. Only the on-call operator can change them. The workspace name and numeric ID are shown at the top; similar names exist, so verify the numeric ID against the incident ticket before making a change. All console times are UTC.

An incident ticket is required before pausing. Pausing prevents the next digest job from starting; it cannot stop a job already Running, recall email, or undo sent messages. The Jobs tab shows Pending, Running, Completed, or Failed. Pending is eligible for a pause. If the current job is Running, do not press Pause as a way to stop it: page the incident commander with workspace ID and job ID; the commander decides what to do. A Completed or Failed current job cannot be undone; pausing can still prevent the next scheduled job. Pause requires entering the incident ticket number and selecting Confirm pause. Success is shown as `Paused` on the workspace's Schedule tab. The Jobs tab alone does not prove pause state. If the Schedule tab does not show Paused after refresh, stop and page the incident commander; do not repeatedly toggle the control.

Paused workspaces do not queue missed digests. Resuming sets the next run to the next scheduled nightly time; it does not send a catch-up digest. Only resume after the incident commander approves in the incident ticket. On the Schedule tab select Resume, then Confirm resume. Refresh and confirm `Active` and the next UTC run time. Record pause or resume time, workspace ID, and observed schedule state in the ticket. If resume does not show Active, stop and page the commander. Manual send is a separate privileged operation and is outside this procedure. Ordinary scheduled nightly time is shown in the Schedule tab and varies by workspace; do not assume a fixed hour. This packet supplies all facts needed; the incident handbook has no additional prerequisite for these actions.

## Starting pause-digest.md

# Digest controls

To pause, open Digest console, find a workspace, and use Pause. Enter a ticket and confirm. The nightly digest is now stopped.

To resume, use Resume and confirm. Check the Jobs tab to see whether a digest appears. Ask the incident commander if anything looks odd.

Record the event in the ticket. These controls are for the on-call operator. Missed digests are skipped. See the incident handbook for context.
