"""Importação em lote de magias D&D 5e via Excel (planilha PHB)."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from threading import Lock
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.repositories.base import commit_with_rollback

MAX_IMPORT_ROWS = 2000
IMPORT_TTL_MINUTES = 30

HEADERS_ESPERADOS = [
    "classe_lista",
    "nome",
    "nivel",
    "escola",
    "tempo_conjuracao",
    "alcance",
    "componentes",
    "duracao",
    "concentracao",
    "ritual",
    "descricao",
    "descricao_nivel_superior",
    "classes_slug",
    "pagina_pdf",
    "slug",
]

CLASSE_SLUG_MAP = {
    "mago": "mago",
    "wizard": "mago",
    "feiticeiro": "mago",
    "sorcerer": "mago",
    "clerigo": "clerigo",
    "cleric": "clerigo",
    "druida": "druida",
    "druid": "druida",
    "bardo": "bardo",
    "bard": "bardo",
    "bruxo": "bruxo",
    "warlock": "bruxo",
    "paladino": "paladino",
    "paladin": "paladino",
    "patrulheiro": "patrulheiro",
    "ranger": "patrulheiro",
}


@dataclass
class ImportDraft:
    rows: list[dict[str, Any]]
    expires_at: datetime


def _dedupe_classes_links(links: list[dict[str, Any]]) -> list[dict[str, Any]]:
    por_classe: dict[str, dict[str, Any]] = {}
    for link in links:
        slug = (link.get("classe_slug") or "").strip().lower()
        if slug and slug not in por_classe:
            por_classe[slug] = link
    return list(por_classe.values())


def _slugify(text: str) -> str:
    base = unicodedata.normalize("NFKD", (text or "").strip().lower())
    base = base.encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base[:120] or "magia"


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val or "").strip().lower()
    return s in ("1", "true", "sim", "yes", "s", "x")


def _parse_componentes(raw: str) -> tuple[bool, bool, str | None]:
    s = (raw or "").upper()
    verbal = "V" in s
    somatico = "S" in s
    material = None
    if "M" in s:
        material = (raw or "").split("M", 1)[-1].strip(" (),") or "Material"
    return verbal, somatico, material


def _parse_nivel(raw: Any, nome: str, escola: str) -> int:
    if raw is not None and str(raw).strip() != "":
        try:
            return max(0, min(9, int(float(str(raw).strip()))))
        except ValueError:
            pass
    esc = (escola or "").lower()
    if "truque" in esc or "cantrip" in esc:
        return 0
    nome_l = (nome or "").lower()
    if nome_l.endswith("(truque)") or "truque" in nome_l:
        return 0
    return 1


def _classe_slug(raw: str) -> str:
    key = (raw or "").strip().lower().replace(" ", "_")
    return CLASSE_SLUG_MAP.get(key, key)


class Dnd5eMagiaImportService:
    _drafts: dict[str, ImportDraft] = {}
    _lock = Lock()

    def __init__(self, magia_repo: Dnd5eMagiaRepository):
        self.magia_repo = magia_repo

    def gerar_modelo(self) -> bytes:
        try:
            from openpyxl import Workbook
        except Exception as exc:  # pragma: no cover
            raise HTTPException(
                status_code=500, detail="Dependência openpyxl não instalada"
            ) from exc

        wb = Workbook()
        ws = wb.active
        ws.title = "magias_phb"
        ws.append(HEADERS_ESPERADOS)
        ws.append(
            [
                "Mago",
                "Mísseis Mágicos",
                1,
                "Evocação",
                "1 ação",
                "36 metros",
                "V, S",
                "Instantâneo",
                "não",
                "não",
                "Três dardos de força.",
                "",
                "mago",
                209,
                "misseis-magicos",
            ]
        )
        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()

    async def preview(self, arquivo: UploadFile) -> dict[str, Any]:
        rows, erros = await self._ler_planilha(arquivo)
        import_id = str(uuid4())
        expires = datetime.now(timezone.utc) + timedelta(minutes=IMPORT_TTL_MINUTES)
        with self._lock:
            self._drafts[import_id] = ImportDraft(rows=rows, expires_at=expires)
        return {
            "import_id": import_id,
            "total_linhas": len(rows) + len(erros),
            "validas": len(rows),
            "erros": erros[:50],
            "amostra": rows[:5],
        }

    def confirmar(self, import_id: str) -> dict[str, Any]:
        draft = self._obter_draft(import_id)
        importadas = 0
        atualizadas = 0
        ignoradas = 0

        for row in draft.rows:
            slug = row["slug"]
            existente = self.magia_repo.obter_por_slug(slug)
            if existente:
                magia = existente
                atualizadas += 1
            else:
                magia = Dnd5eMagia(
                    slug=slug,
                    nome=row["nome"],
                    nivel=row["nivel"],
                    escola=row.get("escola"),
                    tempo_conjuracao=row.get("tempo_conjuracao"),
                    alcance_texto=row.get("alcance"),
                    duracao=row.get("duracao"),
                    requer_concentracao=row.get("concentracao", False),
                    ritual=row.get("ritual", False),
                    componentes_verbal=row.get("componentes_verbal", False),
                    componentes_somatico=row.get("componentes_somatico", False),
                    componentes_material=row.get("componentes_material"),
                    descricao=row.get("descricao"),
                    descricao_nivel_superior=row.get("descricao_nivel_superior"),
                    pagina_referencia=row.get("pagina_referencia"),
                    ativo=True,
                )
                self.magia_repo.criar(magia)
                importadas += 1

            links = _dedupe_classes_links(row.get("classes_links", []))
            for link in links:
                classe_slug = link["classe_slug"]
                existente_db = (
                    self.magia_repo.db.query(Dnd5eMagiaClasse)
                    .filter(
                        Dnd5eMagiaClasse.magia_id == magia.id,
                        Dnd5eMagiaClasse.classe_slug == classe_slug,
                    )
                    .first()
                )
                if existente_db:
                    ignoradas += 1
                    continue
                self.magia_repo.db.add(
                    Dnd5eMagiaClasse(
                        magia_id=magia.id,
                        classe_slug=classe_slug,
                        nivel=link["nivel"],
                    )
                )
        commit_with_rollback(self.magia_repo.db)

        with self._lock:
            self._drafts.pop(import_id, None)

        return {
            "importadas": importadas,
            "atualizadas": atualizadas,
            "vinculos_ignorados": ignoradas,
        }

    def _obter_draft(self, import_id: str) -> ImportDraft:
        with self._lock:
            draft = self._drafts.get(import_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Importação expirada ou inválida")
        if draft.expires_at < datetime.now(timezone.utc):
            with self._lock:
                self._drafts.pop(import_id, None)
            raise HTTPException(status_code=410, detail="Importação expirada")
        return draft

    async def _ler_planilha(
        self, arquivo: UploadFile
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        try:
            from openpyxl import load_workbook
        except Exception as exc:  # pragma: no cover
            raise HTTPException(
                status_code=500, detail="Dependência openpyxl não instalada"
            ) from exc

        content = await arquivo.read()
        wb = load_workbook(BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        headers = [str(c.value or "").strip().lower() for c in next(ws.iter_rows(max_row=1))]
        if headers[: len(HEADERS_ESPERADOS)] != HEADERS_ESPERADOS:
            raise HTTPException(
                status_code=422,
                detail=f"Cabeçalhos inválidos. Esperado: {', '.join(HEADERS_ESPERADOS)}",
            )

        rows: list[dict[str, Any]] = []
        erros: list[dict[str, Any]] = []
        por_slug: dict[str, dict[str, Any]] = {}

        for idx, row_cells in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if idx > MAX_IMPORT_ROWS + 1:
                break
            vals = list(row_cells) + [None] * (len(HEADERS_ESPERADOS) - len(row_cells or []))
            nome = str(vals[1] or "").strip()
            if not nome:
                continue

            slug = str(vals[14] or "").strip() or _slugify(nome)
            nivel = _parse_nivel(vals[2], nome, str(vals[3] or ""))
            comp_v, comp_s, comp_m = _parse_componentes(str(vals[6] or ""))
            classe_raw = str(vals[12] or vals[0] or "").strip()
            classe_slug = _classe_slug(classe_raw)

            try:
                pagina = int(float(str(vals[13]))) if vals[13] not in (None, "") else None
            except ValueError:
                pagina = None

            parsed = {
                "linha": idx,
                "slug": slug,
                "nome": nome,
                "nivel": nivel,
                "escola": str(vals[3] or "").strip() or None,
                "tempo_conjuracao": str(vals[4] or "").strip() or None,
                "alcance": str(vals[5] or "").strip() or None,
                "duracao": str(vals[7] or "").strip() or None,
                "concentracao": _parse_bool(vals[8]),
                "ritual": _parse_bool(vals[9]),
                "componentes_verbal": comp_v,
                "componentes_somatico": comp_s,
                "componentes_material": comp_m,
                "descricao": str(vals[10] or "").strip() or None,
                "descricao_nivel_superior": str(vals[11] or "").strip() or None,
                "pagina_referencia": pagina,
                "classes_links": [{"classe_slug": classe_slug, "nivel": nivel}],
            }

            if slug in por_slug:
                por_slug[slug]["classes_links"].append(
                    {"classe_slug": classe_slug, "nivel": nivel}
                )
                por_slug[slug]["classes_links"] = _dedupe_classes_links(
                    por_slug[slug]["classes_links"]
                )
            else:
                parsed["classes_links"] = _dedupe_classes_links(
                    parsed["classes_links"]
                )
                por_slug[slug] = parsed

        rows = list(por_slug.values())
        return rows, erros
