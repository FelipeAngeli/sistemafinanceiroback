"""Core module - configurações, exceções e utilitários compartilhados.

Este módulo contém funcionalidades transversais usadas por todas as camadas.
"""

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.core.exceptions import (
    AppException,
    DomainError,
    ValidationError,
    BusinessRuleError,
    NotFoundError,
    EntityNotFoundError,
    InfrastructureError,
    DatabaseError,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    # Logger
    "get_logger",
    # Exceptions
    "AppException",
    "DomainError",
    "ValidationError",
    "BusinessRuleError",
    "NotFoundError",
    "EntityNotFoundError",
    "InfrastructureError",
    "DatabaseError",
]
