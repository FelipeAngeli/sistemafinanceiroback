# Configuração do Gunicorn

Este documento explica a configuração do Gunicorn no projeto.

## Por que Gunicorn?

O projeto usa **Gunicorn** com **Uvicorn workers** para produção porque:

1. **Performance**: Múltiplos workers processam requisições em paralelo
2. **Confiabilidade**: Reinício automático de workers em caso de falha
3. **Escalabilidade**: Fácil ajuste do número de workers
4. **Produção-ready**: Battle-tested em milhares de aplicações Python

## Arquitetura

```
Gunicorn (Master Process)
├── Worker 1 (UvicornWorker) → FastAPI App
├── Worker 2 (UvicornWorker) → FastAPI App
├── Worker 3 (UvicornWorker) → FastAPI App
└── Worker 4 (UvicornWorker) → FastAPI App
```

Cada worker roda uma instância do FastAPI e processa requisições de forma assíncrona (ASGI).

## Configuração

O arquivo `gunicorn.conf.py` contém todas as configurações:

### Principais Configurações

- **bind**: `0.0.0.0:$PORT` - Endereço e porta (lê PORT do ambiente)
- **workers**: Controlado via `WEB_CONCURRENCY` (padrão: 2-4)
- **worker_class**: `uvicorn.workers.UvicornWorker` (ASGI)
- **timeout**: 120 segundos (tempo máximo para processar requisição)
- **preload_app**: `True` (carrega app antes de forking)
- **max_requests**: 1000 (reinicia worker após N requisições)

### Variáveis de Ambiente

```env
PORT=10000              # Porta do servidor (definida pelo Render)
WEB_CONCURRENCY=2        # Número de workers (ajustar conforme recursos)
LOG_LEVEL=info          # Nível de log (debug, info, warning, error)
```

## Uso

### Desenvolvimento

Para desenvolvimento, use Uvicorn diretamente (com reload):

```bash
uvicorn app.main:app --reload
```

### Produção

Para produção, use Gunicorn:

```bash
gunicorn app.main:app -c gunicorn.conf.py
```

## Ajustar Workers

O número de workers é calculado automaticamente, mas pode ser ajustado via `WEB_CONCURRENCY`:

**Fórmula padrão:**
```
workers = (2 × CPU cores) + 1
```

**Limite máximo:** 4 workers (configurado em `gunicorn.conf.py`)

**Recomendações por plano Render:**

| Plano | CPU | Memória | Workers Recomendados |
|-------|-----|---------|---------------------|
| Starter | 0.5 | 512MB | 2 |
| Standard | 1 | 2GB | 2-4 |
| Pro | 2+ | 4GB+ | 4-8 |

**Configurar:**
```env
WEB_CONCURRENCY=4  # No dashboard do Render ou render.yaml
```

## Monitoramento

### Logs

Gunicorn envia logs para stdout/stderr, que são capturados pelo Render:

- **Access logs**: Requisições HTTP
- **Error logs**: Erros e warnings

### Métricas

O Render fornece métricas básicas:
- CPU usage
- Memory usage
- Request rate

Para métricas avançadas, considere integrar com StatsD (comentado em `gunicorn.conf.py`).

## Troubleshooting

### Workers morrendo constantemente

- Reduza `WEB_CONCURRENCY`
- Verifique logs para erros específicos
- Aumente recursos do plano se necessário

### Alta utilização de memória

- Reduza número de workers
- Verifique se há memory leaks
- Gunicorn reinicia workers após `max_requests` (1000)

### Timeout errors

- Aumente `timeout` em `gunicorn.conf.py` (padrão: 120s)
- Otimize queries de banco de dados
- Verifique se há operações bloqueantes

## Recursos

- [Documentação Gunicorn](https://docs.gunicorn.org/)
- [Uvicorn Workers](https://www.uvicorn.org/deployment/#gunicorn)
- [Render Deployment](RENDER_DEPLOY.md)
