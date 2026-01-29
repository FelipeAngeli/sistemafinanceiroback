"""Schemas Pydantic para autenticação."""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema para registro de usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., min_length=6, description="Senha (mínimo 6 caracteres)")
    name: str = Field(..., min_length=2, max_length=255, description="Nome do usuário")


class UserLogin(BaseModel):
    """Schema para login de usuário."""

    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class TokenResponse(BaseModel):
    """Schema de resposta de token."""

    access_token: str = Field(..., description="Token JWT de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    user_id: str = Field(..., description="ID do usuário")
    user_email: str = Field(..., description="Email do usuário")
    user_name: str = Field(..., description="Nome do usuário")


class UserResponse(BaseModel):
    """Schema de resposta de usuário."""

    id: str = Field(..., description="ID do usuário")
    email: str = Field(..., description="Email do usuário")
    name: str = Field(..., description="Nome do usuário")
