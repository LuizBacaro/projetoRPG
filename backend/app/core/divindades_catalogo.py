"""
Catalogo das divindades D&D 3.5 — Tabela 3-7 (Livro do Jogador).

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

from typing import Iterable, List, Optional, TypedDict
import unicodedata


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
    """Retorna copia do catalogo (evita mutacao acidental)."""
    return [dict(item) for item in DIVINDADES]  # type: ignore[misc]


def listar_nomes() -> List[str]:
    """Retorna apenas os nomes canonicos (uso historico em /magias/divindades)."""
    return [item["nome"] for item in DIVINDADES]


def listar_labels() -> List[str]:
    """Retorna labels 'Nome, Titulo' para exibicao em UI."""
    return [item["label"] for item in DIVINDADES]


def buscar_por_nome(nome: str) -> Optional[DivindadeCatalogo]:
    """Localiza uma divindade por nome ou label (tolerante a acento/caixa)."""
    if not nome:
        return None
    chave = _key(nome)
    for item in DIVINDADES:
        if _key(item["nome"]) == chave or _key(item["label"]) == chave:
            return dict(item)  # type: ignore[return-value]
    return None


def dominios_permitidos(nome: str) -> Optional[List[str]]:
    """Retorna lista de dominios canonicos permitidos para a divindade, ou None se nao catalogada."""
    item = buscar_por_nome(nome)
    if not item:
        return None
    return list(item["dominios"])


def validar_dominios_para_divindade(nome: str, dominios: Iterable[str]) -> List[str]:
    """
    Valida se os dominios informados pertencem a lista da divindade.

    Retorna a lista de dominios invalidos (nomes exatos informados).
    Se a divindade nao estiver no catalogo, retorna [] (sem validacao).
    """
    permitidos = dominios_permitidos(nome)
    if permitidos is None:
        return []

    chaves_permitidas = {_key(d) for d in permitidos}
    invalidos: List[str] = []
    for item in dominios:
        chave = _key(item)
        if chave and chave not in chaves_permitidas:
            invalidos.append(str(item).strip())
    return invalidos
