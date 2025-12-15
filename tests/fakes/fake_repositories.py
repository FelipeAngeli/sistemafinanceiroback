"""Repositórios fake (in-memory) para testes unitários.

Implementam as interfaces de repositório sem dependência de banco de dados.
Úteis para testar casos de uso isoladamente.
"""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.domain.entities.financial_entry import EntryStatus, FinancialEntry
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.financial_repository import FinancialEntryRepository


class FakePatientRepository(PatientRepository):
    """Repositório fake de pacientes (in-memory)."""

    def __init__(self) -> None:
        self._patients: Dict[UUID, Patient] = {}

    async def create(self, patient: Patient) -> Patient:
        self._patients[patient.id] = patient
        return patient

    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        return self._patients.get(patient_id)

    async def list_all(self, active_only: bool = True) -> List[Patient]:
        patients = list(self._patients.values())
        if active_only:
            patients = [p for p in patients if p.active]
        return patients

    async def update(self, patient: Patient) -> Patient:
        self._patients[patient.id] = patient
        return patient

    async def delete(self, patient_id: UUID) -> bool:
        if patient_id in self._patients:
            del self._patients[patient_id]
            return True
        return False


class FakeSessionRepository(SessionRepository):
    """Repositório fake de sessões (in-memory)."""

    def __init__(self) -> None:
        self._sessions: Dict[UUID, Session] = {}

    async def create(self, session: Session) -> Session:
        self._sessions[session.id] = session
        return session

    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        return self._sessions.get(session_id)

    async def list_by_patient(self, patient_id: UUID) -> List[Session]:
        return [s for s in self._sessions.values() if s.patient_id == patient_id]

    async def list_recent(self, limit: int = 10) -> List[Session]:
        sessions = sorted(
            self._sessions.values(),
            key=lambda s: s.date_time,
            reverse=True,
        )
        return sessions[:limit]

    async def update(self, session: Session) -> Session:
        self._sessions[session.id] = session
        return session


class FakeFinancialEntryRepository(FinancialEntryRepository):
    """Repositório fake de lançamentos financeiros (in-memory)."""

    def __init__(self) -> None:
        self._entries: Dict[UUID, FinancialEntry] = {}

    async def create(self, entry: FinancialEntry) -> FinancialEntry:
        self._entries[entry.id] = entry
        return entry

    async def get_by_id(self, entry_id: UUID) -> Optional[FinancialEntry]:
        return self._entries.get(entry_id)

    async def list_by_period(
        self,
        start_date: date,
        end_date: date,
        status_filter: Optional[List[EntryStatus]] = None,
    ) -> List[FinancialEntry]:
        entries = [
            e for e in self._entries.values()
            if start_date <= e.entry_date <= end_date
        ]
        if status_filter:
            entries = [e for e in entries if e.status in status_filter]
        return sorted(entries, key=lambda e: e.entry_date, reverse=True)

    async def list_pending(self) -> List[FinancialEntry]:
        return [
            e for e in self._entries.values()
            if e.status == EntryStatus.PENDENTE
        ]

    async def update(self, entry: FinancialEntry) -> FinancialEntry:
        self._entries[entry.id] = entry
        return entry
