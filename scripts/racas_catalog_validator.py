"""
Validador do catálogo canônico de raças.

Validações conservadoras:
- presença mínima de raças esperadas (PHB básico);
- slug e nome não vazios por raça;
- modificadores com estrutura `{atributo, valor}` quando existirem;
- deslocamento e tamanho coerentes.

Gera lista de `ValidationIssue` (com level `error` ou `warning`) sem abortar,
deixando a decisão para o chamador.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, Iterable


RACAS_OBRIGATORIAS = {
    "humanos",
    "anoes",
    "elfos",
    "gnomos",
    "meio-elfos",
    "meio-orcs",
    "halfling",
}

TAMANHOS_CONHECIDOS = {"Minúsculo", "Miúdo", "Pequeno", "Médio", "Grande", "Enorme"}

ATRIBUTOS_VALIDOS = {
    "forca",
    "destreza",
    "constituicao",
    "inteligencia",
    "sabedoria",
    "carisma",
}


@dataclass(frozen=True)
class ValidationIssue:
    level: str  # "error" | "warning"
    message: str


def _load_catalog(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(path: Path) -> list[ValidationIssue]:
    payload = _load_catalog(path)
    racas = payload.get("racas", [])
    if not isinstance(racas, list):
        return [ValidationIssue("error", "Campo 'racas' não é uma lista.")]

    return list(validate_records(racas))


def validate_records(racas: Iterable[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    slugs: set[str] = set()

    for raca in racas:
        nome = str(raca.get("nome") or "").strip()
        slug = str(raca.get("slug") or "").strip()

        if not nome:
            issues.append(ValidationIssue("error", "Raça sem nome definido."))
        if not slug:
            issues.append(
                ValidationIssue("error", f"Raça {nome!r} sem slug.")
            )
        elif slug in slugs:
            issues.append(
                ValidationIssue(
                    "error", f"Slug duplicado no catálogo: {slug!r}"
                )
            )
        else:
            slugs.add(slug)

        tamanho = str(raca.get("tamanho") or "").strip()
        if tamanho and tamanho not in TAMANHOS_CONHECIDOS:
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Tamanho incomum em {nome!r}: {tamanho!r}",
                )
            )

        desl = raca.get("deslocamento_metros")
        if desl is not None and (not isinstance(desl, int) or desl <= 0):
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Deslocamento inválido em {nome!r}: {desl!r}",
                )
            )

        modificadores = raca.get("modificadores_habilidade") or []
        if not isinstance(modificadores, list):
            issues.append(
                ValidationIssue(
                    "error",
                    f"modificadores_habilidade de {nome!r} não é lista.",
                )
            )
        else:
            for idx, mod in enumerate(modificadores):
                if not isinstance(mod, dict):
                    issues.append(
                        ValidationIssue(
                            "error",
                            f"Modificador #{idx} de {nome!r} não é objeto.",
                        )
                    )
                    continue
                if mod.get("atributo") not in ATRIBUTOS_VALIDOS:
                    issues.append(
                        ValidationIssue(
                            "error",
                            f"Atributo inválido em {nome!r}: {mod.get('atributo')!r}",
                        )
                    )
                if not isinstance(mod.get("valor"), int):
                    issues.append(
                        ValidationIssue(
                            "error",
                            f"Valor inválido em {nome!r}: {mod.get('valor')!r}",
                        )
                    )

    faltantes = RACAS_OBRIGATORIAS - slugs
    if faltantes:
        issues.append(
            ValidationIssue(
                "warning",
                f"Raças esperadas ausentes no catálogo: {sorted(faltantes)}",
            )
        )

    return issues


__all__ = [
    "ATRIBUTOS_VALIDOS",
    "RACAS_OBRIGATORIAS",
    "TAMANHOS_CONHECIDOS",
    "ValidationIssue",
    "validate_catalog",
    "validate_records",
]
