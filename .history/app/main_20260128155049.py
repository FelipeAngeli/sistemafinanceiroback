"""Ponto de entrada da aplicação.

Inicia a aplicação FastAPI.

Para desenvolvimento:
    uvicorn app.main:app --reload
    python -m app.main

Para produção (com Gunicorn):
    gunicorn app.main:app -c gunicorn.conf.py
    
Gunicorn usa UvicornWorker para suportar ASGI (FastAPI).
"""

from app.core.config import get_settings
from app.interfaces.http.api import create_app

# Cria a aplicação FastAPI
app = create_app()


if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    settings = get_settings()
    # Desabilitar reload no Windows devido a problemas com multiprocessing
    use_reload = settings.debug and sys.platform != "win32"
    
    # Render define PORT via variável de ambiente
    port = int(os.environ.get("PORT", settings.port))
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        reload=use_reload,
    )
