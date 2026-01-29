"""
Testes para entidade Patient.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from app.core.exceptions import ValidationError
from app.domain.entities.patient import Patient


class TestPatient:
    """Testes da entidade Patient."""

    def test_create_patient(self):
        """Deve criar paciente com dados válidos."""
        patient = Patient(
            name="Ana Souza ",
            user_id=uuid4(),
            email="ana@example.com ",
            phone="(11) 99999-9999",
            observation="Prefere manhã.",
        )

        assert patient.name == "Ana Souza"
        assert patient.email == "ana@example.com"
        assert patient.phone == "(11) 99999-9999"
        assert patient.observation == "Prefere manhã."
        assert patient.active is True
        assert isinstance(patient.created_at, datetime)

    def test_invalid_name_raises_validation_error(self):
        """Não deve aceitar nome vazio."""
        with pytest.raises(ValidationError):
            Patient(name=" ", user_id=uuid4())

    def test_invalid_email_raises_validation_error(self):
        """Não deve aceitar email inválido."""
        with pytest.raises(ValidationError):
            Patient(name="Ana", user_id=uuid4(), email="invalid-email")

    def test_deactivate_and_activate_patient(self):
        """Deve alterar estado ativo e atualizar timestamp."""
        patient = Patient(name="João", user_id=uuid4())
        assert patient.updated_at is None

        patient.deactivate()
        assert patient.active is False
        first_update = patient.updated_at
        assert isinstance(first_update, datetime)

        patient.activate()
        assert patient.active is True
        assert patient.updated_at != first_update

    def test_update_patient_fields(self):
        """Deve atualizar campos corretamente."""
        patient = Patient(name="Joana", user_id=uuid4(), email="joana@ex.com")

        patient.update(
            name="Joana Lima",
            email="joanalima@example.com",
            phone="123",
            observation="obs",
        )

        assert patient.name == "Joana Lima"
        assert patient.email == "joanalima@example.com"
        assert patient.phone == "123"
        assert patient.observation == "obs"
        assert patient.updated_at is not None
