"""Router para endpoints de Sessões."""

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Query, status
from app.interfaces.http.dependencies import CreateSessionUC, ListSessionsUC, GetSessionByIdUC, UpdateSessionStatusUC
from app.interfaces.http.schemas.session_schemas import (
    SessionCreate,
    SessionListItem,
    SessionListResponse,
    SessionResponse,
    SessionStatusUpdate,
    SessionStatusResponse,
)
from app.use_cases.session.schedule_session import CreateSessionInput
from app.use_cases.session.list_sessions import ListSessionsInput
from app.use_cases.session.get_session_by_id import GetSessionByIdInput
from app.use_cases.session.update_session_status import UpdateSessionStatusInput

router = APIRouter(prefix="/sessions", tags=["Sessões"])


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Buscar sessão por ID",
    description="Busca uma sessão específica pelo seu ID.",
)
async def get_session_by_id(
    session_id: UUID,
    use_case: GetSessionByIdUC,
) -> SessionResponse:
    """Busca uma sessão por ID.
    
    Validações:
    - ID deve ser um UUID válido (validado automaticamente pelo FastAPI)
    - Sessão deve existir no banco de dados
    - Retorna 404 se sessão não encontrada
    
    Nota: Autenticação e verificação de permissões devem ser adicionadas
    quando o sistema de autenticação for implementado.
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
    )


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
