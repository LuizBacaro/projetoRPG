"""
Schemas Pydantic de Usuário
SRP: validação e serialização de dados de usuário
"""

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..models.usuario import PerfilUsuario


class UsuarioBase(BaseModel):
    perfil: PerfilUsuario = Field(
        ...,
        description=(
            "Perfil da conta. Novos cadastros públicos são sempre jogador. "
            "Mestre de mesa: criar campanha no jogo (ADR 0005). "
            "Valor mestre aqui é legado/admin."
        ),
    )
    nome: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=150)

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


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=128)
    ativo: bool = True

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        return v


class UsuarioUpdate(BaseModel):
    perfil: Optional[PerfilUsuario] = None
    nome: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=3, max_length=150)
    senha: Optional[str] = Field(default=None, min_length=6, max_length=128)
    ativo: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(padrao, v):
            raise ValueError("E-mail inválido")
        return v.lower().strip()

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        return v


class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool
    usuario_responsavel: Optional[str] = None
    data_acao: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UsuarioListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    usuarios: list[UsuarioResponse]
