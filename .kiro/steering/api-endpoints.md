---
inclusion: always
---

# CLB API Endpoint Registry & System Configuration

> Source: Miro board frames F-13, F-14

## API Endpoint Registry (F-13)

### Authentication (No Auth Required)
| EP-ID | Method | Path                          | Description                        |
|-------|--------|-------------------------------|------------------------------------|
| EP-01 | POST   | /api/v1/auth/google/init      | Initiate Google Calendar OAuth     |
| EP-02 | GET    | /api/v1/auth/google/callback  | Google Calendar OAuth callback     |

### Scores (Auth Required)
| EP-ID | Method | Path                     | Description                              |
|-------|--------|--------------------------|------------------------------------------|
| EP-03 | GET    | /api/v1/scores/current   | Current CL score for authenticated user  |
| EP-04 | GET    | /api/v1/scores/history   | CL score time series (max 90 days)       |
| EP-12 | WS     | /api/v1/scores/stream    | WebSocket real-time score updates (15-min refresh) |

### Signals (Auth Required)
| EP-ID | Method | Path                     | Description                    |
|-------|--------|--------------------------|--------------------------------|
| EP-05 | GET    | /api/v1/signals/current  | All 24 signal snapshots        |

### Scenarios (Auth Required)
| EP-ID | Method | Path                          | Description                        |
|-------|--------|-------------------------------|------------------------------------|
| EP-06 | GET    | /api/v1/scenarios             | List mock scenarios (SCN-01–05)    |
| EP-07 | POST   | /api/v1/scenarios/activate    | Activate a mock scenario           |
| EP-08 | POST   | /api/v1/scenarios/deactivate  | Deactivate mock, return to live    |

### Interventions (Auth Required)
| EP-ID | Method | Path                            | Description                      |
|-------|--------|----------------------------------|----------------------------------|
| EP-09 | GET    | /api/v1/interventions/history    | Intervention history (live+dry)  |
| EP-10 | POST   | /api/v1/interventions/trigger    | Manually trigger (demo only)     |

### Team (Auth Required)
| EP-ID | Method | Path                    | Description                    |
|-------|--------|-------------------------|--------------------------------|
| EP-11 | GET    | /api/v1/team/heatmap    | Team heatmap data (all users)  |

### Miro Write-Back (Auth Required)
| EP-ID | Method | Path                            | Description                          |
|-------|--------|----------------------------------|--------------------------------------|
| EP-13 | POST   | /api/v1/miro/intervention-card   | Create intervention card on Miro     |
| EP-14 | POST   | /api/v1/miro/heatmap-update      | Update team heatmap frame on Miro    |

### Consent & Privacy (Auth Required)
| EP-ID | Method | Path                     | Description                        |
|-------|--------|--------------------------|-------------------------------------|
| EP-15 | GET    | /api/v1/consent/settings | Fetch user consent settings         |
| EP-16 | PUT    | /api/v1/consent/level    | Update user consent level           |
| EP-17 | DELETE | /api/v1/user/data        | Delete all user data (GDPR Art.17)  |

### System
| EP-ID | Method | Path              | Description                    | Auth |
|-------|--------|-------------------|--------------------------------|------|
| EP-18 | GET    | /api/v1/health    | Health check / system status   | No   |
| EP-19 | GET    | /api/v1/config    | Fetch system configuration     | Yes  |
| EP-20 | PATCH  | /api/v1/config    | Update system configuration    | Yes  |

**Guardrail:** No endpoint should be added, removed, or renamed without explicit user instruction.

---

## System Configuration (F-14)

| Config ID | Parameter Name                  | Type    | Default                      | Valid Range                    | Used By              |
|-----------|---------------------------------|---------|------------------------------|--------------------------------|----------------------|
| CFG-01    | work_hours_start                | time    | 08:00                        | 00:00–23:59 (user TZ)         | T-04, C-03, B-01     |
| CFG-02    | work_hours_end                  | time    | 18:00                        | 00:00–23:59 (user TZ)         | T-04, C-03, B-01     |
| CFG-03    | after_hours_threshold_mins      | integer | 30                           | 0–180                          | B-01                 |
| CFG-04    | work_days                       | array   | [Mon,Tue,Wed,Thu,Fri]        | Any subset of [Mon–Sun]        | B-02                 |
| CFG-05    | demo_mode_enabled               | boolean | false                        | true / false                   | All sources          |
| CFG-06    | demo_actor_name                 | string  | "Alex Chen"                  | Any string (1–50 chars)        | UI display           |
| CFG-07    | timezone                        | string  | "America/Los_Angeles"        | Valid IANA timezone             | T-04, C-03, B-01, B-02 |
| CFG-08    | data_retention_days             | integer | 90                           | 30–365                         | Data cleanup         |
| CFG-09    | score_refresh_interval_mins     | integer | 15                           | 5–60                           | Scoring engine       |
| CFG-10    | focus_block_duration_mins       | integer | 120                          | 60–240                         | INT-01               |
| CFG-11    | back_to_back_gap_threshold_mins | integer | 15                           | 0–30                           | T-02                 |
| CFG-12    | weekend_alert_enabled           | boolean | true                         | true / false                   | B-02                 |

### Configuration Rules
- All time-based configs (CFG-01, CFG-02, CFG-07) must be respected by signals T-04, C-03, B-01, B-02
- Changes to CFG-01 through CFG-04 require immediate signal recalculation
- CFG-05 and CFG-06 control demo mode behavior
- CFG-09 controls the refresh rate of the entire scoring pipeline
- Configuration must be user-specific (not system-wide) unless explicitly shared at team level
