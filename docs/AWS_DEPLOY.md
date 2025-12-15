# Deploy na AWS

Este documento explica como adaptar a aplicação para rodar na AWS.

## Opção 1: AWS Lambda + API Gateway

Ideal para cargas variáveis e custo baixo (pay-per-use).

### Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ API Gateway │────▶│   Lambda    │────▶│  RDS/Aurora │
│  (HTTP API) │     │  (FastAPI)  │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
```

### Passos

1. **Instalar dependências de produção:**
```bash
pip install mangum asyncpg
```

2. **Configurar variáveis de ambiente no Lambda:**
```
DATABASE_URL=postgresql+asyncpg://user:pass@rds-host:5432/db
APP_ENV=production
LOG_LEVEL=INFO
AWS_LAMBDA_MODE=true
```

3. **Handler já criado:** `app/lambda_handler.py`
```python
from mangum import Mangum
from app.interfaces.http.api import create_app

app = create_app()
handler = Mangum(app, lifespan="off")
```

4. **Empacotar para deploy:**
```bash
# Criar diretório de build
mkdir -p build
pip install -r requirements.txt -t build/
cp -r app build/
cd build && zip -r ../lambda.zip .
```

5. **Criar Lambda e API Gateway via console ou IaC (Terraform/CDK)**

### Considerações Lambda

- **Cold starts:** Primeira requisição pode ser lenta (~1-3s)
- **Timeout:** Configurar timeout adequado (30s recomendado)
- **Memória:** 256MB-512MB geralmente suficiente
- **VPC:** Necessário se RDS estiver em VPC privada
- **Lifespan:** Mangum com `lifespan="off"` pois Lambda não mantém estado

---

## Opção 2: ECS Fargate (Container)

Ideal para cargas constantes e maior controle.

### Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     ALB     │────▶│ ECS Fargate │────▶│  RDS/Aurora │
│             │     │ (Container) │     │ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
```

### Dockerfile (já criado)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Passos

1. **Build da imagem:**
```bash
docker build -t psychologist-system .
```

2. **Push para ECR:**
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag psychologist-system:latest <account>.dkr.ecr.<region>.amazonaws.com/psychologist-system:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/psychologist-system:latest
```

3. **Criar Task Definition no ECS** com:
   - Imagem do ECR
   - Variáveis de ambiente
   - CPU/Memória (0.5 vCPU / 1GB recomendado)
   - Health check: `/health`

4. **Criar Service no ECS** com:
   - ALB (Application Load Balancer)
   - Auto Scaling baseado em CPU/memória
   - Subnets privadas + NAT Gateway

### Considerações ECS

- **Custo fixo:** Paga por hora de execução
- **Sem cold starts:** Container sempre rodando
- **Auto Scaling:** Escala horizontal automática
- **Health checks:** ALB monitora `/health`

---

## Banco de Dados: RDS PostgreSQL

### Configuração recomendada

- **Engine:** PostgreSQL 15+
- **Instância:** db.t3.micro (dev) / db.t3.small (prod)
- **Multi-AZ:** Sim para produção
- **Backup:** 7 dias de retenção
- **Encryption:** Habilitado

### String de conexão

```
DATABASE_URL=postgresql+asyncpg://user:password@mydb.xxx.rds.amazonaws.com:5432/psychologist
```

### Migrar de SQLite para PostgreSQL

1. Descomentar `asyncpg` no requirements.txt
2. Atualizar DATABASE_URL
3. A aplicação criará as tabelas automaticamente no startup

---

## Variáveis de Ambiente (Produção)

```env
# Aplicação
APP_NAME=PsychologistSystem
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Banco
DATABASE_URL=postgresql+asyncpg://user:pass@rds-host:5432/db

# AWS
AWS_REGION=us-east-1
AWS_LAMBDA_MODE=true  # Apenas para Lambda

# CORS (domínios específicos)
CORS_ORIGINS=["https://meusite.com"]
```

---

## Checklist de Deploy

- [ ] RDS PostgreSQL criado e acessível
- [ ] Variáveis de ambiente configuradas
- [ ] CORS configurado com domínios corretos
- [ ] Logs configurados (CloudWatch)
- [ ] Health check funcionando
- [ ] SSL/TLS habilitado (ACM + ALB/API Gateway)
- [ ] Backup de banco configurado
- [ ] Monitoring/Alertas (CloudWatch Alarms)
