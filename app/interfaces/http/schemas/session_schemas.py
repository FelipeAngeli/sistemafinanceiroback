"""Schemas Pydantic para Session."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.session import SessionStatus


class SessionCreate(BaseModel):
    """Schema para criação de sessão."""

    patient_id: UUID
    date_time: datetime = Field(..., examples=["2024-12-15T14:00:00"])
    price: Decimal = Field(..., ge=0, examples=[200.00])
    duration_minutes: int = Field(default=50, ge=1, examples=[50])
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    """Schema de resposta para sessão."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str] = None


class SessionStatusUpdate(BaseModel):
    """Schema para atualização de status da sessão."""

    new_status: SessionStatus = Field(..., examples=["concluida"])
    notes: Optional[str] = Field(None, examples=["Sessão realizada com sucesso"])


class SessionStatusResponse(BaseModel):
    """Schema de resposta para atualização de status."""

    session_id: UUID
    previous_status: SessionStatus
    new_status: SessionStatus
    financial_entry_created: bool = False
    financial_entry_id: Optional[UUID] = None
    financial_entry_amount: Optional[Decimal] = None


class SessionListItem(BaseModel):
    """Item de sessão na listagem."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str] = None


class SessionListResponse(BaseModel):
    """Schema de resposta para listagem de sessões."""

    sessions: list[SessionListItem]
    total: int
