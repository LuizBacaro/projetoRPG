"""Elegibilidade ao grimório / vínculos de magias MB (conjuradores T20, nível mínimo, exceção de mesa).

Regra: classes com entrada em `conjuracao_classe_mb.json` (mago, feiticeiro, bardo, clérigo, druida;
paladino e ranger a partir do nível em que o MB libera conjuração). Demais classes só com
`tormenta_conjuracao_manual_mb: true` em `ficha_json` (multiclasse, talentos, inventor, homebrew).
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from app.games.tormenta.rules.conjuracao_t20 import _mapa_conjuracao_por_slug


def nivel_efetivo_conjuracao_mb(
    ficha_json: Optional[Dict[str, Any]], nivel_personagem: int
) -> int:
    """Nível usado para liberar conjuração MB e checar `conjuracao_inicia_nivel` (multiclasse / override)."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    raw = fj.get("tormenta_nivel_conjurador_mb")
    if raw is not None and str(raw).strip() != "":
        try:
            return max(1, min(40, int(raw)))
        except (TypeError, ValueError):
            pass
    arr = fj.get("tormenta_niveis_classe_mb")
    if isinstance(arr, list) and arr:
        mapa = _mapa_conjuracao_por_slug()
        total = 0
        for it in arr:
            if not isinstance(it, dict):
                continue
            sl = str(it.get("slug") or "").strip().lower()
            if sl not in mapa:
                continue
            try:
                ni = int(it.get("nivel") or 0)
            except (TypeError, ValueError):
                ni = 0
            if ni > 0:
                total += ni
        if total > 0:
            return max(1, min(40, total))
    try:
        nv = int(nivel_personagem)
    except (TypeError, ValueError):
        nv = 1
    return max(1, min(40, nv))


def resumo_elegibilidade_grimorio_mb(
    *,
    tipo: str,
    nivel: int,
    ficha_json: Optional[Dict[str, Any]],
) -> Tuple[bool, str]:
    """
    Retorna (permitido, motivo). `motivo` vazio se permitido; caso contrário texto para UI/log (422).
    `tipo` é ignorado na lógica atual (reservado para futuras exceções por NPC/monstro).
    """
    _ = tipo
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    if fj.get("tormenta_conjuracao_manual_mb") is True:
        return True, ""

    try:
        nv_base = int(nivel)
    except (TypeError, ValueError):
        nv_base = 1
    nv = nivel_efetivo_conjuracao_mb(fj, nv_base)

    slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    if not slug:
        return (
            False,
            "Selecione a classe MB na ficha ou ative tormenta_conjuracao_manual_mb em ficha_json "
            "(multiclasse, talentos de conjuração, inventor etc., conforme a mesa).",
        )

    row = _mapa_conjuracao_por_slug().get(slug)
    if not row:
        return (
            False,
            f"A classe «{slug}» não possui lista de magias de conjurador no MB deste projeto "
            "(mago, feiticeiro, bardo, clérigo, druida; paladino e ranger com magias a partir do 5º nível). "
            "Para outras origens, use tormenta_conjuracao_manual_mb na ficha.",
        )

    ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
    if nv < ini:
        rotulo = slug.replace("_", " ").title()
        return (
            False,
            f"Para {rotulo} (MB), a conjuração com lista de magias começa no {ini}º nível "
            f"(nível considerado para conjuração MB: {nv}). Ajuste o nível do personagem, "
            f"tormenta_nivel_conjurador_mb / tormenta_niveis_classe_mb em ficha_json ou use tormenta_conjuracao_manual_mb.",
        )
    return True, ""
