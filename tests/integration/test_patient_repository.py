"""Testes para SqlAlchemyPatientRepository."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.patient import Patient
from app.infra.repositories.patient_repository_impl import SqlAlchemyPatientRepository


def _make_patient(name: str = "Maria Silva") -> Patient:
    return Patient(
        name=name,
        email="maria@example.com",
        phone="11999999999",
        observation="Observação",
    )


@pytest.mark.asyncio
async def test_create_and_get_patient(patient_repository: SqlAlchemyPatientRepository):
    patient = _make_patient()

    created = await patient_repository.create(patient)
    assert created.id == patient.id

    fetched = await patient_repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == patient.name


@pytest.mark.asyncio
async def test_list_all_filters_active(patient_repository: SqlAlchemyPatientRepository):
    patient_active = _make_patient("Paciente Ativo")
    patient_inactive = _make_patient("Paciente Inativo")
    patient_inactive.deactivate()

    await patient_repository.create(patient_active)
    await patient_repository.create(patient_inactive)

    active_only = await patient_repository.list_all()
    assert all(p.active for p in active_only)
    assert any(p.id == patient_active.id for p in active_only)

    all_patients = await patient_repository.list_all(active_only=False)
    assert len(all_patients) >= 2
    assert any(p.id == patient_inactive.id for p in all_patients)


@pytest.mark.asyncio
async def test_update_patient(patient_repository: SqlAlchemyPatientRepository):
    patient = _make_patient("Paciente Original")
    await patient_repository.create(patient)

    patient.update(name="Paciente Atualizado", phone="000")
    updated = await patient_repository.update(patient)

    assert updated.name == "Paciente Atualizado"
    assert updated.phone == "000"


@pytest.mark.asyncio
async def test_delete_patient(patient_repository: SqlAlchemyPatientRepository):
    patient = _make_patient("Paciente Removido")
    await patient_repository.create(patient)

    deleted = await patient_repository.delete(patient.id)
    assert deleted is True

    missing = await patient_repository.get_by_id(patient.id)
    assert missing is None


@pytest.mark.asyncio
async def test_get_stats(patient_repository: SqlAlchemyPatientRepository, db_session: AsyncSession):
    # Limpa tabela para previsibilidade
    await db_session.execute(text("DELETE FROM patients"))
    await db_session.commit()

    active_patient = _make_patient("Ativo")
    inactive_patient = _make_patient("Inativo")
    inactive_patient.deactivate()

    await patient_repository.create(active_patient)
    await patient_repository.create(inactive_patient)

    stats = await patient_repository.get_stats()
    assert stats.total == 2
    assert stats.active == 1
    assert stats.inactive == 1
