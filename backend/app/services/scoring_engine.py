"""Scoring Engine — computes CL Score, Burnout Risk, and Flow State.

All formulas strictly from F-05 Scoring Model:
- Composite: CL_SCORE = temporal*0.30 + communication*0.25 + task*0.25 + boundary*0.20
- Bands: OPTIMAL(0-30), MODERATE(31-50), HIGH(51-70), CRITICAL(71-85), BURNOUT(86-100)
- Burnout Risk: sigmoid(CL_SCORE) * multipliers
- Flow State: ALL 5 conditions must be TRUE

Temporal Score Rules from design document Section 6.2:
- meeting_count_today >= 8: +25
- meeting_count_today >= 5: +15
- back_to_back_chains >= 3: +20
- back_to_back_chains >= 1: +10
- avg_gap_minutes < 10: +15
- after_hours_meetings >= 2: +20
- focus_blocks_available == 0: +20
- days_without_break >= 3: +15
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class CLScoreResult:
    """Complete CL Score calculation result."""

    cl_score: int
    band: str
    burnout_risk: float
    flow_state: bool
    component_scores: dict
    risk_factors: list[str]


# Band thresholds from F-05
BANDS = [
    (0, 30, "OPTIMAL"),
    (31, 50, "MODERATE"),
    (51, 70, "HIGH"),
    (71, 85, "CRITICAL"),
    (86, 100, "BURNOUT"),
]


def _score_to_band(score: int) -> str:
    """Map CL score to band per F-05."""
    for low, high, band in BANDS:
        if low <= score <= high:
            return band
    return "BURNOUT"  # Anything above 100 clips to BURNOUT


def _sigmoid(x: float) -> float:
    """Sigmoid function for burnout risk base calculation."""
    return 1 / (1 + math.exp(-0.05 * (x - 50)))


class ScoringEngine:
    """Computes composite CL Score from component scores.

    Weights from F-05:
    - temporal_score * 0.30
    - communication_score * 0.25
    - task_score * 0.25
    - boundary_score * 0.20
    """

    def compute(
        self,
        temporal_signals: dict,
        communication_signals: dict,
        task_signals: dict,
        boundary_signals: dict,
        consecutive_high_days: int = 0,
    ) -> CLScoreResult:
        """Compute full CL Score result from all signal groups."""

        # Calculate component scores (0-100 each)
        temporal_score = self._compute_temporal_score(temporal_signals)
        communication_score = self._compute_communication_score(communication_signals)
        task_score = self._compute_task_score(task_signals)
        boundary_score = self._compute_boundary_score(boundary_signals)

        # Composite CL Score (F-05 formula)
        cl_score_raw = (
            temporal_score * 0.30
            + communication_score * 0.25
            + task_score * 0.25
            + boundary_score * 0.20
        )
        cl_score = max(0, min(100, round(cl_score_raw)))

        # Band mapping
        band = _score_to_band(cl_score)

        # Burnout risk (F-05)
        burnout_risk = self._compute_burnout_risk(
            cl_score,
            band,
            consecutive_high_days,
            communication_signals,
            boundary_signals,
        )

        # Flow state (F-05 — all 5 conditions must be TRUE)
        flow_state = self._compute_flow_state(
            temporal_signals, communication_signals, task_score, cl_score
        )

        # Collect risk factors
        risk_factors = self._collect_risk_factors(
            temporal_signals, communication_signals, task_signals, boundary_signals
        )

        component_scores = {
            "temporal": temporal_score,
            "communication": communication_score,
            "task": task_score,
            "boundary": boundary_score,
        }

        return CLScoreResult(
            cl_score=cl_score,
            band=band,
            burnout_risk=round(burnout_risk, 3),
            flow_state=flow_state,
            component_scores=component_scores,
            risk_factors=risk_factors,
        )

    def _compute_temporal_score(self, signals: dict) -> int:
        """Calculate temporal_score (0-100) from T-01 through T-07.

        Scoring rules from design document Section 6.2.
        """
        score = 0

        # T-01: meeting_count_today
        meeting_count = float(signals.get("T-01", 0))
        if meeting_count >= 8:
            score += 25
        elif meeting_count >= 5:
            score += 15

        # T-02: back_to_back_chains
        b2b = float(signals.get("T-02", 0))
        if b2b >= 3:
            score += 20
        elif b2b >= 1:
            score += 10

        # T-03: avg_gap_minutes
        avg_gap = float(signals.get("T-03", 480))
        if avg_gap < 10:
            score += 15

        # T-04: after_hours_meetings
        after_hours = float(signals.get("T-04", 0))
        if after_hours >= 2:
            score += 20

        # T-06: focus_blocks_available
        focus_blocks = float(signals.get("T-06", 5))
        if focus_blocks == 0:
            score += 20

        # T-07: days_without_break
        days_no_break = float(signals.get("T-07", 0))
        if days_no_break >= 3:
            score += 15

        return min(100, score)

    def _compute_communication_score(self, signals: dict) -> int:
        """Calculate communication_score (0-100) from C-01 through C-07."""
        score = 0

        # C-01: messages_sent_today
        messages = float(signals.get("C-01", 0))
        if messages >= 80:
            score += 25
        elif messages >= 40:
            score += 15

        # C-02: avg_response_time_mins (low = reactive = high load)
        response_time = float(signals.get("C-02", 60))
        if response_time < 5:
            score += 20
        elif response_time < 15:
            score += 10

        # C-03: after_hours_messages
        after_hours = float(signals.get("C-03", 0))
        if after_hours >= 10:
            score += 25
        elif after_hours >= 5:
            score += 15

        # C-04: sentiment_score_today (negative = high load)
        sentiment = float(signals.get("C-04", 0.5))
        if sentiment < -0.3:
            score += 15
        elif sentiment < 0:
            score += 5

        # C-05: sentiment_trend_delta (declining = concerning)
        trend = float(signals.get("C-05", 0))
        if trend < -0.5:
            score += 15
        elif trend < -0.2:
            score += 5

        # C-06: channels_active (many = fragmented attention)
        channels = float(signals.get("C-06", 3))
        if channels >= 12:
            score += 10

        # C-07: dm_vs_channel_ratio (high DM = more interruptions)
        dm_ratio = float(signals.get("C-07", 0.3))
        if dm_ratio >= 0.7:
            score += 10

        return min(100, score)

    def _compute_task_score(self, signals: dict) -> int:
        """Calculate task_score (0-100) from TA-01 through TA-07."""
        score = 0

        # TA-01: open_prs_count
        prs = float(signals.get("TA-01", 0))
        if prs >= 8:
            score += 20
        elif prs >= 4:
            score += 10

        # TA-02: review_requests_today
        reviews = float(signals.get("TA-02", 0))
        if reviews >= 6:
            score += 20
        elif reviews >= 3:
            score += 10

        # TA-03: avg_tasks_in_progress
        tasks = float(signals.get("TA-03", 0))
        if tasks >= 10:
            score += 25
        elif tasks >= 7:
            score += 15

        # TA-04: ticket_reassignments
        reassignments = float(signals.get("TA-04", 0))
        if reassignments >= 4:
            score += 15
        elif reassignments >= 2:
            score += 5

        # TA-05: context_switches
        switches = float(signals.get("TA-05", 0))
        if switches >= 15:
            score += 20
        elif switches >= 8:
            score += 10

        # TA-06: incomplete_task_pct
        incomplete = float(signals.get("TA-06", 0))
        if incomplete >= 40:
            score += 15
        elif incomplete >= 20:
            score += 5

        # TA-07: avg_task_age_days
        age = float(signals.get("TA-07", 0))
        if age >= 14:
            score += 10

        return min(100, score)

    def _compute_boundary_score(self, signals: dict) -> int:
        """Calculate boundary_score (0-100) from B-01 through B-03."""
        score = 0

        # B-01: boundary_violations
        violations = float(signals.get("B-01", 0))
        if violations >= 10:
            score += 35
        elif violations >= 5:
            score += 20
        elif violations >= 2:
            score += 10

        # B-02: weekend_work_detected (boolean as 0/1)
        weekend = float(signals.get("B-02", 0))
        if weekend > 0:
            score += 30

        # B-03: vacation_interrupted (boolean as 0/1) — Critical weight
        vacation = float(signals.get("B-03", 0))
        if vacation > 0:
            score += 50

        return min(100, score)

    def _compute_burnout_risk(
        self,
        cl_score: int,
        band: str,
        consecutive_high_days: int,
        communication_signals: dict,
        boundary_signals: dict,
    ) -> float:
        """Compute burnout risk probability per F-05.

        burnout_risk = sigmoid(CL_SCORE)
                     * sustained_high_load_multiplier (1.0-1.5)
                     * sentiment_degradation_multiplier (1.0-1.3)
                     * after_hours_multiplier (1.0-1.2)
        """
        base = _sigmoid(cl_score)

        # sustained_high_load_multiplier: 1.5 if HIGH/CRITICAL for 3+ consecutive days
        sustained_mult = 1.5 if (band in ("HIGH", "CRITICAL") and consecutive_high_days >= 3) else 1.0

        # sentiment_degradation_multiplier: 1.3 if sentiment_trend_delta < -0.5
        sentiment_delta = float(communication_signals.get("C-05", 0))
        sentiment_mult = 1.3 if sentiment_delta < -0.5 else 1.0

        # after_hours_multiplier: 1.2 if boundary_violations > 5 per day
        violations = float(boundary_signals.get("B-01", 0))
        after_hours_mult = 1.2 if violations > 5 else 1.0

        risk = base * sustained_mult * sentiment_mult * after_hours_mult
        return min(1.0, risk)  # Cap at 1.0

    def _compute_flow_state(
        self,
        temporal_signals: dict,
        communication_signals: dict,
        task_score: int,
        cl_score: int,
    ) -> bool:
        """Compute flow state per F-05.

        Flow state = TRUE only when ALL conditions met:
        1. No meetings in next 2 hours (approximated by focus_blocks >= 2)
        2. focus_blocks_available >= 2
        3. task_score < 30
        4. avg_response_time_mins > 45
        5. CL_SCORE < 40
        """
        focus_blocks = float(temporal_signals.get("T-06", 0))
        avg_response = float(communication_signals.get("C-02", 0))

        conditions = [
            focus_blocks >= 2,  # Conditions 1 & 2 combined
            task_score < 30,
            avg_response > 45,
            cl_score < 40,
        ]

        return all(conditions)

    def _collect_risk_factors(
        self,
        temporal_signals: dict,
        communication_signals: dict,
        task_signals: dict,
        boundary_signals: dict,
    ) -> list[str]:
        """Collect signal IDs that are contributing to elevated load."""
        factors = []

        if float(temporal_signals.get("T-02", 0)) >= 3:
            factors.append("T-02")
        if float(temporal_signals.get("T-06", 5)) == 0:
            factors.append("T-06")
        if float(temporal_signals.get("T-07", 0)) >= 3:
            factors.append("T-07")
        if float(communication_signals.get("C-03", 0)) > 5:
            factors.append("C-03")
        if float(communication_signals.get("C-05", 0)) < -0.5:
            factors.append("C-05")
        if float(task_signals.get("TA-03", 0)) > 7:
            factors.append("TA-03")
        if float(task_signals.get("TA-05", 0)) >= 15:
            factors.append("TA-05")
        if float(boundary_signals.get("B-01", 0)) > 5:
            factors.append("B-01")
        if float(boundary_signals.get("B-03", 0)) > 0:
            factors.append("B-03")

        return factors
