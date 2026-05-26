"""Signal Engine — computes all 24 signals from F-04.

Temporal signals (T-01 to T-07): derived from LIVE Google Calendar data.
Communication signals (C-01 to C-07): derived from MOCK Slack data.
Task signals (TA-01 to TA-07): derived from MOCK GitHub + Jira data.
Boundary signals (B-01 to B-03): cross-source derived.

All signal definitions strictly from Miro board frame F-04.
No invented signals. No raw content stored.
"""

from datetime import datetime, time, timedelta, timezone
from typing import Optional

from app.config import settings


def _parse_time(time_str: str) -> time:
    """Parse HH:MM string to time object."""
    parts = time_str.split(":")
    return time(int(parts[0]), int(parts[1]))


def _is_after_hours(event_start: datetime) -> bool:
    """Check if an event is outside work hours (CFG-01, CFG-02)."""
    work_start = _parse_time(settings.work_hours_start)
    work_end = _parse_time(settings.work_hours_end)
    event_time = event_start.time()
    return event_time < work_start or event_time > work_end


def _is_weekend(dt: datetime) -> bool:
    """Check if date falls on a non-work day (CFG-04)."""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_name = day_names[dt.weekday()]
    return day_name not in settings.work_days


class TemporalSignalEngine:
    """Computes T-01 through T-07 from LIVE Google Calendar events.

    Input: list of calendar events (derived data only — no titles/attendees).
    Output: dict of signal_id -> value.
    """

    def compute(self, events: list[dict], week_events: list[dict] = None) -> dict:
        """Compute all 7 temporal signals from today's calendar events."""
        signals = {}

        # T-01: meeting_count_today — Count of calendar events today
        signals["T-01"] = len(events)

        # T-02: back_to_back_chains — Sequences with gap < CFG-11 mins
        signals["T-02"] = self._count_back_to_back(events)

        # T-03: avg_gap_minutes — Avg minutes between consecutive meetings
        signals["T-03"] = self._avg_gap_minutes(events)

        # T-04: after_hours_meetings — Events outside CFG-01 to CFG-02
        signals["T-04"] = self._count_after_hours(events)

        # T-05: total_meeting_hours — Sum of event durations today
        signals["T-05"] = self._total_meeting_hours(events)

        # T-06: focus_blocks_available — Uninterrupted blocks >= 2 hours
        signals["T-06"] = self._count_focus_blocks(events)

        # T-07: days_without_break — Consecutive days with >6h meetings
        signals["T-07"] = self._days_without_break(week_events or [])

        return signals

    def _count_back_to_back(self, events: list[dict]) -> int:
        """Count sequences where gap between meetings < CFG-11 mins."""
        if len(events) < 2:
            return 0

        threshold = settings.back_to_back_gap_threshold_mins
        chains = 0

        for i in range(len(events) - 1):
            end_current = events[i].get("end")
            start_next = events[i + 1].get("start")

            if not end_current or not start_next:
                continue

            end_dt = datetime.fromisoformat(end_current)
            start_dt = datetime.fromisoformat(start_next)
            gap_mins = (start_dt - end_dt).total_seconds() / 60

            if gap_mins < threshold:
                chains += 1

        return chains

    def _avg_gap_minutes(self, events: list[dict]) -> float:
        """Calculate average gap between consecutive meetings."""
        if len(events) < 2:
            return 480.0  # Max range — no meetings means max gap

        gaps = []
        for i in range(len(events) - 1):
            end_current = events[i].get("end")
            start_next = events[i + 1].get("start")

            if not end_current or not start_next:
                continue

            end_dt = datetime.fromisoformat(end_current)
            start_dt = datetime.fromisoformat(start_next)
            gap_mins = (start_dt - end_dt).total_seconds() / 60

            if gap_mins >= 0:
                gaps.append(gap_mins)

        return round(sum(gaps) / len(gaps), 1) if gaps else 480.0

    def _count_after_hours(self, events: list[dict]) -> int:
        """Count events outside work hours (CFG-01 to CFG-02)."""
        count = 0
        for event in events:
            start_str = event.get("start")
            if start_str:
                start_dt = datetime.fromisoformat(start_str)
                if _is_after_hours(start_dt):
                    count += 1
        return count

    def _total_meeting_hours(self, events: list[dict]) -> float:
        """Sum of all event durations in hours."""
        total_mins = sum(event.get("duration_minutes", 0) for event in events)
        return round(total_mins / 60, 1)

    def _count_focus_blocks(self, events: list[dict]) -> int:
        """Count uninterrupted blocks >= 2 hours in the workday."""
        work_start = _parse_time(settings.work_hours_start)
        work_end = _parse_time(settings.work_hours_end)

        today = datetime.now(timezone.utc).date()
        day_start = datetime.combine(today, work_start, tzinfo=timezone.utc)
        day_end = datetime.combine(today, work_end, tzinfo=timezone.utc)

        if not events:
            # Entire workday is one focus block
            total_hours = (day_end - day_start).total_seconds() / 3600
            return int(total_hours // 2)

        # Build list of busy periods
        busy_periods = []
        for event in events:
            start_str = event.get("start")
            end_str = event.get("end")
            if start_str and end_str:
                busy_periods.append((
                    datetime.fromisoformat(start_str),
                    datetime.fromisoformat(end_str),
                ))

        busy_periods.sort(key=lambda x: x[0])

        # Find free blocks
        focus_blocks = 0
        current_time = day_start

        for busy_start, busy_end in busy_periods:
            if busy_start > current_time:
                free_hours = (busy_start - current_time).total_seconds() / 3600
                if free_hours >= 2:
                    focus_blocks += 1
            current_time = max(current_time, busy_end)

        # Check remaining time after last meeting
        if current_time < day_end:
            free_hours = (day_end - current_time).total_seconds() / 3600
            if free_hours >= 2:
                focus_blocks += 1

        return focus_blocks

    def _days_without_break(self, week_events: list[dict]) -> int:
        """Count consecutive days with >6h meetings (looking back)."""
        if not week_events:
            return 0

        # Group events by date
        daily_hours: dict[str, float] = {}
        for event in week_events:
            date = event.get("date", "")
            duration = event.get("duration_minutes", 0)
            if date:
                daily_hours[date] = daily_hours.get(date, 0) + duration / 60

        # Count consecutive days with >6h from today backwards
        today = datetime.now(timezone.utc).date()
        consecutive = 0

        for i in range(30):  # Max range from F-04
            check_date = (today - timedelta(days=i)).isoformat()
            if daily_hours.get(check_date, 0) > 6:
                consecutive += 1
            else:
                break

        return consecutive
