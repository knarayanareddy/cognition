---
inclusion: always
---

# CLB Intervention Rules

> Source: Miro board frame F-06

## Intervention Table

| INT-ID | Intervention Name          | Execution Mode | Trigger Condition                              | Action                                                |
|--------|----------------------------|----------------|------------------------------------------------|-------------------------------------------------------|
| INT-01 | Add Focus Block            | **LIVE**       | focus_blocks_available == 0 AND CL > 50       | Create 2h calendar event "Focus Time — CLB Protected" |
| INT-02 | Insert Meeting Buffers     | **DRY-RUN**    | back_to_back_chains >= 3                       | Propose 15-min buffer events between meetings         |
| INT-03 | Enable Slack DND           | **DRY-RUN**    | after_hours_messages > 5                       | Set Slack status + enable DND via Slack API           |
| INT-04 | Decline Non-Critical Meetings | **DRY-RUN** | total_meeting_hours > 6 AND CL > 65           | Mark optional meetings as "decline" candidates        |
| INT-05 | Reduce Sprint Scope        | **DRY-RUN**    | avg_tasks_in_progress > 7                      | Notify PM: "recommend reducing sprint load"           |
| INT-06 | Manager Alert              | **DRY-RUN**    | CL > 80 OR burnout_risk > 0.75                | Private Slack DM to manager with risk summary         |
| INT-07 | Vacation Guard             | **DRY-RUN**    | vacation_interrupted == true                   | Alert: "User is on PTO — escalate is blocked"         |

## Critical Rules

- Only INT-01 executes for real (creates actual Google Calendar event)
- All other interventions are DRY-RUN (planned but not executed)
- UI must display LIVE/DRY-RUN badge on every intervention card
- Every intervention (live or dry-run) must create a Miro card in F-09
- Every intervention must update the team heatmap in F-08
