"""
Seeds de arranque específicos do D&D 3.5 (equipamentos, talentos, magias, catálogo de classes).

Importados no startup a partir de `app.main`.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.shared.core.config import settings

logger = logging.getLogger(__name__)


def inicializar_equipamentos(db: Session) -> None:
    """
    Sincroniza o catálogo de equipamentos com a Tabela 7-5 (planilha / seed gerado).

    Dados em `backend/scripts/seed_equipamentos.py` (regenerar com
    `python processar_equipamentos_excel.py` na raiz do projeto).

    Remove itens legados do seed antigo (sem categoria) que não estejam em uso
    e insere/atualiza entradas da planilha por nome.
    """
    from scripts.seed_equipamentos import seed_equipamentos

    seed_equipamentos(db)


def inicializar_consumiveis(db: Session) -> None:
    """
    Sincroniza o catálogo de consumíveis (poções/óleos/pergaminhos) a partir do seed gerado.

    Dados em `backend/scripts/seed_consumiveis.py` (regenerar com
    `python processar_consumiveis_excel.py` na raiz do projeto).
    """
    from scripts.seed_consumiveis import seed_consumiveis

    seed_consumiveis(db)


def inicializar_talentos(db: Session) -> None:
    """
    Sincroniza o catálogo LdJ com `talentos_importacao_limpo.json` (raiz do repo),
    gerado por `processar_talentos_excel.py` a partir de `Tabela_5-1_Talentos_LdJ.xlsx`.

    Em cada startup: upsert por nome + remove legado fora do JSON (soft-delete se não usado em fichas).
    Se o JSON não existir no deploy, usa seed mínimo só quando a tabela está vazia.
    """
    from datetime import datetime, timezone

    from .catalogs.talentos_catalog_seed import (
        default_json_path,
        sincronizar_catalogo_talentos_desde_json,
    )
    from .models.talento import Talento

    json_path = default_json_path()
    if json_path.is_file():
        sincronizar_catalogo_talentos_desde_json(
            db, json_path=json_path, remover_legado=True
        )
        return

    # Fallback: seed mínimo só se o JSON não estiver no deploy e tabela vazia
    count = db.query(Talento).filter(Talento.deleted_at.is_(None)).count()
    if count > 0:
        logger.warning(
            "Sem talentos_importacao_limpo.json e já existem %s talentos — não alterando.",
            count,
        )
        return

    logger.warning(
        "Catálogo JSON ausente em %s — usando seed mínimo de desenvolvimento.",
        json_path,
    )

    TALENTOS_PADRAO = [
        ("Golpe Poderoso", "Realiza um ataque com + 2 de dano", "PHB p.95"),
        ("Ataque Especial", "Permite um ataque extra uma vez por dia", "PHB p.95"),
        ("Arma Focada", "Aumenta bônus com uma arma específica", "PHB p.93"),
        ("Especialização de Arma", "Aumenta dano com uma arma específica", "PHB p.93"),
        ("Lidar com Corda", "Bônus em testes com corda", "PHB p.95"),
        ("Vitalidade Aumentada", "Aumenta pontos de vida", "PHB p.95"),
        ("Reflexos Rápidos", "Aproveita a iniciativa melhor", "PHB p.95"),
        ("Golpe Girante", "Ataque contra múltiplos inimigos", "PHB p.95"),
        ("Salto Acrobático", "Bônus em testes de acrobacia", "PHB p.93"),
        ("Esquiva Extraordinária", "Evasão melhorada contra ataques", "PHB p.95"),
        ("Defesa Aprimorada", "Aumenta CA permanentemente", "PHB p.95"),
        ("Conjuração Rápida", "Reduz tempo de conjuração", "PHB p.95"),
        ("Magia Silenciosa", "Conjura sem componentes verbais", "PHB p.95"),
        ("Magia Imóvel", "Conjura sem componentes somáticos", "PHB p.95"),
        ("Golpe Certeiro", "Bônus para acertar com armas de melee", "PHB p.95"),
    ]

    for nome, descricao, pagina_ref in TALENTOS_PADRAO:
        db.add(
            Talento(
                nome=nome,
                descricao=descricao,
                pagina_referencia=pagina_ref,
                ativo=True,
                criado_em=datetime.now(timezone.utc),
            )
        )
    db.commit()
    print(
        f"✅ {len(TALENTOS_PADRAO)} talentos (seed mínimo) inseridos — prefira o JSON no repositório."
    )


def inicializar_catalogo_tabelas_classes() -> None:
    """
    Inicialização opt-in do catálogo de classes.

    Sem side effects de banco; apenas valida carregamento quando habilitado.
    """
    from .catalogs.classes_tables_catalog import initialize_classes_tables_catalog

    initialize_classes_tables_catalog()


def inicializar_catalogo_magias_se_vazio(db: Session) -> None:
    """
    Garante catálogo PHB em `magias` / `magias_classes` quando o banco está vazio.

    - **SQLite (dev):** se `magias` estiver vazia, executa `scripts/seed_magias.py` no startup
      (primeira subida pode levar ~20–40s).
    - **PostgreSQL / outros:** só popula automaticamente se `SEED_MAGIAS_ON_EMPTY=1` no `.env`;
      caso contrário apenas avisa — use `cd backend && python scripts/seed_magias.py` manualmente.
    """
    from scripts.seed_magias import seed_magias

    from .models.magia import Magia

    try:
        total = db.query(Magia).count()
    except Exception as exc:  # pragma: no cover - schema ainda não pronto
        logger.warning("Não foi possível verificar tabela magias: %s", exc)
        return

    if total > 0:
        return

    url = (settings.DATABASE_URL or "").lower()
    is_sqlite = "sqlite" in url
    if not is_sqlite and not settings.SEED_MAGIAS_ON_EMPTY:
        msg = (
            "Tabela `magias` vazia — grimório e escolas ficam vazios. "
            "Execute no servidor: cd backend && python scripts/seed_magias.py "
            "ou defina SEED_MAGIAS_ON_EMPTY=1 uma vez no .env e reinicie."
        )
        logger.warning(msg)
        print(f"⚠️  {msg}")
        return

    logger.info("Tabela magias vazia — executando seed PHB (aguarde ~20–40s)…")
    print("📚 Populando catálogo de magias (primeira execução pode demorar)…")
    try:
        seed_magias(db, force=False)
        logger.info("✅ Catálogo de magias (seed PHB) concluído.")
        print("✅ Catálogo de magias inicializado.")
    except Exception as exc:
        logger.exception("Falha ao executar seed_magias: %s", exc)
        print(f"❌ Falha ao popular magias: {exc}")
        raise
