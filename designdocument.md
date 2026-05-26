# COGNITIVE LOAD BALANCER (CLB)
## Master Design Document — v2.0
### Purpose: Miro Sidekick Knowledge Source + Kiro Steering + MCP-Ready Spec

---

## ⚠️ AGENT INSTRUCTIONS (READ FIRST)

This document is the single source of truth for the Cognitive Load Balancer
system. If you are an AI agent (Miro Sidekick, Kiro, or MCP client):

- DO NOT invent signal definitions, scoring logic, or intervention rules.
- ALL system behaviour is defined in the tables below. Use them exactly.
- When generating PRDs, prototypes, slides, code, or specs — derive ONLY
  from the content in this document.
- When in doubt between this document and a user prompt, ask for
  clarification before deviating from this document.
- Data source modes are defined in Section 4. Calendar = LIVE.
  All others = MOCK (showcase mode). Never treat mock sources as live.
- Intervention modes are defined in Section 7. Only Calendar interventions
  execute for real. All others are DRY-RUN and must be labelled as such.

---

## SECTION 1 — PRODUCT IDENTITY

| Field               | Value                                                          |
|---------------------|----------------------------------------------------------------|
| Product Name        | Cognitive Load Balancer (CLB)                                  |
| Tagline             | Your Miro board thinks. Your agent acts.                      |
| Version             | MVP 1.0 (Hackathon Submission)                                 |
| Primary User        | Knowledge workers, engineering teams, remote squads            |
| Secondary User      | Engineering managers, team leads                               |
| Core Problem        | Cognitive overload from fragmentation, context switching,      |
|                     | and always-on communication is the leading burnout driver —    |
|                     | yet nobody measures it and nobody acts on it automatically.    |
| Core Solution       | An autonomous intervention agent that measures cognitive load  |
|                     | from work signals, scores it in real time, and triggers        |
|                     | protective actions before burnout occurs.                      |
| Key Differentiator  | The Miro board IS the rules engine. Kiro reads the board via   |
|                     | Miro MCP to build the system. The agent writes results back    |
|                     | to the board. Miro is not documentation — it is infrastructure.|
| Hackathon Theme     | Kiro × Miro: Integration Flow + Tool Usage                     |

---

## SECTION 2 — SYSTEM ARCHITECTURE

### 2.1 Pipeline (end-to-end)
[MIRO BOARD — Rules Engine + Control Plane] ↓ Kiro reads via Miro MCP Server [KIRO — Spec-Driven Development] ↓ Generates requirements.md + design.md + tasks.md [CLB APPLICATION — Built by Kiro] ↓ Ingests work signals [DATA SOURCES: Calendar(LIVE) / Slack(MOCK) / GitHub(MOCK) / Jira(MOCK)] ↓ Computes [SIGNAL ENGINE → SCORING ENGINE → CL SCORE + BURNOUT RISK + FLOW STATE] ↓ Triggers [INTERVENTION AGENT — LangGraph Orchestrated] ↓ Executes or Dry-Runs [INTERVENTIONS: Calendar(LIVE) / Slack(DRY-RUN) / Jira(DRY-RUN) / Manager(DRY-RUN)] ↓ Writes back [MIRO BOARD — Live Heatmap + Intervention Cards + Score Updates]

text


### 2.2 Architecture Layers

| Layer              | Technology                  | Notes                          |
|--------------------|-----------------------------|--------------------------------|
| Frontend           | Next.js + Tailwind CSS      | Live/Mock badge on all cards   |
| Backend API        | FastAPI (Python)            | REST + WebSocket endpoints     |
| Agent Orchestrator | LangGraph                   | Intervention decision logic    |
| Real-time          | WebSocket (FastAPI)         | 15-minute score refresh        |
| Database           | PostgreSQL                  | Scores, interventions, signals |
| Miro Integration   | Miro MCP Server             | Read board + write back        |
| Calendar           | Google Calendar API         | LIVE data source               |
| LLM                | Claude Sonnet (primary)     | Local Ollama fallback          |
| Deployment         | Single URL (live demo)      | Required for judging           |

---

## SECTION 3 — USER STORIES (REQUIREMENTS)

### 3.1 Core User Stories

