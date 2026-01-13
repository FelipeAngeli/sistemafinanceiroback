# Decisão: GET /dashboard/metrics

## 📋 Decisão Tomada

**OPÇÃO 1: REMOVER** ✅

O endpoint `GET /dashboard/metrics` **NÃO será implementado** no backend.

---

## 🎯 Justificativa

### 1. **Código Não Utilizado**
- O endpoint está definido no frontend mas nunca é chamado
- Manter código morto aumenta complexidade sem benefício
- Viola o princípio YAGNI (You Aren't Gonna Need It)

### 2. **Funcionalidade Já Coberta**
- O endpoint `GET /dashboard/summary` já fornece todos os dados necessários:
  - Relatório financeiro completo
  - Sessões de hoje
  - Sessões recentes
  - Resumo de pacientes
- Métricas podem ser calculadas no frontend a partir desses dados

### 3. **Flexibilidade**
- Cálculos de métricas no frontend são mais flexíveis
- Permite diferentes visualizações sem mudanças no backend
- Reduz carga no servidor

### 4. **Manutenibilidade**
- Menos código = menos bugs potenciais
- Menos endpoints = menos testes necessários
- Código mais limpo e fácil de manter

---

## 📝 Ação Necessária no Frontend

### Remover a definição de `ApiEndpoints.dashboardMetrics`

**Arquivo:** `lib/api/api_endpoints.dart` (ou similar)

**Antes:**
```dart
class ApiEndpoints {
  static const String baseUrl = 'http://localhost:8000';
  
  // Dashboard
  static const String dashboardSummary = '/dashboard/summary';
  static const String dashboardMetrics = '/dashboard/metrics'; // ❌ REMOVER ESTA LINHA
  
  // ... outros endpoints
}
```

**Depois:**
```dart
class ApiEndpoints {
  static const String baseUrl = 'http://localhost:8000';
  
  // Dashboard
  static const String dashboardSummary = '/dashboard/summary';
  // dashboardMetrics removido - não utilizado
  
  // ... outros endpoints
}
```

---

## 🔄 Alternativa: Calcular Métricas no Frontend

Se você precisar de métricas específicas, calcule-as no frontend usando os dados de `GET /dashboard/summary`:

### Exemplo de Métricas que Podem Ser Calculadas:

```dart
// Exemplo em Dart/Flutter
class DashboardMetrics {
  final DashboardSummaryResponse summary;
  
  DashboardMetrics(this.summary);
  
  // Taxa de comparecimento
  double get attendanceRate {
    final totalSessions = summary.recentSessions.length;
    final completedSessions = summary.recentSessions
        .where((s) => s.status == 'concluida')
        .length;
    return totalSessions > 0 ? completedSessions / totalSessions : 0.0;
  }
  
  // Média de receita por paciente
  double get averageRevenuePerPatient {
    final totalPatients = summary.patientsSummary.totalPatients;
    final totalRevenue = summary.financialReport.totalRevenue;
    return totalPatients > 0 ? totalRevenue / totalPatients : 0.0;
  }
  
  // Crescimento mensal (comparar períodos)
  double calculateMonthlyGrowth(DashboardSummaryResponse previousMonth) {
    final currentRevenue = summary.financialReport.totalRevenue;
    final previousRevenue = previousMonth.financialReport.totalRevenue;
    if (previousRevenue == 0) return 0.0;
    return ((currentRevenue - previousRevenue) / previousRevenue) * 100;
  }
}
```

---

## 📊 Endpoints Disponíveis no Backend

### Dashboard

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/dashboard/summary` | Resumo consolidado com todos os dados necessários |

**Query Parameters:**
- `start_date` (obrigatório): Data inicial do período (YYYY-MM-DD)
- `end_date` (obrigatório): Data final do período (YYYY-MM-DD)

**Resposta:**
```json
{
  "financial_report": {
    "total_revenue": 5000.00,
    "total_paid": 3000.00,
    "total_pending": 2000.00,
    "entries": [...],
    "period_start": "2024-01-01",
    "period_end": "2024-01-31"
  },
  "today_sessions": [...],
  "recent_sessions": [...],
  "patients_summary": {
    "total_patients": 25,
    "active_patients": 20,
    "inactive_patients": 5
  }
}
```

---

## 🔮 Se Precisar Implementar no Futuro

Se no futuro você realmente precisar de métricas específicas que não podem ser calculadas no frontend (ex: análises complexas, agregações pesadas), você pode:

1. **Adicionar ao endpoint existente:**
   - Expandir `GET /dashboard/summary` para incluir métricas calculadas

2. **Criar endpoint específico:**
   - Implementar `GET /dashboard/metrics` com métricas específicas
   - Seguir o mesmo padrão dos outros endpoints

3. **Usar query parameters:**
   - Adicionar `?include_metrics=true` ao endpoint summary

---

## ✅ Checklist de Ação

- [ ] Remover `dashboardMetrics` de `ApiEndpoints` no frontend
- [ ] Remover qualquer referência ao endpoint no código frontend
- [ ] Verificar se há testes que referenciam este endpoint e removê-los
- [ ] Atualizar documentação do frontend se necessário
- [ ] Confirmar que `GET /dashboard/summary` atende todas as necessidades

---

## 📚 Documentação Relacionada

- [Validação Dashboard Summary](./VALIDATION_DASHBOARD_SUMMARY.md)
- [API Endpoints](./API_ENDPOINTS.md)
- [Frontend Integration](./FRONTEND_INTEGRATION.md)

---

**Data da Decisão:** 2024-12-XX  
**Status:** ✅ Implementado - Endpoint não será criado no backend
