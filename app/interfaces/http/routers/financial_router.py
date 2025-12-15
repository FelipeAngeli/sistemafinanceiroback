"""Router para endpoints Financeiros."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.domain.entities.financial_entry import EntryStatus
from app.interfaces.http.dependencies import FinancialReportUC
from app.interfaces.http.schemas.financial_schemas import (
    FinancialEntryResponse,
    FinancialReportResponse,
)
from app.use_cases.financial.financial_report import FinancialReportInput

router = APIRouter(prefix="/financial", tags=["Financeiro"])


@router.get(
    "/entries",
    response_model=FinancialReportResponse,
    summary="Listar lançamentos financeiros",
    description=(
        "Lista lançamentos financeiros em um período, "
        "com totais consolidados e filtros opcionais por status."
    ),
)
async def list_financial_entries(
    use_case: FinancialReportUC,
    start_date: date = Query(
        ...,
        description="Data inicial do período",
        examples=["2024-01-01"],
    ),
    end_date: date = Query(
        ...,
        description="Data final do período",
        examples=["2024-12-31"],
    ),
    status: Optional[list[EntryStatus]] = Query(
        None,
        description="Filtrar por status (pendente, pago). Pode passar múltiplos.",
        examples=[["pendente"]],
    ),
) -> FinancialReportResponse:
    """Lista lançamentos financeiros com relatório consolidado."""
    input_data = FinancialReportInput(
        start_date=start_date,
        end_date=end_date,
        status_filter=status,
    )
    output = await use_case.execute(input_data)
    return FinancialReportResponse(
        entries=[
            FinancialEntryResponse(
                id=e.id,
                session_id=e.session_id,
                patient_id=e.patient_id,
                entry_date=e.entry_date,
                amount=e.amount,
                status=e.status,
                description=e.description,
            )
            for e in output.entries
        ],
        total_entries=output.total_entries,
        total_amount=output.total_amount,
        total_pending=output.total_pending,
        total_paid=output.total_paid,
        period_start=output.period_start,
        period_end=output.period_end,
    )
