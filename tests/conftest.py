"""Configurações e fixtures compartilhadas para testes.

Este arquivo configura:
- Banco SQLite em memória para testes de integração
- Fixtures de repositórios (fake para unitários, real para integração)
- Dados de exemplo
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import AsyncGenerator
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.domain.entities.patient import Patient
from app.domain.entities.session import Session, SessionStatus
from app.domain.entities.financial_entry import FinancialEntry, EntryStatus
from app.infra.db.models import Base
from app.infra.repositories import (
    SqlAlchemyPatientRepository,
    SqlAlchemySessionRepository,
    SqlAlchemyFinancialEntryRepository,
)


# ============================================================
# Event Loop
# ============================================================

@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para toda a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================
# Database Fixtures (Integração)
# ============================================================

@pytest_asyncio.fixture
async def db_engine():
    """Engine SQLAlchemy com SQLite em memória."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Sessão do banco para cada teste."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with session_factory() as session:
        yield session
        await session.rollback()


# ============================================================
# Repository Fixtures (Integração)
# ============================================================

@pytest_asyncio.fixture
async def patient_repository(db_session: AsyncSession) -> SqlAlchemyPatientRepository:
    """Repositório de pacientes com banco real."""
    return SqlAlchemyPatientRepository(db_session)


@pytest_asyncio.fixture
async def session_repository(db_session: AsyncSession) -> SqlAlchemySessionRepository:
    """Repositório de sessões com banco real."""
    return SqlAlchemySessionRepository(db_session)


@pytest_asyncio.fixture
async def financial_repository(db_session: AsyncSession) -> SqlAlchemyFinancialEntryRepository:
    """Repositório financeiro com banco real."""
    return SqlAlchemyFinancialEntryRepository(db_session)


# ============================================================
# Entity Fixtures (Dados de exemplo)
# ============================================================

@pytest.fixture
def sample_user_id() -> UUID:
    """ID de usuário de exemplo."""
    return uuid4()


@pytest.fixture
def sample_patient(sample_user_id: UUID) -> Patient:
    """Paciente de exemplo."""
    return Patient(
        user_id=sample_user_id,
        name="Maria Silva",
        email="maria@email.com",
        phone="(11) 99999-9999",
    )


@pytest.fixture
def sample_patient_id() -> UUID:
    """ID fixo para testes."""
    return uuid4()


@pytest.fixture
def sample_session(sample_user_id: UUID, sample_patient_id: UUID) -> Session:
    """Sessão de exemplo (AGENDADA)."""
    return Session(
        user_id=sample_user_id,
        patient_id=sample_patient_id,
        date_time=datetime(2024, 12, 15, 14, 0),
        price=Decimal("200.00"),
        duration_minutes=50,
    )


@pytest.fixture
def sample_financial_entry(sample_user_id: UUID, sample_patient_id: UUID) -> FinancialEntry:
    """Lançamento financeiro de exemplo."""
    return FinancialEntry(
        session_id=uuid4(),
        patient_id=sample_patient_id,
        user_id=sample_user_id,
        amount=Decimal("200.00"),
        entry_date=datetime(2024, 12, 15).date(),
    )


# ============================================================
# Data Fixtures (Dicts)
# ============================================================

@pytest.fixture
def sample_patient_data() -> dict:
    """Dados para criação de paciente."""
    return {
        "name": "Maria Silva",
        "email": "maria@email.com",
        "phone": "(11) 99999-9999",
    }


@pytest.fixture
def sample_session_data() -> dict:
    """Dados para criação de sessão."""
    return {
        "date_time": datetime(2024, 12, 15, 14, 0),
        "duration_minutes": 50,
        "price": Decimal("200.00"),
    }
