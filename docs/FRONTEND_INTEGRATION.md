# Guia de Integração Frontend

Este documento contém todas as informações necessárias para criar um frontend
que se conecte ao backend do Sistema de Gestão para Psicóloga.

---

## Visão Geral

### Backend
- **URL Base (dev):** `http://localhost:8000`
- **Documentação Swagger:** `http://localhost:8000/docs`
- **Autenticação:** Não implementada (adicionar se necessário)
- **Formato:** JSON (application/json)

### Entidades Principais

```
┌──────────┐       ┌──────────┐       ┌─────────────────┐
│ Patient  │──1:N──│ Session  │──1:1──│ FinancialEntry  │
└──────────┘       └──────────┘       └─────────────────┘
```

- **Patient:** Paciente cadastrado
- **Session:** Sessão de atendimento (AGENDADA → CONCLUÍDA ou CANCELADA)
- **FinancialEntry:** Lançamento financeiro (criado automaticamente ao concluir sessão)

---

## Regra de Negócio Principal

> **Quando uma sessão é marcada como CONCLUÍDA, um lançamento financeiro 
> PENDENTE é criado automaticamente com o valor da sessão.**

---

## Endpoints da API

### 1. Pacientes

#### Criar Paciente
```http
POST /patients
Content-Type: application/json

{
  "name": "Maria Silva",           // obrigatório, min 2 chars
  "email": "maria@email.com",      // opcional, formato email
  "phone": "(11) 99999-9999",      // opcional
  "notes": "Observações"           // opcional
}
```

**Resposta (201 Created):**
```json
{
  "id": "uuid-do-paciente",
  "name": "Maria Silva",
  "email": "maria@email.com",
  "phone": "(11) 99999-9999",
  "active": true
}
```

#### Listar Pacientes
```http
GET /patients?active_only=true
```

**Resposta (200 OK):**
```json
{
  "patients": [
    {
      "id": "uuid",
      "name": "Maria Silva",
      "email": "maria@email.com",
      "phone": "(11) 99999-9999",
      "active": true
    }
  ],
  "total": 1
}
```

#### Buscar Paciente por ID
```http
GET /patients/{patient_id}
```

**Resposta (200 OK):**
```json
{
  "id": "uuid",
  "name": "Maria Silva",
  "email": "maria@email.com",
  "phone": "(11) 99999-9999",
  "active": true
}
```

**Erro (404 Not Found):**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Paciente com id 'uuid' não encontrado(a).",
    "details": {"resource": "Paciente", "resource_id": "uuid"}
  }
}
```

---

### 2. Sessões

#### Criar Sessão (Agendar)
```http
POST /sessions
Content-Type: application/json

{
  "patient_id": "uuid-do-paciente",   // obrigatório
  "date_time": "2024-12-15T14:00:00", // obrigatório, ISO 8601
  "price": 200.00,                    // obrigatório, >= 0
  "duration_minutes": 50,             // opcional, default 50
  "notes": "Primeira consulta"        // opcional
}
```

**Resposta (201 Created):**
```json
{
  "id": "uuid-da-sessao",
  "patient_id": "uuid-do-paciente",
  "date_time": "2024-12-15T14:00:00",
  "price": "200.00",
  "duration_minutes": 50,
  "status": "agendada"
}
```

#### Atualizar Status da Sessão
```http
PATCH /sessions/{session_id}/status
Content-Type: application/json

{
  "new_status": "concluida",          // "concluida" ou "cancelada"
  "notes": "Sessão realizada"         // opcional
}
```

**Resposta (200 OK) - Quando CONCLUÍDA:**
```json
{
  "session_id": "uuid-da-sessao",
  "previous_status": "agendada",
  "new_status": "concluida",
  "financial_entry_created": true,
  "financial_entry_id": "uuid-do-lancamento",
  "financial_entry_amount": "200.00"
}
```

**Resposta (200 OK) - Quando CANCELADA:**
```json
{
  "session_id": "uuid-da-sessao",
  "previous_status": "agendada",
  "new_status": "cancelada",
  "financial_entry_created": false,
  "financial_entry_id": null,
  "financial_entry_amount": null
}
```

#### Status Possíveis
| Status | Valor | Descrição |
|--------|-------|-----------|
| Agendada | `agendada` | Estado inicial |
| Concluída | `concluida` | Sessão realizada (gera lançamento) |
| Cancelada | `cancelada` | Sessão cancelada (não gera lançamento) |

---

### 3. Financeiro

#### Listar Lançamentos / Relatório
```http
GET /financial/entries?start_date=2024-12-01&end_date=2024-12-31&status=pendente
```

**Parâmetros:**
| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| start_date | date | Sim | Data inicial (YYYY-MM-DD) |
| end_date | date | Sim | Data final (YYYY-MM-DD) |
| status | string[] | Não | Filtro: `pendente`, `pago` |

**Resposta (200 OK):**
```json
{
  "entries": [
    {
      "id": "uuid",
      "session_id": "uuid",
      "patient_id": "uuid",
      "entry_date": "2024-12-15",
      "amount": "200.00",
      "status": "pendente",
      "description": "Sessão de 15/12/2024 14:00"
    }
  ],
  "total_entries": 1,
  "total_amount": "200.00",
  "total_pending": "200.00",
  "total_paid": "0",
  "period_start": "2024-12-01",
  "period_end": "2024-12-31"
}
```

#### Status dos Lançamentos
| Status | Valor | Descrição |
|--------|-------|-----------|
| Pendente | `pendente` | Aguardando pagamento |
| Pago | `pago` | Pagamento recebido |

---

### 4. Health Check

```http
GET /health
```

**Resposta (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Códigos de Erro

| Código HTTP | Código | Descrição |
|-------------|--------|-----------|
| 404 | NOT_FOUND | Recurso não encontrado |
| 422 | VALIDATION_ERROR | Dados inválidos |
| 422 | BUSINESS_RULE_ERROR | Violação de regra de negócio |
| 500 | INTERNAL_ERROR | Erro interno do servidor |

**Formato padrão de erro:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Descrição do erro",
    "details": {}
  }
}
```

