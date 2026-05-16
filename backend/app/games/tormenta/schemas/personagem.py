"""Schemas Pydantic — ficha Tormenta 20 (Módulo Básico)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.games.tormenta.schemas.consumivel_personagem import (
    TormentaConsumivelPersonagemItem,
)
from app.games.tormenta.schemas.equipamento_personagem import (
    TormentaEquipamentoPersonagemItem,
)
from app.games.tormenta.schemas.magia_personagem import TormentaMagiaPersonagemItem
from app.games.tormenta.schemas.talento_personagem import TormentaTalentoPersonagemItem
from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    resumo_elegibilidade_grimorio_mb,
)

# Limite do JSON da ficha (perícias, equipamento, magias, notas).
TORMENTA_FICHA_JSON_MAX_BYTES = 96_000


def validar_ficha_json_serializavel_e_tamanho(blob: Any) -> Dict[str, Any]:
    if blob is None:
        return {}
    if not isinstance(blob, dict):
        raise ValueError("ficha_json deve ser um objeto JSON (dicionário)")
    try:
        raw = json.dumps(blob, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValueError("ficha_json contém valores não serializáveis em JSON") from e
    if len(raw.encode("utf-8")) > TORMENTA_FICHA_JSON_MAX_BYTES:
        raise ValueError(
            f"ficha_json excede {TORMENTA_FICHA_JSON_MAX_BYTES} bytes após serialização UTF-8"
        )
    return blob


class TormentaPersonagemBase(BaseModel):
    tipo: str = Field(default="jogador", max_length=20)
    nome: str = Field(..., max_length=120)
    jogador_nome: Optional[str] = Field(None, max_length=120)
    raca: Optional[str] = Field(None, max_length=120)
    classe_nivel: Optional[str] = Field(None, max_length=160)
    sexo: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    tendencia: Optional[str] = Field(None, max_length=80)
    divindade: Optional[str] = Field(None, max_length=120)

    foto_url: Optional[str] = Field(None, max_length=2048)

    # Padrão 10 em cada (compra por pontos + raça aplicada na ficha; ver ficha_json.atributos_compra).
    for_valor: int = Field(default=10, ge=0, le=99)
    des_valor: int = Field(default=10, ge=0, le=99)
    con_valor: int = Field(default=10, ge=0, le=99)
    int_valor: int = Field(default=10, ge=0, le=99)
    sab_valor: int = Field(default=10, ge=0, le=99)
    car_valor: int = Field(default=10, ge=0, le=99)

    pv_max: int = Field(default=1, ge=0, le=9999)
    pv_atual: Optional[int] = Field(None, ge=-9999, le=9999)
    pa_max: int = Field(
        default=0,
        ge=0,
        le=999,
        description="Pontos de Magia (PM) máximos — MB; calculado na criação se classe conjuradora MB.",
    )
    pa_atual: Optional[int] = Field(
        None, ge=-999, le=999, description="PM atuais (gastos na mesa)."
    )
    ca: int = Field(default=10, ge=0, le=99)
    rd: str = Field(default="", max_length=80)
    nivel: int = Field(default=1, ge=0, le=40)
    iniciativa: int = Field(default=0, ge=-99, le=99)
    deslocamento: str = Field(default="", max_length=80)
    tamanho: str = Field(default="", max_length=80)

    fort_total: int = Field(default=0, ge=-99, le=99)
    ref_total: int = Field(default=0, ge=-99, le=99)
    von_total: int = Field(default=0, ge=-99, le=99)

    ficha_json: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("ficha_json", mode="before")
    @classmethod
    def _validar_ficha(cls, v: Any) -> Dict[str, Any]:
        return validar_ficha_json_serializavel_e_tamanho(v if v is not None else {})


class TormentaPersonagemCreate(TormentaPersonagemBase):
    pass


class TormentaPersonagemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, max_length=120)
    jogador_nome: Optional[str] = Field(None, max_length=120)
    raca: Optional[str] = Field(None, max_length=120)
    classe_nivel: Optional[str] = Field(None, max_length=160)
    sexo: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    tendencia: Optional[str] = Field(None, max_length=80)
    divindade: Optional[str] = Field(None, max_length=120)

    foto_url: Optional[str] = Field(None, max_length=2048)

    for_valor: Optional[int] = Field(None, ge=0, le=99)
    des_valor: Optional[int] = Field(None, ge=0, le=99)
    con_valor: Optional[int] = Field(None, ge=0, le=99)
    int_valor: Optional[int] = Field(None, ge=0, le=99)
    sab_valor: Optional[int] = Field(None, ge=0, le=99)
    car_valor: Optional[int] = Field(None, ge=0, le=99)

    pv_max: Optional[int] = Field(None, ge=0, le=9999)
    pv_atual: Optional[int] = Field(None, ge=-9999, le=9999)
    pa_max: Optional[int] = Field(
        None, ge=0, le=999, description="Pontos de Magia (PM) máximos."
    )
    pa_atual: Optional[int] = Field(None, ge=-999, le=999, description="PM atuais.")
    ca: Optional[int] = Field(None, ge=0, le=99)
    rd: Optional[str] = Field(None, max_length=80)
    nivel: Optional[int] = Field(None, ge=0, le=40)
    iniciativa: Optional[int] = Field(None, ge=-99, le=99)
    deslocamento: Optional[str] = Field(None, max_length=80)
    tamanho: Optional[str] = Field(None, max_length=80)

    fort_total: Optional[int] = Field(None, ge=-99, le=99)
    ref_total: Optional[int] = Field(None, ge=-99, le=99)
    von_total: Optional[int] = Field(None, ge=-99, le=99)

    ficha_json: Optional[Dict[str, Any]] = None

    @field_validator("ficha_json", mode="before")
    @classmethod
    def _validar_ficha_upd(cls, v: Any) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        return validar_ficha_json_serializavel_e_tamanho(v)


class TormentaPersonagemResponse(TormentaPersonagemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campanha_id: Optional[int] = None
    talentos: List[TormentaTalentoPersonagemItem] = Field(default_factory=list)
    equipamentos: List[TormentaEquipamentoPersonagemItem] = Field(default_factory=list)
    consumiveis: List[TormentaConsumivelPersonagemItem] = Field(default_factory=list)
    magias: List[TormentaMagiaPersonagemItem] = Field(
        default_factory=list,
        description="Vínculos grimório / conhecidas / preparadas (catálogo MB por slug).",
    )
    grimorio_mb_permitido: bool = Field(
        default=False,
        description="True se a ficha pode vincular magias MB (classe conjuradora + nível MB ou tormenta_conjuracao_manual_mb).",
    )
    grimorio_mb_motivo: Optional[str] = Field(
        default=None,
        description="Se grimorio_mb_permitido for false, texto para exibir na UI; caso contrário null.",
    )

    @model_validator(mode="after")
    def _preencher_elegibilidade_grimorio_mb(self) -> Self:
        ok, msg = resumo_elegibilidade_grimorio_mb(
            tipo=str(self.tipo or ""),
            nivel=int(self.nivel or 1),
            ficha_json=self.ficha_json,
        )
        self.grimorio_mb_permitido = ok
        self.grimorio_mb_motivo = None if ok else (msg or None)
        return self
