"""EP-11: GET /api/v1/team/heatmap — Team heatmap data (all users, current scores).

Powers F-08 visualization. Colour-coded by band:
- Green (OPTIMAL), Yellow (MODERATE), Orange (HIGH), Red (CRITICAL), Dark Red (BURNOUT)
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

router = APIRouter()


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


# Demo team data for heatmap visualization
DEMO_TEAM = [
    {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "cl_score": 42,
        "band": "MODERATE",
        "burnout_risk": 0.28,
        "flow_state": False,
        "data_mode": "live",
    },
    {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "cl_score": 23,
        "band": "OPTIMAL",
        "burnout_risk": 0.12,
        "flow_state": True,
        "data_mode": "mock",
    },
    {
        "user_id": "00000000-0000-0000-0000-000000000003",
        "cl_score": 67,
        "band": "HIGH",
        "burnout_risk": 0.65,
        "flow_state": False,
        "data_mode": "mock",
    },
    {
        "user_id": "00000000-0000-0000-0000-000000000004",
        "cl_score": 78,
        "band": "CRITICAL",
        "burnout_risk": 0.82,
        "flow_state": False,
        "data_mode": "mock",
    },
]


@router.get("/heatmap")
async def get_team_heatmap(
    team_id: str = Query(default="default"),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-11: Fetch team heatmap data (all users, current scores).

    Returns all team members with CL scores, bands, burnout risk, flow state.
    Powers the F-08 Live Heatmap visualization.
    """
    now = datetime.now(timezone.utc)

    return {
        "team_id": team_id,
        "users": [
            {
                **user,
                "last_updated": now.isoformat(),
            }
            for user in DEMO_TEAM
        ],
    }
