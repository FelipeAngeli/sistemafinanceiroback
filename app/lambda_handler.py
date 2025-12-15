"""Handler para AWS Lambda com API Gateway.

Este módulo permite rodar a aplicação FastAPI em AWS Lambda.
Usa Mangum como adaptador ASGI para Lambda.

Instalação:
    pip install mangum

Deploy:
    1. Empacotar código + dependências em ZIP
    2. Criar função Lambda (Python 3.11+)
    3. Configurar API Gateway (HTTP API ou REST API)
    4. Definir variáveis de ambiente no Lambda

Variáveis de ambiente necessárias:
    - DATABASE_URL: URL do banco (ex: PostgreSQL RDS)
    - APP_ENV: production
    - LOG_LEVEL: INFO
    - AWS_LAMBDA_MODE: true
"""

from mangum import Mangum

from app.interfaces.http.api import create_app

# Cria aplicação FastAPI
app = create_app()

# Adapta para AWS Lambda
# O Mangum traduz eventos do API Gateway para requests ASGI
handler = Mangum(app, lifespan="off")


# Para testes locais do handler
if __name__ == "__main__":
    # Simula evento do API Gateway
    test_event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "stage": "dev",
        },
    }
    test_context = {}

    response = handler(test_event, test_context)
    print(f"Response: {response}")
