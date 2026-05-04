"""Catálogo estático (listas Lite) + meta de custos em pontos (Basic Set / Characters) para a ficha."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CATALOGO_PATH = Path(__file__).resolve().parent / "gurps_lite_catalogo.json"


def carregar_catalogo_lite_ficha() -> dict[str, Any]:
    with open(_CATALOGO_PATH, encoding="utf-8") as f:
        return json.load(f)
