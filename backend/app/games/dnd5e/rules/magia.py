"""Magia D&D 5E — espaços, CD, salvaguardas, concentração (Cap. 10–11)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Literal, Optional

from app.games.dnd5e.data.spell_slots_full_caster import CLASSE_HABILIDADE_PRIMARIA
from app.games.dnd5e.data.spell_tables import (
    BARD_SLOTS,
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
    if slug in ("bardo", "bard"):
        return list(BARD_SLOTS[nivel])
    if slug in ("paladino", "paladin", "patrulheiro", "ranger"):
        return list(HALF_CASTER_SLOTS[nivel])
    return list(FULL_CASTER_SLOTS[nivel])


CUSTO_PONTO_FEITICARIA_SLOT: dict[int, int] = {1: 2, 2: 3, 3: 5, 4: 6, 5: 7}


def truque_multiplicador_dados(nivel_personagem: int) -> int:
    """PHB: truques escalam dados aos níveis 5, 11 e 17 do personagem."""
    n = max(1, int(nivel_personagem))
    if n >= 17:
        return 4
    if n >= 11:
        return 3
    if n >= 5:
        return 2
    return 1


def save_causa_metade_dano(
    *,
    dano: Optional[str],
    save_tipo: str,
    slug: str = "",
) -> bool:
    """True se passar no save reduz o dano à metade (PHB padrão; exceções por slug)."""
    if not dano or (save_tipo or "nenhum").strip().lower() in ("", "nenhum"):
        return False
    slug_l = (slug or "").strip().lower()
    if slug_l in {
        "disintegrate",
        "desintegrar",
        "power-word-kill",
        "palavra-poder-matar",
    }:
        return False
    return True


def _parse_bonus_dados_upcast(
    descricao: Optional[str], delta_niveis: int
) -> Optional[str]:
    if not descricao or delta_niveis <= 0:
        return None
    import re

    m = re.search(r"\+?\s*(\d+)\s*d\s*(\d+)", str(descricao), re.I)
    if not m:
        return None
    per_level = int(m.group(1))
    faces = int(m.group(2))
    return f"{per_level * delta_niveis}d{faces}"


def _somar_expressoes_dado(base: str, extra: str) -> str:
    import re

    def parse_dice(expr: str):
        m = re.match(r"^(\d+)\s*d\s*(\d+)(.*)$", str(expr).strip().lower())
        if not m:
            return None
        return int(m.group(1)), int(m.group(2)), m.group(3)

    b = parse_dice(base)
    e = parse_dice(extra)
    if b and e and b[1] == e[1]:
        return f"{b[0] + e[0]}d{b[1]}{b[2]}"
    return f"{base}+{extra}"


def escalar_dano_upcast(
    expressao: str,
    nivel_magia: int,
    nivel_slot: Optional[int],
    *,
    descricao_nivel_superior: Optional[str] = None,
) -> str:
    """Soma dados extras por slot acima do nível da magia (ex.: Bola de Fogo +1d6/nível)."""
    if nivel_slot is None or nivel_magia <= 0 or int(nivel_slot) <= int(nivel_magia):
        return str(expressao)
    delta = int(nivel_slot) - int(nivel_magia)
    bonus = _parse_bonus_dados_upcast(descricao_nivel_superior, delta)
    if not bonus:
        return str(expressao)
    return _somar_expressoes_dado(str(expressao), bonus)


def escalar_expressao_dano_truque(expressao: str, nivel_personagem: int) -> str:
    """Multiplica quantidade de dados em expressões NdX (+mod opcional)."""
    mult = truque_multiplicador_dados(nivel_personagem)
    if mult <= 1:
        return str(expressao)
    expr = str(expressao).strip().lower()
    if "d" not in expr:
        return expr
    left, right = expr.split("d", 1)
    dados = left.strip()
    if not dados.isdigit():
        return expr
    return f"{int(dados) * mult}d{right}"


def pontos_feiticaria_max(classe: str, nivel: int) -> int:
    """Feiticeiro PHB: pontos = nível (a partir do 2º)."""
    if (classe or "").strip().lower() not in ("feiticeiro", "sorcerer"):
        return 0
    return max(0, int(nivel)) if int(nivel) >= 2 else 0


def custo_ponto_feiticaria_criar_slot(nivel_slot: int) -> int:
    if nivel_slot not in CUSTO_PONTO_FEITICARIA_SLOT:
        raise ValueError("Só é possível criar slots de 1º a 5º nível")
    return CUSTO_PONTO_FEITICARIA_SLOT[nivel_slot]


def recuperacao_arcana_max_niveis_slot(nivel_mago: int) -> int:
    """Total de níveis de slot recuperáveis (metade do nível de mago, arred. p/ cima)."""
    return max(0, (int(nivel_mago) + 1) // 2)


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
        parts.append(
            f"M ({material[:60]})" if len(material) > 60 else f"M ({material})"
        )
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
