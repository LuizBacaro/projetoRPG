"""Catálogo da ficha: JSON Lite +, se existir, listas extraídas do PDF Personagens (Devir).

Se o banco tiver as tabelas `gurps_catalogo_ficha_*` populadas, GET /catalogo/lite-ficha usa o banco
para perícias / vantagens / desvantagens e mantém `meta` (custos Basic, fontes) a partir dos arquivos.
"""

from __future__ import annotations

import json
import logging
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_DIR = Path(__file__).resolve().parent
_CATALOGO_LITE_PATH = _DIR / "gurps_lite_catalogo.json"
_SUMARIO_PERSONAGENS_PATH = _DIR / "gurps_personagens_sumario_catalogo.json"


def _parse_custo_opcional(custo_texto: str | None) -> int | None:
    if not custo_texto:
        return None
    t = custo_texto.strip().lower()
    if "variável" in t or "variavel" in t:
        return None
    m = re.search(r"(-?\d+)", custo_texto.replace("–", "-"))
    if not m:
        return None
    return int(m.group(1))


def carregar_apenas_lite_json() -> dict[str, Any]:
    with open(_CATALOGO_LITE_PATH, encoding="utf-8") as f:
        return json.load(f)


def carregar_sumario_personagens_json() -> dict[str, Any] | None:
    if not _SUMARIO_PERSONAGENS_PATH.is_file():
        return None
    with open(_SUMARIO_PERSONAGENS_PATH, encoding="utf-8") as f:
        return json.load(f)


def _aplicar_sumario_sobre_catalogo(
    out: dict[str, Any], sumario: dict[str, Any]
) -> None:
    per: list[dict[str, Any]] = []
    for p in sumario.get("pericias", []):
        nome = (p.get("nome") or "").strip()
        if not nome:
            continue
        dif = p.get("dificuldade", "M")
        if dif == "VD":
            dif = "D"
        per.append(
            {
                "nome": nome,
                "atributo_base": p.get("atributo_base", "dx"),
                "dificuldade": dif,
                "nt": bool(p.get("nt")),
            }
        )

    vant: list[dict[str, Any]] = []
    for v in sumario.get("vantagens", []):
        nome = (v.get("nome") or "").strip()
        if not nome:
            continue
        ct = v.get("custo_texto")
        vant.append(
            {
                "nome": nome,
                "custo": _parse_custo_opcional(ct),
                "custo_texto": ct,
            }
        )

    desv: list[dict[str, Any]] = []
    for d in sumario.get("desvantagens", []):
        nome = (d.get("nome") or "").strip()
        if not nome:
            continue
        ct = d.get("custo_texto")
        desv.append(
            {
                "nome": nome,
                "custo": _parse_custo_opcional(ct),
                "custo_texto": ct,
            }
        )

    out["pericias"] = per
    out["vantagens"] = vant
    out["desvantagens"] = desv
    meta = out.setdefault("meta", {})
    meta["fonte_listas_personagens_pdf"] = sumario.get("meta", {})


def montar_catalogo_de_arquivos() -> dict[str, Any]:
    out = deepcopy(carregar_apenas_lite_json())
    sumario = carregar_sumario_personagens_json()
    if sumario:
        _aplicar_sumario_sobre_catalogo(out, sumario)
    return out


def _anexar_meta_diagnostico_listas(out: dict[str, Any], origem: str) -> None:
    """Ajuda a diagnosticar produção: listas vêm do Postgres ou dos JSON no deploy."""
    meta = out.setdefault("meta", {})
    meta["catalogo_listas_origem"] = origem
    meta["catalogo_listas_counts"] = {
        "pericias": len(out.get("pericias") or []),
        "vantagens": len(out.get("vantagens") or []),
        "desvantagens": len(out.get("desvantagens") or []),
    }
    meta["catalogo_sumario_pdf_presente"] = _SUMARIO_PERSONAGENS_PATH.is_file()


def carregar_catalogo_lite_ficha(db: Session | None = None) -> dict[str, Any]:
    if db is not None:
        try:
            from app.games.gurps.repositories.catalogo_ficha_repository import (
                GurpsCatalogoFichaRepository,
            )

            repo = GurpsCatalogoFichaRepository(db)
            if repo.catalogo_populado():
                out = repo.resposta_api_catalogo()
                _anexar_meta_diagnostico_listas(out, "postgres")
                return out
        except Exception as exc:
            # Migração ainda não aplicada, schema diferente, etc. — evita 500 + “falso CORS” no browser.
            logger.warning(
                "Catálogo GURPS lite-ficha: falha ao usar Postgres (%s); usando JSON embarcado.",
                exc,
                exc_info=True,
            )
            out = montar_catalogo_de_arquivos()
            _anexar_meta_diagnostico_listas(out, "arquivos_json")
            out.setdefault("meta", {})["catalogo_listas_fallback_de_db"] = True
            return out
    out = montar_catalogo_de_arquivos()
    _anexar_meta_diagnostico_listas(out, "arquivos_json")
    return out