| ID   | As a...            | I want to...                                    | So that...                               |
|------|--------------------|-------------------------------------------------|------------------------------------------|
| US01 | Knowledge worker   | See my real-time cognitive load score           | I understand when I am at risk           |
| US02 | Knowledge worker   | Have focus blocks added to my calendar          | I am protected from further overload     |
| US03 | Knowledge worker   | Control what data is collected about me         | I trust the system and opt in consciously|
| US04 | Engineering manager| See my team's cognitive load heatmap            | I can spot burnout risk early            |
| US05 | Engineering manager| Receive private alerts about at-risk teammates  | I can take action before damage is done  |
| US06 | Team member        | Toggle mock scenarios to showcase capability    | Stakeholders understand the full system  |
| US07 | Hackathon judge    | See Kiro read the Miro board and build the app  | The integration flow is demonstrated     |
| US08 | Hackathon judge    | Access a live URL with a working demo           | The functional MVP is proven             |

### 3.2 Acceptance Criteria (MVP)

| ID    | Criterion                                                                 | Pass Condition                          |
|-------|---------------------------------------------------------------------------|-----------------------------------------|
| AC01  | CLB app connects to Google Calendar via OAuth                             | Real events load into signal engine     |
| AC02  | CL Score updates every 15 minutes using live calendar data                | Score visible on dashboard              |
| AC03  | At least one real intervention fires (Focus Block creation)               | Event appears in Google Calendar        |
| AC04  | Mock data toggles available for Slack, GitHub, Jira                       | UI shows MOCK badge; score changes      |
| AC05  | All mock interventions labelled as DRY-RUN in UI and Miro                 | No confusion between real and simulated |
| AC06  | Kiro reads Miro board via MCP and generates spec artifacts                | .kiro/specs/ directory contains output  |
| AC07  | App writes intervention cards back to Miro board                          | New cards visible on board after demo   |
| AC08  | Privacy consent screen shown before any data collection begins            | Consent recorded before processing      |
| AC09  | Live URL accessible by judges                                             | App loads at deployed URL               |
| AC10  | /.kiro directory committed to repo with specs, steering, hooks            | Visible in GitHub repo                  |

---

## SECTION 4 — DATA SOURCES

### 4.1 Source Registry

| Source ID | Name             | Mode       | Scenario Options                          | Signals Produced          |
|-----------|------------------|------------|-------------------------------------------|---------------------------|
| SRC-01    | Google Calendar  | **LIVE**   | N/A — uses real user calendar             | Temporal signals (T-*)    |
| SRC-02    | Slack            | **MOCK**   | Normal / Interrupted / After-Hours Storm  | Communication signals(C-*)|
| SRC-03    | GitHub           | **MOCK**   | Normal / PR Storm / Review Overload       | Task signals (TA-*)       |
| SRC-04    | Jira / Linear    | **MOCK**   | Normal / Sprint Crunch / Reassign Chaos   | Task signals (TA-*)       |

### 4.2 Mock Scenarios (selectable in UI and on Miro board)

| Scenario ID | Name               | Description                                            | Sources Affected    |
|-------------|--------------------|--------------------------------------------------------|---------------------|
| SCN-01      | Baseline           | Normal working day, moderate activity                  | SRC-02, SRC-03, SRC-04 |
| SCN-02      | Interruption Storm | 40+ Slack messages, 8 PR review requests in 4 hours    | SRC-02, SRC-03      |
| SCN-03      | Sprint Crunch      | 12+ open tickets, 5 reassignments, deadline pressure   | SRC-04              |
| SCN-04      | After-Hours Bleed  | Messages sent 9pm–11pm, calendar events before 8am     | SRC-02, SRC-01 mock |
| SCN-05      | Full Overload      | All of the above combined — demonstrates CRITICAL state| SRC-02, SRC-03, SRC-04|

### 4.3 Unified Work Event Schema

All sources (live and mock) produce events in this shape:

