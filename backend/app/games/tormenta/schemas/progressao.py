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
    classe_nivel_atual: Optional[int] = None
    classe_nivel_novo: Optional[int] = None
    classe_nova_multiclasse: bool = False
    multiclasse_v13_novo: Optional[List[Dict[str, Any]]] = None
    nivel_conjuracao_atual: Optional[int] = None
    nivel_conjuracao_novo: Optional[int] = None
    pv_max_atual: Optional[int] = None
    pv_max_novo: Optional[int] = None
    pv_ganho: Optional[int] = None
    pa_max_atual: Optional[int] = None
    pa_max_novo: Optional[int] = None
    pa_ganho: Optional[int] = None
    beneficio_nivel: Optional[Dict[str, Any]] = None
    graduacao_pericias_atual: str = ""
    graduacao_pericias_nova: str = ""
    talentos_totais_novo: int = 0
    talentos_ganho: int = 0
    poderes_gerais_totais_novo: Optional[int] = None
    poderes_gerais_ganho: Optional[int] = None
    pontos_habilidade_acumulados: int = 0
    bonus_meio_nivel_atual: int = 0
    bonus_meio_nivel: int = 0
    bonus_treino_atual: int = 0
    bonus_treino_novo: int = 0
    pericias_mudou_meio: bool = False
    pericias_mudou_treino: bool = False
    pericias_nota: str = ""
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
    classe_slug: Optional[str] = Field(
        None,
        description="Classe v1.3 que recebe +1 (multiclasse). Omitido = classe principal.",
    )


class TormentaSubirNivelAplicarResponse(BaseModel):
    preview: TormentaSubirNivelPreviewResponse
    personagem: TormentaPersonagemResponse
