"""Entidade Session (Sessão).

Representa uma sessão de atendimento psicológico.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from app.core.exceptions import BusinessRuleError, ValidationError


class SessionStatus(str, Enum):
    """Status possíveis de uma sessão."""

    AGENDADA = "agendada"
    REALIZADA = "realizada"
    CANCELADA = "cancelada"
    FALTOU = "faltou"


@dataclass
class Session:
    """Entidade Sessão."""

    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int = 50
    status: SessionStatus = SessionStatus.AGENDADA
    notes: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._validate_price()
        self._validate_duration()
        self._ensure_decimal_price()

    def _ensure_decimal_price(self) -> None:
        """Garante que price seja Decimal."""
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))

    def _validate_price(self) -> None:
        """Valida que preço não seja negativo."""
        price_value = Decimal(str(self.price)) if not isinstance(self.price, Decimal) else self.price
        if price_value < 0:
            raise ValidationError("Preço não pode ser negativo.")

    def _validate_duration(self) -> None:
        """Valida duração da sessão."""
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise ValidationError("Duração deve ser maior que zero.")

    def is_completable(self) -> bool:
        """Verifica se sessão pode ser marcada como realizada ou faltou."""
        return self.status == SessionStatus.AGENDADA

    def is_cancellable(self) -> bool:
        """Verifica se sessão pode ser cancelada."""
        return self.status == SessionStatus.AGENDADA

    def mark_as_realized(self) -> None:
        """Marca sessão como realizada."""
        if not self.is_completable():
            raise BusinessRuleError(
                f"Sessão com status '{self.status.value}' não pode ser marcada como realizada."
            )
        self.status = SessionStatus.REALIZADA
        self.updated_at = datetime.utcnow()

    def mark_as_missed(self) -> None:
        """Marca sessão como faltou (paciente não compareceu)."""
        if not self.is_completable():
            raise BusinessRuleError(
                f"Sessão com status '{self.status.value}' não pode ser marcada como faltou."
            )
        self.status = SessionStatus.FALTOU
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela a sessão."""
        if not self.is_cancellable():
            raise BusinessRuleError(
                f"Sessão com status '{self.status.value}' não pode ser cancelada."
            )
        self.status = SessionStatus.CANCELADA
        self.updated_at = datetime.utcnow()

    def reschedule(self, new_date_time: datetime) -> None:
        """Reagenda a sessão para nova data/hora."""
        if self.status != SessionStatus.AGENDADA:
            raise BusinessRuleError("Apenas sessões agendadas podem ser reagendadas.")
        self.date_time = new_date_time
        self.updated_at = datetime.utcnow()
