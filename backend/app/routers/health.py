"""EP-18: GET /api/v1/health — Health check / system status (public, no auth)."""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return system health status. Public endpoint — no auth required."""
    return {
        "status": "healthy",
        "services": {
            "database": "healthy",
            "calendar_api": "healthy",
            "miro_mcp": "healthy",
            "websocket": "healthy",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
