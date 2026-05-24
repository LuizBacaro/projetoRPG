"""
Schemas Pydantic para Combatente (DTOs)
SRP: apenas serialização/validação
"""

import json
import re
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.games.dnd35.schemas.ataque import (
    AtaqueResponse,
    MagiaPreparadaResponse,
    MagiaSlotResponse,
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")

# Jogadores costumam ficar ≤30; monstros/NPC de bestiário podem exceder (ex.: dragões).
_ATTR_MAX = 50


def _strip_html(v):
    """Remove tags HTML de strings para prevenir XSS"""
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", str(v)).strip()


class CombatenteBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., pattern="^(jogador|monstro|npc)$")
    classe: str = Field(..., min_length=1, max_length=50)
    raca: Optional[str] = Field(default="", max_length=50)
    raca_slug: Optional[str] = Field(default="", max_length=80)
    divindade: Optional[str] = Field(default="", max_length=80)
    alinhamento: Optional[str] = Field(default="", max_length=30)
    dominios: Optional[str] = Field(default="", max_length=120)
    campanha_id: Optional[int] = Field(default=None, ge=1)

    # ✅ NOVO: apenas monstros usam, mas aceita em todos os tipos (nullable)
    pagina_referencia: Optional[str] = Field(default="", max_length=100)

    @field_validator(
        "nome",
        "classe",
        "raca",
        "raca_slug",
        "divindade",
        "alinhamento",
        "dominios",
        "pagina_referencia",
        mode="before",
    )
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)

    hp_maximo: int = Field(..., gt=0)
    iniciativa: int = Field(..., ge=0)

    ca: int = Field(default=10, ge=0, le=50)
    toque: int = Field(default=10, ge=0, le=50)
    surpresa: int = Field(default=10, ge=0, le=50)
    pc: int = Field(default=0, ge=0)
    pp: int = Field(default=0, ge=0)
    po: int = Field(default=0, ge=0)
    pl: int = Field(default=0, ge=0)

    forca: int = Field(default=10, ge=1, le=_ATTR_MAX)
    destreza: int = Field(default=10, ge=1, le=_ATTR_MAX)
    constituicao: int = Field(default=10, ge=1, le=_ATTR_MAX)
    inteligencia: int = Field(default=10, ge=1, le=_ATTR_MAX)
    sabedoria: int = Field(default=10, ge=1, le=_ATTR_MAX)
    carisma: int = Field(default=10, ge=1, le=_ATTR_MAX)

    fortitude: int = Field(default=0, ge=-10, le=50)
    reflexos: int = Field(default=0, ge=-10, le=50)
    vontade: int = Field(default=0, ge=-10, le=50)

    nivel: int = Field(default=1, ge=1, le=20)
    pontos: int = Field(default=0, ge=0)


class CombatenteCreate(CombatenteBase):
    foto_url: Optional[str] = None


class CombatenteUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, pattern="^(jogador|monstro|npc)$")
    classe: Optional[str] = Field(None, min_length=1, max_length=50)
    raca: Optional[str] = Field(None, max_length=50)
    raca_slug: Optional[str] = Field(None, max_length=80)
    divindade: Optional[str] = Field(None, max_length=80)
    alinhamento: Optional[str] = Field(None, max_length=30)
    dominios: Optional[str] = Field(None, max_length=120)
    campanha_id: Optional[int] = Field(default=None, ge=1)

    # ✅ NOVO
    pagina_referencia: Optional[str] = Field(None, max_length=100)

    @field_validator(
        "nome",
        "classe",
        "raca",
        "raca_slug",
        "divindade",
        "alinhamento",
        "dominios",
        "pagina_referencia",
        mode="before",
    )
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)

    hp_atual: Optional[int] = Field(None, ge=0)
    hp_maximo: Optional[int] = Field(None, gt=0)
    iniciativa: Optional[int] = Field(None, ge=0)
    foto_url: Optional[str] = None

    ca: Optional[int] = Field(None, ge=0, le=50)
    toque: Optional[int] = Field(None, ge=0, le=50)
    surpresa: Optional[int] = Field(None, ge=0, le=50)
    pc: Optional[int] = Field(None, ge=0)
    pp: Optional[int] = Field(None, ge=0)
    po: Optional[int] = Field(None, ge=0)
    pl: Optional[int] = Field(None, ge=0)

    forca: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)
    destreza: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)
    constituicao: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)
    inteligencia: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)
    sabedoria: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)
    carisma: Optional[int] = Field(None, ge=1, le=_ATTR_MAX)

    fortitude: Optional[int] = Field(None, ge=-10, le=50)
    reflexos: Optional[int] = Field(None, ge=-10, le=50)
    vontade: Optional[int] = Field(None, ge=-10, le=50)

    nivel: Optional[int] = Field(None, ge=1, le=20)
    pontos: Optional[int] = Field(None, ge=0)
    idiomas_customizados: Optional[Any] = None


