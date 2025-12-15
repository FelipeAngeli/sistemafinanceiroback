"""Entidade FinancialEntry (Lançamento Financeiro).

Representa um lançamento financeiro gerado a partir de uma sessão concluída.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
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
    amount: Decimal
    entry_date: date
    description: str = ""
    status: EntryStatus = EntryStatus.PENDENTE
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validações após inicialização."""
        self._ensure_decimal_amount()
        self._validate_amount()

    def _ensure_decimal_amount(self) -> None:
        """Garante que amount seja Decimal."""
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))

    def _validate_amount(self) -> None:
        """Valida que valor não seja negativo."""
        amount_value = Decimal(str(self.amount)) if not isinstance(self.amount, Decimal) else self.amount
        if amount_value < 0:
            raise ValidationError("Valor do lançamento não pode ser negativo.")

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
        self.paid_at = datetime.utcnow()

    def is_overdue(self, reference_date: Optional[date] = None) -> bool:
        """Verifica se está em atraso (pendente e data já passou)."""
        if not self.is_pending():
            return False
        ref = reference_date or date.today()
        return self.entry_date < ref

    @classmethod
    def create_from_session(
        cls,
        session_id: UUID,
        patient_id: UUID,
        amount: Decimal,
        session_date: datetime,
        description: str = "",
    ) -> "FinancialEntry":
        """Factory method para criar lançamento a partir de sessão concluída."""
        return cls(
            session_id=session_id,
            patient_id=patient_id,
            amount=amount,
            entry_date=session_date.date(),
            description=description or "Sessão de atendimento",
        )
