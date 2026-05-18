"""Magia D&D 5E — espaços, CD, salvaguardas, concentração (Cap. 10–11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Literal, Optional

from app.games.dnd5e.data.spell_slots_full_caster import CLASSE_HABILIDADE_PRIMARIA
from app.games.dnd5e.data.spell_tables import (
    FULL_CASTER_SLOTS,
    HALF_CASTER_SLOTS,
    WARLOCK_SLOTS,
)
from app.games.dnd5e.rules.dados import rolar_d20
from app.games.dnd5e.rules.habilidades import calcular_bonus_proficiencia

TipoSalvacao = Literal["nenhum", "reflexos", "fortitude", "vontade"]
HabilidadePrimaria = Literal["int", "wis", "cha", "dex"]


@dataclass
class Magia:
    magia_id: str
    nome: str
    nivel: int  # 0 = truque
    escola: str = ""
    tempo_execucao: str = "acao"
    alcance: str = "9m"
    duracao: str = "instantaneo"
    teste_resistencia: TipoSalvacao = "nenhum"
    descricao: str = ""
    requer_concentracao: bool = False


@dataclass
class Conjurador:
    conjurador_id: str
    nome: str
    classe: str
    nivel: int
    habilidade_primaria: HabilidadePrimaria = "int"
    mod_habilidade: int = 0
    bonus_proficiencia: int = field(default=2)
    espacos_por_nivel: List[int] = field(default_factory=list)
    espacos_usados_por_nivel: List[int] = field(default_factory=list)
    magias_conhecidas: List[Magia] = field(default_factory=list)
    magias_preparadas: List[Magia] = field(default_factory=list)
    magia_concentracao: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.bonus_proficiencia:
            self.bonus_proficiencia = calcular_bonus_proficiencia(self.nivel)
        if not self.espacos_por_nivel:
            self.espacos_por_nivel = espacos_por_classe_nivel(self.classe, self.nivel)
        if not self.espacos_usados_por_nivel:
            self.espacos_usados_por_nivel = [0] * len(self.espacos_por_nivel)

    def espacos_disponiveis(self, nivel_magia: int) -> int:
        if nivel_magia < 0 or nivel_magia >= len(self.espacos_por_nivel):
            return 0
        return max(
            0,
            self.espacos_por_nivel[nivel_magia]
            - self.espacos_usados_por_nivel[nivel_magia],
        )


def habilidade_primaria_classe(classe: str) -> HabilidadePrimaria:
    slug = (classe or "").strip().lower()
    chave = CLASSE_HABILIDADE_PRIMARIA.get(slug, "int")
    return chave  # type: ignore[return-value]


def max_nivel_magia_conjuravel(classe: str, nivel: int) -> int:
    """Maior nível de magia para o qual o personagem tem espaço (PHB 5e)."""
    slots = espacos_por_classe_nivel(classe, nivel)
    for idx in range(len(slots) - 1, 0, -1):
        if slots[idx] > 0:
            return idx
    return 0


def espacos_por_classe_nivel(classe: str, nivel: int) -> List[int]:
    """Espaços por nível de magia (índice = nível da magia). Truques no índice 0."""
    slug = (classe or "").strip().lower()
    nivel = max(1, min(20, nivel))
    if slug in ("bruxo", "warlock"):
        qtd, slot_lvl = WARLOCK_SLOTS[nivel]
        arr = [0] * 10
        arr[slot_lvl] = qtd
        return arr
    if slug in ("paladino", "paladin", "patrulheiro", "ranger"):
        return list(HALF_CASTER_SLOTS[nivel])
    return list(FULL_CASTER_SLOTS[nivel])


def calcular_dc_magia(bonus_proficiencia: int, mod_habilidade: int) -> int:
    """CD = 8 + proficiência + mod da habilidade de conjuração."""
    return 8 + bonus_proficiencia + mod_habilidade


def lancar_magia(
    conjurador: Conjurador,
    magia: Magia,
    *,
    nivel_slot: Optional[int] = None,
    ignorar_slot: bool = False,
) -> bool:
    """Gasta espaço (truques não gastam). nivel_slot permite upcast (≥ nível da magia)."""
    if magia.nivel > 0 and not ignorar_slot:
        slot = max(magia.nivel, int(nivel_slot or magia.nivel))
        if slot >= len(conjurador.espacos_usados_por_nivel):
            return False
        if conjurador.espacos_disponiveis(slot) <= 0:
            return False
        conjurador.espacos_usados_por_nivel[slot] += 1

    dur = (magia.duracao or "").lower()
    if magia.requer_concentracao or "concentr" in dur:
        conjurador.magia_concentracao = magia.magia_id
    return True


def componentes_resumo(
    verbal: bool,
    somatico: bool,
    material: Optional[str] = None,
) -> str:
    parts = []
    if verbal:
        parts.append("V")
    if somatico:
        parts.append("S")
    if material:
        parts.append(f"M ({material[:60]})" if len(material) > 60 else f"M ({material})")
    elif material is not None and material == "":
        parts.append("M")
    return ", ".join(parts) if parts else "—"


def recuperar_espacos_repouso_longo(conjurador: Conjurador) -> None:
    """Repouso longo: restaura todos os espaços."""
    conjurador.espacos_usados_por_nivel = [0] * len(conjurador.espacos_por_nivel)


def salvaguarda_atinge_dc(
    mod_salvacao: int,
    dc: int,
    *,
    rolagem_d20: Optional[int] = None,
    bonus_extra: int = 0,
    rng: Optional[Callable[[int, int], int]] = None,
) -> bool:
    """True se o alvo passa (total >= DC)."""
    roll = rolagem_d20 if rolagem_d20 is not None else rolar_d20(rng)
    return roll + mod_salvacao + bonus_extra >= dc


def teste_concentracao(
    conjurador: Conjurador,
    dano_recebido: int,
    mod_constituicao: int,
    *,
    rolagem_d20: Optional[int] = None,
    bonus_proficiencia: Optional[int] = None,
) -> bool:
    """Teste de concentração: DC 10 ou metade do dano (o maior). True = mantém."""
    if not conjurador.magia_concentracao:
        return True
    dc = max(10, dano_recebido // 2)
    prof = (
        bonus_proficiencia
        if bonus_proficiencia is not None
        else conjurador.bonus_proficiencia
    )
    roll = rolagem_d20 if rolagem_d20 is not None else rolar_d20()
    total = roll + mod_constituicao + prof
    if total < dc:
        conjurador.magia_concentracao = None
        return False
    return True
