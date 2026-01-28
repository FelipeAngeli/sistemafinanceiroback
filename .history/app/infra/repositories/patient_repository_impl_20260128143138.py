"""
Implementação SQLAlchemy do repositório de pacientes.

Esta implementação pode usar SQL, DynamoDB, ou qualquer persistência.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.patient import Patient, PatientStats
from app.domain.repositories.patient_repository import PatientRepository
from app.infra.db.mappers.patient_mapper import PatientMapper
from app.infra.db.models.patient_model import PatientModel


class SqlAlchemyPatientRepository(PatientRepository):
    """Implementação SQLAlchemy do repositório de pacientes."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_stats(self) -> PatientStats:
        """Retorna estatísticas gerais dos pacientes."""
        stmt = select(
            func.count(PatientModel.id).label("total"),
            func.sum(case((PatientModel.active == True, 1), else_=0)).label("active"),
            func.sum(case((PatientModel.active == False, 1), else_=0)).label("inactive"),
        )
        
        result = await self._session.execute(stmt)
        row = result.one()
        
        return PatientStats(
            total=row.total or 0,
            active=row.active or 0,
            inactive=row.inactive or 0,
        )

    async def create(self, patient: Patient) -> Patient:
        """Persiste um novo paciente."""
        try:
            model = PatientMapper.to_model(patient)
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)
            return PatientMapper.to_entity(model)
        except Exception as e:
            await self._session.rollback()
            raise

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
        from app.core.exceptions import EntityNotFoundError
        
        stmt = select(PatientModel).where(PatientModel.id == str(patient.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise EntityNotFoundError("Paciente", str(patient.id))
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
