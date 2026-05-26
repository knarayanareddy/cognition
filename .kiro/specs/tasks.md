# Tasks — Cognitive Load Balancer (CLB) MVP 1.0

> Source of truth: Miro board `https://miro.com/app/board/uXjVHOUD00o=/`
> Tasks derived from acceptance criteria (F-11), architecture pipeline (F-01), and endpoint registry (F-13).
> Each task maps to one or more acceptance criteria.

---

## Phase 1: Foundation & Authentication

### Task 1.1: Project Scaffolding
- [ ] Initialize project structure (frontend + backend)
- [ ] Set up .kiro directory with specs, steering, hooks
- [ ] Configure build tooling and dependency management
- **Acceptance Criteria:** AC10

### Task 1.2: Google Calendar OAuth Integration
- [ ] Implement EP-01: POST /api/v1/auth/google/init (initiate OAuth flow)
- [ ] Implement EP-02: GET /api/v1/auth/google/callback (exchange code for token)
- [ ] Store access token securely for authenticated user
- [ ] Verify real calendar events load successfully
- **Acceptance Criteria:** AC01

### Task 1.3: Privacy Consent Screen
- [ ] Implement consent UI shown before any data collection
- [ ] Support three consent levels: BASIC, STANDARD, FULL
- [ ] Implement EP-15: GET /api/v1/consent/settings
- [ ] Implement EP-16: PUT /api/v1/consent/level
- [ ] Block all data processing until consent is recorded
- **Acceptance Criteria:** AC08

---

## Phase 2: Signal Engine

### Task 2.1: Temporal Signal Extraction (LIVE)
- [ ] Connect to Google Calendar API using stored OAuth token
- [ ] Compute T-01: meeting_count_today (count of calendar events today)
- [ ] Compute T-02: back_to_back_chains (sequences with gap < CFG-11 mins)
- [ ] Compute T-03: avg_gap_minutes (avg minutes between consecutive meetings)
- [ ] Compute T-04: after_hours_meetings (events outside CFG-01 to CFG-02, user TZ)
- [ ] Compute T-05: total_meeting_hours (sum of event durations today)
- [ ] Compute T-06: focus_blocks_available (uninterrupted blocks ≥ 2 hours)
- [ ] Compute T-07: days_without_break (consecutive days with >6h meetings)
- [ ] Respect CFG-01, CFG-02, CFG-07, CFG-11 in all calculations
- **Acceptance Criteria:** AC01, AC02

### Task 2.2: Communication Signal Mock Generator (MOCK)
- [ ] Build mock data generator for Slack signals (SRC-02)
- [ ] Generate C-01 through C-07 values based on active scenario
- [ ] Support scenario variations: Baseline, Interruption Storm, After-Hours Bleed, Full Overload
- [ ] Badge all mock data with MOCK indicator
- **Acceptance Criteria:** AC04

### Task 2.3: Task Signal Mock Generator (MOCK)
- [ ] Build mock data generator for GitHub (SRC-03) and Jira (SRC-04) signals
- [ ] Generate TA-01 through TA-07 values based on active scenario
- [ ] Support scenario variations: Baseline, PR Storm, Review Overload, Sprint Crunch, Reassign Chaos, Full Overload
- [ ] Badge all mock data with MOCK indicator
- **Acceptance Criteria:** AC04

### Task 2.4: Boundary Signal Derivation
- [ ] Compute B-01: boundary_violations (after_hours_meetings + after_hours_messages)
- [ ] Compute B-02: weekend_work_detected (activity on days not in CFG-04)
- [ ] Compute B-03: vacation_interrupted (activity during PTO calendar blocks)
- [ ] Respect CFG-01, CFG-02, CFG-03, CFG-04 in boundary calculations
- **Acceptance Criteria:** AC02

### Task 2.5: Signal API Endpoint
- [ ] Implement EP-05: GET /api/v1/signals/current (all 24 signal snapshots)
- [ ] Include signal_id, value, source_mode (LIVE/MOCK), captured_at for each signal
- **Acceptance Criteria:** AC02

---

## Phase 3: Scoring Engine

### Task 3.1: Component Score Calculation
- [ ] Calculate temporal_score (0–100) from T-01 through T-07 using signal thresholds
- [ ] Calculate communication_score (0–100) from C-01 through C-07
- [ ] Calculate task_score (0–100) from TA-01 through TA-07
- [ ] Calculate boundary_score (0–100) from B-01 through B-03
- **Acceptance Criteria:** AC02

