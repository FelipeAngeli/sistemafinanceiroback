"""Implementação SQLAlchemy do repositório de sessões."""

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.session import Session
from app.domain.repositories.session_repository import SessionRepository
from app.infra.db.mappers.session_mapper import SessionMapper
from app.infra.db.models.session_model import SessionModel


class SqlAlchemySessionRepository(SessionRepository):
    """Implementação SQLAlchemy do repositório de sessões."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, session: Session) -> Session:
        """Persiste uma nova sessão."""
        model = SessionMapper.to_model(session)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return SessionMapper.to_entity(model)

    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Busca sessão por ID."""
        stmt = select(SessionModel).where(SessionModel.id == str(session_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return SessionMapper.to_entity(model) if model else None

    async def list_by_patient(self, patient_id: UUID) -> List[Session]:
        """Lista todas as sessões de um paciente."""
        stmt = (
            select(SessionModel)
            .where(SessionModel.patient_id == str(patient_id))
            .order_by(SessionModel.date_time.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [SessionMapper.to_entity(m) for m in models]

    async def list_recent(self, limit: int = 10) -> List[Session]:
        """Lista as sessões mais recentes."""
        stmt = (
            select(SessionModel)
            .order_by(SessionModel.date_time.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [SessionMapper.to_entity(m) for m in models]

    async def update(self, session: Session) -> Session:
        """Atualiza uma sessão existente."""
        stmt = select(SessionModel).where(SessionModel.id == str(session.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Session {session.id} not found")
        SessionMapper.update_model(model, session)
        await self._session.commit()
        await self._session.refresh(model)
        return SessionMapper.to_entity(model)

    async def list_all(
        self,
        patient_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[Session]:
        """Lista sessões com filtros opcionais."""
        stmt = select(SessionModel)

        if patient_id:
            stmt = stmt.where(SessionModel.patient_id == str(patient_id))

        if status:
            stmt = stmt.where(SessionModel.status == status)

        if start_date:
            start_datetime = datetime.combine(start_date, time.min)
            stmt = stmt.where(SessionModel.date_time >= start_datetime)

        if end_date:
            end_datetime = datetime.combine(end_date, time.max)
            stmt = stmt.where(SessionModel.date_time <= end_datetime)

        stmt = stmt.order_by(SessionModel.date_time.desc()).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [SessionMapper.to_entity(m) for m in models]
