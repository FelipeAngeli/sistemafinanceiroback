"""Configuração do banco de dados SQLAlchemy.

Configuração centralizada de engine e session.
Facilmente adaptável para PostgreSQL/RDS trocando apenas a URL.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


class DatabaseManager:
    """Gerenciador de conexão com banco de dados.

    Uso:
        db = DatabaseManager()
        await db.init()  # Cria tabelas
        async with db.session() as session:
            # usar session
        await db.close()
    """

    def __init__(self, database_url: str | None = None) -> None:
        """Inicializa o gerenciador.

        Args:
            database_url: URL do banco. Se None, usa SQLite local.
                - SQLite: sqlite+aiosqlite:///./data.db
                - PostgreSQL: postgresql+asyncpg://user:pass@host/db
        """
        settings = get_settings()
        self._database_url = database_url or settings.database_url or "sqlite+aiosqlite:///./psychologist.db"

        self._engine: AsyncEngine = create_async_engine(
            self._database_url,
            echo=settings.debug,  # Log SQL em modo debug
            future=True,
        )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Retorna a engine SQLAlchemy."""
        return self._engine

    async def init(self) -> None:
        """Inicializa o banco de dados (cria tabelas)."""
        from app.infra.db.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Fecha conexões com o banco."""
        await self._engine.dispose()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager para sessão do banco.

        Uso:
            async with db.session() as session:
                # operações
                await session.commit()
        """
        session = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Singleton global (opcional, para uso simplificado)
_db_manager: DatabaseManager | None = None


def get_database_manager() -> DatabaseManager:
    """Retorna instância global do DatabaseManager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper para FastAPI."""
    db = get_database_manager()
    async with db.session() as session:
        yield session
