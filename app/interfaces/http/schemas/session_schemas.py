"""Schemas Pydantic para Session."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.session import SessionStatus


class SessionCreate(BaseModel):
    """Schema para criação de sessão."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                    "date_time": "2024-12-15T14:00:00",
                    "price": 200.00,
                    "duration_minutes": 50,
                    "notes": "Primeira sessão de terapia cognitiva"
                }
            ]
        }
    )

    patient_id: UUID = Field(..., description="ID do paciente para quem a sessão será agendada")
    date_time: datetime = Field(..., description="Data e hora da sessão", examples=["2024-12-15T14:00:00"])
    price: Decimal = Field(..., ge=0, description="Valor da sessão em reais", examples=[200.00])
    duration_minutes: int = Field(default=50, ge=1, description="Duração da sessão em minutos", examples=[50])
    notes: Optional[str] = Field(None, description="Observações sobre a sessão")


class SessionUpdate(BaseModel):
    """Schema para atualização parcial de sessão. Todos os campos são opcionais."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "date_time": "2024-12-20T15:00:00",
                    "price": 250.00,
                    "notes": "Sessão remarcada - ajuste de horário"
                },
                {
                    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                    "price": 180.00
                }
            ]
        }
    )

    patient_id: Optional[UUID] = Field(None, description="Novo ID do paciente (transferir sessão)")
    date_time: Optional[datetime] = Field(None, description="Nova data e hora da sessão", examples=["2024-12-15T14:00:00"])
    price: Optional[Decimal] = Field(None, ge=0, description="Novo valor da sessão em reais", examples=[200.00])
    notes: Optional[str] = Field(None, description="Atualizar observações da sessão")


class SessionResponse(BaseModel):
    """Schema de resposta completo para sessão."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                    "date_time": "2024-12-15T14:00:00",
                    "price": 200.00,
                    "duration_minutes": 50,
                    "status": "agendada",
                    "notes": "Primeira sessão de terapia cognitiva",
                    "created_at": "2024-12-01T10:30:00",
                    "updated_at": "2024-12-10T15:45:00"
                }
            ]
        }
    )

    id: UUID = Field(..., description="ID único da sessão")
    patient_id: UUID = Field(..., description="ID do paciente")
    date_time: datetime = Field(..., description="Data e hora da sessão")
    price: Decimal = Field(..., description="Valor da sessão em reais")
    duration_minutes: int = Field(..., description="Duração da sessão em minutos")
    status: SessionStatus = Field(..., description="Status da sessão (agendada, realizada, cancelada, faltou)")
    notes: Optional[str] = Field(None, description="Observações sobre a sessão")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")


class SessionStatusUpdate(BaseModel):
    """Schema para atualização de status da sessão."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "new_status": "realizada",
                    "notes": "Sessão realizada com sucesso"
                },
                {
                    "new_status": "cancelada",
                    "notes": "Cancelada por solicitação do paciente"
                },
                {
                    "new_status": "faltou",
                    "notes": "Paciente não compareceu"
                }
            ]
        }
    )

    new_status: SessionStatus = Field(..., description="Novo status da sessão", examples=["realizada"])
    notes: Optional[str] = Field(None, description="Observações sobre a mudança de status", examples=["Sessão realizada com sucesso"])


class SessionStatusResponse(BaseModel):
    """Schema de resposta para atualização de status. Quando realizada, gera lançamento financeiro."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "session_id": "123e4567-e89b-12d3-a456-426614174000",
                    "previous_status": "agendada",
                    "new_status": "realizada",
                    "financial_entry_created": True,
                    "financial_entry_id": "456e7890-a12b-34c5-d678-901234567890",
                    "financial_entry_amount": 200.00
                }
            ]
        }
    )

    session_id: UUID = Field(..., description="ID da sessão atualizada")
    previous_status: SessionStatus = Field(..., description="Status anterior da sessão")
    new_status: SessionStatus = Field(..., description="Novo status da sessão")
    financial_entry_created: bool = Field(default=False, description="Indica se um lançamento financeiro foi criado")
    financial_entry_id: Optional[UUID] = Field(None, description="ID do lançamento financeiro criado (se aplicável)")
    financial_entry_amount: Optional[Decimal] = Field(None, description="Valor do lançamento financeiro (se criado)")


class SessionListItem(BaseModel):
    """Item de sessão na listagem."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID único da sessão")
    patient_id: UUID = Field(..., description="ID do paciente")
    date_time: datetime = Field(..., description="Data e hora da sessão")
    price: Decimal = Field(..., description="Valor da sessão em reais")
    duration_minutes: int = Field(..., description="Duração da sessão em minutos")
    status: SessionStatus = Field(..., description="Status da sessão")
    notes: Optional[str] = Field(None, description="Observações sobre a sessão")


class SessionListResponse(BaseModel):
    """Schema de resposta para listagem de sessões com paginação."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "sessions": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                            "date_time": "2024-12-15T14:00:00",
                            "price": 200.00,
                            "duration_minutes": 50,
                            "status": "agendada",
                            "notes": "Primeira sessão"
                        }
                    ],
                    "total": 1
                }
            ]
        }
    )

    sessions: list[SessionListItem] = Field(..., description="Lista de sessões encontradas")
    total: int = Field(..., description="Número total de sessões (considerando filtros)")
