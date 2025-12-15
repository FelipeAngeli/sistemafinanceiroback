"""Router para Health Checks."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Health Check",
    description="Verifica se a aplicação está rodando.",
)
async def health() -> dict:
    """Retorna status de saúde da aplicação."""
    return {"status": "healthy"}


@router.get(
    "/",
    summary="Root",
    description="Endpoint raiz da API.",
)
async def root() -> dict:
    """Endpoint raiz."""
    return {
        "app": "Sistema de Gestão para Psicóloga",
        "version": "0.1.0",
        "docs": "/docs",
    }
