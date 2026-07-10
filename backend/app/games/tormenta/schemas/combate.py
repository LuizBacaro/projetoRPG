"""Schemas — combate Tormenta (Arena)."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class TormentaIniciarCombateRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)


class TormentaCombateCondicaoMbItem(BaseModel):
    rotulos: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)

    @field_validator("rotulos", "tips")
    @classmethod
    def _limitar_listas(cls, v: List[str]) -> List[str]:
        out: List[str] = []
        for x in (v or [])[:80]:
            s = str(x).strip()[:1200]
            if s:
                out.append(s)
        return out


class TormentaCombateCondicoesMbRequest(BaseModel):
    """Chaves = id do personagem (string); apenas combatentes do combate ativo."""

    por_personagem: Dict[str, TormentaCombateCondicaoMbItem] = Field(..., min_length=1)


class TormentaCombateRolarIniciativaRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)


class TormentaCombateAplicarIniciativaManualRequest(BaseModel):
    """Chaves = id do personagem (string); valor = iniciativa total na mesa."""

    por_personagem: Dict[str, int] = Field(..., min_length=1)

    @field_validator("por_personagem")
    @classmethod
    def _validar_totais(cls, v: Dict[str, int]) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for k, val in (v or {}).items():
            try:
                n = int(val)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Iniciativa inválida para personagem {k}") from e
            if n < -99 or n > 99:
                raise ValueError(
                    f"Iniciativa fora do intervalo (-99 a 99) para personagem {k}"
                )
            out[str(k)] = n
        return out


class TormentaCombateRolarAtaqueRequest(BaseModel):
    atacante_id: int
    alvo_id: int
    bab: int = Field(0, ge=-99, le=99)
    mod_atributo: int = Field(0, ge=-99, le=99)
    bonus_arma: int = Field(0, ge=-99, le=99)
    penalidades: int = Field(0, ge=0, le=99)
    ca_alvo: Optional[int] = Field(None, ge=0, le=99)


class TormentaCombateRolarDanoRequest(BaseModel):
    formula_dano: str = Field("1d8", max_length=40)
    mod_atributo: int = Field(0, ge=-99, le=99)
    confirmar_critico: bool = False
    aplicar_ao_alvo_id: Optional[int] = None
    atacante_id: Optional[int] = Field(
        None, description="Opcional: aplica Força dos Titãs se Galokk e flag ativa."
    )
    forca_dos_titas: bool = Field(
        False, description="Gasta 1 PM — dado extra no dano máximo (Galokk)."
    )


class TormentaCombateTestarResistenciaMagiaRequest(BaseModel):
    """Teste de resistência contra magia (MB): CD explícita ou círculo + conjurador."""

    alvo_id: int
    tipo: Optional[str] = Field(
        None, description="fortitude | reflexos | vontade (ou infere de magia_slug)"
    )
    cd: Optional[int] = Field(None, ge=1, le=99)
    circulo_magia: Optional[int] = Field(None, ge=0, le=9)
    conjurador_id: Optional[int] = None
    magia_slug: Optional[str] = Field(
        None,
        max_length=120,
        description="Opcional: infere tipo de teste do catálogo MB.",
    )
    falha_voluntaria: bool = False
    efeito_mental: bool = Field(
        False,
        description="Eiradaan: Canção da Melancolia (pior de 2d20 em Vontade).",
    )
