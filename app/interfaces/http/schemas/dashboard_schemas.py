"""Schemas Pydantic para Dashboard."""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardFinancialStats(BaseModel):
    """Estatísticas financeiras do período."""
    
    total_received: Decimal = Field(..., description="Total recebido no período (em reais)")
    total_pending: Decimal = Field(..., description="Total pendente de recebimento (em reais)")
    total_entries: int = Field(..., description="Número total de lançamentos financeiros")
    pending_count: int = Field(..., description="Quantidade de lançamentos pendentes")
    entries: List[dict] = Field(default=[], description="Lista de lançamentos financeiros (opcional)")


class DashboardSessionItem(BaseModel):
    """Item de sessão para listagens do dashboard."""
    
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único da sessão")
    patient_id: UUID = Field(..., description="ID do paciente")
    patient_name: str = Field(..., description="Nome do paciente")
    date_time: datetime = Field(..., description="Data e hora da sessão")
    price: Decimal = Field(..., description="Valor da sessão em reais")
    status: str = Field(..., description="Status da sessão (agendada, realizada, cancelada, faltou)")


class DashboardSessionStats(BaseModel):
    """Estatísticas de sessões do período."""
    
    today: List[DashboardSessionItem] = Field(..., description="Sessões agendadas para hoje")
    recent: List[DashboardSessionItem] = Field(..., description="Sessões recentes (últimas realizadas)")
    total_month: int = Field(..., description="Total de sessões no período solicitado")


class DashboardPatientStats(BaseModel):
    """Estatísticas de pacientes."""
    
    total: int = Field(..., description="Número total de pacientes cadastrados")
    active: int = Field(..., description="Número de pacientes ativos")
    inactive: int = Field(..., description="Número de pacientes inativos")


class DashboardPeriod(BaseModel):
    """Período aplicado no filtro."""
    
    start: date = Field(..., description="Data inicial do período")
    end: date = Field(..., description="Data final do período")


class DashboardSummaryResponse(BaseModel):
    """Response agregado do dashboard com todas as estatísticas."""
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "financial": {
                        "total_received": 5000.00,
                        "total_pending": 2400.00,
                        "total_entries": 15,
                        "pending_count": 5,
                        "entries": []
                    },
                    "sessions": {
                        "today": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                                "patient_name": "Maria Silva",
                                "date_time": "2024-12-15T14:00:00",
                                "price": 200.00,
                                "status": "agendada"
                            }
                        ],
                        "recent": [
                            {
                                "id": "456e7890-a12b-34c5-d678-901234567890",
                                "patient_id": "321fedcb-a987-65d4-c321-ba0987654321",
                                "patient_name": "João Santos",
                                "date_time": "2024-12-14T15:00:00",
                                "price": 200.00,
                                "status": "concluida"
                            }
                        ],
                        "total_month": 25
                    },
                    "patients": {
                        "total": 30,
                        "active": 28,
                        "inactive": 2
                    },
                    "period": {
                        "start": "2024-12-01",
                        "end": "2024-12-31"
                    }
                }
            ]
        }
    )
    
    financial: DashboardFinancialStats = Field(..., description="Estatísticas financeiras do período")
    sessions: DashboardSessionStats = Field(..., description="Estatísticas de sessões")
    patients: DashboardPatientStats = Field(..., description="Estatísticas de pacientes")
    period: DashboardPeriod = Field(..., description="Período utilizado nos filtros")