### Task 3.2: Composite CL Score
- [ ] Implement weighted formula: temporal*0.30 + communication*0.25 + task*0.25 + boundary*0.20
- [ ] Map score to band: OPTIMAL(0–30), MODERATE(31–50), HIGH(51–70), CRITICAL(71–85), BURNOUT(86–100)
- [ ] Refresh every CFG-09 minutes (default 15)
- **Acceptance Criteria:** AC02

### Task 3.3: Burnout Risk Calculation
- [ ] Implement sigmoid(CL_SCORE) base calculation
- [ ] Apply sustained_high_load_multiplier (1.5 if HIGH/CRITICAL for 3+ consecutive days)
- [ ] Apply sentiment_degradation_multiplier (1.3 if sentiment_trend_delta < -0.5)
- [ ] Apply after_hours_multiplier (1.2 if boundary_violations > 5 per day)
- **Acceptance Criteria:** AC02

### Task 3.4: Flow State Detection
- [ ] Evaluate all 5 conditions simultaneously (no meetings in 2h, focus_blocks >= 2, task_score < 30, avg_response_time > 45, CL_SCORE < 40)
- [ ] Flow state = TRUE only when ALL conditions met
- **Acceptance Criteria:** AC02

### Task 3.5: Score API Endpoints
- [ ] Implement EP-03: GET /api/v1/scores/current
- [ ] Implement EP-04: GET /api/v1/scores/history (max 90 days, per CFG-08)
- [ ] Implement EP-12: WS /api/v1/scores/stream (WebSocket, 15-min refresh)
- **Acceptance Criteria:** AC02

---

## Phase 4: Intervention Agent

### Task 4.1: INT-01 — Add Focus Block (LIVE)
- [ ] Evaluate trigger: focus_blocks_available == 0 AND CL > 50
- [ ] Create 2h Google Calendar event titled "Focus Time — CLB Protected"
- [ ] Duration configurable via CFG-10 (default 120 mins)
- [ ] Verify event appears in user's actual Google Calendar
- [ ] Log as LIVE execution with green card colour
- **Acceptance Criteria:** AC03

### Task 4.2: INT-02 through INT-07 (DRY-RUN)
- [ ] INT-02: Evaluate back_to_back_chains >= 3 → plan 15-min buffer events
- [ ] INT-03: Evaluate after_hours_messages > 5 → plan Slack DND
- [ ] INT-04: Evaluate total_meeting_hours > 6 AND CL > 65 → plan meeting declines
- [ ] INT-05: Evaluate avg_tasks_in_progress > 7 → plan sprint scope reduction
- [ ] INT-06: Evaluate CL > 80 OR burnout_risk > 0.75 → plan manager alert
- [ ] INT-07: Evaluate vacation_interrupted == true → plan vacation guard
- [ ] All logged as DRY-RUN (planned but NOT executed)
- [ ] All display DRY-RUN badge in UI
- **Acceptance Criteria:** AC05

### Task 4.3: Intervention API Endpoints
- [ ] Implement EP-09: GET /api/v1/interventions/history
- [ ] Implement EP-10: POST /api/v1/interventions/trigger (demo use only)
- **Acceptance Criteria:** AC03, AC05

---

## Phase 5: Mock Scenario System

### Task 5.1: Scenario Management
- [ ] Implement EP-06: GET /api/v1/scenarios (list SCN-01 through SCN-05)
- [ ] Implement EP-07: POST /api/v1/scenarios/activate
- [ ] Implement EP-08: POST /api/v1/scenarios/deactivate
- [ ] Scenario toggle visible in dashboard UI
- [ ] Selected scenario updates CL score in real time
- **Acceptance Criteria:** AC04

### Task 5.2: Scenario Data Profiles
- [ ] SCN-01 (Baseline): Normal working day, moderate activity across SRC-02, SRC-03, SRC-04
- [ ] SCN-02 (Interruption Storm): 40+ Slack messages, 8 PR review requests in 4 hours
- [ ] SCN-03 (Sprint Crunch): 12+ open tickets, 5 reassignments, deadline pressure
- [ ] SCN-04 (After-Hours Bleed): Messages 9pm–11pm, calendar events before 8am
- [ ] SCN-05 (Full Overload): All combined — demonstrates CRITICAL state
- **Acceptance Criteria:** AC04

