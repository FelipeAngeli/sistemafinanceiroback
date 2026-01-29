"""Testes de integração para SqlAlchemySessionRepository."""

from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.entities.patient import Patient
from app.domain.entities.session import Session, SessionStatus
from app.infra.repositories.patient_repository_impl import SqlAlchemyPatientRepository
from app.infra.repositories.session_repository_impl import SqlAlchemySessionRepository


def _make_patient(name: str = "Paciente Sessão", user_id=None) -> Patient:
    if user_id is None:
        user_id = uuid4()
    return Patient(
        user_id=user_id,
        name=name,
        email="paciente@example.com",
        phone="11988887777",
    )


def _make_session(patient_id, user_id=None, **overrides) -> Session:
    if user_id is None:
        user_id = uuid4()
    defaults = {
        "user_id": user_id,
        "patient_id": patient_id,
        "date_time": datetime.utcnow(),
        "price": Decimal("150.00"),
        "duration_minutes": 50,
        "notes": "Sessão padrão",
    }
    defaults.update(overrides)
    return Session(**defaults)


@pytest.mark.asyncio
async def test_create_and_get_session(
    session_repository: SqlAlchemySessionRepository,
    patient_repository: SqlAlchemyPatientRepository,
    sample_user_id,
):
    patient = await patient_repository.create(_make_patient(user_id=sample_user_id))
    session = _make_session(patient.id, user_id=sample_user_id)

    created = await session_repository.create(session)
    fetched = await session_repository.get_by_id(user_id=sample_user_id, session_id=created.id)

    assert fetched is not None
    assert fetched.patient_id == patient.id
    assert fetched.status == SessionStatus.AGENDADA


@pytest.mark.asyncio
async def test_list_by_patient_and_recent(
    session_repository: SqlAlchemySessionRepository,
    patient_repository: SqlAlchemyPatientRepository,
    sample_user_id,
):
    patient = await patient_repository.create(_make_patient("Paciente Listagem", user_id=sample_user_id))

    for days in range(3):
        session = _make_session(
            patient.id,
            user_id=sample_user_id,
            date_time=datetime.utcnow() - timedelta(days=days),
        )
        await session_repository.create(session)

    sessions_by_patient = await session_repository.list_by_patient(user_id=sample_user_id, patient_id=patient.id)
    assert len(sessions_by_patient) == 3
    assert sessions_by_patient[0].date_time >= sessions_by_patient[-1].date_time

    recent = await session_repository.list_recent(user_id=sample_user_id, limit=2)
    assert len(recent) == 2


@pytest.mark.asyncio
async def test_update_session(
    session_repository: SqlAlchemySessionRepository,
    patient_repository: SqlAlchemyPatientRepository,
    sample_user_id,
):
    patient = await patient_repository.create(_make_patient("Paciente Update", user_id=sample_user_id))
    session = await session_repository.create(_make_session(patient.id, user_id=sample_user_id))

    session.notes = "Atualizado"
    session.mark_as_realized()
    updated = await session_repository.update(session)

    assert updated.status == SessionStatus.REALIZADA
    assert updated.notes == "Atualizado"


@pytest.mark.asyncio
async def test_list_all_with_filters(
    session_repository: SqlAlchemySessionRepository,
    patient_repository: SqlAlchemyPatientRepository,
    sample_user_id,
):
    patient = await patient_repository.create(_make_patient("Paciente Filtros", user_id=sample_user_id))
    other_patient = await patient_repository.create(_make_patient("Outro Paciente", user_id=sample_user_id))

    session1 = await session_repository.create(
        _make_session(
            patient.id,
            user_id=sample_user_id,
            date_time=datetime(2024, 12, 10, 14, 0),
            status=SessionStatus.AGENDADA,
        )
    )
    session2 = await session_repository.create(
        _make_session(
            patient.id,
            user_id=sample_user_id,
            date_time=datetime(2024, 12, 12, 10, 0),
            status=SessionStatus.CANCELADA,
        )
    )
    await session_repository.create(
        _make_session(other_patient.id, user_id=sample_user_id, date_time=datetime(2024, 12, 11, 9, 0))
    )

    filtered = await session_repository.list_all(
        user_id=sample_user_id,
        patient_id=patient.id,
        status=SessionStatus.CANCELADA.value,
        start_date=date(2024, 12, 11),
        end_date=date(2024, 12, 31),
    )

    assert len(filtered) == 1
    assert filtered[0].id == session2.id
    assert filtered[0].status == SessionStatus.CANCELADA
    assert filtered[0].patient_id == patient.id
