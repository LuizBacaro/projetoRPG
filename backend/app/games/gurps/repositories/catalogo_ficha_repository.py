"""Persistência do catálogo opcional da ficha GURPS (listas servidas por GET /catalogo/lite-ficha)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.games.gurps.catalogs.lite_catalog import montar_catalogo_de_arquivos
from app.games.gurps.models.catalogo_ficha import (
    GurpsCatalogoFichaDesvantagem,
    GurpsCatalogoFichaPericia,
    GurpsCatalogoFichaVantagem,
)

# Campos enriquecidos que trafegam dentro da coluna JSON `meta_custo`.
# Mantido em sincronia com `lite_catalog._CAMPOS_ENRIQUECIDOS`.
_CAMPOS_META = (
    "cost_model",
    "custo_por_nivel",
    "custo_base",
    "custo_min",
    "custo_max",
    "opcoes_custo",
    "autocontrole",
    "unidade_nivel",
    "tipo_mfsoc",
    "exotica_sob",
    "paginas",
)


def _extrair_meta_custo(item: dict[str, Any]) -> dict[str, Any] | None:
    meta = {k: item[k] for k in _CAMPOS_META if k in item and item[k] is not None}
    return meta or None


def _linha_para_resposta_api(
    nome: str, custo, custo_texto, meta_custo
) -> dict[str, Any]:
    resp: dict[str, Any] = {
        "nome": nome,
        "custo": custo,
        "custo_texto": custo_texto,
    }
    if isinstance(meta_custo, dict):
        for k, v in meta_custo.items():
            if v is not None:
                resp[k] = v
    return resp


class GurpsCatalogoFichaRepository:
    def __init__(self, db: Session):
        self.db = db

    def catalogo_populado(self) -> bool:
        if self.db.query(GurpsCatalogoFichaVantagem).limit(1).first() is None:
            return False
        if self.db.query(GurpsCatalogoFichaDesvantagem).limit(1).first() is None:
            return False
        if self.db.query(GurpsCatalogoFichaPericia).limit(1).first() is None:
            return False
        return True

    def resposta_api_catalogo(self) -> dict[str, Any]:
        base = montar_catalogo_de_arquivos()
        vant_rows = (
            self.db.query(GurpsCatalogoFichaVantagem)
            .order_by(GurpsCatalogoFichaVantagem.ordem, GurpsCatalogoFichaVantagem.nome)
            .all()
        )
        base["vantagens"] = [
            _linha_para_resposta_api(r.nome, r.custo, r.custo_texto, r.meta_custo)
            for r in vant_rows
        ]
        desv_rows = (
            self.db.query(GurpsCatalogoFichaDesvantagem)
            .order_by(
                GurpsCatalogoFichaDesvantagem.ordem, GurpsCatalogoFichaDesvantagem.nome
            )
            .all()
        )
        base["desvantagens"] = [
            _linha_para_resposta_api(r.nome, r.custo, r.custo_texto, r.meta_custo)
            for r in desv_rows
        ]
        per_rows = (
            self.db.query(GurpsCatalogoFichaPericia)
            .order_by(GurpsCatalogoFichaPericia.ordem, GurpsCatalogoFichaPericia.nome)
            .all()
        )
        base["pericias"] = [
            {
                "nome": r.nome,
                "atributo_base": r.atributo_base,
                "dificuldade": r.dificuldade,
                "nt": bool(r.nt),
            }
            for r in per_rows
        ]
        return base


def repopular_catalogo_ficha_de_arquivos(db: Session) -> tuple[int, int, int]:
    """Apaga o catálogo persistido e reinsere a mesma união Lite + sumário PDF usada pelos JSON.

    A partir do commit `q2r3s4t5u6v7` também persiste `meta_custo` com o contrato
    enriquecido do catálogo (cost_model, opcoes_custo, faixa, autocontrole, etc.).
    """
    payload = montar_catalogo_de_arquivos()
    db.execute(delete(GurpsCatalogoFichaVantagem))
    db.execute(delete(GurpsCatalogoFichaDesvantagem))
    db.execute(delete(GurpsCatalogoFichaPericia))
    nv = nd = np = 0
    for i, v in enumerate(payload.get("vantagens") or []):
        nome = (v.get("nome") or "").strip()
        if not nome:
            continue
        db.add(
            GurpsCatalogoFichaVantagem(
                nome=nome,
                custo=v.get("custo"),
                custo_texto=v.get("custo_texto"),
                ordem=i,
                meta_custo=_extrair_meta_custo(v),
            )
        )
        nv += 1
    for i, d in enumerate(payload.get("desvantagens") or []):
        nome = (d.get("nome") or "").strip()
        if not nome:
            continue
        db.add(
            GurpsCatalogoFichaDesvantagem(
                nome=nome,
                custo=d.get("custo"),
                custo_texto=d.get("custo_texto"),
                ordem=i,
                meta_custo=_extrair_meta_custo(d),
            )
        )
        nd += 1
    for i, p in enumerate(payload.get("pericias") or []):
        nome = (p.get("nome") or "").strip()
        if not nome:
            continue
        db.add(
            GurpsCatalogoFichaPericia(
                nome=nome,
                atributo_base=(p.get("atributo_base") or "dx").lower(),
                dificuldade=p.get("dificuldade") or "M",
                nt=bool(p.get("nt")),
                ordem=i,
            )
        )
        np += 1
    return nv, nd, np
