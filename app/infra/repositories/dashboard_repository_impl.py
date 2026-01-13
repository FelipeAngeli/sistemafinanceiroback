"""Implementação SQLAlchemy do repositório de dashboard."""

from datetime import date, datetime, time

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.domain.entities.financial_entry import EntryStatus
from app.domain.entities.session import SessionStatus
from app.domain.repositories.dashboard_repository import DashboardRepository
from app.domain.dtos.dashboard_dtos import (
    DashboardFinancialStatsDTO,
    DashboardPatientStatsDTO,
    DashboardSessionItemDTO,
    DashboardSessionStatsDTO,
)
from app.infra.db.models.financial_entry_model import FinancialEntryModel
from app.infra.db.models.patient_model import PatientModel
from app.infra.db.models.session_model import SessionModel


class SqlAlchemyDashboardRepository(DashboardRepository):
    """Implementação SQLAlchemy do repositório de dashboard."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_financial_stats(
        self, start_date: date, end_date: date
    ) -> DashboardFinancialStatsDTO:
        """Busca estatísticas financeiras no período."""
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # Query agregada para somas e contagens
        stmt = select(
            func.sum(
                case(
                    (FinancialEntryModel.status == EntryStatus.PAGO.value, FinancialEntryModel.amount),
                    else_=0,
                )
            ).label("total_received"),
            func.sum(
                case(
                    (FinancialEntryModel.status == EntryStatus.PENDENTE.value, FinancialEntryModel.amount),
                    else_=0,
                )
            ).label("total_pending"),
            func.count(FinancialEntryModel.id).label("total_entries"),
            func.sum(
                case((FinancialEntryModel.status == EntryStatus.PENDENTE.value, 1), else_=0)
            ).label("pending_count"),
        ).where(
            and_(
                FinancialEntryModel.entry_date >= start_date,
                FinancialEntryModel.entry_date <= end_date,
            )
        )

        result = await self._session.execute(stmt)
        row = result.one()

        return DashboardFinancialStatsDTO(
            total_received=row.total_received or 0,
            total_pending=row.total_pending or 0,
            total_entries=row.total_entries or 0,
            pending_count=row.pending_count or 0,
            entries=[],
        )

    async def get_session_stats(
        self, start_date: date, end_date: date
    ) -> DashboardSessionStatsDTO:
        """Busca estatísticas de sessões."""
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        
        # 1. Today's sessions (scheduled)
        today = date.today()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        
        stmt_today = (
            select(SessionModel)
            .options(joinedload(SessionModel.patient))
            .where(
                and_(
                    SessionModel.date_time >= today_start,
                    SessionModel.date_time <= today_end,
                    SessionModel.status == SessionStatus.AGENDADA.value,
                )
            )
            .order_by(SessionModel.date_time.asc())
        )
        result_today = await self._session.execute(stmt_today)
        sessions_today = result_today.scalars().all()

        # 2. Recent sessions (last 10)
        stmt_recent = (
            select(SessionModel)
            .options(joinedload(SessionModel.patient))
            .order_by(SessionModel.date_time.desc())
            .limit(10)
        )
        result_recent = await self._session.execute(stmt_recent)
        sessions_recent = result_recent.scalars().all()

        # 3. Total in period
        stmt_total = select(func.count(SessionModel.id)).where(
            and_(
                SessionModel.date_time >= start_datetime,
                SessionModel.date_time <= end_datetime,
            )
        )
        result_total = await self._session.execute(stmt_total)
        total_period = result_total.scalar_one()

        # Helper para converter Model -> DashboardSessionItemDTO
        def to_item(model: SessionModel) -> DashboardSessionItemDTO:
            return DashboardSessionItemDTO(
                id=model.id,
                patient_id=model.patient_id,
                patient_name=model.patient.name if model.patient else "Desconhecido",
                date_time=model.date_time,
                price=model.price,
                status=model.status,
            )

        return DashboardSessionStatsDTO(
            today=[to_item(s) for s in sessions_today],
            recent=[to_item(s) for s in sessions_recent],
            total_month=total_period,
        )

    async def get_patient_stats(self) -> DashboardPatientStatsDTO:
        """Busca estatísticas de pacientes."""
        stmt = select(
            func.count(PatientModel.id).label("total"),
            func.sum(case((PatientModel.active == True, 1), else_=0)).label("active"),
            func.sum(case((PatientModel.active == False, 1), else_=0)).label("inactive"),
        )
        
        result = await self._session.execute(stmt)
        row = result.one()

        return DashboardPatientStatsDTO(
            total=row.total or 0,
            active=row.active or 0,
            inactive=row.inactive or 0,
        )
