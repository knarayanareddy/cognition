---
inclusion: always
---

# CLB Privacy & Consent Policy

> Source: Miro board frame F-07 + KIRO STEERING FILE document on board
> DO NOT modify without updating Miro board first

## Core Principles

| Principle        | Implementation                                      |
|------------------|-----------------------------------------------------|
| Consent First    | No data collected before explicit user opt-in       |
| Data Minimisation| Only derived signals stored — never raw content     |
| Transparency     | Every data point shown in "My Data" dashboard       |
| Right to Delete  | One-click data deletion (GDPR Art. 17 compliant)   |
| Mock Safety      | Mock mode never touches real user data              |
| Retention Limit  | All score data auto-deleted after CFG-08 days (default: 90) |

## Consent Levels

| Level    | What is Collected                              | What is NOT Collected     |
|----------|------------------------------------------------|---------------------------|
| BASIC    | Calendar event counts and durations only       | Event titles, attendees   |
| STANDARD | BASIC + Slack metadata (counts, timing)        | Message content           |
| FULL     | STANDARD + GitHub/Jira activity metadata       | Code content, ticket text |

## Data Schema (PostgreSQL)

### cl_scores table
- `id` (UUID, primary key)
- `user_id` (UUID, not null)
- `score` (integer, 0–100)
- `band` (varchar: OPTIMAL/MODERATE/HIGH/CRITICAL/BURNOUT)
- `burnout_risk` (decimal)
- `flow_state` (boolean)
- `component_scores` (JSONB: temporal, communication, task, boundary)
- `risk_factors` (JSONB: array of signal IDs that triggered)
- `recommended_interventions` (JSONB)
- `data_mode` (varchar: live | mock)
- `created_at` (timestamptz)

### interventions table
- `id` (UUID, primary key)
- `user_id` (UUID, not null)
- `int_type` (varchar: INT-01 through INT-07)
- `execution_mode` (varchar: live | dry-run)
- `triggered_by` (JSONB: array of signal IDs)
- `cl_score_before` (integer)
- `cl_score_after` (integer, nullable)
- `action_taken` (text)
- `outcome` (varchar: success | pending | dry-run-planned)
- `miro_card_id` (varchar)
- `created_at` (timestamptz)

### signal_snapshots table
- `id` (UUID, primary key)
- `user_id` (UUID, not null)
- `signal_id` (varchar: T-*, C-*, TA-*, B-*)
- `value` (decimal)
- `source_mode` (varchar: live | mock)
- `captured_at` (timestamptz)

## API Endpoints

- **EP-15**: `GET /api/v1/consent/settings` → fetch current consent level
- **EP-16**: `PUT /api/v1/consent/level` → update consent level
- **EP-17**: `DELETE /api/v1/user/data` → GDPR erasure (Art. 17 compliant)

## MVP Requirement

Consent screen must be shown before any data collection begins (AC08).

## Critical Rules

1. Never store raw message content, event titles, or code content
2. Only derived signals (counts, durations, metadata) are stored
3. User can delete all data with one click (EP-17)
4. Data retention: CFG-08 days (default 90), then auto-deleted
5. Mock mode never writes to production integrations
