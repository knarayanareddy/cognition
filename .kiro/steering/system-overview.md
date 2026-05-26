---
inclusion: always
---

# CLB System Overview & Agent Guardrails

> Source: Miro board frames F-01, F-12

## Product Identity

- **Product Name:** Cognitive Load Balancer (CLB)
- **Tagline:** Your Miro board thinks. Your agent acts.
- **Version:** MVP 1.0 (Hackathon Submission)
- **Classification:** Cognitive load intervention agent (NOT a "burnout tracker")

## Architecture Pipeline

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

## Key Differentiator

The Miro board IS the rules engine. Kiro reads the board via Miro MCP to build the system. The agent writes results back to the board. Miro is not documentation — it is infrastructure.

## Agent Guardrails (F-12) — MUST NOT:

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
