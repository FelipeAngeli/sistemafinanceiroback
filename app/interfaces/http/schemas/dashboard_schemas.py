"""Schemas Pydantic para Dashboard."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.financial_entry import EntryStatus


class FinancialEntrySummarySchema(BaseModel):
    """Schema de resumo de lançamento financeiro."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    patient_id: UUID
    entry_date: date
    amount: Decimal
    status: EntryStatus
    description: str


class FinancialReportSchema(BaseModel):
    """Schema de relatório financeiro."""

    total_revenue: Decimal = Field(..., description="Receita total do período")
    total_paid: Decimal = Field(..., description="Total pago")
    total_pending: Decimal = Field(..., description="Total pendente")
    entries: List[FinancialEntrySummarySchema] = Field(
        ..., description="Lista de lançamentos (limitado a 100)"
    )
    period_start: date = Field(..., description="Data inicial do período")
    period_end: date = Field(..., description="Data final do período")


class SessionSummarySchema(BaseModel):
    """Schema de resumo de sessão."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: str
    notes: Optional[str] = None


class PatientsSummarySchema(BaseModel):
    """Schema de resumo de pacientes."""

    total_patients: int = Field(..., description="Total de pacientes")
    active_patients: int = Field(..., description="Pacientes ativos")
    inactive_patients: int = Field(..., description="Pacientes inativos")


class DashboardSummaryResponse(BaseModel):
    """Schema de resposta do resumo do dashboard."""

    financial_report: FinancialReportSchema
    today_sessions: List[SessionSummarySchema] = Field(
        ..., description="Sessões agendadas para hoje"
    )
    recent_sessions: List[SessionSummarySchema] = Field(
        ..., description="Últimas 10 sessões recentes"
    )
    patients_summary: PatientsSummarySchema
