"""Antecedentes D&D 5E — traços e aplicação na ficha (Cap. 4)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

from app.games.dnd5e.data.antecedentes_catalogo import ANTECEDENTES_CATALOGO


@dataclass
class Traco:
    personalidade: List[str] = field(default_factory=list)
    ideais: List[str] = field(default_factory=list)
    lacos: List[str] = field(default_factory=list)
    fraquezas: List[str] = field(default_factory=list)


@dataclass
class Antecedente:
    antecedente_id: str
    nome: str
    descricao: str = ""
    pericias: List[str] = field(default_factory=list)
    idiomas_qtd: int = 0
    equipamento: List[str] = field(default_factory=list)
    ouro_extra: int = 0
    tracos_modelo: Optional[Traco] = None


@dataclass
class PersonagemAntecedente:
    pericias: List[str] = field(default_factory=list)
    idiomas: List[str] = field(default_factory=list)
    equipamento: List[str] = field(default_factory=list)
    ouro: int = 0
    antecedente_id: Optional[str] = None
    tracos: Traco = field(default_factory=Traco)


def antecedente_do_catalogo(slug: str) -> Optional[Antecedente]:
    key = slug.strip().lower()
    for row in ANTECEDENTES_CATALOGO:
        if row.get("slug") == key:
            return Antecedente(
                antecedente_id=row["slug"],
                nome=str(row.get("nome", "")),
                descricao=str(row.get("descricao", "")),
                pericias=list(row.get("pericias") or []),
                idiomas_qtd=int(row.get("idiomas_qtd", 0)),
                equipamento=list(row.get("equipamento") or []),
                ouro_extra=int(row.get("ouro_extra", 0)),
            )
    return None


def listar_antecedentes() -> List[Antecedente]:
    return [
        a for s in ANTECEDENTES_CATALOGO if (a := antecedente_do_catalogo(s["slug"]))
    ]


def _sem_duplicar_pericias(
    existentes: Sequence[str], novas: Sequence[str]
) -> List[str]:
    low = {p.lower() for p in existentes}
    out = list(existentes)
    for p in novas:
        if p.lower() not in low:
            out.append(p)
            low.add(p.lower())
    return out


def aplicar_antecedente(
    personagem: PersonagemAntecedente, antecedente: Antecedente
) -> None:
    personagem.antecedente_id = antecedente.antecedente_id
    personagem.pericias = _sem_duplicar_pericias(
        personagem.pericias, antecedente.pericias
    )
    for _ in range(antecedente.idiomas_qtd):
        personagem.idiomas.append(f"idioma_extra_{len(personagem.idiomas) + 1}")
    personagem.equipamento.extend(antecedente.equipamento)
    personagem.ouro += antecedente.ouro_extra


def gerar_tracos(
    antecedente: Antecedente,
    *,
    rng: Optional[random.Random] = None,
) -> Traco:
    """Gera 2 traços por categoria (amostra genérica se o catálogo não tiver listas)."""
    r = rng or random.Random()
    modelo = antecedente.tracos_modelo
    if modelo and len(modelo.personalidade) >= 2:
        return Traco(
            personalidade=r.sample(modelo.personalidade, 2),
            ideais=r.sample(modelo.ideais, min(2, len(modelo.ideais))),
            lacos=r.sample(modelo.lacos, min(2, len(modelo.lacos))),
            fraquezas=r.sample(modelo.fraquezas, min(2, len(modelo.fraquezas))),
        )
    pool_p = [f"Traco de personalidade ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_i = [f"Ideal ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_l = [f"Laco ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_f = [f"Fraqueza ({antecedente.nome}) {i}" for i in range(1, 5)]
    return Traco(
        personalidade=r.sample(pool_p, 2),
        ideais=r.sample(pool_i, 2),
        lacos=r.sample(pool_l, 2),
        fraquezas=r.sample(pool_f, 2),
    )
