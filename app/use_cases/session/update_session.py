"""Use Case: Atualizar Sessão.

Responsável por atualizar os dados de uma sessão existente.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.core.exceptions import EntityNotFoundError, NotFoundError, ValidationError
from app.domain.entities.session import SessionStatus
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class UpdateSessionInput:
    """Dados de entrada para atualização de sessão."""

    session_id: UUID
    patient_id: Optional[UUID] = None
    date_time: Optional[datetime] = None
    price: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class UpdateSessionOutput:
    """Dados de saída após atualização de sessão."""

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class UpdateSessionUseCase:
    """Caso de uso para atualizar sessão.

    Fluxo:
        1. Busca sessão pelo ID
        2. Valida se paciente existe (se patient_id for informado)
        3. Atualiza campos da entidade
        4. Persiste alterações
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        patient_repository: PatientRepository,
    ) -> None:
        self._session_repository = session_repository
        self._patient_repository = patient_repository

    async def execute(self, input_data: UpdateSessionInput) -> UpdateSessionOutput:
        """Executa a atualização da sessão."""
        # 1. Buscar sessão
        session = await self._session_repository.get_by_id(input_data.session_id)
        if not session:
            raise NotFoundError(resource="Sessão", resource_id=str(input_data.session_id))

        # 2. Validar paciente se foi alterado
        if input_data.patient_id and input_data.patient_id != session.patient_id:
            patient = await self._patient_repository.get_by_id(input_data.patient_id)
            if not patient:
                raise ValidationError(f"Paciente com ID {input_data.patient_id} não encontrado.", field="patient_id")
            session.patient_id = input_data.patient_id

        # 3. Atualizar campos
        if input_data.date_time is not None:
            # TODO: Validar conflito de horário? Por enquanto apenas atualiza.
            if session.status == SessionStatus.AGENDADA:
                session.reschedule(input_data.date_time)
            else:
                # Se não for reagendamento padrão, apenas atualiza o campo para histórico
                # (embora reschedule force status agendada, aqui vamos permitir edição direta se for admin/correção)
                # A regra de negócio diz "não atualizar status por este endpoint".
                # Mas se mudou a data, logicamente é um reagendamento se estiver agendada.
                # Se já foi concluída, pode ser uma correção de registro.
                session.date_time = input_data.date_time
                session.updated_at = datetime.utcnow()

        if input_data.price is not None:
            session.price = input_data.price
            session.updated_at = datetime.utcnow()

        if input_data.notes is not None:
            session.notes = input_data.notes
            session.updated_at = datetime.utcnow()

        # 4. Persistir
        # O repositório deve lidar com a persistência
        updated_session = await self._session_repository.update(session)

        return UpdateSessionOutput(
            id=updated_session.id,
            patient_id=updated_session.patient_id,
            date_time=updated_session.date_time,
            price=updated_session.price,
            duration_minutes=updated_session.duration_minutes,
            status=updated_session.status,
            notes=updated_session.notes,
            created_at=updated_session.created_at,
            updated_at=updated_session.updated_at,
        )
