"""Utilitários para criação e validação de tokens JWT."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

# Configurações JWT
SECRET_KEY: str = settings.secret_key
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT de acesso.

    Args:
        data: Dados a serem codificados no token (ex: {"sub": user_id}).
        expires_delta: Tempo de expiração do token. Se None, usa padrão.

    Returns:
        Token JWT codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica e valida um token JWT.

    Args:
        token: Token JWT a ser decodificado.

    Returns:
        Payload do token se válido, None caso contrário.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Optional[str]:
    """Verifica um token e retorna o user_id.

    Args:
        token: Token JWT a ser verificado.

    Returns:
        user_id se token válido, None caso contrário.
    """
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload.get("sub")
