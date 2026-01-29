"""Testes para SessionMapper."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.domain.entities.session import Session, SessionStatus
from app.infra.db.mappers.session_mapper import SessionMapper
from app.infra.db.models.session_model import SessionModel


def _make_session(status: SessionStatus = SessionStatus.AGENDADA) -> Session:
    return Session(
        id=uuid4(),
        user_id=uuid4(),
        patient_id=uuid4(),
        date_time=datetime.now(UTC),
        price=Decimal("150.50"),
        duration_minutes=45,
        status=status,
        notes="Anotação",
    )


def test_to_model_maps_fields():
    session = _make_session()

    model = SessionMapper.to_model(session)

    assert model.id == str(session.id)
    assert model.patient_id == str(session.patient_id)
    assert model.date_time == session.date_time
    assert model.duration_minutes == session.duration_minutes
    assert model.price == session.price
    assert model.status == session.status.value
    assert model.notes == session.notes


def test_to_entity_converts_decimal_and_status():
    model = SessionModel(
        id=str(uuid4()),
        user_id=str(uuid4()),
        patient_id=str(uuid4()),
        date_time=datetime.now(UTC),
        duration_minutes=60,
        price=Decimal("200.00"),
        status=SessionStatus.REALIZADA.value,
        notes="Finalizada",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    entity = SessionMapper.to_entity(model)

    assert str(entity.id) == model.id
    assert str(entity.patient_id) == model.patient_id
    assert entity.price == Decimal("200.00")
    assert entity.status == SessionStatus.REALIZADA
    assert entity.notes == model.notes


def test_update_model_writes_changes():
    model = SessionModel(
        id=str(uuid4()),
        user_id=str(uuid4()),
        patient_id=str(uuid4()),
        date_time=datetime.now(UTC),
        duration_minutes=60,
        price=Decimal("100"),
        status=SessionStatus.AGENDADA.value,
        notes="",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    entity = _make_session(status=SessionStatus.FALTOU)

    SessionMapper.update_model(model, entity)

    assert model.patient_id == str(entity.patient_id)
    assert model.duration_minutes == entity.duration_minutes
    assert model.status == entity.status.value
    assert model.notes == entity.notes
    assert model.updated_at == entity.updated_at
