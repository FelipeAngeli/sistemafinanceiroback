"""Configuração da aplicação FastAPI.

Factory function que cria e configura a aplicação.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logger import get_logger
from app.infra.db.database import get_database_manager
from app.interfaces.http.exception_handlers import register_exception_handlers
from app.interfaces.http.routers import (
    dashboard_router,
    patient_router,
    session_router,
    financial_router,
    health_router,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia ciclo de vida da aplicação.

    - Startup: inicializa banco de dados
    - Shutdown: fecha conexões
    """
    settings = get_settings()
    logger.info(f"Iniciando {settings.app_name} em modo {settings.app_env}")

    # Startup
    db = get_database_manager()
    await db.init()
    logger.info("Banco de dados inicializado")

    yield

    # Shutdown
    await db.close()
    logger.info("Conexões encerradas")


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI.

    Returns:
        Aplicação FastAPI configurada.
    """
    settings = get_settings()

    app = FastAPI(
        title="Sistema de Gestão para Psicóloga",
        description="""
## API REST para Gestão de Consultório de Psicologia

Esta API permite gerenciar:

- **Pacientes**: Cadastro e consulta de pacientes
- **Sessões**: Agendamento, conclusão e cancelamento de sessões
- **Financeiro**: Lançamentos automáticos e relatórios

### Regra de Negócio Principal

Quando uma sessão é marcada como **CONCLUÍDA**, um lançamento financeiro 
**PENDENTE** é criado automaticamente com o valor da sessão.

### Arquitetura

Desenvolvido seguindo **Clean Architecture** com separação clara entre:
- Domínio (entidades e regras de negócio)
- Casos de Uso (lógica de aplicação)
- Infraestrutura (banco de dados)
- Interfaces (API REST)

### Tecnologias

- **FastAPI** + **Pydantic** (validação)
- **SQLAlchemy** (ORM async)
- **SQLite** (dev) / **PostgreSQL** (prod)
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "Health",
                "description": "Endpoints de health check e status da API.",
            },
            {
                "name": "Pacientes",
                "description": "Gerenciamento de pacientes: criar, listar, buscar.",
            },
            {
                "name": "Sessões",
                "description": "Gerenciamento de sessões: agendar, concluir, cancelar. "
                "Ao concluir, cria lançamento financeiro automaticamente.",
            },
            {
                "name": "Financeiro",
                "description": "Relatórios financeiros e listagem de lançamentos.",
            },
            {
                "name": "Dashboard",
                "description": "Resumo consolidado do dashboard com múltiplas informações.",
            },
        ],
        contact={
            "name": "Suporte",
            "email": "suporte@sistema.com",
        },
        license_info={
            "name": "MIT",
        },
    )

    # Exception handlers globais
    register_exception_handlers(app)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar routers
    app.include_router(health_router)
    app.include_router(patient_router)
    app.include_router(session_router)
    app.include_router(financial_router)
    app.include_router(dashboard_router)

    return app
