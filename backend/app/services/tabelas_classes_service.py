"""
Service para leitura do catálogo de tabelas de classes (somente leitura).
"""

from __future__ import annotations

from typing import Any

from app.core.classes_tables_catalog import load_classes_tables_catalog


class TabelasClassesService:
    def listar_tabelas(
        self,
        skip: int = 0,
        limit: int = 100,
        table_number: int | None = None,
    ) -> dict[str, Any]:
        payload = load_classes_tables_catalog()
        tables = payload.get("tables", [])
        if not isinstance(tables, list):
            return {"total": 0, "skip": skip, "limit": limit, "items": []}

        if table_number is not None:
            tables = [t for t in tables if t.get("table_number") == table_number]

        tables = sorted(tables, key=lambda t: t.get("table_number", 0))
        total = len(tables)
        items = tables[skip : skip + limit]
        return {"total": total, "skip": skip, "limit": limit, "items": items}

    def obter_tabela(self, table_number: int) -> dict[str, Any] | None:
        payload = load_classes_tables_catalog()
        tables = payload.get("tables", [])
        if not isinstance(tables, list):
            return None
        for table in tables:
            if table.get("table_number") == table_number:
                return table
        return None