```json
{
  "event_id": "string",
  "source": "calendar | slack | github | jira",
  "mode": "live | mock",
  "type": "meeting | message | pr_review | ticket_update | ...",
  "actor_id": "string (anonymised)",
  "timestamp": "ISO8601",
  "duration_minutes": "integer | null",
  "metadata": {
    "is_after_hours": "boolean",
    "is_back_to_back": "boolean",
    "context_switch": "boolean"
  }
}
SECTION 5 — SIGNAL CATALOG
5.1 Temporal Signals (Source: SRC-01 — Google Calendar LIVE)
Signal ID	Signal Name	Formula / Logic	Range	Weight
T-01	meeting_count_today	Count of calendar events today	0–20+	High
T-02	back_to_back_chains	Sequences with gap < 15 min	0–10+	High
T-03	avg_gap_minutes	Avg minutes between consecutive meetings	0–480	Medium
T-04	after_hours_meetings	Events outside 08:00–18:00	0–10+	High
T-05	total_meeting_hours	Sum of event durations today	0–12+	Medium
T-06	focus_blocks_available	Uninterrupted blocks ≥ 2 hours	0–5+	High
T-07	days_without_break	Consecutive days with >6h meetings	0–30+	High
5.2 Communication Signals (Source: SRC-02 — Slack MOCK)
Signal ID	Signal Name	Formula / Logic	Range	Weight
C-01	messages_sent_today	Total messages sent	0–200+	Medium
C-02	avg_response_time_mins	Avg time from mention to reply	0–480	Medium
C-03	after_hours_messages	Messages sent outside 08:00–18:00	0–50+	High
C-04	sentiment_score_today	NLP sentiment: -1.0 (negative) to 1.0	-1 to 1	Low
C-05	sentiment_trend_delta	sentiment_today minus 7-day avg	-2 to 2	Medium
C-06	channels_active	Distinct channels posted in	0–30+	Low
C-07	dm_vs_channel_ratio	DMs / (DMs + channel posts)	0–1	Low
5.3 Task Signals (Source: SRC-03 GitHub + SRC-04 Jira MOCK)
Signal ID	Signal Name	Formula / Logic	Range	Weight
TA-01	open_prs_count	Active PRs assigned to user	0–20+	High
TA-02	review_requests_today	PR review requests received today	0–15+	High
TA-03	avg_tasks_in_progress	Jira tickets in "In Progress"	0–20+	High
TA-04	ticket_reassignments	Tickets reassigned to user this week	0–10+	Medium
TA-05	context_switches	Branch switches or ticket status changes	0–30+	High
TA-06	incomplete_task_pct	% tasks past due date	0–100	Medium
TA-07	avg_task_age_days	Average age of open tasks in days	0–90+	Low
5.4 Boundary Signals (Cross-source derived)
Signal ID	Signal Name	Formula / Logic	Range	Weight
B-01	boundary_violations	after_hours_meetings + after_hours_messages	0–60+	High
B-02	weekend_work_detected	Events or messages on Saturday/Sunday	boolean	High
B-03	vacation_interrupted	Activity during PTO calendar blocks	boolean	Critical
SECTION 6 — SCORING MODEL
6.1 Component Score Calculation
Each component score is calculated 0–100:

Component	Signals Used	Max Points
Temporal Score	T-01 through T-07	100
Communication Score	C-01 through C-07	100
Task Score	TA-01 through TA-07	100
Boundary Score	B-01 through B-03	100
6.2 Temporal Score Rules (example — full rules for all components follow same pattern)
Condition	Points Added
meeting_count_today >= 8	+25
meeting_count_today >= 5	+15
back_to_back_chains >= 3	+20
back_to_back_chains >= 1	+10
avg_gap_minutes < 10	+15
after_hours_meetings >= 2	+20
focus_blocks_available == 0	+20
days_without_break >= 3	+15
6.3 Composite CL Score
text

CL_SCORE = (
  temporal_score    * 0.30 +
  communication_score * 0.25 +
  task_score        * 0.25 +
  boundary_score    * 0.20
)
6.4 CL Score Bands
Band	Score Range	Colour	Action Required
OPTIMAL	0–30	Green	None
MODERATE	31–50	Yellow	Monitor + suggest focus time
HIGH	51–70	Orange	Trigger protective actions
CRITICAL	71–85	Red	Urgent intervention required
BURNOUT	86–100	Dark Red	Immediate manager alert
6.5 Burnout Risk Probability
text

burnout_risk = sigmoid(CL_SCORE) 
             * sustained_high_load_multiplier  (1.0–1.5)
             * sentiment_degradation_multiplier (1.0–1.3)
             * after_hours_multiplier           (1.0–1.2)
sustained_high_load_multiplier: 1.5 if HIGH/CRITICAL for 3+ consecutive days
sentiment_degradation_multiplier: 1.3 if sentiment_trend_delta < -0.5
after_hours_multiplier: 1.2 if boundary_violations > 5 per day
6.6 Flow State Detection
Flow state = TRUE only when ALL conditions met:

Condition	Value Required
No meetings in next 2 hours	true
focus_blocks_available	>= 2
task_score	< 30
avg_response_time_mins (Slack)	> 45 (slow — user is deep in work)
CL_SCORE	< 40
SECTION 7 — INTERVENTION DECISION TABLE
7.1 Intervention Registry
INT-ID	Intervention Name	Execution Mode	Trigger Condition	Action
INT-01	Add Focus Block	LIVE	focus_blocks_available == 0 AND CL > 50	Create 2h calendar event "Focus Time — CLB Protected"
INT-02	Insert Meeting Buffers	DRY-RUN	back_to_back_chains >= 3	Propose 15-min buffer events between meetings
INT-03	Enable Slack DND	DRY-RUN	after_hours_messages > 5	Set Slack status + enable DND via Slack API
INT-04	Decline Non-Critical Meetings	DRY-RUN	total_meeting_hours > 6 AND CL > 65	Mark optional meetings as "decline" candidates
INT-05	Reduce Sprint Scope	DRY-RUN	avg_tasks_in_progress > 7	Notify PM: "recommend reducing sprint load"
INT-06	Manager Alert	DRY-RUN	CL > 80 OR burnout_risk > 0.75	Private Slack DM to manager with risk summary
INT-07	Vacation Guard	DRY-RUN	vacation_interrupted == true	Alert: "User is on PTO — escalate is blocked"
7.2 Intervention Output Schema
Every intervention (live or dry-run) must produce this record:

JSON

{
  "intervention_id": "string",
  "int_type": "INT-01 | INT-02 | ...",
  "execution_mode": "live | dry-run",
  "triggered_by": ["signal_ids"],
  "cl_score_at_trigger": "integer",
  "timestamp": "ISO8601",
  "action_taken": "string description",
  "outcome": "success | pending | dry-run-planned",
  "miro_card_created": "boolean",
  "before_score": "integer",
  "after_score": "integer | null"
}
7.3 Miro Write-Back Rules
When an intervention fires (live or dry-run), the system MUST:

Create a new card on the Miro board in the "Intervention Log" frame
Card title: [INT-ID] [Intervention Name]
Card body: trigger condition, score at trigger, execution mode (LIVE/DRY-RUN)
Card colour: LIVE = green, DRY-RUN = yellow, FAILED = red
Update the team heatmap widget on the Miro board with the new score
SECTION 8 — MIRO BOARD STRUCTURE (CONTROL PLANE)
The Miro board is not documentation. It is the live control plane for the CLB system. Kiro reads this board via Miro MCP to generate specs and build the system. The running app writes back to this board in real time.

8.1 Required Frames (agent-parseable)
Frame ID	Frame Name	Contents	Machine-Readable Format
F-01	System Overview	Architecture pipeline diagram + tagline	Diagram + text
F-02	Capability Matrix	Data source table (Section 4.1)	Miro Table
F-03	Mock Scenarios	Scenario table (Section 4.2)	Miro Table
F-04	Signal Catalog	All signals (Sections 5.1–5.4)	Miro Tables
F-05	Scoring Model	CL score formula + bands + burnout + flow	Miro Doc + Table
F-06	Intervention Rules	Intervention Decision Table (Section 7.1)	Miro Table
F-07	Privacy & Consent	Data minimisation rules (Section 9)	Miro Doc
F-08	Live Heatmap	Team CL score cards (written by app)	Miro Cards (app-written)
F-09	Intervention Log	Intervention cards (written by app)	Miro Cards (app-written)
F-10	Demo Script	3-minute demo narrative (Section 11)	Miro Doc
8.2 Kiro MCP Configuration (for .kiro/settings/mcp.json)
JSON

{
  "mcpServers": {
    "miro-mcp": {
      "url": "https://mcp.miro.com/",
      "disabled": false,
      "autoApprove": []
    }
  }
}
8.3 Kiro Steering Files Required (for .kiro/steering/)
File	Inclusion	Purpose
product.md	always	Product identity (Section 1)
tech.md	always	Architecture layers (Section 2.2)
structure.md	always	Repo structure and file conventions
miro-rules.md	always	Miro is the control plane — never duplicate rules
data-sources.md	always	Source registry + live vs mock rules (Section 4)
scoring-model.md	always	Scoring formula + bands (Section 6)
interventions.md	always	Intervention rules + dry-run policy (Section 7)
privacy-policy.md	always	Data minimisation + consent rules (Section 9)
SECTION 9 — PRIVACY & CONSENT ARCHITECTURE
9.1 Core Principles
Principle	Implementation
Consent First	No data collected before explicit user opt-in
Data Minimisation	Only derived signals stored — never raw message content
Transparency	Every data point shown in "My Data" dashboard
Right to Delete	One-click data deletion (GDPR Art. 17 compliant)
Mock Safety	Mock mode never touches real user data
Retention Limit	All score data auto-deleted after 90 days
9.2 Consent Levels
Level	What is Collected	What is NOT Collected
BASIC	Calendar event counts and durations only	Event titles, attendees
STANDARD	BASIC + Slack metadata (counts, timing)	Message content
FULL	STANDARD + GitHub/Jira activity metadata	Code content, ticket text
9.3 Data Schema (PostgreSQL)
SQL

-- Cognitive load scores time series
CREATE TABLE cl_scores (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL,
  score         INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
  band          VARCHAR(20) NOT NULL,
  burnout_risk  DECIMAL(4,3),
  flow_state    BOOLEAN DEFAULT FALSE,
  component_scores JSONB,     -- {"temporal": 65, "communication": 40, ...}
  risk_factors  JSONB,        -- ["back_to_back_chains_3", "focus_blocks_0"]
  recommended_interventions JSONB,
  data_mode     VARCHAR(10) DEFAULT 'live',  -- 'live' or 'mock'
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Intervention log
CREATE TABLE interventions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL,
  int_type        VARCHAR(10) NOT NULL,
  execution_mode  VARCHAR(10) NOT NULL,  -- 'live' or 'dry-run'
  triggered_by    JSONB,
  cl_score_before INTEGER,
  cl_score_after  INTEGER,
  action_taken    TEXT,
  outcome         VARCHAR(20),
  miro_card_id    VARCHAR(100),
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Signal snapshots (derived only — no raw content)
CREATE TABLE signal_snapshots (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL,
  signal_id   VARCHAR(10) NOT NULL,
  value       DECIMAL(10,3),
  source_mode VARCHAR(10),  -- 'live' or 'mock'
  captured_at TIMESTAMPTZ DEFAULT NOW()
);
SECTION 10 — KIRO SPEC ARTIFACTS EXPECTED
When Kiro reads the Miro board and this document via MCP, it should generate:

10.1 requirements.md (expected structure)
text

# Requirements: Cognitive Load Balancer
## User Stories
- US01 through US08 (from Section 3.1)
## Acceptance Criteria
- AC01 through AC10 (from Section 3.2)
## Out of Scope for MVP
- Full Slack integration (mock only)
- Full GitHub integration (mock only)
- Full Jira integration (mock only)
- Sentiment analysis (signals defined but not scored in MVP)
10.2 design.md (expected structure)
text

# Technical Design: CLB
## Architecture Diagram
(pipeline from Section 2.1)
## Component Design
- FastAPI backend with WebSocket endpoint
- Next.js frontend with Live/Mock badge system
- LangGraph intervention agent
- Google Calendar OAuth integration
- Miro MCP write-back client
## Data Models
(schemas from Section 9.3)
## API Contracts
(endpoints for /scores, /interventions, /signals, /scenarios, /miro/writeback)
10.3 tasks.md (expected structure)
text

# Implementation Tasks: CLB
Wave 1 (independent, run concurrently):
  - [ ] Set up FastAPI project structure
  - [ ] Configure Google Calendar OAuth
  - [ ] Configure Miro MCP client
  - [ ] Set up PostgreSQL schema
Wave 2 (depends on Wave 1):
  - [ ] Build signal engine (temporal signals from Calendar)
  - [ ] Build mock data providers (Slack/GitHub/Jira scenarios)
  - [ ] Build scoring engine (CL score + bands)
  - [ ] Build Miro write-back service
Wave 3 (depends on Wave 2):
  - [ ] Build LangGraph intervention agent
  - [ ] Build Next.js dashboard (score cards + heatmap)
  - [ ] Build mock scenario toggle UI
  - [ ] Implement INT-01 (Add Focus Block — LIVE)
Wave 4 (depends on Wave 3):
  - [ ] Integrate consent flow
  - [ ] Deploy to live URL
  - [ ] Write intervention cards to Miro board
  - [ ] End-to-end demo test
SECTION 11 — DEMO SCRIPT (3-MINUTE JUDGE NARRATIVE)
11.1 Script
Time	Action	What Judge Sees
0:00	Open Miro board	Structured frames: Capability Matrix, Rules, Log
0:20	Point to F-06 Intervention Rules table	"This table IS the agent's brain — not config"
0:40	Open Kiro. Show MCP connected to Miro	.kiro/settings/mcp.json connected to miro.com
1:00	Show Kiro reading the board	Kiro returns structured content from board frames
1:15	Show .kiro/specs/ directory	requirements.md mirrors board language exactly
1:30	Open live app at deployed URL	Calendar events loading, real CL score showing
1:50	Trigger real INT-01 intervention	Focus block appears in Google Calendar live
2:10	Toggle mock scenario SCN-05 (Full Overload)	Score rises, CRITICAL band, 4 dry-run plans appear
2:25	All dry-run interventions labelled clearly	DRY-RUN badge visible on every planned action
2:35	Show Miro board — new intervention cards	App wrote 5 new cards to F-09 Intervention Log
2:50	Summary: "Miro thinks, Kiro builds, CLB acts"	Close on heatmap frame with live scores
11.2 Key Lines for Judges
"We didn't use Miro as a whiteboard. The board IS the rules engine."
"Kiro didn't get a prompt. It read a structured spec from Miro and built from it."
"Calendar is live. Everything else is showcased through mock scenarios — clearly labelled."
"The agent doesn't just measure load. It protects you from it."
"One data source, one real intervention, five mock scenarios, full architecture — all working."
SECTION 12 — HACKATHON JUDGING ALIGNMENT
Criterion	How CLB Scores a 5
Innovation	Miro-as-rules-engine is a new paradigm. Board drives agent
behaviour at runtime, not just at build time.
Real-World Impact	Burnout is universal. Intervention-not-just-analytics. Consent-
first architecture enables real enterprise deployment.
Tool Usage	Bidirectional Miro↔App loop. Board is config, not docs. Kiro
reads board to build. App writes back to board.
Functional MVP	Live URL. Real Calendar integration. One real intervention.
Mock scenarios extend capability showcase cleanly.
Integration Flow	Kiro reads Miro via MCP → generates spec → builds app → app
writes back to Miro. Causal chain is fully demonstrable.
SECTION 13 — WHAT MUST NEVER CHANGE (AGENT GUARDRAILS)
Any AI agent using this document as a knowledge source MUST NOT:

Invent new signal names, IDs, or formulas not in Section 5
Change the scoring weights or thresholds in Section 6 without explicit user instruction
Treat Slack, GitHub, or Jira as LIVE integrations in MVP scope
Execute INT-02 through INT-07 as real (live) interventions — they are DRY-RUN only
Store raw message content, event titles, or code content — derived signals only
Skip the consent screen before data collection
Create a UI that does not clearly badge LIVE vs MOCK and EXECUTED vs DRY-RUN
Omit the Miro write-back step (Section 7.3) from the implementation
Ignore the /.kiro directory structure — it must be committed to the repo
Present this as a "burnout tracker" — it is a cognitive load intervention agent
SECTION 14 — GLOSSARY
Term	Definition
CL Score	Cognitive Load Score — composite 0-100 metric
Control Plane	The Miro board — authoritative source of system rules
Dry-Run	An intervention that is planned but not executed against real APIs
Flow State	Detected condition of deep, uninterrupted focus work
Live Mode	Data source or intervention using real API with real user data
Mock Mode	Simulated data using predefined scenarios — no real API calls
MCP	Model Context Protocol — how Kiro connects to Miro board
Spec-Driven	Kiro's workflow: requirements → design → tasks → code
Steering File	Persistent context file in .kiro/steering/ that guides Kiro
Write-Back	The CLB app pushing results (scores, cards) to the Miro board
