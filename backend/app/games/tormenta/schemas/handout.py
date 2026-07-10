"""Schemas — handouts de campanha Tormenta 20 (RF-T12f)."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TormentaHandoutBase(BaseModel):
    campanha_id: int = Field(..., ge=1)
    titulo: str = Field(..., min_length=1, max_length=200)
    corpo_md: str = Field(default="", max_length=8000)
    imagem_url: str | None = Field(default=None, max_length=2048)
    visivel_para_user_ids: List[int] = Field(default_factory=list)

    @field_validator("titulo", mode="before")
    @classmethod
    def validar_titulo(cls, value):
        texto = str(value or "").strip()
        if not texto:
            raise ValueError("Titulo do handout e obrigatorio")
        return texto

    @field_validator("corpo_md", mode="before")
    @classmethod
    def validar_corpo(cls, value):
        return str(value or "").strip()

    @field_validator("imagem_url", mode="before")
    @classmethod
    def validar_imagem(cls, value):
        if value is None:
            return None
        texto = str(value).strip()
        return texto or None

    @field_validator("visivel_para_user_ids", mode="before")
    @classmethod
    def validar_visiveis(cls, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError(
                "visivel_para_user_ids deve ser uma lista de IDs de usuario"
            )
        out = []
        for item in value:
            try:
                uid = int(item)
            except (TypeError, ValueError):
                continue
            if uid > 0 and uid not in out:
                out.append(uid)
        return out


class TormentaHandoutCreate(TormentaHandoutBase):
    pass


class TormentaHandoutUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    corpo_md: str | None = Field(default=None, max_length=8000)
    imagem_url: str | None = Field(default=None, max_length=2048)
    visivel_para_user_ids: List[int] | None = None

    @field_validator("titulo", mode="before")
    @classmethod
    def validar_titulo(cls, value):
        if value is None:
            return value
        texto = str(value).strip()
        if not texto:
            raise ValueError("Titulo do handout nao pode ser vazio")
        return texto

    @field_validator("corpo_md", mode="before")
    @classmethod
    def validar_corpo(cls, value):
        if value is None:
            return value
        return str(value).strip()

    @field_validator("imagem_url", mode="before")
    @classmethod
    def validar_imagem(cls, value):
        if value is None:
            return value
        texto = str(value).strip()
        return texto or None

    @field_validator("visivel_para_user_ids", mode="before")
    @classmethod
    def validar_visiveis(cls, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise ValueError(
                "visivel_para_user_ids deve ser uma lista de IDs de usuario"
            )
        out = []
        for item in value:
            try:
                uid = int(item)
            except (TypeError, ValueError):
                continue
            if uid > 0 and uid not in out:
                out.append(uid)
        return out


class TormentaHandoutResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campanha_id: int
    campanha_nome: str = ""
    titulo: str
    corpo_md: str = ""
    imagem_url: str | None = None
    visivel_para_user_ids: List[int] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
