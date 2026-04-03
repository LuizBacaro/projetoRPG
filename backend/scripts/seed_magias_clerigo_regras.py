"""
seed_magias_clerigo_regras.py

Gera uma base de regras para renderizacao de magias de clerigo por alinhamento,
incluindo magias de classe e de dominio.

Fontes:
- CSV de restricoes por alinhamento (raiz do projeto)
- seed_magias.py (magias base de clerigo)
- seed_dominios.py (magias por dominio)
"""

from __future__ import annotations

import csv
import ast
import json
import os
import shutil
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple


# Mantido para compatibilidade com execucao direta via python backend/scripts/...
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


ROOT = Path(__file__).resolve().parents[2]
CSV_COMPLETO = ROOT / "restricoes_clerigo_completo.csv"
CSV_REGRAS = ROOT / "restries-de-magias-divinas-por-alinhamento-do-clrigo.csv"
SEED_MAGIAS_FILE = ROOT / "backend" / "scripts" / "seed_magias.py"
SEED_DOMINIOS_FILE = ROOT / "backend" / "scripts" / "seed_dominios.py"
OUT_DIR = ROOT / "backend" / "scripts" / "generated"
OUT_JSON = OUT_DIR / "seed_magias_clerigo_regras.json"
OUT_CSV = OUT_DIR / "seed_magias_clerigo_regras.csv"

ALIGNMENT_COLUMNS = [
    ("pode_leal_bom", "Leal e Bom"),
    ("pode_leal_neutro", "Leal e Neutro"),
    ("pode_leal_mau", "Leal e Mau"),
    ("pode_neutro_bom", "Neutro e Bom"),
    ("pode_neutro", "Neutro"),
    ("pode_neutro_mau", "Neutro e Mau"),
    ("pode_caotico_bom", "Caótico e Bom"),
    ("pode_caotico_neutro", "Caótico e Neutro"),
    ("pode_caotico_mau", "Caótico e Mau"),
]


DEITY_CONVERSION_EXCEPTIONS: Dict[str, str] = {
    "WEE JAS": "Infligir (sempre)",
    "ST. CUTHBERT": "Curar (sempre)",
    "OBAD-HAI": "Curar (se neutro/bom)",
}


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _norm(text: str) -> str:
    if text is None:
        return ""
    txt = unicodedata.normalize("NFKD", str(text))
    txt = "".join(ch for ch in txt if not unicodedata.combining(ch))
    txt = txt.upper().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def _parse_bool_portuguese(value: str) -> bool:
    normalized = _norm(value)
    return "SIM" in normalized


def _to_sim_nao(value: str) -> str:
    return "SIM" if _parse_bool_portuguese(value) else "NAO"


def _parse_allowed_alignments_from_row(row: Dict[str, str]) -> List[str]:
    allowed: List[str] = []
    for col, label in ALIGNMENT_COLUMNS:
        if _parse_bool_portuguese(row.get(col, "")):
            allowed.append(label)
    return allowed


def _is_complete_cleric_csv(csv_path: Path) -> bool:
    if not csv_path.exists():
        return False
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
    required = {
        "chave_catalogo",
        "nome_magia",
        "nivel",
        "origem_lista",
        "dominio",
        "eh_magia_dominio",
        "pode_leal_bom",
        "pode_caotico_mau",
        "requer_dominio_escolhido",
    }
    return required.issubset(set(header))


