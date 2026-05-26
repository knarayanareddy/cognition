---
inclusion: always
---

# CLB Data Sources & Capability Matrix

> Source: Miro board frame F-02

## Data Source Registry

| Source ID | Name            | Mode     | Scenario Options                          | Signals Produced            |
|-----------|-----------------|----------|-------------------------------------------|-----------------------------|
| SRC-01    | Google Calendar | **LIVE** | N/A — uses real user calendar             | Temporal signals (T-*)      |
| SRC-02    | Slack           | **MOCK** | Normal / Interrupted / After-Hours Storm  | Communication signals (C-*) |
| SRC-03    | GitHub          | **MOCK** | Normal / PR Storm / Review Overload       | Task signals (TA-*)         |
| SRC-04    | Jira / Linear   | **MOCK** | Normal / Sprint Crunch / Reassign Chaos   | Task signals (TA-*)         |

## Critical Rules

- Calendar = LIVE (real OAuth, real events, real interventions)
- All others = MOCK (showcase mode, clearly badged)
- UI must display LIVE/MOCK badge on every data card
- Never treat mock sources as live
