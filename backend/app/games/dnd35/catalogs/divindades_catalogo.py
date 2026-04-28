"""
Catálogo das divindades D&D 3.5 — Tabela 3-7 (Livro do Jogador).

Canónico: `app.games.dnd35.catalogs.divindades_catalogo`.

Fonte: tabelas_classes_excel/Tabela_3-7_Deuses.xlsx

Correcoes aplicadas em relacao a extracao bruta:
  * "Morandin" -> "Moradin" (grafia canonica do Livro do Jogador 3.5).
  * Hextor: tendencia corrigida para "Leal e Mau" (o extrator misturou linhas).
  * "Pelos" -> "Pelor" (grafia canonica).

Este catalogo alimenta:
  * MagiaService.listar_divindades_sugeridas / listar_divindades_catalogo
  * Endpoint GET /api/v1/magias/divindades e /magias/divindades/catalogo
  * Validacao de dominios de clerigo vs. divindade escolhida
    (CombatenteService._aplicar_regras_dominios_por_classe)
"""

from __future__ import annotations

from typing import Any, Iterable, List, Optional, Sequence, Tuple, TypedDict
import unicodedata


# ---------------------------------------------------------------------------
# Constantes de alinhamento (regra do "um passo" D&D 3.5)
# ---------------------------------------------------------------------------

# Domínios cujo alinhamento intrínseco é incompatível com a tendência oposta
# do personagem/clérigo. (PHB 3.5 — um clérigo não pode escolher domínio
# cujo descritor conflite com o próprio alinhamento.)
DOMINIO_EIXO_ALINHAMENTO = {
    "bem": ("moral", 1),    # exige não-Mau
    "mal": ("moral", -1),   # exige não-Bom
    "ordem": ("ordem", 1),  # exige não-Caótico
    "caos": ("ordem", -1),  # exige não-Leal
}


class DivindadeCatalogo(TypedDict):
    nome: str
    titulo: str
    label: str
    tendencia: str
    dominios: List[str]
    descricao: str


