"""Score endpoints (EP-03, EP-04, EP-12).

EP-03: GET /api/v1/scores/current — Current CL score for authenticated user
EP-04: GET /api/v1/scores/history — CL score time series (max 90 days per CFG-08)
EP-12: WS /api/v1/scores/stream — WebSocket real-time score updates (15-min refresh)
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import CLScore
from app.routers.signals import get_active_scenario
from app.services.boundary_signals import BoundarySignalEngine
from app.services.mock_generators import CommunicationSignalGenerator, TaskSignalGenerator
from app.services.scoring_engine import ScoringEngine
from app.services.signal_engine import TemporalSignalEngine

router = APIRouter()


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.get("/current")
async def get_current_score(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-03: Fetch current CL score for authenticated user.

    Computes score from all 24 signals using F-05 formula:
    CL_SCORE = temporal*0.30 + communication*0.25 + task*0.25 + boundary*0.20
    """
    scenario_id = get_active_scenario(user_id) or "SCN-01"

    # Compute all signals
    temporal_engine = TemporalSignalEngine()
    temporal_signals = temporal_engine.compute(events=[], week_events=[])

    comm_generator = CommunicationSignalGenerator()
    communication_signals = comm_generator.generate(scenario_id)

    task_generator = TaskSignalGenerator()
    task_signals = task_generator.generate(scenario_id)

    boundary_engine = BoundarySignalEngine()
    boundary_signals = boundary_engine.compute(
        temporal_signals=temporal_signals,
        communication_signals=communication_signals,
        has_pto_today=False,
    )

    # Compute CL Score
    scoring_engine = ScoringEngine()
    result = scoring_engine.compute(
        temporal_signals=temporal_signals,
        communication_signals=communication_signals,
        task_signals=task_signals,
        boundary_signals=boundary_signals,
        consecutive_high_days=0,
    )

    # Determine data mode
    data_mode = "mock" if scenario_id != "SCN-01" else "live"

    return {
        "user_id": str(user_id),
        "cl_score": result.cl_score,
        "band": result.band,
        "burnout_risk": result.burnout_risk,
        "flow_state": result.flow_state,
        "component_scores": result.component_scores,
        "risk_factors": result.risk_factors,
        "data_mode": data_mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/history")
async def get_score_history(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-04: Fetch CL score time series for user.

    Max 90 days retention per CFG-08.
    """
    # Default to last 7 days if no dates provided
    now = datetime.now(timezone.utc)
    end = now
    start = now - timedelta(days=7)

    if start_date:
        start = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    if end_date:
        end = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    # Enforce max retention (CFG-08: 90 days)
    max_start = now - timedelta(days=settings.data_retention_days)
    if start < max_start:
        start = max_start

    scores = (
        db.query(CLScore)
        .filter(
            CLScore.user_id == user_id,
            CLScore.created_at >= start,
            CLScore.created_at <= end,
        )
        .order_by(CLScore.created_at.desc())
        .all()
    )

    return {
        "user_id": str(user_id),
        "scores": [
            {
                "timestamp": score.created_at.isoformat(),
                "cl_score": score.score,
                "band": score.band,
                "data_mode": score.data_mode,
            }
            for score in scores
        ],
    }


@router.websocket("/stream")
async def score_stream(websocket: WebSocket):
    """EP-12: WebSocket endpoint for real-time score updates.

    Pushes score updates every CFG-09 minutes (default: 15).
    """
    await websocket.accept()

    try:
        import asyncio

        while True:
            # Compute current score
            scenario_id = "SCN-01"

            temporal_engine = TemporalSignalEngine()
            temporal_signals = temporal_engine.compute(events=[], week_events=[])

            comm_generator = CommunicationSignalGenerator()
            communication_signals = comm_generator.generate(scenario_id)

            task_generator = TaskSignalGenerator()
            task_signals = task_generator.generate(scenario_id)

            boundary_engine = BoundarySignalEngine()
            boundary_signals = boundary_engine.compute(
                temporal_signals=temporal_signals,
                communication_signals=communication_signals,
                has_pto_today=False,
            )

            scoring_engine = ScoringEngine()
            result = scoring_engine.compute(
                temporal_signals=temporal_signals,
                communication_signals=communication_signals,
                task_signals=task_signals,
                boundary_signals=boundary_signals,
            )

            await websocket.send_json({
                "user_id": "00000000-0000-0000-0000-000000000001",
                "cl_score": result.cl_score,
                "band": result.band,
                "component_scores": result.component_scores,
                "data_mode": "live",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

            # Wait for CFG-09 interval (default 15 minutes)
            await asyncio.sleep(settings.score_refresh_interval_mins * 60)

    except WebSocketDisconnect:
        pass
