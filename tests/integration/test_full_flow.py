"""Teste de integração: fluxo completo do sistema.

Este teste valida o fluxo principal usando banco SQLite em memória
com repositórios reais (SQLAlchemy).

Fluxo testado:
1. Criar paciente
2. Criar sessão AGENDADA
3. Atualizar sessão para CONCLUIDA
4. Verificar se FinancialEntry PENDENTE foi criado
5. Marcar lançamento como PAGO
6. Gerar relatório no período
"""

from datetime import date, datetime
from decimal import Decimal

import pytest

from app.domain.entities.patient import Patient
from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.financial_entry import EntryStatus
from app.use_cases.patient.create_patient import CreatePatientInput, CreatePatientUseCase
from app.use_cases.session.schedule_session import CreateSessionInput, CreateSessionUseCase
from app.use_cases.session.update_session_status import (
    UpdateSessionStatusInput,
    UpdateSessionStatusUseCase,
)
from app.use_cases.financial.financial_report import (
    FinancialReportInput,
    FinancialReportUseCase,
)


class TestFullFlow:
    """Teste de integração do fluxo completo."""

    @pytest.mark.asyncio
    async def test_fluxo_completo_sessao_ate_pagamento(
        self,
        patient_repository,
        session_repository,
        financial_repository,
    ):
        """
        Testa o fluxo completo:
        1. Criar paciente
        2. Criar sessão AGENDADA
        3. Realizar sessão (gera lançamento PENDENTE)
        4. Marcar como PAGO
        5. Gerar relatório
        """
        # ============================================================
        # 1. Criar Paciente
        # ============================================================
        create_patient_uc = CreatePatientUseCase(patient_repository)

        patient_input = CreatePatientInput(
            name="Ana Paula Santos",
            email="ana.paula@email.com",
            phone="(11) 98888-7777",
        )
        patient_output = await create_patient_uc.execute(patient_input)

        assert patient_output.name == "Ana Paula Santos"
        assert patient_output.active is True
        patient_id = patient_output.id

        # Verificar persistência
        saved_patient = await patient_repository.get_by_id(patient_id)
        assert saved_patient is not None
        assert saved_patient.name == "Ana Paula Santos"

        # ============================================================
        # 2. Criar Sessão AGENDADA
        # ============================================================
        create_session_uc = CreateSessionUseCase(session_repository, patient_repository)

        session_input = CreateSessionInput(
            patient_id=patient_id,
            date_time=datetime(2024, 12, 15, 14, 0),
            price=Decimal("200.00"),
            duration_minutes=50,
        )
        session_output = await create_session_uc.execute(session_input)

        assert session_output.status == SessionStatus.AGENDADA
        assert session_output.price == Decimal("200.00")
        session_id = session_output.id

        # ============================================================
        # 3. Realizar Sessão (deve criar FinancialEntry PENDENTE)
        # ============================================================
        update_status_uc = UpdateSessionStatusUseCase(
            session_repository, financial_repository
        )

        status_input = UpdateSessionStatusInput(
            session_id=session_id,
            new_status=SessionStatus.REALIZADA,
            notes="Sessão realizada com sucesso.",
        )
        status_output = await update_status_uc.execute(status_input)

        # Verificar transição de status
        assert status_output.previous_status == SessionStatus.AGENDADA
        assert status_output.new_status == SessionStatus.REALIZADA

        # Verificar que lançamento foi criado
        assert status_output.financial_entry_id is not None
        assert status_output.financial_entry_amount == Decimal("200.00")
        financial_entry_id = status_output.financial_entry_id

        # Verificar lançamento no banco
        pending = await financial_repository.list_pending()
        assert len(pending) == 1
        assert pending[0].id == financial_entry_id
        assert pending[0].status == EntryStatus.PENDENTE
        assert pending[0].session_id == session_id
        assert pending[0].patient_id == patient_id

        # ============================================================
        # 4. Marcar Lançamento como PAGO
        # ============================================================
        entry = await financial_repository.get_by_id(financial_entry_id)
        assert entry is not None

        # Usar método da entidade
        entry.mark_as_paid()
        await financial_repository.update(entry)

        # Verificar que foi atualizado
        updated_entry = await financial_repository.get_by_id(financial_entry_id)
        assert updated_entry.status == EntryStatus.PAGO
        assert updated_entry.paid_at is not None

        # Lista de pendentes agora vazia
        pending_after = await financial_repository.list_pending()
        assert len(pending_after) == 0

        # ============================================================
        # 5. Gerar Relatório Financeiro
        # ============================================================
        report_uc = FinancialReportUseCase(financial_repository)

        report_input = FinancialReportInput(
            start_date=date(2024, 12, 1),
            end_date=date(2024, 12, 31),
        )
        report_output = await report_uc.execute(report_input)

        # Verificar relatório
        assert report_output.total_entries == 1
        assert report_output.total_amount == Decimal("200.00")
        assert report_output.total_paid == Decimal("200.00")
        assert report_output.total_pending == Decimal("0")

        # Verificar detalhes do lançamento no relatório
        assert len(report_output.entries) == 1
        entry_summary = report_output.entries[0]
        assert entry_summary.session_id == session_id
        assert entry_summary.patient_id == patient_id
        assert entry_summary.status == EntryStatus.PAGO

    @pytest.mark.asyncio
    async def test_cancelar_sessao_nao_gera_lancamento(
        self,
        patient_repository,
        session_repository,
        financial_repository,
    ):
        """
        Testa que ao cancelar uma sessão, NÃO é gerado lançamento financeiro.
        """
        # Criar paciente
        create_patient_uc = CreatePatientUseCase(patient_repository)
        patient_output = await create_patient_uc.execute(
            CreatePatientInput(name="João Silva")
        )

        # Criar sessão
        create_session_uc = CreateSessionUseCase(session_repository, patient_repository)
        session_output = await create_session_uc.execute(
            CreateSessionInput(
                patient_id=patient_output.id,
                date_time=datetime(2024, 12, 20, 10, 0),
                price=Decimal("180.00"),
            )
        )

        # Cancelar sessão
        update_status_uc = UpdateSessionStatusUseCase(
            session_repository, financial_repository
        )
        status_output = await update_status_uc.execute(
            UpdateSessionStatusInput(
                session_id=session_output.id,
                new_status=SessionStatus.CANCELADA,
            )
        )

        # Verificar
        assert status_output.new_status == SessionStatus.CANCELADA
        assert status_output.financial_entry_id is None

        # Sem lançamentos
        pending = await financial_repository.list_pending()
        assert len(pending) == 0

    @pytest.mark.asyncio
    async def test_multiplas_sessoes_mesmo_paciente(
        self,
        patient_repository,
        session_repository,
        financial_repository,
    ):
        """
        Testa múltiplas sessões para o mesmo paciente.
        """
        # Criar paciente
        create_patient_uc = CreatePatientUseCase(patient_repository)
        patient = await create_patient_uc.execute(
            CreatePatientInput(name="Carlos Mendes", email="carlos@email.com")
        )

        # Criar e concluir 3 sessões
        create_session_uc = CreateSessionUseCase(session_repository, patient_repository)
        update_status_uc = UpdateSessionStatusUseCase(
            session_repository, financial_repository
        )

        for i, day in enumerate([1, 8, 15], 1):
            session = await create_session_uc.execute(
                CreateSessionInput(
                    patient_id=patient.id,
                    date_time=datetime(2024, 12, day, 14, 0),
                    price=Decimal("200.00"),
                )
            )
            await update_status_uc.execute(
                UpdateSessionStatusInput(
                    session_id=session.id,
                    new_status=SessionStatus.REALIZADA,
                )
            )

        # Verificar 3 lançamentos pendentes
        pending = await financial_repository.list_pending()
        assert len(pending) == 3

        # Relatório
        report_uc = FinancialReportUseCase(financial_repository)
        report = await report_uc.execute(
            FinancialReportInput(
                start_date=date(2024, 12, 1),
                end_date=date(2024, 12, 31),
            )
        )

        assert report.total_entries == 3
        assert report.total_amount == Decimal("600.00")
        assert report.total_pending == Decimal("600.00")
        assert report.total_paid == Decimal("0")
