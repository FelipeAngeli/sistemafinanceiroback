"""Exceções customizadas da aplicação.

Hierarquia de exceções para tratamento consistente de erros.

Hierarquia:
    AppException (base)
    ├── DomainError (erros de domínio/negócio)
    │   ├── ValidationError (dados inválidos)
    │   └── BusinessRuleError (violação de regra)
    ├── NotFoundError (entidade não encontrada)
    └── InfrastructureError (erros de infra)
"""

from typing import Any, Optional


class AppException(Exception):
    """Exceção base da aplicação.

    Todas as exceções customizadas devem herdar desta classe.
    Facilita tratamento centralizado em middlewares/handlers.
    """

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Converte exceção para dict (para respostas HTTP)."""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# ============================================================
# Erros de Domínio
# ============================================================


class DomainError(AppException):
    """Erro genérico de domínio/negócio."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, code="DOMAIN_ERROR", details=details)


class ValidationError(DomainError):
    """Erro de validação de dados.

    Usado quando dados de entrada são inválidos.
    Exemplo: nome vazio, email mal formatado, preço negativo.
    """

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message=message, details=details)
        self.code = "VALIDATION_ERROR"


class BusinessRuleError(DomainError):
    """Violação de regra de negócio.

    Usado quando uma operação viola uma regra do domínio.
    Exemplo: concluir sessão já cancelada, pagar lançamento já pago.
    """

    def __init__(self, message: str, rule: Optional[str] = None):
        details = {"rule": rule} if rule else {}
        super().__init__(message=message, details=details)
        self.code = "BUSINESS_RULE_ERROR"


# ============================================================
# Erros de Not Found
# ============================================================


class NotFoundError(AppException):
    """Recurso não encontrado.

    Usado quando uma entidade/recurso não existe.
    """

    def __init__(
        self,
        resource: str,
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self.resource = resource
        self.resource_id = resource_id
        msg = message or f"{resource} não encontrado(a)."
        if resource_id:
            msg = f"{resource} com id '{resource_id}' não encontrado(a)."
        super().__init__(
            message=msg,
            code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id},
        )


# Alias para compatibilidade
EntityNotFoundError = NotFoundError


# ============================================================
# Erros de Infraestrutura
# ============================================================


class InfrastructureError(AppException):
    """Erro de infraestrutura.

    Usado para erros de banco, rede, serviços externos.
    """

    def __init__(self, message: str, service: Optional[str] = None):
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            code="INFRASTRUCTURE_ERROR",
            details=details,
        )


class DatabaseError(InfrastructureError):
    """Erro de banco de dados."""

    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(message=message, service="database")
        self.code = "DATABASE_ERROR"
        if operation:
            self.details["operation"] = operation
