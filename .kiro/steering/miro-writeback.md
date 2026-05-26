---
inclusion: always
---

# CLB Miro Write-Back Rules

> Source: Miro board frames F-08, F-09

## F-08: Live Heatmap

### Purpose
Real-time team cognitive load visualization. Updated by CLB app every 15 minutes (per CFG-09).

### Card Format (one per user)
- User ID (anonymised)
- Current CL Score (0-100)
- Band (OPTIMAL / MODERATE / HIGH / CRITICAL / BURNOUT)
- Burnout Risk % (0-100)
- Flow State (true/false)
- Data Mode badge (LIVE or MOCK)
- Last Updated timestamp

### API
- **EP-14**: `POST /api/v1/miro/heatmap-update`
- Request: `{user_id, cl_score, band, burnout_risk, flow_state, data_mode}`
- Response: `{miro_card_id, frame_id: "F-08", card_url}`

### Requirement
Must use Miro MCP write-back API to create/update cards in this frame. Non-negotiable core feature (AC07).

---

## F-09: Intervention Log

### Purpose
Audit trail of all interventions (live and dry-run). Written by CLB app when interventions fire.

### Card Format (one per intervention)
- INT-ID (e.g., INT-01, INT-02)
- Intervention Name
- Execution Mode badge (LIVE or DRY-RUN)
- Trigger Condition (which signals caused it)
- CL Score at Trigger
- Action Taken (description)
- Outcome (success / pending / dry-run-planned)
- Timestamp

### Card Colour Rules
- LIVE + success = green
- DRY-RUN = yellow
- FAILED = red

### API
- **EP-13**: `POST /api/v1/miro/intervention-card`
- Request: `{intervention_id, int_type, execution_mode, trigger_condition, cl_score, action_taken, outcome}`
- Response: `{miro_card_id, frame_id: "F-09", card_url}`

### Requirement
Must use Miro MCP write-back API. Every intervention must create a card here. Non-negotiable core feature (AC07).
