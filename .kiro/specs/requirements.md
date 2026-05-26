# Requirements — Cognitive Load Balancer (CLB) MVP 1.0

> Source of truth: Miro board `https://miro.com/app/board/uXjVHOUD00o=/`
> Frames: F-01 through F-14 (Control Plane Document)
> All definitions below are derived strictly from board content. Nothing is invented.

---

## 1. Product Overview (F-01)

**Product Name:** Cognitive Load Balancer (CLB)
**Tagline:** Your Miro board thinks. Your agent acts.
**Version:** MVP 1.0 (Hackathon Submission)

**Core Problem:** Cognitive overload from fragmentation, context switching, and always-on communication is the leading burnout driver — yet nobody measures it and nobody acts on it automatically.

**Core Solution:** An autonomous intervention agent that measures cognitive load from work signals, scores it in real time, and triggers protective actions before burnout occurs.

**Key Differentiator:** The Miro board IS the rules engine. Kiro reads the board via Miro MCP to build the system. The agent writes results back to the board. Miro is not documentation — it is infrastructure.

---

## 2. Data Sources (F-02)

| Source ID | Name            | Mode     | Scenario Options                          | Signals Produced          |
|-----------|-----------------|----------|-------------------------------------------|---------------------------|
| SRC-01    | Google Calendar | **LIVE** | N/A — uses real user calendar             | Temporal signals (T-*)    |
| SRC-02    | Slack           | **MOCK** | Normal / Interrupted / After-Hours Storm  | Communication signals (C-*) |
| SRC-03    | GitHub          | **MOCK** | Normal / PR Storm / Review Overload       | Task signals (TA-*)       |
| SRC-04    | Jira / Linear   | **MOCK** | Normal / Sprint Crunch / Reassign Chaos   | Task signals (TA-*)       |

### Critical Rules
- Calendar = LIVE (real OAuth, real events, real interventions)
- All others = MOCK (showcase mode, clearly badged)
- UI must display LIVE/MOCK badge on every data card
- Never treat mock sources as live

---

## 3. Mock Scenarios (F-03)

| Scenario ID | Name               | Description                                              | Sources Affected         |
|-------------|--------------------|----------------------------------------------------------|--------------------------|
| SCN-01      | Baseline           | Normal working day, moderate activity                    | SRC-02, SRC-03, SRC-04  |
| SCN-02      | Interruption Storm | 40+ Slack messages, 8 PR review requests in 4 hours     | SRC-02, SRC-03           |
| SCN-03      | Sprint Crunch      | 12+ open tickets, 5 reassignments, deadline pressure    | SRC-04                   |
| SCN-04      | After-Hours Bleed  | Messages sent 9pm–11pm, calendar events before 8am      | SRC-02, SRC-01 mock      |
| SCN-05      | Full Overload      | All of the above combined — demonstrates CRITICAL state  | SRC-02, SRC-03, SRC-04  |

**UI Requirement:** Scenario toggle must be visible in dashboard. Selected scenario must update CL score in real time.

---

## 4. Signal Catalog (F-04)

### 4.1 Temporal Signals (Source: SRC-01 — Google Calendar LIVE)

| Signal ID | Signal Name            | Formula / Logic                          | Range    | Weight |
|-----------|------------------------|------------------------------------------|----------|--------|
| T-01      | meeting_count_today    | Count of calendar events today           | 0–20+   | High   |
| T-02      | back_to_back_chains    | Sequences with gap < 15 min             | 0–10+   | High   |
| T-03      | avg_gap_minutes        | Avg minutes between consecutive meetings | 0–480   | Medium |
| T-04      | after_hours_meetings   | Events outside CFG-01 to CFG-02 (user TZ)| 0–10+  | High   |
| T-05      | total_meeting_hours    | Sum of event durations today             | 0–12+   | Medium |
| T-06      | focus_blocks_available | Uninterrupted blocks ≥ 2 hours          | 0–5+    | High   |
| T-07      | days_without_break     | Consecutive days with >6h meetings       | 0–30+   | High   |

### 4.2 Communication Signals (Source: SRC-02 — Slack MOCK)

