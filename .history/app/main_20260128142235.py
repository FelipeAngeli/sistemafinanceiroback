"""Ponto de entrada da aplicação.

Inicia a aplicação FastAPI.

Para rodar:
    uvicorn app.main:app --reload

Ou:
    python -m app.main
"""

from app.core.config import get_settings
from app.interfaces.http.api import create_app

# Cria a aplicação FastAPI
app = create_app()


if __name__ == "__main__":
    import sys
    import uvicorn

    settings = get_settings()
    # Desabilitar reload no Windows devido a problemas com multiprocessing
    use_reload = settings.debug and sys.platform != "win32"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=use_reload,
    )
