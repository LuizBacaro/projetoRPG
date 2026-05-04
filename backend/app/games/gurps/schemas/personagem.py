"""Schemas Pydantic — ficha GURPS."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Limite do blob JSON em UTF-8 (proteção contra payloads enormes).
GURPS_EXTRAS_MAX_JSON_BYTES = 65_536
# Versão do formato documentado em `extras` (chave "v"); migrar leitura no futuro conforme necessário.
GURPS_EXTRAS_FORMAT_VERSION = 1

_GURPS_EXTRAS_OPENAPI_EXAMPLE: Dict[str, Any] = {
    "v": GURPS_EXTRAS_FORMAT_VERSION,
    "criacao": "2026-05-01",
    "aparencia_long": "Alto, capa verde.",
    "equipamento": "Espada larga, poções.",
    "escudo": "+2",
    "enc": {"nenhuma": {"fp": "0", "d": "—"}, "leve": {"fp": "", "d": ""}},
    "hit": {"cranio": "4", "torso": "0 / 10"},
    "arma": {"golp": "sw+1", "bal": "thr", "nh": "14"},
}
# Convenção de evolução (G4.4):
# - `extras` guarda campos ainda não canonizados em coluna.
# - quando um campo fica estável e vira regra de negócio central,
#   migrar para coluna SQL com fallback de leitura por uma janela.


def validar_extras_json_serializavel_e_tamanho(ex: Any) -> Dict[str, Any]:
    if not isinstance(ex, dict):
        raise ValueError("extras deve ser um objeto JSON (dicionário)")
    try:
        raw = json.dumps(ex, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValueError("extras contém valores não serializáveis em JSON") from e
    if len(raw.encode("utf-8")) > GURPS_EXTRAS_MAX_JSON_BYTES:
        raise ValueError(
            f"extras excede {GURPS_EXTRAS_MAX_JSON_BYTES} bytes após serialização UTF-8"
        )
    return ex


def normalizar_extras_para_gravacao(ex: Dict[str, Any]) -> Dict[str, Any]:
    """Garante chave `v` para evolução futura do formato; não sobrescreve `v` enviada pelo cliente."""
    out = dict(ex)
    out.setdefault("v", GURPS_EXTRAS_FORMAT_VERSION)
    return out


class GurpsVantagemLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    custo: int = 0


class GurpsDesvantagemLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    custo: int = 0


class GurpsPericiaLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    tipo: str = Field(..., max_length=20)
    nh: int = 0
    custo: int = 0


class GurpsPersonagemBase(BaseModel):
    tipo: str = Field(default="jogador", max_length=20)
    nome: str = Field(..., max_length=120)
    conceito: Optional[str] = Field(None, max_length=200)
    reacao: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    campanha_id: Optional[int] = None
    iniciativa: int = Field(
        0,
        description=(
            "Campo legado na ficha; não define ordem de turno. "
            "Na arena GURPS a ordem segue Velocidade básica (velocidade_valor), depois DX, depois sorteio."
        ),
    )

    st_custo: int = 0
    st_valor: int = 10
    dx_custo: int = 0
    dx_valor: int = 10
    iq_custo: int = 0
    iq_valor: int = 10
    ht_custo: int = 0
    ht_valor: int = 10
    vontade_custo: int = 0
    vontade_valor: int = Field(
        10,
        description="Vontade. Quando omitido, o backend assume IQ (Lite).",
    )
    percepcao_custo: int = 0
    percepcao_valor: int = Field(
        10,
        description="Percepção. Quando omitido, o backend assume IQ (Lite).",
    )
    pvs_custo: int = 0
    pvs_valor: int = Field(
        10,
        description="PV máximo. Quando omitido, o backend assume ST (Lite).",
    )
    pvs_atual: Optional[int] = None
    fadiga_custo: int = 0
    fadiga_valor: int = Field(
        10,
        description="Fadiga máxima (PF). Quando omitido, o backend assume HT (Lite).",
    )
    fadiga_atual: Optional[int] = None
    velocidade_custo: int = 0
    velocidade_valor: Decimal = Field(
        default=Decimal("5.00"),
        description=(
            "Velocidade básica (VB). Quando omitido, o backend calcula por (HT + DX) / 4."
        ),
    )
    deslocamento_custo: int = 0
    deslocamento_valor: int = Field(
        5,
        description=(
            "Deslocamento básico. Quando omitido, o backend usa a parte inteira da VB."
        ),
    )
    esquiva: int = Field(
        0,
        description="Esquiva. Quando omitida, o backend calcula como floor(VB) + 3 (Lite).",
    )
    aparar: int = 0
    bloqueio: Optional[str] = Field(None, max_length=20)
    dano_impacto: Optional[str] = Field(
        None,
        max_length=40,
        description="GDP/thr. Quando omitido, backend calcula pela tabela de ST (Lite).",
    )
    dano_balanco: Optional[str] = Field(
        None,
        max_length=40,
        description="BAL/sw. Quando omitido, backend calcula pela tabela de ST (Lite).",
    )
    pontos_atributos: int = 0
    pontos_vantagens: int = 0
    pontos_desvantagens: int = 0
    pontos_pericias: int = 0
    pontos_total: int = 0


class GurpsPersonagemCreate(GurpsPersonagemBase):
    vantagens: List[GurpsVantagemLinha] = Field(default_factory=list)
    desvantagens: List[GurpsDesvantagemLinha] = Field(default_factory=list)
    pericias: List[GurpsPericiaLinha] = Field(default_factory=list)
    extras: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Campos livres da ficha (encargo `enc`, locais de acerto `hit`, equipamento, notas). "
            "Inclua `v` (inteiro) como versão do formato; o servidor define `v=1` se omitido."
        ),
        json_schema_extra={"example": _GURPS_EXTRAS_OPENAPI_EXAMPLE},
    )

    @field_validator("extras")
    @classmethod
    def _extras_validar_create(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        return validar_extras_json_serializavel_e_tamanho(v)


class GurpsPersonagemUpdate(BaseModel):
    tipo: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, max_length=120)
    conceito: Optional[str] = Field(None, max_length=200)
    reacao: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    campanha_id: Optional[int] = None
    iniciativa: Optional[int] = Field(
        None,
        description=(
            "Legado; ordem de turno na arena usa velocidade_valor (VB), DX e sorteio, não este campo."
        ),
    )
    foto_url: Optional[str] = Field(None, max_length=500)

    st_custo: Optional[int] = None
    st_valor: Optional[int] = None
    dx_custo: Optional[int] = None
    dx_valor: Optional[int] = None
    iq_custo: Optional[int] = None
    iq_valor: Optional[int] = None
    ht_custo: Optional[int] = None
    ht_valor: Optional[int] = None
    vontade_custo: Optional[int] = None
    vontade_valor: Optional[int] = None
    percepcao_custo: Optional[int] = None
    percepcao_valor: Optional[int] = None
    pvs_custo: Optional[int] = None
    pvs_valor: Optional[int] = None
    pvs_atual: Optional[int] = None
    fadiga_custo: Optional[int] = None
    fadiga_valor: Optional[int] = None
    fadiga_atual: Optional[int] = None
    velocidade_custo: Optional[int] = None
    velocidade_valor: Optional[Decimal] = None
    deslocamento_custo: Optional[int] = None
    deslocamento_valor: Optional[int] = None
    esquiva: Optional[int] = None
    aparar: Optional[int] = None
    bloqueio: Optional[str] = Field(None, max_length=20)
    dano_impacto: Optional[str] = Field(None, max_length=40)
    dano_balanco: Optional[str] = Field(None, max_length=40)
    pontos_atributos: Optional[int] = None
    pontos_vantagens: Optional[int] = None
    pontos_desvantagens: Optional[int] = None
    pontos_pericias: Optional[int] = None
    pontos_total: Optional[int] = None

    vantagens: Optional[List[GurpsVantagemLinha]] = None
    desvantagens: Optional[List[GurpsDesvantagemLinha]] = None
    pericias: Optional[List[GurpsPericiaLinha]] = None
    extras: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Substitui o objeto extras inteiro quando enviado.",
        json_schema_extra={"example": _GURPS_EXTRAS_OPENAPI_EXAMPLE},
    )

    @field_validator("extras")
    @classmethod
    def _extras_validar_update(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return None
        return validar_extras_json_serializavel_e_tamanho(v)


class GurpsPersonagemResponse(GurpsPersonagemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dono_id: Optional[int] = None
    foto_url: Optional[str] = None
    pvs_atual: int
    fadiga_atual: int
    extras: Dict[str, Any] = Field(
        default_factory=dict,
        validation_alias="extras_json",
        description="JSON livre persistido na ficha; ver campo homônimo em Create.",
        json_schema_extra={"example": _GURPS_EXTRAS_OPENAPI_EXAMPLE},
    )
    vantagens: List[GurpsVantagemLinha] = Field(default_factory=list)
    desvantagens: List[GurpsDesvantagemLinha] = Field(default_factory=list)
    pericias: List[GurpsPericiaLinha] = Field(default_factory=list)
