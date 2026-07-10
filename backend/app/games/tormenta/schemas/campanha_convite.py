"""Schemas — convite de campanha Tormenta (RF-T12k)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TormentaCampanhaConviteStatusResponse(BaseModel):
    campanha_id: int
    ativo: bool
    token: str | None = None
    url_path: str | None = Field(
        None,
        description="Caminho relativo para o jogador (dashboard.html?convite=…).",
    )


class TormentaCampanhaConviteInfoResponse(BaseModel):
    campanha_id: int
    nome: str
    mestre_nome: str = ""
    descricao: str = ""


class TormentaCampanhaConviteEntrarRequest(BaseModel):
    personagem_id: int = Field(..., ge=1)
