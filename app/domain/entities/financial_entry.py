"""Entidade FinancialEntry (Lançamento Financeiro).

Representa um lançamento financeiro gerado a partir de uma sessão concluída.
"""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from app.core.exceptions import BusinessRuleError, ValidationError


class EntryStatus(str, Enum):
    """Status de um lançamento financeiro."""

    PENDENTE = "pendente"
    PAGO = "pago"


@dataclass
class FinancialEntry:
    """Entidade Lançamento Financeiro."""

    session_id: UUID
    patient_id: UUID
    user_id: UUID
    amount: Decimal
    entry_date: date
    description: str = ""
    status: EntryStatus = EntryStatus.PENDENTE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    paid_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._ensure_decimal_amount()
        self._validate_amount()
        self._validate_description()
        self._validate_entry_date()

    def _ensure_decimal_amount(self) -> None:
        """Garante que amount seja Decimal."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def _validate_amount(self) -> None:
        """Valida que valor não seja negativo e dentro de limites razoáveis."""
        amount_value = Decimal(str(self.amount)) if not isinstance(self.amount, Decimal) else self.amount
        if amount_value < 0:
            raise ValidationError("Valor do lançamento não pode ser negativo.")
        # Limite máximo de R$ 10.000,00 por lançamento
        max_amount = Decimal("10000.00")
        if amount_value > max_amount:
            raise ValidationError(f"Valor não pode ser maior que R$ {max_amount:,.2f}.")

    def _validate_description(self) -> None:
        """Valida descrição do lançamento."""
        if len(self.description) > 500:
            raise ValidationError("Descrição não pode ter mais de 500 caracteres.")

    def _validate_entry_date(self) -> None:
        """Valida data do lançamento."""
        from datetime import timedelta
        
        # Data não pode ser muito antiga (mais de 10 anos no passado)
        min_date = date.today() - timedelta(days=3650)  # ~10 anos
        if self.entry_date < min_date:
            raise ValidationError("Data do lançamento não pode ser muito antiga (mais de 10 anos).")
        # Data não pode ser muito futura (mais de 1 ano)
        max_date = date.today() + timedelta(days=365)
        if self.entry_date > max_date:
            raise ValidationError("Data do lançamento não pode ser muito futura (mais de 1 ano).")

    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status == EntryStatus.PENDENTE

    def is_paid(self) -> bool:
        """Verifica se está pago."""
        return self.status == EntryStatus.PAGO

    def mark_as_paid(self) -> None:
        """Marca lançamento como pago."""
        if self.is_paid():
            raise BusinessRuleError("Lançamento já está pago.")
        self.status = EntryStatus.PAGO
        self.paid_at = datetime.now(UTC)

    def mark_as_pending(self) -> None:
        """Marca lançamento como pendente novamente (reversão de pagamento)."""
        if not self.is_paid():
            raise BusinessRuleError("Lançamento já está pendente.")
        self.status = EntryStatus.PENDENTE
        self.paid_at = None

    def is_overdue(self, reference_date: Optional[date] = None) -> bool:
        """Verifica se está em atraso (pendente e data já passou)."""
        if not self.is_pending():
            return False
        ref = reference_date or date.today()
        return self.entry_date < ref

    def days_overdue(self, reference_date: Optional[date] = None) -> int:
        """Retorna número de dias em atraso."""
        if not self.is_overdue(reference_date):
            return 0
        ref = reference_date or date.today()
        return (ref - self.entry_date).days

    def can_be_paid(self) -> bool:
        """Verifica se o lançamento pode ser marcado como pago."""
        return self.is_pending()

    def can_be_reversed(self) -> bool:
        """Verifica se o pagamento pode ser revertido."""
        return self.is_paid()

    @classmethod
    def create_from_session(
        cls,
        session_id: UUID,
        patient_id: UUID,
        user_id: UUID,
        amount: Decimal,
        session_date: datetime,
        description: str = "",
    ) -> "FinancialEntry":
        """Factory method para criar lançamento a partir de sessão concluída."""
        return cls(
            session_id=session_id,
            patient_id=patient_id,
            user_id=user_id,
            amount=amount,
            entry_date=session_date.date(),
            description=description or "Sessão de atendimento",
        )
