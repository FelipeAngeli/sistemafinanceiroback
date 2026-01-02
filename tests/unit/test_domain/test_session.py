"""
Testes para entidade Session.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.core.exceptions import BusinessRuleError, ValidationError
from app.domain.entities.session import Session, SessionStatus


class TestSession:
    """Testes da entidade Session."""

    def test_create_session_with_scheduled_status(self):
        """Deve criar sessão com status agendado e validar dados."""
        session = Session(
            patient_id=uuid4(),
            date_time=datetime.utcnow(),
            price=Decimal("200.00"),
            duration_minutes=50,
            notes="Primeira sessão",
        )

        assert session.status == SessionStatus.AGENDADA
        assert session.price == Decimal("200.00")
        assert session.duration_minutes == 50
        assert session.notes == "Primeira sessão"

    def test_invalid_price_raises_validation_error(self):
        """Não deve aceitar preço negativo."""
        with pytest.raises(ValidationError):
            Session(
                patient_id=uuid4(),
                date_time=datetime.utcnow(),
                price=Decimal("-1"),
            )

    def test_invalid_duration_raises_validation_error(self):
        """Não deve aceitar duração menor/igual a zero."""
        with pytest.raises(ValidationError):
            Session(
                patient_id=uuid4(),
                date_time=datetime.utcnow(),
                price=Decimal("100"),
                duration_minutes=0,
            )

    def test_complete_session(self):
        """Deve concluir sessão corretamente."""
        session = Session(
            patient_id=uuid4(),
            date_time=datetime.utcnow(),
            price=Decimal("200"),
        )

        session.mark_as_realized()
        assert session.status == SessionStatus.REALIZADA
        assert session.updated_at is not None

    def test_mark_as_missed_with_invalid_status(self):
        """Não deve permitir marcar como faltou se não estiver agendada."""
        session = Session(
            patient_id=uuid4(),
            date_time=datetime.utcnow(),
            price=Decimal("200"),
            status=SessionStatus.CANCELADA,
        )

        with pytest.raises(BusinessRuleError):
            session.mark_as_missed()

    def test_cancel_session(self):
        """Deve cancelar sessão corretamente."""
        session = Session(
            patient_id=uuid4(),
            date_time=datetime.utcnow(),
            price=Decimal("200"),
        )

        session.cancel()
        assert session.status == SessionStatus.CANCELADA
        assert session.updated_at is not None

    def test_reschedule_session(self):
        """Deve reagendar sessão apenas se agendada."""
        session = Session(
            patient_id=uuid4(),
            date_time=datetime.utcnow(),
            price=Decimal("150"),
        )

        new_date = datetime.utcnow() + timedelta(days=3)
        session.reschedule(new_date)
        assert session.date_time == new_date

        session.status = SessionStatus.REALIZADA
        with pytest.raises(BusinessRuleError):
            session.reschedule(datetime.utcnow())
