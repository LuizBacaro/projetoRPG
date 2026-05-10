"""
Schemas de Autenticação
SRP: validação dos dados de login, registro e resposta do token
"""

import re

from pydantic import BaseModel, field_validator

from .usuario import UsuarioResponse


class LoginRequest(BaseModel):
    email: str
    senha: str


class RegistroRequest(BaseModel):
    """Schema para auto-cadastro público — perfil Jogador por padrão."""

    nome: str
    email: str
    senha: str

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str) -> str:
        padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(padrao, v):
            raise ValueError("E-mail inválido")
        return v.lower().strip()

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
