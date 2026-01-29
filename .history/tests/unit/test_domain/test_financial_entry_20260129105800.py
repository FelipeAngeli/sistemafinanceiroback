"""Testes para entidade FinancialEntry."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import BusinessRuleError, ValidationError
from app.domain.entities.financial_entry import EntryStatus, FinancialEntry


class TestFinancialEntry:
    """Testes da entidade FinancialEntry."""

    def test_create_financial_entry(self):
        """Deve criar lançamento pendente válido."""
        entry = FinancialEntry(
            session_id=uuid4(),
            patient_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal("150.00"),
            entry_date=date.today(),
            description="Sessão semanal",
        )

        assert entry.status == EntryStatus.PENDENTE
        assert entry.amount == Decimal("150.00")
        assert entry.description == "Sessão semanal"
        assert entry.paid_at is None

    def test_invalid_amount_raises_validation_error(self):
        """Valor negativo não é permitido."""
        with pytest.raises(ValidationError):
            FinancialEntry(
                session_id=uuid4(),
                patient_id=uuid4(),
                user_id=uuid4(),
                amount=Decimal("-10"),
                entry_date=date.today(),
            )

    def test_mark_as_paid_updates_status_and_timestamp(self):
        """Deve marcar como pago e registrar paid_at."""
        entry = FinancialEntry(
            session_id=uuid4(),
            patient_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal("200.50"),
            entry_date=date.today(),
        )

        entry.mark_as_paid()
        assert entry.status == EntryStatus.PAGO
        assert entry.paid_at is not None

        with pytest.raises(BusinessRuleError):
            entry.mark_as_paid()

    def test_is_overdue_checks_pending_entries(self):
        """Somente pendentes com data passada são considerados em atraso."""
        entry = FinancialEntry(
            session_id=uuid4(),
            patient_id=uuid4(),
            user_id=uuid4(),
            amount=Decimal("100"),
            entry_date=date.today() - timedelta(days=3),
        )

        assert entry.is_overdue()

        entry.mark_as_paid()
        assert entry.is_overdue() is False

    def test_create_from_session_factory(self):
        """Factory deve preencher campos corretamente."""
        session_id = uuid4()
        patient_id = uuid4()
        user_id = uuid4()
        entry = FinancialEntry.create_from_session(
            session_id=session_id,
            patient_id=patient_id,
            user_id=user_id,
            amount=Decimal("180"),
            session_date=datetime.now(UTC),
            description="Sessão especial",
        )

        assert entry.session_id == session_id
        assert entry.patient_id == patient_id
        assert entry.entry_date == entry.created_at.date()
        assert entry.description == "Sessão especial"
