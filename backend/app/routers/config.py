"""Configuration endpoints (EP-19, EP-20).

EP-19: GET /api/v1/config — Fetch current system configuration (CFG-01 through CFG-12)
EP-20: PATCH /api/v1/config — Update system configuration settings

Configuration from F-14. Changes to CFG-01–04 trigger immediate signal recalculation.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from app.config import settings

router = APIRouter()


def get_current_user_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


class ConfigUpdate(BaseModel):
    work_hours_start: Optional[str] = None
    work_hours_end: Optional[str] = None
    after_hours_threshold_mins: Optional[int] = None
    work_days: Optional[list] = None
    demo_mode_enabled: Optional[bool] = None
    demo_actor_name: Optional[str] = None
    timezone: Optional[str] = None
    data_retention_days: Optional[int] = None
    score_refresh_interval_mins: Optional[int] = None
    focus_block_duration_mins: Optional[int] = None
    back_to_back_gap_threshold_mins: Optional[int] = None
    weekend_alert_enabled: Optional[bool] = None


@router.get("")
async def get_config(user_id: uuid.UUID = Depends(get_current_user_id)):
    """EP-19: Fetch current system configuration.

    Returns all CFG-01 through CFG-12 settings from F-14.
    """
    return {
        "config": {
            "work_hours_start": settings.work_hours_start,
            "work_hours_end": settings.work_hours_end,
            "after_hours_threshold_mins": settings.after_hours_threshold_mins,
            "work_days": settings.work_days,
            "demo_mode_enabled": settings.demo_mode_enabled,
            "demo_actor_name": settings.demo_actor_name,
            "timezone": settings.timezone,
            "data_retention_days": settings.data_retention_days,
            "score_refresh_interval_mins": settings.score_refresh_interval_mins,
            "focus_block_duration_mins": settings.focus_block_duration_mins,
            "back_to_back_gap_threshold_mins": settings.back_to_back_gap_threshold_mins,
            "weekend_alert_enabled": settings.weekend_alert_enabled,
        }
    }


@router.patch("")
async def update_config(
    body: ConfigUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """EP-20: Update system configuration settings.

    All fields optional. Only provided fields are updated.
    Changes to CFG-01–04 trigger immediate signal recalculation.
    """
    updated_fields = {}

    if body.work_hours_start is not None:
        settings.work_hours_start = body.work_hours_start
        updated_fields["work_hours_start"] = body.work_hours_start
    if body.work_hours_end is not None:
        settings.work_hours_end = body.work_hours_end
        updated_fields["work_hours_end"] = body.work_hours_end
    if body.after_hours_threshold_mins is not None:
        settings.after_hours_threshold_mins = body.after_hours_threshold_mins
        updated_fields["after_hours_threshold_mins"] = body.after_hours_threshold_mins
    if body.work_days is not None:
        settings.work_days = body.work_days
        updated_fields["work_days"] = body.work_days
    if body.demo_mode_enabled is not None:
        settings.demo_mode_enabled = body.demo_mode_enabled
        updated_fields["demo_mode_enabled"] = body.demo_mode_enabled
    if body.demo_actor_name is not None:
        settings.demo_actor_name = body.demo_actor_name
        updated_fields["demo_actor_name"] = body.demo_actor_name
    if body.timezone is not None:
        settings.timezone = body.timezone
        updated_fields["timezone"] = body.timezone
    if body.data_retention_days is not None:
        settings.data_retention_days = body.data_retention_days
        updated_fields["data_retention_days"] = body.data_retention_days
    if body.score_refresh_interval_mins is not None:
        settings.score_refresh_interval_mins = body.score_refresh_interval_mins
        updated_fields["score_refresh_interval_mins"] = body.score_refresh_interval_mins
    if body.focus_block_duration_mins is not None:
        settings.focus_block_duration_mins = body.focus_block_duration_mins
        updated_fields["focus_block_duration_mins"] = body.focus_block_duration_mins
    if body.back_to_back_gap_threshold_mins is not None:
        settings.back_to_back_gap_threshold_mins = body.back_to_back_gap_threshold_mins
        updated_fields["back_to_back_gap_threshold_mins"] = body.back_to_back_gap_threshold_mins
    if body.weekend_alert_enabled is not None:
        settings.weekend_alert_enabled = body.weekend_alert_enabled
        updated_fields["weekend_alert_enabled"] = body.weekend_alert_enabled

    return {
        "config": updated_fields,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
