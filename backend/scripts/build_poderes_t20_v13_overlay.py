#!/usr/bin/env python3
"""
Gera/atualiza `poderes_pre_requisitos_v13_overlay.json` a partir do catálogo
`talentos_mb_catalogo.json` (Cap. 2 v1.3) — pré-req estruturados para combate,
destino e magia que o parser de texto não cobre bem (nível, poder, perícia).

Uso:
  .venv/bin/python backend/scripts/build_poderes_t20_v13_overlay.py
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[1]
_CATALOGO = _ROOT / "app/games/tormenta/data/talentos_mb_catalogo.json"
_OUT = _ROOT / "app/games/tormenta/data/poderes_pre_requisitos_v13_overlay.json"

_ATTR = {
    "for": "for",
    "força": "for",
    "forca": "for",
    "des": "des",
    "destreza": "des",
    "con": "con",
    "constituição": "con",
    "constituicao": "con",
    "int": "int",
    "inteligência": "int",
    "inteligencia": "int",
    "sab": "sab",
    "sabedoria": "sab",
    "car": "car",
    "carisma": "car",
}

# Dependências poder→poder / regras especiais (livro Cap. 2)
_EXTRA: Dict[str, List[Dict[str, Any]]] = {
    "ataque preciso": [{"tipo": "poder", "slug": "ataque_poderoso"}],
    "carga de cavalaria": [{"tipo": "poder", "slug": "ginete"}],
    "arremesso potente": [{"tipo": "poder", "slug": "estilo_de_arremesso"}],
    "arremesso multiplo": [{"tipo": "poder", "slug": "estilo_de_arremesso"}],
    "ataque com escudo": [{"tipo": "poder", "slug": "estilo_de_arma_e_escudo"}],
    "bloqueio com escudo": [{"tipo": "poder", "slug": "estilo_de_arma_e_escudo"}],
    "ataque pesado": [{"tipo": "poder", "slug": "estilo_de_duas_maos"}],
    "arma secundaria grande": [{"tipo": "poder", "slug": "estilo_de_duas_armas"}],
    "piqueiro": [{"tipo": "poder", "slug": "estilo_de_arma_longa"}],
    "mira apurada": [{"tipo": "poder", "slug": "estilo_de_disparo"}],
    "foco em arma": [{"tipo": "proficiencia_arma"}],
    "magia acelerada": [{"tipo": "conjura_magias"}],
    "magia ampliada": [{"tipo": "conjura_magias"}],
    "magia discreta": [{"tipo": "conjura_magias"}],
    "magia ilimitada": [{"tipo": "conjura_magias"}],
    "foco em magia": [{"tipo": "conjura_magias"}],
    "celebrar ritual": [{"tipo": "conjura_magias"}],
    "escrever pergaminho": [{"tipo": "conjura_magias"}],
    "preparar pocao": [{"tipo": "conjura_magias"}],
}


def _norm(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def _slug(nome: str) -> str:
    return re.sub(r"\s+", "_", _norm(nome)).strip("_")


def _parse_texto(prereq: str) -> List[Dict[str, Any]]:
    t = str(prereq or "").strip()
    if not t or t in ("—", "-", "n/a"):
        return []
    out: List[Dict[str, Any]] = []
    for m in re.finditer(
        r"\b(For(?:ça|ca)?|Des(?:treza)?|Con(?:stitui[cç][aã]o)?|"
        r"Int(?:elig[eê]ncia)?|Sab(?:edoria)?|Car(?:isma)?)\s*([+-]?\d+)\b",
        t,
        re.I,
    ):
        key = unicodedata.normalize("NFKD", m.group(1)).encode("ascii", "ignore").decode()
        key = key.lower()[:3]
        ch = _ATTR.get(key) or _ATTR.get(m.group(1).lower())
        if ch:
            out.append({"tipo": "atributo_min", "atributo": ch, "valor": int(m.group(2))})
    for m in re.finditer(r"(\d+)\s*º\s*n[ií]vel", t, re.I):
        out.append({"tipo": "nivel_min", "valor": int(m.group(1))})
    # perícias comuns citadas sozinhas
    for nome, slug in (
        ("Luta", "luta"),
        ("Pontaria", "pontaria"),
        ("Cavalgar", "cavalgar"),
        ("Enganação", "enganacao"),
        ("Intimidação", "intimidacao"),
        ("Iniciativa", "iniciativa"),
        ("Percepção", "percepcao"),
        ("Cura", "cura"),
        ("Misticismo", "misticismo"),
        ("Religião", "religiao"),
    ):
        if re.search(rf"\b{re.escape(nome)}\b", t, re.I):
            out.append({"tipo": "pericia_treinada", "slug": slug})
    if re.search(r"lan[cç]ar magias", t, re.I) or re.search(
        r"habilidade magias", t, re.I
    ):
        out.append({"tipo": "conjura_magias"})
    if re.search(r"profici[eê]ncia com a arma", t, re.I):
        out.append({"tipo": "proficiencia_arma"})
    return out


def main() -> int:
    data = json.loads(_CATALOGO.read_text(encoding="utf-8"))
    overlay: Dict[str, List[Dict[str, Any]]] = {}
    for row in data.get("itens") or []:
        if not isinstance(row, dict):
            continue
        cat = str(row.get("categoria_v13") or "")
        if cat not in ("combate", "destino", "magia"):
            continue
        nome = str(row.get("nome") or "").strip()
        key = _norm(nome)
        if not key:
            continue
        reqs = _parse_texto(str(row.get("prerequisitos") or ""))
        for extra in _EXTRA.get(key, []):
            if extra not in reqs:
                reqs.append(dict(extra))
        # dedupe por (tipo, atributo/slug/valor)
        uniq: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for r in reqs:
            sig = json.dumps(r, sort_keys=True, ensure_ascii=False)
            if sig in seen:
                continue
            seen.add(sig)
            uniq.append(r)
        if uniq:
            overlay[key] = uniq

    payload = {
        "_meta": {
            "fonte": "Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf — Cap. 2 p.124–131",
            "nota": (
                "Overlay por nome normalizado; gerado por "
                "backend/scripts/build_poderes_t20_v13_overlay.py a partir do catálogo."
            ),
            "total": len(overlay),
        },
        "overlay_por_nome": dict(sorted(overlay.items())),
    }
    _OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Overlay: {len(overlay)} poderes → {_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
