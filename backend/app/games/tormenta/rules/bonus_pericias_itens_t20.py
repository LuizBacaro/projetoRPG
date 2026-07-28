"""Agrega bônus/penalidade de perícia a partir de melhorias de itens superiores (RF-T14).

MVP: lê ``melhorias[]`` (slugs) em itens passados pelo cliente (ataques/armaduras)
e aplica mods de ``itens_superiores_v13.json``:

- chaves de perícia (``diplomacia``, ``enganacao``, …) → ``outros``
- ``ocultar`` → ``bonus_uso`` quando uso_id == ``ocultar`` e perícia Ladinagem
- ``pericia`` genérico (Aprimorado) → ignorado sem ``pericia_slug`` no item
"""

from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence

from app.games.tormenta.rules.itens_superiores_v13_t20 import lista_melhorias_v13

# Mods que não são perícia / uso
_IGNORAR_MODS = frozenset(
    {
        "ataque",
        "dano",
        "defesa",
        "ca",
        "critico",
        "deslocamento",
        "espacos",
        "penalidade_armadura",
        "rd",
        "pv",
        "pm",
    }
)

# uso_id canônico ← chave no mods da melhoria
_MOD_PARA_USO: Dict[str, tuple[str, str]] = {
    "ocultar": ("ladinagem", "ocultar"),
}


def slug_pericia_nome(nome: str) -> str:
    s = unicodedata.normalize("NFKD", str(nome or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = s.replace(" ", "_")
    for a, b in (
        ("ç", "c"),
        ("ã", "a"),
        ("õ", "o"),
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    ):
        s = s.replace(a, b)
    # já sem acentos via NFKD; limpar restos
    s = "".join(c if c.isalnum() or c == "_" else "_" for c in s)
    s = "_".join(p for p in s.split("_") if p)
    aliases = {
        "atuacao": "atuacao",
        "enganacao": "enganacao",
        "percepcao": "percepcao",
        "religiao": "religiao",
        "sobrevivencia": "sobrevivencia",
        "intimidacao": "intimidacao",
        "intuicao": "intuicao",
        "investigacao": "investigacao",
        "oficio": "oficio",
    }
    return aliases.get(s, s)


def _catalogo_por_slug() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in lista_melhorias_v13():
        slug = str(row.get("slug") or "").strip().lower()
        if slug:
            out[slug] = row
    return out


def agregar_bonus_pericia_itens(
    *,
    pericia_slug: str,
    uso_id: Optional[str] = None,
    itens: Optional[Sequence[Mapping[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Retorna ``{ outros, bonus_uso, fontes }``.

    ``itens``: lista de dicts com ``melhorias: string[]`` e opcional
    ``bonus_ativo`` (default True), ``pericia_slug`` (para Aprimorado).
    """
    alvo = slug_pericia_nome(pericia_slug)
    uso = str(uso_id or "").strip().lower() or None
    outros = 0
    bonus_uso = 0
    fontes: List[Dict[str, Any]] = []
    if not alvo or not itens:
        return {"outros": 0, "bonus_uso": 0, "fontes": []}

    cat = _catalogo_por_slug()
    for raw in itens:
        if not isinstance(raw, Mapping):
            continue
        if raw.get("bonus_ativo") is False:
            continue
        mel_list = raw.get("melhorias") or []
        if not isinstance(mel_list, (list, tuple)):
            continue
        item_pericia = slug_pericia_nome(str(raw.get("pericia_slug") or ""))
        for mel_slug in mel_list:
            slug = str(mel_slug or "").strip().lower()
            if not slug or slug not in cat:
                continue
            mods = cat[slug].get("mods") or {}
            if not isinstance(mods, dict):
                continue
            nome_mel = str(cat[slug].get("nome") or slug)
            for mod_key, mod_val in mods.items():
                mk = str(mod_key or "").strip().lower()
                if mk in _IGNORAR_MODS:
                    continue
                try:
                    val = int(mod_val)
                except (TypeError, ValueError):
                    continue
                if val == 0:
                    continue

                # Aprimorado: +1 na perícia do item
                if mk == "pericia":
                    if item_pericia and item_pericia == alvo:
                        outros += val
                        fontes.append(
                            {
                                "melhoria": slug,
                                "nome": nome_mel,
                                "valor": val,
                                "escopo": "pericia",
                            }
                        )
                    continue

                # Uso específico (ex. ocultar)
                if mk in _MOD_PARA_USO:
                    p_req, u_req = _MOD_PARA_USO[mk]
                    if alvo == p_req and uso == u_req:
                        bonus_uso += val
                        fontes.append(
                            {
                                "melhoria": slug,
                                "nome": nome_mel,
                                "valor": val,
                                "escopo": "uso",
                                "uso_id": u_req,
                            }
                        )
                    continue

                # Perícia nomeada no mods
                if slug_pericia_nome(mk) == alvo:
                    outros += val
                    fontes.append(
                        {
                            "melhoria": slug,
                            "nome": nome_mel,
                            "valor": val,
                            "escopo": "pericia",
                        }
                    )

    return {
        "outros": int(outros),
        "bonus_uso": int(bonus_uso),
        "fontes": fontes,
    }


def aplicar_agregado_em_totais(
    *,
    outros_ficha: int,
    bonus_uso_ficha: int,
    agregado: Mapping[str, Any],
) -> Dict[str, int]:
    """Soma ficha + itens sem mutar a ficha."""
    return {
        "outros": int(outros_ficha) + int(agregado.get("outros") or 0),
        "bonus_uso": int(bonus_uso_ficha) + int(agregado.get("bonus_uso") or 0),
        "bonus_itens": int(agregado.get("outros") or 0),
        "bonus_uso_itens": int(agregado.get("bonus_uso") or 0),
    }
