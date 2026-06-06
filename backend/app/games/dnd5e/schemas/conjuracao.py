"""Schemas — estado de conjuração na ficha (slots, preparação)."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class Dnd5eSlotNivelItem(BaseModel):
    nivel: int = Field(ge=0, le=9)
    total: int = Field(ge=0)
    usados: int = Field(ge=0)
    disponiveis: int = Field(ge=0)


class Dnd5eConjuracaoEstadoResponse(BaseModel):
    classe: str
    nivel_personagem: int
    habilidade_primaria: str = "int"
    modo_lista: str = "nenhum"
    max_nivel_magia: int = Field(default=0, ge=0, le=9)
    prepara_magias: bool = False
    magias_conhecidas_max: Optional[int] = None
    magias_conhecidas_atual: int = 0
    magias_preparadas_max: Optional[int] = None
    magias_preparadas_ids: List[int] = Field(default_factory=list)
    magias_preparadas_qty: Dict[str, int] = Field(default_factory=dict)
    magias_lancadas_ids: List[int] = Field(default_factory=list)
    slots: List[Dnd5eSlotNivelItem] = Field(default_factory=list)
    magia_concentracao_id: Optional[int] = None
    recupera_slots_repouso_curto: bool = False
    truque_multiplicador_dados: int = Field(default=1, ge=1, le=4)
    pontos_feiticaria_atual: Optional[int] = Field(None, ge=0)
    pontos_feiticaria_max: Optional[int] = Field(None, ge=0)
    recuperacao_arcana_disponivel: bool = False
    recuperacao_arcana_max_niveis: Optional[int] = Field(None, ge=0)


class Dnd5eConjuracaoGastarSlotRequest(BaseModel):
    # nivel_magia=0 representa truque (sem consumo de espaço, apenas marca a magia).
    nivel_magia: int = Field(..., ge=0, le=9)
    quantidade: int = Field(default=1, ge=1, le=9)
    magia_id: Optional[int] = Field(default=None, ge=1)


class Dnd5eConjuracaoPrepararRequest(BaseModel):
    magia_ids: List[int] = Field(default_factory=list)
    magias_quantidade: Dict[str, int] = Field(default_factory=dict)


class Dnd5eConjuracaoDescansoResponse(BaseModel):
    estado: Dnd5eConjuracaoEstadoResponse
    mensagem: str


class Dnd5ePontosFeiticariaCriarSlotRequest(BaseModel):
    nivel_slot: int = Field(..., ge=1, le=5)


class Dnd5ePontosFeiticariaConverterSlotRequest(BaseModel):
    nivel_slot: int = Field(..., ge=1, le=5)


class Dnd5eRecuperacaoArcanaRequest(BaseModel):
    """Mapa nível do slot (1–5) → quantidade a recuperar."""
    slots: Dict[int, int] = Field(default_factory=dict)

    @field_validator("slots")
    @classmethod
    def _slots_validos(cls, v: Dict[int, int]) -> Dict[int, int]:
        out: Dict[int, int] = {}
        for chave, qtd in (v or {}).items():
            nivel = int(chave)
            if nivel < 1 or nivel > 5:
                raise ValueError("Recuperação arcana só para slots de 1º a 5º nível")
            if int(qtd) < 1:
                continue
            out[nivel] = int(qtd)
        return out


class Dnd5eConjuracaoConcentracaoRequest(BaseModel):
    magia_id: Optional[int] = Field(default=None, ge=1)


class Dnd5eConjuracaoPerfilResponse(BaseModel):
    classe: str
    nivel: int = Field(ge=1, le=20)
    habilidade_primaria: str
    modo_lista: str
    max_nivel_magia: int = Field(ge=0, le=9)
    recupera_slots_repouso_curto: bool = False
    espacos_por_nivel: List[int] = Field(default_factory=list)
    magias_conhecidas_max: Optional[int] = None
    magias_preparadas_max: Optional[int] = None
