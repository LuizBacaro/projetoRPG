#!/usr/bin/env python3
"""Gera ``poderes_herois_arton.json`` a partir da extração PDF + legado HA-4.

Entrada: ``data/_ha_poderes_extract_raw.json`` (e opcionalmente o JSON atual
para preservar slugs/descrições do Treinador e amostras HA-4).

Uso (a partir de ``backend/``)::

    PYTHONPATH=. python3 scripts/build_poderes_herois_arton_catalogo.py

Não copia texto longo do livro — só metadados curtos + página.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DATA = Path(__file__).resolve().parents[1] / "app" / "games" / "tormenta" / "data"
_EXTRACT = _DATA / "_ha_poderes_extract_raw.json"
_OUT = _DATA / "poderes_herois_arton.json"
_LEGACY = _DATA / "poderes_herois_arton.json"

# Tabela 1-22 — poder → lista de raças (slugs do projeto).
# Multi-raça: primeira usada em raca_exigida + prerequisitos listando todas.
_RACA_TABELA_1_22: Dict[str, List[str]] = {
    # Slugs alinhados a racas_v13 + racas_herois_arton.
    # Multi-raça / raça fora do Arena: [] → só prerequisitos textuais.
    "Arma Amada": ["anao"],
    "Atração pela Pólvora": ["anao", "goblin", "kliren"],
    "Conforto do Aço": ["anao"],
    "Coração de Pedra": ["anao"],
    "Duro como Aço": ["anao"],
    "Tradição de Ayrelynn": ["anao"],
    "Cascos Poderosos": ["minotauro", "satiro"],
    "Arsenal de Lisandra": ["dahllan"],
    "Constrição Atroz": ["dahllan"],
    "Fragrância de Rosas": ["dahllan", "duende"],
    "Gavinhas": ["dahllan"],
    "Saraivada Florestal": ["dahllan"],
    "Vitalidade das Fadas": ["dahllan", "duende", "satiro", "silfide"],
    "Crescimento Feérico": ["duende", "silfide"],
    "Glamour": ["duende", "eiradaan", "silfide"],
    "Glamour Maior": ["duende", "eiradaan", "silfide"],
    "Estirpe Arcana": ["eiradaan", "elfo"],
    "Herança Erudita": ["eiradaan", "elfo"],
    "Meditação Mística": ["eiradaan", "elfo"],
    "Sangue Mágico": ["eiradaan", "qareen", "silfide"],
    "Arquearia Élfica": ["elfo"],
    "Esgrima Élfica": ["elfo"],
    "Vigilância Élfica": ["elfo", "meio_elfo"],
    "Fúria Aterrorizante": ["galokk"],
    "Golpe dos Titãs": ["galokk"],
    "Duas Cabeças": [],
    "Dupla Conjuração": [],
    "Dupla Inteligência": [],
    "Dupla Prontidão": [],
    "Entre as Pernas": ["goblin", "hynne"],
    "Escapada Criativa": ["goblin", "meio_elfo"],
    "Falatório Criativo": ["goblin"],
    "Golpe no Joelho": ["goblin", "hynne"],
    "Chassi Gracioso": ["golem"],
    "Programação de Combate": ["golem"],
    "Programação Holística": ["golem"],
    "Soco Foguete": ["golem"],
    "Asas de Aço": ["suraggel"],
    "Citadino": ["humano", "hynne", "meio_elfo"],
    "Comandar Aprimorado": ["humano"],
    "Estilo Clássico": ["humano"],
    "Valentia Inata": ["hynne"],
    "Exaltação do Rejeitado": [],
    "Quadridestria": [],
    "Quatro Braços": [],
    "Lógica Gnômica": ["kliren"],
    "Coro Sibilante": ["medusa"],
    "Magia Ofídica": ["medusa"],
    "Olhar Petrificante": ["medusa"],
    "Veneno Aprimorado": ["medusa"],
    "Ambição Herdada": ["meio_elfo"],
    "Arma Natural Aprimorada": [],
    "Arma Natural Hábil": [],
    "Faro Aprimorado": ["minotauro"],
    "Fúria Natural": ["minotauro"],
    "Marrada Poderosa": ["minotauro", "satiro"],
    "Protetor Eterno": ["minotauro"],
    "Protetor Táurico": ["minotauro"],
    "Explosão Óssea": ["osteon"],
    "Manipulação Esquelética": ["osteon"],
    "Ossos Afiados": ["osteon"],
    "Ajudante Nato": ["qareen"],
    "Amo": ["qareen"],
    "Familiar de Luz": ["qareen", "suraggel"],
    "Familiar de Trevas": ["qareen", "suraggel"],
    "Grande Marca de Wynna": ["qareen"],
    "Camuflagem Mimética": ["sereia_tritao"],
    "Canto da Sereia": ["sereia_tritao"],
    "Pirata Oceânico": ["sereia_tritao"],
    "Asas Extraplanares": ["suraggel"],
    "Criança da Luz": ["suraggel"],
    "Criança das Trevas": ["suraggel"],
    "Devoção Iluminada": ["suraggel"],
    "Eco Arcano": ["eiradaan"],
    "Força Titânica": ["galokk"],
    "Tradição Perdida": ["trog"],
    "Tradição Perdida Aprimorada": ["trog"],
    "Saliva Corrosiva": ["trog"],
}

# Poderes de Guerreiro faltantes na extração bicoluna (Tabela / corpo HA p.68–69).
_GUERREIRO_EXTRA = [
    ("Defesa Estratégica", "HA p.68"),
    ("Determinação Inabalável", "HA p.68"),
    ("Estrategista Inspirador", "HA p.68"),
    ("Executor", "HA p.68"),
]

# Grupo completo Tabela 1-23 (caso a extração parcial falhe).
_GRUPO_TABELA_1_23 = [
    "Abrir a Guarda",
    "Ajuda do Amador",
    "Apontar Fraqueza",
    "Barragem de Golpes",
    "Bode Expiatório",
    "Bote Coletivo",
    "Conforto Familiar",
    "Conselhos Salvadores",
    "Corrente de Corpos",
    "Defesa do Mártir",
    "Dinheiro Atrai Dinheiro",
    "Escudo Vivo",
    "Espírito de União",
    "Exército de Um Grupo Só",
    "Magia Comunitária",
    "Mão Amiga",
    "Parede de Escudos",
    "Presença Luminosa",
    "Saúde Coletiva",
    "Uma Mão Lava a Outra",
]


def _slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def _nome_key(nome: str) -> str:
    return _slug(nome)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _legacy_by_nome(legacy: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in legacy.get("poderes") or []:
        if not isinstance(row, dict):
            continue
        k = _nome_key(str(row.get("nome") or ""))
        if k and k not in out:
            out[k] = row
    return out


def _legacy_by_slug(legacy: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in legacy.get("poderes") or []:
        if not isinstance(row, dict):
            continue
        s = _slug(str(row.get("slug") or ""))
        if s:
            out[s] = row
    return out


def _item(
    *,
    nome: str,
    categoria: str,
    pagina: str,
    legacy_nome: Dict[str, Dict[str, Any]],
    used_slugs: set[str],
    classe_exigida: Optional[str] = None,
    raca_exigida: Optional[str] = None,
    prerequisitos: Optional[str] = None,
    descricao_resumo: Optional[str] = None,
    preferred_slug: Optional[str] = None,
    custo_pm: int = 0,
) -> Dict[str, Any]:
    nk = _nome_key(nome)
    leg = legacy_nome.get(nk) or {}
    slug = preferred_slug or _slug(str(leg.get("slug") or "")) or _slug(nome)
    if classe_exigida and categoria == "classe":
        # Homónimos entre classes → sufixo.
        base = _slug(nome)
        candidate = preferred_slug or _slug(str(leg.get("slug") or "")) or base
        if candidate in used_slugs and not preferred_slug:
            candidate = f"{base}_{_slug(classe_exigida)}"
        slug = candidate
    # Se slug colide, sufixar.
    if slug in used_slugs:
        alt = f"{slug}_{_slug(classe_exigida or raca_exigida or categoria)}"
        n = 2
        while alt in used_slugs:
            alt = f"{slug}_{n}"
            n += 1
        slug = alt
    used_slugs.add(slug)

    item: Dict[str, Any] = {
        "slug": slug,
        "nome": nome,
        "fonte_catalogo": "herois_arton",
        "categoria_v13": categoria,
        "custo_pm": int(leg.get("custo_pm") if leg.get("custo_pm") is not None else custo_pm),
        "pagina_referencia": str(pagina or leg.get("pagina_referencia") or "").strip()
        or f"HA",
    }
    if classe_exigida:
        item["classe_exigida"] = _slug(classe_exigida)
    if raca_exigida:
        item["raca_exigida"] = _slug(raca_exigida)
    resumo = descricao_resumo or leg.get("descricao_resumo")
    if resumo and categoria in {"combate", "destino", "magia", "tormenta", "grupo"}:
        # Amostras HA-4 antigas marcavam gerais como «Guerreiro: …».
        rs = str(resumo).strip()
        if rs.lower().startswith("guerreiro:"):
            rs = rs.split(":", 1)[1].strip()
            rs = rs[0].upper() + rs[1:] if rs else rs
        resumo = rs or None
    if resumo:
        item["descricao_resumo"] = str(resumo).strip()[:200]
    if prerequisitos:
        item["prerequisitos"] = prerequisitos
    elif leg.get("prerequisitos"):
        item["prerequisitos"] = str(leg["prerequisitos"])
    # Preservar efeitos estruturados (motor efeitos_ficha_t20) e flags do legado HA-4.
    if isinstance(leg.get("efeitos"), list) and leg["efeitos"]:
        item["efeitos"] = list(leg["efeitos"])
    if leg.get("requer_aliado_mesmo_poder"):
        item["requer_aliado_mesmo_poder"] = True
    return item


def _raca_meta(nome: str) -> Tuple[Optional[str], Optional[str]]:
    races = _RACA_TABELA_1_22.get(nome)
    if races is None:
        return None, None
    if not races:
        return None, "Pré-requisito: raça elegível (ver HA Tabela 1-22)."
    if len(races) == 1:
        return races[0], None
    return races[0], "Raças: " + ", ".join(races)


def build() -> Dict[str, Any]:
    extract = _load_json(_EXTRACT)
    legacy = _load_json(_LEGACY)
    legacy_nome = _legacy_by_nome(legacy)
    legacy_slug = _legacy_by_slug(legacy)
    used: set[str] = set()
    poderes: List[Dict[str, Any]] = []

    # 1) Treinador — preservar os 20 HA-4; acrescentar novos do extract.
    treinador_legacy = [
        r
        for r in (legacy.get("poderes") or [])
        if isinstance(r, dict) and str(r.get("categoria_v13") or "") == "treinador"
    ]
    seen_treinador = set()
    for row in treinador_legacy:
        nome = str(row.get("nome") or "").strip()
        if not nome:
            continue
        poderes.append(
            _item(
                nome=nome,
                categoria="treinador",
                pagina=str(row.get("pagina_referencia") or "HA p.18"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                classe_exigida="treinador",
                preferred_slug=_slug(str(row.get("slug") or "")),
                descricao_resumo=str(row.get("descricao_resumo") or "") or None,
                custo_pm=int(row.get("custo_pm") or 0),
            )
        )
        seen_treinador.add(_nome_key(nome))
    for row in extract.get("_meta", {}).get("treinador") or []:
        nome = str(row.get("nome") or "").strip()
        if not nome or _nome_key(nome) in seen_treinador:
            continue
        poderes.append(
            _item(
                nome=nome,
                categoria="treinador",
                pagina=str(row.get("pagina_referencia") or "HA p.18"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                classe_exigida="treinador",
            )
        )
        seen_treinador.add(_nome_key(nome))

    # 2) Gerais HA (combate/destino/magia/tormenta) — corrigir amostras mal classificadas.
    prefer_geral_slug = {
        "chuva_de_golpes": "chuva_de_golpes",
        "escudo_heroico": "escudo_heroico",
        "pancada_estonteante": "pancada_estonteante",
        "precisao_letal": "precisao_letal",
        "defesa_armada": "defesa_armada",
        "bravura_indomita": "bravura_indomita",
        "coragem_aguerida": "coragem_aguerida",
        "mobilidade": "mobilidade",
        "grandao": "grandao",
        "heroi_sete_instrumentos": "heroi_sete_instrumentos",
        "foco_habilidade": "foco_habilidade",
        "pose_assustadora": "pose_assustadora",
        "andarilho_urbano": "andarilho_urbano",
        "bolsoes_insanos": "bolsoes_insanos",
        "carapaca_corrompida": "carapaca_corrompida",
        "simetria_radial": "simetria_radial",
    }
    # Não reemitir escudo_heroico_geral (duplicata).
    for cat in ("combate", "destino", "magia", "tormenta"):
        for row in extract.get(cat) or []:
            nome = str(row.get("nome") or "").strip()
            if not nome:
                continue
            base = _slug(nome)
            pref = prefer_geral_slug.get(base)
            # Preferir slug legado exacto se existir
            if base in legacy_slug and str(legacy_slug[base].get("categoria_v13")) in {
                "combate",
                "destino",
                "magia",
                "tormenta",
                "classe",  # amostras erradas → viram gerais
            }:
                pref = base
            if nome == "Escudo Heroico":
                pref = "escudo_heroico"
            if nome == "Chuva de Golpes":
                pref = "chuva_de_golpes"
            if nome == "Pancada Estonteante":
                pref = "pancada_estonteante"
            poderes.append(
                _item(
                    nome=nome,
                    categoria=cat,
                    pagina=str(row.get("pagina_referencia") or "HA"),
                    legacy_nome=legacy_nome,
                    used_slugs=used,
                    preferred_slug=pref,
                )
            )

    # 3) Classe
    classe_seen: set[Tuple[str, str]] = set()
    for row in extract.get("classe") or []:
        nome = str(row.get("nome") or "").strip()
        classe = _slug(str(row.get("classe_exigida") or ""))
        if not nome or not classe:
            continue
        key = (_nome_key(nome), classe)
        if key in classe_seen:
            continue
        classe_seen.add(key)
        # Não duplicar gerais que a extração possa ter atribuído a classe.
        if _nome_key(nome) in {
            _nome_key(x["nome"])
            for x in poderes
            if x.get("categoria_v13") in {"combate", "destino", "magia", "tormenta"}
        }:
            continue
        preferred = None
        # Preservar slugs de amostras de classe HA-4
        leg = legacy_nome.get(_nome_key(nome))
        if leg and str(leg.get("categoria_v13")) == "classe":
            preferred = _slug(str(leg.get("slug") or ""))
        poderes.append(
            _item(
                nome=nome,
                categoria="classe",
                pagina=str(row.get("pagina_referencia") or "HA"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                classe_exigida=classe,
                preferred_slug=preferred,
            )
        )
    for nome, pag in _GUERREIRO_EXTRA:
        key = (_nome_key(nome), "guerreiro")
        if key in classe_seen:
            continue
        classe_seen.add(key)
        poderes.append(
            _item(
                nome=nome,
                categoria="classe",
                pagina=pag,
                legacy_nome=legacy_nome,
                used_slugs=used,
                classe_exigida="guerreiro",
            )
        )

    # 4) Raça
    raca_seen: set[str] = set()
    for row in extract.get("raca") or []:
        nome = str(row.get("nome") or "").strip()
        if not nome or _nome_key(nome) in raca_seen:
            continue
        raca_seen.add(_nome_key(nome))
        raca_ex = row.get("raca_exigida")
        pre = None
        mapped, pre_map = _raca_meta(nome)
        if mapped:
            raca_ex = mapped
            pre = pre_map
        elif not raca_ex:
            raca_ex, pre = _raca_meta(nome)
        # Preferir slug legado
        preferred = None
        leg = legacy_nome.get(_nome_key(nome))
        if leg and str(leg.get("categoria_v13")) == "raca":
            preferred = _slug(str(leg.get("slug") or ""))
            if leg.get("raca_exigida") and not raca_ex:
                raca_ex = leg.get("raca_exigida")
        poderes.append(
            _item(
                nome=nome,
                categoria="raca",
                pagina=str(row.get("pagina_referencia") or "HA p.84"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                raca_exigida=str(raca_ex) if raca_ex else None,
                prerequisitos=pre,
                preferred_slug=preferred,
            )
        )
    # Legado raça ausente na extração
    for row in legacy.get("poderes") or []:
        if str(row.get("categoria_v13")) != "raca":
            continue
        nome = str(row.get("nome") or "").strip()
        if not nome or _nome_key(nome) in raca_seen:
            continue
        raca_seen.add(_nome_key(nome))
        poderes.append(
            _item(
                nome=nome,
                categoria="raca",
                pagina=str(row.get("pagina_referencia") or "HA"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                raca_exigida=str(row.get("raca_exigida") or "") or None,
                preferred_slug=_slug(str(row.get("slug") or "")),
                descricao_resumo=str(row.get("descricao_resumo") or "") or None,
            )
        )

    # 5) Grupo
    grupo_seen: set[str] = set()
    for row in extract.get("grupo") or []:
        nome = str(row.get("nome") or "").strip()
        if not nome:
            continue
        grupo_seen.add(_nome_key(nome))
        preferred = None
        leg = legacy_nome.get(_nome_key(nome))
        if leg and str(leg.get("categoria_v13")) == "grupo":
            preferred = _slug(str(leg.get("slug") or ""))
        poderes.append(
            _item(
                nome=nome,
                categoria="grupo",
                pagina=str(row.get("pagina_referencia") or "HA p.92"),
                legacy_nome=legacy_nome,
                used_slugs=used,
                preferred_slug=preferred,
            )
        )
    for nome in _GRUPO_TABELA_1_23:
        if _nome_key(nome) in grupo_seen:
            continue
        grupo_seen.add(_nome_key(nome))
        poderes.append(
            _item(
                nome=nome,
                categoria="grupo",
                pagina="HA p.93",
                legacy_nome=legacy_nome,
                used_slugs=used,
            )
        )

    poderes.sort(
        key=lambda x: (
            str(x.get("categoria_v13") or "").lower(),
            str(x.get("nome") or "").lower(),
        )
    )

    from collections import Counter

    cats = Counter(p["categoria_v13"] for p in poderes)
    meta = {
        "fonte": "T20-Herois-de-Arton-v1-1.pdf — Cap. 1 (Treinador p.16–21; poderes p.54–97)",
        "nota": (
            "Catálogo completo HA: Treinador + classe + gerais + raça + grupo. "
            "Metadados curtos; textos longos ficam no livro. "
            f"Totais: {dict(cats)} (n={len(poderes)})."
        ),
        "build": "scripts/build_poderes_herois_arton_catalogo.py",
    }
    return {"_meta": meta, "poderes": poderes}


def main() -> None:
    doc = build()
    _OUT.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    from collections import Counter

    cats = Counter(p["categoria_v13"] for p in doc["poderes"])
    print(f"Wrote {_OUT} — {len(doc['poderes'])} poderes — {dict(cats)}")


if __name__ == "__main__":
    main()
