"""Exception handlers globais para FastAPI.

Traduz exceções da aplicação para respostas HTTP apropriadas.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    BusinessRuleError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from app.core.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registra handlers de exceção na aplicação FastAPI."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Handler para NotFoundError -> 404."""
        logger.warning(f"Not found: {exc.message}", extra={"path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=exc.to_dict(),
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handler para ValidationError -> 422."""
        logger.warning(f"Validation error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exc.to_dict(),
        )

    @app.exception_handler(BusinessRuleError)
    async def business_rule_handler(
        request: Request, exc: BusinessRuleError
    ) -> JSONResponse:
        """Handler para BusinessRuleError -> 422."""
        logger.warning(f"Business rule violation: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exc.to_dict(),
        )

    @app.exception_handler(DomainError)
    async def domain_handler(request: Request, exc: DomainError) -> JSONResponse:
        """Handler para DomainError genérico -> 400."""
        logger.warning(f"Domain error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=exc.to_dict(),
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handler para AppException genérica -> 500."""
        logger.error(f"App exception: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=exc.to_dict(),
        )

    @app.exception_handler(Exception)
    async def generic_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handler para exceções não tratadas -> 500."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Erro interno do servidor.",
                    "details": {},
                }
            },
        )
