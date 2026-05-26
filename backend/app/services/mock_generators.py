"""Mock Data Generators for MOCK sources (SRC-02, SRC-03, SRC-04).

Communication signals (C-01 to C-07): Slack MOCK — SRC-02
Task signals (TA-01 to TA-07): GitHub MOCK (SRC-03) + Jira MOCK (SRC-04)

All signal definitions strictly from F-04. No invented signals.
All mock data clearly badged with MOCK indicator.

Scenario profiles from F-03:
- SCN-01: Baseline — Normal working day, moderate activity
- SCN-02: Interruption Storm — 40+ Slack messages, 8 PR review requests in 4 hours
- SCN-03: Sprint Crunch — 12+ open tickets, 5 reassignments, deadline pressure
- SCN-04: After-Hours Bleed — Messages 9pm–11pm, calendar events before 8am
- SCN-05: Full Overload — All combined, demonstrates CRITICAL state
"""

import random
from dataclasses import dataclass


@dataclass
class MockSignalProfile:
    """Signal values for a specific scenario."""

    # Communication signals (C-01 to C-07)
    messages_sent_today: float  # C-01
    avg_response_time_mins: float  # C-02
    after_hours_messages: float  # C-03
    sentiment_score_today: float  # C-04
    sentiment_trend_delta: float  # C-05
    channels_active: float  # C-06
    dm_vs_channel_ratio: float  # C-07

    # Task signals (TA-01 to TA-07)
    open_prs_count: float  # TA-01
    review_requests_today: float  # TA-02
    avg_tasks_in_progress: float  # TA-03
    ticket_reassignments: float  # TA-04
    context_switches: float  # TA-05
    incomplete_task_pct: float  # TA-06
    avg_task_age_days: float  # TA-07


# Scenario profiles derived strictly from F-03 descriptions
SCENARIO_PROFILES: dict[str, MockSignalProfile] = {
    # SCN-01: Baseline — Normal working day, moderate activity
    "SCN-01": MockSignalProfile(
        messages_sent_today=25,
        avg_response_time_mins=15,
        after_hours_messages=1,
        sentiment_score_today=0.6,
        sentiment_trend_delta=0.0,
        channels_active=5,
        dm_vs_channel_ratio=0.3,
        open_prs_count=2,
        review_requests_today=1,
        avg_tasks_in_progress=4,
        ticket_reassignments=0,
        context_switches=5,
        incomplete_task_pct=10,
        avg_task_age_days=5,
    ),
    # SCN-02: Interruption Storm — 40+ Slack messages, 8 PR review requests in 4 hours
    "SCN-02": MockSignalProfile(
        messages_sent_today=45,
        avg_response_time_mins=5,
        after_hours_messages=3,
        sentiment_score_today=0.2,
        sentiment_trend_delta=-0.4,
        channels_active=12,
        dm_vs_channel_ratio=0.6,
        open_prs_count=6,
        review_requests_today=8,
        avg_tasks_in_progress=5,
        ticket_reassignments=1,
        context_switches=18,
        incomplete_task_pct=20,
        avg_task_age_days=8,
    ),
    # SCN-03: Sprint Crunch — 12+ open tickets, 5 reassignments, deadline pressure
    "SCN-03": MockSignalProfile(
        messages_sent_today=30,
        avg_response_time_mins=10,
        after_hours_messages=2,
        sentiment_score_today=0.1,
        sentiment_trend_delta=-0.3,
        channels_active=6,
        dm_vs_channel_ratio=0.4,
        open_prs_count=4,
        review_requests_today=3,
        avg_tasks_in_progress=12,
        ticket_reassignments=5,
        context_switches=22,
        incomplete_task_pct=45,
        avg_task_age_days=14,
    ),
    # SCN-04: After-Hours Bleed — Messages 9pm–11pm, calendar events before 8am
    "SCN-04": MockSignalProfile(
        messages_sent_today=35,
        avg_response_time_mins=8,
        after_hours_messages=12,
        sentiment_score_today=-0.1,
        sentiment_trend_delta=-0.6,
        channels_active=7,
        dm_vs_channel_ratio=0.5,
        open_prs_count=3,
        review_requests_today=2,
        avg_tasks_in_progress=5,
        ticket_reassignments=1,
        context_switches=8,
        incomplete_task_pct=15,
        avg_task_age_days=7,
    ),
    # SCN-05: Full Overload — All combined, demonstrates CRITICAL state
    "SCN-05": MockSignalProfile(
        messages_sent_today=60,
        avg_response_time_mins=3,
        after_hours_messages=15,
        sentiment_score_today=-0.5,
        sentiment_trend_delta=-0.8,
        channels_active=15,
        dm_vs_channel_ratio=0.7,
        open_prs_count=10,
        review_requests_today=10,
        avg_tasks_in_progress=15,
        ticket_reassignments=6,
        context_switches=28,
        incomplete_task_pct=60,
        avg_task_age_days=20,
    ),
}


def _add_jitter(value: float, pct: float = 0.1) -> float:
    """Add small random variation to make mock data feel realistic."""
    jitter = value * pct * (random.random() * 2 - 1)
    return round(value + jitter, 3)


class CommunicationSignalGenerator:
    """Generates C-01 through C-07 mock values for Slack (SRC-02).

    All data badged as MOCK. Never treated as live.
    """

    def generate(self, scenario_id: str = "SCN-01") -> dict:
        """Generate communication signal values for the given scenario."""
        profile = SCENARIO_PROFILES.get(scenario_id, SCENARIO_PROFILES["SCN-01"])

        return {
            "C-01": _add_jitter(profile.messages_sent_today),
            "C-02": _add_jitter(profile.avg_response_time_mins),
            "C-03": _add_jitter(profile.after_hours_messages),
            "C-04": round(max(-1.0, min(1.0, _add_jitter(profile.sentiment_score_today, 0.05))), 3),
            "C-05": round(max(-2.0, min(2.0, _add_jitter(profile.sentiment_trend_delta, 0.05))), 3),
            "C-06": _add_jitter(profile.channels_active),
            "C-07": round(max(0.0, min(1.0, _add_jitter(profile.dm_vs_channel_ratio, 0.05))), 3),
        }


class TaskSignalGenerator:
    """Generates TA-01 through TA-07 mock values for GitHub (SRC-03) + Jira (SRC-04).

    All data badged as MOCK. Never treated as live.
    """

    def generate(self, scenario_id: str = "SCN-01") -> dict:
        """Generate task signal values for the given scenario."""
        profile = SCENARIO_PROFILES.get(scenario_id, SCENARIO_PROFILES["SCN-01"])

        return {
            "TA-01": _add_jitter(profile.open_prs_count),
            "TA-02": _add_jitter(profile.review_requests_today),
            "TA-03": _add_jitter(profile.avg_tasks_in_progress),
            "TA-04": _add_jitter(profile.ticket_reassignments),
            "TA-05": _add_jitter(profile.context_switches),
            "TA-06": round(max(0.0, min(100.0, _add_jitter(profile.incomplete_task_pct))), 1),
            "TA-07": _add_jitter(profile.avg_task_age_days),
        }
