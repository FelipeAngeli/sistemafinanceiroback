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
        from sqlalchemy.exc import OperationalError
        import sqlite3

        # Usa connect() ao invés de begin() para evitar problemas com transações
        # quando tabelas já existem
        async with self._engine.connect() as conn:
            # Usa checkfirst=True para evitar erro se tabelas já existirem
            # run_sync passa a conexão síncrona como primeiro argumento
            def create_tables(sync_conn):
                try:
                    Base.metadata.create_all(bind=sync_conn, checkfirst=True)
                except (OperationalError, sqlite3.OperationalError) as e:
                    # Se a tabela já existe, ignora o erro
                    # Isso pode acontecer mesmo com checkfirst=True em alguns casos
                    error_msg = str(e).lower()
                    if "already exists" not in error_msg and "duplicate" not in error_msg:
                        # Se não for erro de tabela existente, re-raise
                        raise
            
            try:
                await conn.run_sync(create_tables)
                await conn.commit()
            except (OperationalError, sqlite3.OperationalError) as e:
                # Tratamento adicional no nível async
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate" in error_msg:
                    # Se for erro de tabela já existente, ignora silenciosamente
                    # Não precisa fazer commit pois não houve mudanças
                    pass
                else:
                    raise
            except Exception as e:
                # Captura qualquer outro erro e verifica se é relacionado a tabelas existentes
                error_msg = str(e).lower()
                if "already exists" in error_msg or "duplicate" in error_msg:
                    # Se for erro de tabela já existente, ignora silenciosamente
                    pass
                else:
                    raise

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
