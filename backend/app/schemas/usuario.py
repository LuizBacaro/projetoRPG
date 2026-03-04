"""
Schemas Pydantic de Usuário
SRP: validação e serialização de dados de usuário
"""
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from ..models.usuario import PerfilUsuario
import re


# ── Base ──────────────────────────────────────────────────────────────────────

class UsuarioBase(BaseModel):
    perfil: PerfilUsuario
    nome:   str
    email:  str

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: str) -> str:
        padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(padrao, v):
            raise ValueError("E-mail inválido")
        return v.lower().strip()


# ── Criação ───────────────────────────────────────────────────────────────────

class UsuarioCreate(UsuarioBase):
    senha: str
    ativo: bool = True

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        return v


# ── Atualização ───────────────────────────────────────────────────────────────

class UsuarioUpdate(BaseModel):
    perfil: Optional[PerfilUsuario] = None
    nome:   Optional[str]           = None
    email:  Optional[str]           = None
    senha:  Optional[str]           = None
    ativo:  Optional[bool]          = None

    @field_validator("email")
    @classmethod
    def email_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        padrao = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(padrao, v):
            raise ValueError("E-mail inválido")
        return v.lower().strip()

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        return v


# ── Resposta ──────────────────────────────────────────────────────────────────

class UsuarioResponse(UsuarioBase):
    id:                  int
    ativo:               bool
    usuario_responsavel: Optional[str]      = None
    data_acao:           Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Lista ─────────────────────────────────────────────────────────────────────

class UsuarioListResponse(BaseModel):
    total:    int
    usuarios: list[UsuarioResponse]