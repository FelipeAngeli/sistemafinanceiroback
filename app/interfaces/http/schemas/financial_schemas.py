"""Schemas Pydantic para Financial."""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.entities.financial_entry import EntryStatus


class FinancialEntryResponse(BaseModel):
    """Schema de resposta para lançamento financeiro."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    patient_id: UUID
    entry_date: date
    amount: Decimal
    status: EntryStatus
    description: str


class FinancialReportResponse(BaseModel):
    """Schema de resposta para relatório financeiro."""

    entries: list[FinancialEntryResponse]
    total_entries: int
    total_amount: Decimal
    total_pending: Decimal
    total_paid: Decimal
    period_start: date
    period_end: date
