"""Testes unitários para FinancialReportUseCase."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.use_cases.financial.financial_report import (
    FinancialReportInput,
    FinancialReportUseCase,
)
from tests.fakes import FakeFinancialEntryRepository


class TestFinancialReportUseCase:
    """Testes para FinancialReportUseCase."""

    @pytest.fixture
    def financial_repo(self) -> FakeFinancialEntryRepository:
        """Repositório fake financeiro."""
        return FakeFinancialEntryRepository()

    @pytest.fixture
    def use_case(
        self, financial_repo: FakeFinancialEntryRepository
    ) -> FinancialReportUseCase:
        """Instância do caso de uso."""
        return FinancialReportUseCase(financial_repository=financial_repo)

    @pytest.fixture
    def report_user_id(self) -> UUID:
        """Usuário comum para os lançamentos."""
        return uuid4()

    @pytest.fixture
    def sample_entries(self, report_user_id: UUID) -> list[FinancialEntry]:
        """Lista de lançamentos de exemplo."""
        patient_id = uuid4()
        return [
            FinancialEntry(
                session_id=uuid4(),
                patient_id=patient_id,
                user_id=report_user_id,
                amount=Decimal("200.00"),
                entry_date=date(2024, 12, 1),
                status=EntryStatus.PAGO,
            ),
            FinancialEntry(
                session_id=uuid4(),
                patient_id=patient_id,
                user_id=report_user_id,
                amount=Decimal("200.00"),
                entry_date=date(2024, 12, 8),
                status=EntryStatus.PAGO,
            ),
            FinancialEntry(
                session_id=uuid4(),
                patient_id=patient_id,
                user_id=report_user_id,
                amount=Decimal("200.00"),
                entry_date=date(2024, 12, 15),
                status=EntryStatus.PENDENTE,
            ),
            FinancialEntry(
                session_id=uuid4(),
                patient_id=patient_id,
                user_id=report_user_id,
                amount=Decimal("250.00"),
                entry_date=date(2024, 12, 22),
                status=EntryStatus.PENDENTE,
            ),
        ]

    # ============================================================
    # Testes de Sucesso
    # ============================================================

    @pytest.mark.asyncio
    async def test_relatorio_periodo_completo(
        self,
        use_case: FinancialReportUseCase,
        financial_repo: FakeFinancialEntryRepository,
        sample_entries: list[FinancialEntry],
        report_user_id: UUID,
    ):
        """Deve retornar relatório completo do período."""
        # Arrange
        for entry in sample_entries:
            await financial_repo.create(entry)

        input_data = FinancialReportInput(
            user_id=report_user_id,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert
        assert output.total_entries == 4
        assert output.total_amount == Decimal("850.00")
        assert output.total_paid == Decimal("400.00")
        assert output.total_pending == Decimal("450.00")
        assert output.period_start == date(2024, 12, 1)
        assert output.period_end == date(2024, 12, 31)

    @pytest.mark.asyncio
    async def test_relatorio_filtrado_por_status_pendente(
        self,
        use_case: FinancialReportUseCase,
        financial_repo: FakeFinancialEntryRepository,
        sample_entries: list[FinancialEntry],
        report_user_id: UUID,
    ):
        """Deve filtrar apenas lançamentos pendentes."""
        # Arrange
        for entry in sample_entries:
            await financial_repo.create(entry)

        input_data = FinancialReportInput(
            user_id=report_user_id,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            status_filter=[EntryStatus.PENDENTE],
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert
        assert output.total_entries == 2
        assert output.total_pending == Decimal("450.00")
        assert output.total_paid == Decimal("0")
        assert all(e.status == EntryStatus.PENDENTE for e in output.entries)

    @pytest.mark.asyncio
    async def test_relatorio_filtrado_por_status_pago(
        self,
        use_case: FinancialReportUseCase,
        financial_repo: FakeFinancialEntryRepository,
        sample_entries: list[FinancialEntry],
        report_user_id: UUID,
    ):
        """Deve filtrar apenas lançamentos pagos."""
        # Arrange
        for entry in sample_entries:
            await financial_repo.create(entry)

        input_data = FinancialReportInput(
            user_id=report_user_id,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
            status_filter=[EntryStatus.PAGO],
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert
        assert output.total_entries == 2
        assert output.total_paid == Decimal("400.00")
        assert output.total_pending == Decimal("0")

    @pytest.mark.asyncio
    async def test_relatorio_periodo_parcial(
        self,
        use_case: FinancialReportUseCase,
        financial_repo: FakeFinancialEntryRepository,
        sample_entries: list[FinancialEntry],
        report_user_id: UUID,
    ):
        """Deve considerar apenas lançamentos dentro do período."""
        # Arrange
        for entry in sample_entries:
            await financial_repo.create(entry)

        input_data = FinancialReportInput(
            user_id=report_user_id,
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 10),
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert - Apenas 2 lançamentos no período
        assert output.total_entries == 2
        assert output.total_amount == Decimal("400.00")

    @pytest.mark.asyncio
    async def test_relatorio_periodo_vazio(
        self,
        use_case: FinancialReportUseCase,
        financial_repo: FakeFinancialEntryRepository,
    ):
        """Deve retornar relatório vazio se não houver lançamentos."""
        input_data = FinancialReportInput(
            user_id=uuid4(),
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )

        # Act
        output = await use_case.execute(input_data)

        # Assert
        assert output.total_entries == 0
        assert output.total_amount == Decimal("0")
        assert output.total_pending == Decimal("0")
        assert output.total_paid == Decimal("0")
        assert len(output.entries) == 0
