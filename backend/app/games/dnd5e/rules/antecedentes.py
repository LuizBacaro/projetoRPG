"""Antecedentes D&D 5E — traços e aplicação na ficha (Cap. 4)."""

from __future__ import annotations

import random
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.antecedentes_catalogo import ANTECEDENTES_CATALOGO
from app.games.dnd5e.data.antecedentes_tracos_catalogo import tracos_opcoes_antecedente
from app.games.dnd5e.rules.antecedente_tracos import normalizar_tracos_escolhidos
from app.games.dnd5e.rules.idiomas import normalizar_idiomas_escolhidos

_NOMES_ITEM_ANTECEDENTE: Dict[str, str] = {
    "simbolo_sagrado": "Símbolo sagrado",
    "livro_preces": "Livro de preces",
    "roupa_religiosa": "Roupas de aventureiro",
    "ferramentas_profissionais": "Ferramentas de artesão",
    "carta_guilda": "Carta de membro da guilda",
    "roupa_escura": "Roupas escuras com capuz",
    "kit_disfarce": "Kit de disfarce",
    "cajado": "Cajado",
    "armadilhas": "Armadilhas de caçador",
    "pele": "Pele de animal",
    "ferramentas_artesao": "Ferramentas de artesão",
    "pa": "Pá",
    "insignia": "Insígnia de patente",
    "trofeu": "Troféu de inimigo",
    "kit_jogos": "Kit de jogos",
    "roupa_fina": "Roupas finas",
    "instrumento": "Instrumento musical",
    "admirecao": "Admiradores",
    "porta_pergaminho": "Porta-pergaminho",
    "kit_herbalismo": "Kit de herbalismo",
    "anel_sinete": "Anel com sinete",
    "vidro_tinta": "Frasco de tinta",
    "facas": "Facas",
    "livro": "Livro de conhecimento",
    "roupa_comum": "Roupas comuns",
    "adaga": "Adaga",
    "corda": "Corda (15 m)",
    "faca": "Faca pequena",
    "mapa_cidade": "Mapa da cidade",
    "rato": "Rato de estimação",
}


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
    ferramentas: List[str] = field(default_factory=list)
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
            opcoes = tracos_opcoes_antecedente(key)
            tracos_modelo = Traco(
                personalidade=list(opcoes.get("personalidade") or []),
                ideais=list(opcoes.get("ideais") or []),
                lacos=list(opcoes.get("lacos") or []),
                fraquezas=list(opcoes.get("fraquezas") or []),
            )
            return Antecedente(
                antecedente_id=row["slug"],
                nome=str(row.get("nome", "")),
                descricao=str(row.get("descricao", "")),
                pericias=list(row.get("pericias") or []),
                ferramentas=list(row.get("ferramentas") or []),
                idiomas_qtd=int(row.get("idiomas_qtd", 0)),
                equipamento=list(row.get("equipamento") or []),
                ouro_extra=int(row.get("ouro_extra", 0)),
                tracos_modelo=tracos_modelo,
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
    personagem: PersonagemAntecedente,
    antecedente: Antecedente,
    *,
    idiomas_escolhidos: Optional[Sequence[str]] = None,
) -> None:
    personagem.antecedente_id = antecedente.antecedente_id
    personagem.pericias = _sem_duplicar_pericias(
        personagem.pericias, antecedente.pericias
    )
    if idiomas_escolhidos is not None:
        personagem.idiomas.extend(normalizar_idiomas_escolhidos(idiomas_escolhidos))
    personagem.equipamento.extend(antecedente.equipamento)
    personagem.ouro += antecedente.ouro_extra


def nome_item_antecedente(slug: str) -> str:
    chave = (slug or "").strip().lower()
    if chave in _NOMES_ITEM_ANTECEDENTE:
        return _NOMES_ITEM_ANTECEDENTE[chave]
    return chave.replace("_", " ").strip().title() or chave


def _item_inventario_antecedente(slug: str, antecedente_slug: str) -> Dict[str, Any]:
    item_slug = (slug or "").strip().lower()
    return {
        "id": f"ant_{antecedente_slug}_{item_slug}_{uuid.uuid4().hex[:8]}",
        "slug": item_slug,
        "nome": nome_item_antecedente(item_slug),
        "quantidade": 1,
        "fonte": "antecedente",
        "antecedente_slug": antecedente_slug,
    }


def _remover_itens_antecedente(
    equipamentos: Sequence[Dict[str, Any]],
    antecedente_slug: str,
) -> List[Dict[str, Any]]:
    alvo = (antecedente_slug or "").strip().lower()
    if not alvo:
        return list(equipamentos)
    return [
        item
        for item in equipamentos
        if not (
            isinstance(item, dict)
            and item.get("fonte") == "antecedente"
            and str(item.get("antecedente_slug") or "").strip().lower() == alvo
        )
    ]


