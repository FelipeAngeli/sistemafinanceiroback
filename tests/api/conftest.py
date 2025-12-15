"""Fixtures para testes de API."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infra.db.models import Base
from app.infra.db.database import get_database_manager
from app.interfaces.http.api import create_app


@pytest.fixture(scope="module")
def event_loop():
    """Event loop para o módulo de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def test_app():
    """Aplicação FastAPI para testes.
    
    Configura banco SQLite em memória antes de criar a app.
    """
    # Criar engine em memória
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Substituir o database manager global
    from app.infra.db import database
    
    original_manager = database._db_manager
    
    # Criar novo manager com engine em memória
    class TestDatabaseManager:
        def __init__(self, eng):
            self._engine = eng
            self._session_factory = async_sessionmaker(
                bind=eng,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        
        async def init(self):
            pass  # Tabelas já criadas
        
        async def close(self):
            pass
        
        def session(self):
            from contextlib import asynccontextmanager
            @asynccontextmanager
            async def _session():
                async with self._session_factory() as session:
                    yield session
            return _session()
    
    database._db_manager = TestDatabaseManager(engine)
    
    # Criar app
    app = create_app()
    
    yield app
    
    # Cleanup
    database._db_manager = original_manager
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP assíncrono para testes."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
