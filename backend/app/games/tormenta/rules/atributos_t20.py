"""Regras de atributos Tormenta 20 — modificadores por faixa e custo em compra por pontos."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_COMPRA_JSON = _DATA_DIR / "atributos_compra_pontos.json"
_PERICIAS_JSON = _DATA_DIR / "pericias_atributo_chave.json"

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


@lru_cache(maxsize=1)
def _carregar_compra_pontos() -> Dict[str, Any]:
    raw = _COMPRA_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def custo_valor_atributo_compra(valor: int) -> Optional[int]:
    """Custo em pontos para um valor na compra por pontos (típico 8–18). None se fora da tabela."""
    data = _carregar_compra_pontos()
    for row in data.get("custos", []):
        if int(row["valor"]) == int(valor):
            return int(row["custo"])
    return None


def pontos_iniciais_compra() -> int:
    data = _carregar_compra_pontos()
    return int(data.get("_meta", {}).get("pontos_iniciais", 20))


def custo_total_compra_seis_atributos(
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
) -> Optional[int]:
    """Soma dos custos se todos os seis valores estiverem na tabela; senão None."""
    vals = (forca, destreza, constituicao, inteligencia, sabedoria, carisma)
    total = 0
    for v in vals:
        c = custo_valor_atributo_compra(v)
        if c is None:
            return None
        total += c
    return total


def lista_custos_compra() -> List[Dict[str, int]]:
    """Cópia somente leitura das linhas {valor, custo} para API futura."""
    data = _carregar_compra_pontos()
    return [dict(x) for x in data.get("custos", [])]


def _rolar_um_valor_4d6(rng: random.Random) -> int:
    """4d6 descartando o menor dado (MB)."""
    dados = sorted(rng.randint(1, 6) for _ in range(4))
    return int(sum(dados[1:]))


def soma_modificadores_valores(valores: Sequence[int]) -> int:
    return sum(modificador_atributo_t20(int(v)) for v in valores)


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


def gerar_seis_valores_4d6(
    *,
    seed: Optional[int] = None,
    exigir_qualidade_mb: bool = True,
    max_tentativas: int = 100,
) -> List[int]:
    """Rola seis atributos 4d6; repete até cumprir a regra de reroll do MB (se exigida)."""
    rng = random.Random(seed)
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


def validar_valores_base_4d6(valores: Sequence[int]) -> None:
    vals = [int(v) for v in valores]
    if len(vals) != 6:
        raise ValueError("Devem ser exatamente seis valores-base (4d6).")
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


@lru_cache(maxsize=1)
def _carregar_pericias_atributo() -> Dict[str, Any]:
    raw = _PERICIAS_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def lista_pericias_com_atributo() -> List[Dict[str, Any]]:
    """Lista ordenada para a ficha: nome, atributo, somente_treinado, penalidade_armadura."""
    data = _carregar_pericias_atributo()
    out: List[Dict[str, Any]] = []
    for row in data.get("pericias", []):
        nome = str(row.get("nome", ""))
        attr = row.get("atributo")
        if attr is not None:
            attr = str(attr).lower().strip()
            if attr not in _ATTR_VALIDOS:
                raise ValueError(f"atributo invalido em pericia '{nome}': {attr!r}")
        st_raw = row.get("somente_treinado", False)
        somente_treinado = bool(st_raw) if isinstance(st_raw, bool) else False
        pen_raw = row.get("penalidade_armadura", False)
        penalidade_armadura = bool(pen_raw) if isinstance(pen_raw, bool) else False
        out.append(
            {
                "nome": nome,
                "atributo": attr,
                "somente_treinado": somente_treinado,
                "penalidade_armadura": penalidade_armadura,
            }
        )
    return out
