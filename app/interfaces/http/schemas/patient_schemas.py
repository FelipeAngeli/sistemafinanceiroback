"""Schemas Pydantic para Patient."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreate(BaseModel):
    """Schema para criação de paciente."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Maria Silva",
                    "email": "maria.silva@email.com",
                    "phone": "(11) 99999-9999",
                    "observation": "Paciente com histórico de ansiedade. Prefere sessões no período da tarde.",
                    "active": True
                },
                {
                    "name": "João Santos",
                    "email": "joao@email.com",
                    "phone": "(21) 98888-8888",
                    "observation": None,
                    "active": True
                }
            ]
        }
    )

    name: str = Field(..., min_length=2, max_length=255, description="Nome completo do paciente", examples=["Maria Silva"])
    email: Optional[EmailStr] = Field(None, description="Email do paciente (opcional)", examples=["maria@email.com"])
    phone: Optional[str] = Field(None, max_length=50, description="Telefone de contato (opcional)", examples=["(11) 99999-9999"])
    observation: Optional[str] = Field(None, description="Observações e anotações sobre o paciente", examples=["Observações sobre o paciente"])
    active: bool = Field(default=True, description="Indica se o paciente está ativo")


class PatientResponse(BaseModel):
    """Schema de resposta para paciente."""

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Maria Silva",
                    "email": "maria.silva@email.com",
                    "phone": "(11) 99999-9999",
                    "observation": "Observação importante",
                    "active": True
                }
            ]
        }
    )

    id: UUID = Field(..., description="ID único do paciente")
    name: str = Field(..., description="Nome completo do paciente")
    email: Optional[str] = Field(None, description="Email do paciente")
    phone: Optional[str] = Field(None, description="Telefone de contato")
    observation: Optional[str] = Field(None, description="Observações sobre o paciente")
    active: bool = Field(..., description="Indica se o paciente está ativo no sistema")


class PatientListResponse(BaseModel):
    """Schema de resposta para listagem de pacientes."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "patients": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Maria Silva",
                            "email": "maria.silva@email.com",
                            "phone": "(11) 99999-9999",
                            "active": True
                        },
                        {
                            "id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                            "name": "João Santos",
                            "email": "joao@email.com",
                            "phone": "(21) 98888-8888",
                            "active": True
                        }
                    ],
                    "total": 2
                }
            ]
        }
    )

    patients: list[PatientResponse] = Field(..., description="Lista de pacientes encontrados")
    total: int = Field(..., description="Número total de pacientes")


class PatientSummaryResponse(BaseModel):
    """Schema para resumo estatístico de pacientes."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total": 25,
                    "active": 22,
                    "inactive": 3,
                    "percentage_active": 88.0
                }
            ]
        }
    )

    total: int = Field(..., description="Número total de pacientes cadastrados")
    active: int = Field(..., description="Número de pacientes ativos")
    inactive: int = Field(..., description="Número de pacientes inativos")
    percentage_active: float = Field(..., description="Percentual de pacientes ativos (0-100)")
