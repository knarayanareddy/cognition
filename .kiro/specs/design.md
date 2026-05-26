# Design — Cognitive Load Balancer (CLB) MVP 1.0

> Source of truth: Miro board `https://miro.com/app/board/uXjVHOUD00o=/`
> Derived from frames F-01, F-05, F-06, F-08, F-09, F-13, F-14.
> All architecture, endpoints, and configuration below are strictly from board content.

---

## 1. Architecture Pipeline (F-01)

```
[MIRO BOARD — Rules Engine + Control Plane]
        ↓ Kiro reads via Miro MCP Server
[KIRO — Spec-Driven Development]
        ↓ Generates requirements.md + design.md + tasks.md
[CLB APPLICATION — Built by Kiro]
        ↓ Ingests work signals
[DATA SOURCES: Calendar(LIVE) / Slack(MOCK) / GitHub(MOCK) / Jira(MOCK)]
        ↓ Computes
[SIGNAL ENGINE → SCORING ENGINE → CL SCORE + BURNOUT RISK + FLOW STATE]
        ↓ Triggers
[INTERVENTION AGENT — LangGraph Orchestrated]
        ↓ Executes or Dry-Runs
[INTERVENTIONS: Calendar(LIVE) / Slack(DRY-RUN) / Jira(DRY-RUN) / Manager(DRY-RUN)]
        ↓ Writes back
[MIRO BOARD — Live Heatmap + Intervention Cards + Score Updates]
```

### Key Design Decisions
- LangGraph orchestrates the intervention agent
- WebSocket (EP-12) provides real-time score streaming at 15-minute intervals
- Miro MCP write-back is a non-negotiable core feature (AC07)
- Only Google Calendar has LIVE OAuth integration; all other sources use mock data generators

---

## 2. Scoring Engine Design (F-05)

### Component Score Calculation
Each of the 4 component scores (temporal, communication, task, boundary) is calculated 0–100 using signal thresholds from F-04.

### Composite Formula
```
CL_SCORE = (
  temporal_score      * 0.30 +
  communication_score * 0.25 +
  task_score          * 0.25 +
  boundary_score      * 0.20
)
```

### Burnout Risk Formula
```
burnout_risk = sigmoid(CL_SCORE)
             * sustained_high_load_multiplier  (1.0–1.5)
             * sentiment_degradation_multiplier (1.0–1.3)
             * after_hours_multiplier           (1.0–1.2)
```

### Flow State Logic
All conditions must be TRUE simultaneously:
- No meetings in next 2 hours
- focus_blocks_available >= 2
- task_score < 30
- avg_response_time_mins > 45
- CL_SCORE < 40

---

## 3. Intervention Agent Design (F-06)

### Execution Modes
- **LIVE**: Action is executed for real (only INT-01 — creates Google Calendar event)
- **DRY-RUN**: Action is planned and logged but NOT executed (INT-02 through INT-07)

### Intervention Flow
1. Scoring engine produces CL_SCORE + component scores
2. Intervention agent evaluates trigger conditions from F-06 table
3. If triggered:
   - LIVE (INT-01): Execute via Google Calendar API → create "Focus Time — CLB Protected" event
   - DRY-RUN (INT-02–07): Log planned action with full context
4. Write intervention card to Miro frame F-09 (via EP-13)
5. Update team heatmap in Miro frame F-08 (via EP-14)

### Card Colour Rules (F-09)
- LIVE + success = green
- DRY-RUN = yellow
- FAILED = red

---

## 4. Miro Write-Back Design (F-08, F-09)

### F-08: Live Heatmap
Cards written per user containing:
- User ID (anonymised)
- Current CL Score (0-100)
- Band (OPTIMAL / MODERATE / HIGH / CRITICAL / BURNOUT)
- Burnout Risk % (0-100)
- Flow State (true/false)
- Data Mode badge (LIVE or MOCK)
- Last Updated timestamp

Updated every 15 minutes via EP-14.

### F-09: Intervention Log
Cards written per intervention containing:
- INT-ID (e.g., INT-01, INT-02)
- Intervention Name
- Execution Mode badge (LIVE or DRY-RUN)
- Trigger Condition (which signals caused it)
- CL Score at Trigger
- Action Taken (description)
- Outcome (success / pending / dry-run-planned)
- Timestamp

Written via EP-13 whenever an intervention fires.

---

## 5. API Endpoint Registry (F-13)

### Authentication
| EP-ID | Method | Path                          | Description                        | Auth |
|-------|--------|-------------------------------|------------------------------------|------|
| EP-01 | POST   | /api/v1/auth/google/init      | Initiate Google Calendar OAuth     | No   |
| EP-02 | GET    | /api/v1/auth/google/callback  | Google Calendar OAuth callback     | No   |

### Scores
| EP-ID | Method | Path                     | Description                              | Auth |
|-------|--------|--------------------------|------------------------------------------|------|
| EP-03 | GET    | /api/v1/scores/current   | Current CL score for authenticated user  | Yes  |
| EP-04 | GET    | /api/v1/scores/history   | CL score time series (max 90 days)       | Yes  |
| EP-12 | WS     | /api/v1/scores/stream    | WebSocket real-time score updates        | Yes  |

### Signals
| EP-ID | Method | Path                     | Description                    | Auth |
|-------|--------|--------------------------|--------------------------------|------|
| EP-05 | GET    | /api/v1/signals/current  | All 24 signal snapshots        | Yes  |

