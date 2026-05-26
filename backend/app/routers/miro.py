"""Miro write-back endpoints (EP-13, EP-14).

EP-13: POST /api/v1/miro/intervention-card — Create intervention card on Miro board (F-09)
EP-14: POST /api/v1/miro/heatmap-update — Update team heatmap frame on Miro board (F-08)

Write-back rules:
- Every intervention must create a card in F-09
- Every score update must update the heatmap in F-08
- Card colours: LIVE+success=green, DRY-RUN=yellow, FAILED=red
- Non-negotiable core feature (AC07)
"""

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.miro_client import HeatmapUpdate, InterventionCard, miro_client

router = APIRouter()


class InterventionCardRequest(BaseModel):
    intervention_id: str
    int_type: str
    execution_mode: str
    trigger_condition: str
    cl_score: int
    action_taken: str
    outcome: str


class HeatmapUpdateRequest(BaseModel):
    user_id: str
    cl_score: int
    band: str
    burnout_risk: float
    flow_state: bool
    data_mode: str


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.post("/intervention-card")
async def create_intervention_card(
    body: InterventionCardRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-13: Create intervention card on Miro board (frame F-09).

    Card colour rules:
    - LIVE + success = green
    - DRY-RUN = yellow
    - FAILED = red
    """
    card = InterventionCard(
        intervention_id=body.intervention_id,
        int_type=body.int_type,
        execution_mode=body.execution_mode,
        trigger_condition=body.trigger_condition,
        cl_score=body.cl_score,
        action_taken=body.action_taken,
        outcome=body.outcome,
    )

    result = await miro_client.write_intervention_card(card)

    return {
        "miro_card_id": result["miro_card_id"],
        "frame_id": "F-09",
        "card_url": result["card_url"],
    }


@router.post("/heatmap-update")
async def update_heatmap(
    body: HeatmapUpdateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-14: Update team heatmap frame on Miro board (frame F-08).

    Updated every 15 minutes (per CFG-09).
    """
    update = HeatmapUpdate(
        user_id=body.user_id,
        cl_score=body.cl_score,
        band=body.band,
        burnout_risk=body.burnout_risk,
        flow_state=body.flow_state,
        data_mode=body.data_mode,
    )

    result = await miro_client.write_heatmap_update(update)

    return {
        "miro_card_id": result["miro_card_id"],
        "frame_id": "F-08",
        "card_url": result["card_url"],
    }
