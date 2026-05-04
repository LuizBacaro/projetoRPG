"""Schemas — combate GURPS (Arena)."""

from typing import List, Literal

from pydantic import BaseModel, Field


class GurpsIniciarCombateRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)


class GurpsDefinirManobraRequest(BaseModel):
    manobra: Literal["fazer_nada", "ataque", "defesa_total"] = Field(
        ...,
        description="Manobra do personagem ativo no turno atual.",
    )


class GurpsDefinirPosturaRequest(BaseModel):
    postura: Literal["em_pe", "agachado", "deitado"] = Field(
        ...,
        description="Postura do personagem ativo no turno atual.",
    )


class GurpsAtaqueRequest(BaseModel):
    alvo_id: int = Field(..., ge=1)
    nh_ataque: int | None = Field(
        None,
        ge=1,
        le=30,
        description="NH base do ataque. Em soco/chute, se omitido usa DX do atacante.",
    )
    tipo_ataque: Literal["arma", "soco", "chute"] = Field(
        "arma",
        description="Tipo de ataque. soco/chute aplicam ajustes mínimos do combate sem armas (G4.1).",
    )
    tipo_defesa: Literal["auto", "esquiva", "aparar", "bloqueio"] = Field(
        "auto",
        description="Defesa ativa do alvo. Em 'auto', usa a melhor defesa disponível.",
    )
    expressao_dano: str | None = Field(
        None,
        description="Opcional; usa Nd, Nd+M ou Nd-M. Se omitido, usa dano_impacto do atacante.",
    )
    dados_ataque: List[int] | None = Field(
        None, description="Opcional para debug/teste determinístico (3 dados 1..6)."
    )
    dados_defesa: List[int] | None = Field(
        None, description="Opcional para debug/teste determinístico (3 dados 1..6)."
    )
    dados_dano: List[int] | None = Field(
        None, description="Opcional para debug/teste determinístico (quantidade conforme expressão)."
    )


class GurpsAjustePvRequest(BaseModel):
    alvo_id: int = Field(..., ge=1)
    delta_pv: int = Field(
        ...,
        description="Ajuste de PV no alvo. Positivo cura, negativo causa dano direto.",
    )


class GurpsEsforcoRequest(BaseModel):
    custo_fadiga: int = Field(
        1,
        ge=1,
        le=10,
        description="Custo de fadiga (PF) para esforço na rodada atual.",
    )
    usar_surto: bool = Field(
        False,
        description="Marca uso de surto/esforço extra da mesa para fins de rastreio.",
    )
    descricao: str | None = Field(
        None,
        max_length=120,
        description="Descrição curta do esforço realizado (ex.: ataque forte, deslocamento extra).",
    )
