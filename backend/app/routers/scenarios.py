"""Scenario endpoints (EP-06, EP-07, EP-08).

EP-06: GET /api/v1/scenarios — List mock scenarios (SCN-01 through SCN-05)
EP-07: POST /api/v1/scenarios/activate — Activate a mock scenario
EP-08: POST /api/v1/scenarios/deactivate — Deactivate mock, return to live

Scenario definitions from F-03. All mock data clearly badged.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.routers.signals import get_active_scenario, set_active_scenario

router = APIRouter()

# Scenario registry from F-03
SCENARIOS = {
    "SCN-01": {
        "scenario_id": "SCN-01",
        "name": "Baseline",
        "description": "Normal working day, moderate activity",
        "sources_affected": ["SRC-02", "SRC-03", "SRC-04"],
    },
    "SCN-02": {
        "scenario_id": "SCN-02",
        "name": "Interruption Storm",
        "description": "40+ Slack messages, 8 PR review requests in 4 hours",
        "sources_affected": ["SRC-02", "SRC-03"],
    },
    "SCN-03": {
        "scenario_id": "SCN-03",
        "name": "Sprint Crunch",
        "description": "12+ open tickets, 5 reassignments, deadline pressure",
        "sources_affected": ["SRC-04"],
    },
    "SCN-04": {
        "scenario_id": "SCN-04",
        "name": "After-Hours Bleed",
        "description": "Messages sent 9pm–11pm, calendar events before 8am",
        "sources_affected": ["SRC-02", "SRC-01"],
    },
    "SCN-05": {
        "scenario_id": "SCN-05",
        "name": "Full Overload",
        "description": "All of the above combined — demonstrates CRITICAL state",
        "sources_affected": ["SRC-02", "SRC-03", "SRC-04"],
    },
}


class ActivateRequest(BaseModel):
    scenario_id: str
    data_mode: str = "mock"


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("")
async def list_scenarios(user_id: uuid.UUID = Depends(get_current_user_id)):
    """EP-06: Fetch available mock scenarios list.

    Returns SCN-01 through SCN-05 as defined in F-03.
    """
    return {
        "scenarios": list(SCENARIOS.values()),
    }


@router.post("/activate")
async def activate_scenario(
    body: ActivateRequest,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-07: Activate a mock scenario for the current session.

    data_mode must be "mock". Selected scenario updates CL score in real time.
    """
    if body.scenario_id not in SCENARIOS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario_id. Must be one of: {', '.join(SCENARIOS.keys())}",
        )

    if body.data_mode != "mock":
        raise HTTPException(
            status_code=400,
            detail="data_mode must be 'mock' when activating a scenario",
        )

    set_active_scenario(user_id, body.scenario_id)
    scenario = SCENARIOS[body.scenario_id]

    return {
        "scenario_id": body.scenario_id,
        "active": True,
        "sources_affected": scenario["sources_affected"],
        "mock_data_loaded": True,
    }


@router.post("/deactivate")
async def deactivate_scenario(user_id: uuid.UUID = Depends(get_current_user_id)):
    """EP-08: Deactivate mock mode, return to live-only.

    Clears all mock data and returns to LIVE Google Calendar only.
    """
    set_active_scenario(user_id, None)

    return {
        "data_mode": "live",
        "mock_scenario": None,
    }