def sincronizar_antecedente_na_ficha(
    ficha: Dict[str, Any],
    *,
    rng: Optional[random.Random] = None,
) -> Dict[str, Any]:
    """
    Aplica equipamento, ouro, idiomas e traços do antecedente ao inventário da ficha.
    Remove itens/ouro do antecedente anterior quando o slug muda.
    """
    out = dict(ficha or {})
    slug_atual = (out.get("antecedente_slug") or "").strip().lower() or None
    slug_aplicado = (
        out.get("antecedente_inventario_slug") or ""
    ).strip().lower() or None

    if slug_atual == slug_aplicado:
        return out

    inv = dict(out.get("inventario") or {})
    equipamentos = [
        dict(item) for item in (inv.get("equipamentos") or []) if isinstance(item, dict)
    ]
    ouro_po = float(inv.get("ouro_po") or 0)
    ouro_ant_aplicado = int(out.get("antecedente_ouro_aplicado") or 0)
    idiomas_ficha = normalizar_idiomas_escolhidos(out.get("antecedente_idiomas") or [])
    tracos_ficha = normalizar_tracos_escolhidos(
        out.get("antecedente_tracos"),
        slug_atual or "",
    )
    trocou_antecedente = bool(slug_aplicado and slug_aplicado != slug_atual)

    if slug_aplicado:
        equipamentos = _remover_itens_antecedente(equipamentos, slug_aplicado)
        ouro_po = max(0.0, ouro_po - ouro_ant_aplicado)

    out.pop("antecedente_tracos", None)
    out.pop("antecedente_idiomas", None)
    out["antecedente_ouro_aplicado"] = 0
    out["antecedente_inventario_slug"] = slug_atual

    if not slug_atual:
        inv["equipamentos"] = equipamentos
        inv["ouro_po"] = ouro_po
        out["inventario"] = inv
        return out

    ant = antecedente_do_catalogo(slug_atual)
    if ant is None:
        inv["equipamentos"] = equipamentos
        inv["ouro_po"] = ouro_po
        out["inventario"] = inv
        return out

    for item_slug in ant.equipamento:
        equipamentos.append(_item_inventario_antecedente(item_slug, slug_atual))

    ouro_po += float(ant.ouro_extra)
    out["antecedente_ouro_aplicado"] = int(ant.ouro_extra)
    if trocou_antecedente:
        out["antecedente_tracos"] = {
            "personalidade": [],
            "ideais": [],
            "lacos": [],
            "fraquezas": [],
        }
    elif all(
        tracos_ficha.get(cat)
        for cat in ("personalidade", "ideais", "lacos", "fraquezas")
    ):
        out["antecedente_tracos"] = tracos_ficha
    else:
        out["antecedente_tracos"] = {
            "personalidade": [],
            "ideais": [],
            "lacos": [],
            "fraquezas": [],
        }
    if trocou_antecedente:
        out["antecedente_idiomas"] = []
    elif ant.idiomas_qtd > 0 and len(idiomas_ficha) == ant.idiomas_qtd:
        out["antecedente_idiomas"] = idiomas_ficha
    else:
        out["antecedente_idiomas"] = []

    inv["equipamentos"] = equipamentos
    inv["ouro_po"] = ouro_po
    out["inventario"] = inv
    return out


def gerar_tracos(
    antecedente: Antecedente,
    *,
    rng: Optional[random.Random] = None,
) -> Traco:
    """Gera 1 traço por categoria (PHB) a partir do catálogo."""
    r = rng or random.Random()
    modelo = antecedente.tracos_modelo
    if modelo and len(modelo.personalidade) >= 1:
        return Traco(
            personalidade=[r.choice(modelo.personalidade)],
            ideais=[r.choice(modelo.ideais)] if modelo.ideais else [],
            lacos=[r.choice(modelo.lacos)] if modelo.lacos else [],
            fraquezas=[r.choice(modelo.fraquezas)] if modelo.fraquezas else [],
        )
    pool_p = [f"Traco de personalidade ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_i = [f"Ideal ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_l = [f"Laco ({antecedente.nome}) {i}" for i in range(1, 5)]
    pool_f = [f"Fraqueza ({antecedente.nome}) {i}" for i in range(1, 5)]
    return Traco(
        personalidade=[r.choice(pool_p)],
        ideais=[r.choice(pool_i)],
        lacos=[r.choice(pool_l)],
        fraquezas=[r.choice(pool_f)],
    )
