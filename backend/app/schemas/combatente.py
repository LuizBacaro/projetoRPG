"""
Schemas Pydantic para Combatente (DTOs)
SRP: apenas serialização/validação
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from .ataque import AtaqueResponse, MagiaSlotResponse, MagiaPreparadaResponse
import re

_HTML_TAG_RE = re.compile(r'<[^>]+>')


def _strip_html(v):
    """Remove tags HTML de strings para prevenir XSS"""
    if v is None:
        return v
    return _HTML_TAG_RE.sub('', str(v)).strip()


class CombatenteBase(BaseModel):
    nome:       str = Field(..., min_length=1, max_length=100)
    tipo:       str = Field(..., pattern="^(jogador|monstro|npc)$")
    classe:     str = Field(..., min_length=1, max_length=50)
    raca:       Optional[str] = Field(default="", max_length=50)
    raca_slug:  Optional[str] = Field(default="", max_length=80)
    divindade: Optional[str] = Field(default="", max_length=80)
    alinhamento: Optional[str] = Field(default="", max_length=30)
    dominios: Optional[str] = Field(default="", max_length=120)

    # ✅ NOVO: apenas monstros usam, mas aceita em todos os tipos (nullable)
    pagina_referencia: Optional[str] = Field(default="", max_length=100)

    @field_validator('nome', 'classe', 'raca', 'raca_slug', 'divindade', 'alinhamento', 'dominios', 'pagina_referencia', mode='before')
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)

    hp_maximo:  int = Field(..., gt=0)
    iniciativa: int = Field(..., ge=0)

    ca:       int = Field(default=10, ge=0, le=50)
    toque:    int = Field(default=10, ge=0, le=50)
    surpresa: int = Field(default=10, ge=0, le=50)
    pc:       int = Field(default=0, ge=0)
    pp:       int = Field(default=0, ge=0)
    po:       int = Field(default=0, ge=0)
    pl:       int = Field(default=0, ge=0)

    forca:        int = Field(default=10, ge=1, le=30)
    destreza:     int = Field(default=10, ge=1, le=30)
    constituicao: int = Field(default=10, ge=1, le=30)
    inteligencia: int = Field(default=10, ge=1, le=30)
    sabedoria:    int = Field(default=10, ge=1, le=30)
    carisma:      int = Field(default=10, ge=1, le=30)

    fortitude: int = Field(default=0, ge=-10, le=50)
    reflexos:  int = Field(default=0, ge=-10, le=50)
    vontade:   int = Field(default=0, ge=-10, le=50)

    nivel:  int = Field(default=1,  ge=1, le=20)
    pontos: int = Field(default=0,  ge=0)


class CombatenteCreate(CombatenteBase):
    foto_url: Optional[str] = None


class CombatenteUpdate(BaseModel):
    nome:       Optional[str] = Field(None, min_length=1, max_length=100)
    tipo:       Optional[str] = Field(None, pattern="^(jogador|monstro|npc)$")
    classe:     Optional[str] = Field(None, min_length=1, max_length=50)
    raca:       Optional[str] = Field(None, max_length=50)
    raca_slug:  Optional[str] = Field(None, max_length=80)
    divindade: Optional[str] = Field(None, max_length=80)
    alinhamento: Optional[str] = Field(None, max_length=30)
    dominios: Optional[str] = Field(None, max_length=120)

    # ✅ NOVO
    pagina_referencia: Optional[str] = Field(None, max_length=100)

    @field_validator('nome', 'classe', 'raca', 'raca_slug', 'divindade', 'alinhamento', 'dominios', 'pagina_referencia', mode='before')
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)

    hp_atual:   Optional[int] = Field(None, ge=0)
    hp_maximo:  Optional[int] = Field(None, gt=0)
    iniciativa: Optional[int] = Field(None, ge=0)
    foto_url:   Optional[str] = None

    ca:       Optional[int] = Field(None, ge=0, le=50)
    toque:    Optional[int] = Field(None, ge=0, le=50)
    surpresa: Optional[int] = Field(None, ge=0, le=50)
    pc:       Optional[int] = Field(None, ge=0)
    pp:       Optional[int] = Field(None, ge=0)
    po:       Optional[int] = Field(None, ge=0)
    pl:       Optional[int] = Field(None, ge=0)

    forca:        Optional[int] = Field(None, ge=1, le=30)
    destreza:     Optional[int] = Field(None, ge=1, le=30)
    constituicao: Optional[int] = Field(None, ge=1, le=30)
    inteligencia: Optional[int] = Field(None, ge=1, le=30)
    sabedoria:    Optional[int] = Field(None, ge=1, le=30)
    carisma:      Optional[int] = Field(None, ge=1, le=30)

    fortitude: Optional[int] = Field(None, ge=-10, le=50)
    reflexos:  Optional[int] = Field(None, ge=-10, le=50)
    vontade:   Optional[int] = Field(None, ge=-10, le=50)

    nivel:  Optional[int] = Field(None, ge=1, le=20)
    pontos: Optional[int] = Field(None, ge=0)


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
    id:       int
    dono_id:  Optional[int] = None
    hp_atual: int
    foto_url: Optional[str] = None
    raca:     Optional[str] = ""

    # ✅ NOVO: exposto no response para o frontend exibir na ficha/arena
    pagina_referencia: Optional[str] = ""
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

    ataques:           List[AtaqueResponse]         = []
    magias_slots:      List[MagiaSlotResponse]      = []
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
    id:        int
    nome:      str
    hp_atual:  int
    hp_maximo: int
    mensagem:  str
    class Config:
        from_attributes = True


class DanoCuraMassaResponse(BaseModel):
    resultados: List[DanoCuraResponse]
    total: int