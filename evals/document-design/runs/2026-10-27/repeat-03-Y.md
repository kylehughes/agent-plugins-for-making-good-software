# Pause the nightly digest

Use this procedure to prevent a workspace's next nightly digest job from starting during an incident. Only the on-call operator can change these controls in the internal Digest console. An incident ticket is required before pausing.

Pausing cannot stop a Running job, recall email, or undo sent messages. Paused workspaces do not queue missed digests. Resuming schedules the next nightly run; it does not send a catch-up digest.

## Check before pausing

1. Open the workspace in the Digest console. Verify the numeric workspace ID at the top against the incident ticket. Similar workspace names exist; do not rely on the name alone.
2. Open the Jobs tab and check the current job's state:
   - **Pending:** the job is eligible for a pause. Continue below.
   - **Running:** do not press Pause to try to stop it. Page the incident commander with the workspace ID and job ID. The commander decides what to do.
   - **Completed or Failed:** the current job cannot be undone. Continue below if the next scheduled job needs to be prevented.

All console times are UTC. The ordinary nightly time varies by workspace; read it on the Schedule tab rather than assuming a fixed hour.

## Pause and verify

1. Select Pause, enter the incident ticket number, and select Confirm pause.
2. Refresh the Schedule tab and confirm that it shows `Paused`. The Jobs tab alone does not prove that the workspace is paused.
3. Record the pause time, workspace ID, and observed schedule state in the incident ticket.

If the refreshed Schedule tab does not show `Paused`, stop and page the incident commander. Do not repeatedly toggle the control. Record the observed state in the ticket.

## Resume and verify

Resume only after the incident commander approves in the incident ticket.

1. Open the workspace in the Digest console and verify its numeric ID against the incident ticket.
2. On the Schedule tab, select Resume, then Confirm resume.
3. Refresh and confirm that the Schedule tab shows `Active` and the next UTC run time. The next run is the next scheduled nightly time for that workspace.
4. Record the resume time, workspace ID, and observed schedule state, including the next run time, in the ticket.

If the Schedule tab does not show `Active`, stop and page the incident commander. Record the observed state in the ticket.

Missed digests are skipped. Manual send is a separate privileged operation and is outside this procedure.
