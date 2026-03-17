"""
seed_magias.py
SRP: Popular a tabela de magias com dados do D&D 3.5 PHB
SOLID: Single Responsibility — apenas seed de magias
"""

import os
import sys

# ── Adicionar raiz ao path ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy.orm import Session
from app.models.magia import Magia


# ══════════════════════════════════════════════════════════════
# DADOS — D&D 3.5 PHB — TODAS AS CLASSES
# Formato: (nome, nivel, classe, escola, sub_escola, componentes,
#           alcance, area_efeito, duracao, tempo_conjuracao,
#           dano, teste_resistencia, resistencia_magica, descricao)
# ══════════════════════════════════════════════════════════════

MAGIAS_MAGO = [
    # ── Nível 0 ──
    ("Abrir/Fechar",        0, "Mago", "Transmutação",  "",           "V, S, M",  "Curto",    "",                         "Permanente",         "1 ação padrão", "",          "Vontade",  False, "Abre ou fecha portas, baús e similares."),
    ("Arrumar",             0, "Mago", "Transmutação",  "",           "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Limpa, organiza ou conserta um objeto pequeno."),
    ("Detectar Magia",      0, "Mago", "Adivinhação",   "",           "V, S",     "60 pés",   "Cone de 60 pés",           "Concentração, 1 min/nível", "1 ação padrão", "", "Nenhum", False, "Detecta feitiços e itens mágicos em 60 pés."),
    ("Detectar Veneno",     0, "Mago", "Adivinhação",   "",           "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Detecta a presença de veneno em criaturas ou objetos."),
    ("Flare",               0, "Mago", "Evocação",      "",           "V",        "Curto",    "",                         "Instantânea",        "1 ação padrão", "",          "Fortitude","Sim",  "Cria um flash ofuscante que penaliza o ataque do alvo."),
    ("Luz",                 0, "Mago", "Evocação",      "",           "V, M",     "Toque",    "",                         "10 min/nível",       "1 ação padrão", "",          "Nenhum",   False, "Objeto tocado emite luz como tocha por 10 min/nível."),
    ("Leitura Mágica",      0, "Mago", "Adivinhação",   "",           "V, S, F",  "Pessoal",  "",                         "10 min/nível",       "1 ação padrão", "",          "Nenhum",   False, "Permite ler escritas mágicas e pergaminhos."),
    ("Mão de Mago",         0, "Mago", "Transmutação",  "",           "V, S",     "Curto",    "",                         "Concentração",       "1 ação padrão", "",          "Nenhum",   False, "Mão mágica telecinética move até 5 lb."),
    ("Mensagem",            0, "Mago", "Transmutação",  "",           "V, S, F",  "Médio",    "",                         "10 min/nível",       "1 ação padrão", "",          "Nenhum",   False, "Sussurra mensagem a distância sem ser ouvido."),
    ("Prestidigitação",     0, "Mago", "Universal",     "",           "V, S",     "10 pés",   "",                         "1 hora",             "1 ação padrão", "",          "Nenhum",   False, "Realiza truques mágicos menores."),
    ("Raio de Gelo",        0, "Mago", "Evocação",      "Frio",       "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "1d3 frio", "Fortitude","Sim",  "Raio de frio que causa 1d3 de dano."),
    ("Resistência",         0, "Mago", "Abjuração",     "",           "V, S, M",  "Toque",    "",                         "1 minuto",           "1 ação padrão", "",          "Vontade",  False, "+1 em todos os testes de resistência por 1 minuto."),
    ("Som Imaginário",      0, "Mago", "Ilusão",        "Figurado",   "V, S, M",  "Longo",    "",                         "Concentração+1 rnd/nível", "1 ação padrão", "", "Vontade", False, "Cria ilusão sonora."),
    ("Toque Chocante",      0, "Mago", "Evocação",      "Elétrico",   "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "1d6 elétrico", "Nenhum", "Sim", "Descarga elétrica que causa 1d6 de dano elétrico."),

    # ── Nível 1 ──
    ("Armadura de Mago",    1, "Mago", "Conjuração",    "Criação",    "V, S, F",  "Toque",    "",                         "1 hora/nível",       "1 ação padrão", "",          "Vontade",  False, "Concede +4 de bônus de armadura à CA."),
    ("Charme de Pessoa",    1, "Mago", "Encantamento",  "Enfeitiçar", "V, S",     "Curto",    "",                         "1 hora/nível",       "1 ação padrão", "",          "Vontade",  Sim,   "Faz a criatura tratar o conjurador como amigo."),
    ("Compreender Idiomas", 1, "Mago", "Adivinhação",   "",           "V, S, M",  "Pessoal",  "",                         "10 min/nível",       "1 ação padrão", "",          "Nenhum",   False, "Compreende qualquer idioma falado ou escrito."),
    ("Dormir",              1, "Mago", "Encantamento",  "Compulsão",  "V, S, M",  "Médio",    "Burst de 10 pés",          "1 min/nível",        "1 rodada",      "",          "Vontade",  False, "Faz criaturas com até 4 DV adormecerem."),
    ("Escudo",              1, "Mago", "Abjuração",     "",           "V, S",     "Pessoal",  "",                         "1 min/nível",        "1 ação padrão", "",          "Nenhum",   False, "+4 de escudo à CA; bloqueia Projéteis Mágicos."),
    ("Identificar",         1, "Mago", "Adivinhação",   "",           "V, S, M",  "Toque",    "",                         "Instantânea",        "1 hora",        "",          "Nenhum",   False, "Identifica as propriedades mágicas de um item."),
    ("Imagem Silenciosa",   1, "Mago", "Ilusão",        "Figurado",   "V, S, F",  "Longo",    "4 quadrados/nível",        "Concentração",       "1 ação padrão", "",          "Vontade",  False, "Cria ilusão visual silenciosa."),
    ("Projétil Mágico",     1, "Mago", "Evocação",      "Força",      "V, S",     "Médio",    "",                         "Instantânea",        "1 ação padrão", "1d4+1/missil", "Nenhum", "Sim", "1 míssil de força (+1 a cada 2 níveis acima de 1°)."),
    ("Queda Suave",         1, "Mago", "Transmutação",  "",           "V",        "Curto",    "",                         "Até atingir o solo",  "Imediata",     "",          "Vontade",  False, "Faz a criatura cair lentamente como se flutuasse."),
    ("Salto",               1, "Mago", "Transmutação",  "",           "V, S, M",  "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Aumenta enormemente a capacidade de salto do alvo."),
    ("Toque Elétrico",      1, "Mago", "Evocação",      "Elétrico",   "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "1d6/nível (máx 5d6)", "Nenhum", "Sim", "Toque elétrico que causa 1d6 por nível (máx 5d6)."),

    # ── Nível 2 ──
    ("Detectar Pensamentos",2, "Mago", "Adivinhação",   "",           "V, S, F",  "60 pés",   "Cone de 60 pés",           "Concentração, máx 1 min/nível", "1 ação padrão", "", "Vontade", False, "Lê pensamentos superficiais de criaturas no alcance."),
    ("Flecha Ácida",        2, "Mago", "Conjuração",    "Criação",    "V, S, M, F","Longo",   "",                         "Instantânea + 1 rnd", "1 ação padrão", "2d4 ácido + 2d4/rnd", "Nenhum", "Sim", "Faz ácido grudar no alvo causando 2d4 por rodada."),
    ("Invisibilidade",      2, "Mago", "Ilusão",        "Glamour",    "V, S, M",  "Pessoal ou Toque", "",               "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Torna criatura ou objeto invisível."),
    ("Levitar",             2, "Mago", "Transmutação",  "",           "V, S, F",  "Curto",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Alvo sobe ou desce verticalmente a 20 pés/rodada."),
    ("Localizar Objeto",    2, "Mago", "Adivinhação",   "",           "V, S, F",  "Longo",    "",                         "1 min/nível",        "1 ação padrão", "",          "Nenhum",   False, "Sente direção de objeto familiar no alcance."),
    ("Nuvem de Névoa",      2, "Mago", "Conjuração",    "Criação",    "V, S",     "Médio",    "Cilindro de 20 pés raio",  "10 min/nível",       "1 rodada",      "",          "Nenhum",   False, "Cria névoa densa que bloqueia visão."),
    ("Resistência a Energia",2,"Mago","Abjuração",     "",           "V, S, M",  "Toque",    "",                         "10 min/nível",       "1 ação padrão", "",          "Fortitude", False,"Reduz dano de energia específica em 10/20/30 pts."),
    ("Toque de Idiotice",   2, "Mago", "Encantamento",  "Compulsão",  "V, S",     "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  Sim,   "Reduz INT e SAB do alvo em 1d6."),
    ("Web",                 2, "Mago", "Conjuração",    "Criação",    "V, S, M",  "Médio",    "20 pés raio, 10 pés altura", "10 min/nível",    "1 ação padrão", "",          "Reflexos", Sim,   "Cria teia pegajosa que prende criaturas na área."),

    # ── Nível 3 ──
    ("Bola de Fogo",        3, "Mago", "Evocação",      "Fogo",       "V, S, M",  "Longo",    "Burst de 20 pés de raio",  "Instantânea",        "1 ação padrão", "1d6/nível (máx 10d6)", "Reflexos", "Sim", "Bola de fogo que explode em área de 20 pés de raio."),
    ("Clarividência",       3, "Mago", "Adivinhação",   "",           "V, S, F",  "Longo",    "",                         "1 min/nível",        "10 minutos",    "",          "Nenhum",   False, "Vê ou ouve à distância por um local familiar."),
    ("Deslocamento",        3, "Mago", "Ilusão",        "Figurado",   "V, M",     "Toque",    "",                         "1 rnd/nível",        "1 ação padrão", "",          "Vontade",  False, "Alvo parece estar levemente deslocado; 50% de erro."),
    ("Dissipar Magia",      3, "Mago", "Abjuração",     "",           "V, S",     "Médio",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Cancela feitiços e efeitos mágicos."),
    ("Relâmpago",           3, "Mago", "Evocação",      "Elétrico",   "V, S, M",  "Médio",    "Raio de 120 pés",          "Instantânea",        "1 ação padrão", "1d6/nível (máx 10d6)", "Reflexos", "Sim", "Raio elétrico que percorre 120 pés em linha reta."),
    ("Sugestão",            3, "Mago", "Encantamento",  "Compulsão",  "V, M",     "Curto",    "",                         "1 hora/nível",       "1 ação padrão", "",          "Vontade",  Sim,   "Compele alvo a seguir sugestão razoável."),
    ("Voo",                 3, "Mago", "Transmutação",  "",           "V, S, F",  "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Alvo ganha velocidade de voo de 60 pés."),
    ("Haste",               3, "Mago", "Transmutação",  "",           "V, S, M",  "Curto",    "1 criatura/nível",         "1 rnd/nível",        "1 ação padrão", "",          "Fortitude", False,"Concede velocidade extra, +1 ataque e +1 CA."),

    # ── Nível 4 ──
    ("Arcano Olho",         4, "Mago", "Adivinhação",   "",           "V, S, M",  "Ilimitado","",                         "1 min/nível",        "10 minutos",    "",          "Nenhum",   False, "Cria olho invisível que pode voar e espionar."),
    ("Confusão",            4, "Mago", "Encantamento",  "Compulsão",  "V, S, M",  "Médio",    "Burst de 15 pés de raio",  "1 rnd/nível",        "1 ação padrão", "",          "Vontade",  Sim,   "Criaturas na área agem aleatoriamente."),
    ("Dimensão Porta",      4, "Mago", "Conjuração",    "Teletransporte","V",     "Longo",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Teletransporta o conjurador para local visível."),
    ("Polimorfar",          4, "Mago", "Transmutação",  "",           "V, S, M",  "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Fortitude", False,"Transforma criatura em outra forma animal."),
    ("Tempestade de Gelo",  4, "Mago", "Evocação",      "Frio/Impacto","V, S, M, F","Longo",  "Cilindro 20 pés raio",     "1 rodada",           "1 ação padrão", "3d6 impacto + 2d6 frio", "Nenhum", "Sim", "Granizo que causa 3d6+2d6 e dificulta movimento."),
    ("Muro de Fogo",        4, "Mago", "Evocação",      "Fogo",       "V, S, M",  "Médio",    "Muro de 20 pés/nível",     "Concentração + 1 rnd/nível", "1 ação padrão", "2d4 fogo (próx) ou 1d4 (distante)", "Reflexos", "Sim", "Cria muro de fogo que causa dano ao atravessar."),
    ("Muro de Gelo",        4, "Mago", "Evocação",      "Frio",       "V, S, M",  "Médio",    "Muro de 10 pés/nível",     "1 min/nível",        "1 ação padrão", "2d6 frio",  "Reflexos", Sim,   "Cria parede sólida de gelo."),

    # ── Nível 5 ──
    ("Cone de Frio",        5, "Mago", "Evocação",      "Frio",       "V, S, M",  "60 pés",   "Cone de 60 pés",           "Instantânea",        "1 ação padrão", "1d6/nível (máx 15d6)", "Reflexos", "Sim", "Cone de frio intenso que causa 1d6/nível."),
    ("Dominar Pessoa",      5, "Mago", "Encantamento",  "Compulsão",  "V, S",     "Curto",    "",                         "1 dia/nível",        "1 rodada",      "",          "Vontade",  Sim,   "Controla completamente ações de uma pessoa."),
    ("Nuvem Mortal",        5, "Mago", "Conjuração",    "Criação",    "V, S",     "Médio",    "Cilindro 30 pés raio",     "1 min/nível",        "1 rodada",      "1d4 Con",   "Fortitude", Sim,  "Nuvem de gás mortal que reduz Constituição."),
    ("Passagem de Parede",  5, "Mago", "Transmutação",  "",           "V, S, M",  "Toque",    "",                         "1 hora/nível",       "1 ação padrão", "",          "Nenhum",   False, "Permite atravessar paredes sólidas."),
    ("Teletransporte",      5, "Mago", "Conjuração",    "Teletransporte","V",     "Pessoal e Toque","",                   "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Teletransporta o conjurador e aliados."),

    # ── Nível 6 ──
    ("Cadeia de Relâmpagos",6, "Mago", "Evocação",      "Elétrico",   "V, S, F",  "Médio",    "1 alvo primário + secundários","Instantânea", "1 ação padrão", "1d6/nível (primário), metade (secundários)", "Reflexos", "Sim", "Raio que salta entre múltiplos alvos."),
    ("Desintegrar",         6, "Mago", "Transmutação",  "",           "V, S, M",  "Médio",    "",                         "Instantânea",        "1 ação padrão", "2d6/nível (máx 40d6)", "Fortitude", "Sim", "Raio que reduz alvo a pó se falhar na resistência."),
    ("Visão Verdadeira",    6, "Mago", "Adivinhação",   "",           "V, S, M",  "Toque",    "60 pés",                   "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Vê tudo em sua forma verdadeira dentro de 60 pés."),

    # ── Nível 7 ──
    ("Dedos de Morte",      7, "Mago", "Necromancia",   "",           "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "3d6 + 1/nível", "Fortitude", "Sim", "Mata criaturas com menos de 101 pontos de vida."),
    ("Inversão de Gravidade",7,"Mago", "Transmutação",  "",           "V, S",     "Médio",    "Cilindro 40 pés raio",     "1 rnd/nível",        "1 ação padrão", "",          "Reflexos", False, "Inverte a gravidade em uma área."),
    ("Teleporte em Grupo",  7, "Mago", "Conjuração",    "Teletransporte","V",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Teletransporta conjurador e aliados para local conhecido."),

    # ── Nível 8 ──
    ("Labirinto",           8, "Mago", "Conjuração",    "Teletransporte","V, S",  "Curto",    "",                         "Até escapar",        "1 ação padrão", "",          "Nenhum",   False, "Prende criatura em labirinto extradimensional."),
    ("Parar Tempo",         8, "Mago", "Transmutação",  "",           "V",        "Pessoal",  "",                         "1d4+1 rodadas",      "1 ação padrão", "",          "Nenhum",   False, "Para o tempo para todos exceto o conjurador."),

    # ── Nível 9 ──
    ("Desejo",              9, "Mago", "Universal",     "",           "V",        "Veja texto","",                        "Veja texto",         "1 ação padrão", "",          "Nenhum",   False, "Versão mais poderosa de Desejo Limitado."),
    ("Portal",              9, "Mago", "Conjuração",    "Criação",    "V, S",     "Médio",    "",                         "Concentração + 2 rnds/nível", "1 ação padrão", "", "Nenhum", False, "Cria portal para outro plano de existência."),
    ("Prisão Astral",       9, "Mago", "Abjuração",     "",           "V, S",     "Curto",    "",                         "Permanente",         "1 ação padrão", "",          "Vontade",  Sim,   "Aprisiona criatura no plano astral."),
]

MAGIAS_CLERIGO = [
    # ── Nível 0 ──
    ("Criar Água",          0, "Clérigo","Conjuração",  "Criação",    "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Cria 2 galões de água pura por nível."),
    ("Cura Menor",          0, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "1d8+1/nível","Vontade", False, "Cura 1d8 + 1/nível (máx +5) PV."),
    ("Detectar Magia",      0, "Clérigo","Adivinhação", "",           "V, S",     "60 pés",   "Cone de 60 pés",           "Concentração 1 min/nível","1 ação padrão","",       "Nenhum",   False, "Detecta feitiços e itens mágicos em 60 pés."),
    ("Detectar Veneno",     0, "Clérigo","Adivinhação", "",           "V, S",     "Curto",    "",                         "Instantânea",        "1 ação padrão", "",          "Nenhum",   False, "Detecta veneno em criaturas ou objetos."),
    ("Guia",                0, "Clérigo","Adivinhação", "",           "V, S",     "Toque",    "",                         "1 minuto",           "1 ação padrão", "",          "Vontade",  False, "+1 de competência em um teste de habilidade."),
    ("Luz",                 0, "Clérigo","Evocação",    "",           "V, M",     "Toque",    "",                         "10 min/nível",       "1 ação padrão", "",          "Nenhum",   False, "Objeto tocado emite luz por 10 min/nível."),
    ("Orientação",          0, "Clérigo","Adivinhação", "",           "V, S",     "Toque",    "",                         "1 minuto",           "1 ação padrão", "",          "Vontade",  False, "+1 em próximo ataque, save ou teste de habilidade."),
    ("Resistência",         0, "Clérigo","Abjuração",   "",           "V, S, M",  "Toque",    "",                         "1 minuto",           "1 ação padrão", "",          "Vontade",  False, "+1 em todos os testes de resistência por 1 minuto."),

    # ── Nível 1 ──
    ("Abençoar",            1, "Clérigo","Encantamento","Compulsão",  "V, S, DF", "50 pés",   "Burst de 50 pés",          "1 min/nível",        "1 ação padrão", "",          "Nenhum",   False, "+1 em ataques e salvaguardas contra medo para aliados."),
    ("Cura Leve",           1, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "1d8+1/nível","Vontade", False, "Cura 1d8 + 1/nível (máx +5) PV."),
    ("Detectar Mal",        1, "Clérigo","Adivinhação", "",           "V, S, DF", "60 pés",   "Cone de 60 pés",           "Concentração 10 min/nível","1 ação padrão","",      "Nenhum",   False, "Detecta presença, poder e localização do mal."),
    ("Escudo da Fé",        1, "Clérigo","Abjuração",   "",           "V, S, M",  "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "+2 de deflexão à CA (e +1 a cada 6 níveis)."),
    ("Proteção contra Mal", 1, "Clérigo","Abjuração",   "",           "V, S, DF", "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "+2 CA, +2 saves contra criaturas malignas."),

    # ── Nível 2 ──
    ("Ajuda",               2, "Clérigo","Encantamento","Compulsão",  "V, S, DF", "Toque",    "",                         "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "+1 em ataques e saves contra medo; 1d8+1/nível PVtemp."),
    ("Cura Moderada",       2, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "2d8+1/nível","Vontade", False, "Cura 2d8 + 1/nível (máx +10) PV."),
    ("Silêncio",            2, "Clérigo","Ilusão",      "Figurado",   "V, S",     "Longo",    "Esfera de 20 pés de raio", "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Nenhum som pode ser emitido ou ouvido na área."),
    ("Zona da Verdade",     2, "Clérigo","Encantamento","Compulsão",  "V, S",     "Curto",    "Burst de 20 pés de raio",  "1 min/nível",        "1 ação padrão", "",          "Vontade",  False, "Criaturas na área não podem mentir conscientemente."),

    # ── Nível 3 ──
    ("Cura Séria",          3, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "3d8+1/nível","Vontade", False, "Cura 3d8 + 1/nível (máx +15) PV."),
    ("Curar Doenças",       3, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "",          "Fortitude", False,"Cura todas as doenças que afligem o alvo."),
    ("Oração",              3, "Clérigo","Encantamento","Compulsão",  "V",        "40 pés",   "Burst de 40 pés",          "1 rnd/nível",        "1 ação padrão", "",          "Nenhum",   False, "+1 em ataques/dano/saves/testes aliados; -1 inimigos."),
    ("Remover Maldição",    3, "Clérigo","Abjuração",   "",           "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "",          "Vontade",  False, "Remove todas as maldições do alvo."),

    # ── Nível 4 ──
    ("Cura Crítica",        4, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "4d8+1/nível","Vontade", False, "Cura 4d8 + 1/nível (máx +20) PV."),
    ("Restauração",         4, "Clérigo","Conjuração",  "Cura",       "V, S, M",  "Toque",    "",                         "Instantânea",        "3 rodadas",     "",          "Vontade",  False, "Restaura níveis negativos e dano de habilidade."),

    # ── Nível 5 ──
    ("Curar",               5, "Clérigo","Conjuração",  "Cura",       "V, S",     "Toque",    "",                         "Instantânea",        "1 ação padrão", "10/nível (máx 150)", "Vontade", False, "Cura 10 PV por nível (máx 150) e remove condições."),
    ("Levantar Morto",      5, "Clérigo","Conjuração",  "Cura",       "V, S, M",  "Toque",    "",                         "Instantânea",        "1 minuto",      "",          "Nenhum",   False, "Retorna criatura morta há até 1 dia/nível à vida."),

    # ── Nível 6 ──
    ("Encontrar o Caminho", 6, "Clérigo","Adivinhação", "",           "V, S, F",  "Pessoal",  "",                         "10 min/nível",       "3 rodadas",     "",          "Nenhum",   False, "Indica o melhor caminho para um destino conhecido."),

    # ── Nível 7 ──
    ("Ressurreição",        7, "Clérigo","Conjuração",  "Cura",       "V, S, M",  "Toque",    "",                         "Instantânea",        "10 minutos",    "",          "Nenhum",   False, "Traz de volta criatura morta com todos os PV."),
    ("Palavra Sagrada",     7, "Clérigo","Evocação",    "",           "V",        "40 pés",   "Criaturas não-boas em 40 pés","Instantânea",     "1 ação padrão", "",          "Vontade",  Sim,   "Atordoa, cega, surda ou mata criaturas malignas."),

    # ── Nível 9 ──
    ("Milagre",             9, "Clérigo","Evocação",    "",           "V, S",     "Veja texto","",                        "Veja texto",         "1 ação padrão", "",          "Veja texto",False,"Solicita intervenção divina para qualquer efeito."),
]

MAGIAS_DRUIDA = [
    ("Criar Água",          0, "Druida","Conjuração",   "Criação",    "V, S",     "Curto",    "",              "Instantânea",     "1 ação padrão","",             "Nenhum",   False,"Cria 2 galões de água por nível."),
    ("Detectar Magia",      0, "Druida","Adivinhação",  "",           "V, S",     "60 pés",   "Cone 60 pés",   "Concentração 1 min/nível","1 ação padrão","",    "Nenhum",   False,"Detecta feitiços e itens mágicos."),
    ("Flare",               0, "Druida","Evocação",     "",           "V",        "Curto",    "",              "Instantânea",     "1 ação padrão","",             "Fortitude",Sim,  "Flash ofuscante; -1 ataque ao alvo."),
    ("Resistência",         0, "Druida","Abjuração",    "",           "V, S, DF", "Toque",    "",              "1 minuto",        "1 ação padrão","",             "Vontade",  False,"+1 em todos os testes de resistência."),
    ("Amizade com Animais", 1, "Druida","Encantamento", "Encantamento","V, S, M", "Curto",    "",              "1 hora/nível",    "1 ação padrão","",             "Vontade",  False,"Torna animal magicamente amigável."),
    ("Entalar",             1, "Druida","Transmutação", "",           "V, S, DF", "Longo",    "40 pés de raio","1 min/nível",     "1 ação padrão","",             "Reflexos", False,"Plantas crescem e imobilizam criaturas na área."),
    ("Forma Animal",        2, "Druida","Transmutação", "",           "V, S, DF", "Pessoal",  "",              "1 hora/nível",    "1 ação padrão","",             "Nenhum",   False,"Transforma o druida em animal de tamanho médio ou menor."),
    ("Chamado de Relâmpago",3, "Druida","Evocação",     "Elétrico",   "V, S, DF", "Médio",    "Cilindro 30 pés","Concentração 1 min/nível","1 rodada","3d6 elétrico","Reflexos",Sim,"Chama raios do céu repetidamente na área."),
    ("Neutralizar Veneno",  3, "Druida","Conjuração",   "Cura",       "V, S, M",  "Toque",    "",              "Instantânea",     "1 ação padrão","",             "Vontade",  False,"Neutraliza veneno e cura dano de veneno."),
    ("Controlar Água",      4, "Druida","Transmutação", "",           "V, S, DF", "Longo",    "300 pés cúbicos/nível","10 min/nível","1 ação padrão","",          "Nenhum",   False,"Baixa ou eleva nível de água em área."),
    ("Reencarnação",        4, "Druida","Transmutação", "",           "V, S, M, DF","Toque",  "",              "Instantânea",     "10 minutos",   "",             "Nenhum",   False,"Traz criatura morta de volta em novo corpo aleatório."),
    ("Comunhão com Natureza",5,"Druida","Adivinhação",  "",           "V, S",     "Pessoal",  "",              "Instantânea",     "10 minutos",   "",             "Nenhum",   False,"Obtém conhecimento da área natural ao redor."),
    ("Transporte via Plantas",6,"Druida","Conjuração","Teletransporte","V, S",    "Toque",    "",              "Instantânea",     "1 ação padrão","",             "Nenhum",   False,"Entra em uma planta e emerge de outra do mesmo tipo."),
    ("Terremoto",           8, "Druida","Evocação",     "",           "V, S, DF", "Longo",    "Burst 80 pés de raio","1 rnd",    "1 ação padrão","Veja texto",   "Reflexos", False,"Cria violento tremor de terra na área."),
]

MAGIAS_BARDO = [
    ("Detectar Magia",      0, "Bardo","Adivinhação",   "",           "V, S",     "60 pés",   "Cone 60 pés",   "Concentração 1 min/nível","1 ação padrão","",    "Nenhum",   False,"Detecta feitiços e itens mágicos."),
    ("Luz",                 0, "Bardo","Evocação",      "",           "V, M",     "Toque",    "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Objeto emite luz como tocha."),
    ("Mão de Mago",         0, "Bardo","Transmutação",  "",           "V, S",     "Curto",    "",              "Concentração",    "1 ação padrão","",             "Nenhum",   False,"Mão telecinética move até 5 lb."),
    ("Mensagem",            0, "Bardo","Transmutação",  "",           "V, S, F",  "Médio",    "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Sussurra mensagem a distância."),
    ("Prestidigitação",     0, "Bardo","Universal",     "",           "V, S",     "10 pés",   "",              "1 hora",          "1 ação padrão","",             "Nenhum",   False,"Realiza truques mágicos menores."),
    ("Charme de Pessoa",    1, "Bardo","Encantamento",  "Enfeitiçar", "V, S",     "Curto",    "",              "1 hora/nível",    "1 ação padrão","",             "Vontade",  Sim,  "Faz pessoa tratar conjurador como amigo."),
    ("Compreender Idiomas", 1, "Bardo","Adivinhação",   "",           "V, S, M",  "Pessoal",  "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Compreende qualquer idioma."),
    ("Cura Leve",           1, "Bardo","Conjuração",    "Cura",       "V, S",     "Toque",    "",              "Instantânea",     "1 ação padrão","1d8+1/nível",  "Vontade",  False,"Cura 1d8 + 1/nível PV."),
    ("Dormir",              1, "Bardo","Encantamento",  "Compulsão",  "V, S, M",  "Médio",    "Burst 10 pés",  "1 min/nível",     "1 rodada",     "",             "Vontade",  False,"Faz criaturas adormecerem."),
    ("Detectar Pensamentos",2, "Bardo","Adivinhação",   "",           "V, S, F",  "60 pés",   "Cone 60 pés",   "Concentração 1 min/nível","1 ação padrão","",    "Vontade",  False,"Lê pensamentos superficiais."),
    ("Invisibilidade",      2, "Bardo","Ilusão",        "Glamour",    "V, S, M",  "Pessoal/Toque","",          "1 min/nível",     "1 ação padrão","",             "Vontade",  False,"Torna criatura invisível."),
    ("Sugestão",            2, "Bardo","Encantamento",  "Compulsão",  "V, M",     "Curto",    "",              "1 hora/nível",    "1 ação padrão","",             "Vontade",  Sim,  "Compele alvo a seguir sugestão razoável."),
    ("Clarividência",       3, "Bardo","Adivinhação",   "",           "V, S, F",  "Longo",    "",              "1 min/nível",     "10 minutos",   "",             "Nenhum",   False,"Vê ou ouve em local distante."),
    ("Dissipar Magia",      3, "Bardo","Abjuração",     "",           "V, S",     "Médio",    "",              "Instantânea",     "1 ação padrão","",             "Nenhum",   False,"Cancela feitiços e efeitos mágicos."),
    ("Dominar Pessoa",      4, "Bardo","Encantamento",  "Compulsão",  "V, S",     "Curto",    "",              "1 dia/nível",     "1 rodada",     "",             "Vontade",  Sim,  "Controla ações de uma pessoa."),
    ("Localizar Criatura",  4, "Bardo","Adivinhação",   "",           "V, S, M",  "Longo",    "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Sente direção de criatura específica."),
    ("Geas",                6, "Bardo","Encantamento",  "Compulsão",  "V",        "Curto",    "",              "1 dia/nível",     "1 rodada",     "",             "Vontade",  False,"Obriga criatura a cumprir tarefa ou sofrer penalidade."),
]

MAGIAS_PALADINO = [
    ("Abençoar Arma",       1, "Paladino","Transmutação","",          "V, S, DF", "Toque",    "",              "1 min/nível",     "1 ação padrão","",             "Nenhum",   False,"Arma recebe bônus sagrado e causa dano extra a mortos-vivos."),
    ("Cura Leve",           1, "Paladino","Conjuração",  "Cura",      "V, S",     "Toque",    "",              "Instantânea",     "1 ação padrão","1d8+1/nível",  "Vontade",  False,"Cura 1d8 + 1/nível (máx +5) PV."),
    ("Detectar Mal",        1, "Paladino","Adivinhação", "",          "V, S, DF", "60 pés",   "Cone 60 pés",   "Concentração 10 min/nível","1 ação padrão","",    "Nenhum",   False,"Detecta presença e poder do mal."),
    ("Escudo da Fé",        1, "Paladino","Abjuração",   "",          "V, S, M",  "Toque",    "",              "1 min/nível",     "1 ação padrão","",             "Vontade",  False,"+2 de deflexão à CA."),
    ("Proteção contra Mal", 1, "Paladino","Abjuração",   "",          "V, S, DF", "Toque",    "",              "1 min/nível",     "1 ação padrão","",             "Vontade",  False,"+2 CA e +2 saves contra criaturas malignas."),
    ("Ajuda",               2, "Paladino","Encantamento","Compulsão", "V, S, DF", "Toque",    "",              "1 min/nível",     "1 ação padrão","",             "Vontade",  False,"+1 ataque/saves contra medo; PVtemp."),
    ("Remover Paralisia",   2, "Paladino","Conjuração",  "Cura",      "V, S",     "Curto",    "",              "Instantânea",     "1 ação padrão","",             "Vontade",  False,"Remove paralisia ou imobilidade de criaturas."),
    ("Resistência a Energia",2,"Paladino","Abjuração",   "",          "V, S, M",  "Toque",    "",              "10 min/nível",    "1 ação padrão","",             "Fortitude",False,"Reduz dano de tipo de energia específica."),
    ("Zona da Verdade",     2, "Paladino","Encantamento","Compulsão", "V, S",     "Curto",    "Burst 20 pés",  "1 min/nível",     "1 ação padrão","",             "Vontade",  False,"Criaturas não podem mentir na área."),
    ("Cura Séria",          3, "Paladino","Conjuração",  "Cura",      "V, S",     "Toque",    "",              "Instantânea",     "1 ação padrão","3d8+1/nível",  "Vontade",  False,"Cura 3d8 + 1/nível (máx +15) PV."),
    ("Curar Doenças",       3, "Paladino","Conjuração",  "Cura",      "V, S",     "Toque",    "",              "Instantânea",     "1 ação padrão","",             "Fortitude",False,"Cura todas as doenças do alvo."),
    ("Discernir Mentiras",  3, "Paladino","Adivinhação", "",          "V, S, DF", "Curto",    "",              "Concentração 1 min/nível","1 ação padrão","",     "Vontade",  False,"Detecta se alvo está mentindo conscientemente."),
    ("Oração",              3, "Paladino","Encantamento","Compulsão", "V",        "40 pés",   "Burst 40 pés",  "1 rnd/nível",     "1 ação padrão","",             "Nenhum",   False,"+1 aliados; -1 inimigos em ataques/dano/saves."),
    ("Cura Crítica",        4, "Paladino","Conjuração",  "Cura",      "V, S",     "Toque",    "",              "Instantânea",     "1 ação padrão","4d8+1/nível",  "Vontade",  False,"Cura 4d8 + 1/nível (máx +20) PV."),
    ("Espada Sagrada",      4, "Paladino","Evocação",    "",          "V, S",     "Toque",    "",              "1 rnd/nível",     "1 ação padrão","",             "Nenhum",   False,"Cria arma de força sagrada que luta sozinha."),
    ("Localizar Criatura",  4, "Paladino","Adivinhação", "",          "V, S, M",  "Longo",    "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Sente direção de criatura específica."),
    ("Quebrar Encantamento",4, "Paladino","Abjuração",   "",          "V, S",     "Curto",    "",              "Instantânea",     "1 ação padrão","",             "Vontade",  False,"Remove encantamentos, maldições e petrificação."),
]

MAGIAS_RANGER = [
    ("Alarme",              1, "Ranger","Abjuração",    "",           "V, S, F",  "Curto",    "20 pés de raio","8 horas",         "1 ação padrão","",             "Nenhum",   False,"Alerta quando criaturas passam pela área guardada."),
    ("Amizade com Animais", 1, "Ranger","Encantamento", "Encantamento","V, S, M", "Curto",    "",              "1 hora/nível",    "1 ação padrão","",             "Vontade",  False,"Torna animal magicamente amigável."),
    ("Entalar",             1, "Ranger","Transmutação", "",           "V, S, DF", "Longo",    "40 pés de raio","1 min/nível",     "1 ação padrão","",             "Reflexos", False,"Plantas crescem e imobilizam criaturas na área."),
    ("Falar com Animais",   1, "Ranger","Adivinhação",  "",           "V, S",     "Pessoal",  "",              "1 min/nível",     "1 ação padrão","",             "Nenhum",   False,"Comunica-se com animais de modo limitado."),
    ("Localizar Animais",   1, "Ranger","Adivinhação",  "",           "V, S, DF", "Longo",    "Cone 60 pés",   "Concentração 1 min/nível","1 ação padrão","",    "Nenhum",   False,"Sente a direção de animais ou plantas."),
    ("Detectar Armadilhas", 2, "Ranger","Adivinhação",  "",           "V, S",     "Pessoal",  "",              "Concentração 1 min/nível","1 ação padrão","",    "Nenhum",   False,"Detecta a presença de armadilhas no alcance."),
    ("Névoa Obscurecedora", 2, "Ranger","Conjuração",   "Criação",    "V, S",     "Médio",    "Nuvem 20 pés",  "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Névoa densa que cega e dificulta a visão."),
    ("Proteção contra Energia",2,"Ranger","Abjuração",  "",           "V, S, DF", "Toque",    "",              "10 min/nível",    "1 ação padrão","",             "Fortitude",False,"Protege contra até 12 pontos de dano de energia/rodada."),
    ("Curar Veneno",        3, "Ranger","Conjuração",   "Cura",       "V, S, M",  "Toque",    "",              "Instantânea",     "1 ação padrão","",             "Vontade",  False,"Neutraliza veneno e cura 1d4 de dano de habilidade."),
    ("Neutralizar Veneno",  3, "Ranger","Conjuração",   "Cura",       "V, S, M",  "Toque",    "",              "Instantânea",     "1 ação padrão","",             "Vontade",  False,"Neutraliza completamente o veneno e seus efeitos."),
    ("Reduzir Animal",      3, "Ranger","Transmutação", "",           "V, S",     "Toque",    "",              "1 hora/nível (D)","1 ação padrão","",             "Nenhum",   False,"Reduz tamanho de animal em uma categoria."),
    ("Forma Animal",        4, "Ranger","Transmutação", "",           "V, S, DF", "Pessoal",  "",              "1 hora/nível",    "1 ação padrão","",             "Nenhum",   False,"Transforma o ranger em animal de tamanho médio ou menor."),
    ("Liberdade de Movimento",4,"Ranger","Abjuração",   "",           "V, S, M, F","Toque",   "",              "10 min/nível",    "1 ação padrão","",             "Vontade",  False,"Alvo pode mover-se normalmente independente de magia."),
    ("Localizar Criatura",  4, "Ranger","Adivinhação",  "",           "V, S, M",  "Longo",    "",              "10 min/nível",    "1 ação padrão","",             "Nenhum",   False,"Sente direção de criatura específica."),
]


def seed_magias(db: Session, force: bool = False) -> dict:
    """
    Popula tabela de magias com dados do D&D 3.5 PHB.

    SRP: Única responsabilidade — inserir dados de magias.

    Args:
        db: Sessão SQLAlchemy
        force: Se True, limpa a tabela antes de inserir

    Returns:
        dict: Estatísticas da operação
    """
    stats = {
        'inseridas': 0,
        'ignoradas': 0,
        'erros': 0,
        'total': 0,
    }

    try:
        # ── Verificar se já tem dados ──
        total_existente = db.query(Magia).count()
        if total_existente > 0 and not force:
            print(f"✅ Tabela magias já populada com {total_existente} registros. Pulando seed.")
            stats['ignoradas'] = total_existente
            return stats

        # ── Limpar se force=True ──
        if force:
            db.query(Magia).delete()
            db.commit()
            print("🗑️  Tabela magias limpa para re-seed.")

        # ── Consolidar todas as magias ──
        todas_magias = (
            MAGIAS_MAGO +
            MAGIAS_CLERIGO +
            MAGIAS_DRUIDA +
            MAGIAS_BARDO +
            MAGIAS_PALADINO +
            MAGIAS_RANGER
        )

        # ── Inserir em lotes ──
        LOTE = 50
        for i in range(0, len(todas_magias), LOTE):
            lote = todas_magias[i:i + LOTE]
            for dados in lote:
                try:
                    magia = Magia(
                        nome              = dados[0],
                        nivel             = dados[1],
                        classe            = dados[2],
                        escola            = dados[3],
                        sub_escola        = dados[4],
                        componentes       = dados[5],
                        alcance           = dados[6],
                        area_efeito       = dados[7],
                        duracao           = dados[8],
                        tempo_conjuracao  = dados[9],
                        dano              = dados[10],
                        teste_resistencia = dados[11],
                        resistencia_magica= dados[12],
                        descricao         = dados[13],
                        ativo             = True,
                    )
                    db.add(magia)
                    stats['inseridas'] += 1
                except Exception as e:
                    stats['erros'] += 1
                    print(f"❌ Erro ao inserir magia '{dados[0]}': {e}")

            db.commit()
            print(f"✅ Lote {i // LOTE + 1}: {min(i + LOTE, len(todas_magias))}/{len(todas_magias)} magias inseridas.")

        stats['total'] = stats['inseridas']
        print(f"\n✅ Seed completo! {stats['inseridas']} magias inseridas com sucesso.")
        return stats

    except Exception as e:
        db.rollback()
        print(f"❌ Erro crítico no seed de magias: {e}")
        raise