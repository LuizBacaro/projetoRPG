"""Schemas Pydantic — ficha D&D 5e."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

DND5E_FICHA_MAX_JSON_BYTES = 65_536
DND5E_FICHA_FORMAT_VERSION = 2


def validar_ficha_json_serializavel_e_tamanho(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("ficha deve ser um objeto JSON (dicionário)")
    try:
        raw = json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValueError("ficha contém valores não serializáveis em JSON") from e
    if len(raw.encode("utf-8")) > DND5E_FICHA_MAX_JSON_BYTES:
        raise ValueError(
            f"ficha excede {DND5E_FICHA_MAX_JSON_BYTES} bytes após serialização UTF-8"
        )
    return data


def normalizar_ficha_para_gravacao(data: Dict[str, Any]) -> Dict[str, Any]:
    from app.games.dnd5e.rules.progressao import migrar_ficha_para_v2

    return migrar_ficha_para_v2(data)


def ficha_json_para_resposta(raw: Any) -> Dict[str, Any]:
    """Normaliza leitura de JSON da coluna (SQLite pode devolver str)."""
    if raw is None:
        return {}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            return {}
        data = parsed if isinstance(parsed, dict) else {}
    else:
        data = raw if isinstance(raw, dict) else {}
    from app.games.dnd5e.rules.progressao import migrar_ficha_para_v2

    return migrar_ficha_para_v2(data)


class Dnd5ePersonagemBase(BaseModel):
    tipo: str = Field(default="jogador", max_length=20)
    nome: str = Field(..., max_length=120)
    jogador_nome: Optional[str] = Field(None, max_length=120)
    nivel: int = Field(default=1, ge=1, le=20)
    experiencia: int = Field(default=0, ge=0)
    strength: int = Field(default=10, ge=1, le=25)
    dexterity: int = Field(default=10, ge=1, le=25)
    constitution: int = Field(default=10, ge=1, le=25)
    intelligence: int = Field(default=10, ge=1, le=25)
    wisdom: int = Field(default=10, ge=1, le=25)
    charisma: int = Field(default=10, ge=1, le=25)
    hp_max: int = Field(default=0, ge=0)
    hp_atual: Optional[int] = Field(None, ge=0)


class Dnd5ePersonagemCreate(Dnd5ePersonagemBase):
    ficha: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("ficha")
    @classmethod
    def _ficha_validar_create(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        return validar_ficha_json_serializavel_e_tamanho(v)


class Dnd5ePersonagemUpdate(BaseModel):
    tipo: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, max_length=120)
    jogador_nome: Optional[str] = Field(None, max_length=120)
    foto_url: Optional[str] = Field(None, max_length=2048)
    nivel: Optional[int] = Field(None, ge=1, le=20)
    experiencia: Optional[int] = Field(None, ge=0)
    strength: Optional[int] = Field(None, ge=1, le=25)
    dexterity: Optional[int] = Field(None, ge=1, le=25)
    constitution: Optional[int] = Field(None, ge=1, le=25)
    intelligence: Optional[int] = Field(None, ge=1, le=25)
    wisdom: Optional[int] = Field(None, ge=1, le=25)
    charisma: Optional[int] = Field(None, ge=1, le=25)
    hp_max: Optional[int] = Field(None, ge=0)
    hp_atual: Optional[int] = Field(None, ge=0)
    ficha: Optional[Dict[str, Any]] = None

    @field_validator("ficha")
    @classmethod
    def _ficha_validar_update(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        return validar_ficha_json_serializavel_e_tamanho(v)


class Dnd5ePersonagemResponse(Dnd5ePersonagemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dono_id: Optional[int] = None
    dono_nome: Optional[str] = ""
    foto_url: Optional[str] = None
    hp_atual: int
    ficha: Dict[str, Any] = Field(default_factory=dict)
    strength_mod: int
    dexterity_mod: int
    constitution_mod: int
    intelligence_mod: int
    wisdom_mod: int
    charisma_mod: int
    bonus_proficiencia: int