class HabilidadeEspecialEnriquecida(BaseModel):
    """Representação canônica de uma habilidade especial para a ficha.

    - `raw` preserva o texto como extraído da tabela de classe/raça
      (ex.: "Fúria (1/dia)"), garantindo fallback visual quando o
      catálogo não conhece a habilidade.
    - `slug`, `titulo` e `descricao` vêm do catálogo canônico
      (docs/dados/habilidades_especiais_catalogo.json) quando a
      resolução foi bem-sucedida; caso contrário ficam vazios.
    """

    raw: str = ""
    slug: str = ""
    titulo: str = ""
    descricao: str = ""


class HabilidadesEspeciaisNivel(BaseModel):
    nivel: int = 0
    habilidades: List[HabilidadeEspecialEnriquecida] = []


class CombatenteResponse(CombatenteBase):
    id: int
    dono_id: Optional[int] = None
    hp_atual: int
    foto_url: Optional[str] = None
    raca: Optional[str] = ""

    # ✅ NOVO: exposto no response para o frontend exibir na ficha/arena
    pagina_referencia: Optional[str] = ""
    campanha_nome: Optional[str] = ""
    bonus_base_ataque: Optional[str] = ""
    habilidades_especiais: Optional[str] = ""
    # Novo campo enriquecido; fallback legado permanece em `habilidades_especiais`.
    habilidades_especiais_detalhadas: List[HabilidadesEspeciaisNivel] = []
    tamanho_racial: Optional[str] = ""
    deslocamento_racial_metros: Optional[int] = None
    idiomas_raciais: List[str] = []
    idiomas_customizados: List[str] = []
    passivos_raciais: List[str] = []
    # Linhas canônicas de bônus racial em perícia (catálogo de raças), sem misturar
    # resistências/ataque/CA. Usado pela UI de perícias para aplicar bônus automático.
    modificadores_pericia: List[str] = []
    fortitude_base: Optional[int] = 0
    reflexos_base: Optional[int] = 0
    vontade_base: Optional[int] = 0

    @field_validator("idiomas_customizados", mode="before")
    @classmethod
    def _idiomas_customizados_desde_orm(cls, v: Any) -> list[str]:
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        texto = str(v).strip()
        if not texto:
            return []
        try:
            parsed = json.loads(texto)
        except (TypeError, ValueError):
            parsed = None
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
        if isinstance(parsed, str) and parsed.strip():
            return [parsed.strip()]
        return [x.strip() for x in texto.split(",") if x.strip()]

    ataques: List[AtaqueResponse] = []
    magias_slots: List[MagiaSlotResponse] = []
    magias_preparadas: List[MagiaPreparadaResponse] = []

    class Config:
        from_attributes = True


class HPUpdateRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)


class IniciativaUpdateRequest(BaseModel):
    iniciativa: int = Field(..., ge=0)


class DanoRequest(BaseModel):
    dano: int = Field(..., gt=0)


class DanoCuraRequest(BaseModel):
    valor: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {"example": {"valor": 10}}


class DanoCuraMassaRequest(BaseModel):
    combatente_ids: List[int] = Field(..., min_length=1)
    valor: int = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "combatente_ids": [1, 2, 3],
                "valor": 10,
            }
        }


class DanoCuraResponse(BaseModel):
    id: int
    nome: str
    hp_atual: int
    hp_maximo: int
    mensagem: str

    class Config:
        from_attributes = True


class DanoCuraMassaResponse(BaseModel):
    resultados: List[DanoCuraResponse]
    total: int