| Signal ID | Signal Name            | Formula / Logic                          | Range    | Weight |
|-----------|------------------------|------------------------------------------|----------|--------|
| C-01      | messages_sent_today    | Total messages sent                      | 0–200+  | Medium |
| C-02      | avg_response_time_mins | Avg time from mention to reply           | 0–480   | Medium |
| C-03      | after_hours_messages   | Messages sent outside CFG-01 to CFG-02   | 0–50+   | High   |
| C-04      | sentiment_score_today  | NLP sentiment: -1.0 (negative) to 1.0   | -1 to 1 | Low    |
| C-05      | sentiment_trend_delta  | sentiment_today minus 7-day avg          | -2 to 2 | Medium |
| C-06      | channels_active        | Distinct channels posted in              | 0–30+   | Low    |
| C-07      | dm_vs_channel_ratio    | DMs / (DMs + channel posts)             | 0–1     | Low    |

### 4.3 Task Signals (Source: SRC-03 GitHub + SRC-04 Jira MOCK)

| Signal ID | Signal Name            | Formula / Logic                          | Range    | Weight |
|-----------|------------------------|------------------------------------------|----------|--------|
| TA-01     | open_prs_count         | Active PRs assigned to user              | 0–20+   | High   |
| TA-02     | review_requests_today  | PR review requests received today        | 0–15+   | High   |
| TA-03     | avg_tasks_in_progress  | Jira tickets in "In Progress"            | 0–20+   | High   |
| TA-04     | ticket_reassignments   | Tickets reassigned to user this week     | 0–10+   | Medium |
| TA-05     | context_switches       | Branch switches or ticket status changes | 0–30+   | High   |
| TA-06     | incomplete_task_pct    | % tasks past due date                    | 0–100   | Medium |
| TA-07     | avg_task_age_days      | Average age of open tasks in days        | 0–90+   | Low    |

### 4.4 Boundary Signals (Cross-Source Derived)

