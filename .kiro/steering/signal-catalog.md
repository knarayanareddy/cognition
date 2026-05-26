---
inclusion: always
---

# CLB Signal Catalog

> Source: Miro board frame F-04
> Total signals: 24 (7 Temporal + 7 Communication + 7 Task + 3 Boundary)

## Temporal Signals (Source: SRC-01 — Google Calendar LIVE)

| Signal ID | Signal Name            | Formula / Logic                            | Range    | Weight |
|-----------|------------------------|--------------------------------------------|----------|--------|
| T-01      | meeting_count_today    | Count of calendar events today             | 0–20+   | High   |
| T-02      | back_to_back_chains    | Sequences with gap < CFG-11 mins           | 0–10+   | High   |
| T-03      | avg_gap_minutes        | Avg minutes between consecutive meetings   | 0–480   | Medium |
| T-04      | after_hours_meetings   | Events outside CFG-01 to CFG-02 (user TZ)  | 0–10+   | High   |
| T-05      | total_meeting_hours    | Sum of event durations today               | 0–12+   | Medium |
| T-06      | focus_blocks_available | Uninterrupted blocks ≥ 2 hours            | 0–5+    | High   |
| T-07      | days_without_break     | Consecutive days with >6h meetings         | 0–30+   | High   |

## Communication Signals (Source: SRC-02 — Slack MOCK)

| Signal ID | Signal Name            | Formula / Logic                            | Range    | Weight |
|-----------|------------------------|--------------------------------------------|----------|--------|
| C-01      | messages_sent_today    | Total messages sent                        | 0–200+  | Medium |
| C-02      | avg_response_time_mins | Avg time from mention to reply             | 0–480   | Medium |
| C-03      | after_hours_messages   | Messages sent outside CFG-01 to CFG-02     | 0–50+   | High   |
| C-04      | sentiment_score_today  | NLP sentiment: -1.0 (negative) to 1.0     | -1 to 1 | Low    |
| C-05      | sentiment_trend_delta  | sentiment_today minus 7-day avg            | -2 to 2 | Medium |
| C-06      | channels_active        | Distinct channels posted in                | 0–30+   | Low    |
| C-07      | dm_vs_channel_ratio    | DMs / (DMs + channel posts)               | 0–1     | Low    |

## Task Signals (Source: SRC-03 GitHub + SRC-04 Jira MOCK)

| Signal ID | Signal Name            | Formula / Logic                            | Range    | Weight |
|-----------|------------------------|--------------------------------------------|----------|--------|
| TA-01     | open_prs_count         | Active PRs assigned to user                | 0–20+   | High   |
| TA-02     | review_requests_today  | PR review requests received today          | 0–15+   | High   |
| TA-03     | avg_tasks_in_progress  | Jira tickets in "In Progress"              | 0–20+   | High   |
| TA-04     | ticket_reassignments   | Tickets reassigned to user this week       | 0–10+   | Medium |
| TA-05     | context_switches       | Branch switches or ticket status changes   | 0–30+   | High   |
| TA-06     | incomplete_task_pct    | % tasks past due date                      | 0–100   | Medium |
| TA-07     | avg_task_age_days      | Average age of open tasks in days          | 0–90+   | Low    |

## Boundary Signals (Cross-Source Derived)

| Signal ID | Signal Name            | Formula / Logic                                                    | Range    | Weight   |
|-----------|------------------------|--------------------------------------------------------------------|----------|----------|
| B-01      | boundary_violations    | after_hours_meetings + after_hours_messages (per CFG-01/02/03)    | 0–60+   | High     |
| B-02      | weekend_work_detected  | Events or messages on days not in CFG-04 (user's work_days)       | boolean  | High     |
| B-03      | vacation_interrupted   | Activity during PTO calendar blocks                                | boolean  | Critical |