# Tabela 3-7 completa (19 divindades oficiais do Livro do Jogador 3.5).
# dominios: mantem os nomes canonicos do livro. Alguns (Animal, Planta,
# Agua, Ordem) ainda nao existem em DOMINIOS_FIXOS do MagiaService, mas
# sao preservados aqui para fidelidade a fonte e uso pela validacao.
DIVINDADES: List[DivindadeCatalogo] = [
    {
        "nome": "Heironeous",
        "titulo": "Deus do Heroismo",
        "label": "Heironeous, Deus do Heroismo",
        "tendencia": "Leal e Bom",
        "dominios": ["Bem", "Ordem", "Guerra"],
        "descricao": "Patrono dos paladinos e cavaleiros justos; seus clerigos lutam pela honra e pela justica.",
    },
    {
        "nome": "Moradin",
        "titulo": "Deus dos Anoes",
        "label": "Moradin, Deus dos Anoes",
        "tendencia": "Leal e Bom",
        "dominios": ["Terra", "Bem", "Ordem", "Protecao"],
        "descricao": "Pai-forjador da raca anoa; inspira artesaos, defensores e fundadores de reinos.",
    },
    {
        "nome": "Yondalla",
        "titulo": "Deusa dos Halflings",
        "label": "Yondalla, Deusa dos Halflings",
        "tendencia": "Leal e Bom",
        "dominios": ["Bem", "Ordem", "Protecao"],
        "descricao": "Matriarca dos halflings; protege comunidades, familias e viajantes de boa indole.",
    },
    {
        "nome": "Ehlonna",
        "titulo": "Deusa das Florestas",
        "label": "Ehlonna, Deusa das Florestas",
        "tendencia": "Neutro e Bom",
        "dominios": ["Animal", "Bem", "Planta", "Sol"],
        "descricao": "Venerada por elfos, druidas e rangers; guardia das florestas e das criaturas selvagens benignas.",
    },
    {
        "nome": "Garl Glittergold",
        "titulo": "Deus dos Gnomos",
        "label": "Garl Glittergold, Deus dos Gnomos",
        "tendencia": "Neutro e Bom",
        "dominios": ["Bem", "Protecao", "Enganacao"],
        "descricao": "Patrono dos gnomos; mistura astucia, humor e protecao dos pequenos.",
    },
    {
        "nome": "Pelor",
        "titulo": "Deus do Sol",
        "label": "Pelor, Deus do Sol",
        "tendencia": "Neutro e Bom",
        "dominios": ["Bem", "Cura", "Forca", "Sol"],
        "descricao": "Luz, cura e esperanca; patrono preferido de clerigos curandeiros e combatentes contra mortos-vivos.",
    },
    {
        "nome": "Corellon Larethian",
        "titulo": "Deus dos Elfos",
        "label": "Corellon Larethian, Deus dos Elfos",
        "tendencia": "Caotico e Bom",
        "dominios": ["Caos", "Bem", "Protecao", "Guerra"],
        "descricao": "Criador da raca elfica; protetor da magia, da arte e da guerra contra o mal organizado.",
    },
    {
        "nome": "Kord",
        "titulo": "Deus da Forca",
        "label": "Kord, Deus da Forca",
        "tendencia": "Caotico e Bom",
        "dominios": ["Caos", "Bem", "Sorte", "Forca"],
        "descricao": "Campeao dos guerreiros barbaros e atletas; exalta a forca bruta guiada pela coragem.",
    },
    {
        "nome": "Wee Jas",
        "titulo": "Deusa da Morte e da Magia",
        "label": "Wee Jas, Deusa da Morte e da Magia",
        "tendencia": "Leal e Neutro",
        "dominios": ["Morte", "Ordem", "Magia"],
        "descricao": "Regente disciplinada da morte e da magia; seus clerigos fascinam/comandam mortos-vivos e so conjuram magias de infligir ferimentos.",
    },
    {
        "nome": "St. Cuthbert",
        "titulo": "Deus da Retribuicao",
        "label": "St. Cuthbert, Deus da Retribuicao",
        "tendencia": "Leal e Neutro",
        "dominios": ["Destruicao", "Ordem", "Protecao", "Forca"],
        "descricao": "Impoe a lei com punho firme; seus clerigos expulsam/destroem mortos-vivos e convertem magias em cura.",
    },
    {
        "nome": "Boccob",
        "titulo": "Deus da Magia",
        "label": "Boccob, Deus da Magia",
        "tendencia": "Neutro",
        "dominios": ["Conhecimento", "Magia", "Enganacao"],
        "descricao": "Arquimago cosmico; arquetipo do estudioso neutro que venera o proprio ato de conjurar.",
    },
    {
        "nome": "Fharlanghn",
        "titulo": "Deus das Estradas",
        "label": "Fharlanghn, Deus das Estradas",
        "tendencia": "Neutro",
        "dominios": ["Sorte", "Protecao", "Viagem"],
        "descricao": "Guardiao de viajantes, bardos errantes e exploradores; abencoa jornadas e encruzilhadas.",
    },
    {
        "nome": "Obad-Hai",
        "titulo": "Deus da Natureza",
        "label": "Obad-Hai, Deus da Natureza",
        "tendencia": "Neutro",
        "dominios": ["Ar", "Animal", "Terra", "Fogo", "Planta", "Agua"],
        "descricao": "Senhor dos elementos e dos ciclos naturais; seus clerigos expulsam/destroem mortos-vivos e so convertem em cura.",
    },
    {
        "nome": "Olidammara",
        "titulo": "Deus dos Ladroes",
        "label": "Olidammara, Deus dos Ladroes",
        "tendencia": "Caotico e Neutro",
        "dominios": ["Caos", "Sorte", "Enganacao"],
        "descricao": "Trapaceiro alegre; patrono de ladinos, malandros, musicos de rua e aventureiros oportunistas.",
    },
    {
        "nome": "Hextor",
        "titulo": "Deus da Tirania",
        "label": "Hextor, Deus da Tirania",
        "tendencia": "Leal e Mau",
        "dominios": ["Destruicao", "Mal", "Ordem", "Guerra"],
        "descricao": "Arquirrival de Heironeous; patrono de tiranos, conquistadores e exercitos brutais.",
    },
    {
        "nome": "Nerull",
        "titulo": "Deus da Morte",
        "label": "Nerull, Deus da Morte",
        "tendencia": "Neutro e Mau",
        "dominios": ["Morte", "Mal", "Enganacao", "Guerra"],
        "descricao": "Ceifador sinistro; fonte preferida de necromantes e cultos que cortejam a morte.",
    },
    {
        "nome": "Vecna",
        "titulo": "Deus dos Segredos",
        "label": "Vecna, Deus dos Segredos",
        "tendencia": "Neutro e Mau",
        "dominios": ["Mal", "Conhecimento", "Magia"],
        "descricao": "Lich divinizado; venerado por conspiradores, magos sombrios e buscadores de saberes proibidos.",
    },
    {
        "nome": "Erythnul",
        "titulo": "Deus da Matanca",
        "label": "Erythnul, Deus da Matanca",
        "tendencia": "Caotico e Mau",
        "dominios": ["Caos", "Mal", "Enganacao", "Guerra"],
        "descricao": "Senhor do massacre e do panico; patrono de orcs, gnolls e saqueadores.",
    },
    {
        "nome": "Gruumsh",
        "titulo": "Deus dos Orcs",
        "label": "Gruumsh, Deus dos Orcs",
        "tendencia": "Caotico e Mau",
        "dominios": ["Caos", "Mal", "Forca", "Guerra"],
        "descricao": "Divindade caolha dos orcs; impoe conquista, pilhagem e odio aos elfos.",
    },
]


