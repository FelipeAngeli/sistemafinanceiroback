"""Use Case: Relatório Financeiro.

Responsável por gerar relatório financeiro de um período.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import ValidationError
from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.domain.repositories.financial_repository import FinancialEntryRepository


@dataclass(frozen=True)
class FinancialReportInput:
    """Dados de entrada para relatório financeiro."""

    start_date: date
    end_date: date
    status_filter: Optional[List[EntryStatus]] = None


@dataclass(frozen=True)
class FinancialEntrySummary:
    """Resumo de um lançamento para o relatório."""

    id: UUID
    session_id: UUID
    patient_id: UUID
    entry_date: date
    amount: Decimal
    status: EntryStatus
    description: str


@dataclass
class FinancialReportOutput:
    """Dados de saída do relatório financeiro."""

    entries: List[FinancialEntrySummary]
    total_entries: int
    total_amount: Decimal
    total_pending: Decimal
    total_paid: Decimal
    period_start: date
    period_end: date


class FinancialReportUseCase:
    """Caso de uso para gerar relatório financeiro.

    Fluxo:
        1. Busca lançamentos no período especificado
        2. Filtra por status se especificado
        3. Calcula totais (geral, pendente, pago)
        4. Retorna relatório consolidado
    """

    def __init__(self, financial_repository: FinancialEntryRepository) -> None:
        self._repository = financial_repository

    async def execute(self, input_data: FinancialReportInput) -> FinancialReportOutput:
        """Executa a geração do relatório financeiro."""
        # Validar período
        self._validate_period(input_data.start_date, input_data.end_date)
        
        # Buscar lançamentos no período
        entries = await self._repository.list_by_period(
            start_date=input_data.start_date,
            end_date=input_data.end_date,
            status_filter=input_data.status_filter,
        )

        # Converter para summaries
        summaries = [
            FinancialEntrySummary(
                id=e.id,
                session_id=e.session_id,
                patient_id=e.patient_id,
                entry_date=e.entry_date,
                amount=e.amount,
                status=e.status,
                description=e.description,
            )
            for e in entries
        ]

        # Calcular totais
        total_amount = sum((e.amount for e in entries), Decimal("0"))
        total_pending = sum(
            (e.amount for e in entries if e.status == EntryStatus.PENDENTE),
            Decimal("0"),
        )
        total_paid = sum(
            (e.amount for e in entries if e.status == EntryStatus.PAGO),
            Decimal("0"),
        )

        return FinancialReportOutput(
            entries=summaries,
            total_entries=len(entries),
            total_amount=total_amount,
            total_pending=total_pending,
            total_paid=total_paid,
            period_start=input_data.start_date,
            period_end=input_data.end_date,
        )

    def _validate_period(self, start_date: date, end_date: date) -> None:
        """Valida o período de datas do relatório."""
        if start_date > end_date:
            raise ValidationError(
                "Data inicial não pode ser maior que data final.",
                field="start_date",
            )
        
        # Validar que período não excede 5 anos (para performance)
        from datetime import timedelta
        max_period = timedelta(days=365 * 5)
        if (end_date - start_date) > max_period:
            raise ValidationError(
                "Período não pode exceder 5 anos.",
                field="period",
            )
