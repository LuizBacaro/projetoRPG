"""Bloco de Ameaça Tormenta 20 — formatação determinística (RF-T13).

Sem LLM: monta texto estilo livro a partir de colunas + ficha_json.ameaca.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

PAPEIS_COMBATE = frozenset({"solo", "lacaio", "especial"})
ATRIBUTOS_KEYS = ("for", "des", "con", "int", "sab", "car")
ATRIBUTOS_LABELS = {
    "for": "For",
    "des": "Des",
    "con": "Con",
    "int": "Int",
    "sab": "Sab",
    "car": "Car",
}
MAGIAS_TOP_N = 8


def modificador_atributo(valor: Any) -> int:
    try:
        v = int(valor)
    except (TypeError, ValueError):
        v = 10
    return (v - 10) // 2


def formatar_bonus(n: Any) -> str:
    try:
        i = int(n)
    except (TypeError, ValueError):
        s = str(n or "").strip()
        return s if s else "+0"
    return f"+{i}" if i >= 0 else str(i)


def _as_dict(blob: Any) -> Dict[str, Any]:
    return dict(blob) if isinstance(blob, Mapping) else {}


def _ameaca_raw(ficha_json: Mapping[str, Any] | None) -> Dict[str, Any]:
    fj = _as_dict(ficha_json)
    nested = fj.get("ameaca")
    return _as_dict(nested)


def obter_nd(
    snapshot: Mapping[str, Any], ficha_json: Mapping[str, Any] | None
) -> float:
    am = _ameaca_raw(ficha_json)
    fj = _as_dict(ficha_json)
    for src in (am.get("nd"), fj.get("nd"), snapshot.get("nivel")):
        if src is None or src == "":
            continue
        try:
            if isinstance(src, str) and "/" in src:
                a, b = src.split("/", 1)
                return max(0.0, float(a) / float(b))
            return max(0.0, float(src))
        except (TypeError, ValueError):
            continue
    return 1.0


def formatar_nd(nd: Any, ficha_json: Mapping[str, Any] | None = None) -> str:
    am = _ameaca_raw(ficha_json)
    rot = str(
        am.get("nd_rotulo") or _as_dict(ficha_json).get("nd_rotulo") or ""
    ).strip()
    if rot:
        return rot
    try:
        n = float(nd)
    except (TypeError, ValueError):
        return str(nd)
    if abs(n - 0.25) < 1e-9:
        return "1/4"
    if abs(n - 0.5) < 1e-9:
        return "1/2"
    if n == int(n):
        return str(int(n))
    return str(n).rstrip("0").rstrip(".")


def obter_papel_combate(
    snapshot: Mapping[str, Any],
    ficha_json: Mapping[str, Any] | None,
    *,
    override: Optional[str] = None,
) -> str:
    if override:
        p = str(override).strip().lower()
        if p in PAPEIS_COMBATE:
            return p
    am = _ameaca_raw(ficha_json)
    raw = str(am.get("papel_combate") or "").strip().lower()
    if raw in PAPEIS_COMBATE:
        return raw
    try:
        pa = int(snapshot.get("pa_max") or 0)
    except (TypeError, ValueError):
        pa = 0
    return "especial" if pa > 0 else "solo"


def obter_tipo_criatura(ficha_json: Mapping[str, Any] | None) -> str:
    am = _ameaca_raw(ficha_json)
    fj = _as_dict(ficha_json)
    for src in (am.get("tipo_criatura"), fj.get("tipo_criatura")):
        s = str(src or "").strip()
        if s:
            return s
    return "Humanoide"


def _lista_ataques_legado(ficha_json: Mapping[str, Any] | None) -> List[Dict[str, str]]:
    fj = _as_dict(ficha_json)
    raw = fj.get("ataques")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, Mapping):
            continue
        nome = str(item.get("nome") or item.get("arma") or f"Ataque {i + 1}").strip()
        ataque = str(
            item.get("ataque")
            if item.get("ataque") is not None
            else item.get("bonus_ataque") or item.get("teste") or "+0"
        ).strip()
        dano = str(item.get("dano") or "—").strip()
        critico = str(item.get("critico") or "").strip()
        out.append(
            {
                "nome": nome or f"Ataque {i + 1}",
                "ataque": ataque or "+0",
                "dano": dano or "—",
                "critico": critico,
            }
        )
    return out


def _acoes_resolvidas(
    ficha_json: Mapping[str, Any] | None
) -> Dict[str, List[Dict[str, Any]]]:
    am = _ameaca_raw(ficha_json)
    acoes = _as_dict(am.get("acoes"))
    corpo = list(acoes.get("corpo_a_corpo") or [])
    dist = list(acoes.get("distancia") or [])
    especiais = list(acoes.get("especiais") or [])
    magias = list(acoes.get("magias") or [])

    if not corpo and not dist:
        legado = _lista_ataques_legado(ficha_json)
        corpo = legado

    def _norm_ataque(itens: Sequence[Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for i, item in enumerate(itens):
            if not isinstance(item, Mapping):
                continue
            out.append(
                {
                    "nome": str(item.get("nome") or f"Ataque {i + 1}").strip(),
                    "ataque": str(
                        item.get("ataque")
                        if item.get("ataque") is not None
                        else item.get("bonus_ataque") or "+0"
                    ).strip(),
                    "dano": str(item.get("dano") or "—").strip(),
                    "critico": str(item.get("critico") or "").strip(),
                }
            )
        return out

    return {
        "corpo_a_corpo": _norm_ataque(corpo),
        "distancia": _norm_ataque(dist),
        "especiais": [dict(x) for x in especiais if isinstance(x, Mapping)],
        "magias": [dict(x) for x in magias if isinstance(x, Mapping)],
    }


def _pericias_fortes(
    ficha_json: Mapping[str, Any] | None,
) -> List[Tuple[str, str]]:
    am = _ameaca_raw(ficha_json)
    fortes = am.get("pericias_fortes")
    out: List[Tuple[str, str]] = []
    if isinstance(fortes, list) and fortes:
        for item in fortes:
            if not isinstance(item, Mapping):
                continue
            nome = str(item.get("nome") or "").strip()
            if not nome:
                continue
            bonus = item.get("bonus")
            if bonus is None:
                bonus = item.get("total")
            out.append((nome, formatar_bonus(bonus)))
        return out

    # Fallback: top perícias do array ficha_json.pericias por total/bonus
    fj = _as_dict(ficha_json)
    raw = fj.get("pericias")
    if not isinstance(raw, list):
        return []
    ranked: List[Tuple[int, str, str]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        nome = str(item.get("nome") or "").strip()
        if not nome:
            continue
        try:
            total = int(
                item.get("total")
                if item.get("total") is not None
                else item.get("bonus") or item.get("graduacao") or 0
            )
        except (TypeError, ValueError):
            total = 0
        ranked.append((total, nome, formatar_bonus(total)))
    ranked.sort(key=lambda t: (-t[0], t[1]))
    return [(n, b) for _, n, b in ranked[:6]]


def _magias_de_vinculos(
    magias: Sequence[Mapping[str, Any]] | None,
    *,
    mod_chave: int = 0,
) -> List[Dict[str, Any]]:
    if not magias:
        return []
    out: List[Dict[str, Any]] = []
    for item in magias:
        if not isinstance(item, Mapping):
            continue
        nome = str(
            item.get("nome") or item.get("magia_nome") or item.get("slug") or ""
        ).strip()
        if not nome:
            continue
        try:
            circulo = int(item.get("circulo") if item.get("circulo") is not None else 1)
        except (TypeError, ValueError):
            circulo = 1
        cd = item.get("cd")
        if cd is None:
            cd = 10 + max(0, circulo) + int(mod_chave)
        custo = item.get("custo_pm")
        if custo is None:
            custo = item.get("custo")
        out.append({"nome": nome, "cd": int(cd), "custo_pm": custo, "circulo": circulo})
        if len(out) >= MAGIAS_TOP_N:
            break
    return out


def _formatar_linha_ataque(item: Mapping[str, Any]) -> str:
    nome = str(item.get("nome") or "Ataque").strip()
    ataque = str(item.get("ataque") or "+0").strip()
    if ataque and not ataque.startswith(("+", "-")):
        try:
            ataque = formatar_bonus(int(ataque))
        except (TypeError, ValueError):
            pass
    dano = str(item.get("dano") or "—").strip()
    critico = str(item.get("critico") or "").strip()
    interno = f"{dano}"
    if critico:
        interno = f"{dano}, Crítico {critico}"
    return f"{nome} {ataque} ({interno})"


def _formatar_especial(item: Mapping[str, Any]) -> str:
    nome = str(item.get("nome") or "Habilidade").strip()
    tipo = str(item.get("tipo_acao") or "").strip()
    texto = str(item.get("texto") or "").strip()
    custo = item.get("custo_pm")
    partes = [nome]
    if tipo:
        partes.append(f"({tipo})")
    if custo is not None and str(custo).strip() != "":
        partes.append(f"— {custo} PM")
    linha = " ".join(partes)
    if texto:
        linha = f"{linha}: {texto}"
    return linha


def _formatar_magia(item: Mapping[str, Any]) -> str:
    nome = str(item.get("nome") or "Magia").strip()
    cd = item.get("cd")
    custo = item.get("custo_pm")
    partes = [nome]
    if cd is not None and str(cd).strip() != "":
        partes.append(f"(CD {cd})")
    if custo is not None and str(custo).strip() != "":
        partes.append(f"— {custo} PM")
    return " ".join(partes)


def _mod_chave_conjuracao(
    snapshot: Mapping[str, Any], ficha_json: Mapping[str, Any]
) -> int:
    """Heurística: maior entre INT/SAB/CAR (sem dependência de classe)."""
    return max(
        modificador_atributo(snapshot.get("int_valor")),
        modificador_atributo(snapshot.get("sab_valor")),
        modificador_atributo(snapshot.get("car_valor")),
    )


def montar_bloco_ameaca(
    snapshot: Mapping[str, Any],
    *,
    ficha_json: Mapping[str, Any] | None = None,
    magias_vinculos: Sequence[Mapping[str, Any]] | None = None,
    preferir_override: bool = True,
) -> Tuple[str, str]:
    """
    Retorna (texto, fonte) onde fonte é ``override`` ou ``gerado``.
    """
    fj = _as_dict(ficha_json if ficha_json is not None else snapshot.get("ficha_json"))
    am = _ameaca_raw(fj)
    if preferir_override:
        override = am.get("texto_override")
        if isinstance(override, str) and override.strip():
            return override.strip(), "override"

    nome = str(snapshot.get("nome") or "Ameaça").strip() or "Ameaça"
    nd = obter_nd(snapshot, fj)
    tipo_criatura = obter_tipo_criatura(fj)
    tamanho = str(snapshot.get("tamanho") or "").strip() or "Médio"
    tipo_tam = f"{tipo_criatura} {tamanho}".strip()

    ini = formatar_bonus(snapshot.get("iniciativa"))
    percepcao = am.get("percepcao")
    if percepcao is None:
        # fallback: perícia Percepção ou SAB
        percepcao = modificador_atributo(snapshot.get("sab_valor"))
        for nome_p, bonus in _pericias_fortes(fj):
            if nome_p.lower() in ("percepção", "percepcao"):
                try:
                    percepcao = int(str(bonus).replace("+", ""))
                except ValueError:
                    percepcao = bonus
                break
    sentidos = str(am.get("sentidos") or "").strip() or "—"

    ca = snapshot.get("ca", 10)
    fort = formatar_bonus(snapshot.get("fort_total"))
    ref = formatar_bonus(snapshot.get("ref_total"))
    von = formatar_bonus(snapshot.get("von_total"))
    rd = str(snapshot.get("rd") or "").strip() or "—"

    pv = snapshot.get("pv_max", 1)
    pm = snapshot.get("pa_max", 0)
    desl = str(snapshot.get("deslocamento") or "").strip() or "—"

    acoes = _acoes_resolvidas(fj)
    magias = list(acoes["magias"])
    if not magias:
        magias = _magias_de_vinculos(
            magias_vinculos,
            mod_chave=_mod_chave_conjuracao(snapshot, fj),
        )
    if not magias:
        magias_texto = str(fj.get("magias_texto") or "").strip()
        if magias_texto:
            magias = [
                {"nome": linha.strip()}
                for linha in magias_texto.splitlines()
                if linha.strip()
            ][:MAGIAS_TOP_N]

    nulos = {
        str(x).strip().lower()
        for x in (am.get("atributos_nulos") or [])
        if str(x).strip()
    }
    attrs_parts: List[str] = []
    for key in ATRIBUTOS_KEYS:
        label = ATRIBUTOS_LABELS[key]
        if key in nulos or f"{key}_valor" in nulos:
            attrs_parts.append(f"{label} —")
            continue
        col = f"{key}_valor"
        mod = modificador_atributo(snapshot.get(col))
        attrs_parts.append(f"{label} {formatar_bonus(mod)}")

    pericias = _pericias_fortes(fj)
    fracas = am.get("pericias_fracas_bonus")
    peri_txt_parts = [f"{n} {b}" for n, b in pericias]
    if fracas is not None and str(fracas).strip() != "":
        peri_txt_parts.append(f"outras {formatar_bonus(fracas)}")
    peri_linha = ", ".join(peri_txt_parts) if peri_txt_parts else "—"

    equip = str(am.get("equipamento_tesouro") or "").strip()
    if not equip:
        equip = str(fj.get("equipamento_texto") or "").strip() or "—"

    nd_txt = formatar_nd(nd, fj)
    linhas: List[str] = [
        f"{nome} ND {nd_txt}",
        tipo_tam,
        f"Iniciativa {ini}, Percepção {formatar_bonus(percepcao) if not isinstance(percepcao, str) else percepcao}, Sentidos {sentidos}",
        f"Defesa {ca}, Fort {fort}, Ref {ref}, Von {von}, RD {rd}",
        f"Pontos de Vida {pv}, Pontos de Mana {pm}",
        f"Deslocamento {desl}",
    ]

    if acoes["corpo_a_corpo"]:
        linhas.append(
            "Ações Corpo a Corpo: "
            + "; ".join(_formatar_linha_ataque(a) for a in acoes["corpo_a_corpo"])
        )
    else:
        linhas.append("Ações Corpo a Corpo: —")

    if acoes["distancia"]:
        linhas.append(
            "Ações À Distância: "
            + "; ".join(_formatar_linha_ataque(a) for a in acoes["distancia"])
        )
    else:
        linhas.append("Ações À Distância: —")

    if acoes["especiais"]:
        linhas.append(
            "Habilidades Especiais: "
            + "; ".join(_formatar_especial(a) for a in acoes["especiais"])
        )
    else:
        talentos = str(fj.get("talentos_texto") or "").strip()
        linhas.append(
            "Habilidades Especiais: "
            + (talentos.replace("\n", "; ") if talentos else "—")
        )

    if magias:
        linhas.append("Magias: " + "; ".join(_formatar_magia(m) for m in magias))
    else:
        linhas.append("Magias: —")

    linhas.append("Atributos: " + ", ".join(attrs_parts))
    linhas.append("Perícias: " + peri_linha)
    linhas.append("Equipamento e Tesouro: " + equip)

    papel = obter_papel_combate(snapshot, fj)
    # Papel não entra no template clássico do livro; anexa como metadado curto no fim
    # apenas se explícito no ameaca (já usado na UI). Mantemos só no consolidar.
    _ = papel

    return "\n".join(linhas), "gerado"


def consolidar_ameaca_de_personagem(
    snapshot: Mapping[str, Any],
    *,
    ficha_json: Mapping[str, Any] | None = None,
    magias_vinculos: Sequence[Mapping[str, Any]] | None = None,
    papel_combate: Optional[str] = None,
) -> Dict[str, Any]:
    """Preenche/normaliza ``ficha_json.ameaca`` a partir do personagem (conversão)."""
    fj: Dict[str, Any] = deepcopy(
        _as_dict(ficha_json if ficha_json is not None else snapshot.get("ficha_json"))
    )
    am_prev = _ameaca_raw(fj)
    acoes = _acoes_resolvidas(fj)

    if not acoes["magias"]:
        acoes["magias"] = _magias_de_vinculos(
            magias_vinculos,
            mod_chave=_mod_chave_conjuracao(snapshot, fj),
        )

    fortes = _pericias_fortes(fj)
    percepcao = am_prev.get("percepcao")
    if percepcao is None:
        percepcao = modificador_atributo(snapshot.get("sab_valor"))
        for n, b in fortes:
            if n.lower() in ("percepção", "percepcao"):
                try:
                    percepcao = int(str(b).replace("+", ""))
                except ValueError:
                    percepcao = b
                break

    papel = obter_papel_combate(snapshot, fj, override=papel_combate)
    nd = obter_nd(snapshot, fj)
    tipo_criatura = obter_tipo_criatura(fj)

    pericias_fortes_out: List[Dict[str, Any]] = []
    for n, b in fortes:
        raw_b = str(b).replace("+", "").strip()
        try:
            bonus_val: Any = int(raw_b)
        except (TypeError, ValueError):
            bonus_val = b
        pericias_fortes_out.append({"nome": n, "bonus": bonus_val})

    ameaca: Dict[str, Any] = {
        "nd": nd,
        "papel_combate": papel,
        "tipo_criatura": tipo_criatura,
        "percepcao": percepcao,
        "sentidos": str(am_prev.get("sentidos") or "").strip(),
        "atributos_nulos": list(am_prev.get("atributos_nulos") or []),
        "pericias_fortes": pericias_fortes_out,
        "pericias_fracas_bonus": am_prev.get("pericias_fracas_bonus", 0),
        "acoes": {
            "corpo_a_corpo": acoes["corpo_a_corpo"],
            "distancia": acoes["distancia"],
            "especiais": acoes["especiais"],
            "magias": acoes["magias"],
        },
        "equipamento_tesouro": str(
            am_prev.get("equipamento_tesouro") or fj.get("equipamento_texto") or ""
        ).strip(),
        "texto_override": None,
    }

    # Preservar sentidos/equip se vazios no novo
    if not ameaca["sentidos"] and am_prev.get("sentidos"):
        ameaca["sentidos"] = am_prev["sentidos"]

    fj["ameaca"] = ameaca
    # Normalizar legado para o nested
    if "nd" in fj and fj.get("nd") is not None:
        fj["nd"] = nd
    if "tipo_criatura" in fj or tipo_criatura:
        fj["tipo_criatura"] = tipo_criatura
    return fj


def limpar_texto_override(ficha_json: MutableMapping[str, Any]) -> Dict[str, Any]:
    fj = dict(ficha_json or {})
    am = _as_dict(fj.get("ameaca"))
    am["texto_override"] = None
    fj["ameaca"] = am
    return fj


def ameaca_minima(
    *, nd: float | int = 1, papel_combate: str = "solo"
) -> Dict[str, Any]:
    papel = papel_combate if papel_combate in PAPEIS_COMBATE else "solo"
    try:
        nd_val: float | int = max(0.0, float(nd))
        if nd_val == int(nd_val):
            nd_val = int(nd_val)
    except (TypeError, ValueError):
        nd_val = 1
    return {
        "nd": nd_val,
        "papel_combate": papel,
        "tipo_criatura": "Humanoide",
        "percepcao": 0,
        "sentidos": "",
        "atributos_nulos": [],
        "pericias_fortes": [],
        "pericias_fracas_bonus": 0,
        "acoes": {
            "corpo_a_corpo": [],
            "distancia": [],
            "especiais": [],
            "magias": [],
        },
        "equipamento_tesouro": "",
        "texto_override": None,
    }
