"""Configuração do Gunicorn para produção.

Gunicorn com Uvicorn workers para FastAPI (ASGI).
Documentação: https://docs.gunicorn.org/
"""

import multiprocessing
import os

# Bind address e porta
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Workers
# Fórmula recomendada: (2 x CPU cores) + 1
# Para Render, usar número fixo de workers (ex: 2-4)
workers = int(os.environ.get("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
# Limitar workers para evitar uso excessivo de memória
if workers > 4:
    workers = 4

# Worker class: UvicornWorker para FastAPI (ASGI)
worker_class = "uvicorn.workers.UvicornWorker"

# Worker connections (threads por worker)
worker_connections = 1000

# Timeouts
timeout = 120  # Tempo máximo para processar uma requisição (segundos)
keepalive = 5  # Tempo para manter conexões keep-alive

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
# Gunicorn aceita: debug, info, warning, error, critical
log_level = os.environ.get("LOG_LEVEL", "info").lower()
# Garantir que seja um nível válido do Gunicorn
if log_level not in ["debug", "info", "warning", "error", "critical"]:
    log_level = "info"
loglevel = log_level

# Process naming
proc_name = "sistemafinanceiroback"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (se necessário, configurar via variáveis de ambiente)
# keyfile = None
# certfile = None

# Performance
preload_app = True  # Carrega aplicação antes de forking workers
max_requests = 1000  # Reinicia worker após N requisições (previne memory leaks)
max_requests_jitter = 50  # Adiciona aleatoriedade ao max_requests

# Graceful timeout para shutdown
graceful_timeout = 30

# StatsD (opcional, para métricas)
# statsd_host = None
# statsd_prefix = "gunicorn"
