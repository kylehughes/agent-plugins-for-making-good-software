# Evaluator key: 03-procedure

Development. Evaluator only. This tests conditions at the point of action, sequencing, state verification, and safe stopping. Do not execute any controls.

## Starting contexts and reader tasks

1. **Direct incident entry.** On-call operator has ticket INC-214, numeric workspace ID 481, and sees two similarly named workspaces. Job 700 is Running. Start at the produced pause instructions, skipping any introduction. Ask what to check and do next. Required: match numeric ID to incident, inspect job state, recognize Pause cannot stop Running, and page commander with workspace ID and job ID. Do not press Pause as a way to stop this run; do not promise recall of mail. Ticket and operator role are preconditions; a warning located only after the action fails this trial.
2. **Eligible pause.** Same operator and ticket, current job Pending. Ask for steps and proof that next run is prevented. Required: correct workspace; Pause, ticket, Confirm pause; refresh Schedule and confirm Paused; record UTC time, ID, state in ticket. Jobs presence or absence is not proof. If state is not Paused after refresh, stop and page commander rather than repeatedly toggle.
3. **Resume / direct entry.** Start at resume heading or equivalent. Operator sees Paused, commander has not approved. Ask if they can resume to send yesterday's missed digest. Required: obtain approval in ticket first. Resume does not catch up; next scheduled nightly run only. With approval, Resume, Confirm resume, refresh Schedule for Active and next UTC time, then record event. If not Active, stop and page commander. Time comes from Schedule, not an assumed fixed hour.
4. **Completed job.** Current job Completed and the operator wants to prevent tonight's next run. Required: completed sending cannot be undone; pause is still useful for the next scheduled job. Failed job likewise cannot be undone. No manual send instructions belong here.

## Permissible inference and alternatives

Console literacy is given; console controls and state semantics are not. A decision table, branched procedure, separate pause/resume sections, or short checklist can all pass. The order need only enforce prerequisites before side effects and confirmation afterward. Repeating a short role or approval condition at direct-entry sections is useful; wholesale duplication is not required. Links to an explicit shared prerequisite are acceptable if the path is unavoidable before action.

## Preservation and mode

Return a finished rewritten procedure. No dependency on the unavailable handbook may be necessary to complete these tasks. No operating action is authorized. Preserve skipped-digest behavior and commander authority. Distinguish failure to deliver the requested rewrite from unsafe/incomplete content. A long architecture explanation is a proportionality defect, even with correct steps.

## Scoring anchors

Critical: no Running-stop claim, no resume without approval, no lost verification path. Major: wrong state used for success, missing identity check, no stop/escalation on unclear result. Minor: inconvenient wording with a complete safe route. Record where each prerequisite is encountered relative to its action.
