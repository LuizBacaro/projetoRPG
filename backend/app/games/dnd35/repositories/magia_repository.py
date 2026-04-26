"""Repository para operações de persistência de Magias (D&D 3.5).

Localização: `app.games.dnd35.repositories.magia_repository`. Shim em
`app.repositories.magia_repository` durante a reorganização multi-jogo.
"""

from __future__ import annotations

from typing import Optional, Set, Tuple

from sqlalchemy import asc, desc, false, func
from sqlalchemy.orm import Session, joinedload

from app.core.text_utils import classes_magia
from app.core.text_utils import normalizar_classe as _normalizar_classe
from app.core.text_utils import normalizar_classe_acesso
from app.games.dnd35.models.magia import Magia, MagiaClasse, MagiaHistorico
from app.games.dnd35.models.ataque import MagiaPreparada
from app.repositories.base import BaseRepository, apply_not_deleted, commit_with_rollback


class MagiaRepository(BaseRepository[Magia]):
    def __init__(self, db: Session):
        super().__init__(Magia, db)

    def _magia_ids_por_classe(self, classe_filtro: str) -> Set[int]:
        """
        Resolve magias da classe usando normalização Python (acentos, aliases Feiticeiro→Mago).
        Evita func.upper() no SQL: no SQLite upper('Clérigo') ≠ 'CLERIGO', quebrando o filtro.
        """
        alvo = normalizar_classe_acesso(classe_filtro)
        if not alvo:
            return set()
        ids: Set[int] = set()
        for mid, c in self.db.query(MagiaClasse.magia_id, MagiaClasse.classe).all():
            if c and normalizar_classe_acesso(c) == alvo:
                ids.add(int(mid))
        for mid, legacy in self.db.query(Magia.id, Magia.classe).filter(Magia.classe.isnot(None)).all():
            if legacy and alvo in classes_magia(legacy):
                ids.add(int(mid))
        return ids

    def _magia_ids_por_classe_e_nivel(self, classe_filtro: str, nivel: int) -> Set[int]:
        alvo = normalizar_classe_acesso(classe_filtro)
        if not alvo:
            return set()
        ids: Set[int] = set()
        q = self.db.query(MagiaClasse.magia_id, MagiaClasse.classe, MagiaClasse.nivel)
        for mid, c, nv in q.all():
            if int(nv) == int(nivel) and c and normalizar_classe_acesso(c) == alvo:
                ids.add(int(mid))
        for mid, legacy, nv in self.db.query(Magia.id, Magia.classe, Magia.nivel).filter(Magia.classe.isnot(None)).all():
            if int(nv) == int(nivel) and legacy and alvo in classes_magia(legacy):
                ids.add(int(mid))
        return ids

    def query_base(self):
        query = self.db.query(Magia)
        if hasattr(query, "options"):
            query = query.options(joinedload(Magia.classes_niveis))
        return apply_not_deleted(query, Magia)

    def get_by_nome(self, nome: str) -> Optional[Magia]:
        return self.query_base().filter(func.lower(Magia.nome) == func.lower(nome.strip())).first()

    def listar_paginado(
        self,
        *,
        classe: Optional[str],
        nivel: Optional[int],
        escola: Optional[str],
        nome: Optional[str],
        componentes: Optional[str],
        dominio: Optional[str],
        ativo: Optional[bool],
        sort_by: Optional[str],
        sort_dir: Optional[str],
        skip: int,
        limit: int,
    ) -> Tuple[int, list[Magia]]:
        query = self.query_base()

        if ativo is not None:
            query = query.filter(Magia.ativo == ativo)
        else:
            query = query.filter(Magia.ativo.is_(True))

        if classe:
            if nivel is not None:
                ids_classe = self._magia_ids_por_classe_e_nivel(classe, nivel)
            else:
                ids_classe = self._magia_ids_por_classe(classe)
            if not ids_classe:
                query = query.filter(false())
            else:
                query = query.filter(Magia.id.in_(ids_classe))

        elif nivel is not None:
            query = query.filter((Magia.nivel == nivel) | Magia.classes_niveis.any(MagiaClasse.nivel == nivel))

        if escola:
            query = query.filter(Magia.escola.ilike(escola.strip()))

        if nome:
            query = query.filter(Magia.nome.ilike(f"%{nome.strip()}%"))

        if componentes:
            query = query.filter(Magia.componentes.ilike(f"%{componentes.strip()}%"))

        if dominio:
            query = query.filter(Magia.dominios.ilike(f"%{dominio.strip()}%"))

        total = query.count()
        sort_column = {
            "nome": Magia.nome,
            "escola": Magia.escola,
            "nivel": Magia.nivel,
        }.get((sort_by or "").strip().lower())

        direction = (sort_dir or "asc").strip().lower()
        if sort_column is not None:
            order_expr = desc(sort_column) if direction == "desc" else asc(sort_column)
            items = query.order_by(order_expr, Magia.id.asc()).offset(skip).limit(limit).all()
        else:
            items = query.order_by(Magia.nivel, Magia.nome, Magia.id.asc()).offset(skip).limit(limit).all()

        return total, items

    def listar_classes(self) -> list[str]:
        classes_legacy = {
            _normalizar_classe(row[0])
            for row in self.db.query(Magia.classe).filter(Magia.classe.isnot(None)).all()
            if row[0] and row[0].strip()
        }
        classes_rel = {
            _normalizar_classe(row[0])
            for row in self.db.query(MagiaClasse.classe).distinct().all()
            if row[0] and row[0].strip()
        }
        return sorted(classes_legacy | classes_rel)

    def replace_classes(self, magia: Magia, classes_niveis: list[dict]) -> None:
        magia.classes_niveis.clear()
        # Garante que os vínculos antigos sejam removidos antes de inserir novos
        # para evitar conflito de unicidade (magia_id, classe) no mesmo flush.
        self.db.flush()
        for item in classes_niveis:
            magia.classes_niveis.append(
                MagiaClasse(classe=_normalizar_classe(str(item["classe"])), nivel=item["nivel"])
            )

    def has_dependencias(self, magia_id: int) -> bool:
        return (
            self.db.query(MagiaPreparada.id)
            .filter(MagiaPreparada.magia_id == magia_id)
            .first()
            is not None
        )

    def save(self, magia: Magia) -> Magia:
        commit_with_rollback(self.db)
        self.db.refresh(magia)
        return magia

    def registrar_historico(
        self,
        *,
        magia_id: int | None,
        usuario_id: int | None,
        acao: str,
        dados_anteriores: dict | None,
        dados_novos: dict | None,
    ) -> MagiaHistorico:
        item = MagiaHistorico(
            magia_id=magia_id,
            usuario_id=usuario_id,
            acao=acao,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
        )
        self.db.add(item)
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def listar_historico(self, magia_id: int, *, limit: int = 50) -> list[MagiaHistorico]:
        return (
            self.db.query(MagiaHistorico)
            .filter(MagiaHistorico.magia_id == magia_id)
            .order_by(MagiaHistorico.criado_em.desc(), MagiaHistorico.id.desc())
            .limit(limit)
            .all()
        )
