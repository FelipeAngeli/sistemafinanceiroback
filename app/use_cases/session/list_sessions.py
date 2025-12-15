"""
Use Case: Listar Sessões.

Responsável por listar sessões com filtros opcionais.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.domain.entities.session import SessionStatus
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class ListSessionsInput:
    """Dados de entrada para listagem de sessões."""

    patient_id: Optional[UUID] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 50


@dataclass(frozen=True)
class SessionSummary:
    """Resumo de uma sessão para listagem."""

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str]


@dataclass
class ListSessionsOutput:
    """Dados de saída da listagem de sessões."""

    sessions: List[SessionSummary]
    total: int


class ListSessionsUseCase:
    """Caso de uso para listar sessões.

    Fluxo:
        1. Busca sessões no repositório com filtros
        2. Converte para lista de resumos
        3. Retorna output com lista e total
    """

    def __init__(self, session_repository: SessionRepository) -> None:
        self._repository = session_repository

    async def execute(self, input_data: ListSessionsInput) -> ListSessionsOutput:
        """Executa a listagem de sessões."""
        sessions = await self._repository.list_all(
            patient_id=input_data.patient_id,
            status=input_data.status,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
            limit=input_data.limit,
        )

        summaries = [
            SessionSummary(
                id=s.id,
                patient_id=s.patient_id,
                date_time=s.date_time,
                price=s.price,
                duration_minutes=s.duration_minutes,
                status=s.status,
                notes=s.notes,
            )
            for s in sessions
        ]

        return ListSessionsOutput(
            sessions=summaries,
            total=len(summaries),
        )
