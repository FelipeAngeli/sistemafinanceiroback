"""Router para endpoints de Dashboard."""

from datetime import date

from fastapi import APIRouter, Query

from app.interfaces.http.dependencies import DashboardSummaryUC
from app.interfaces.http.dependencies.auth import CurrentUser
from app.interfaces.http.schemas.dashboard_schemas import (
    DashboardSummaryResponse,
    FinancialEntrySummarySchema,
    FinancialReportSchema,
    PatientsSummarySchema,
    SessionSummarySchema,
)
from app.use_cases.dashboard.dashboard_summary import DashboardSummaryInput

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Resumo do Dashboard",
    description=(
        "Consolida múltiplas informações do dashboard em uma única resposta: "
        "relatório financeiro, sessões de hoje, sessões recentes e resumo de pacientes. "
        "Otimizado para performance com queries paralelas."
    ),
)
async def get_dashboard_summary(
    current_user: CurrentUser,
    use_case: DashboardSummaryUC,
    start_date: date = Query(
        ...,
        description="Data inicial do período financeiro (YYYY-MM-DD)",
        examples=["2024-01-01"],
    ),
    end_date: date = Query(
        ...,
        description="Data final do período financeiro (YYYY-MM-DD)",
        examples=["2024-01-31"],
    ),
) -> DashboardSummaryResponse:
    """Retorna resumo consolidado do dashboard do usuário autenticado.
    
    **Autenticação:**
    Requer token JWT válido. Retorna apenas dados do usuário autenticado.
    
    Validações:
    - Formato das datas (YYYY-MM-DD) - validado automaticamente pelo FastAPI
    - start_date <= end_date
    - Período não pode exceder 1 ano
    
    Otimizações:
    - Queries executadas em paralelo
    - Limite de 100 entradas financeiras
    - Limite de 100 sessões de hoje
    """
    input_data = DashboardSummaryInput(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
    )
    
    output = await use_case.execute(input_data)
    
    # Converter para schemas
    financial_report = FinancialReportSchema(
        total_revenue=output.financial_report.total_revenue,
        total_paid=output.financial_report.total_paid,
        total_pending=output.financial_report.total_pending,
        entries=[
            FinancialEntrySummarySchema(
                id=e.id,
                session_id=e.session_id,
                patient_id=e.patient_id,
                entry_date=e.entry_date,
                amount=e.amount,
                status=e.status,
                description=e.description,
            )
            for e in output.financial_report.entries
        ],
        period_start=output.financial_report.period_start,
        period_end=output.financial_report.period_end,
    )
    
    today_sessions = [
        SessionSummarySchema(
            id=s.id,
            patient_id=s.patient_id,
            date_time=s.date_time,
            price=s.price,
            duration_minutes=s.duration_minutes,
            status=s.status,
            notes=s.notes,
        )
        for s in output.today_sessions
    ]
    
    recent_sessions = [
        SessionSummarySchema(
            id=s.id,
            patient_id=s.patient_id,
            date_time=s.date_time,
            price=s.price,
            duration_minutes=s.duration_minutes,
            status=s.status,
            notes=s.notes,
        )
        for s in output.recent_sessions
    ]
    
    patients_summary = PatientsSummarySchema(
        total_patients=output.patients_summary.total_patients,
        active_patients=output.patients_summary.active_patients,
        inactive_patients=output.patients_summary.inactive_patients,
    )
    
    return DashboardSummaryResponse(
        financial_report=financial_report,
        today_sessions=today_sessions,
        recent_sessions=recent_sessions,
        patients_summary=patients_summary,
    )
