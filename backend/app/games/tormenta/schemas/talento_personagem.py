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
    adicionado_em: datetime


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