# ---------------------------------------------------------------------------
# Helpers publicos
# ---------------------------------------------------------------------------


def _key(valor: str) -> str:
    """Normaliza nome para comparacao: sem acentos, minusculo, sem espacos extras."""
    if not valor:
        return ""
    decomp = unicodedata.normalize("NFD", str(valor))
    sem_acento = "".join(ch for ch in decomp if unicodedata.category(ch) != "Mn")
    return sem_acento.strip().lower()


def listar_catalogo() -> List[DivindadeCatalogo]:
    """Retorna copia do catalogo OFICIAL (sem customizadas)."""
    return [dict(item) for item in DIVINDADES]  # type: ignore[misc]


def _normalizar_custom(entrada: Any) -> Optional[DivindadeCatalogo]:
    """Converte um registro de DivindadeCustom (ORM, dict ou schema) em
    DivindadeCatalogo. Retorna None se nao tiver nome."""
    if entrada is None:
        return None

    def _get(key: str, default: Any = None) -> Any:
        if isinstance(entrada, dict):
            return entrada.get(key, default)
        return getattr(entrada, key, default)

    nome = str(_get("nome", "") or "").strip()
    if not nome:
        return None
    titulo = str(_get("titulo", "") or "").strip()
    tendencia = str(_get("tendencia", "") or "").strip()
    descricao = _get("descricao", "") or ""
    dominios_raw = _get("dominios", []) or []
    if isinstance(dominios_raw, str):
        dominios = [item.strip() for item in dominios_raw.split(",") if item.strip()]
    else:
        dominios = [str(item).strip() for item in dominios_raw if str(item).strip()]
    label = f"{nome}, {titulo}" if titulo else nome
    return {
        "nome": nome,
        "titulo": titulo,
        "label": label,
        "tendencia": tendencia,
        "dominios": dominios,
        "descricao": str(descricao).strip(),
    }


