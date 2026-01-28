"""Configurações da aplicação.

Centraliza variáveis de ambiente com validação via Pydantic.
Permite fácil troca entre ambientes (dev/staging/prod).
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field, field_validator
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

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        """Converte log_level para maiúsculo."""
        if isinstance(v, str):
            return v.upper()
        return v

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(
        default=8000,
        description="Porta do servidor. Render define PORT dinamicamente via variável de ambiente.",
    )

    @field_validator("port", mode="before")
    @classmethod
    def parse_port(cls, v: str | int) -> int:
        """Converte port para int (Pydantic já mapeia PORT do ambiente automaticamente)."""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return 8000
        return v if isinstance(v, int) else 8000

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./psychologist.db",
        description=(
            "URL de conexão com o banco. Exemplos:\n"
            "- SQLite: sqlite+aiosqlite:///./data.db\n"
            "- PostgreSQL: postgresql+asyncpg://user:pass@host:5432/db\n"
            "Nota: Render fornece postgresql://, mas será convertido automaticamente."
        ),
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        """Converte postgresql:// para postgresql+asyncpg:// se necessário.
        
        Render e outros serviços fornecem URLs no formato postgresql://,
        mas SQLAlchemy async precisa de postgresql+asyncpg://.
        """
        if isinstance(v, str) and v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

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
