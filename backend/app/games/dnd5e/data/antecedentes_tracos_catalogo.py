"""Traços de antecedente PHB — opções por background."""

from __future__ import annotations

from typing import Dict, List

TracosDict = Dict[str, List[str]]

_TRACOS_ACOLITO: TracosDict = {
    "personalidade": [
        "Guio os outros com paciência e conselhos sábios.",
        "Vejo omens em cada evento e ação.",
        "Nada pode abalar minha otimismo.",
        "Cito textos sagrados e provérbios em quase toda conversa.",
    ],
    "ideais": [
        "Tradição. As tradições ancestrais devem ser preservadas.",
        "Caridade. Sempre ajudo quem está em necessidade.",
        "Aspiração. Busco ser digno da graça do meu deus.",
        "Justiça. Injustiças devem ser corrigidas.",
    ],
    "lacos": [
        "Entregaria a vida para recuperar uma relíquia antiga.",
        "Ainda sinto culpa por abandonar o templo.",
        "Devo minha vida ao sacerdote que me acolheu.",
        "Tudo o que faço é pelo povo comum.",
    ],
    "fraquezas": [
        "Julgo os outros severamente e a mim mesmo ainda mais.",
        "Confio cegamente na autoridade de qualquer templo.",
        "Sou inflexível em meus pensamentos e crenças.",
        "Suspeito de estranhos e espero o pior deles.",
    ],
}

_TRACOS_NOBRE: TracosDict = {
    "personalidade": [
        "Sou honesto demais para disfarçar meus verdadeiros sentimentos.",
        "Gosto de resolver problemas com palavras, não com armas.",
        "Insulto os outros com elegante condescendência.",
        "Guardo um segredo que poderia arruinar minha família.",
    ],
    "ideais": [
        "Responsabilidade. Devo respeitar quem está abaixo de mim.",
        "Poder. Se eu obtiver poder, ninguém me dirá o que fazer.",
        "Independência. Não devo favores a ninguém.",
        "Nobreza. Meu dever é proteger os fracos.",
    ],
    "lacos": [
        "Esconderei qualquer coisa para proteger a honra da família.",
        "A lealdade à minha família vem antes de tudo.",
        "O povo precisa ver-me como herói.",
        "Quero provar que mereço o título que carrego.",
    ],
    "fraquezas": [
        "Secretamente acredito que todos estão abaixo de mim.",
        "Escondo um escândalo que destruiria minha família.",
        "Ouço insultos mesmo quando ninguém os pronuncia.",
        "Tenho dificuldade em confiar na lealdade dos outros.",
    ],
}

_TRACOS_SOLDADO: TracosDict = {
    "personalidade": [
        "Sou sempre polido e respeitoso.",
        "Sou assombrado por memórias de guerra.",
        "Ganhei pouco respeito por superiores incompetentes.",
        "Falo de forma direta sobre táticas e batalhas.",
    ],
    "ideais": [
        "Grandeza. O objetivo de um soldado é alcançar a glória.",
        "Responsabilidade. Faço o que precisa ser feito.",
        "Independência. Quando sigo ordens, perco minha identidade.",
        "Povo. Meus camaradas são mais importantes que reinos.",
    ],
    "lacos": [
        "Daria a vida pelos soldados com quem servi.",
        "Protejo quem não pode se proteger.",
        "Busco honrar um companheiro que caiu em batalha.",
        "Luto para esquecer as atrocidades que testemunhei.",
    ],
    "fraquezas": [
        "O inimigo cruel que derrotarei a qualquer custo.",
        "Não sinto compaixão por mortos inimigos.",
        "Obedeço ordens mesmo quando questiono sua justiça.",
        "A bebida me faz esquecer o que vi.",
    ],
}

_TRACOS_GENERICO: TracosDict = {
    "personalidade": [
        "Prefiro agir antes de pensar demais.",
        "Valorizo um plano bem feito.",
        "Conto histórias em quase toda conversa.",
        "Sou curioso sobre lugares e pessoas novas.",
    ],
    "ideais": [
        "Liberdade. Correntes existem para ser quebradas.",
        "Comunidade. Todos devem ajudar uns aos outros.",
        "Conhecimento. A verdade vale mais que ouro.",
        "Redenção. Todo mundo merece uma segunda chance.",
    ],
    "lacos": [
        "Protejo quem não pode se defender sozinho.",
        "Devo uma dívida que nunca poderei pagar.",
        "Busco vingar uma injustiça do passado.",
        "Quero recuperar algo que perdi.",
    ],
    "fraquezas": [
        "Confio demais em quem demonstra bondade.",
        "A violência é muitas vezes minha primeira resposta.",
        "Guardo ressentimentos por muito tempo.",
        "Tenho medo de falhar com quem depende de mim.",
    ],
}

TRACOS_POR_ANTECEDENTE: Dict[str, TracosDict] = {
    "acolito": _TRACOS_ACOLITO,
    "nobre": _TRACOS_NOBRE,
    "soldado": _TRACOS_SOLDADO,
    "artesao-guilda": _TRACOS_GENERICO,
    "criminoso": _TRACOS_GENERICO,
    "forasteiro": _TRACOS_GENERICO,
    "heroi-popular": _TRACOS_GENERICO,
    "charlatao": _TRACOS_GENERICO,
    "artista": _TRACOS_GENERICO,
    "eremita": _TRACOS_GENERICO,
    "sabio": _TRACOS_GENERICO,
    "marinheiro": _TRACOS_GENERICO,
    "orphan": _TRACOS_GENERICO,
}

CATEGORIAS_TRACOS = ("personalidade", "ideais", "lacos", "fraquezas")


def tracos_opcoes_antecedente(slug: str) -> Dict[str, List[str]]:
    key = (slug or "").strip().lower()
    base = TRACOS_POR_ANTECEDENTE.get(key, _TRACOS_GENERICO)
    return {cat: list(base.get(cat) or []) for cat in CATEGORIAS_TRACOS}
