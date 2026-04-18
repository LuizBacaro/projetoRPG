"""
Catálogo de talentos (LdJ) — fonte única para seed e importação CLI.

O arquivo `talentos_importacao_limpo.json` na raiz do repositório é a fonte canónica.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import and_

from ..models.talento import Talento, TalentoJogador
from .config import settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Nomes do seed legado em init_db (antigo) → nome exato no JSON.
MAPEAMENTO_SEED_PARA_JSON: dict[str, str | None] = {
    "Golpe Poderoso": "Ataque Poderoso¹",
    "Ataque Especial": None,
    "Arma Focada": "Foco em Arma¹²",
    "Especialização de Arma": "Especialização em Arma¹²",
    "Lidar com Corda": "Mãos Leves",
    "Vitalidade Aumentada": "Vitalidade³",
    "Reflexos Rápidos": "Reflexos Rápidos",
    "Golpe Girante": "Ataque Giratório¹",
    "Salto Acrobático": "Acrobático",
    "Esquiva Extraordinária": "Mobilidade¹",
    "Defesa Aprimorada": "Esquiva¹",
    "Conjuração Rápida": "Acelerar Magia",
    "Magia Silenciosa": "Magia Silenciosa",
    "Magia Imóvel": "Magia Sem Gestos",
    "Golpe Certeiro": "Acuidade com Arma¹²",
}


def default_json_path() -> Path:
    """
    Preferência: raiz do repositório; fallback: pasta `backend/` (deploys que não incluem a raiz).
    """
    root = settings.BASE_DIR.parent / "talentos_importacao_limpo.json"
    beside_backend = settings.BASE_DIR / "talentos_importacao_limpo.json"
    if root.is_file():
        return root
    if beside_backend.is_file():
        return beside_backend
    return root


def _trunc(s: str | None, max_len: int) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def load_rows_from_json(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def upsert_talentos_from_rows(db: "Session", rows: list[dict]) -> tuple[int, int]:
    """Insere ou atualiza talentos por `nome` (catálogo completo)."""
    criados = 0
    atualizados = 0
    for row in rows:
        nome = _trunc(row.get("nome"), 100)
        if not nome:
            continue

        descricao = _trunc(row.get("beneficios") or row.get("descricao"), 1000)
        prerequisitos = _trunc(row.get("prerequisitos"), 500)
        secao = _trunc(row.get("secao"), 200)
        pagina = _trunc(row.get("pagina_referencia"), 50)

        q = db.query(Talento).filter(Talento.nome == nome, Talento.deleted_at.is_(None))
        existing = q.first()

        if existing:
            existing.descricao = descricao
            existing.prerequisitos = prerequisitos or existing.prerequisitos
            existing.secao = secao or existing.secao
            existing.pagina_referencia = pagina or existing.pagina_referencia
            existing.ativo = True
            atualizados += 1
        else:
            db.add(
                Talento(
                    nome=nome,
                    descricao=descricao,
                    prerequisitos=prerequisitos,
                    secao=secao,
                    pagina_referencia=pagina or None,
                    ativo=True,
                    criado_em=datetime.now(timezone.utc),
                )
            )
            criados += 1
    return criados, atualizados


def aplicar_mapeamento_seed_antigo(db: "Session", rows: list[dict]) -> tuple[int, list[str]]:
    """Alinha nomes do seed antigo ao texto do JSON (mesma lógica do script CLI)."""
    idx: dict[str, dict] = {}
    for row in rows:
        n = row.get("nome")
        if isinstance(n, str) and n.strip():
            idx[n.strip()] = row

    atualizados = 0
    avisos: list[str] = []

    for seed_nome, json_nome in MAPEAMENTO_SEED_PARA_JSON.items():
        if not json_nome:
            continue
        if json_nome not in idx:
            avisos.append(f"Nome JSON não encontrado no arquivo: {json_nome!r} (seed {seed_nome!r})")
            continue

        talento = (
            db.query(Talento)
            .filter(Talento.nome == seed_nome, Talento.deleted_at.is_(None))
            .first()
        )
        if not talento:
            avisos.append(f"Seed não encontrado no banco: {seed_nome!r}")
            continue

        src = idx[json_nome]
        talento.descricao = _trunc(src.get("beneficios") or src.get("descricao"), 1000)
        talento.prerequisitos = _trunc(src.get("prerequisitos"), 500)
        talento.secao = _trunc(src.get("secao"), 200)
        talento.pagina_referencia = _trunc(src.get("pagina_referencia"), 50) or talento.pagina_referencia
        talento.ativo = True
        atualizados += 1

    return atualizados, avisos


def nomes_catalogo(rows: list[dict]) -> set[str]:
    out: set[str] = set()
    for row in rows:
        n = row.get("nome")
        if isinstance(n, str) and n.strip():
            out.add(n.strip())
    return out


def desativar_talentos_fora_do_catalogo(db: "Session", nomes_validos: set[str]) -> tuple[int, list[str]]:
    """
    Soft-delete de talentos ativos cujo nome não está no catálogo JSON,
    apenas se nenhum combatente os usa (talentos_jogador).
    """
    removidos = 0
    avisos: list[str] = []
    now = datetime.now(timezone.utc)
    candidatos = (
        db.query(Talento)
        .filter(
            and_(
                Talento.deleted_at.is_(None),
                Talento.ativo.is_(True),
            )
        )
        .all()
    )
    for t in candidatos:
        if t.nome in nomes_validos:
            continue
        em_uso = db.query(TalentoJogador).filter(TalentoJogador.talento_id == t.id).first()
        if em_uso:
            avisos.append(
                f"Mantido (em uso por combatente): {t.nome!r} — ajuste manual ou migração se quiser remover."
            )
            continue
        t.deleted_at = now
        t.ativo = False
        removidos += 1
    return removidos, avisos


def sincronizar_catalogo_talentos_desde_json(
    db: "Session",
    json_path: Path | None = None,
    *,
    remover_legado: bool = True,
) -> bool:
    """
    Upsert completo a partir de `talentos_importacao_limpo.json` (gerado pela planilha LdJ).

    Em cada startup do servidor alinha Neon/Render ao repositório, como o seed de equipamentos.
    Opcionalmente remove (soft-delete) linhas ativas que não estão no JSON e não têm uso em fichas.
    """
    path = json_path or default_json_path()
    if not path.is_file():
        logger.warning("Catálogo JSON não encontrado em %s — talentos não sincronizados.", path)
        return False

    rows = load_rows_from_json(path)
    criados, atualizados = upsert_talentos_from_rows(db, rows)
    enriquecidos, avisos_map = aplicar_mapeamento_seed_antigo(db, rows)

    removidos = 0
    avisos_legado: list[str] = []
    if remover_legado:
        removidos, avisos_legado = desativar_talentos_fora_do_catalogo(db, nomes_catalogo(rows))

    db.commit()
    logger.info(
        "Catálogo talentos: +%s novos, %s atualizados; mapeamento seed: %s; legado removido: %s",
        criados,
        atualizados,
        enriquecidos,
        removidos,
    )
    for a in avisos_map:
        logger.debug("talentos mapeamento: %s", a)
    for a in avisos_legado:
        logger.info("talentos legado: %s", a)
    print(
        f"✅ Catálogo talentos (LdJ): {criados} novos, {atualizados} atualizados"
        + (f", {removidos} legados ocultados" if removidos else "")
    )
    return True


def seed_catalogo_inicial_vazio(db: "Session", json_path: Path | None = None) -> bool:
    """Compat: delega para sincronização completa (nome legado)."""
    return sincronizar_catalogo_talentos_desde_json(db, json_path=json_path, remover_legado=True)
