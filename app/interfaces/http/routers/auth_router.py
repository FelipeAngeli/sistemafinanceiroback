"""Router para endpoints de Autenticação."""

from fastapi import APIRouter, status

from app.interfaces.http.dependencies import RegisterUserUC, LoginUserUC
from app.interfaces.http.schemas.auth_schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from app.use_cases.auth.register_user import RegisterUserInput
from app.use_cases.auth.login_user import LoginUserInput

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuário",
    description="Cria um novo usuário no sistema.",
)
async def register_user(
    data: UserRegister,
    use_case: RegisterUserUC,
) -> UserResponse:
    """Registra um novo usuário no sistema.
    
    **Validações:**
    - Email deve ser único
    - Senha deve ter no mínimo 6 caracteres
    - Nome deve ter entre 2 e 255 caracteres
    
    **Retorna:**
    - Dados do usuário criado (sem senha)
    """
    input_data = RegisterUserInput(
        email=data.email,
        password=data.password,
        name=data.name,
    )
    output = await use_case.execute(input_data)
    return UserResponse(
        id=str(output.id),
        email=output.email,
        name=output.name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuário",
    description="Autentica um usuário e retorna token JWT.",
)
async def login_user(
    data: UserLogin,
    use_case: LoginUserUC,
) -> TokenResponse:
    """Autentica um usuário e retorna token JWT.
    
    **Validações:**
    - Email e senha devem ser válidos
    - Usuário deve estar ativo
    
    **Retorna:**
    - Token JWT de acesso
    - Dados do usuário autenticado
    
    **Uso do token:**
    Incluir no header das requisições:
    ```
    Authorization: Bearer <token>
    ```
    """
    input_data = LoginUserInput(
        email=data.email,
        password=data.password,
    )
    output = await use_case.execute(input_data)
    return TokenResponse(
        access_token=output.access_token,
        token_type=output.token_type,
        user_id=output.user_id,
        user_email=output.user_email,
        user_name=output.user_name,
    )
