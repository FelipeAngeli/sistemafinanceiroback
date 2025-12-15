"""
Controller HTTP para Health Checks.

Útil para readiness/liveness probes em containers e ALB.
"""


class HealthController:
    """Controller para verificação de saúde da aplicação."""

    async def health(self) -> dict:
        """GET /health - Retorna status da aplicação."""
        return {"status": "healthy"}

    async def ready(self) -> dict:
        """GET /ready - Verifica se aplicação está pronta para receber tráfego."""
        pass
