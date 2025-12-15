"""Implementação SQLAlchemy do repositório de lançamentos financeiros."""

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.infra.db.mappers.financial_entry_mapper import FinancialEntryMapper
from app.infra.db.models.financial_entry_model import FinancialEntryModel


class SqlAlchemyFinancialEntryRepository(FinancialEntryRepository):
    """Implementação SQLAlchemy do repositório de lançamentos financeiros."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entry: FinancialEntry) -> FinancialEntry:
        """Persiste um novo lançamento financeiro."""
        model = FinancialEntryMapper.to_model(entry)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return FinancialEntryMapper.to_entity(model)

    async def get_by_id(self, entry_id: UUID) -> Optional[FinancialEntry]:
        """Busca lançamento por ID."""
        stmt = select(FinancialEntryModel).where(
            FinancialEntryModel.id == str(entry_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return FinancialEntryMapper.to_entity(model) if model else None

    async def list_by_period(
        self,
        start_date: date,
        end_date: date,
        status_filter: Optional[List[EntryStatus]] = None,
    ) -> List[FinancialEntry]:
        """Lista lançamentos em um período."""
        stmt = select(FinancialEntryModel).where(
            and_(
                FinancialEntryModel.entry_date >= start_date,
                FinancialEntryModel.entry_date <= end_date,
            )
        )
        if status_filter:
            status_values = [s.value for s in status_filter]
            stmt = stmt.where(FinancialEntryModel.status.in_(status_values))
        stmt = stmt.order_by(FinancialEntryModel.entry_date.desc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [FinancialEntryMapper.to_entity(m) for m in models]

    async def list_pending(self) -> List[FinancialEntry]:
        """Lista todos os lançamentos pendentes."""
        stmt = (
            select(FinancialEntryModel)
            .where(FinancialEntryModel.status == EntryStatus.PENDENTE.value)
            .order_by(FinancialEntryModel.entry_date.asc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [FinancialEntryMapper.to_entity(m) for m in models]

    async def update(self, entry: FinancialEntry) -> FinancialEntry:
        """Atualiza um lançamento existente."""
        stmt = select(FinancialEntryModel).where(
            FinancialEntryModel.id == str(entry.id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"FinancialEntry {entry.id} not found")
        FinancialEntryMapper.update_model(model, entry)
        await self._session.commit()
        await self._session.refresh(model)
        return FinancialEntryMapper.to_entity(model)
