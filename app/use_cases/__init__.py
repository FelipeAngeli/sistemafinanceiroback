"""Use Cases (Application Layer) - orquestração de regras de negócio.

Os casos de uso contêm a lógica de aplicação e orquestram
as entidades de domínio e repositórios.
"""

from app.use_cases.patient.create_patient import (
    CreatePatientInput,
    CreatePatientOutput,
    CreatePatientUseCase,
)
from app.use_cases.patient.list_patients import (
    ListPatientsInput,
    ListPatientsOutput,
    ListPatientsUseCase,
    PatientSummary,
)
from app.use_cases.session.schedule_session import (
    CreateSessionInput,
    CreateSessionOutput,
    CreateSessionUseCase,
)
from app.use_cases.session.update_session_status import (
    UpdateSessionStatusInput,
    UpdateSessionStatusOutput,
    UpdateSessionStatusUseCase,
)
from app.use_cases.financial.financial_report import (
    FinancialReportInput,
    FinancialReportOutput,
    FinancialReportUseCase,
    FinancialEntrySummary,
)

__all__ = [
    # Patient
    "CreatePatientUseCase",
    "CreatePatientInput",
    "CreatePatientOutput",
    "ListPatientsUseCase",
    "ListPatientsInput",
    "ListPatientsOutput",
    "PatientSummary",
    # Session
    "CreateSessionUseCase",
    "CreateSessionInput",
    "CreateSessionOutput",
    "UpdateSessionStatusUseCase",
    "UpdateSessionStatusInput",
    "UpdateSessionStatusOutput",
    # Financial
    "FinancialReportUseCase",
    "FinancialReportInput",
    "FinancialReportOutput",
    "FinancialEntrySummary",
]
