"""Fixtures para testes de API."""

import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infra.db.models import Base
from app.infra.db.database import get_database_manager
from app.interfaces.http.api import create_app


@pytest.fixture
def auth_headers(token: str) -> dict:
    """Retorna headers com token de autenticação."""
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def token(client: AsyncClient) -> str:
    """Cria usuário de teste e retorna token JWT."""
    # Gerar email único para evitar conflitos
    unique_email = f"test_{uuid4().hex[:8]}@example.com"
    
    # Registrar usuário
    register_response = await client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "test123",
            "name": "Usuário Teste",
        },
    )
    assert register_response.status_code == 201
    
    # Fazer login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": "test123",
        },
    )
    assert login_response.status_code == 200
    
    return login_response.json()["access_token"]


@pytest_asyncio.fixture
async def user2_token(client: AsyncClient) -> str:
    """Cria segundo usuário de teste e retorna token JWT."""
    # Gerar email único para evitar conflitos
    unique_email = f"test2_{uuid4().hex[:8]}@example.com"
    
    # Registrar segundo usuário
    register_response = await client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": "test123",
            "name": "Usuário Teste 2",
        },
    )
    assert register_response.status_code == 201
    
    # Fazer login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": "test123",
        },
    )
    assert login_response.status_code == 200
    
    return login_response.json()["access_token"]


@pytest.fixture
def user2_auth_headers(user2_token: str) -> dict:
    """Retorna headers com token do segundo usuário."""
    return {"Authorization": f"Bearer {user2_token}"}


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