| Signal ID | Signal Name            | Formula / Logic                                              | Range    | Weight   |
|-----------|------------------------|--------------------------------------------------------------|----------|----------|
| B-01      | boundary_violations    | after_hours_meetings + after_hours_messages                  | 0–60+   | High     |
| B-02      | weekend_work_detected  | Events or messages on days not in CFG-04 (user's work_days) | boolean  | High     |
| B-03      | vacation_interrupted   | Activity during PTO calendar blocks                          | boolean  | Critical |

---

## 5. Scoring Model (F-05)

### 5.1 Composite CL Score Formula

```
CL_SCORE = (
  temporal_score      * 0.30 +
  communication_score * 0.25 +
  task_score          * 0.25 +
  boundary_score      * 0.20
)
```

Each component score calculated 0–100 using signal thresholds.

### 5.2 CL Score Bands

| Band     | Score Range | Colour   | Action Required                |
|----------|-------------|----------|--------------------------------|
| OPTIMAL  | 0–30        | Green    | None                           |
| MODERATE | 31–50       | Yellow   | Monitor + suggest focus time   |
| HIGH     | 51–70       | Orange   | Trigger protective actions     |
| CRITICAL | 71–85       | Red      | Urgent intervention required   |
| BURNOUT  | 86–100      | Dark Red | Immediate manager alert        |

### 5.3 Burnout Risk Probability

```
burnout_risk = sigmoid(CL_SCORE)
             * sustained_high_load_multiplier  (1.0–1.5)
             * sentiment_degradation_multiplier (1.0–1.3)
             * after_hours_multiplier           (1.0–1.2)
```

**Multipliers:**
- `sustained_high_load_multiplier`: 1.5 if HIGH/CRITICAL for 3+ consecutive days
- `sentiment_degradation_multiplier`: 1.3 if sentiment_trend_delta < -0.5
- `after_hours_multiplier`: 1.2 if boundary_violations > 5 per day

### 5.4 Flow State Detection

Flow state = TRUE only when ALL conditions met:

| Condition                          | Value Required |
|------------------------------------|----------------|
| No meetings in next 2 hours        | true           |
| focus_blocks_available             | >= 2           |
| task_score                         | < 30           |
| avg_response_time_mins (Slack)     | > 45           |
| CL_SCORE                           | < 40           |

---

## 6. Intervention Rules (F-06)

| INT-ID | Intervention Name          | Execution Mode | Trigger Condition                              | Action                                              |
|--------|----------------------------|----------------|------------------------------------------------|-----------------------------------------------------|
| INT-01 | Add Focus Block            | **LIVE**       | focus_blocks_available == 0 AND CL > 50       | Create 2h calendar event "Focus Time — CLB Protected" |
| INT-02 | Insert Meeting Buffers     | **DRY-RUN**    | back_to_back_chains >= 3                       | Propose 15-min buffer events between meetings       |
| INT-03 | Enable Slack DND           | **DRY-RUN**    | after_hours_messages > 5                       | Set Slack status + enable DND via Slack API         |
| INT-04 | Decline Non-Critical Meetings | **DRY-RUN** | total_meeting_hours > 6 AND CL > 65           | Mark optional meetings as "decline" candidates      |
| INT-05 | Reduce Sprint Scope        | **DRY-RUN**    | avg_tasks_in_progress > 7                      | Notify PM: "recommend reducing sprint load"         |
| INT-06 | Manager Alert              | **DRY-RUN**    | CL > 80 OR burnout_risk > 0.75                | Private Slack DM to manager with risk summary       |
| INT-07 | Vacation Guard             | **DRY-RUN**    | vacation_interrupted == true                   | Alert: "User is on PTO — escalate is blocked"       |

### Critical Rules
- Only INT-01 executes for real (creates actual Google Calendar event)
- All other interventions are DRY-RUN (planned but not executed)
- UI must display LIVE/DRY-RUN badge on every intervention card
- Every intervention (live or dry-run) must create a Miro card in F-09
- Every intervention must update the team heatmap in F-08

---

## 7. Privacy & Consent (F-07)

### Core Principles

| Principle        | Implementation                                      |
|------------------|-----------------------------------------------------|
| Consent First    | No data collected before explicit user opt-in       |
| Data Minimisation| Only derived signals stored — never raw content     |
| Transparency     | Every data point shown in "My Data" dashboard       |
| Right to Delete  | One-click data deletion (GDPR Art. 17 compliant)   |
| Mock Safety      | Mock mode never touches real user data              |
| Retention Limit  | All score data auto-deleted after 90 days           |

### Consent Levels

| Level    | What is Collected                              | What is NOT Collected     |
|----------|------------------------------------------------|---------------------------|
| BASIC    | Calendar event counts and durations only       | Event titles, attendees   |
| STANDARD | BASIC + Slack metadata (counts, timing)        | Message content           |
| FULL     | STANDARD + GitHub/Jira activity metadata       | Code content, ticket text |

**MVP Requirement:** Consent screen must be shown before any data collection begins (AC08).

---

## 8. Acceptance Criteria (F-11) — LOCKED SCOPE

| ID   | Criterion                                                          | Pass Condition                          |
|------|--------------------------------------------------------------------|-----------------------------------------|
| AC01 | CLB app connects to Google Calendar via OAuth                      | Real events load into signal engine     |
| AC02 | CL Score updates every 15 minutes using live calendar data         | Score visible on dashboard              |
| AC03 | At least one real intervention fires (Focus Block creation)        | Event appears in Google Calendar        |
| AC04 | Mock data toggles available for Slack, GitHub, Jira                | UI shows MOCK badge; score changes      |
| AC05 | All mock interventions labelled as DRY-RUN in UI and Miro          | No confusion between real and simulated |
| AC06 | Kiro reads Miro board via MCP and generates spec artifacts         | .kiro/specs/ directory contains output  |
| AC07 | App writes intervention cards back to Miro board                   | New cards visible on board after demo   |
| AC08 | Privacy consent screen shown before any data collection begins     | Consent recorded before processing      |
| AC09 | Live URL accessible by judges                                      | App loads at deployed URL               |
| AC10 | .kiro directory committed to repo with specs, steering, hooks      | Visible in GitHub repo                  |

---

## 9. Agent Guardrails (F-12)

Any AI agent using this board as a knowledge source MUST NOT:

1. Invent new signal names, IDs, or formulas not in F-04
2. Change the scoring weights or thresholds in F-05 without explicit user instruction
3. Treat Slack, GitHub, or Jira as LIVE integrations in MVP scope
4. Execute INT-02 through INT-07 as real (live) interventions — they are DRY-RUN only
5. Store raw message content, event titles, or code content — derived signals only
6. Skip the consent screen before data collection
7. Create a UI that does not clearly badge LIVE vs MOCK and EXECUTED vs DRY-RUN
8. Omit the Miro write-back step from the implementation
9. Ignore the .kiro directory structure — it must be committed to the repo
10. Present this as a "burnout tracker" — it is a cognitive load intervention agent
