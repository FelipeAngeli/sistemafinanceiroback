"""Configurações da aplicação.

Centraliza variáveis de ambiente com validação via Pydantic.
Permite fácil troca entre ambientes (dev/staging/prod).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações globais da aplicação.

    Variáveis de ambiente são lidas automaticamente.
    Exemplo: APP_NAME -> app_name

    Para trocar de SQLite para PostgreSQL:
        DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="PsychologistSystem")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Ambiente de execução",
    )
    debug: bool = Field(
        default=False,
        description="Modo debug (logs detalhados, reload automático)",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Nível de log",
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./psychologist.db",
        description=(
            "URL de conexão com o banco. Exemplos:\n"
            "- SQLite: sqlite+aiosqlite:///./data.db\n"
            "- PostgreSQL: postgresql+asyncpg://user:pass@host:5432/db"
        ),
    )

    # AWS (para deploy)
    aws_region: str = Field(default="us-east-1")
    aws_lambda_mode: bool = Field(
        default=False,
        description="True quando rodando em AWS Lambda",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
        ],
        description="Origens permitidas para CORS",
    )

    @computed_field
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção."""
        return self.app_env == "production"

    @computed_field
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento."""
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada de configurações.

    Usa lru_cache para evitar reler .env a cada chamada.
    """
    return Settings()
