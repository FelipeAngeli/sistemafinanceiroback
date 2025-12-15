"""
Controller HTTP para Lançamentos Financeiros.

Stub para futura implementação com FastAPI.
"""

from typing import List
from uuid import UUID


class FinancialController:
    """Controller REST para lançamentos financeiros."""

    async def list(self, patient_id: UUID = None, status: str = None) -> List[dict]:
        """GET /financial - Lista lançamentos com filtros."""
        pass

    async def get(self, entry_id: UUID) -> dict:
        """GET /financial/{id} - Busca lançamento por ID."""
        pass

    async def mark_as_paid(self, entry_id: UUID) -> dict:
        """POST /financial/{id}/pay - Marca lançamento como pago."""
        pass
