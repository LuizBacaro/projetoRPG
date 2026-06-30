"""Schemas — talentos do personagem Tormenta (vínculo + catálogo)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TormentaTalentoPersonagemItem(BaseModel):
    """Uma linha de talento na ficha (resposta API)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    talento_id: int
    nome: str
    descricao: Optional[str] = None
    pagina_referencia: Optional[str] = None
    origem_catalogo_mb: bool = True
    notas: Optional[str] = None
    categoria_v13: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Categoria v1.3 derivada do catálogo ou notas auto:v13.",
    )
    custo_pm: int = Field(
        default=0,
        ge=0,
        le=99,
        description="PM ao ativar (catálogo); 0 se passivo.",
    )
    adicionado_em: datetime


class TormentaPoderAtivarRequest(BaseModel):
    """Ativa poder com custo PM (v1.3)."""

    model_config = ConfigDict(extra="forbid")

    vinculo_id: int = Field(..., ge=1)
    custo_pm: Optional[int] = Field(
        None,
        ge=0,
        le=99,
        description="Override opcional; padrão = catálogo.",
    )


class TormentaPoderAtivarResponse(BaseModel):
    nome: str
    custo_pm: int = Field(ge=0)
    pa_atual_antes: int
    pa_atual_depois: int
    pa_max: int


class TormentaTalentoVinculoCreate(BaseModel):
    """Corpo para vincular talento: use `talento_id` (catálogo) ou `nome` (busca/criação)."""

    model_config = ConfigDict(extra="forbid")

    talento_id: Optional[int] = Field(None, ge=1)
    nome: Optional[str] = Field(None, max_length=200)
    notas: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def _exige_um_identificador(self) -> TormentaTalentoVinculoCreate:
        tid = self.talento_id is not None
        nom = self.nome is not None and str(self.nome).strip() != ""
        if tid == nom:
            raise ValueError("Informe exatamente um entre talento_id ou nome")
        return self


class TormentaMigrarTalentosJsonResponse(BaseModel):
    """Resultado de importar talentos_mb_lista do ficha_json."""

    vinculos_criados: int = Field(ge=0)
    ignorados_duplicados: int = Field(ge=0)
