"""Use Case: Atualizar Status da Sessão.

Responsável por atualizar o status de uma sessão.
REGRA IMPORTANTE: Ao concluir uma sessão, cria automaticamente
um lançamento financeiro com status PENDENTE.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.core.exceptions import BusinessRuleError, EntityNotFoundError
from app.domain.entities.financial_entry import FinancialEntry
from app.domain.entities.session import Session, SessionStatus
from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.domain.repositories.session_repository import SessionRepository


@dataclass(frozen=True)
class UpdateSessionStatusInput:
    """Dados de entrada para atualização de status."""

    session_id: UUID
    new_status: SessionStatus
    notes: Optional[str] = None


@dataclass(frozen=True)
class UpdateSessionStatusOutput:
    """Dados de saída após atualização de status."""

    session_id: UUID
    previous_status: SessionStatus
    new_status: SessionStatus
    financial_entry_id: Optional[UUID] = None  # Preenchido se criou lançamento
    financial_entry_amount: Optional[Decimal] = None


class UpdateSessionStatusUseCase:
    """Caso de uso para atualizar status de uma sessão.

    Fluxo:
        1. Busca sessão por ID
        2. Valida transição de status
        3. Atualiza status na entidade
        4. SE status == CONCLUIDA:
           - Verifica se já existe lançamento financeiro
           - Se não existir, cria lançamento com status PENDENTE
        5. Persiste alterações
        6. Retorna output com informações da operação

    Regra de Negócio:
        Quando uma sessão é CONCLUÍDA, o sistema DEVE criar automaticamente
        um lançamento financeiro pendente com o valor da sessão.
    """

    def __init__(
        self,
        session_repository: SessionRepository,
        financial_repository: FinancialEntryRepository,
    ) -> None:
        self._session_repository = session_repository
        self._financial_repository = financial_repository

    async def execute(
        self, input_data: UpdateSessionStatusInput
    ) -> UpdateSessionStatusOutput:
        """Executa a atualização de status da sessão."""
        # 1. Buscar sessão
        session = await self._session_repository.get_by_id(input_data.session_id)
        if not session:
            raise EntityNotFoundError("Sessão", str(input_data.session_id))

        previous_status = session.status

        # 2. Validar e aplicar transição de status
        self._apply_status_transition(session, input_data.new_status)

        # 3. Atualizar notas se fornecidas
        if input_data.notes:
            session.notes = input_data.notes

        # 4. Persistir sessão atualizada
        await self._session_repository.update(session)

        # 5. Se concluída, criar lançamento financeiro
        financial_entry: Optional[FinancialEntry] = None
        if input_data.new_status == SessionStatus.CONCLUIDA:
            financial_entry = await self._create_financial_entry_if_not_exists(session)

        # 6. Retornar output
        return UpdateSessionStatusOutput(
            session_id=session.id,
            previous_status=previous_status,
            new_status=session.status,
            financial_entry_id=financial_entry.id if financial_entry else None,
            financial_entry_amount=financial_entry.amount if financial_entry else None,
        )

    def _apply_status_transition(
        self, session: Session, new_status: SessionStatus
    ) -> None:
        """Aplica a transição de status na entidade Session."""
        if new_status == SessionStatus.CONCLUIDA:
            session.complete()  # Valida internamente se pode concluir
        elif new_status == SessionStatus.CANCELADA:
            session.cancel()  # Valida internamente se pode cancelar
        elif new_status == SessionStatus.AGENDADA:
            raise BusinessRuleError(
                "Não é possível voltar uma sessão para status AGENDADA."
            )

    async def _create_financial_entry_if_not_exists(
        self, session: Session
    ) -> Optional[FinancialEntry]:
        """Cria lançamento financeiro se ainda não existir para a sessão."""
        # Verificar se já existe lançamento para esta sessão
        pending_entries = await self._financial_repository.list_pending()
        existing = next(
            (e for e in pending_entries if e.session_id == session.id), None
        )

        if existing:
            # Já existe lançamento, não criar duplicado
            return existing

        # Criar novo lançamento financeiro
        entry = FinancialEntry.create_from_session(
            session_id=session.id,
            patient_id=session.patient_id,
            amount=session.price,
            session_date=session.date_time,
            description=f"Sessão de {session.date_time.strftime('%d/%m/%Y %H:%M')}",
        )

        return await self._financial_repository.create(entry)