---

## Phase 6: Miro Write-Back

### Task 6.1: Intervention Card Write-Back
- [ ] Implement EP-13: POST /api/v1/miro/intervention-card
- [ ] Write card to Miro frame F-09 with: INT-ID, name, execution mode badge, trigger condition, CL score, action taken, outcome, timestamp
- [ ] Apply card colour rules: LIVE+success=green, DRY-RUN=yellow, FAILED=red
- [ ] Verify cards appear on Miro board after intervention fires
- **Acceptance Criteria:** AC07

### Task 6.2: Heatmap Update Write-Back
- [ ] Implement EP-14: POST /api/v1/miro/heatmap-update
- [ ] Write/update card in Miro frame F-08 with: user ID, CL score, band, burnout risk, flow state, data mode badge, timestamp
- [ ] Update every 15 minutes (per CFG-09)
- **Acceptance Criteria:** AC07

---

## Phase 7: Dashboard UI

### Task 7.1: Main Dashboard
- [ ] Display current CL Score with band colour coding
- [ ] Show burnout risk percentage
- [ ] Show flow state indicator
- [ ] Display all 24 signals with current values
- [ ] Badge every data card with LIVE or MOCK indicator
- **Acceptance Criteria:** AC02, AC04, AC05

### Task 7.2: Intervention Panel
- [ ] List all interventions (live and dry-run)
- [ ] Display LIVE/DRY-RUN badge on every intervention card
- [ ] Show trigger condition, CL score at trigger, action taken, outcome
- **Acceptance Criteria:** AC03, AC05

### Task 7.3: Scenario Toggle
- [ ] Dropdown or toggle UI for SCN-01 through SCN-05
- [ ] Real-time score update when scenario changes
- [ ] Clear MOCK badge when scenario is active
- **Acceptance Criteria:** AC04

### Task 7.4: Team Heatmap View
- [ ] Implement EP-11: GET /api/v1/team/heatmap
- [ ] Display all team members with CL scores, bands, burnout risk, flow state
- [ ] Colour-coded by band (Green/Yellow/Orange/Red/Dark Red)
- **Acceptance Criteria:** AC07

---

## Phase 8: System & Operations

### Task 8.1: Health & Configuration
- [ ] Implement EP-18: GET /api/v1/health (public, no auth)
- [ ] Implement EP-19: GET /api/v1/config (returns CFG-01 through CFG-12)
- [ ] Implement EP-20: PATCH /api/v1/config (partial updates)
- [ ] Changes to CFG-01–04 trigger immediate signal recalculation
- **Acceptance Criteria:** AC09

### Task 8.2: Data Deletion (GDPR)
- [ ] Implement EP-17: DELETE /api/v1/user/data
- [ ] One-click deletion of all scores, interventions, signals
- [ ] GDPR Art. 17 compliant
- **Acceptance Criteria:** AC08

### Task 8.3: Demo Mode
- [ ] When CFG-05 = true: switch all sources to mock, display "DEMO MODE" banner
- [ ] Load pre-configured persona data using CFG-06 actor name
- [ ] All interventions remain DRY-RUN in demo mode
- [ ] Demo sessions expire after 24 hours
- **Acceptance Criteria:** AC04, AC05

### Task 8.4: Deployment
- [ ] Deploy to accessible URL for judge review
- [ ] Verify all endpoints respond correctly
- [ ] Confirm Miro MCP connection works from deployed environment
- **Acceptance Criteria:** AC09

---

## Phase 9: Repository & Kiro Integration

### Task 9.1: .kiro Directory Structure
- [ ] Commit .kiro/specs/requirements.md (this file set)
- [ ] Commit .kiro/specs/design.md
- [ ] Commit .kiro/specs/tasks.md
- [ ] Add steering files as needed
- [ ] Add hooks as needed
- **Acceptance Criteria:** AC06, AC10

### Task 9.2: Verify Miro-to-Kiro Pipeline
- [ ] Confirm Kiro reads Miro board via MCP
- [ ] Confirm generated specs mirror board language exactly
- [ ] Confirm .kiro/specs/ directory contains output matching board frames
- **Acceptance Criteria:** AC06