### Scenarios
| EP-ID | Method | Path                          | Description                        | Auth |
|-------|--------|-------------------------------|------------------------------------|------|
| EP-06 | GET    | /api/v1/scenarios             | List mock scenarios (SCN-01–05)    | Yes  |
| EP-07 | POST   | /api/v1/scenarios/activate    | Activate a mock scenario           | Yes  |
| EP-08 | POST   | /api/v1/scenarios/deactivate  | Deactivate mock, return to live    | Yes  |

### Interventions
| EP-ID | Method | Path                            | Description                      | Auth |
|-------|--------|----------------------------------|----------------------------------|------|
| EP-09 | GET    | /api/v1/interventions/history    | Intervention history (live+dry)  | Yes  |
| EP-10 | POST   | /api/v1/interventions/trigger    | Manually trigger (demo only)     | Yes  |

### Team
| EP-ID | Method | Path                    | Description                    | Auth |
|-------|--------|-------------------------|--------------------------------|------|
| EP-11 | GET    | /api/v1/team/heatmap    | Team heatmap data (all users)  | Yes  |

### Miro Write-Back
| EP-ID | Method | Path                            | Description                          | Auth |
|-------|--------|----------------------------------|--------------------------------------|------|
| EP-13 | POST   | /api/v1/miro/intervention-card   | Create intervention card on Miro     | Yes  |
| EP-14 | POST   | /api/v1/miro/heatmap-update      | Update team heatmap frame on Miro    | Yes  |

### Consent & Privacy
| EP-ID | Method | Path                     | Description                        | Auth |
|-------|--------|--------------------------|-------------------------------------|------|
| EP-15 | GET    | /api/v1/consent/settings | Fetch user consent settings         | Yes  |
| EP-16 | PUT    | /api/v1/consent/level    | Update user consent level           | Yes  |
| EP-17 | DELETE | /api/v1/user/data        | Delete all user data (GDPR Art.17)  | Yes  |

### System
| EP-ID | Method | Path              | Description                    | Auth |
|-------|--------|-------------------|--------------------------------|------|
| EP-18 | GET    | /api/v1/health    | Health check / system status   | No   |
| EP-19 | GET    | /api/v1/config    | Fetch system configuration     | Yes  |
| EP-20 | PATCH  | /api/v1/config    | Update system configuration    | Yes  |

**Guardrail:** No endpoint should be added, removed, or renamed without explicit user instruction.

---

## 6. System Configuration (F-14)

| Config ID | Parameter Name                  | Type    | Default                      | Valid Range                              | Used By        |
|-----------|---------------------------------|---------|------------------------------|------------------------------------------|----------------|
| CFG-01    | work_hours_start                | time    | 08:00                        | 00:00–23:59 (user TZ)                   | T-04, C-03, B-01 |
| CFG-02    | work_hours_end                  | time    | 18:00                        | 00:00–23:59 (user TZ)                   | T-04, C-03, B-01 |
| CFG-03    | after_hours_threshold_mins      | integer | 30                           | 0–180                                    | B-01           |
| CFG-04    | work_days                       | array   | [Mon,Tue,Wed,Thu,Fri]        | Any subset of [Mon–Sun]                  | B-02           |
| CFG-05    | demo_mode_enabled               | boolean | false                        | true / false                             | All sources    |
| CFG-06    | demo_actor_name                 | string  | "Alex Chen"                  | Any string (1–50 chars)                  | UI display     |
| CFG-07    | timezone                        | string  | "America/Los_Angeles"        | Valid IANA timezone                       | T-04, C-03, B-01, B-02 |
| CFG-08    | data_retention_days             | integer | 90                           | 30–365                                   | Data cleanup   |
| CFG-09    | score_refresh_interval_mins     | integer | 15                           | 5–60                                     | Scoring engine |
| CFG-10    | focus_block_duration_mins       | integer | 120                          | 60–240                                   | INT-01         |
| CFG-11    | back_to_back_gap_threshold_mins | integer | 15                           | 0–30                                     | T-02           |
| CFG-12    | weekend_alert_enabled           | boolean | true                         | true / false                             | B-02           |

### Configuration Rules
- All time-based configs (CFG-01, CFG-02, CFG-07) must be respected by signals T-04, C-03, B-01, B-02
- Changes to CFG-01 through CFG-04 require immediate signal recalculation
- CFG-05 and CFG-06 control demo mode behavior
- CFG-09 controls the refresh rate of the entire scoring pipeline
- Configuration must be user-specific (not system-wide) unless explicitly shared at team level

### Demo Mode (CFG-05 = true)
When enabled:
1. All data sources switch to mock mode (overrides SRC-01 LIVE temporarily)
2. UI displays "DEMO MODE" banner with actor name from CFG-06
3. Pre-configured persona data loads (8 meetings/day, 2 back-to-back chains, 1 after-hours event, 45 Slack messages/day, 5 open PRs, 8 tasks in progress)
4. CL score immediately recalculates using demo signals
5. All interventions remain in DRY-RUN mode
6. Miro board updates with demo actor cards in F-08 and F-09

**Demo Mode Guardrails:**
- Never write demo data to production integrations
- Always display DEMO MODE badge prominently in UI
- Demo mode sessions expire after 24 hours unless renewed
