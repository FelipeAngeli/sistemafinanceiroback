"""Use Case: Criar Sessão.

Responsável por criar uma nova sessão de atendimento.
Não cria lançamento financeiro - isso ocorre apenas ao concluir.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.core.exceptions import EntityNotFoundError
from app.domain.entities.session import Session, SessionStatus
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class CreateSessionInput:
    """Dados de entrada para criação de sessão."""

    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int = 50
    notes: Optional[str] = None


@dataclass(frozen=True)
class CreateSessionOutput:
    """Dados de saída após criação de sessão."""

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class CreateSessionUseCase:
    """Caso de uso para criar uma nova sessão.

    Fluxo:
        1. Valida se paciente existe
        2. Cria entidade Session com status AGENDADA
        3. Persiste via repositório
        4. Retorna output (não cria lançamento financeiro aqui)
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        patient_repository: PatientRepository,
    ) -> None:
        self._session_repository = session_repository
        self._patient_repository = patient_repository

    async def execute(self, input_data: CreateSessionInput) -> CreateSessionOutput:
        """Executa a criação da sessão."""
        # Verificar se paciente existe
        patient = await self._patient_repository.get_by_id(input_data.patient_id)
        if not patient:
            raise EntityNotFoundError("Paciente", str(input_data.patient_id))

        # Criar sessão (sempre inicia como AGENDADA)
        session = Session(
            patient_id=input_data.patient_id,
            date_time=input_data.date_time,
            price=input_data.price,
            duration_minutes=input_data.duration_minutes,
            notes=input_data.notes,
            status=SessionStatus.AGENDADA,
        )

        # Persistir
        saved_session = await self._session_repository.create(session)

        return CreateSessionOutput(
            id=saved_session.id,
            patient_id=saved_session.patient_id,
            date_time=saved_session.date_time,
            price=saved_session.price,
            duration_minutes=saved_session.duration_minutes,
            status=saved_session.status,
            notes=saved_session.notes,
            created_at=saved_session.created_at,
            updated_at=saved_session.updated_at,
        )
