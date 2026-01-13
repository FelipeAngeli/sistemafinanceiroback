"""
Use Case: Resumo do Dashboard.

Consolida múltiplas informações do dashboard em uma única resposta:
- Relatório financeiro do período
- Sessões agendadas para hoje
- Sessões recentes
- Resumo de pacientes
"""

import asyncio
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import ValidationError
from app.domain.entities.financial_entry import EntryStatus
from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository
from app.use_cases.financial.financial_report import (
    FinancialEntrySummary,
    FinancialReportInput,
    FinancialReportOutput,
    FinancialReportUseCase,
)


@dataclass(frozen=True)
class DashboardSummaryInput:
    """Dados de entrada para resumo do dashboard."""

    start_date: date
    end_date: date


@dataclass(frozen=True)
class FinancialReportData:
    """Dados do relatório financeiro."""

    total_revenue: Decimal
    total_paid: Decimal
    total_pending: Decimal
    entries: List[FinancialEntrySummary]
    period_start: date
    period_end: date


@dataclass(frozen=True)
class SessionSummary:
    """Resumo de uma sessão para o dashboard."""

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: str
    notes: Optional[str]


@dataclass(frozen=True)
class PatientsSummary:
    """Resumo de pacientes."""

    total_patients: int
    active_patients: int
    inactive_patients: int


@dataclass(frozen=True)
class DashboardSummaryOutput:
    """Dados de saída do resumo do dashboard."""

    financial_report: FinancialReportData
    today_sessions: List[SessionSummary]
    recent_sessions: List[SessionSummary]
    patients_summary: PatientsSummary


class DashboardSummaryUseCase:
    """Caso de uso para gerar resumo do dashboard.

    Otimiza performance executando queries em paralelo quando possível.
    """

    def __init__(
        self,
        financial_repository: FinancialEntryRepository,
        session_repository: SessionRepository,
        patient_repository: PatientRepository,
    ) -> None:
        self._financial_repo = financial_repository
        self._session_repo = session_repository
        self._patient_repo = patient_repository
        self._financial_report_uc = FinancialReportUseCase(financial_repository)

    async def execute(self, input_data: DashboardSummaryInput) -> DashboardSummaryOutput:
        """Executa a geração do resumo do dashboard."""
        # Validar período
        self._validate_period(input_data.start_date, input_data.end_date)

        # Data de hoje para filtrar sessões
        today = date.today()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)

        # Executar queries em paralelo para melhor performance
        financial_report_task = self._get_financial_report(input_data)
        today_sessions_task = self._get_today_sessions(today_start, today_end)
        recent_sessions_task = self._get_recent_sessions()
        patients_summary_task = self._get_patients_summary()

        # Aguardar todas as queries
        (
            financial_report_output,
            today_sessions,
            recent_sessions,
            patients_summary,
        ) = await asyncio.gather(
            financial_report_task,
            today_sessions_task,
            recent_sessions_task,
            patients_summary_task,
        )

        # Converter relatório financeiro para formato do dashboard
        financial_report_data = FinancialReportData(
            total_revenue=financial_report_output.total_amount,
            total_paid=financial_report_output.total_paid,
            total_pending=financial_report_output.total_pending,
            entries=financial_report_output.entries[:100],  # Limitar a 100 entradas
            period_start=financial_report_output.period_start,
            period_end=financial_report_output.period_end,
        )

        return DashboardSummaryOutput(
            financial_report=financial_report_data,
            today_sessions=today_sessions,
            recent_sessions=recent_sessions,
            patients_summary=patients_summary,
        )

    def _validate_period(self, start_date: date, end_date: date) -> None:
        """Valida o período de datas."""
        if start_date > end_date:
            raise ValidationError(
                "Data inicial não pode ser maior que data final.",
                field="start_date",
            )

        # Validar que período não excede 1 ano (opcional, para performance)
        days_diff = (end_date - start_date).days
        if days_diff > 365:
            raise ValidationError(
                "Período não pode exceder 1 ano.",
                field="period",
            )

    async def _get_financial_report(
        self, input_data: DashboardSummaryInput
    ) -> FinancialReportOutput:
        """Busca relatório financeiro do período."""
        report_input = FinancialReportInput(
            start_date=input_data.start_date,
            end_date=input_data.end_date,
        )
        return await self._financial_report_uc.execute(report_input)

    async def _get_today_sessions(
        self, today_start: datetime, today_end: datetime
    ) -> List[SessionSummary]:
        """Busca sessões agendadas para hoje."""
        from app.domain.entities.session import SessionStatus
        
        sessions = await self._session_repo.list_all(
            status=SessionStatus.AGENDADA.value,
            start_date=today_start.date(),
            end_date=today_end.date(),
            limit=100,  # Limitar para performance
        )

        return [
            SessionSummary(
                id=s.id,
                patient_id=s.patient_id,
                date_time=s.date_time,
                price=s.price,
                duration_minutes=s.duration_minutes,
                status=s.status.value,
                notes=s.notes,
            )
            for s in sessions
        ]

    async def _get_recent_sessions(self) -> List[SessionSummary]:
        """Busca últimas 10 sessões recentes."""
        sessions = await self._session_repo.list_recent(limit=10)

        return [
            SessionSummary(
                id=s.id,
                patient_id=s.patient_id,
                date_time=s.date_time,
                price=s.price,
                duration_minutes=s.duration_minutes,
                status=s.status.value,
                notes=s.notes,
            )
            for s in sessions
        ]

    async def _get_patients_summary(self) -> PatientsSummary:
        """Busca resumo de pacientes (total, ativos, inativos)."""
        # Buscar todos os pacientes (ativos e inativos)
        all_patients = await self._patient_repo.list_all(active_only=False)
        active_patients = await self._patient_repo.list_all(active_only=True)

        total = len(all_patients)
        active = len(active_patients)
        inactive = total - active

        return PatientsSummary(
            total_patients=total,
            active_patients=active,
            inactive_patients=inactive,
        )
