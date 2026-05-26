---
inclusion: always
---

# CLB Scoring Model

> Source: Miro board frame F-05

## Composite CL Score Formula

```
CL_SCORE = (
  temporal_score      * 0.30 +
  communication_score * 0.25 +
  task_score          * 0.25 +
  boundary_score      * 0.20
)
```

Each component score calculated 0–100 using signal thresholds.

## CL Score Bands

| Band     | Score Range | Colour   | Action Required                |
|----------|-------------|----------|--------------------------------|
| OPTIMAL  | 0–30        | Green    | None                           |
| MODERATE | 31–50       | Yellow   | Monitor + suggest focus time   |
| HIGH     | 51–70       | Orange   | Trigger protective actions     |
| CRITICAL | 71–85       | Red      | Urgent intervention required   |
| BURNOUT  | 86–100      | Dark Red | Immediate manager alert        |

## Burnout Risk Probability

```
burnout_risk = sigmoid(CL_SCORE)
             * sustained_high_load_multiplier  (1.0–1.5)
             * sentiment_degradation_multiplier (1.0–1.3)
             * after_hours_multiplier           (1.0–1.2)
```

### Multipliers
- **sustained_high_load_multiplier**: 1.5 if HIGH/CRITICAL for 3+ consecutive days
- **sentiment_degradation_multiplier**: 1.3 if sentiment_trend_delta < -0.5
- **after_hours_multiplier**: 1.2 if boundary_violations > 5 per day

## Flow State Detection

Flow state = TRUE only when ALL conditions met:

| Condition                          | Value Required |
|------------------------------------|----------------|
| No meetings in next 2 hours        | true           |
| focus_blocks_available             | >= 2           |
| task_score                         | < 30           |
| avg_response_time_mins (Slack)     | > 45           |
| CL_SCORE                           | < 40           |
