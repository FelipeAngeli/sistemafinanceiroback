"""Interface do repositório de dashboard."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.domain.dtos.dashboard_dtos import (
    DashboardFinancialStatsDTO,
    DashboardPatientStatsDTO,
    DashboardSessionStatsDTO,
)


class DashboardRepository(ABC):
    """Interface para busca de dados agregados do dashboard."""

    @abstractmethod
    async def get_financial_stats(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> DashboardFinancialStatsDTO:
        """Busca estatísticas financeiras do usuário no período."""
        ...

    @abstractmethod
    async def get_session_stats(
        self, user_id: UUID, start_date: date, end_date: date
    ) -> DashboardSessionStatsDTO:
        """Busca estatísticas de sessões do usuário (hoje, recentes, total no período)."""
        ...

    @abstractmethod
    async def get_patient_stats(self, user_id: UUID) -> DashboardPatientStatsDTO:
        """Busca estatísticas gerais de pacientes do usuário."""
        ...
