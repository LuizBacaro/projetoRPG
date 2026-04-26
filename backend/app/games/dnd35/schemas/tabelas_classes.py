"""
Schemas para catálogo de tabelas de classes (read-only) — D&D 3.5.

Localização: `app.games.dnd35.schemas.tabelas_classes`. Shim em
`app.schemas.tabelas_classes` durante a reorganização multi-jogo.
"""

from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class TabelaClassesResponse(BaseModel):
    table_number: int
    title: str
    source_file: str
    metadata: Dict[str, str]
    header: List[str]
    rows: List[Dict[str, str]]


class TabelasClassesListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[TabelaClassesResponse]
