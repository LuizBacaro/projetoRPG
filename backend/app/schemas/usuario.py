"""
Schemas Pydantic de Usuário
SRP: validação e serialização de dados de usuário
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from ..models.usuario import PerfilUsuario


# ── Base ──────────────────────────────────────────────────────────────────────

class UsuarioBase(BaseModel):
    perfil: PerfilUsuario
    nome:   str
    email:  EmailStr

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()


# ── Criação ───────────────────────────────────────────────────────────────────

class UsuarioCreate(UsuarioBase):
    senha: str  # senha em texto puro — será hasheada no service

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
    email:  Optional[EmailStr]      = None
    senha:  Optional[str]           = None
    ativo:  Optional[bool]          = None

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
    usuario_responsavel: Optional[str]   = None
    data_acao:           Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Lista ─────────────────────────────────────────────────────────────────────

class UsuarioListResponse(BaseModel):
    total:    int
    usuarios: list[UsuarioResponse]