"""Configuração da aplicação FastAPI.

Factory function que cria e configura a aplicação.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.core.config import get_settings
from app.core.logger import get_logger
from app.infra.db.database import get_database_manager
from app.interfaces.http.exception_handlers import register_exception_handlers
from app.interfaces.http.routers import (
    auth_router,
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

    # Obter origens CORS das configurações
    cors_allow_origins = settings.cors_origins.copy()
    
    # IMPORTANTE: Quando allow_credentials=True, não podemos usar "*" como origem
    # Se houver "*" na lista, removemos e tratamos separadamente
    allow_all_origins = "*" in cors_allow_origins
    if allow_all_origins:
        cors_allow_origins.remove("*")
    
    # CORS - DEVE SER O PRIMEIRO MIDDLEWARE para processar requisições OPTIONS corretamente
    # Se allow_all_origins=True, usamos ["*"] mas com allow_credentials=False
    # Caso contrário, usamos a lista específica com allow_credentials=True
    if allow_all_origins and not cors_allow_origins:
        # Se só tem "*" e nenhuma origem específica, permite todas sem credentials
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,  # Não pode ser True com "*"
            allow_methods=["*"],  # Inclui OPTIONS automaticamente
            allow_headers=["*"],
            expose_headers=["*"],
        )
    else:
        # Usa lista específica de origens com credentials habilitado
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_allow_origins if cors_allow_origins else ["*"],
            allow_credentials=True if cors_allow_origins else False,
            allow_methods=["*"],  # Inclui OPTIONS automaticamente
            allow_headers=["*"],
            expose_headers=["*"],
        )

    # Exception handlers globais (depois do CORS)
    register_exception_handlers(app)

    # Handler explícito para OPTIONS (fallback caso o middleware não capture)
    # Este handler garante que OPTIONS requests sempre retornem 200 mesmo para rotas inexistentes
    @app.options("/{full_path:path}")
    async def options_handler(request: Request, full_path: str) -> Response:
        """Handler para requisições OPTIONS não capturadas pelo middleware CORS.
        
        Este é um fallback de segurança. O CORSMiddleware deve processar
        a maioria das requisições OPTIONS antes que cheguem aqui.
        """
        origin = request.headers.get("origin")
        
        # Determina origem permitida
        if allow_all_origins:
            # Se permite todas as origens, usa a origem da requisição ou "*"
            allowed_origin = origin if origin else "*"
            allow_creds = False  # Não pode ser True com "*"
        else:
            # Verifica se a origem está na lista permitida
            if origin and origin in cors_allow_origins:
                allowed_origin = origin
                allow_creds = True
            elif origin:
                # Origem não permitida - retorna sem CORS headers
                return Response(status_code=200)
            else:
                # Sem origem (requisição não-CORS)
                allowed_origin = "*"
                allow_creds = False
        
        headers = {
            "Access-Control-Allow-Methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": allowed_origin,
        }
        
        if allow_creds:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        return Response(status_code=200, headers=headers)

    # Registrar routers
    app.include_router(health_router)
    app.include_router(auth_router)  # Autenticação (sem proteção)
    app.include_router(patient_router)
    app.include_router(session_router)
    app.include_router(financial_router)
    app.include_router(dashboard_router)

    return app
