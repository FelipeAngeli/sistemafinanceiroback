"""Routers FastAPI."""

from app.interfaces.http.routers.dashboard_router import router as dashboard_router
from app.interfaces.http.routers.patient_router import router as patient_router
from app.interfaces.http.routers.session_router import router as session_router
from app.interfaces.http.routers.financial_router import router as financial_router
from app.interfaces.http.routers.health_router import router as health_router

__all__ = [
    "dashboard_router",
    "patient_router",
    "session_router",
    "financial_router",
    "health_router",
]
