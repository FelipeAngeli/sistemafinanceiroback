"""Testes unitários para UpdateSessionStatusUseCase.

Foco principal: validar que ao concluir uma sessão,
um lançamento financeiro PENDENTE é criado automaticamente.
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.financial_entry import EntryStatus
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.use_cases.session.update_session_status import (
    UpdateSessionStatusInput,
    UpdateSessionStatusUseCase,
)
from tests.fakes import FakeSessionRepository, FakeFinancialEntryRepository


class TestUpdateSessionStatusUseCase:
    """Testes para UpdateSessionStatusUseCase."""

    @pytest.fixture
    def session_repo(self) -> FakeSessionRepository:
        """Repositório fake de sessões."""
        return FakeSessionRepository()

    @pytest.fixture
    def financial_repo(self) -> FakeFinancialEntryRepository:
        """Repositório fake financeiro."""
        return FakeFinancialEntryRepository()

    @pytest.fixture
    def use_case(
        self, session_repo: FakeSessionRepository, financial_repo: FakeFinancialEntryRepository
    ) -> UpdateSessionStatusUseCase:
        """Instância do caso de uso."""
        return UpdateSessionStatusUseCase(
            session_repository=session_repo,
            financial_repository=financial_repo,
        )

    @pytest.fixture
    def agendada_session(self) -> Session:
        """Sessão agendada para testes."""
        return Session(
            patient_id=uuid4(),
            date_time=datetime(2024, 12, 15, 14, 0),
            price=Decimal("200.00"),
            status=SessionStatus.AGENDADA,
        )

    # ============================================================
    # Testes de Sucesso
    # ============================================================

    @pytest.mark.asyncio
    async def test_concluir_sessao_cria_lancamento_financeiro(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
        financial_repo: FakeFinancialEntryRepository,
        agendada_session: Session,
    ):
        """Ao concluir sessão, deve criar lançamento financeiro PENDENTE."""
        # Arrange
        await session_repo.create(agendada_session)

        input_data = UpdateSessionStatusInput(
            session_id=agendada_session.id,
            new_status=SessionStatus.CONCLUIDA,
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert - Status atualizado
        assert output.previous_status == SessionStatus.AGENDADA
        assert output.new_status == SessionStatus.CONCLUIDA

        # Assert - Lançamento financeiro criado
        assert output.financial_entry_id is not None
        assert output.financial_entry_amount == Decimal("200.00")

        # Assert - Lançamento está pendente
        pending = await financial_repo.list_pending()
        assert len(pending) == 1
        assert pending[0].session_id == agendada_session.id
        assert pending[0].status == EntryStatus.PENDENTE

    @pytest.mark.asyncio
    async def test_concluir_sessao_nao_duplica_lancamento(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
        financial_repo: FakeFinancialEntryRepository,
        agendada_session: Session,
    ):
        """Se já existe lançamento para a sessão, não deve duplicar."""
        # Arrange - Criar sessão
        await session_repo.create(agendada_session)

        # Act - Concluir primeira vez
        input_data = UpdateSessionStatusInput(
            session_id=agendada_session.id,
            new_status=SessionStatus.CONCLUIDA,
        )
        output1 = await use_case.execute(input_data)

        # Assert - Apenas um lançamento
        pending = await financial_repo.list_pending()
        assert len(pending) == 1
        assert output1.financial_entry_id == pending[0].id

    @pytest.mark.asyncio
    async def test_cancelar_sessao_nao_cria_lancamento(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
        financial_repo: FakeFinancialEntryRepository,
        agendada_session: Session,
    ):
        """Ao cancelar sessão, NÃO deve criar lançamento financeiro."""
        # Arrange
        await session_repo.create(agendada_session)

        input_data = UpdateSessionStatusInput(
            session_id=agendada_session.id,
            new_status=SessionStatus.CANCELADA,
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert
        assert output.new_status == SessionStatus.CANCELADA
        assert output.financial_entry_id is None

        pending = await financial_repo.list_pending()
        assert len(pending) == 0

    @pytest.mark.asyncio
    async def test_concluir_sessao_com_notas(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
        agendada_session: Session,
    ):
        """Ao concluir, deve atualizar notas da sessão."""
        # Arrange
        await session_repo.create(agendada_session)

        input_data = UpdateSessionStatusInput(
            session_id=agendada_session.id,
            new_status=SessionStatus.CONCLUIDA,
            notes="Paciente apresentou melhora significativa.",
        )

        # Act
        await use_case.execute(input_data)

        # Assert
        updated = await session_repo.get_by_id(agendada_session.id)
        assert updated.notes == "Paciente apresentou melhora significativa."

    # ============================================================
    # Testes de Erro
    # ============================================================

    @pytest.mark.asyncio
    async def test_sessao_nao_encontrada(
        self,
        use_case: UpdateSessionStatusUseCase,
    ):
        """Deve lançar erro se sessão não existe."""
        input_data = UpdateSessionStatusInput(
            session_id=uuid4(),
            new_status=SessionStatus.CONCLUIDA,
        )

        with pytest.raises(NotFoundError) as exc_info:
            await use_case.execute(input_data)

        assert "não encontrado" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_nao_pode_concluir_sessao_ja_cancelada(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
    ):
        """Não deve permitir concluir sessão já cancelada."""
        # Arrange
        session = Session(
            patient_id=uuid4(),
            date_time=datetime(2024, 12, 15, 14, 0),
            price=Decimal("200.00"),
            status=SessionStatus.CANCELADA,
        )
        # Bypass validation para criar sessão já cancelada
        object.__setattr__(session, "status", SessionStatus.CANCELADA)
        await session_repo.create(session)

        input_data = UpdateSessionStatusInput(
            session_id=session.id,
            new_status=SessionStatus.CONCLUIDA,
        )

        # Act & Assert
        with pytest.raises(BusinessRuleError) as exc_info:
            await use_case.execute(input_data)

        assert "não pode ser concluída" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_nao_pode_cancelar_sessao_ja_concluida(
        self,
        use_case: UpdateSessionStatusUseCase,
        session_repo: FakeSessionRepository,
    ):
        """Não deve permitir cancelar sessão já concluída."""
        # Arrange
        session = Session(
            patient_id=uuid4(),
            date_time=datetime(2024, 12, 15, 14, 0),
            price=Decimal("200.00"),
        )
        # Bypass para criar como concluída
        object.__setattr__(session, "status", SessionStatus.CONCLUIDA)
        await session_repo.create(session)

        input_data = UpdateSessionStatusInput(
            session_id=session.id,
            new_status=SessionStatus.CANCELADA,
        )

        # Act & Assert
        with pytest.raises(BusinessRuleError):
            await use_case.execute(input_data)
