"""Configuração de logging estruturado.

Logger configurado para fácil integração com CloudWatch, ELK, Datadog.
Suporta formato JSON em produção para melhor parseabilidade.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class StructuredFormatter(logging.Formatter):
    """Formatter que gera logs em formato JSON estruturado.

    Ideal para produção onde logs são ingeridos por sistemas como
    CloudWatch Logs Insights, ELK, Datadog, etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adiciona exception info se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Adiciona campos extras
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Formatter legível para desenvolvimento.

    Usa cores ANSI para facilitar leitura no terminal.
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"{timestamp} | {color}{record.levelname:8}{self.RESET} | "
            f"{record.name} | {record.getMessage()}"
        )


class AppLogger:
    """Logger da aplicação com suporte a contexto.

    Uso:
        logger = get_logger(__name__)
        logger.info("Mensagem simples")
        logger.info("Com contexto", extra={"user_id": "123", "action": "login"})
    """

    _configured = False
    _log_level = logging.INFO
    _use_json = False

    @classmethod
    def configure(
        cls,
        level: str = "INFO",
        use_json: bool = False,
    ) -> None:
        """Configura o logging globalmente.

        Args:
            level: Nível de log (DEBUG, INFO, WARNING, ERROR)
            use_json: Se True, usa formato JSON (produção)
        """
        if cls._configured:
            return

        cls._log_level = getattr(logging, level.upper(), logging.INFO)
        cls._use_json = use_json

        # Configura root logger
        root = logging.getLogger()
        root.setLevel(cls._log_level)

        # Remove handlers existentes
        root.handlers.clear()

        # Adiciona handler apropriado
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(cls._log_level)

        if use_json:
            handler.setFormatter(StructuredFormatter())
        else:
            handler.setFormatter(ConsoleFormatter())

        root.addHandler(handler)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: Optional[str] = None) -> logging.Logger:
        """Retorna logger configurado."""
        # Auto-configura se necessário
        if not cls._configured:
            # Import aqui para evitar circular import
            from app.core.config import get_settings
            settings = get_settings()
            cls.configure(
                level=settings.log_level,
                use_json=settings.is_production,
            )

        return logging.getLogger(name or "app")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Atalho para obter logger configurado.

    Args:
        name: Nome do logger (geralmente __name__ do módulo).

    Returns:
        Logger configurado.

    Exemplo:
        from app.core.logger import get_logger

        logger = get_logger(__name__)
        logger.info("Aplicação iniciada")
        logger.error("Erro ao processar", exc_info=True)
    """
    return AppLogger.get_logger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any,
) -> None:
    """Loga mensagem com contexto adicional.

    Args:
        logger: Logger a usar
        level: Nível de log (logging.INFO, etc)
        message: Mensagem
        **context: Campos extras para incluir no log
    """
    extra = {"extra_fields": context} if context else {}
    logger.log(level, message, extra=extra)