def _build_from_complete_csv(csv_path: Path) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                nivel = int((row.get("nivel") or "").strip())
            except Exception:
                continue

            alinhamentos_permitidos = _parse_allowed_alignments_from_row(row)
            alinhamentos_bloqueados = [
                label for _, label in ALIGNMENT_COLUMNS if label not in alinhamentos_permitidos
            ]

            records.append(
                {
                    "chave_catalogo": (row.get("chave_catalogo") or "").strip(),
                    "nome_magia": (row.get("nome_magia") or "").strip(),
                    "nivel": nivel,
                    "origem_lista": (row.get("origem_lista") or "").strip(),
                    "dominio": (row.get("dominio") or "").strip(),
                    "eh_magia_dominio": _to_sim_nao(row.get("eh_magia_dominio", "")),
                    "familia_tendencia": (row.get("familia_tendencia") or "").strip(),
                    "modo_restricao": (row.get("modo_restricao") or "").strip(),
                    "subvariantes_tendencia": (row.get("subvariantes_tendencia") or "").strip(),
                    "subvariantes_por_alinhamento": (row.get("subvariantes_por_alinhamento") or "").strip(),
                    "pode_leal_bom": _to_sim_nao(row.get("pode_leal_bom", "")),
                    "pode_leal_neutro": _to_sim_nao(row.get("pode_leal_neutro", "")),
                    "pode_leal_mau": _to_sim_nao(row.get("pode_leal_mau", "")),
                    "pode_neutro_bom": _to_sim_nao(row.get("pode_neutro_bom", "")),
                    "pode_neutro": _to_sim_nao(row.get("pode_neutro", "")),
                    "pode_neutro_mau": _to_sim_nao(row.get("pode_neutro_mau", "")),
                    "pode_caotico_bom": _to_sim_nao(row.get("pode_caotico_bom", "")),
                    "pode_caotico_neutro": _to_sim_nao(row.get("pode_caotico_neutro", "")),
                    "pode_caotico_mau": _to_sim_nao(row.get("pode_caotico_mau", "")),
                    "alinhamentos_permitidos": alinhamentos_permitidos,
                    "alinhamentos_bloqueados": alinhamentos_bloqueados,
                    "requer_dominio_escolhido": _to_sim_nao(row.get("requer_dominio_escolhido", "")),
                    "dominios_opostos_bloqueiam": (row.get("dominios_opostos_bloqueiam") or "").strip(),
                    "observacao": (row.get("observacao") or "").strip(),
                }
            )

    records.sort(key=lambda r: (int(r["nivel"]), _norm(r["nome_magia"]), _norm(r["dominio"])))
    return {
        "metadata": {
            "fonte_csv": str(csv_path),
            "total_registros": len(records),
            "alinhamentos_suportados": [label for _, label in ALIGNMENT_COLUMNS],
            "excecoes_conversao_por_divindade": DEITY_CONVERSION_EXCEPTIONS,
        },
        "regras_magias": records,
    }


def _load_assignments(py_file: Path, wanted: List[str]) -> Dict[str, Any]:
    source = py_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(py_file))
    env: Dict[str, Any] = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue

        name = node.targets[0].id
        needs_domain_deps = "ALL_DOMAINS" in wanted and name.startswith("DOMINIO_")
        if name not in wanted and not needs_domain_deps:
            continue

        expr = ast.Expression(node.value)
        code = compile(expr, filename=str(py_file), mode="eval")
        env[name] = eval(code, {}, env)

    return env


