"""Router para endpoints do Dashboard."""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.interfaces.http.dependencies import GetDashboardSummaryUC
from app.interfaces.http.schemas.dashboard_schemas import DashboardSummaryResponse
from app.use_cases.dashboard.get_dashboard_summary import GetDashboardSummaryInput

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Resumo do Dashboard",
    description=(
        "Retorna dados agregados e estatísticas completas para o dashboard, incluindo:\n\n"
        "- **Financeiro**: Total recebido, pendente e contadores de lançamentos\n"
        "- **Sessões**: Agendadas para hoje, recentes e total do período\n"
        "- **Pacientes**: Total cadastrado, ativos e inativos\n\n"
        "Este endpoint utiliza queries otimizadas com agregações SQL para performance."
    ),
    responses={
        200: {
            "description": "Resumo do dashboard retornado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "financial": {
                            "total_received": 5000.00,
                            "total_pending": 2400.00,
                            "total_entries": 15,
                            "pending_count": 5,
                            "entries": []
                        },
                        "sessions": {
                            "today": [
                                {
                                    "id": "123e4567-e89b-12d3-a456-426614174000",
                                    "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                                    "patient_name": "Maria Silva",
                                    "date_time": "2024-12-15T14:00:00",
                                    "price": 200.00,
                                    "status": "realizada"
                                }
                            ],
                            "recent": [
                                {
                                    "id": "456e7890-a12b-34c5-d678-901234567890",
                                    "patient_id": "321fedcb-a987-65d4-c321-ba0987654321",
                                    "patient_name": "João Santos",
                                    "date_time": "2024-12-14T15:00:00",
                                    "price": 200.00,
                                    "status": "realizada"
                                }
                            ],
                            "total_month": 25
                        },
                        "patients": {
                            "total": 30,
                            "active": 28,
                            "inactive": 2
                        },
                        "period": {
                            "start": "2024-12-01",
                            "end": "2024-12-31"
                        }
                    }
                }
            }
        },
        422: {
            "description": "Parâmetros de data inválidos",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_dates": {
                            "summary": "Datas obrigatórias não fornecidas",
                            "value": {
                                "detail": [
                                    {
                                        "type": "missing",
                                        "loc": ["query", "start_date"],
                                        "msg": "Field required"
                                    }
                                ]
                            }
                        },
                        "invalid_date_format": {
                            "summary": "Formato de data inválido",
                            "value": {
                                "detail": [
                                    {
                                        "type": "date_parsing",
                                        "loc": ["query", "start_date"],
                                        "msg": "Input should be a valid date",
                                        "input": "invalid-date"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_dashboard_summary(
    use_case: GetDashboardSummaryUC,
    start_date: date = Query(..., description="Data inicial do período (formato: YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data final do período (formato: YYYY-MM-DD)"),
) -> DashboardSummaryResponse:
    """Busca resumo agregado do dashboard para o período especificado.
    
    **Parâmetros de Query:**
    - `start_date`: Data inicial do período (obrigatório, formato: YYYY-MM-DD)
    - `end_date`: Data final do período (obrigatório, formato: YYYY-MM-DD)
    
    **Retorna:**
    - Objeto DashboardSummaryResponse com estatísticas completas:
      - Dados financeiros do período
      - Sessões de hoje e recentes
      - Estatísticas de pacientes
    
    **Erros:**
    - `422`: Datas inválidas ou não fornecidas
    
    **Exemplo de uso:**
    ```
    GET /dashboard/summary?start_date=2024-12-01&end_date=2024-12-31
    ```
    
    **Performance:**
    Este endpoint utiliza queries SQL otimizadas com agregações (SUM, COUNT) 
    e JOINs eficientes para garantir resposta rápida mesmo com grandes volumes de dados.
    """
    input_data = GetDashboardSummaryInput(
        start_date=start_date,
        end_date=end_date,
    )
    return await use_case.execute(input_data)
