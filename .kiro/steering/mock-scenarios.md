---
inclusion: always
---

# CLB Mock Scenarios

> Source: Miro board frame F-03

## Scenario Definitions

| Scenario ID | Name               | Description                                              | Sources Affected         |
|-------------|--------------------|----------------------------------------------------------|--------------------------|
| SCN-01      | Baseline           | Normal working day, moderate activity                    | SRC-02, SRC-03, SRC-04  |
| SCN-02      | Interruption Storm | 40+ Slack messages, 8 PR review requests in 4 hours     | SRC-02, SRC-03           |
| SCN-03      | Sprint Crunch      | 12+ open tickets, 5 reassignments, deadline pressure    | SRC-04                   |
| SCN-04      | After-Hours Bleed  | Messages sent 9pm–11pm, calendar events before 8am      | SRC-02, SRC-01 mock      |
| SCN-05      | Full Overload      | All of the above combined — demonstrates CRITICAL state  | SRC-02, SRC-03, SRC-04  |

## UI Requirement

Scenario toggle must be visible in dashboard. Selected scenario must update CL score in real time.
