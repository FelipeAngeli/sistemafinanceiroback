"""Router para endpoints de Pacientes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from app.interfaces.http.dependencies import (
    CreatePatientUC,
    ListPatientsUC,
    GetPatientSummaryUC,
    PatientRepo,
)
from app.interfaces.http.schemas.patient_schemas import (
    PatientCreate,
    PatientResponse,
    PatientListResponse,
    PatientSummaryResponse,
)
from app.use_cases.patient.create_patient import CreatePatientInput
from app.use_cases.patient.list_patients import ListPatientsInput

router = APIRouter(prefix="/patients", tags=["Pacientes"])


@router.get(
    "/summary",
    response_model=PatientSummaryResponse,
    summary="Resumo de pacientes",
    description=(
        "Retorna estatísticas gerais e agregadas dos pacientes cadastrados no sistema:\n\n"
        "- Total de pacientes cadastrados\n"
        "- Quantidade de pacientes ativos\n"
        "- Quantidade de pacientes inativos\n"
        "- Percentual de pacientes ativos\n\n"
        "Este endpoint utiliza query SQL otimizada com agregação (COUNT) para performance, "
        "evitando carregar todos os registros em memória."
    ),
    responses={
        200: {
            "description": "Estatísticas de pacientes retornadas com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "total": 25,
                        "active": 22,
                        "inactive": 3,
                        "percentage_active": 88.0
                    }
                }
            }
        }
    }
)
async def get_patient_summary(
    use_case: GetPatientSummaryUC,
) -> PatientSummaryResponse:
    """Retorna estatísticas agregadas dos pacientes.
    
    **Retorna:**
    - Objeto PatientSummaryResponse contendo:
      - `total`: Número total de pacientes cadastrados
      - `active`: Quantidade de pacientes ativos
      - `inactive`: Quantidade de pacientes inativos
      - `percentage_active`: Percentual de pacientes ativos (0-100)
    
    **Exemplo de uso:**
    ```
    GET /patients/summary
    ```
    
    **Performance:**
    Este endpoint utiliza query SQL otimizada com agregação COUNT/SUM 
    para calcular as estatísticas diretamente no banco de dados, 
    garantindo resposta rápida independente do volume de registros.
    
    **Nota:**
    Não requer parâmetros - retorna estatísticas de todos os pacientes.
    """
    output = await use_case.execute()
    return PatientSummaryResponse(
        total=output.total,
        active=output.active,
        inactive=output.inactive,
        percentage_active=output.percentage_active,
    )


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar paciente",
    description="Cria um novo paciente no sistema.",
)
async def create_patient(
    data: PatientCreate,
    use_case: CreatePatientUC,
) -> PatientResponse:
    """Cria um novo paciente.
    
    Exceções são tratadas pelos handlers globais.
    """
    input_data = CreatePatientInput(
        name=data.name,
        email=data.email,
        phone=data.phone,
        notes=data.notes,
    )
    output = await use_case.execute(input_data)
    return PatientResponse(
        id=output.id,
        name=output.name,
        email=output.email,
        phone=output.phone,
        active=output.active,
    )


@router.get(
    "",
    response_model=PatientListResponse,
    summary="Listar pacientes",
    description="Lista todos os pacientes cadastrados.",
)
async def list_patients(
    use_case: ListPatientsUC,
    active_only: bool = True,
) -> PatientListResponse:
    """Lista todos os pacientes."""
    input_data = ListPatientsInput(active_only=active_only)
    output = await use_case.execute(input_data)
    return PatientListResponse(
        patients=[
            PatientResponse(
                id=p.id,
                name=p.name,
                email=p.email,
                phone=p.phone,
                active=p.active,
            )
            for p in output.patients
        ],
        total=output.total,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Buscar paciente",
    description="Busca um paciente pelo ID.",
)
async def get_patient(
    patient_id: UUID,
    patient_repo: PatientRepo,
) -> PatientResponse:
    """Busca um paciente por ID."""
    patient = await patient_repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paciente com id '{patient_id}' não encontrado.",
        )
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        email=patient.email,
        phone=patient.phone,
        active=patient.active,
    )
