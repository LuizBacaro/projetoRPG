"""Catálogo mínimo de perícias GURPS Lite e validações iniciais."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class PericiaLite:
    nome: str
    tipo: str
    atributo_base: str
    atributo_minimo: Optional[int] = None


_PERICIAS_LITE: tuple[PericiaLite, ...] = (
    PericiaLite("Briga", "E", "dx"),
    PericiaLite("Furtividade", "M", "dx"),
    PericiaLite("Primeiros Socorros", "E", "iq"),
    PericiaLite("Observacao", "M", "per"),
    PericiaLite("Sobrevivencia", "M", "per"),
    PericiaLite("Medicina", "D", "iq", atributo_minimo=11),
)

_PERICIAS_INDEX = {p.nome.casefold(): p for p in _PERICIAS_LITE}


def listar_pericias_lite() -> list[dict]:
    return [
        {
            "nome": p.nome,
            "tipo": p.tipo,
            "atributo_base": p.atributo_base,
            "atributo_minimo": p.atributo_minimo,
        }
        for p in _PERICIAS_LITE
    ]


def obter_pericia_lite(nome: str) -> Optional[PericiaLite]:
    return _PERICIAS_INDEX.get(str(nome or "").strip().casefold())


def validar_pre_requisitos_lite(
    *,
    pericias: Iterable[dict],
    st_valor: int,
    dx_valor: int,
    iq_valor: int,
    ht_valor: int,
    percepcao_valor: int,
) -> list[str]:
    attrs = {
        "st": int(st_valor or 0),
        "dx": int(dx_valor or 0),
        "iq": int(iq_valor or 0),
        "ht": int(ht_valor or 0),
        "per": int(percepcao_valor or 0),
    }
    erros: list[str] = []
    for s in pericias or []:
        nome = str((s or {}).get("nome", "")).strip()
        if not nome:
            continue
        cat = obter_pericia_lite(nome)
        if cat is None or cat.atributo_minimo is None:
            continue
        atual = int(attrs.get(cat.atributo_base, 0))
        if atual < cat.atributo_minimo:
            erros.append(
                f"{cat.nome} requer {cat.atributo_base.upper()} >= {cat.atributo_minimo}"
            )
    return erros

