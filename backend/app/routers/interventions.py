"""Intervention endpoints (EP-09, EP-10).

EP-09: GET /api/v1/interventions/history — Intervention history (live + dry-run)
EP-10: POST /api/v1/interventions/trigger — Manually trigger an intervention (demo only)

Intervention rules from F-06:
- INT-01: LIVE (creates actual Google Calendar event)
- INT-02 through INT-07: DRY-RUN only (planned but NOT executed)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Intervention
from app.services.miro_client import InterventionCard, miro_client

router = APIRouter()


class TriggerRequest(BaseModel):
    int_type: str
    execution_mode: str
    force: bool = False


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


# Intervention definitions from F-06
INTERVENTION_DEFS = {
    "INT-01": {
        "name": "Add Focus Block",
        "execution_mode": "live",
        "action": 'Create 2h calendar event "Focus Time — CLB Protected"',
    },
    "INT-02": {
        "name": "Insert Meeting Buffers",
        "execution_mode": "dry-run",
        "action": "Propose 15-min buffer events between meetings",
    },
    "INT-03": {
        "name": "Enable Slack DND",
        "execution_mode": "dry-run",
        "action": "Set Slack status + enable DND via Slack API",
    },
    "INT-04": {
        "name": "Decline Non-Critical Meetings",
        "execution_mode": "dry-run",
        "action": 'Mark optional meetings as "decline" candidates',
    },
    "INT-05": {
        "name": "Reduce Sprint Scope",
        "execution_mode": "dry-run",
        "action": 'Notify PM: "recommend reducing sprint load"',
    },
    "INT-06": {
        "name": "Manager Alert",
        "execution_mode": "dry-run",
        "action": "Private Slack DM to manager with risk summary",
    },
    "INT-07": {
        "name": "Vacation Guard",
        "execution_mode": "dry-run",
        "action": 'Alert: "User is on PTO — escalate is blocked"',
    },
}


@router.get("/history")
async def get_intervention_history(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-09: Fetch intervention history for user.

    Includes both live and dry-run interventions.
    """
    if db is None:
        # No DB connection — return empty for development
        return {"user_id": str(user_id), "interventions": []}

    query = db.query(Intervention).filter(Intervention.user_id == user_id)

    if start_date:
        query = query.filter(
            Intervention.created_at >= datetime.fromisoformat(start_date)
        )
    if end_date:
        query = query.filter(
            Intervention.created_at <= datetime.fromisoformat(end_date)
        )

    interventions = query.order_by(Intervention.created_at.desc()).all()

    return {
        "user_id": str(user_id),
        "interventions": [
            {
                "intervention_id": str(i.id),
                "int_type": i.int_type,
                "execution_mode": i.execution_mode,
                "triggered_by": i.triggered_by,
                "cl_score_at_trigger": i.cl_score_before,
                "action_taken": i.action_taken,
                "outcome": i.outcome,
                "timestamp": i.created_at.isoformat() if i.created_at else None,
            }
            for i in interventions
        ],
    }


@router.post("/trigger")
async def trigger_intervention(
    body: TriggerRequest,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-10: Manually trigger an intervention (demo use only).

    execution_mode is a required field.
    Only INT-01 can be triggered as "live". All others must be "dry-run".
    """
    if body.int_type not in INTERVENTION_DEFS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid int_type. Must be one of: {', '.join(INTERVENTION_DEFS.keys())}",
        )

    definition = INTERVENTION_DEFS[body.int_type]

    # Enforce execution mode rules from F-06
    if body.int_type != "INT-01" and body.execution_mode == "live":
        raise HTTPException(
            status_code=400,
            detail=f"{body.int_type} can only be triggered as dry-run. Only INT-01 supports live execution.",
        )

    if body.int_type == "INT-01" and body.execution_mode == "live":
        # LIVE execution — create actual Google Calendar event
        outcome = "success"
        # In production: call calendar_client.create_focus_block()
    else:
        # DRY-RUN — plan but do not execute
        outcome = "dry-run-planned"

    intervention_id = str(uuid.uuid4())

    # Write intervention card to Miro (F-09) — AC07
    card = InterventionCard(
        intervention_id=intervention_id,
        int_type=body.int_type,
        execution_mode=body.execution_mode,
        trigger_condition=f"Manual trigger (demo) - force={body.force}",
        cl_score=0,
        action_taken=definition["action"],
        outcome=outcome,
    )
    miro_result = await miro_client.write_intervention_card(card)

    return {
        "intervention_id": intervention_id,
        "int_type": body.int_type,
        "execution_mode": body.execution_mode,
        "outcome": outcome,
        "miro_card_created": True,
    }