---

## Exemplos de Código (React/TypeScript)

### Configuração do Cliente API

```typescript
// src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Erro na requisição');
  }

  return response.json();
}

export const api = {
  // Pacientes
  patients: {
    list: (activeOnly = true) => 
      fetchAPI<PatientListResponse>(`/patients?active_only=${activeOnly}`),
    
    get: (id: string) => 
      fetchAPI<Patient>(`/patients/${id}`),
    
    create: (data: CreatePatientInput) =>
      fetchAPI<Patient>('/patients', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Sessões
  sessions: {
    create: (data: CreateSessionInput) =>
      fetchAPI<Session>('/sessions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    
    updateStatus: (id: string, data: UpdateStatusInput) =>
      fetchAPI<SessionStatusResponse>(`/sessions/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },

  // Financeiro
  financial: {
    report: (startDate: string, endDate: string, status?: string[]) => {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });
      status?.forEach(s => params.append('status', s));
      return fetchAPI<FinancialReport>(`/financial/entries?${params}`);
    },
  },
};
```

### Tipos TypeScript

```typescript
// src/types/index.ts

// Paciente
interface Patient {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  active: boolean;
}

interface PatientListResponse {
  patients: Patient[];
  total: number;
}

interface CreatePatientInput {
  name: string;
  email?: string;
  phone?: string;
  notes?: string;
}

// Sessão
type SessionStatus = 'agendada' | 'concluida' | 'cancelada';

interface Session {
  id: string;
  patient_id: string;
  date_time: string;
  price: string;
  duration_minutes: number;
  status: SessionStatus;
}

interface CreateSessionInput {
  patient_id: string;
  date_time: string;
  price: number;
  duration_minutes?: number;
  notes?: string;
}

interface UpdateStatusInput {
  new_status: 'concluida' | 'cancelada';
  notes?: string;
}

interface SessionStatusResponse {
  session_id: string;
  previous_status: SessionStatus;
  new_status: SessionStatus;
  financial_entry_created: boolean;
  financial_entry_id: string | null;
  financial_entry_amount: string | null;
}

// Financeiro
type EntryStatus = 'pendente' | 'pago';

interface FinancialEntry {
  id: string;
  session_id: string;
  patient_id: string;
  entry_date: string;
  amount: string;
  status: EntryStatus;
  description: string;
}

interface FinancialReport {
  entries: FinancialEntry[];
  total_entries: number;
  total_amount: string;
  total_pending: string;
  total_paid: string;
  period_start: string;
  period_end: string;
}
```

### Exemplo de Componente

```tsx
// src/app/patients/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Patient } from '@/types';

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.patients.list()
      .then(data => setPatients(data.patients))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    const patient = await api.patients.create({
      name: 'Novo Paciente',
      email: 'novo@email.com',
    });
    setPatients([...patients, patient]);
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h1>Pacientes</h1>
      <button onClick={handleCreate}>Novo Paciente</button>
      <ul>
        {patients.map(p => (
          <li key={p.id}>{p.name} - {p.email}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Fluxo Principal da Aplicação

```
1. CADASTRAR PACIENTE
   POST /patients
   └─> Paciente criado

2. AGENDAR SESSÃO
   POST /sessions
   └─> Sessão com status "agendada"

3. REALIZAR SESSÃO (concluir)
   PATCH /sessions/{id}/status {"new_status": "concluida"}
   └─> Sessão "concluida"
   └─> Lançamento financeiro "pendente" criado automaticamente

4. REGISTRAR PAGAMENTO
   (futuro endpoint ou direto no banco)
   └─> Lançamento marcado como "pago"

5. GERAR RELATÓRIO
   GET /financial/entries?start_date=...&end_date=...
   └─> Lista de lançamentos com totais
```

---

## Variáveis de Ambiente (Frontend)

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Checklist para o Frontend

- [ ] Configurar cliente HTTP (fetch/axios)
- [ ] Criar tipos TypeScript baseados neste documento
- [ ] Implementar tratamento de erros
- [ ] Páginas:
  - [ ] Lista de pacientes
  - [ ] Cadastro de paciente
  - [ ] Agenda (sessões do dia/semana)
  - [ ] Concluir/Cancelar sessão
  - [ ] Relatório financeiro
- [ ] Componentes:
  - [ ] Formulário de paciente
  - [ ] Formulário de sessão
  - [ ] Card de sessão (com ações)
  - [ ] Tabela de lançamentos
  - [ ] Resumo financeiro (totais)

---

## Sugestão de Stack Frontend

- **Framework:** Next.js 14+ (App Router)
- **Styling:** Tailwind CSS
- **Componentes:** shadcn/ui
- **Ícones:** Lucide React
- **Formulários:** React Hook Form + Zod
- **Data Fetching:** TanStack Query (React Query)
- **Datas:** date-fns

---

## Contato

- **Swagger UI:** http://localhost:8000/docs
- **Backend rodando:** `uvicorn app.main:app --reload`
