"""CLB FastAPI Application — Cognitive Load Balancer MVP 1.0."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, config, consent, health, interventions, miro, scenarios, scores, signals, team, user_data

app = FastAPI(
    title="Cognitive Load Balancer",
    description="Your Miro board thinks. Your agent acts.",
    version="1.0.0",
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["system"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(consent.router, prefix="/api/v1/consent", tags=["consent"])
app.include_router(user_data.router, prefix="/api/v1/user", tags=["user-data"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(scores.router, prefix="/api/v1/scores", tags=["scores"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"])
app.include_router(miro.router, prefix="/api/v1/miro", tags=["miro"])
app.include_router(interventions.router, prefix="/api/v1/interventions", tags=["interventions"])
app.include_router(team.router, prefix="/api/v1/team", tags=["team"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
