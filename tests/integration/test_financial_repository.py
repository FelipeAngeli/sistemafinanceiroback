"""Testes para SqlAlchemyFinancialEntryRepository."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.domain.entities.session import Session
from app.domain.entities.patient import Patient
from app.infra.repositories.financial_repository_impl import SqlAlchemyFinancialEntryRepository
from app.infra.repositories.patient_repository_impl import SqlAlchemyPatientRepository
from app.infra.repositories.session_repository_impl import SqlAlchemySessionRepository


def _make_patient(name: str = "Paciente Financeiro", user_id=None) -> Patient:
    if user_id is None:
        user_id = uuid4()
    return Patient(user_id=user_id, name=name, email="fin@example.com")


def _make_session(patient_id, user_id=None):
    if user_id is None:
        user_id = uuid4()
    return Session(
        user_id=user_id,
        patient_id=patient_id,
        date_time=datetime.now(UTC),
        price=Decimal("200.00"),
    )


def _make_entry(patient_id, session_id, user_id=None, **overrides) -> FinancialEntry:
    if user_id is None:
        user_id = uuid4()
    base = {
        "session_id": session_id,
        "patient_id": patient_id,
        "user_id": user_id,
        "amount": Decimal("200.00"),
        "entry_date": date.today(),
        "description": "Sessão",
    }
    base.update(overrides)
    return FinancialEntry(**base)


@pytest.mark.asyncio
async def test_create_get_and_update_entry(
    financial_repository: SqlAlchemyFinancialEntryRepository,
    patient_repository: SqlAlchemyPatientRepository,
    session_repository: SqlAlchemySessionRepository,
    sample_user_id,
):
    patient = await patient_repository.create(_make_patient(user_id=sample_user_id))
    session = await session_repository.create(_make_session(patient.id, user_id=sample_user_id))
    entry = _make_entry(patient.id, session.id, user_id=sample_user_id)

    created = await financial_repository.create(entry)
    fetched = await financial_repository.get_by_id(user_id=sample_user_id, entry_id=created.id)
    assert fetched is not None
    assert fetched.session_id == session.id

    fetched.mark_as_paid()
    updated = await financial_repository.update(fetched)
    assert updated.status == EntryStatus.PAGO
    assert updated.paid_at is not None


@pytest.mark.asyncio
async def test_list_pending(financial_repository, patient_repository, session_repository, db_session: AsyncSession, sample_user_id):
    await db_session.execute(text("DELETE FROM financial_entries"))
    await db_session.commit()

    patient = await patient_repository.create(_make_patient("Pendentes", user_id=sample_user_id))
    session = await session_repository.create(_make_session(patient.id, user_id=sample_user_id))
    entry1 = await financial_repository.create(_make_entry(patient.id, session.id, user_id=sample_user_id))
    entry2 = await financial_repository.create(
        _make_entry(patient.id, session.id, user_id=sample_user_id, amount=Decimal("150.00"))
    )

    pending = await financial_repository.list_pending(user_id=sample_user_id)
    assert len(pending) == 2
    ids = {e.id for e in pending}
    assert entry1.id in ids and entry2.id in ids


@pytest.mark.asyncio
async def test_list_by_period_with_filter(
    financial_repository,
    patient_repository,
    session_repository,
    db_session: AsyncSession,
    sample_user_id,
):
    await db_session.execute(text("DELETE FROM financial_entries"))
    await db_session.commit()

    patient = await patient_repository.create(_make_patient("Período", user_id=sample_user_id))
    session = await session_repository.create(_make_session(patient.id, user_id=sample_user_id))

    # Entry pago em 1º
    entry_paid = _make_entry(
        patient.id,
        session.id,
        user_id=sample_user_id,
        entry_date=date(2024, 12, 1),
    )
    entry_paid.mark_as_paid()
    await financial_repository.create(entry_paid)

    # Entry pendente em 5º
    await financial_repository.create(
        _make_entry(
            patient.id,
            session.id,
            user_id=sample_user_id,
            entry_date=date(2024, 12, 5),
        )
    )

    results = await financial_repository.list_by_period(
        user_id=sample_user_id,
        start_date=date(2024, 12, 1),
        end_date=date(2024, 12, 31),
        status_filter=[EntryStatus.PAGO],
    )
    assert len(results) == 1
    assert results[0].status == EntryStatus.PAGO
