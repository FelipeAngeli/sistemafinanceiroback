"""Entidade Session (Sessão).

Representa uma sessão de atendimento psicológico.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
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

    user_id: UUID
    patient_id: UUID
    date_time: datetime
    price: Decimal
    duration_minutes: int = 50
    status: SessionStatus = SessionStatus.AGENDADA
    notes: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._validate_price()
        self._validate_duration()
        self._validate_notes()
        self._ensure_decimal_price()

    def _ensure_decimal_price(self) -> None:
        """Garante que price seja Decimal."""
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))

    def _validate_price(self) -> None:
        """Valida que preço não seja negativo e dentro de limites razoáveis."""
        price_value = Decimal(str(self.price)) if not isinstance(self.price, Decimal) else self.price
        if price_value < 0:
            raise ValidationError("Preço não pode ser negativo.")
        # Limite máximo de R$ 10.000,00 por sessão
        max_price = Decimal("10000.00")
        if price_value > max_price:
            raise ValidationError(f"Preço não pode ser maior que R$ {max_price:,.2f}.")

    def _validate_duration(self) -> None:
        """Valida duração da sessão."""
        if self.duration_minutes is not None and self.duration_minutes <= 0:
            raise ValidationError("Duração deve ser maior que zero.")
        # Duração máxima de 8 horas (480 minutos)
        max_duration = 480
        if self.duration_minutes > max_duration:
            raise ValidationError(f"Duração não pode ser maior que {max_duration} minutos.")

    def _validate_notes(self) -> None:
        """Valida observações da sessão."""
        if self.notes is not None and len(self.notes) > 2000:
            raise ValidationError("Observações não podem ter mais de 2000 caracteres.")

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
        self.updated_at = datetime.now(UTC)

    def mark_as_missed(self) -> None:
        """Marca sessão como faltou (paciente não compareceu)."""
        if not self.is_completable():
            raise BusinessRuleError(
                f"Sessão com status '{self.status.value}' não pode ser marcada como faltou."
            )
        self.status = SessionStatus.FALTOU
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancela a sessão."""
        if not self.is_cancellable():
            raise BusinessRuleError(
                f"Sessão com status '{self.status.value}' não pode ser cancelada."
            )
        self.status = SessionStatus.CANCELADA
        self.updated_at = datetime.now(UTC)

    def reschedule(self, new_date_time: datetime) -> None:
        """Reagenda a sessão para nova data/hora."""
        if self.status != SessionStatus.AGENDADA:
            raise BusinessRuleError("Apenas sessões agendadas podem ser reagendadas.")
        # Valida que a nova data não seja muito antiga (mais de 1 ano no passado)
        now = datetime.now(UTC)
        one_year_ago = now.replace(year=now.year - 1)
        if new_date_time.tzinfo is None:
            new_date_time = new_date_time.replace(tzinfo=UTC)
        if new_date_time < one_year_ago:
            raise ValidationError("Não é possível agendar sessões com mais de 1 ano de antecedência.")
        self.date_time = new_date_time
        self.updated_at = datetime.now(UTC)

    def is_scheduled(self) -> bool:
        """Verifica se a sessão está agendada."""
        return self.status == SessionStatus.AGENDADA

    def is_completed(self) -> bool:
        """Verifica se a sessão foi concluída (realizada ou faltou)."""
        return self.status in (SessionStatus.REALIZADA, SessionStatus.FALTOU)

    def is_realized(self) -> bool:
        """Verifica se a sessão foi realizada."""
        return self.status == SessionStatus.REALIZADA

    def is_cancelled(self) -> bool:
        """Verifica se a sessão foi cancelada."""
        return self.status == SessionStatus.CANCELADA

    def is_missed(self) -> bool:
        """Verifica se o paciente faltou à sessão."""
        return self.status == SessionStatus.FALTOU

    def can_generate_financial_entry(self) -> bool:
        """Verifica se a sessão pode gerar um lançamento financeiro."""
        return self.status == SessionStatus.REALIZADA
