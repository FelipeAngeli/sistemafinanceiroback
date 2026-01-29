"""Use Case: Obter Resumo do Dashboard.

Agrega informações financeiras, de sessões e pacientes para o dashboard.
"""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.domain.repositories.dashboard_repository import DashboardRepository
from app.interfaces.http.schemas.dashboard_schemas import (
    DashboardFinancialStats,
    DashboardPatientStats,
    DashboardPeriod,
    DashboardSessionItem,
    DashboardSessionStats,
    DashboardSummaryResponse,
)


@dataclass(frozen=True)
class GetDashboardSummaryInput:
    """Input para o resumo do dashboard."""

    user_id: UUID
    start_date: date
    end_date: date


class GetDashboardSummaryUseCase:
    """Caso de uso para carregar resumo do dashboard."""

    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self._repository = dashboard_repository

    async def execute(
        self, input_data: GetDashboardSummaryInput
    ) -> DashboardSummaryResponse:
        """Executa a busca de dados agregados."""
        
        financial_dto = await self._repository.get_financial_stats(
            user_id=input_data.user_id,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
        )
        
        sessions_dto = await self._repository.get_session_stats(
            user_id=input_data.user_id,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
        )
        
        patients_dto = await self._repository.get_patient_stats(user_id=input_data.user_id)

        # Convert DTOs to Response Schemas
        financial = DashboardFinancialStats(
            total_received=financial_dto.total_received,
            total_pending=financial_dto.total_pending,
            total_entries=financial_dto.total_entries,
            pending_count=financial_dto.pending_count,
            entries=financial_dto.entries,
        )

        sessions = DashboardSessionStats(
            today=[
                DashboardSessionItem(
                    id=item.id,
                    patient_id=item.patient_id,
                    patient_name=item.patient_name,
                    date_time=item.date_time,
                    price=item.price,
                    status=item.status,
                ) for item in sessions_dto.today
            ],
            recent=[
                DashboardSessionItem(
                    id=item.id,
                    patient_id=item.patient_id,
                    patient_name=item.patient_name,
                    date_time=item.date_time,
                    price=item.price,
                    status=item.status,
                ) for item in sessions_dto.recent
            ],
            total_month=sessions_dto.total_month,
        )

        patients = DashboardPatientStats(
            total=patients_dto.total,
            active=patients_dto.active,
            inactive=patients_dto.inactive,
        )

        return DashboardSummaryResponse(
            financial=financial,
            sessions=sessions,
            patients=patients,
            period=DashboardPeriod(
                start=input_data.start_date,
                end=input_data.end_date,
            ),
        )
