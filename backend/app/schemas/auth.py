"""
Schemas de Autenticação
SRP: validação dos dados de login e resposta do token
"""
from pydantic import BaseModel
from .usuario import UsuarioResponse


class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    usuario:      UsuarioResponse