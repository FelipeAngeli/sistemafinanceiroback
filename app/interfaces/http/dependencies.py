"""Dependency Injection para FastAPI.

Configura e fornece instâncias de repositórios e casos de uso.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.database import get_database_manager
from app.infra.repositories.patient_repository_impl import SqlAlchemyPatientRepository
from app.infra.repositories.session_repository_impl import SqlAlchemySessionRepository
from app.infra.repositories.financial_repository_impl import SqlAlchemyFinancialEntryRepository
from app.infra.repositories.dashboard_repository_impl import SqlAlchemyDashboardRepository

from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.domain.repositories.dashboard_repository import DashboardRepository
from app.use_cases.patient.create_patient import CreatePatientUseCase
from app.use_cases.patient.list_patients import ListPatientsUseCase
from app.use_cases.patient.get_patient_summary import GetPatientSummaryUseCase
from app.use_cases.session.schedule_session import CreateSessionUseCase
from app.use_cases.session.list_sessions import ListSessionsUseCase
from app.use_cases.session.get_session_by_id import GetSessionByIdUseCase
from app.use_cases.session.update_session import UpdateSessionUseCase
from app.use_cases.session.update_session_status import UpdateSessionStatusUseCase
from app.use_cases.financial.financial_report import FinancialReportUseCase
from app.use_cases.dashboard.get_dashboard_summary import GetDashboardSummaryUseCase
from app.use_cases.dashboard.dashboard_summary import DashboardSummaryUseCase


# ============================================================
# Database Session
# ============================================================

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornece sessão do banco de dados."""
    db = get_database_manager()
    async with db.session() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db_session)]


# ============================================================
# Repositories
# ============================================================

async def get_patient_repository(session: DbSession) -> PatientRepository:
    """Fornece repositório de pacientes."""
    return SqlAlchemyPatientRepository(session)


async def get_session_repository(session: DbSession) -> SessionRepository:
    """Fornece repositório de sessões."""
    return SqlAlchemySessionRepository(session)


async def get_financial_repository(session: DbSession) -> FinancialEntryRepository:
    """Fornece repositório de lançamentos financeiros."""
    return SqlAlchemyFinancialEntryRepository(session)


async def get_dashboard_repository(session: DbSession) -> DashboardRepository:
    """Fornece repositório de dashboard."""
    return SqlAlchemyDashboardRepository(session)


PatientRepo = Annotated[PatientRepository, Depends(get_patient_repository)]
SessionRepo = Annotated[SessionRepository, Depends(get_session_repository)]
FinancialRepo = Annotated[FinancialEntryRepository, Depends(get_financial_repository)]
DashboardRepo = Annotated[DashboardRepository, Depends(get_dashboard_repository)]


# ============================================================
# Use Cases
# ============================================================

async def get_create_patient_use_case(repo: PatientRepo) -> CreatePatientUseCase:
    """Fornece caso de uso de criação de paciente."""
    return CreatePatientUseCase(patient_repository=repo)


async def get_list_patients_use_case(repo: PatientRepo) -> ListPatientsUseCase:
    """Fornece caso de uso de listagem de pacientes."""
    return ListPatientsUseCase(patient_repository=repo)


async def get_patient_summary_use_case(repo: PatientRepo) -> GetPatientSummaryUseCase:
    """Fornece caso de uso de resumo de pacientes."""
    return GetPatientSummaryUseCase(patient_repository=repo)


async def get_create_session_use_case(
    session_repo: SessionRepo,
    patient_repo: PatientRepo,
) -> CreateSessionUseCase:
    """Fornece caso de uso de criação de sessão."""
    return CreateSessionUseCase(
        session_repository=session_repo,
        patient_repository=patient_repo,
    )


async def get_list_sessions_use_case(
    session_repo: SessionRepo,
) -> ListSessionsUseCase:
    """Fornece caso de uso de listagem de sessões."""
    return ListSessionsUseCase(session_repository=session_repo)


async def get_session_by_id_use_case(
    session_repo: SessionRepo,
) -> GetSessionByIdUseCase:
    """Fornece caso de uso de busca de sessão por ID."""
    return GetSessionByIdUseCase(session_repository=session_repo)


async def get_update_session_use_case(
    session_repo: SessionRepo,
    patient_repo: PatientRepo,
) -> UpdateSessionUseCase:
    """Fornece caso de uso de atualização de sessão."""
    return UpdateSessionUseCase(
        session_repository=session_repo,
        patient_repository=patient_repo,
    )


async def get_update_session_status_use_case(
    session_repo: SessionRepo,
    financial_repo: FinancialRepo,
) -> UpdateSessionStatusUseCase:
    """Fornece caso de uso de atualização de status."""
    return UpdateSessionStatusUseCase(
        session_repository=session_repo,
        financial_repository=financial_repo,
    )


async def get_financial_report_use_case(
    repo: FinancialRepo,
) -> FinancialReportUseCase:
    """Fornece caso de uso de relatório financeiro."""
    return FinancialReportUseCase(financial_repository=repo)


async def get_dashboard_summary_use_case_legacy(
    repo: DashboardRepo,
) -> GetDashboardSummaryUseCase:
    """Fornece caso de uso de resumo do dashboard (implementação legacy com repositório)."""
    return GetDashboardSummaryUseCase(dashboard_repository=repo)


async def get_dashboard_summary_use_case(
    financial_repo: FinancialRepo,
    session_repo: SessionRepo,
    patient_repo: PatientRepo,
) -> DashboardSummaryUseCase:
    """Fornece caso de uso de resumo do dashboard (nova implementação com queries paralelas)."""
    return DashboardSummaryUseCase(
        financial_repository=financial_repo,
        session_repository=session_repo,
        patient_repository=patient_repo,
    )


# Type aliases para injeção nos endpoints
CreatePatientUC = Annotated[CreatePatientUseCase, Depends(get_create_patient_use_case)]
ListPatientsUC = Annotated[ListPatientsUseCase, Depends(get_list_patients_use_case)]
GetPatientSummaryUC = Annotated[GetPatientSummaryUseCase, Depends(get_patient_summary_use_case)]
CreateSessionUC = Annotated[CreateSessionUseCase, Depends(get_create_session_use_case)]
ListSessionsUC = Annotated[ListSessionsUseCase, Depends(get_list_sessions_use_case)]
GetSessionByIdUC = Annotated[GetSessionByIdUseCase, Depends(get_session_by_id_use_case)]
UpdateSessionUC = Annotated[UpdateSessionUseCase, Depends(get_update_session_use_case)]
UpdateSessionStatusUC = Annotated[UpdateSessionStatusUseCase, Depends(get_update_session_status_use_case)]
FinancialReportUC = Annotated[FinancialReportUseCase, Depends(get_financial_report_use_case)]
GetDashboardSummaryUC = Annotated[GetDashboardSummaryUseCase, Depends(get_dashboard_summary_use_case_legacy)]
DashboardSummaryUC = Annotated[DashboardSummaryUseCase, Depends(get_dashboard_summary_use_case)]
