"""Router para endpoints de Sessões."""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status
from app.interfaces.http.dependencies import (
    CreateSessionUC,
    ListSessionsUC,
    UpdateSessionStatusUC,
    UpdateSessionUC,
    GetSessionByIdUC,
)
from app.interfaces.http.schemas.session_schemas import (
    SessionCreate,
    SessionListItem,
    SessionListResponse,
    SessionResponse,
    SessionStatusUpdate,
    SessionStatusResponse,
    SessionUpdate,
)
from app.use_cases.session.schedule_session import CreateSessionInput
from app.use_cases.session.list_sessions import ListSessionsInput
from app.use_cases.session.get_session_by_id import GetSessionByIdInput
from app.use_cases.session.update_session_status import UpdateSessionStatusInput
from app.use_cases.session.update_session import UpdateSessionInput

router = APIRouter(prefix="/sessions", tags=["Sessões"])


@router.get(
    "",
    response_model=SessionListResponse,
    summary="Listar sessões",
    description="Lista sessões com filtros opcionais por paciente, status e período.",
)
async def list_sessions(
    use_case: ListSessionsUC,
    patient_id: Optional[UUID] = Query(None, description="Filtrar por paciente"),
    status: Optional[str] = Query(
        None,
        description="Filtrar por status",
        pattern="^(agendada|concluida|cancelada)$",
    ),
    start_date: Optional[date] = Query(None, description="Data inicial"),
    end_date: Optional[date] = Query(None, description="Data final"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
) -> SessionListResponse:
    """Lista sessões com filtros opcionais."""
    input_data = ListSessionsInput(
        patient_id=patient_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    output = await use_case.execute(input_data)
    return SessionListResponse(
        sessions=[
            SessionListItem(
                id=s.id,
                patient_id=s.patient_id,
                date_time=s.date_time,
                price=s.price,
                duration_minutes=s.duration_minutes,
                status=s.status,
                notes=s.notes,
            )
            for s in output.sessions
        ],
        total=output.total,
    )


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar sessão",
    description="Cria uma nova sessão de atendimento para um paciente.",
)
async def create_session(
    data: SessionCreate,
    use_case: CreateSessionUC,
) -> SessionResponse:
    """Cria uma nova sessão.
    
    Exceções são tratadas pelos handlers globais.
    """
    input_data = CreateSessionInput(
        patient_id=data.patient_id,
        date_time=data.date_time,
        price=data.price,
        duration_minutes=data.duration_minutes,
        notes=data.notes,
    )
    output = await use_case.execute(input_data)
    return SessionResponse(
        id=output.id,
        patient_id=output.patient_id,
        date_time=output.date_time,
        price=output.price,
        duration_minutes=output.duration_minutes,
        status=output.status,
        notes=output.notes,
        created_at=output.created_at,
        updated_at=output.updated_at,
    )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Buscar sessão por ID",
    description=(
        "Retorna os detalhes completos de uma sessão específica, incluindo informações "
        "sobre o paciente, data/hora, valor, status e observações."
    ),
    responses={
        200: {
            "description": "Sessão encontrada e retornada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                        "date_time": "2024-12-15T14:00:00",
                        "price": 200.00,
                        "duration_minutes": 50,
                        "status": "agendada",
                        "notes": "Primeira sessão de terapia cognitiva",
                        "created_at": "2024-12-01T10:30:00",
                        "updated_at": "2024-12-10T15:45:00"
                    }
                }
            }
        },
        404: {
            "description": "Sessão não encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session with id '123e4567-e89b-12d3-a456-426614174000' not found"
                    }
                }
            }
        },
        422: {
            "description": "ID inválido fornecido",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "uuid_parsing",
                                "loc": ["path", "session_id"],
                                "msg": "Input should be a valid UUID",
                                "input": "invalid-uuid"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_session(
    session_id: UUID,
    use_case: GetSessionByIdUC,
) -> SessionResponse:
    """Busca uma sessão específica pelo seu ID único.
    
    **Parâmetros:**
    - `session_id`: UUID da sessão a ser buscada
    
    **Retorna:**
    - Objeto SessionResponse com todos os detalhes da sessão
    
    **Erros:**
    - `404`: Sessão não encontrada
    - `422`: ID inválido (não é um UUID válido)
    """
    input_data = GetSessionByIdInput(session_id=session_id)
    output = await use_case.execute(input_data)
    
    return SessionResponse(
        id=output.id,
        patient_id=output.patient_id,
        date_time=output.date_time,
        price=output.price,
        duration_minutes=output.duration_minutes,
        status=output.status,
        notes=output.notes,
        created_at=output.created_at,
        updated_at=output.updated_at,
    )


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Atualizar dados da sessão",
    description=(
        "Atualiza dados de uma sessão existente. Suporta atualização parcial - "
        "apenas os campos enviados serão atualizados. "
        "**Nota:** O status da sessão não pode ser atualizado por este endpoint, "
        "use PATCH /sessions/{id}/status para alterar o status."
    ),
    responses={
        200: {
            "description": "Sessão atualizada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "patient_id": "987fcdeb-51a2-43d7-9876-543210fedcba",
                        "date_time": "2024-12-20T15:00:00",
                        "price": 250.00,
                        "duration_minutes": 50,
                        "status": "agendada",
                        "notes": "Sessão remarcada - ajuste de horário",
                        "created_at": "2024-12-01T10:30:00",
                        "updated_at": "2024-12-15T09:20:00"
                    }
                }
            }
        },
        404: {
            "description": "Sessão não encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session with id '123e4567-e89b-12d3-a456-426614174000' not found"
                    }
                }
            }
        },
        422: {
            "description": "Erro de validação - dados inválidos ou patient_id inexistente",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_uuid": {
                            "summary": "UUID inválido no path",
                            "value": {
                                "detail": [
                                    {
                                        "type": "uuid_parsing",
                                        "loc": ["path", "session_id"],
                                        "msg": "Input should be a valid UUID",
                                        "input": "invalid-uuid"
                                    }
                                ]
                            }
                        },
                        "invalid_patient": {
                            "summary": "Patient ID não existe",
                            "value": {
                                "detail": "Patient with id '987fcdeb-51a2-43d7-9876-543210fedcba' not found"
                            }
                        },
                        "invalid_price": {
                            "summary": "Preço negativo",
                            "value": {
                                "detail": [
                                    {
                                        "type": "greater_than_equal",
                                        "loc": ["body", "price"],
                                        "msg": "Input should be greater than or equal to 0"
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
async def update_session(
    session_id: UUID,
    data: SessionUpdate,
    use_case: UpdateSessionUC,
) -> SessionResponse:
    """Atualiza dados de uma sessão existente (atualização parcial).
    
    **Parâmetros:**
    - `session_id`: UUID da sessão a ser atualizada
    - `data`: Dados para atualização (todos os campos são opcionais)
      - `patient_id`: Transferir sessão para outro paciente
      - `date_time`: Nova data e hora
      - `price`: Novo valor
      - `notes`: Atualizar observações
    
    **Retorna:**
    - Objeto SessionResponse com todos os dados atualizados
    
    **Erros:**
    - `404`: Sessão não encontrada
    - `422`: Dados inválidos (patient_id inexistente, preço negativo, etc.)
    
    **Importante:**
    - Este endpoint NÃO atualiza o status da sessão
    - Para alterar o status, use o endpoint PATCH /sessions/{id}/status
    """
    input_data = UpdateSessionInput(
        session_id=session_id,
        patient_id=data.patient_id,
        date_time=data.date_time,
        price=data.price,
        notes=data.notes,
    )
    output = await use_case.execute(input_data)
    
    return SessionResponse(
        id=output.id,
        patient_id=output.patient_id,
        date_time=output.date_time,
        price=output.price,
        duration_minutes=output.duration_minutes,
        status=output.status,
        notes=output.notes,
        created_at=output.created_at,
        updated_at=output.updated_at,
    )


@router.patch(
    "/{session_id}/status",
    response_model=SessionStatusResponse,
    summary="Atualizar status da sessão",
    description=(
        "Atualiza o status de uma sessão. "
        "Quando concluída, cria automaticamente um lançamento financeiro pendente."
    ),
)
async def update_session_status(
    session_id: UUID,
    data: SessionStatusUpdate,
    use_case: UpdateSessionStatusUC,
) -> SessionStatusResponse:
    """Atualiza o status de uma sessão.
    
    Exceções são tratadas pelos handlers globais.
    """
    input_data = UpdateSessionStatusInput(
        session_id=session_id,
        new_status=data.new_status,
        notes=data.notes,
    )
    output = await use_case.execute(input_data)
    return SessionStatusResponse(
        session_id=output.session_id,
        previous_status=output.previous_status,
        new_status=output.new_status,
        financial_entry_created=output.financial_entry_id is not None,
        financial_entry_id=output.financial_entry_id,
        financial_entry_amount=output.financial_entry_amount,
    )
