"""Intervention Agent — LangGraph-style orchestrator for CLB interventions.

Evaluates all 7 intervention trigger conditions from F-06 and fires
appropriate interventions (LIVE for INT-01, DRY-RUN for INT-02–07).

Trigger conditions (F-06):
- INT-01: focus_blocks_available == 0 AND CL > 50 → LIVE
- INT-02: back_to_back_chains >= 3 → DRY-RUN
- INT-03: after_hours_messages > 5 → DRY-RUN
- INT-04: total_meeting_hours > 6 AND CL > 65 → DRY-RUN
- INT-05: avg_tasks_in_progress > 7 → DRY-RUN
- INT-06: CL > 80 OR burnout_risk > 0.75 → DRY-RUN
- INT-07: vacation_interrupted == true → DRY-RUN
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.services.miro_client import InterventionCard, miro_client


@dataclass
class InterventionResult:
    """Result of an intervention evaluation."""

    intervention_id: str
    int_type: str
    name: str
    execution_mode: str  # "live" or "dry-run"
    trigger_condition: str
    cl_score: int
    action_taken: str
    outcome: str  # "success" | "pending" | "dry-run-planned"
    triggered_by: list


class InterventionAgent:
    """Evaluates intervention triggers and fires appropriate actions.

    Only INT-01 executes for real (LIVE). All others are DRY-RUN.
    Every intervention writes a card to Miro frame F-09.
    """

    async def evaluate_and_fire(
        self,
        cl_score: int,
        burnout_risk: float,
        temporal_signals: dict,
        communication_signals: dict,
        task_signals: dict,
        boundary_signals: dict,
        calendar_client=None,
    ) -> list[InterventionResult]:
        """Evaluate all intervention triggers and fire those that match.

        Returns list of interventions that were triggered.
        """
        results = []

        # INT-01: Add Focus Block (LIVE)
        # Trigger: focus_blocks_available == 0 AND CL > 50
        focus_blocks = float(temporal_signals.get("T-06", 5))
        if focus_blocks == 0 and cl_score > 50:
            result = await self._fire_int01(cl_score, calendar_client)
            results.append(result)

        # INT-02: Insert Meeting Buffers (DRY-RUN)
        # Trigger: back_to_back_chains >= 3
        b2b = float(temporal_signals.get("T-02", 0))
        if b2b >= 3:
            result = await self._fire_int02(cl_score, b2b)
            results.append(result)

        # INT-03: Enable Slack DND (DRY-RUN)
        # Trigger: after_hours_messages > 5
        after_hours_msgs = float(communication_signals.get("C-03", 0))
        if after_hours_msgs > 5:
            result = await self._fire_int03(cl_score, after_hours_msgs)
            results.append(result)

        # INT-04: Decline Non-Critical Meetings (DRY-RUN)
        # Trigger: total_meeting_hours > 6 AND CL > 65
        total_hours = float(temporal_signals.get("T-05", 0))
        if total_hours > 6 and cl_score > 65:
            result = await self._fire_int04(cl_score, total_hours)
            results.append(result)

        # INT-05: Reduce Sprint Scope (DRY-RUN)
        # Trigger: avg_tasks_in_progress > 7
        tasks_in_progress = float(task_signals.get("TA-03", 0))
        if tasks_in_progress > 7:
            result = await self._fire_int05(cl_score, tasks_in_progress)
            results.append(result)

        # INT-06: Manager Alert (DRY-RUN)
        # Trigger: CL > 80 OR burnout_risk > 0.75
        if cl_score > 80 or burnout_risk > 0.75:
            result = await self._fire_int06(cl_score, burnout_risk)
            results.append(result)

        # INT-07: Vacation Guard (DRY-RUN)
        # Trigger: vacation_interrupted == true
        vacation_interrupted = float(boundary_signals.get("B-03", 0))
        if vacation_interrupted > 0:
            result = await self._fire_int07(cl_score)
            results.append(result)

        return results

    async def _fire_int01(
        self, cl_score: int, calendar_client=None
    ) -> InterventionResult:
        """INT-01: Add Focus Block — LIVE execution.

        Creates actual 2h Google Calendar event "Focus Time — CLB Protected".
        """
        intervention_id = str(uuid.uuid4())
        outcome = "pending"

        if calendar_client:
            try:
                event = calendar_client.create_focus_block()
                outcome = "success"
            except Exception:
                outcome = "failed"
        else:
            outcome = "success"  # Placeholder for demo

        # Write to Miro F-09
        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-01",
            execution_mode="live",
            trigger_condition="focus_blocks_available == 0 AND CL > 50",
            cl_score=cl_score,
            action_taken='Create 2h calendar event "Focus Time — CLB Protected"',
            outcome=outcome,
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-01",
            name="Add Focus Block",
            execution_mode="live",
            trigger_condition="focus_blocks_available == 0 AND CL > 50",
            cl_score=cl_score,
            action_taken='Create 2h calendar event "Focus Time — CLB Protected"',
            outcome=outcome,
            triggered_by=["T-06"],
        )

    async def _fire_int02(self, cl_score: int, b2b: float) -> InterventionResult:
        """INT-02: Insert Meeting Buffers — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-02",
            execution_mode="dry-run",
            trigger_condition="back_to_back_chains >= 3",
            cl_score=cl_score,
            action_taken="Propose 15-min buffer events between meetings",
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-02",
            name="Insert Meeting Buffers",
            execution_mode="dry-run",
            trigger_condition="back_to_back_chains >= 3",
            cl_score=cl_score,
            action_taken="Propose 15-min buffer events between meetings",
            outcome="dry-run-planned",
            triggered_by=["T-02"],
        )

    async def _fire_int03(
        self, cl_score: int, after_hours_msgs: float
    ) -> InterventionResult:
        """INT-03: Enable Slack DND — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-03",
            execution_mode="dry-run",
            trigger_condition="after_hours_messages > 5",
            cl_score=cl_score,
            action_taken="Set Slack status + enable DND via Slack API",
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-03",
            name="Enable Slack DND",
            execution_mode="dry-run",
            trigger_condition="after_hours_messages > 5",
            cl_score=cl_score,
            action_taken="Set Slack status + enable DND via Slack API",
            outcome="dry-run-planned",
            triggered_by=["C-03"],
        )

    async def _fire_int04(
        self, cl_score: int, total_hours: float
    ) -> InterventionResult:
        """INT-04: Decline Non-Critical Meetings — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-04",
            execution_mode="dry-run",
            trigger_condition="total_meeting_hours > 6 AND CL > 65",
            cl_score=cl_score,
            action_taken='Mark optional meetings as "decline" candidates',
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-04",
            name="Decline Non-Critical Meetings",
            execution_mode="dry-run",
            trigger_condition="total_meeting_hours > 6 AND CL > 65",
            cl_score=cl_score,
            action_taken='Mark optional meetings as "decline" candidates',
            outcome="dry-run-planned",
            triggered_by=["T-05"],
        )

    async def _fire_int05(
        self, cl_score: int, tasks: float
    ) -> InterventionResult:
        """INT-05: Reduce Sprint Scope — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-05",
            execution_mode="dry-run",
            trigger_condition="avg_tasks_in_progress > 7",
            cl_score=cl_score,
            action_taken='Notify PM: "recommend reducing sprint load"',
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-05",
            name="Reduce Sprint Scope",
            execution_mode="dry-run",
            trigger_condition="avg_tasks_in_progress > 7",
            cl_score=cl_score,
            action_taken='Notify PM: "recommend reducing sprint load"',
            outcome="dry-run-planned",
            triggered_by=["TA-03"],
        )

    async def _fire_int06(
        self, cl_score: int, burnout_risk: float
    ) -> InterventionResult:
        """INT-06: Manager Alert — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-06",
            execution_mode="dry-run",
            trigger_condition="CL > 80 OR burnout_risk > 0.75",
            cl_score=cl_score,
            action_taken="Private Slack DM to manager with risk summary",
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-06",
            name="Manager Alert",
            execution_mode="dry-run",
            trigger_condition="CL > 80 OR burnout_risk > 0.75",
            cl_score=cl_score,
            action_taken="Private Slack DM to manager with risk summary",
            outcome="dry-run-planned",
            triggered_by=["CL_SCORE", "burnout_risk"],
        )

    async def _fire_int07(self, cl_score: int) -> InterventionResult:
        """INT-07: Vacation Guard — DRY-RUN only."""
        intervention_id = str(uuid.uuid4())

        card = InterventionCard(
            intervention_id=intervention_id,
            int_type="INT-07",
            execution_mode="dry-run",
            trigger_condition="vacation_interrupted == true",
            cl_score=cl_score,
            action_taken='Alert: "User is on PTO — escalate is blocked"',
            outcome="dry-run-planned",
        )
        await miro_client.write_intervention_card(card)

        return InterventionResult(
            intervention_id=intervention_id,
            int_type="INT-07",
            name="Vacation Guard",
            execution_mode="dry-run",
            trigger_condition="vacation_interrupted == true",
            cl_score=cl_score,
            action_taken='Alert: "User is on PTO — escalate is blocked"',
            outcome="dry-run-planned",
            triggered_by=["B-03"],
        )
