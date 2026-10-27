# Pause or resume a nightly digest

Use this procedure as the on-call operator to prevent a workspace's next nightly digest job from starting, then resume its schedule after the incident. An incident ticket is required before pausing. Only the on-call operator can change these controls in the internal Digest console.

Pausing cannot stop a Running job, recall email, or undo sent messages. Paused workspaces do not queue missed digests. Resuming schedules the next run for the workspace's next nightly time; it does not send a catch-up digest. All console times are UTC.

## Check whether to pause

1. Open the workspace in the Digest console. Verify the numeric workspace ID at the top against the incident ticket. Similar workspace names exist; do not rely on the name alone.
2. Check the current job in the Jobs tab and choose the applicable path:

   | Current job state | Action |
   | --- | --- |
   | Pending | Pause can prevent the job from starting. Follow the pause steps below. |
   | Running | Do not press Pause to try to stop it. Page the incident commander with the workspace ID and job ID. The commander decides what to do. |
   | Completed or Failed | The current job cannot be undone. Pause can still prevent the next scheduled job. Follow the pause steps below if that is needed. |

## Pause and verify

Before changing the schedule, confirm that you have an incident ticket and that the workspace's numeric ID matches it. If the current job is Running, use the escalation path above instead of trying to stop it with Pause.

1. On the Schedule tab, select Pause.
2. Enter the incident ticket number and select Confirm pause.
3. Refresh the Schedule tab and confirm that it shows `Paused`. The Jobs tab alone does not prove that the workspace is paused.
4. Record the pause time, workspace ID, and observed schedule state in the incident ticket, using UTC for the time.

If the Schedule tab does not show `Paused` after refresh, stop and page the incident commander. Do not repeatedly toggle the control.

## Resume and verify

Resume only after the incident commander approves it in the incident ticket. Missed digests are skipped; resuming does not send a catch-up digest. Manual send is a separate privileged operation outside this procedure.

1. Open the workspace in the Digest console and verify its numeric ID against the incident ticket.
2. On the Schedule tab, select Resume, then Confirm resume.
3. Refresh the Schedule tab. Confirm that it shows `Active` and check the next UTC run time. The nightly time varies by workspace; do not assume a fixed hour.
4. Record the resume time, workspace ID, and observed schedule state in the ticket, using UTC for the time.

If the Schedule tab does not show `Active`, stop and page the incident commander.