def listar_catalogo_completo(
    customizadas: Optional[Sequence[Any]] = None,
) -> List[DivindadeCatalogo]:
    """Retorna o catalogo oficial acrescido das divindades customizadas
    (passadas pelo service). Customizadas com nome duplicado em relacao ao
    catalogo oficial sao ignoradas (oficial tem prioridade)."""
    base = listar_catalogo()
    if not customizadas:
        return base
    chaves = {_key(item["nome"]) for item in base}
    for bruto in customizadas:
        normalizado = _normalizar_custom(bruto)
        if not normalizado:
            continue
        chave = _key(normalizado["nome"])
        if chave in chaves:
            continue
        base.append(normalizado)
        chaves.add(chave)
    return base


def listar_nomes() -> List[str]:
    """Retorna apenas os nomes canonicos do catalogo oficial."""
    return [item["nome"] for item in DIVINDADES]


def listar_labels() -> List[str]:
    """Retorna labels 'Nome, Titulo' do catalogo oficial."""
    return [item["label"] for item in DIVINDADES]


def buscar_por_nome(
    nome: str,
    customizadas: Optional[Sequence[Any]] = None,
) -> Optional[DivindadeCatalogo]:
    """Localiza uma divindade por nome ou label no catalogo oficial e, opcionalmente,
    nas customizadas fornecidas. Tolerante a acento/caixa."""
    if not nome:
        return None
    chave = _key(nome)
    for item in DIVINDADES:
        if _key(item["nome"]) == chave or _key(item["label"]) == chave:
            return dict(item)  # type: ignore[return-value]
    if customizadas:
        for bruto in customizadas:
            normalizado = _normalizar_custom(bruto)
            if not normalizado:
                continue
            if _key(normalizado["nome"]) == chave or _key(normalizado["label"]) == chave:
                return normalizado
    return None


def dominios_permitidos(
    nome: str,
    customizadas: Optional[Sequence[Any]] = None,
) -> Optional[List[str]]:
    """Retorna a lista de dominios canonicos permitidos para a divindade,
    considerando catalogo oficial + customizadas passadas. None = nao catalogada."""
    item = buscar_por_nome(nome, customizadas=customizadas)
    if not item:
        return None
    return list(item["dominios"])


def validar_dominios_para_divindade(
    nome: str,
    dominios: Iterable[str],
    customizadas: Optional[Sequence[Any]] = None,
) -> List[str]:
    """
    Valida se os dominios informados pertencem a lista da divindade.

    Retorna a lista de dominios invalidos (nomes exatos informados).
    Se a divindade nao estiver no catalogo (oficial + customizadas), retorna []
    (sem validacao — sera tratada como divindade homebrew fora do sistema).
    """
    permitidos = dominios_permitidos(nome, customizadas=customizadas)
    if permitidos is None:
        return []

    chaves_permitidas = {_key(d) for d in permitidos}
    invalidos: List[str] = []
    for item in dominios:
        chave = _key(item)
        if chave and chave not in chaves_permitidas:
            invalidos.append(str(item).strip())
    return invalidos


# ---------------------------------------------------------------------------
# Helpers de alinhamento (filtros em cascata)
# ---------------------------------------------------------------------------


