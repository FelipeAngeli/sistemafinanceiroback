"""Interfaces de repositórios (ports).

Estas interfaces definem os contratos que a camada de infraestrutura
deve implementar. Seguem o padrão Repository do DDD.
"""

from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository

__all__ = [
    "PatientRepository",
    "SessionRepository",
    "FinancialEntryRepository",
]
