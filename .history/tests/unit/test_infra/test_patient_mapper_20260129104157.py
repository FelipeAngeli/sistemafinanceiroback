"""Testes para PatientMapper."""

from datetime import datetime
from uuid import uuid4

from app.domain.entities.patient import Patient
from app.infra.db.mappers.patient_mapper import PatientMapper
from app.infra.db.models.patient_model import PatientModel


def _make_patient() -> Patient:
    return Patient(
        id=uuid4(),
        name="Maria",
        user_id=uuid4(),
        email="maria@example.com",
        phone="(11) 99999-9999",
        observation="obs",
        active=False,
    )


def test_to_model_maps_all_fields():
    patient = _make_patient()
    model = PatientMapper.to_model(patient)

    assert model.id == str(patient.id)
    assert model.name == patient.name
    assert model.email == patient.email
    assert model.phone == patient.phone
    assert model.observation == patient.observation
    assert model.active == patient.active
    assert model.created_at == patient.created_at
    assert model.updated_at == patient.updated_at


def test_to_entity_maps_back_to_domain():
    model = PatientModel(
        id=str(uuid4()),
        user_id=str(uuid4()),
        name="José",
        email="jose@example.com",
        phone="(11) 88888-8888",
        observation="anotação",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    entity = PatientMapper.to_entity(model)

    assert str(entity.id) == model.id
    assert entity.name == model.name
    assert entity.email == model.email
    assert entity.phone == model.phone
    assert entity.observation == model.observation
    assert entity.active == model.active
    assert entity.created_at == model.created_at
    assert entity.updated_at == model.updated_at


def test_update_model_applies_entity_changes():
    model = PatientModel(
        id=str(uuid4()),
        user_id=str(uuid4()),
        name="Original",
        email="original@example.com",
        phone="(11) 77777-7777",
        observation="",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    entity = Patient(
        id=uuid4(),
        name="Atualizado",
        user_id=uuid4(),
        email="new@example.com",
        phone="(11) 66666-6666",
        observation="obs",
        active=False,
    )

    PatientMapper.update_model(model, entity)

    assert model.name == entity.name
    assert model.email == entity.email
    assert model.phone == entity.phone
    assert model.observation == entity.observation
    assert model.active == entity.active