def parse_alinhamento(valor: str) -> Optional[Tuple[int, int]]:
    """
    Converte uma tendencia ("Leal e Bom", "Caotico e Mau", "Neutro", ...) em
    um par (eixo_ordem, eixo_moral) onde cada eixo vale:

    * eixo_ordem : 1 = Leal, 0 = Neutro, -1 = Caotico
    * eixo_moral : 1 = Bom,  0 = Neutro, -1 = Mau

    Retorna None quando nao consegue interpretar o valor (ex.: string vazia).
    Aceita "Mal" e "Mau" como sinonimos.
    """
    chave = _key(valor)
    if not chave:
        return None

    # "Neutro" puro = (0, 0)
    if chave in {"neutro", "verdadeiro neutro", "neutro neutro"}:
        return (0, 0)

    ordem = 0
    moral = 0

    if "leal" in chave:
        ordem = 1
    elif "caotico" in chave:
        ordem = -1

    if "bom" in chave or "bem" in chave:
        moral = 1
    elif "mau" in chave or "mal" in chave:
        moral = -1

    # Caso textos como "Leal e Neutro" / "Neutro e Bom" / "Caotico e Neutro"
    # o eixo nao-mencionado fica em 0 (Neutro). Se NADA casou, devolve None.
    if ordem == 0 and moral == 0 and "neutro" not in chave:
        return None
    return (ordem, moral)


def alinhamento_compativel(tendencia_divindade: str, alinhamento_personagem: str) -> bool:
    """
    Regra "um passo" (PHB 3.5): um adorador/clerigo pode diferir da divindade
    em, no maximo, um passo em cada um dos eixos (ordem/moral).

    Se qualquer um dos alinhamentos nao for interpretavel, retorna True (nao
    bloqueia o usuario por falta de dado).
    """
    a = parse_alinhamento(tendencia_divindade)
    b = parse_alinhamento(alinhamento_personagem)
    if a is None or b is None:
        return True
    return abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1


def filtrar_por_alinhamento(
    alinhamento_personagem: str,
    customizadas: Optional[Sequence[Any]] = None,
) -> List[DivindadeCatalogo]:
    """
    Retorna as divindades compativeis com o alinhamento informado (regra do
    um passo), considerando catalogo oficial + customizadas opcionais.
    Se o alinhamento nao for interpretavel, retorna o catalogo completo.
    """
    catalogo = listar_catalogo_completo(customizadas)
    parsed = parse_alinhamento(alinhamento_personagem)
    if parsed is None:
        return catalogo
    return [
        item
        for item in catalogo
        if alinhamento_compativel(item["tendencia"], alinhamento_personagem)
    ]


def dominios_proibidos_por_alinhamento(alinhamento_personagem: str) -> List[str]:
    """
    Retorna nomes canonicos (em minusculo, sem acento) dos dominios
    incompativeis com o alinhamento informado.

    Regra PHB 3.5: clerigo nao pode escolher dominio cujo descritor
    alinhamental seja oposto ao dele. Um passo de folga NAO se aplica aqui -
    a incompatibilidade e direta (Bem vs Mal, Ordem vs Caos).
    """
    parsed = parse_alinhamento(alinhamento_personagem)
    if parsed is None:
        return []
    ordem_p, moral_p = parsed
    proibidos: List[str] = []
    for nome_dominio, (eixo, sinal) in DOMINIO_EIXO_ALINHAMENTO.items():
        valor = moral_p if eixo == "moral" else ordem_p
        # O dominio "Bem" (sinal=+1) e proibido se moral_p < 0 (Mau).
        # O dominio "Mal" (sinal=-1) e proibido se moral_p > 0 (Bom).
        # Idem para Ordem/Caos no eixo de ordem.
        if valor != 0 and (valor * sinal) < 0:
            proibidos.append(nome_dominio)
    return proibidos


def validar_dominios_contra_alinhamento(
    alinhamento_personagem: str, dominios: Iterable[str]
) -> List[str]:
    """
    Retorna a lista de dominios informados que sao incompativeis com o
    alinhamento do personagem (ex.: personagem "Leal e Bom" escolhendo
    dominio "Mal" ou "Caos"). Se o alinhamento for desconhecido, retorna [].
    """
    proibidos = set(dominios_proibidos_por_alinhamento(alinhamento_personagem))
    if not proibidos:
        return []
    invalidos: List[str] = []
    for item in dominios:
        if _key(item) in proibidos:
            invalidos.append(str(item).strip())
    return invalidos
