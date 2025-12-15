"""
Implementação SQLAlchemy do repositório de pacientes.

Esta implementação pode usar SQL, DynamoDB, ou qualquer persistência.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.patient import Patient
from app.domain.repositories.patient_repository import PatientRepository
from app.infra.db.mappers.patient_mapper import PatientMapper
from app.infra.db.models.patient_model import PatientModel


class SqlAlchemyPatientRepository(PatientRepository):
    """Implementação SQLAlchemy do repositório de pacientes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, patient: Patient) -> Patient:
        """Persiste um novo paciente."""
        model = PatientMapper.to_model(patient)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return PatientMapper.to_entity(model)

    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """Busca paciente por ID."""
        stmt = select(PatientModel).where(PatientModel.id == str(patient_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PatientMapper.to_entity(model) if model else None

    async def list_all(self, active_only: bool = True) -> List[Patient]:
        """Lista todos os pacientes."""
        stmt = select(PatientModel).order_by(PatientModel.name)
        if active_only:
            stmt = stmt.where(PatientModel.active == True)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [PatientMapper.to_entity(m) for m in models]

    async def update(self, patient: Patient) -> Patient:
        """Atualiza um paciente existente."""
        stmt = select(PatientModel).where(PatientModel.id == str(patient.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Patient {patient.id} not found")
        PatientMapper.update_model(model, patient)
        await self._session.commit()
        await self._session.refresh(model)
        return PatientMapper.to_entity(model)

    async def delete(self, patient_id: UUID) -> bool:
        """Remove um paciente (hard delete)."""
        stmt = select(PatientModel).where(PatientModel.id == str(patient_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
