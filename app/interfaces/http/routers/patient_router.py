"""Router para endpoints de Pacientes."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from app.interfaces.http.dependencies import (
    CreatePatientUC,
    ListPatientsUC,
    PatientRepo,
)
from app.interfaces.http.schemas.patient_schemas import (
    PatientCreate,
    PatientResponse,
    PatientListResponse,
)
from app.use_cases.patient.create_patient import CreatePatientInput
from app.use_cases.patient.list_patients import ListPatientsInput

router = APIRouter(prefix="/patients", tags=["Pacientes"])


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
