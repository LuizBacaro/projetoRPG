"""Detecção e migração de atributos v1.3 persistidos como score 10–18 (RF-T01-ui-n).

Contexto: a UI antiga exibia `10 + 2×nativo` (ex.: 14) e, em alguns fluxos, gravou
esse score em `for_valor`…`car_valor` em fichas `regra_versao=v13`.

Heurística conservadora:
- Só fichas v1.3 (`regra_versao` em `ficha_json`).
- Converte um atributo se `valor >= 12` (nativo v1.3 típico não passa de ~+7; 12+ é score).
- Converte 6, 8, 10 se **outro** atributo da mesma ficha tiver sinal de score (>= 12).
- Não altera fichas MB (8–18 é escala válida lá).
- Valores 5, 7, 9, 11 etc. permanecem (monstros nativos como For 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional, Tuple

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

ATTR_COLS: Tuple[str, ...] = (
    "for_valor",
    "des_valor",
    "con_valor",
    "int_valor",
    "sab_valor",
    "car_valor",
)
ATTR_KEYS: Tuple[str, ...] = ("for", "des", "con", "int", "sab", "car")

# Scores de exibição 10+2×nativo para nativo −2…+4 (Tabela 1-1 / UI legada).
SCORE_EXIBICAO_V13: frozenset[int] = frozenset({6, 8, 10, 12, 14, 16, 18})

# Limiar: nativo v1.3 acima disso na mesa é atípico; 12+ quase sempre score gravado.
LIMIAR_SCORE_CERTO = 12


def score_exibicao_para_nativo(valor: int) -> int:
    """Converte score de exibição (10+2×nativo) em atributo nativo v1.3."""
    return int((int(valor) - 10) // 2)


def tem_sinal_score_era(valores: Mapping[str, int]) -> bool:
    """True se algum atributo indica que a ficha foi salva na escala 10–18."""
    return any(int(v) >= LIMIAR_SCORE_CERTO for v in valores.values())


def campo_parece_score_persistido(valor: int, *, sinal_score_era: bool) -> bool:
    v = int(valor)
    if v >= LIMIAR_SCORE_CERTO:
        return True
    if sinal_score_era and v in SCORE_EXIBICAO_V13:
        return True
    return False


def ler_atributos_colunas(row: Mapping[str, Any]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for col, key in zip(ATTR_COLS, ATTR_KEYS):
        raw = row.get(col)
        try:
            out[key] = int(raw)
        except (TypeError, ValueError):
            out[key] = 0
    return out


def aplicar_atributos_colunas(row: Dict[str, Any], valores: Mapping[str, int]) -> None:
    for col, key in zip(ATTR_COLS, ATTR_KEYS):
        row[col] = int(valores[key])


@dataclass
class AlteracaoAtributo:
    campo: str
    antes: int
    depois: int


@dataclass
class PlanoMigracaoAtributosV13:
    personagem_id: int
    nome: str
    tipo: str
    alteracoes_colunas: List[AlteracaoAtributo] = field(default_factory=list)
    alteracoes_compra: List[AlteracaoAtributo] = field(default_factory=list)
    motivo: str = ""

    @property
    def precisa_migrar(self) -> bool:
        return bool(self.alteracoes_colunas or self.alteracoes_compra)


def _planejar_mapa_atributos(
    valores: Mapping[str, int],
    *,
    prefixo: str,
) -> Tuple[Dict[str, int], List[AlteracaoAtributo]]:
    atual = {k: int(valores[k]) for k in ATTR_KEYS}
    sinal = tem_sinal_score_era(atual)
    novo = dict(atual)
    alteracoes: List[AlteracaoAtributo] = []

    for key in ATTR_KEYS:
        antes = atual[key]
        if not campo_parece_score_persistido(antes, sinal_score_era=sinal):
            continue
        depois = score_exibicao_para_nativo(antes)
        if depois == antes:
            continue
        novo[key] = depois
        alteracoes.append(
            AlteracaoAtributo(campo=f"{prefixo}{key}", antes=antes, depois=depois)
        )

    return novo, alteracoes


def planejar_migracao_personagem(
    *,
    personagem_id: int,
    nome: str,
    tipo: str,
    ficha_json: Optional[Mapping[str, Any]],
    atributos_colunas: Mapping[str, int],
) -> Optional[PlanoMigracaoAtributosV13]:
    """Retorna plano de migração ou None se ficha não é v1.3."""
    if regra_versao_de_ficha(ficha_json) != REGRA_VERSAO_V13:
        return None

    valores = ler_atributos_colunas(atributos_colunas)
    novo_cols, alt_cols = _planejar_mapa_atributos(valores, prefixo="")

    alt_compra: List[AlteracaoAtributo] = []
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    compra_raw = fj.get("atributos_compra")
    if isinstance(compra_raw, dict):
        compra_vals: Dict[str, int] = {}
        for key in ATTR_KEYS:
            try:
                compra_vals[key] = int(compra_raw.get(key, 0))
            except (TypeError, ValueError):
                compra_vals[key] = 0
        _, alt_compra = _planejar_mapa_atributos(
            compra_vals, prefixo="atributos_compra."
        )

    if not alt_cols and not alt_compra:
        return None

    motivos: List[str] = []
    if any(a.antes >= LIMIAR_SCORE_CERTO for a in alt_cols + alt_compra):
        motivos.append("valor>=12")
    if alt_cols and tem_sinal_score_era(valores):
        motivos.append("score_era_misto")

    return PlanoMigracaoAtributosV13(
        personagem_id=int(personagem_id),
        nome=str(nome or ""),
        tipo=str(tipo or ""),
        alteracoes_colunas=alt_cols,
        alteracoes_compra=alt_compra,
        motivo=",".join(motivos) or "heuristica",
    )


def aplicar_plano_migracao(
    row: Dict[str, Any],
    plano: PlanoMigracaoAtributosV13,
    *,
    registrar_auditoria: bool = True,
) -> Dict[str, Any]:
    """Aplica plano em dict mutável (colunas SQL + ficha_json). Retorna snapshot antes/depois."""
    antes = {col: int(row.get(col, 0)) for col in ATTR_COLS}
    valores = ler_atributos_colunas(row)
    for alt in plano.alteracoes_colunas:
        key = alt.campo
        valores[key] = alt.depois
    aplicar_atributos_colunas(row, valores)

    fj = row.get("ficha_json")
    if not isinstance(fj, dict):
        fj = {}
        row["ficha_json"] = fj
    fj_mut = dict(fj)

    compra = fj_mut.get("atributos_compra")
    if isinstance(compra, dict):
        compra_mut = dict(compra)
        for alt in plano.alteracoes_compra:
            key = alt.campo.replace("atributos_compra.", "", 1)
            compra_mut[key] = alt.depois
        fj_mut["atributos_compra"] = compra_mut

    if registrar_auditoria:
        fj_mut["_migracao_atributos_v13_score"] = {
            "aplicada_em": datetime.now(timezone.utc).isoformat(),
            "motivo": plano.motivo,
            "colunas_antes": antes,
            "colunas_depois": {col: int(row[col]) for col in ATTR_COLS},
            "alteracoes": [
                {"campo": a.campo, "antes": a.antes, "depois": a.depois}
                for a in plano.alteracoes_colunas + plano.alteracoes_compra
            ],
        }
    row["ficha_json"] = fj_mut

    return {
        "antes": antes,
        "depois": {col: int(row[col]) for col in ATTR_COLS},
    }


def resumo_plano(plano: PlanoMigracaoAtributosV13) -> str:
    partes = [f"#{plano.personagem_id} {plano.nome!r} ({plano.tipo}) [{plano.motivo}]"]
    for alt in plano.alteracoes_colunas + plano.alteracoes_compra:
        partes.append(f"  {alt.campo}: {alt.antes} → {alt.depois}")
    return "\n".join(partes)
