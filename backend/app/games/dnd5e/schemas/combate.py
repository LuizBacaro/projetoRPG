"""Schemas — arena de combate D&D 5e (sessão leve)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Dnd5eIniciativaCombatente(BaseModel):
    id: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=120)
    dex_mod: int = Field(default=0, ge=-5, le=20)
    feats: List[str] = Field(default_factory=list)


class Dnd5eIniciativaRequest(BaseModel):
    combatentes: List[Dnd5eIniciativaCombatente] = Field(..., min_length=1)


class Dnd5eIniciativaResultado(BaseModel):
    id: str
    nome: str
    dex_mod: int
    rolagem: int = Field(ge=1, le=20)
    iniciativa: int


class Dnd5eIniciativaResponse(BaseModel):
    ordem: List[Dnd5eIniciativaResultado]


class Dnd5eAtaqueRequest(BaseModel):
    mod_atributo: int = Field(default=0, ge=-5, le=20)
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    ac_alvo: int = Field(..., ge=0, le=40)
    proficiente: bool = True
    bonus_extra: int = Field(default=0, ge=-20, le=20)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)
    condicoes_atacante: List[str] = Field(default_factory=list)
    condicoes_alvo: List[str] = Field(default_factory=list)
    corpo_a_corpo: bool = True
    arma_slug: Optional[str] = Field(
        None,
        max_length=80,
        description="Se informado, aplica finesse/versátil/leve/duas mãos",
    )
    str_mod: Optional[int] = Field(None, ge=-5, le=20)
    dex_mod: Optional[int] = Field(None, ge=-5, le=20)
    duas_maos: bool = False
    feats: List[str] = Field(default_factory=list)
    raca_slug: Optional[str] = Field(
        None,
        max_length=40,
        description="Raça do atacante (traits: sorte halfling)",
    )
    aplicar_sorte_halfling: bool = Field(
        default=True,
        description="Rerrolar natural 1 (halfling)",
    )


class Dnd5eAtaqueResponse(BaseModel):
    rolagem: int
    rolagem_secundaria: Optional[int] = None
    total: int
    acerto: bool
    vantagem: bool = False
    desvantagem: bool = False
    critico_automatico: bool = False
    acerto_automatico: bool = False
    is_critico: bool = False
    sorte_reroll: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Segunda rolagem da Sorte (halfling)",
    )
    mod_atributo_usado: Optional[int] = None
    atributo_usado: Optional[str] = None
    arma_slug: Optional[str] = None
    propriedades: List[str] = Field(default_factory=list)
    bonus_feats: int = 0


class Dnd5eSalvamentoRequest(BaseModel):
    mod_atributo: int = Field(default=0, ge=-5, le=20)
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    cd: int = Field(..., ge=0, le=40)
    proficiente: bool = False
    raca_slug: Optional[str] = Field(None, max_length=40)
    categoria: str = Field(
        default="",
        max_length=32,
        description="Ex.: veneno, encantamento",
    )
    condicoes: List[str] = Field(default_factory=list)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)
    aplicar_sorte_halfling: bool = True
    feats: List[str] = Field(default_factory=list)
    feat_escolhas: Dict[str, Any] = Field(default_factory=dict)
    save_tipo: str = Field(
        default="",
        max_length=20,
        description="fortitude | reflexos | vontade (Resilient)",
    )
    usar_lucky: bool = False
    lucky_restantes: int = Field(default=0, ge=0, le=10)


class Dnd5eSalvamentoResponse(BaseModel):
    rolagem: int
    rolagem_secundaria: Optional[int] = None
    sorte_reroll: Optional[int] = None
    lucky_reroll: Optional[int] = Field(None, ge=1, le=20)
    lucky_restantes: int = Field(default=0, ge=0)
    proficiente_resilient: bool = False
    total: int
    sucesso: bool
    vantagem: bool = False
    bonus_racial: int = 0
    cd: int


class Dnd5eDanoRequest(BaseModel):
    dano: str = Field(default="1d8", max_length=20)
    mod_atributo: int = Field(default=0, ge=-5, le=20)
    is_critico: bool = False
    arma_slug: Optional[str] = Field(None, max_length=80)
    str_mod: Optional[int] = Field(None, ge=-5, le=20)
    dex_mod: Optional[int] = Field(None, ge=-5, le=20)
    duas_maos: bool = False
    rolagem_forcada: Optional[int] = Field(
        None,
        ge=1,
        description="Soma forçada dos dados (testes)",
    )


class Dnd5eDanoResponse(BaseModel):
    dano_total: int = Field(ge=1)
    expressao_dano: Optional[str] = None
    mod_atributo_usado: Optional[int] = None
    atributo_usado: Optional[str] = None


class Dnd5eCondicaoAtivaItem(BaseModel):
    slug: str = Field(..., max_length=40)
    duracao_turnos: int = Field(
        default=-1,
        ge=-1,
        le=99,
        description="-1 permanente; 1+ turnos restantes do combatente",
    )
    origem: Optional[str] = Field(
        None,
        max_length=20,
        description='Ex.: "hp" para inconsciente automático a 0 PV',
    )


class Dnd5eCondicoesTurnoRequest(BaseModel):
    condicoes: List[Dnd5eCondicaoAtivaItem] = Field(default_factory=list)


class Dnd5eCondicoesTurnoResponse(BaseModel):
    condicoes: List[Dnd5eCondicaoAtivaItem]


class Dnd5eSincronizarHpCondicoesRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)
    condicoes: List[Dnd5eCondicaoAtivaItem] = Field(default_factory=list)


class Dnd5eConjurarRequest(BaseModel):
    conjurador_id: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=120)
    classe: str = Field(..., max_length=50)
    nivel_personagem: int = Field(..., ge=1, le=20)
    magia_id: int
    personagem_id: Optional[int] = Field(
        None, description="Se informado, exige magia no grimório"
    )
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    mod_inteligencia: int = Field(default=0, ge=-5, le=20)
    mod_sabedoria: int = Field(default=0, ge=-5, le=20)
    mod_carisma: int = Field(default=0, ge=-5, le=20)
    mod_destreza: int = Field(default=0, ge=-5, le=20)
    mod_constituicao: int = Field(default=0, ge=-5, le=20)
    espacos_por_nivel: List[int] = Field(default_factory=list)
    espacos_usados_por_nivel: List[int] = Field(default_factory=list)
    magia_concentracao_id: Optional[int] = None
    nivel_slot_usado: Optional[int] = Field(
        None,
        ge=1,
        le=9,
        description="Upcast: nível do espaço gasto (≥ nível da magia)",
    )
    magias_preparadas_ids: List[int] = Field(default_factory=list)
    validar_preparacao: bool = False
    teste_resistencia_mod_alvo: Optional[int] = Field(None, ge=-5, le=20)
    rolagem_salvaguarda_alvo: Optional[int] = Field(None, ge=1, le=20)
    ac_alvo: Optional[int] = Field(
        None, ge=0, le=40, description="CA para ataque mágico"
    )
    rolagem_ataque_d20: Optional[int] = Field(None, ge=1, le=20)
    bonus_ataque_extra: int = Field(default=0, ge=-20, le=20)
    condicoes_atacante: List[str] = Field(default_factory=list)
    condicoes_alvo: List[str] = Field(default_factory=list)
    como_ritual: bool = False
    confirmar_material_consumido: bool = False
    armadura_slug: Optional[str] = Field(None, max_length=80)
    escudo_slug: Optional[str] = Field(None, max_length=80)


class Dnd5eConjurarResponse(BaseModel):
    sucesso: bool
    mensagem: str
    dc: int = Field(ge=0)
    espacos_usados_por_nivel: List[int] = Field(default_factory=list)
    magia_concentracao_id: Optional[int] = None
    dano_total: Optional[int] = None
    magia_nome: Optional[str] = None
    magia_nivel: Optional[int] = None
    nivel_slot_gasto: Optional[int] = None
    teste_resistencia: Optional[str] = None
    salvaguarda_passou: Optional[bool] = None
    salvaguarda_rolagem: Optional[int] = Field(None, ge=1, le=20)
    dano_aplicar: Optional[int] = Field(
        None,
        ge=0,
        description="Dano efetivo após resistência (metade se passou no save)",
    )
    componentes: Optional[str] = None
    requer_concentracao: bool = False
    ritual: bool = False
    requer_ataque_magico: bool = False
    ataque_rolagem: Optional[int] = None
    ataque_total: Optional[int] = None
    ataque_acertou: Optional[bool] = None
    ataque_critico: bool = False
    conjurada_como_ritual: bool = False
    material_consumido_confirmado: bool = False


class Dnd5eConcentracaoTesteRequest(BaseModel):
    conjurador_id: str = Field(..., max_length=40)
    dano_recebido: int = Field(..., ge=0)
    mod_constituicao: int = Field(default=0, ge=-5, le=20)
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    magia_concentracao_id: Optional[int] = None
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)
    rolagem_d20_secundaria: Optional[int] = Field(None, ge=1, le=20)
    feats: List[str] = Field(default_factory=list)


class Dnd5eConcentracaoTesteResponse(BaseModel):
    manteve_concentracao: bool
    dc: int
    rolagem: int
    rolagem_secundaria: Optional[int] = Field(None, ge=1, le=20)
    war_caster_vantagem: bool = False
    total: int
    magia_concentracao_id: Optional[int] = None
    mensagem: str


class Dnd5eDeathSaveRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)
    death_failures: int = Field(default=0, ge=0, le=10)
    death_successes: int = Field(default=0, ge=0, le=10)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)


class Dnd5eDeathSaveResponse(BaseModel):
    rolagem: int = Field(ge=1, le=20)
    death_failures: int = Field(ge=0)
    death_successes: int = Field(ge=0)
    hp_atual: int = Field(ge=0)
    status_vida: str
    mensagem: str


class Dnd5eDanoHpRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)
    hp_max: int = Field(..., ge=1)
    dano: int = Field(..., ge=0)
    death_failures: int = Field(default=0, ge=0, le=10)
    death_successes: int = Field(default=0, ge=0, le=10)
    is_critico: bool = False
    status_vida: str = Field(
        default="vivo",
        max_length=20,
        description="vivo | inconsciente | estabilizado | morto",
    )
    raca_slug: Optional[str] = Field(
        None,
        max_length=40,
        description="Raça do alvo (traits: resistência veneno anão)",
    )
    raca_variante_slug: Optional[str] = Field(None, max_length=40)
    tipo_dano: str = Field(
        default="",
        max_length=32,
        description="Ex.: veneno, cortante, fogo",
    )


class Dnd5eDanoHpResponse(BaseModel):
    hp_atual: int = Field(ge=0)
    death_failures: int = Field(ge=0)
    death_successes: int = Field(ge=0)
    status_vida: str
    morte_instantanea: bool = False
    mensagem: str
    dano_aplicado: int = Field(default=0, ge=0)
    dano_original: Optional[int] = Field(None, ge=0)
    mensagem_racial: str = Field(default="", max_length=120)


class Dnd5eEstabilizarRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)
    death_failures: int = Field(default=0, ge=0, le=10)
    death_successes: int = Field(default=0, ge=0, le=10)
    metodo: str = Field(
        default="medicina",
        max_length=20,
        description="medicina (CD 10) | magia",
    )
    mod_medicina: int = Field(default=0, ge=-5, le=20)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)


class Dnd5eEstabilizarResponse(BaseModel):
    death_failures: int = Field(ge=0)
    death_successes: int = Field(ge=0)
    status_vida: str
    sucesso: bool
    rolagem: Optional[int] = Field(None, ge=1, le=20)
    total_medicina: Optional[int] = None
    mensagem: str


class Dnd5eEconomiaTurnoState(BaseModel):
    acao_usada: bool = False
    bonus_acao_usada: bool = False
    movimento_usado_metros: float = Field(default=0.0, ge=0)
    reacao_usada: bool = False
    velocidade_metros: float = Field(default=9.0, ge=0)
    esquivando: bool = False
    desengajado: bool = False
    ajuda_alvo_id: str = Field(default="", max_length=40)


class Dnd5eEconomiaTurnoRequest(BaseModel):
    economia: Dnd5eEconomiaTurnoState = Field(default_factory=Dnd5eEconomiaTurnoState)
    tipo: str = Field(
        ...,
        max_length=20,
        description="acao | bonus_acao | movimento | reacao | dash | dodge | disengage | help | reset",
    )
    metros: float = Field(default=0.0, ge=0, description="Metros ao gastar movimento")
    ajuda_alvo_id: str = Field(default="", max_length=40)


class Dnd5eEconomiaTurnoResponse(BaseModel):
    economia: Dnd5eEconomiaTurnoState
    mensagem: str = ""


class Dnd5eOportunidadeRequest(BaseModel):
    str_mod: int = Field(default=0, ge=-5, le=20)
    dex_mod: int = Field(default=0, ge=-5, le=20)
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    ac_alvo: int = Field(..., ge=0, le=40)
    arma_slug: Optional[str] = Field(None, max_length=80)
    feats: List[str] = Field(default_factory=list)
    raca_slug: Optional[str] = Field(None, max_length=40)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)
    economia_atacante: Dnd5eEconomiaTurnoState = Field(
        default_factory=Dnd5eEconomiaTurnoState
    )
    alvo_desengajado: bool = False


class Dnd5eOportunidadeResponse(Dnd5eAtaqueResponse):
    economia_atacante: Dnd5eEconomiaTurnoState
    tipo: str = "ataque_oportunidade"
