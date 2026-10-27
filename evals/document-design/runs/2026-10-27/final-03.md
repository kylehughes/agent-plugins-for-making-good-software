# Pause the nightly digest

Use this procedure as the on-call operator to pause or resume a workspace's nightly email digest in the internal Digest console. Harbor sends one nightly digest per workspace. All console times are UTC.

Pausing prevents the next digest job from starting. It cannot stop a job already Running, recall email, or undo sent messages. Paused workspaces do not queue missed digests.

## Decide whether to pause

1. Have an incident ticket before pausing. Only the on-call operator can change digest controls.
2. Open the workspace in the Digest console. Verify the numeric workspace ID shown at the top against the incident ticket. Similar workspace names exist; do not rely on the name alone.
3. Check the current job in the Jobs tab:

   | Job state | Action |
   | --- | --- |
   | Pending | The job is eligible for a pause. Continue to [Pause and verify](#pause-and-verify). |
   | Running | Do not press Pause to try to stop it. Page the incident commander with the workspace ID and job ID. The commander decides what to do. |
   | Completed or Failed | The current job cannot be undone. Continue to [Pause and verify](#pause-and-verify) if you need to prevent the next scheduled job. |

## Pause and verify

Before using Pause, confirm that you are the on-call operator, have an incident ticket, and have verified the numeric workspace ID against it. Check the [current job state](#decide-whether-to-pause); if it is Running, page the incident commander with the workspace ID and job ID instead of trying to stop it with Pause.

1. Select Pause, enter the incident ticket number, and select Confirm pause.
2. Refresh the workspace's Schedule tab and confirm that it shows `Paused`. The Jobs tab alone does not prove that the schedule is paused.
3. If the Schedule tab does not show `Paused`, stop and page the incident commander. Do not repeatedly toggle the control.
4. Record the pause time, workspace ID, and observed schedule state in the incident ticket.

## Resume and verify

Only the on-call operator can resume the digest, and only after the incident commander approves in the incident ticket. Verify the numeric workspace ID shown at the top against the ticket before changing the schedule.

Resuming sets the next run to the next scheduled nightly time. It does not send a catch-up digest for missed runs. The nightly time varies by workspace; use the time shown in the Schedule tab rather than assuming a fixed hour.

1. On the Schedule tab, select Resume, then Confirm resume.
2. Refresh the Schedule tab. Confirm that it shows `Active` and check the next UTC run time.
3. If it does not show `Active`, stop and page the incident commander.
4. Record the resume time, workspace ID, and observed schedule state in the incident ticket, along with the next UTC run time you checked.

Manual send is a separate privileged operation and is outside this procedure.
