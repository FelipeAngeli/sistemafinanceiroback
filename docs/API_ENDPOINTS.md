# API Endpoints Overview

Este documento descreve todos os endpoints disponíveis na API (de acordo com o Swagger atual).

## Índice

1. [Health](#health)
2. [Pacientes](#pacientes)
3. [Sessões](#sessões)
4. [Financeiro](#financeiro)
5. [Dashboard](#dashboard)

---

## Health

| Método | Rota    | Descrição                     | Observações |
|--------|---------|--------------------------------|-------------|
| GET    | `/health` | Health check básico            | Retorna `{ "status": "healthy" }`. |
| GET    | `/`       | Endpoint raiz                  | Retorna nome do app, versão e link de docs. |

---

## Pacientes

| Método | Rota               | Descrição                         | Corpo / Query                                                                 | Resposta |
|--------|--------------------|-----------------------------------|-------------------------------------------------------------------------------|----------|
| GET    | `/patients/summary` | Estatísticas de pacientes         | —                                                                             | `PatientSummaryResponse` (totais, ativos, inativos, % ativos). |
| POST   | `/patients`         | Criar paciente                    | `PatientCreate`: `{ name*, email?, phone?, observation? }`                    | `201` + `PatientResponse`. |
| GET    | `/patients`         | Listar pacientes                  | Query `active_only` (bool, default `true`).                                   | `PatientListResponse` (lista + total). |
| GET    | `/patients/{id}`    | Buscar paciente por ID            | Path `id` (UUID).                                                             | `PatientResponse` ou `404`. |

---

## Sessões

| Método | Rota                         | Descrição                                  | Parâmetros / Corpo                                                                                           | Resposta |
|--------|------------------------------|--------------------------------------------|---------------------------------------------------------------------------------------------------------------|----------|
| GET    | `/sessions`                  | Listar sessões                             | Query: `patient_id?`, `status?`, `start_date?`, `end_date?`, `limit` (1-100, default 50).                     | `SessionListResponse`. |
| POST   | `/sessions`                  | Criar sessão                               | `SessionCreate`: `{ patient_id*, date_time*, price*, duration_minutes?, notes? }`.                            | `201` + `SessionResponse` (status inicial `agendada`). |
| GET    | `/sessions/{id}`             | Detalhar sessão                            | Path `id` (UUID).                                                                                              | `SessionResponse` ou `404`. |
| PATCH  | `/sessions/{id}`             | Atualizar dados da sessão (parcial)        | Path `id`; body `SessionUpdate` (todos opcionais: `patient_id`, `date_time`, `price`, `notes`).                | `SessionResponse` atualizada. Não altera status. |
| PATCH  | `/sessions/{id}/status`      | Atualizar status da sessão                 | Body `SessionStatusUpdate`: `{ new_status* (agendada|realizada|cancelada|faltou), notes? }`.                   | `SessionStatusResponse` (inclui info de lançamento financeiro). |

---

## Financeiro

| Método | Rota               | Descrição                                        | Parâmetros / Corpo                                                                                                            | Resposta |
|--------|--------------------|--------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|----------|
| GET    | `/financial/entries` | Listar lançamentos + relatório consolidado        | Query obrigatória: `start_date`, `end_date`. Query opcional: `status` (lista de `pendente`/`pago`).                            | `FinancialReportResponse` (entries + totais: `total_entries`, `total_amount`, `total_pending`, `total_paid`, período). |

> *Observação*: endpoints POST/GET/{id}/PATCH para Financial ainda não estão implementados neste Swagger.

---

## Dashboard

| Método | Rota                  | Descrição                           | Parâmetros / Corpo                                               | Resposta |
|--------|-----------------------|-------------------------------------|------------------------------------------------------------------|----------|
| GET    | `/dashboard/summary`  | Resumo agregado (financeiro/sessões/pacientes) | Query obrigatória: `start_date`, `end_date` (formato `YYYY-MM-DD`). | `DashboardSummaryResponse` com blocos `financial`, `sessions`, `patients`. |

---

*Última atualização:* gerado automaticamente via análise dos routers FastAPI em `app/interfaces/http/routers/`.
