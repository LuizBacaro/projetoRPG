"""Schemas — subir de nível MB."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.games.tormenta.schemas.personagem import TormentaPersonagemResponse


class TormentaSubirNivelPreviewResponse(BaseModel):
    permitido: bool = True
    motivo: str = ""
    nivel_atual: int = Field(..., ge=1, le=40)
    nivel_alvo: int = Field(..., ge=1, le=40)
    classe_slug: str = ""
    nivel_conjuracao_atual: Optional[int] = None
    nivel_conjuracao_novo: Optional[int] = None
    pv_max_atual: Optional[int] = None
    pv_max_novo: Optional[int] = None
    pv_ganho: Optional[int] = None
    pa_max_atual: Optional[int] = None
    pa_max_novo: Optional[int] = None
    pa_ganho: Optional[int] = None
    beneficio_nivel: Optional[Dict[str, Any]] = None
    graduacao_pericias_nova: str = ""
    talentos_totais_novo: int = 0
    talentos_ganho: int = 0
    pontos_habilidade_acumulados: int = 0
    bonus_meio_nivel: int = 0
    habilidade_classe: Optional[str] = None
    magias_livro_ganho: Optional[int] = None
    magias_livro_max_novo: Optional[int] = None
    magias_conhecidas_max_novo: Optional[int] = None
    magias_preparadas_teto_novo: Optional[int] = None
    bardo_pode_trocar_magia: bool = False
    avisos: List[str] = Field(default_factory=list)


class TormentaSubirNivelAplicarRequest(BaseModel):
    aplicar_ganhos_vida: bool = Field(
        True,
        description="Soma pv_ganho aos PV atuais (até o novo máximo).",
    )


class TormentaSubirNivelAplicarResponse(BaseModel):
    preview: TormentaSubirNivelPreviewResponse
    personagem: TormentaPersonagemResponse
