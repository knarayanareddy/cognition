"""Boundary Signal Derivation — B-01 through B-03.

Cross-source derived signals from F-04:
- B-01: boundary_violations = after_hours_meetings + after_hours_messages
- B-02: weekend_work_detected = Events or messages on days not in CFG-04
- B-03: vacation_interrupted = Activity during PTO calendar blocks

Respects CFG-01, CFG-02, CFG-03, CFG-04 in all calculations.
"""

from datetime import datetime, timezone

from app.config import settings


class BoundarySignalEngine:
    """Computes B-01 through B-03 from temporal and communication signals."""

    def compute(
        self,
        temporal_signals: dict,
        communication_signals: dict,
        has_pto_today: bool = False,
    ) -> dict:
        """Compute all 3 boundary signals.

        Args:
            temporal_signals: Dict with T-01 through T-07 values
            communication_signals: Dict with C-01 through C-07 values
            has_pto_today: Whether user has PTO calendar block today
        """
        # B-01: boundary_violations = after_hours_meetings + after_hours_messages
        after_hours_meetings = temporal_signals.get("T-04", 0)
        after_hours_messages = communication_signals.get("C-03", 0)
        b01 = float(after_hours_meetings) + float(after_hours_messages)

        # B-02: weekend_work_detected = Events or messages on days not in CFG-04
        b02 = self._detect_weekend_work(temporal_signals, communication_signals)

        # B-03: vacation_interrupted = Activity during PTO calendar blocks
        b03 = self._detect_vacation_interrupted(
            has_pto_today, temporal_signals, communication_signals
        )

        return {
            "B-01": round(b01, 3),
            "B-02": 1.0 if b02 else 0.0,
            "B-03": 1.0 if b03 else 0.0,
        }

    def _detect_weekend_work(
        self, temporal_signals: dict, communication_signals: dict
    ) -> bool:
        """B-02: Check if today is a non-work day with activity."""
        now = datetime.now(timezone.utc)
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        today_name = day_names[now.weekday()]

        if today_name in settings.work_days:
            return False

        # If it's a non-work day, check for any activity
        has_meetings = temporal_signals.get("T-01", 0) > 0
        has_messages = communication_signals.get("C-01", 0) > 0

        return has_meetings or has_messages

    def _detect_vacation_interrupted(
        self,
        has_pto_today: bool,
        temporal_signals: dict,
        communication_signals: dict,
    ) -> bool:
        """B-03: Check if there's activity during PTO calendar blocks."""
        if not has_pto_today:
            return False

        # Any activity during PTO = vacation interrupted
        has_meetings = temporal_signals.get("T-01", 0) > 0
        has_messages = communication_signals.get("C-01", 0) > 0
        has_tasks = False  # Would check task signals in full implementation

        return has_meetings or has_messages or has_tasks