def _load_alignment_rules(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    rules: Dict[str, Dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            alignment = _strip_html(row.get("Alinhamento", ""))
            if not alignment:
                continue

            rules[alignment] = {
                "allow_bem": _parse_bool_portuguese(row.get("Magias [BEM] - Pode?", "")),
                "allow_mal": _parse_bool_portuguese(row.get("Magias [MAL] - Pode?", "")),
                "allow_ordem": _parse_bool_portuguese(row.get("Magias [ORDEM] - Pode?", "")),
                "allow_caos": _parse_bool_portuguese(row.get("Magias [CAOS] - Pode?", "")),
                "conversao": row.get("Conversão de Magias", "").strip(),
            }
    return rules


def _base_cleric_spells() -> List[Tuple[str, int, str]]:
    loaded = _load_assignments(SEED_MAGIAS_FILE, ["MAGIAS_CLÉRIGO", "MAGIAS_CLERIGO"])
    data = loaded.get("MAGIAS_CLÉRIGO") or loaded.get("MAGIAS_CLERIGO") or []

    spells: List[Tuple[str, int, str]] = []
    for item in data:
        if not isinstance(item, tuple) or len(item) < 2:
            continue
        name = str(item[0]).strip()
        try:
            level = int(item[1])
        except Exception:
            continue
        if not name or name.upper() == "NOME DA MAGIA":
            continue
        descriptor = ""
        if len(item) >= 4:
            descriptor = str(item[3] or "")
        spells.append((name, level, descriptor))
    return spells


def _domain_spells() -> List[Tuple[str, int, str]]:
    spells: List[Tuple[str, int, str]] = []
    loaded = _load_assignments(SEED_DOMINIOS_FILE, ["ALL_DOMAINS"])
    all_domains = loaded.get("ALL_DOMAINS", [])

    for domain_data in all_domains:
        domain_name, _powers, by_level, _description = domain_data
        for level_bucket in by_level:
            for spell in level_bucket:
                if not spell or len(spell) < 2:
                    continue
                name = str(spell[0]).strip()
                if not name:
                    continue
                try:
                    level = int(spell[1])
                except Exception:
                    continue
                spells.append((name, level, str(domain_name)))
    return spells


def _expand_generic_alignment_spells(name: str, level: int) -> List[Tuple[str, int, str]]:
    n = _norm(name)

    if "DETECTAR CAOS / MAL / BEM / ORDEM" in n or "DETECTAR CAOS/MAL/BEM/ORDEM" in n:
        return [
            ("Detectar Caos", level, "CAOS"),
            ("Detectar Mal", level, "MAL"),
            ("Detectar Bem", level, "BEM"),
            ("Detectar Ordem", level, "ORDEM"),
        ]

    if "PROTECAO CONTRA CAOS / MAL / BEM / ORDEM" in n or "PROTECAO CONTRA O CAOS/MAL/BEM/ORDEM" in n:
        return [
            ("Protecao Contra o Caos", level, "ORDEM"),
            ("Protecao Contra o Mal", level, "BEM"),
            ("Protecao Contra o Bem", level, "MAL"),
            ("Protecao Contra a Ordem", level, "CAOS"),
        ]

    if "CIRCULO MAGICO CONTRA O CAOS/MAL/BEM/ORDEM" in n or "CIRCULO MAGICO CONTRA O CAOS / MAL / BEM / ORDEM" in n:
        return [
            ("Circulo Magico Contra o Caos", level, "ORDEM"),
            ("Circulo Magico Contra o Mal", level, "BEM"),
            ("Circulo Magico Contra o Bem", level, "MAL"),
            ("Circulo Magico Contra a Ordem", level, "CAOS"),
        ]

    if "DISSIPAR O CAOS/MAL/BEM/ORDEM" in n or "DISSIPAR O CAOS / MAL / BEM / ORDEM" in n:
        return [
            ("Dissipar o Caos", level, "ORDEM"),
            ("Dissipar o Mal", level, "BEM"),
            ("Dissipar o Bem", level, "MAL"),
            ("Dissipar a Ordem", level, "CAOS"),
        ]

    return []


def _infer_tendency(name: str, descriptor_text: str = "") -> str:
    n = _norm(name)
    d = _norm(descriptor_text)

    if "TENDENCIA EM ARMA" in n:
        return "FLEX"

    # Prioriza descritores explicitos vindos do seed (ex.: "Evoc [bem]").
    if "[BEM]" in d or " BEM " in f" {d} ":
        return "BEM"
    if "[MAL]" in d or " MAL " in f" {d} ":
        return "MAL"
    if "[CAOS]" in d or " CAOS " in f" {d} ":
        return "CAOS"
    if "[ORDEM]" in d or " ORDEM " in f" {d} ":
        return "ORDEM"

    return "NEUTRA"


def _allowed_alignments(tendency: str, rules: Dict[str, Dict[str, Any]]) -> List[str]:
    alignments = list(rules.keys())
    if tendency == "NEUTRA":
        return alignments

    if tendency == "FLEX":
        allowed = []
        for alignment, conf in rules.items():
            if conf["allow_bem"] or conf["allow_mal"] or conf["allow_ordem"] or conf["allow_caos"]:
                allowed.append(alignment)
        return allowed

    key = f"allow_{tendency.lower()}"
    return [alignment for alignment, conf in rules.items() if conf.get(key, False)]


def _build_seed_legacy() -> Dict[str, Any]:
    rules = _load_alignment_rules(CSV_REGRAS)

    records: List[Dict[str, Any]] = []
    dedupe = set()

    # Magias base de classe (clerigo)
    for name, level, descriptor in _base_cleric_spells():
        expanded = _expand_generic_alignment_spells(name, level)

        if expanded:
            candidates = expanded
        else:
            candidates = [(name, level, _infer_tendency(name, descriptor))]

        for spell_name, spell_level, tendency in candidates:
            key = (spell_name, spell_level, "classe", "", tendency)
            if key in dedupe:
                continue
            dedupe.add(key)
            records.append(
                {
                    "nome_magia": spell_name,
                    "nivel": spell_level,
                    "origem": "classe",
                    "dominio": "",
                    "tag_tendencia": tendency,
                    "alinhamentos_permitidos": _allowed_alignments(tendency, rules),
                }
            )

    # Magias de dominio
    for name, level, domain in _domain_spells():
        tendency = _infer_tendency(name)
        if _norm(domain) == "BEM":
            tendency = "BEM"
        elif _norm(domain) == "MAL":
            tendency = "MAL"
        elif _norm(domain) == "ORDEM":
            tendency = "ORDEM"
        elif _norm(domain) == "CAOS":
            tendency = "CAOS"

        key = (name, level, "dominio", domain, tendency)
        if key in dedupe:
            continue
        dedupe.add(key)

        records.append(
            {
                "nome_magia": name,
                "nivel": level,
                "origem": "dominio",
                "dominio": domain,
                "tag_tendencia": tendency,
                "alinhamentos_permitidos": _allowed_alignments(tendency, rules),
            }
        )

    records.sort(key=lambda r: (r["origem"], str(r["dominio"]), int(r["nivel"]), _norm(r["nome_magia"])))

    return {
        "metadata": {
            "fonte_csv": str(CSV_REGRAS.relative_to(ROOT)),
            "total_registros": len(records),
            "alinhamentos_suportados": list(rules.keys()),
            "conversao_por_alinhamento": {k: v["conversao"] for k, v in rules.items()},
            "excecoes_conversao_por_divindade": DEITY_CONVERSION_EXCEPTIONS,
        },
        "regras_magias": records,
    }


def build_seed() -> Dict[str, Any]:
    if _is_complete_cleric_csv(CSV_COMPLETO):
        return _build_from_complete_csv(CSV_COMPLETO)
    return _build_seed_legacy()


def save_outputs(payload: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        rows = payload["regras_magias"]
        if not rows:
            return

        full_columns = [
            "chave_catalogo",
            "nome_magia",
            "nivel",
            "origem_lista",
            "dominio",
            "eh_magia_dominio",
            "familia_tendencia",
            "modo_restricao",
            "subvariantes_tendencia",
            "subvariantes_por_alinhamento",
            "pode_leal_bom",
            "pode_leal_neutro",
            "pode_leal_mau",
            "pode_neutro_bom",
            "pode_neutro",
            "pode_neutro_mau",
            "pode_caotico_bom",
            "pode_caotico_neutro",
            "pode_caotico_mau",
            "alinhamentos_permitidos",
            "alinhamentos_bloqueados",
            "requer_dominio_escolhido",
            "dominios_opostos_bloqueiam",
            "observacao",
        ]

        legacy_columns = [
            "nome_magia",
            "nivel",
            "origem",
            "dominio",
            "tag_tendencia",
            "alinhamentos_permitidos",
        ]

        using_full = "chave_catalogo" in rows[0]
        columns = full_columns if using_full else legacy_columns
        writer.writerow(columns)

        for row in rows:
            values = []
            for col in columns:
                val = row.get(col, "")
                if isinstance(val, list):
                    val = "|".join(str(x) for x in val)
                values.append(val)
            writer.writerow(values)


def main() -> None:
    if Path("/tmp/restricoes_clerigo_completo.csv").exists():
        shutil.copy2("/tmp/restricoes_clerigo_completo.csv", CSV_COMPLETO)

    payload = build_seed()
    save_outputs(payload)
    print(f"OK: {OUT_JSON}")
    print(f"OK: {OUT_CSV}")
    print(f"TOTAL_REGISTROS: {payload['metadata']['total_registros']}")


if __name__ == "__main__":
    main()
