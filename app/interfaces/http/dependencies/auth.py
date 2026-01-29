"""Dependencies de autenticação para FastAPI."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth.jwt_handler import verify_token
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.interfaces.http.dependencies import get_db_session  # noqa: F401
from app.infra.repositories.user_repository_impl import SqlAlchemyUserRepository

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session=Depends(get_db_session),
) -> User:
    """Obtém o usuário atual a partir do token JWT.

    Args:
        credentials: Credenciais HTTP Bearer (token JWT).
        session: Sessão do banco de dados.

    Returns:
        Entidade User do usuário autenticado.

    Raises:
        HTTPException: Se token inválido ou usuário não encontrado.
    """
    token = credentials.credentials
    
    # Verificar token
    user_id_str = verify_token(token)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuário
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_repo: UserRepository = SqlAlchemyUserRepository(session)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    return user


# Type alias para uso nos routers
CurrentUser = Annotated[User, Depends(get_current_user)]
