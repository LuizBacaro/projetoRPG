#!/usr/bin/env python3
"""
Gera catalogo enriquecido de Vantagens e Desvantagens GURPS (Modulo Basico -
Personagens, tabelas rapidas pags. 298-301), preservando as pericias existentes.

Uso:
    python3 scripts/gurps_gerar_sumario_enriquecido.py

Contrato de saida por item (JSON):
    - nome: str
    - custo_texto: str  (texto do livro, ex. "-15*", "5/nível", "Variável")
    - custo: int | None  (valor unico quando aplicavel)
    - cost_model: "fixo" | "por_nivel" | "opcoes_discretas" | "faixa" |
                    "fixo_mais_por_nivel" | "variavel"
    - custo_por_nivel: int             (por_nivel / fixo_mais_por_nivel)
    - custo_base: int                  (fixo_mais_por_nivel)
    - custo_min / custo_max: int       (faixa)
    - opcoes_custo: [{rotulo?, custo}] (opcoes_discretas)
    - autocontrole: bool               (marcada com "*" no livro)
    - paginas: [int]                   (referencia para lookup manual)
    - tipo_mfsoc: "M" | "F" | "Soc" | "M/F"   (opcional)
    - exotica_sob: "X" | "Sob" | null           (opcional)

Fontes: tabelas de referencia rapida do Modulo Personagens
(pags. 298-299 vantagens; 300-301 desvantagens). Valores validados no corpo
do livro quando aplicavel (Pacifismo p.151; Indulgente p.146; etc.).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "backend"
    / "app"
    / "games"
    / "gurps"
    / "catalogs"
    / "gurps_personagens_sumario_catalogo.json"
)


def fixo(nome: str, custo: int, *, mfsoc: str | None = None,
         xsob: str | None = None, pag: int | None = None,
         autocontrole: bool = False) -> dict[str, Any]:
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": (f"{custo}*" if autocontrole else str(custo)),
        "custo": custo,
        "cost_model": "fixo",
    }
    if autocontrole:
        item["autocontrole"] = True
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


def por_nivel(nome: str, custo_por_nivel: int, *, mfsoc: str | None = None,
              xsob: str | None = None, pag: int | None = None,
              rotulo_unidade: str = "nível") -> dict[str, Any]:
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": f"{custo_por_nivel}/{rotulo_unidade}",
        "custo": custo_por_nivel,
        "cost_model": "por_nivel",
        "custo_por_nivel": custo_por_nivel,
    }
    if rotulo_unidade != "nível":
        item["unidade_nivel"] = rotulo_unidade
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


def opcoes(nome: str, custo_texto: str, opcoes_lista: list[dict[str, Any]], *,
           mfsoc: str | None = None, xsob: str | None = None,
           pag: int | None = None, autocontrole: bool = False,
           custo_padrao: int | None = None) -> dict[str, Any]:
    custos = [o["custo"] for o in opcoes_lista if isinstance(o.get("custo"), int)]
    custo_default = custo_padrao if custo_padrao is not None else (custos[0] if custos else None)
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": custo_texto,
        "custo": custo_default,
        "cost_model": "opcoes_discretas",
        "opcoes_custo": opcoes_lista,
    }
    if autocontrole:
        item["autocontrole"] = True
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


def faixa(nome: str, cmin: int, cmax: int, *, custo_texto: str | None = None,
          mfsoc: str | None = None, xsob: str | None = None,
          pag: int | None = None, autocontrole: bool = False) -> dict[str, Any]:
    txt = custo_texto or f"{cmin} a {cmax}"
    if autocontrole and not txt.endswith("*"):
        txt = f"{txt}*"
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": txt,
        "custo": cmin,
        "cost_model": "faixa",
        "custo_min": cmin,
        "custo_max": cmax,
    }
    if autocontrole:
        item["autocontrole"] = True
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


def variavel(nome: str, *, mfsoc: str | None = None, xsob: str | None = None,
             pag: int | None = None, autocontrole: bool = False,
             custo_texto: str = "Variável") -> dict[str, Any]:
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": custo_texto,
        "custo": None,
        "cost_model": "variavel",
    }
    if autocontrole:
        item["autocontrole"] = True
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


def base_mais_nivel(nome: str, base: int, por_nivel_v: int, *,
                    mfsoc: str | None = None, xsob: str | None = None,
                    pag: int | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "nome": nome,
        "custo_texto": f"{base} + {por_nivel_v}/nível",
        "custo": base,
        "cost_model": "fixo_mais_por_nivel",
        "custo_base": base,
        "custo_por_nivel": por_nivel_v,
    }
    if mfsoc:
        item["tipo_mfsoc"] = mfsoc
    if xsob:
        item["exotica_sob"] = xsob
    if pag:
        item["paginas"] = [pag]
    return item


# --------------------------------------------------------------------------
# VANTAGENS (tabela rapida pags. 298-299)
# --------------------------------------------------------------------------

def montar_vantagens() -> list[dict[str, Any]]:
    v: list[dict[str, Any]] = []
    add = v.append

    add(por_nivel("Abafador de Mana", 10, mfsoc="M", xsob="Sob", pag=34))
    add(por_nivel("Abascanto", 2, mfsoc="M", xsob="Sob", pag=34))
    add(fixo("Abencoado", 10, mfsoc="M", xsob="Sob", pag=35))
    add(fixo("Acessorios", 1, mfsoc="F", xsob="X", pag=100))
    add(fixo("Adaptabilidade Cultural", 10, mfsoc="M", pag=35))
    add(opcoes(
        "Adaptacao ao Terreno",
        "0 ou 5",
        [{"custo": 0}, {"custo": 5}],
        mfsoc="F", xsob="X", pag=35,
    ))
    add(fixo("Aderencia", 20, mfsoc="F", xsob="X", pag=35))
    add(por_nivel("Agente Cativante", 15, mfsoc="M", pag=90))
    add(variavel("Aliados", mfsoc="Soc", pag=35))
    add(fixo("Ambidestria", 5, mfsoc="F", pag=38))
    add(por_nivel("Ampliador de Mana", 50, mfsoc="M", xsob="Sob", pag=38))
    add(fixo("Anfibio", 10, mfsoc="F", pag=39))
    add(variavel("Antecedentes Incomuns", mfsoc="M", pag=39))
    add(fixo("Apagado", 10, mfsoc="Soc", pag=39))
    add(variavel("Aparencia", mfsoc="F", pag=21, custo_texto="Variável"))
    add(por_nivel("Apetrechos", 5, mfsoc="M", pag=39, rotulo_unidade="apetrecho"))
    add(base_mais_nivel("Aptidao Magica", 5, 10, mfsoc="M", xsob="Sob", pag=40))
    add(fixo("Arrebatador", 80, mfsoc="M", xsob="Sob", pag=41))
    add(fixo("Arremedo", 10, mfsoc="M", xsob="X", pag=42))
    add(por_nivel("Artifice", 10, mfsoc="M", pag=90))
    add(por_nivel("Artista Talentoso", 5, mfsoc="M", pag=90))
    add(por_nivel("Ataque Adicional", 25, mfsoc="F", pag=42))
    add(fixo("Ataque Constritivo", 15, mfsoc="F", xsob="X", pag=42))
    add(variavel("Ataque Inato", mfsoc="F", xsob="X", pag=42))
    add(fixo("Atirador", 25, mfsoc="M", pag=43))
    add(por_nivel("Atribulacao", 10, mfsoc="F", xsob="X", pag=44))
    add(por_nivel("Audicao Agucada", 2, mfsoc="F", pag=89))
    add(fixo("Audicao Discriminatoria", 15, mfsoc="F", xsob="X", pag=45))
    add(por_nivel("Audicao Parabolica", 4, mfsoc="F", xsob="X", pag=45))
    add(opcoes(
        "Audicao Subsonica",
        "0 ou 5",
        [{"custo": 0}, {"custo": 5}],
        mfsoc="F", xsob="X", pag=45,
    ))
    add(fixo("Autotranse", 1, mfsoc="M", pag=100))
    add(fixo("Boa Forma", 5, mfsoc="F", pag=45))
    add(por_nivel("Boca Adicional", 5, mfsoc="F", xsob="X", pag=45, rotulo_unidade="boca"))
    add(fixo("Bom Senso", 10, mfsoc="M", pag=45))
    add(variavel("Bracos Adicionais", mfsoc="F", xsob="X", pag=45))
    add(por_nivel("Cabeca Adicional", 15, mfsoc="F", xsob="X", pag=46))
    add(fixo("Calculos Instantaneos", 2, mfsoc="M", pag=46))
    add(por_nivel("Camaleao", 5, mfsoc="F", xsob="X", pag=46))
    add(fixo("Camaleao Social", 5, mfsoc="M", pag=46))
    add(fixo("Caminhar no Ar", 20, mfsoc="F", xsob="X", pag=47))
    add(fixo("Caminhar sobre Liquidos", 15, mfsoc="F", xsob="X", pag=47))
    add(fixo("Canalizacao", 10, mfsoc="M", xsob="Sob", pag=47))
    add(por_nivel("Carga Util", 1, mfsoc="F", xsob="X", pag=47))
    add(por_nivel("Carisma", 5, mfsoc="M", pag=47))
    add(variavel("Cibernetica", mfsoc="F", pag=47))
    add(fixo("Clarisenciencia", 50, mfsoc="M", xsob="Sob", pag=47))
    add(fixo("Clericato", 5, mfsoc="Soc", pag=48))
    add(por_nivel("Companheiro Animal", 5, mfsoc="M", pag=90))
    add(por_nivel("Consumo Reduzido", 2, mfsoc="F", pag=48))
    add(variavel("Contatos", mfsoc="Soc", pag=48))
    add(fixo("Controle da Mente", 50, mfsoc="M", xsob="X", pag=49))
    add(por_nivel("Controle do Metabolismo", 5, mfsoc="F", xsob="X", pag=50))
    add(por_nivel("Controle Termico", 5, mfsoc="M/F", xsob="X", pag=50))
    add(por_nivel("Crescimento", 10, mfsoc="F", xsob="X", pag=51))
    add(fixo("Cronolocalizacao", 5, mfsoc="M", pag=73))
    add(fixo("Cura", 30, mfsoc="M", xsob="X", pag=51))
    add(por_nivel("Dedos Verdes", 5, mfsoc="M", pag=90))
    add(variavel("Defesas Ampliadas", mfsoc="M", pag=52))
    add(opcoes(
        "Dentes",
        "0, 1 ou 2",
        [{"custo": 0}, {"custo": 1}, {"custo": 2}],
        mfsoc="F", xsob="X", pag=52,
    ))
    add(opcoes(
        "Desenvolvedor",
        "25 ou 50",
        [{"custo": 25}, {"custo": 50}],
        mfsoc="M", pag=52,
    ))
    add(por_nivel("Deslocamento Ampliado", 20, mfsoc="F", xsob="X", pag=52))
    add(por_nivel("Destemor", 2, mfsoc="M", pag=53))
    add(variavel("Destino", mfsoc="M", xsob="Sob", pag=53))
    add(por_nivel("Destreza Manual Elevada", 5, mfsoc="F", pag=53))
    add(variavel("Detectar", mfsoc="M/F", xsob="X", pag=53))
    add(por_nivel("Dificil de Subjugar", 2, mfsoc="F", pag=54))
    add(fixo("Digestao Universal", 5, mfsoc="F", xsob="X", pag=54))
    add(fixo("Dobra", 100, mfsoc="M", xsob="Sob", pag=54))
    add(fixo("Dominacao", 20, mfsoc="M", xsob="X", pag=55))
    add(fixo("Dorminhoco", 1, mfsoc="F", pag=101))
    add(por_nivel("Duplicacao", 35, mfsoc="F", xsob="X", pag=56, rotulo_unidade="copia"))
    add(fixo("Durabilidade Sobrenatural", 150, mfsoc="F", xsob="Sob", pag=56))
    add(por_nivel("Duro de Matar", 2, mfsoc="F", pag=56))
    add(por_nivel("Elasticidade", 6, mfsoc="F", xsob="X", pag=57))
    add(variavel("Elo Mental", mfsoc="M", xsob="X", pag=57))
    add(fixo("Empatia", 15, mfsoc="M", pag=57))
    add(fixo("Empatia com Animais", 5, mfsoc="M", pag=57))
    add(fixo("Empatia com Espiritos", 10, mfsoc="M", xsob="Sob", pag=57))
    add(fixo("Empatia com Plantas", 5, mfsoc="M", pag=58))
    add(por_nivel("Encolhimento", 5, mfsoc="F", xsob="X", pag=58))
    add(fixo("Equilibrio Perfeito", 15, mfsoc="F", pag=58))
    add(variavel("Equipamento Caracteristico", mfsoc="Soc", pag=58))
    add(base_mais_nivel("Escavacao", 30, 5, mfsoc="F", xsob="X", pag=58))
    add(por_nivel("Escorregadio", 2, mfsoc="F", xsob="X", pag=59))
    add(por_nivel("Escudo Mental", 4, mfsoc="M", xsob="X", pag=59))
    add(variavel("Espinhos", mfsoc="F", xsob="X", pag=59))
    add(fixo("Estabilidade no Emprego", 1, mfsoc="Soc", pag=59))
    add(variavel("Estatica Psiquica", mfsoc="M", pag=59))
    add(variavel("Estilo", mfsoc="M/F", pag=100))
    add(por_nivel("Expectativa de Vida Ampliada", 2, mfsoc="F", xsob="X", pag=59))
    add(variavel("Experiencia-G", mfsoc="M", pag=60))
    add(variavel("Explorador", mfsoc="M", pag=60))
    add(fixo("Facilidade para Idiomas", 5, mfsoc="M", pag=60))
    add(variavel("Fala Subaquatica", mfsoc="F", xsob="X", pag=60))
    add(opcoes(
        "Fala Subsonica",
        "0 ou 10",
        [{"custo": 0}, {"custo": 10}],
        mfsoc="F", xsob="X", pag=60,
    ))
    add(opcoes(
        "Fala Ultrassonica",
        "0 a 10",
        [{"custo": 0}, {"custo": 10}],
        mfsoc="F", xsob="X", pag=60,
    ))
    add(fixo("Falar com Animais", 25, mfsoc="M", xsob="X", pag=60))
    add(fixo("Falar com Plantas", 15, mfsoc="M", xsob="X", pag=60))
    add(opcoes(
        "Familiaridade Cultural",
        "1 ou 2/cultura",
        [{"custo": 1}, {"custo": 2}],
        mfsoc="Soc", pag=23,
    ))
    add(variavel("Favor", mfsoc="Soc", pag=55))
    add(fixo("Fe", 15, mfsoc="M", xsob="Sob", pag=60))
    add(fixo("Fleuma", 15, mfsoc="M", pag=60))
    add(fixo("Flexibilidade", 5, mfsoc="F", pag=56))
    add(variavel("Forma Alternativa", mfsoc="F", xsob="X", pag=61))
    add(fixo("Forma de Sombras", 50, mfsoc="F", xsob="X", pag=61))
    add(variavel("Garras", mfsoc="F", xsob="X", pag=61))
    add(fixo("Golpeadores", 5, mfsoc="F", xsob="X", pag=62))
    add(variavel("Grupo de Contato", mfsoc="Soc", pag=62))
    add(por_nivel("Habilidade Matematica", 10, mfsoc="M", pag=90))
    add(por_nivel("Habilidade Musical", 5, mfsoc="M", pag=90))
    add(variavel("Habilidades Modulares", mfsoc="M/F", pag=63))
    add(opcoes(
        "Hierarquia",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(opcoes(
        "Hierarquia Administrativa",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(opcoes(
        "Hierarquia Comercial",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(por_nivel("Hierarquia Honoraria", 1, mfsoc="Soc", pag=29))
    add(opcoes(
        "Hierarquia Militar",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(opcoes(
        "Hierarquia Policial",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(opcoes(
        "Hierarquia Religiosa",
        "5 ou 10/nível",
        [{"custo": 5}, {"custo": 10}],
        mfsoc="Soc", pag=29,
    ))
    add(fixo("Hipoalgia (Alto Limiar de Dor)", 10, mfsoc="F", pag=63))
    add(fixo("Idade Imutavel", 15, mfsoc="F", xsob="X", pag=63))
    add(opcoes(
        "Identidade Alternativa",
        "5 ou 15",
        [
            {"rotulo": "Legal", "custo": 5},
            {"rotulo": "Ilegal", "custo": 15},
        ],
        mfsoc="Soc", pag=63,
    ))
    add(fixo("Iluminado", 15, mfsoc="M", xsob="Sob", pag=64))
    add(faixa("Impossivel de Matar", 50, 150, mfsoc="F", xsob="X", pag=64))
    add(faixa("Imunidade Legal", 5, 20, mfsoc="Soc", pag=65))
    add(fixo("Indomavel", 15, mfsoc="M", pag=65))
    add(fixo("Inercia Temporal", 15, mfsoc="M", xsob="Sob", pag=65))
    add(opcoes(
        "Infravisao",
        "0 ou 10",
        [{"custo": 0}, {"custo": 10}],
        mfsoc="F", xsob="X", pag=65,
    ))
    add(fixo("Insubstancialidade", 80, mfsoc="M/F", xsob="X", pag=65))
    add(variavel("Interposicao", mfsoc="F", xsob="X", pag=66))
    add(fixo("Intuicao", 15, mfsoc="M", pag=67))
    add(por_nivel("Investidura de Poder", 10, mfsoc="M", xsob="Sob", pag=67))
    add(fixo("Invisibilidade", 40, mfsoc="M/F", xsob="X", pag=67))
    add(fixo("Lacrado", 15, mfsoc="F", xsob="X", pag=68))
    add(fixo("Lamentavel", 5, mfsoc="Soc", pag=22))
    add(fixo("Leitura da Mente", 30, mfsoc="M", xsob="X", pag=68))
    add(fixo("Lingua Ferina", 5, mfsoc="M", pag=68))
    add(fixo("Longevidade", 2, mfsoc="F", pag=69))
    add(fixo("Matematico Intuitivo", 5, mfsoc="M", pag=46))
    add(fixo("Medium", 10, mfsoc="M", xsob="Sob", pag=69))
    add(por_nivel("Membrana Nictitante", 1, mfsoc="F", xsob="X", pag=69))
    add(fixo("Memoria Eidetica", 5, mfsoc="M", pag=69))
    add(fixo("Memoria Fotografica", 10, mfsoc="M", pag=69))
    add(opcoes(
        "Memoria Racial",
        "15 ou 40",
        [
            {"rotulo": "Passiva", "custo": 15},
            {"rotulo": "Ativa", "custo": 40},
        ],
        mfsoc="M", xsob="X", pag=69,
    ))
    add(fixo("Mente Digital", 5, mfsoc="F", xsob="X", pag=69))
    add(por_nivel("Mente Segmentada", 50, mfsoc="M", xsob="X", pag=70))
    add(variavel("Mestre de Armas", mfsoc="M", pag=70))
    add(fixo("Metabolismo Impoluto", 1, mfsoc="F", xsob="X", pag=101))
    add(variavel("Metamorfose", mfsoc="F", xsob="X", pag=71))
    add(base_mais_nivel("Mordida de Vampiro", 30, 5, mfsoc="F", xsob="X", pag=72))
    add(variavel("Morfose", mfsoc="F", xsob="X", pag=71))
    add(fixo("Nao Come nem Bebe", 10, mfsoc="F", xsob="X", pag=72))
    add(fixo("Nao Dorme", 20, mfsoc="F", xsob="X", pag=73))
    add(fixo("Nao Respira", 20, mfsoc="F", xsob="X", pag=73))
    add(fixo("Neutralizar", 50, mfsoc="M", xsob="X", pag=73))
    add(fixo("Nocao do Perigo", 15, mfsoc="M", pag=73))
    add(fixo("Nocao do Tempo Ampliado", 45, mfsoc="M", xsob="X", pag=73))
    add(fixo("Nocao Exata do Tempo", 2, mfsoc="M", pag=74))
    add(fixo("Nocao Tridimensional do Espaco", 10, mfsoc="F", pag=87))
    add(por_nivel("NT Alto", 5, mfsoc="M", pag=23))
    add(fixo("Olfato Discriminatorio", 15, mfsoc="F", xsob="X", pag=74))
    add(fixo("Oraculo", 15, mfsoc="M", xsob="Sob", pag=74))
    add(por_nivel("Padrao de Tempo Alterado", 100, mfsoc="F", xsob="X", pag=75))
    add(fixo("Paladar Discriminatorio", 10, mfsoc="F", xsob="X", pag=75))
    add(variavel("Patronos", mfsoc="Soc", pag=72))
    add(fixo("Pelagem", 1, mfsoc="F", pag=75))
    add(fixo("Pele Elastica", 20, mfsoc="F", xsob="X", pag=75))
    add(fixo("Pendulear", 5, mfsoc="F", pag=75))
    add(variavel("Permissao de Seguranca", mfsoc="Soc", pag=76))
    add(variavel("Pernas Adicionais", mfsoc="F", xsob="X", pag=76))
    add(opcoes(
        "Poderes Legais",
        "5, 10 ou 15",
        [{"custo": 5}, {"custo": 10}, {"custo": 15}],
        mfsoc="Soc", pag=76,
    ))
    add(fixo("Por Dentro da Moda", 5, mfsoc="Soc", pag=22))
    add(por_nivel("Pouco Sono", 2, mfsoc="F", pag=76))
    add(fixo("Precognicao", 25, mfsoc="M", xsob="Sob", pag=77))
    add(por_nivel("Prender a Respiracao", 2, mfsoc="F", pag=77))
    add(fixo("Proposito Maior", 5, mfsoc="M", pag=77))
    add(fixo("Psicometria", 20, mfsoc="M", xsob="Sob", pag=78))
    add(fixo("Pulmoes com Filtro", 5, mfsoc="F", pag=78))
    add(fixo("Queda de Gato", 10, mfsoc="F", xsob="X", pag=78))
    add(por_nivel("Rastreamento Ampliado", 5, mfsoc="F", xsob="X", pag=82))
    add(fixo("Reconhecimento Social", 5, mfsoc="Soc", pag=82))
    add(fixo("Recuperacao Acelerada", 5, mfsoc="F", pag=82))
    add(fixo("Recuperacao da Consciencia", 10, mfsoc="F", xsob="X", pag=82))
    add(fixo("Recuperacao Muito Acelerada", 15, mfsoc="F", pag=82))
    add(fixo("Redespertar", 10, mfsoc="M", xsob="Sob", pag=82))
    add(fixo("Reflexos em Combate", 15, mfsoc="M", pag=82))
    add(variavel("Regeneracao", mfsoc="F", xsob="X", pag=82))
    add(faixa("Reivindicar Hospitalidade", 1, 10, mfsoc="Soc", pag=83))
    add(por_nivel("Renda Propria", 1, mfsoc="Soc", pag=26))
    add(variavel("Reputacao", mfsoc="Soc", pag=26))
    add(por_nivel("Resistencia a Dano", 5, mfsoc="F", xsob="X", pag=83))
    add(faixa("Resistencia a Pressao", 5, 15, mfsoc="F", xsob="X", pag=84))
    add(fixo("Resistencia ao Vacuo", 5, mfsoc="F", xsob="X", pag=85))
    add(variavel("Resistente", mfsoc="F", pag=85))
    add(fixo("Restaurar Membros", 40, mfsoc="F", xsob="X", pag=85))
    add(por_nivel("Retencao", 2, mfsoc="F", xsob="X", pag=85))
    add(variavel("Riqueza", mfsoc="Soc", pag=25))
    add(fixo("Rosto Sincero", 1, mfsoc="F", pag=101))
    add(fixo("Saltador", 100, mfsoc="M", xsob="Sob", pag=86))
    add(fixo("Sem Ressaca", 1, mfsoc="F", pag=101))
    add(fixo("Sensivel", 5, mfsoc="M", pag=57))
    add(fixo("Senso de Direcao", 5, mfsoc="F", pag=87))
    add(variavel("Sentido de Monitoramento", mfsoc="F", xsob="X", pag=87))
    add(fixo("Sentido de Vibracao", 10, mfsoc="F", xsob="X", pag=88))
    add(por_nivel("Sentido Protegido", 5, mfsoc="F", xsob="X", pag=88, rotulo_unidade="sentido"))
    add(por_nivel("Serendipidade", 15, mfsoc="M", pag=89))
    add(por_nivel("Silencio", 5, mfsoc="F", xsob="X", pag=89))
    add(fixo("Sonda Mental", 20, mfsoc="M", xsob="X", pag=89))
    add(variavel("Sorte", mfsoc="M", pag=89))
    add(opcoes(
        "ST Bracal",
        "3, 5 ou 8/nível",
        [{"custo": 3}, {"custo": 5}, {"custo": 8}],
        mfsoc="F", xsob="X", pag=90,
    ))
    add(por_nivel("ST de Golpe", 5, mfsoc="F", xsob="X", pag=90))
    add(por_nivel("ST de Levantamento", 3, mfsoc="F", xsob="X", pag=90))
    add(por_nivel("Status", 5, mfsoc="Soc", pag=28))
    add(por_nivel("Super Escalada", 3, mfsoc="F", xsob="X", pag=90))
    add(por_nivel("Super Salto", 10, mfsoc="F", xsob="X", pag=90))
    add(fixo("Super Sorte", 100, mfsoc="M", xsob="Sob", pag=90))
    add(opcoes(
        "Superaudicao",
        "0 ou 5",
        [{"custo": 0}, {"custo": 5}],
        mfsoc="F", xsob="X", pag=90,
    ))
    add(variavel("Talento", mfsoc="M", pag=90))
    add(por_nivel("Talento Instintivo", 20, mfsoc="M", xsob="Sob", pag=92))
    add(por_nivel("Tato Apurado", 2, mfsoc="F", pag=89))
    add(por_nivel("Telecinese", 5, mfsoc="M/F", xsob="X", pag=92))
    add(variavel("Telecomunicacao", mfsoc="M/F", xsob="X", pag=93))
    add(base_mais_nivel("Terror", 30, 10, mfsoc="M", xsob="Sob", pag=94))
    add(faixa("Titere", 5, 10, mfsoc="M", xsob="X", pag=94))
    add(variavel("Tolerancia a Ferimentos", mfsoc="F", xsob="X", pag=94))
    add(fixo("Tolerancia ao Alcool", 1, mfsoc="F", pag=101))
    add(variavel("Tolerancia a Radiacao", mfsoc="F", xsob="X", pag=95))
    add(por_nivel("Tolerancia a Temperatura", 1, mfsoc="F", pag=96))
    add(faixa("Tolerancia-G Ampliada", 5, 25, mfsoc="F", pag=96))
    add(fixo("Toque Sensivel", 10, mfsoc="F", pag=96))
    add(fixo("Treinado por um Mestre", 30, mfsoc="M", pag=96))
    add(fixo("Ultraflexibilidade das Juntas", 15, mfsoc="F", xsob="X", pag=97))
    add(opcoes(
        "Ultravisao",
        "0 ou 10",
        [{"custo": 0}, {"custo": 10}],
        mfsoc="F", xsob="X", pag=97,
    ))
    add(fixo("Venturoso", 15, mfsoc="M", pag=97))
    add(fixo("Ver o Invisivel", 15, mfsoc="M", xsob="Sob", pag=97))
    add(fixo("Versatil", 5, mfsoc="M", pag=98))
    add(por_nivel("Vida Extra", 25, mfsoc="F", xsob="X", pag=98, rotulo_unidade="vida"))
    add(fixo("Vinculo Especial", 5, mfsoc="M", xsob="X", pag=98))
    add(fixo("Visao 360 Graus", 25, mfsoc="F", xsob="X", pag=98))
    add(por_nivel("Visao Agucada", 2, mfsoc="F", pag=98))
    add(fixo("Visao Hiperespectral", 25, mfsoc="F", xsob="X", pag=98))
    add(por_nivel("Visao Microscopica", 5, mfsoc="F", xsob="X", pag=99))
    add(fixo("Visao no Escuro", 25, mfsoc="F", xsob="X", pag=99))
    add(por_nivel("Visao Noturna", 1, mfsoc="F", pag=99))
    add(por_nivel("Visao Penetrante", 10, mfsoc="F", xsob="X", pag=99))
    add(fixo("Visao Periferica", 15, mfsoc="F", pag=99))
    add(por_nivel("Visao Telescopica", 5, mfsoc="F", pag=99))
    add(fixo("Visualizacao", 10, mfsoc="M", pag=100))
    add(fixo("Voz Melodiosa", 10, mfsoc="F", pag=101))
    add(fixo("Voz Penetrante", 1, mfsoc="F", pag=101))
    add(fixo("Xeno-adaptabilidade", 20, mfsoc="M", pag=100))
    return v


# --------------------------------------------------------------------------
# DESVANTAGENS (tabela rapida pags. 300-301)
# --------------------------------------------------------------------------

def montar_desvantagens() -> list[dict[str, Any]]:
    d: list[dict[str, Any]] = []
    add = d.append

    add(fixo("Acima do Peso", -1, mfsoc="F", pag=19))
    add(fixo("Acomodado", -1, mfsoc="M", pag=163))
    add(opcoes(
        "Alcoolismo",
        "-15 ou -20",
        [
            {"rotulo": "Alcoolismo", "custo": -15},
            {"rotulo": "Alcoolismo severo", "custo": -20},
        ],
        mfsoc="F", pag=122,
    ))
    add(fixo("Altruismo", -5, autocontrole=True, mfsoc="M", pag=122))
    add(fixo("Amigavel", -5, mfsoc="M", pag=122))
    add(opcoes(
        "Amnesia",
        "-10 ou -25",
        [
            {"rotulo": "Parcial", "custo": -10},
            {"rotulo": "Total", "custo": -25},
        ],
        mfsoc="M", pag=122,
    ))
    add(fixo("Antecedentes Mundanos", -10, mfsoc="M", pag=122))
    add(fixo("Antipatico", -1, mfsoc="M", pag=163))
    add(variavel("Aparencia", mfsoc="F", pag=20))
    add(fixo("Apetite Incontrolavel", -15, autocontrole=True, mfsoc="F", xsob="Sob", pag=122))
    add(fixo("Assexuado", -1, mfsoc="F", xsob="X", pag=165))
    add(fixo("Assustar Animais", -10, mfsoc="M", xsob="Sob", pag=123))
    add(fixo("Ataque Infeccioso", -5, mfsoc="F", xsob="Sob", pag=123))
    add(variavel("Atavismo por Estresse", mfsoc="M", xsob="X", pag=123, autocontrole=True, custo_texto="Variável*"))
    add(fixo("Atento", -1, mfsoc="M", pag=163))
    add(opcoes(
        "Atrapalhado",
        "-5 ou -10",
        [{"custo": -5}, {"custo": -10}],
        mfsoc="F", pag=123,
    ))
    add(fixo("Autodestruicao", -10, mfsoc="F", xsob="X", pag=123))
    add(fixo("Avareza", -10, autocontrole=True, mfsoc="M", pag=123))
    add(variavel("Aversao", mfsoc="M", xsob="Sob", pag=123))
    add(fixo("Aversoes", -1, mfsoc="M", pag=163))
    add(fixo("Azar", -10, mfsoc="M", pag=124))
    add(fixo("Baixa Autoestima", -10, mfsoc="M", pag=124))
    add(por_nivel("Barulhento", -2, mfsoc="F", pag=124))
    add(opcoes(
        "Bestial",
        "-10 ou -15",
        [{"custo": -10}, {"custo": -15}],
        mfsoc="M", xsob="X", pag=124,
    ))
    add(fixo("Bioquimica Incomum", -5, mfsoc="F", xsob="X", pag=124))
    add(fixo("Briguento", -10, autocontrole=True, mfsoc="M", pag=125))
    add(fixo("Castrado", -1, mfsoc="F", pag=165))
    add(fixo("Cegueira", -50, mfsoc="F", pag=125))
    add(fixo("Cegueira Noturna", -10, mfsoc="F", pag=126))
    add(fixo("Chauvinista", -1, mfsoc="M", pag=163))
    add(fixo("Circunspeccao", -10, mfsoc="M", pag=126))
    add(fixo("Cleptomania", -15, autocontrole=True, mfsoc="M", pag=126))
    add(fixo("Cobica", -15, autocontrole=True, mfsoc="M", pag=126))
    add(opcoes(
        "Codigo de Honra",
        "-1 ou -5 a -15",
        [
            {"rotulo": "Peculiaridade", "custo": -1},
            {"rotulo": "Pessoal", "custo": -5},
            {"rotulo": "Profissional", "custo": -10},
            {"rotulo": "Estrito", "custo": -15},
        ],
        mfsoc="M", pag=126,
    ))
    add(fixo("Completamente Desastrado", -15, mfsoc="M", pag=131))
    add(fixo("Complexo de Culpa", -5, mfsoc="M", pag=127))
    add(fixo("Compreensivo", -1, mfsoc="M", pag=163))
    add(faixa("Compulsao", -5, -15, autocontrole=True, mfsoc="M", pag=127))
    add(fixo("Confuso", -10, autocontrole=True, mfsoc="M", pag=128))
    add(por_nivel("Consumo Ampliado", -10, mfsoc="F", pag=128))
    add(fixo("Convulsoes Pos-combate", -5, autocontrole=True, mfsoc="M", pag=129))
    add(fixo("Corcunda", -10, mfsoc="F", pag=129))
    add(fixo("Covardia", -10, autocontrole=True, mfsoc="M", pag=129))
    add(fixo("Credulidade", -10, autocontrole=True, mfsoc="M", pag=129))
    add(fixo("Criativo", -1, mfsoc="M", pag=164))
    add(fixo("Cuidadoso", -1, mfsoc="M", pag=164))
    add(fixo("Curiosidade", -5, autocontrole=True, mfsoc="M", pag=129))
    add(fixo("Daltonismo", -10, mfsoc="F", pag=129))
    add(faixa("Deficiencia Fisica", -10, -30, mfsoc="F", pag=129))
    add(fixo("Deficiencias Menores", -1, mfsoc="F", pag=165))
    add(variavel("Dependencia", mfsoc="F", xsob="X", pag=130))
    add(variavel("Dependentes", mfsoc="Soc", pag=131))
    add(fixo("Depressao Cronica", -15, autocontrole=True, mfsoc="M", pag=131))
    add(fixo("Desastrado", -5, mfsoc="F", pag=131))
    add(fixo("Desatento", -10, autocontrole=True, mfsoc="M", pag=131))
    add(variavel("Dever", mfsoc="Soc", pag=133))
    add(faixa("Dieta Restrita", -10, -40, mfsoc="F", xsob="X", pag=133))
    add(fixo("Disopia", -25, mfsoc="F", pag=134))
    add(fixo("Disosmia", -5, mfsoc="F", pag=135))
    add(fixo("Distracao", -15, mfsoc="M", pag=135))
    add(fixo("Distraido", -1, mfsoc="M", pag=164))
    add(variavel("Disturbio Neurologico", mfsoc="F", pag=135))
    add(por_nivel("Dividas", -1, mfsoc="Soc", pag=26))
    add(fixo("Doenca Contagiosa", -5, mfsoc="F", pag=135))
    add(opcoes(
        "Doente Terminal",
        "-50, -75 ou -100",
        [
            {"rotulo": "6 meses a 2 anos", "custo": -50},
            {"rotulo": "1 semana a 6 meses", "custo": -75},
            {"rotulo": "menos de 1 semana", "custo": -100},
        ],
        mfsoc="F", pag=135,
    ))
    add(variavel("Dor Cronica", mfsoc="F", pag=135))
    add(fixo("Dorminhoco", -5, mfsoc="F", pag=136))
    add(faixa("Doutrinas Religiosas", -5, -15, mfsoc="M", pag=136))
    add(variavel("Drenagem", mfsoc="F", xsob="Sob", pag=136))
    add(fixo("Duro de Ouvido", -10, mfsoc="F", pag=137))
    add(fixo("Egoismo", -5, autocontrole=True, mfsoc="M", pag=137))
    add(fixo("Eletrico", -20, mfsoc="F", xsob="X", pag=137))
    add(fixo("Embotado", -1, mfsoc="M", pag=164))
    add(fixo("Enjoadico", -10, autocontrole=True, mfsoc="M", pag=137))
    add(fixo("Enjoo", -10, mfsoc="F", pag=137))
    add(fixo("Enjoo Espacial", -10, mfsoc="F", pag=137))
    add(fixo("Enjoo Temporal", -10, mfsoc="F", pag=137))
    add(fixo("Entorpecido", -20, mfsoc="F", pag=137))
    add(fixo("Enxerido", -1, mfsoc="M", pag=164))
    add(fixo("Epilepsia", -30, mfsoc="F", pag=137))
    add(faixa("Estigma Social", -5, -20, mfsoc="Soc", pag=138))
    add(fixo("Estomago Sensivel", -1, mfsoc="F", pag=165))
    add(fixo("Excesso de Confianca", -5, autocontrole=True, mfsoc="M", pag=139))
    add(por_nivel("Expectativa de Vida Reduzida", -10, mfsoc="F", xsob="X", pag=139))
    add(fixo("Facil de Decifrar", -10, mfsoc="M", pag=139))
    add(por_nivel("Facil de Matar", -2, mfsoc="F", pag=139))
    add(fixo("Fanatismo", -15, mfsoc="M", pag=139))
    add(opcoes(
        "Fantasias",
        "-1 ou -5 a -15",
        [
            {"rotulo": "Peculiaridade", "custo": -1},
            {"rotulo": "Fantasia", "custo": -5},
            {"rotulo": "Delirio serio", "custo": -10},
            {"rotulo": "Delirio grave", "custo": -15},
        ],
        mfsoc="M", pag=139,
    ))
    add(variavel("Feicoes Estranhas", mfsoc="F", pag=22))
    add(fixo("Ferido", -5, mfsoc="F", pag=140))
    add(variavel("Flashbacks", mfsoc="M", pag=140))
    add(variavel("Fobias", mfsoc="M", pag=140, autocontrole=True, custo_texto="Variável*"))
    add(fixo("Fora de Forma", -5, mfsoc="F", pag=142))
    add(variavel("Fragilidade", mfsoc="F", xsob="X", pag=142))
    add(fixo("Fragilidade em Aceleracao", -1, mfsoc="F", pag=165))
    add(variavel("Fraqueza", mfsoc="F", xsob="X", pag=143))
    add(fixo("Furia", -10, autocontrole=True, mfsoc="M", pag=143))
    add(fixo("Gagueira", -10, mfsoc="F", pag=143))
    add(fixo("Gigantismo", 0, mfsoc="F", pag=19))
    add(fixo("Gordo", -3, mfsoc="F", pag=19))
    add(fixo("Gregario", -10, mfsoc="M", pag=122))
    add(fixo("Gula", -5, autocontrole=True, mfsoc="M", pag=143))
    add(opcoes(
        "Habitos Detestaveis",
        "-5, -10 ou -15",
        [{"custo": -5}, {"custo": -10}, {"custo": -15}],
        mfsoc="M", pag=22,
    ))
    add(fixo("Habitos ou Expressoes", -1, mfsoc="M", pag=164))
    add(fixo("Hemofilia", -30, mfsoc="F", pag=144))
    add(fixo("Hiperalgia", -10, mfsoc="F", pag=144))
    add(fixo("Honestidade", -10, autocontrole=True, mfsoc="M", pag=144))
    add(fixo("Horizontal", -10, mfsoc="F", xsob="X", pag=145))
    add(variavel("Identidade Secreta", mfsoc="Soc", pag=145))
    add(fixo("Identidade Trocada", -5, mfsoc="F", pag=21))
    add(fixo("Impulsividade", -10, autocontrole=True, mfsoc="M", pag=145))
    add(fixo("Indulgente", -15, autocontrole=True, mfsoc="M", pag=146))
    add(variavel("Inimigos", mfsoc="Soc", pag=146))
    add(fixo("Insensivel", -5, mfsoc="M", pag=147))
    add(opcoes(
        "Insone",
        "-10 ou -15",
        [
            {"rotulo": "Leve", "custo": -10},
            {"rotulo": "Grave", "custo": -15},
        ],
        mfsoc="F", pag=147,
    ))
    add(variavel("Intolerancia", mfsoc="M", pag=147))
    add(fixo("Intolerancia ao Alcool", -1, mfsoc="F", pag=165))
    add(opcoes(
        "Intolerancia-G",
        "-10 ou -20",
        [{"custo": -10}, {"custo": -20}],
        mfsoc="F", pag=147,
    ))
    add(fixo("Inveja", -10, mfsoc="M", pag=147))
    add(fixo("Invertebrado", -20, mfsoc="F", xsob="X", pag=147))
    add(fixo("Irritabilidade", -10, autocontrole=True, mfsoc="M", pag=147))
    add(fixo("Lunatico", -10, mfsoc="M", pag=148))
    add(fixo("Luxuria", -15, autocontrole=True, mfsoc="M", pag=148))
    add(fixo("Magnetismo Sobrenatural", -15, mfsoc="M", xsob="Sob", pag=148))
    add(fixo("Magro", -1, mfsoc="F", pag=18))
    add(fixo("Maldicao", -75, mfsoc="M", xsob="Sob", pag=148))
    add(variavel("Maldicao Divina", mfsoc="M", xsob="Sob", pag=148))
    add(fixo("Maneta (Um Braco)", -20, mfsoc="F", pag=148))
    add(fixo("Maneta (Uma Mao)", -15, mfsoc="F", pag=148))
    add(fixo("Maniaco-depressivo", -20, mfsoc="M", pag=149))
    add(fixo("Manuseadores Precarios", -30, mfsoc="F", xsob="X", pag=149))
    add(variavel("Manutencao", mfsoc="F", pag=149))
    add(por_nivel("Mao Fraca", -5, mfsoc="F", pag=150))
    add(opcoes(
        "Marca Registrada",
        "-1 ou -5 a -15",
        [
            {"rotulo": "Peculiaridade", "custo": -1},
            {"rotulo": "Sutil", "custo": -5},
            {"rotulo": "Assinatura", "custo": -10},
            {"rotulo": "Marca elaborada", "custo": -15},
        ],
        mfsoc="M", pag=150,
    ))
    add(fixo("Mau Cheiro", -10, mfsoc="F", pag=150))
    add(fixo("Megalomania", -10, mfsoc="M", pag=150))
    add(fixo("Mentalidade de Escravo", -40, mfsoc="M", pag=150))
    add(fixo("Mente Aberta", -1, mfsoc="M", pag=164))
    add(fixo("Mordida Fraca", -2, mfsoc="F", xsob="X", pag=151))
    add(fixo("Mudanca de Personalidade", -1, mfsoc="M", pag=164))
    add(fixo("Mudez", -15, mfsoc="F", pag=145))
    add(fixo("Muito Fora de Forma", -15, mfsoc="F", pag=142))
    add(fixo("Muito Gordo", -5, mfsoc="F", pag=19))
    add(fixo("Nanismo", -15, mfsoc="F", pag=19))
    add(fixo("Nao-iconografico", -10, mfsoc="M", pag=151))
    add(fixo("No Limite", -15, autocontrole=True, mfsoc="M", pag=151))
    add(fixo("Noturno", -20, mfsoc="F", xsob="X", pag=151))
    add(por_nivel("NT Baixo", -5, mfsoc="M", pag=22))
    add(fixo("Oblivio", -5, mfsoc="M", pag=151))
    add(opcoes(
        "Obsessao",
        "-1, -5 ou -10*",
        [
            {"rotulo": "Peculiaridade", "custo": -1},
            {"rotulo": "Curto prazo", "custo": -5},
            {"rotulo": "Longo prazo", "custo": -10},
        ],
        mfsoc="M", pag=151, autocontrole=True,
    ))
    add(fixo("Orgulhoso", -1, mfsoc="M", pag=164))
    add(opcoes(
        "Pacifismo",
        "Variável",
        [
            {"rotulo": "Assassino Relutante", "custo": -5},
            {"rotulo": "Incapaz de Ferir Inocentes", "custo": -10},
            {"rotulo": "Incapaz de Matar", "custo": -15},
            {"rotulo": "Legitima Defesa", "custo": -15},
            {"rotulo": "Nao-Violencia Total", "custo": -30},
        ],
        mfsoc="M", pag=151,
    ))
    add(fixo("Padrao de Tempo Reduzido", -100, mfsoc="M", xsob="X", pag=152))
    add(fixo("Paralisia Frente ao Combate", -15, mfsoc="F", pag=152))
    add(fixo("Paranoia", -10, mfsoc="M", pag=152))
    add(fixo("Perna Torta", -1, mfsoc="F", pag=165))
    add(fixo("Pesadelos", -5, autocontrole=True, mfsoc="M", pag=152))
    add(fixo("Piromania", -5, autocontrole=True, mfsoc="M", pag=152))
    add(fixo("Pouca Empatia", -20, mfsoc="M", pag=153))
    add(fixo("Preferencias", -1, mfsoc="M", pag=164))
    add(fixo("Preguica", -10, mfsoc="M", pag=153))
    add(opcoes(
        "Problemas na Coluna",
        "-15 ou -25",
        [{"custo": -15}, {"custo": -25}],
        mfsoc="F", pag=153,
    ))
    add(por_nivel("Recuperacao Lenta", -5, mfsoc="F", pag=153))
    add(fixo("Refeicao Demorada", -10, mfsoc="F", xsob="X", pag=153))
    add(fixo("Reprogramavel", -10, mfsoc="M", xsob="X", pag=153))
    add(faixa("Repugnancia", -5, -15, mfsoc="F", xsob="Sob", pag=153))
    add(variavel("Reputacao", mfsoc="Soc", pag=26))
    add(fixo("Ressacas Terriveis", -1, mfsoc="F", pag=165))
    add(variavel("Riqueza", mfsoc="Soc", pag=25))
    add(fixo("Sadismo", -15, autocontrole=True, mfsoc="M", pag=154))
    add(opcoes(
        "Sangue Frio",
        "-5 ou -10",
        [{"custo": -5}, {"custo": -10}],
        mfsoc="F", pag=154,
    ))
    add(fixo("Sanguinolencia", -10, autocontrole=True, mfsoc="M", pag=154))
    add(faixa("Segredo", -5, -30, mfsoc="Soc", pag=155))
    add(fixo("Sem Imaginacao", -5, mfsoc="M", pag=155))
    add(fixo("Sem Manuseadores", -50, mfsoc="F", xsob="X", pag=149))
    add(fixo("Sem Nocao de Profundidade", -15, mfsoc="F", pag=155))
    add(variavel("Sem Pernas", mfsoc="F", xsob="X", pag=155))
    add(opcoes(
        "Sem Recuperacao",
        "-20 ou -30",
        [{"custo": -20}, {"custo": -30}],
        mfsoc="F", xsob="X", pag=156,
    ))
    add(opcoes(
        "Sem um Dedo",
        "-2 ou -5",
        [{"custo": -2}, {"custo": -5}],
        mfsoc="F", pag=156,
    ))
    add(fixo("Semiereto", -5, mfsoc="F", xsob="X", pag=156))
    add(faixa("Senso do Dever", -2, -20, mfsoc="M", pag=156))
    add(fixo("Simpatico", -1, mfsoc="M", pag=164))
    add(fixo("Solitario", -5, autocontrole=True, mfsoc="M", pag=157))
    add(fixo("Sonambulismo", -5, autocontrole=True, mfsoc="M", pag=157))
    add(fixo("Sonhador", -1, mfsoc="M", pag=164))
    add(por_nivel("Sono Complementar", -2, mfsoc="F", pag=157))
    add(fixo("Sono Leve", -5, mfsoc="F", pag=157))
    add(variavel("Sonolento", mfsoc="F", xsob="X", pag=157))
    add(por_nivel("Status", -5, mfsoc="Soc", pag=28))
    add(fixo("Supersensitivo", -15, mfsoc="M", xsob="Sob", pag=157))
    add(variavel("Suporte de Vida Ampliado", mfsoc="F", xsob="X", pag=157))
    add(fixo("Surdez", -20, mfsoc="F", pag=158))
    add(por_nivel("Susceptibilidade a Magia", -3, mfsoc="M", xsob="Sob", pag=158))
    add(variavel("Suscetivel", mfsoc="F", pag=158))
    add(fixo("Teimosia", -5, mfsoc="M", pag=158))
    add(por_nivel("Temor", -2, mfsoc="M", pag=158))
    add(fixo("Tetraplegico", -80, mfsoc="F", pag=158))
    add(opcoes(
        "Timidez",
        "-5, -10 ou -20",
        [{"custo": -5}, {"custo": -10}, {"custo": -20}],
        mfsoc="M", pag=159,
    ))
    add(fixo("Trapaceiro", -15, autocontrole=True, mfsoc="M", pag=159))
    add(fixo("Unico", -5, mfsoc="M", xsob="Sob", pag=159))
    add(fixo("Veracidade", -5, autocontrole=True, mfsoc="M", pag=159))
    add(fixo("Viciado em Trabalho", -5, mfsoc="M", pag=159))
    add(variavel("Vicio", mfsoc="M/F", pag=159))
    add(opcoes(
        "Visao Restrita",
        "-15 ou -30",
        [
            {"rotulo": "Um olho", "custo": -15},
            {"rotulo": "Tunel", "custo": -30},
        ],
        mfsoc="F", pag=160,
    ))
    add(opcoes(
        "Voto",
        "-1 ou -5 a -15",
        [
            {"rotulo": "Peculiaridade", "custo": -1},
            {"rotulo": "Menor", "custo": -5},
            {"rotulo": "Moderado", "custo": -10},
            {"rotulo": "Grande", "custo": -15},
        ],
        mfsoc="M", pag=160,
    ))
    add(fixo("Voz Irritante", -10, mfsoc="F", pag=161))
    add(faixa("Vozes Fantasmagoricas", -5, -15, mfsoc="M", pag=161))
    add(variavel("Vulnerabilidade", mfsoc="F", xsob="X", pag=161))
    add(fixo("Xenofilia", -10, autocontrole=True, mfsoc="M", pag=161))
    add(fixo("Zarolho", -15, mfsoc="F", pag=162))
    return d


def main() -> None:
    d = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    vantagens = montar_vantagens()
    desvantagens = montar_desvantagens()

    # Alfabetizar por nome (case-insensitive, sem acento)
    import unicodedata

    def sort_key(item: dict[str, Any]) -> str:
        s = item.get("nome") or ""
        s = unicodedata.normalize("NFD", s)
        return "".join(c for c in s if not unicodedata.combining(c)).lower()

    vantagens.sort(key=sort_key)
    desvantagens.sort(key=sort_key)

    d["vantagens"] = vantagens
    d["desvantagens"] = desvantagens
    meta = d.setdefault("meta", {})
    meta["nota"] = (
        "Catalogo enriquecido (2026-07-24) — tabelas rapidas do Modulo Basico "
        "Personagens pags. 298-301, com cost_model e opcoes discretas quando "
        "aplicavel. Autocontrole (*) preservado; texto original em custo_texto."
    )
    meta["cost_model_versao"] = 1
    meta["cost_model_valores"] = [
        "fixo",
        "por_nivel",
        "fixo_mais_por_nivel",
        "opcoes_discretas",
        "faixa",
        "variavel",
    ]

    JSON_PATH.write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Atualizado {JSON_PATH.name}: "
        f"{len(vantagens)} vantagens, {len(desvantagens)} desvantagens, "
        f"{len(d.get('pericias', []))} pericias"
    )


if __name__ == "__main__":
    main()
