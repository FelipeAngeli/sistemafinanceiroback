"""
Controller HTTP para Sessões.

Stub para futura implementação com FastAPI.
"""

from typing import List
from uuid import UUID


class SessionController:
    """Controller REST para sessões."""

    async def schedule(self, data: dict) -> dict:
        """POST /sessions - Agenda uma nova sessão."""
        pass

    async def get(self, session_id: UUID) -> dict:
        """GET /sessions/{id} - Busca sessão por ID."""
        pass

    async def list(self, patient_id: UUID = None, status: str = None) -> List[dict]:
        """GET /sessions - Lista sessões com filtros."""
        pass

    async def complete(self, session_id: UUID, data: dict = None) -> dict:
        """POST /sessions/{id}/complete - Conclui uma sessão."""
        pass

    async def cancel(self, session_id: UUID) -> dict:
        """POST /sessions/{id}/cancel - Cancela uma sessão."""
        pass
