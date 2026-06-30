"""Regras de atributos Tormenta 20 — MB (modificador por faixa) e v1.3 (valor direto)."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_COMPRA_JSON = _DATA_DIR / "atributos_compra_pontos.json"
_COMPRA_V13_JSON = _DATA_DIR / "atributos_compra_pontos_v13.json"
_PERICIAS_JSON = _DATA_DIR / "pericias_atributo_chave.json"
_PERICIAS_V13_JSON = _DATA_DIR / "pericias_atributo_chave_v13.json"

_ATTR_VALIDOS = frozenset({"for", "des", "con", "int", "sab", "car"})
CHAVES_ATRIBUTO: Tuple[str, ...] = ("for", "des", "con", "int", "sab", "car")
METODOS_GERACAO_ATRIBUTOS = frozenset({"compra_pontos", "4d6"})
METODO_GERACAO_PADRAO = "compra_pontos"


def modificador_atributo_t20(valor: int) -> int:
    """Modificador de habilidade T20 (tabela por faixas, não fórmula d20).

    Faixas 1–25 conforme regra base; acima de 25 aplica-se +1 no modificador a cada +2 no valor.
    """
    v = int(valor)
    if v < 1:
        v = 1

    if v <= 1:
        return -5
    if v <= 3:
        return -4
    if v <= 5:
        return -3
    if v <= 7:
        return -2
    if v <= 9:
        return -1
    if v <= 11:
        return 0
    if v <= 13:
        return 1
    if v <= 15:
        return 2
    if v <= 17:
        return 3
    if v <= 19:
        return 4
    if v <= 21:
        return 5
    if v <= 23:
        return 6
    if v <= 25:
        return 7
    # A cada +2 no valor, +1 no modificador acima da faixa 24–25.
    return 7 + (v - 25 + 1) // 2


def contribuicao_atributo_t20(valor: int, regra_versao: Optional[str] = None) -> int:
    """Contribuição mecânica do atributo: v1.3 usa o valor; MB usa modificador por faixa."""
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return int(valor)
    return modificador_atributo_t20(int(valor))


@lru_cache(maxsize=2)
def _carregar_compra_pontos(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _COMPRA_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _COMPRA_JSON
    )
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def custo_valor_atributo_compra(
    valor: int, regra_versao: Optional[str] = None
) -> Optional[int]:
    """Custo em pontos na compra. MB: 8–18; v1.3: −2…+4."""
    data = _carregar_compra_pontos(normalizar_regra_versao(regra_versao))
    for row in data.get("custos", []):
        if int(row["valor"]) == int(valor):
            return int(row["custo"])
    return None


def pontos_iniciais_compra(regra_versao: Optional[str] = None) -> int:
    data = _carregar_compra_pontos(normalizar_regra_versao(regra_versao))
    return int(data.get("_meta", {}).get("pontos_iniciais", 20))


def valor_base_inicial_compra(regra_versao: Optional[str] = None) -> int:
    data = _carregar_compra_pontos(normalizar_regra_versao(regra_versao))
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return int(data.get("_meta", {}).get("base_inicial", 0))
    return 10


def custo_total_compra_seis_atributos(
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
    regra_versao: Optional[str] = None,
) -> Optional[int]:
    """Soma dos custos se todos os seis valores estiverem na tabela; senão None."""
    rv = normalizar_regra_versao(regra_versao)
    vals = (forca, destreza, constituicao, inteligencia, sabedoria, carisma)
    total = 0
    for v in vals:
        c = custo_valor_atributo_compra(v, rv)
        if c is None:
            return None
        total += c
    return total


def lista_custos_compra(regra_versao: Optional[str] = None) -> List[Dict[str, int]]:
    """Cópia somente leitura das linhas {valor, custo} para API."""
    data = _carregar_compra_pontos(normalizar_regra_versao(regra_versao))
    return [dict(x) for x in data.get("custos", [])]


def _rolar_um_valor_4d6(rng: random.Random) -> int:
    """4d6 descartando o menor dado (MB)."""
    dados = sorted(rng.randint(1, 6) for _ in range(4))
    return int(sum(dados[1:]))


def soma_modificadores_valores(
    valores: Sequence[int], regra_versao: Optional[str] = None
) -> int:
    rv = normalizar_regra_versao(regra_versao)
    return sum(contribuicao_atributo_t20(int(v), rv) for v in valores)


def _atributo_de_soma_4d6_v13(soma: int) -> int:
    data = _carregar_compra_pontos(REGRA_VERSAO_V13)
    for row in data.get("rolagem_4d6_para_atributo", []):
        lo = int(row.get("soma_min", 0))
        hi = int(row.get("soma_max", 99))
        if lo <= int(soma) <= hi:
            return int(row["atributo"])
    return 0


def converter_soma_4d6_para_atributo(
    soma: int, regra_versao: Optional[str] = None
) -> int:
    """Converte total 4d6 (3 dados) em valor de atributo conforme a edição."""
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return _atributo_de_soma_4d6_v13(int(soma))
    return int(soma)


def qualidade_geracao_4d6(valores: Sequence[int]) -> bool:
    """MB: soma dos modificadores >= +4 ou pelo menos um valor >= 14."""
    vals = [int(v) for v in valores]
    if len(vals) != 6:
        return False
    if any(v < 3 or v > 18 for v in vals):
        return False
    if any(v >= 14 for v in vals):
        return True
    return soma_modificadores_valores(vals) >= 4


def qualidade_geracao_4d6_v13(valores: Sequence[int]) -> bool:
    """v1.3: soma dos seis atributos convertidos deve ser >= 6."""
    vals = [int(v) for v in valores]
    if len(vals) != 6:
        return False
    data = _carregar_compra_pontos(REGRA_VERSAO_V13)
    minima = int(data.get("soma_minima_seis_atributos_4d6", 6))
    return sum(vals) >= minima


def gerar_seis_valores_4d6(
    *,
    seed: Optional[int] = None,
    exigir_qualidade_mb: bool = True,
    max_tentativas: int = 100,
    regra_versao: Optional[str] = None,
) -> List[int]:
    """Rola seis atributos 4d6; MB repete por qualidade MB; v1.3 converte e rerrola menor se soma < 6."""
    rv = normalizar_regra_versao(regra_versao)
    rng = random.Random(seed)
    if rv == REGRA_VERSAO_V13:
        for _ in range(max(1, int(max_tentativas))):
            brutos = [_rolar_um_valor_4d6(rng) for _ in range(6)]
            convertidos = [converter_soma_4d6_para_atributo(s, rv) for s in brutos]
            if qualidade_geracao_4d6_v13(convertidos):
                return convertidos
            idx = min(range(6), key=lambda i: convertidos[i])
            brutos[idx] = _rolar_um_valor_4d6(rng)
            convertidos[idx] = converter_soma_4d6_para_atributo(brutos[idx], rv)
            if qualidade_geracao_4d6_v13(convertidos):
                return convertidos
        return convertidos
    ultima: List[int] = []
    for _ in range(max(1, int(max_tentativas))):
        ultima = [_rolar_um_valor_4d6(rng) for _ in range(6)]
        if not exigir_qualidade_mb or qualidade_geracao_4d6(ultima):
            return ultima
    return ultima


def valores_4d6_para_mapa(valores: Sequence[int]) -> Dict[str, int]:
    """Associa os seis números rolados à ordem canônica FOR..CAR (distribuição inicial na UI)."""
    vals = [int(v) for v in valores]
    if len(vals) != 6:
        raise ValueError("Devem ser exatamente seis valores (4d6).")
    return {chave: vals[i] for i, chave in enumerate(CHAVES_ATRIBUTO)}


def normalizar_metodo_geracao_atributos(metodo: Optional[str]) -> str:
    m = (metodo or METODO_GERACAO_PADRAO).strip().lower()
    if m not in METODOS_GERACAO_ATRIBUTOS:
        raise ValueError(
            f"Método de geração de atributos inválido: {metodo!r} "
            f"(permitido: {', '.join(sorted(METODOS_GERACAO_ATRIBUTOS))})."
        )
    return m


def validar_valores_base_4d6(
    valores: Sequence[int], regra_versao: Optional[str] = None
) -> None:
    rv = normalizar_regra_versao(regra_versao)
    vals = [int(v) for v in valores]
    if len(vals) != 6:
        raise ValueError("Devem ser exatamente seis valores-base (4d6).")
    if rv == REGRA_VERSAO_V13:
        for v in vals:
            if v < -2 or v > 4:
                raise ValueError(
                    f"Valor-base {v} fora do intervalo −2…+4 permitido pela Tabela 1-1 v1.3."
                )
        if not qualidade_geracao_4d6_v13(vals):
            raise ValueError(
                "Rolagem 4d6 inválida v1.3: a soma dos seis atributos deve ser pelo menos 6."
            )
        return
    for v in vals:
        if v < 3 or v > 18:
            raise ValueError(
                f"Valor-base {v} fora do intervalo 3–18 permitido pela rolagem 4d6 do MB."
            )
    if not qualidade_geracao_4d6(vals):
        raise ValueError(
            "Rolagem 4d6 inválida: a soma dos modificadores deve ser pelo menos +4 "
            "ou pelo menos um valor-base deve ser 14 ou mais (MB)."
        )


@lru_cache(maxsize=2)
def _carregar_pericias_atributo(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _PERICIAS_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _PERICIAS_JSON
    )
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


def lista_pericias_com_atributo(
    regra_versao: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lista ordenada para a ficha: slug, nome, atributo, somente_treinado, penalidade_armadura."""
    rv = normalizar_regra_versao(regra_versao)
    data = _carregar_pericias_atributo(rv)
    out: List[Dict[str, Any]] = []
    for row in data.get("pericias", []):
        nome = str(row.get("nome", "")).strip()
        if not nome or nome == "—":
            continue
        slug = str(row.get("slug", "")).strip().lower()
        attr = row.get("atributo")
        if attr is not None:
            attr = str(attr).lower().strip()
            if attr not in _ATTR_VALIDOS:
                raise ValueError(f"atributo invalido em pericia '{nome}': {attr!r}")
        st_raw = row.get("somente_treinado", False)
        somente_treinado = bool(st_raw) if isinstance(st_raw, bool) else False
        pen_raw = row.get("penalidade_armadura", False)
        penalidade_armadura = bool(pen_raw) if isinstance(pen_raw, bool) else False
        item: Dict[str, Any] = {
            "nome": nome,
            "atributo": attr,
            "somente_treinado": somente_treinado,
            "penalidade_armadura": penalidade_armadura,
        }
        if slug:
            item["slug"] = slug
        if row.get("penalidade_armadura_natacao"):
            item["penalidade_armadura_natacao"] = True
        out.append(item)
    return out
