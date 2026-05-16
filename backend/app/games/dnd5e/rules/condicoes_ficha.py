"""Condições de combate persistidas em ficha_json (arena 5e)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.rules.combate import CONDICOES_PADRAO, normalizar_condicao_slug

CHAVE_FICHA_ARENA_CONDICOES = "arena_condicoes"
DURACAO_PERMANENTE = -1
ORIGEM_CONDICAO_HP = "hp"
SLUG_INCONSCIENTE = "inconsciente"


@dataclass(frozen=True)
class CondicaoAtiva:
    slug: str
    duracao_turnos: int = DURACAO_PERMANENTE
    origem: Optional[str] = None

    def para_dict(self) -> Dict[str, Any]:
        row: Dict[str, Any] = {
            "slug": self.slug,
            "duracao_turnos": self.duracao_turnos,
        }
        if self.origem:
            row["origem"] = self.origem
        return row


def _duracao_valida(val: Any) -> int:
    if val is None:
        return DURACAO_PERMANENTE
    try:
        d = int(val)
    except (TypeError, ValueError):
        return DURACAO_PERMANENTE
    if d < DURACAO_PERMANENTE:
        return DURACAO_PERMANENTE
    return d


def normalizar_condicao_ativa(raw: Any) -> Optional[CondicaoAtiva]:
    """Aceita slug string (legado) ou dict {slug, duracao_turnos}."""
    if isinstance(raw, str):
        slug = normalizar_condicao_slug(raw)
        if not slug:
            return None
        return CondicaoAtiva(slug=slug, duracao_turnos=DURACAO_PERMANENTE)
    if isinstance(raw, dict):
        slug = normalizar_condicao_slug(str(raw.get("slug") or ""))
        if not slug:
            return None
        origem = raw.get("origem")
        origem_str = str(origem).strip() if origem else None
        return CondicaoAtiva(
            slug=slug,
            duracao_turnos=_duracao_valida(raw.get("duracao_turnos")),
            origem=origem_str or None,
        )
    return None


def normalizar_condicoes_ficha(raw: Any) -> List[Dict[str, Any]]:
    """Valida slugs PHB e remove duplicatas (mantém a última entrada por slug)."""
    if not raw:
        return []
    if not isinstance(raw, list):
        return []
    por_slug: Dict[str, CondicaoAtiva] = {}
    for item in raw:
        c = normalizar_condicao_ativa(item)
        if c is None:
            continue
        if c.slug not in CONDICOES_PADRAO:
            continue
        por_slug[c.slug] = c
    return [por_slug[s].para_dict() for s in sorted(por_slug)]


def condicoes_ficha_de_resposta(
    ficha: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    if not ficha:
        return []
    return normalizar_condicoes_ficha(ficha.get(CHAVE_FICHA_ARENA_CONDICOES))


def slugs_de_condicoes(condicoes: Sequence[Any]) -> List[str]:
    return [c["slug"] for c in normalizar_condicoes_ficha(list(condicoes))]


def decrementar_condicoes_turno(condicoes: Sequence[Any]) -> List[Dict[str, Any]]:
    """
    Decrementa duracao_turnos de cada condição do combatente ao fim do turno dele.
    Remove entradas que chegarem a 0; -1 = permanente (não decrementa).
    """
    normalizadas = normalizar_condicoes_ficha(list(condicoes))
    restantes: List[Dict[str, Any]] = []
    for row in normalizadas:
        slug = row["slug"]
        duracao = int(row.get("duracao_turnos", DURACAO_PERMANENTE))
        if duracao == DURACAO_PERMANENTE:
            restantes.append(row)
            continue
        nova = duracao - 1
        if nova > 0:
            restantes.append({"slug": slug, "duracao_turnos": nova})
    return restantes


def mesclar_arena_condicoes_em_ficha(
    ficha: Dict[str, Any],
    condicoes: Sequence[Any],
) -> Dict[str, Any]:
    out = dict(ficha)
    out[CHAVE_FICHA_ARENA_CONDICOES] = normalizar_condicoes_ficha(list(condicoes))
    return out


def sincronizar_condicoes_por_hp(
    hp_atual: int,
    condicoes: Sequence[Any],
) -> List[Dict[str, Any]]:
    """
    PHB: 0 PV → inconsciente. Remove apenas inconsciente com origem automática (hp)
    quando PV > 0; condições manuais permanecem.
    """
    hp = max(0, int(hp_atual))
    manual_e_outras: List[Dict[str, Any]] = []
    for row in normalizar_condicoes_ficha(list(condicoes)):
        if (
            row.get("slug") == SLUG_INCONSCIENTE
            and row.get("origem") == ORIGEM_CONDICAO_HP
        ):
            continue
        manual_e_outras.append(row)
    if hp <= 0:
        manual_e_outras.append(
            {
                "slug": SLUG_INCONSCIENTE,
                "duracao_turnos": DURACAO_PERMANENTE,
                "origem": ORIGEM_CONDICAO_HP,
            }
        )
    return normalizar_condicoes_ficha(manual_e_outras)
