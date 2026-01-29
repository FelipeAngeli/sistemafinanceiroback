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
from app.domain.entities.user import User
from app.domain.entities.patient import PatientStats
from app.domain.repositories.patient_repository import PatientRepository
from app.domain.repositories.session_repository import SessionRepository
from app.domain.repositories.financial_repository import FinancialEntryRepository
from app.domain.repositories.user_repository import UserRepository


class FakeUserRepository(UserRepository):
    """Repositório fake de usuários (in-memory)."""

    def __init__(self) -> None:
        self._users: Dict[UUID, User] = {}
        self._users_by_email: Dict[str, User] = {}

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        self._users_by_email[user.email] = user
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        return self._users_by_email.get(email.lower())

    async def update(self, user: User) -> User:
        old_user = self._users.get(user.id)
        if old_user:
            del self._users_by_email[old_user.email]
        self._users[user.id] = user
        self._users_by_email[user.email] = user
        return user


class FakePatientRepository(PatientRepository):
    """Repositório fake de pacientes (in-memory)."""

    def __init__(self) -> None:
        self._patients: Dict[UUID, Patient] = {}

    async def create(self, patient: Patient) -> Patient:
        self._patients[patient.id] = patient
        return patient

    async def get_by_id(self, user_id: UUID, patient_id: UUID) -> Optional[Patient]:
        patient = self._patients.get(patient_id)
        if patient and patient.user_id == user_id:
            return patient
        return None

    async def get_stats(self, user_id: UUID) -> PatientStats:
        patients = [p for p in self._patients.values() if p.user_id == user_id]
        total = len(patients)
        active = sum(1 for p in patients if p.active)
        inactive = total - active
        return PatientStats(total=total, active=active, inactive=inactive)

    async def list_all(self, user_id: UUID, active_only: bool = True) -> List[Patient]:
        patients = [p for p in self._patients.values() if p.user_id == user_id]
        if active_only:
            patients = [p for p in patients if p.active]
        return patients

    async def update(self, patient: Patient) -> Patient:
        self._patients[patient.id] = patient
        return patient

    async def delete(self, user_id: UUID, patient_id: UUID) -> bool:
        patient = self._patients.get(patient_id)
        if patient and patient.user_id == user_id:
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

    async def get_by_id(self, user_id: UUID, session_id: UUID) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session and session.user_id == user_id:
            return session
        return None

    async def list_by_patient(self, user_id: UUID, patient_id: UUID) -> List[Session]:
        return [
            s
            for s in self._sessions.values()
            if s.patient_id == patient_id and s.user_id == user_id
        ]

    async def list_recent(self, user_id: UUID, limit: int = 10) -> List[Session]:
        sessions = [
            s
            for s in self._sessions.values()
            if s.user_id == user_id
        ]
        sessions = sorted(sessions, key=lambda s: s.date_time, reverse=True)
        return sessions[:limit]

    async def update(self, session: Session) -> Session:
        self._sessions[session.id] = session
        return session

    async def list_all(
        self,
        user_id: UUID,
        patient_id: Optional[UUID] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
    ) -> List[Session]:
        sessions = [s for s in self._sessions.values() if s.user_id == user_id]

        if patient_id:
            sessions = [s for s in sessions if s.patient_id == patient_id]

        if status:
            sessions = [s for s in sessions if s.status.value == status]

        if start_date:
            sessions = [s for s in sessions if s.date_time.date() >= start_date]

        if end_date:
            sessions = [s for s in sessions if s.date_time.date() <= end_date]

        sessions.sort(key=lambda s: s.date_time, reverse=True)
        return sessions[:limit]


class FakeFinancialEntryRepository(FinancialEntryRepository):
    """Repositório fake de lançamentos financeiros (in-memory)."""

    def __init__(self) -> None:
        self._entries: Dict[UUID, FinancialEntry] = {}

    async def create(self, entry: FinancialEntry) -> FinancialEntry:
        self._entries[entry.id] = entry
        return entry

    async def get_by_id(self, user_id: UUID, entry_id: UUID) -> Optional[FinancialEntry]:
        entry = self._entries.get(entry_id)
        if entry and entry.user_id == user_id:
            return entry
        return None

    async def list_by_period(
        self,
        user_id: UUID,
        start_date: date,
        end_date: date,
        status_filter: Optional[List[EntryStatus]] = None,
    ) -> List[FinancialEntry]:
        entries = [
            e for e in self._entries.values()
            if e.user_id == user_id and start_date <= e.entry_date <= end_date
        ]
        if status_filter:
            entries = [e for e in entries if e.status in status_filter]
        return sorted(entries, key=lambda e: e.entry_date, reverse=True)

    async def list_pending(self, user_id: UUID) -> List[FinancialEntry]:
        return [
            e for e in self._entries.values()
            if e.user_id == user_id and e.status == EntryStatus.PENDENTE
        ]

    async def update(self, entry: FinancialEntry) -> FinancialEntry:
        self._entries[entry.id] = entry
        return entry
