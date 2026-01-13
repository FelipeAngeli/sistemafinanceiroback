"""
Use Case: Buscar Sessão por ID.

Responsável por buscar uma sessão específica pelo seu ID.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.domain.entities.session import SessionStatus
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class GetSessionByIdInput:
    """Dados de entrada para busca de sessão por ID."""

    session_id: UUID


@dataclass(frozen=True)
class GetSessionByIdOutput:
    """Dados de saída da busca de sessão."""

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class GetSessionByIdUseCase:
    """Caso de uso para buscar sessão por ID.

    Fluxo:
        1. Valida se o ID é um UUID válido (validado pelo FastAPI)
        2. Busca sessão no repositório
        3. Se não encontrada, lança NotFoundError
        4. Retorna dados da sessão
    """

    def __init__(self, session_repository: SessionRepository) -> None:
        self._repository = session_repository

    async def execute(self, input_data: GetSessionByIdInput) -> GetSessionByIdOutput:
        """Executa a busca de sessão por ID."""
        session = await self._repository.get_by_id(input_data.session_id)

        if not session:
            raise NotFoundError(
                resource="Sessão",
                resource_id=str(input_data.session_id),
            )

        return GetSessionByIdOutput(
            id=session.id,
            patient_id=session.patient_id,
            date_time=session.date_time,
            price=session.price,
            duration_minutes=session.duration_minutes,
            status=session.status,
            notes=session.notes,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
