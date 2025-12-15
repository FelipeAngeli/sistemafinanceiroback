"""Schemas Pydantic para Patient."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreate(BaseModel):
    """Schema para criação de paciente."""

    name: str = Field(..., min_length=2, max_length=255, examples=["Maria Silva"])
    email: Optional[EmailStr] = Field(None, examples=["maria@email.com"])
    phone: Optional[str] = Field(None, max_length=50, examples=["(11) 99999-9999"])
    notes: Optional[str] = Field(None, examples=["Observações sobre o paciente"])


class PatientResponse(BaseModel):
    """Schema de resposta para paciente."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    active: bool


class PatientListResponse(BaseModel):
    """Schema de resposta para listagem de pacientes."""

    patients: list[PatientResponse]
    total: int
