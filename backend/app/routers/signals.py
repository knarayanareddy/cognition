"""EP-05: GET /api/v1/signals/current — All 24 signal snapshots.

Returns signal_id, value, source_mode (LIVE/MOCK), captured_at for each signal.
Exactly 24 signals as defined in F-04: T-01 to T-07, C-01 to C-07, TA-01 to TA-07, B-01 to B-03.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.boundary_signals import BoundarySignalEngine
from app.services.mock_generators import CommunicationSignalGenerator, TaskSignalGenerator
from app.services.signal_engine import TemporalSignalEngine

router = APIRouter()

# Active scenario state (in production, stored per-user in DB)
_active_scenario: dict[str, str] = {}


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


def get_active_scenario(user_id: uuid.UUID) -> Optional[str]:
    """Get the currently active mock scenario for a user."""
    return _active_scenario.get(str(user_id))


def set_active_scenario(user_id: uuid.UUID, scenario_id: Optional[str]):
    """Set or clear the active mock scenario for a user."""
    if scenario_id:
        _active_scenario[str(user_id)] = scenario_id
    else:
        _active_scenario.pop(str(user_id), None)


@router.get("/current")
async def get_current_signals(
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-05: Fetch all 24 signal snapshots for the authenticated user.

    Returns all signals from F-04:
    - T-01 to T-07 (Temporal, source: LIVE Google Calendar)
    - C-01 to C-07 (Communication, source: MOCK Slack)
    - TA-01 to TA-07 (Task, source: MOCK GitHub + Jira)
    - B-01 to B-03 (Boundary, cross-source derived)
    """
    now = datetime.now(timezone.utc)
    scenario_id = get_active_scenario(user_id) or "SCN-01"

    # Temporal signals — LIVE from Google Calendar
    # In production, this reads from calendar_client.get_todays_events()
    # For now, use placeholder values (will be connected in full integration)
    temporal_engine = TemporalSignalEngine()
    temporal_signals = temporal_engine.compute(events=[], week_events=[])

    # Communication signals — MOCK from Slack (SRC-02)
    comm_generator = CommunicationSignalGenerator()
    communication_signals = comm_generator.generate(scenario_id)

    # Task signals — MOCK from GitHub (SRC-03) + Jira (SRC-04)
    task_generator = TaskSignalGenerator()
    task_signals = task_generator.generate(scenario_id)

    # Boundary signals — derived from temporal + communication
    boundary_engine = BoundarySignalEngine()
    boundary_signals = boundary_engine.compute(
        temporal_signals=temporal_signals,
        communication_signals=communication_signals,
        has_pto_today=False,
    )

    # Build response with all 24 signals
    signals = []

    for signal_id, value in temporal_signals.items():
        signals.append({
            "signal_id": signal_id,
            "value": value,
            "source_mode": "live",
            "captured_at": now.isoformat(),
        })

    for signal_id, value in communication_signals.items():
        signals.append({
            "signal_id": signal_id,
            "value": value,
            "source_mode": "mock",
            "captured_at": now.isoformat(),
        })

    for signal_id, value in task_signals.items():
        signals.append({
            "signal_id": signal_id,
            "value": value,
            "source_mode": "mock",
            "captured_at": now.isoformat(),
        })

    for signal_id, value in boundary_signals.items():
        signals.append({
            "signal_id": signal_id,
            "value": value,
            "source_mode": "live" if signal_id == "B-01" else "mock",
            "captured_at": now.isoformat(),
        })

    return {
        "user_id": str(user_id),
        "signals": signals,
    }
