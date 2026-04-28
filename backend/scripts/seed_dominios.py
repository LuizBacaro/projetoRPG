"""
seed_dominios.py

Propósito: Este script é responsável por popular a tabela de domínios no banco de dados
com dados do D&D 3.5 Player's Handbook. Ele segue o princípio de Responsabilidade Única (SRP),
focando exclusivamente na inserção e atualização dos registros de domínios.
"""

import os
import sys
import json
from typing import NoReturn

# Adiciona o diretório raiz do projeto ao PATH para permitir imports relativos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy.orm import Session

from app.shared.core.database import SessionLocal

# --- DADOS DOS DOMÍNIOS (Extraídos das abas 13-20 do magias.xlsx) ---

# Formato da tupla de magia:
# ('Nome da Magia', nível, 'DOMINIO', 'Tipo de Magia', '[modificadores]', 'Componentes', 'Alcance',
#  'Alvo/Efeito/Área', 'Duração', 'Teste Resistência', 'Resistência Mágica (Sim/Não)', booleano, 'Descrição')

# --- DOMÍNIO DO AR ---
DOMINIO_AR = (
    "Ar",
    "Poderes Concedidos: Mestre do Ar (Você pode usar 'Rajada de Vento' uma vez por dia).",
    [
        # Nível 1
        [
            ('Mensagem', 1, 'AR', 'Trans', '', 'V,G,M', 'Longo 120m+12m/niv', 'Criatura', '10 min/niv', 'Não', 'Não', False, 'Envia uma mensagem curta para uma criatura'),
            ('Névoa Obscurecente', 1, 'AR', 'Conj', '', 'V,G', 'Curto 7,5m+1,5m/2niv', 'Névoa 6m raio', '1 min/niv', 'Não', 'Não', False, 'Cria uma névoa que obscurece a visão'),
        ],
        # Nível 2
        [
            ('Lufada de Vento', 2, 'AR', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', 'Linha 18m', 'Inst', 'Fort neg', 'Não', False, 'Cria uma rajada de vento que derruba criaturas'),
            ('Muralha de Vento', 2, 'AR', 'Evoc', '', 'V,G', 'Médio 30m+3m/niv', 'Muralha 9m x 6m', '1 rod/niv', 'Não', 'Não', False, 'Cria uma muralha de vento que desvia projéteis'),
        ],
        # Nível 3
        [
            ('Caminhar no Ar', 3, 'AR', 'Trans', '', 'V,G,FD', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', False, 'Permite que a criatura ande no ar'),
            ('Relâmpago', 3, 'AR', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Linha 30m', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de eletricidade em linha'),
        ],
        # Nível 4
        [
            ('Controlar o Vento', 4, 'AR', 'Trans', '', 'V,G', 'Longo 120m+12m/niv', 'Área 12m raio', '10 min/niv', 'Não', 'Não', False, 'Altera a direção e velocidade do vento'),
            ('Tempestade de Gelo', 4, 'AR', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m alt, 6m raio', 'Inst', 'Não', 'Sim', False, 'Chuva de granizo que causa dano e dificulta terreno'),
        ],
        # Nível 5
        [
            ('Invocar Monstro V', 5, 'AR', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do ar médio'),
            ('Névoa Sólida', 5, 'AR', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Névoa 6m raio', '1 min/niv', 'Não', 'Não', True, 'Cria uma névoa densa que impede a visão e o movimento'),
        ],
        # Nível 6
        [
            ('Corrente de Relâmpagos', 6, 'AR', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Primário + 1/niv secundário', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de eletricidade em múltiplos alvos'),
            ('Controlar o Clima', 6, 'AR', 'Trans', '', 'V,G', '2 km', 'Área 2 km raio', '1 hora/niv', 'Não', 'Não', False, 'Altera o clima em uma grande área'),
        ],
        # Nível 7
        [
            ('Ciclone', 7, 'AR', 'Evoc', '', 'V,G', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', '1 rod/niv', 'Fort neg', 'Sim', False, 'Cria um ciclone que arremessa criaturas'),
            ('Invocar Monstro VII', 7, 'AR', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do ar grande'),
        ],
        # Nível 8
        [
            ('Tempestade de Vingança', 8, 'AR', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m raio, 12m alt', '1 rod/niv', 'Não', 'Sim', False, 'Cria uma tempestade devastadora'),
            ('Palavra de Poder, Atordoar', 8, 'AR', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Atordoa uma criatura com até 150 PV'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'AR', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do ar enorme'),
            ('Furacão', 9, 'AR', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m raio, 12m alt', '1 rod/niv', 'Fort neg', 'Sim', False, 'Cria um furacão que causa dano e arrasta criaturas'),
        ],
    ],
    "Domínio associado ao elemento ar, ventos, tempestades e a liberdade do céu. Seus seguidores buscam a agilidade e o poder dos céus."
)

# --- DOMÍNIO DO BEM ---
DOMINIO_BEM = (
    "Bem",
    "Poderes Concedidos: Toque Curativo (Você pode curar 1d6 PV uma vez por dia).",
    [
        # Nível 1
        [
            ('Abençoar Água', 1, 'BEM', 'Trans [bem]', '', 'V,G,M', 'Toque', 'Frasco água tocado', 'Inst', '1 min', '', 'Não', True, 'Cria água benta'),
            ('Bênção', 1, 'BEM', 'Encant', '', 'V,G,FD', '15 m', 'aliados expl. 15m', '1 min/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 para ataques e testes contra medo'),
            ('Curar Ferimentos Leves', 1, 'BEM', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 1d8+1/nível de dano (máximo +5)'),
            ('Proteção Contra o Mal', 1, 'BEM', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 min/niv(D)', '1 AP', '', 'Não', True, '+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares'),
        ],
        # Nível 2
        [
            ('Auxílio', 2, 'BEM', 'Encant', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede +1 de bônus de moral em ataques e testes de resistência'),
            ('Escudo da Fé', 2, 'BEM', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de deflexão na CA'),
            ('Proteger Outro', 2, 'BEM', 'Abjur', '', 'V,G,F', 'Curto 7,5m+1,5m/2niv', '1 criatura', '1 hora/niv', '1 AP', '', 'Não', True, 'Você sofre metade do dano dirigido ao alvo'),
        ],
        # Nível 3
        [
            ('Círculo Mágico Contra o Mal', 3, 'BEM', 'Abjur [bem]', '', 'V,G,M/FD', 'Toque', 'Eman 3m r', '10 min/niv', '1 AP', '', 'Não', False, 'Como as magias de Proteção, mas com 3 m de raio'),
            ('Oração', 3, 'BEM', 'Encant', '', 'V,G,FD', '12 m', 'Explosão 12m raio', '1 rod/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 em várias jogadas e os inimigos recebem -1'),
            ('Remover Maldição', 3, 'BEM', 'Abjur', '', 'V,G', 'Toque', 'Criatura/item Tocado', 'Inst', '1 AP', '', 'Não', True, 'Liberta objeto ou pessoa de maldição'),
        ],
        # Nível 4
        [
            ('Dissipar o Mal', 4, 'BEM', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Conj.+1 extrapl. Conj+1magia em obj/criat. Toc.', '1 rod/niv', '1 AP', '', 'Não', False, '+4 de bônus contra ataques de criaturas malignas'),
            ('Espada Sagrada', 4, 'BEM', 'Evoc [bem]', '', 'V, G', 'Toque', 'Arma branca toc.', '1 rod/niv', '1 AP', '', 'Não', False, 'Arma se torna +5, e causa +2d6 de dano contra seres malignos'),
            ('Proteção Contra a Morte', 4, 'BEM', 'Necr', '', 'V,G,FD', 'Toque', 'Criat. Viva tocada', '1 min/niv', '1 AP', '', 'Não', True, 'Fornece imunidade a magias e efeitos de morte'),
        ],
        # Nível 5
        [
            ('Coluna de Chamas', 5, 'BEM', 'Evoc [bem]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Invocar Monstro V', 5, 'BEM', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um celestial'),
            ('Símbolo da Esperança', 5, 'BEM', 'Encant [bem]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Inspira esperança e remove medo'),
        ],
        # Nível 6
        [
            ('Banimento', 6, 'BEM', 'Abjur', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', '1 ou mais extraplanares', 'Inst', 'Carisma neg', 'Sim', False, 'Bane criaturas extraplanares'),
            ('Cura Completa', 6, 'BEM', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 4d8 +1/nível de dano (máx. +20)'),
        ],
        # Nível 7
        [
            ('Palavra Sagrada', 7, 'BEM', 'Evoc [bem]', '', 'V', '12 m', 'Explosão 12m raio', 'Inst', 'Não', 'Sim', False, 'Causa dano e efeitos negativos em criaturas malignas'),
            ('Restauração Maior', 7, 'BEM', 'Conj [cura]', '', 'V,G,M', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Remove todas as penalidades de habilidade e níveis negativos'),
        ],
        # Nível 8
        [
            ('Aura Sagrada', 8, 'BEM', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
            ('Invocar Monstro VIII', 8, 'BEM', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um celestial maior'),
        ],
        # Nível 9
        [
            ('Cura em Massa', 9, 'BEM', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 1d8 +1/nível de dano em múltiplas criaturas'),
            ('Intervenção Divina', 9, 'BEM', 'Evoc [bem]', '', 'V,G,FD', 'Ilimitado', 'Você', 'Inst', 'Não', 'Não', False, 'Pede a intervenção direta de sua divindade'),
        ],
    ],
    "Domínio da bondade, compaixão e justiça. Seus seguidores buscam proteger os inocentes e combater o mal em todas as suas formas."
)

# --- DOMÍNIO DO CAOS ---
DOMINIO_CAOS = (
    "Caos",
    "Poderes Concedidos: Toque do Caos (Você pode causar 1d6 de dano extra uma vez por dia).",
    [
        # Nível 1
        [
            ('Proteção Contra a Ordem', 1, 'CAOS', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 min/niv(D)', '1 AP', '', 'Não', True, '+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares'),
            ('Mãos Flamejantes', 1, 'CAOS', 'Evoc [fogo]', '', 'V,G', '1,5 m', 'Cone', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo em cone'),
        ],
        # Nível 2
        [
            ('Arma Caótica', 2, 'CAOS', 'Trans [caos]', '', 'V,G,FD', 'Toque', 'Arma tocada', '1 min/niv', 'Não', 'Não', False, 'Arma causa dano extra contra criaturas ordeiras'),
            ('Névoa Mental', 2, 'CAOS', 'Encant', '', 'V,G', 'Curto 7,5m+1,5m/2niv', 'Névoa 6m raio', '1 min/niv', 'Vontade neg', 'Sim', False, 'Causa confusão e desorientação'),
        ],
        # Nível 3
        [
            ('Círculo Mágico Contra a Ordem', 3, 'CAOS', 'Abjur [caos]', '', 'V,G,M/FD', 'Toque', 'Eman 3m r', '10 min/niv', '1 AP', '', 'Não', False, 'Como as magias de Proteção, mas com 3 m de raio'),
            ('Invocar Monstro III', 3, 'CAOS', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura caótica'),
        ],
        # Nível 4
        [
            ('Dissipar a Ordem', 4, 'CAOS', 'Abjur [caos]', '', 'V,G,FD', 'Toque', 'Conj.+1 extrapl. Conj+1magia em obj/criat. Toc.', '1 rod/niv', '1 AP', '', 'Não', False, '+4 de bônus contra ataques de criaturas ordeiras'),
            ('Confusão', 4, 'CAOS', 'Encant', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 3m raio', '1 rod/niv', 'Vontade neg', 'Sim', False, 'Causa confusão em múltiplas criaturas'),
        ],
        # Nível 5
        [
            ('Caos', 5, 'CAOS', 'Encant [caos]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', '1 rod/niv', 'Vontade neg', 'Sim', False, 'Causa confusão em massa'),
            ('Invocar Monstro V', 5, 'CAOS', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura caótica maior'),
        ],
        # Nível 6
        [
            ('Palavra do Caos', 6, 'CAOS', 'Evoc [caos]', '', 'V', '12 m', 'Explosão 12m raio', 'Inst', 'Não', 'Sim', False, 'Causa dano e efeitos negativos em criaturas ordeiras'),
            ('Visão da Verdade', 6, 'CAOS', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Palavra de Poder, Cegar', 7, 'CAOS', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Cega uma criatura com até 200 PV'),
            ('Invocar Monstro VII', 7, 'CAOS', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura caótica ainda maior'),
        ],
        # Nível 8
        [
            ('Aura Caótica', 8, 'CAOS', 'Abjur [caos]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
            ('Símbolo da Loucura', 8, 'CAOS', 'Encant [caos]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa loucura em criaturas próximas'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'CAOS', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura caótica colossal'),
            ('Tempestade da Vingança', 9, 'CAOS', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m raio, 12m alt', '1 rod/niv', 'Não', 'Sim', False, 'Cria uma tempestade devastadora de energia caótica'),
        ],
    ],
    "Domínio da desordem, imprevisibilidade e liberdade. Seus seguidores abraçam a mudança e a destruição das estruturas existentes."
)

# --- DOMÍNIO DO CONHECIMENTO ---
DOMINIO_CONHECIMENTO = (
    "Conhecimento",
    "Poderes Concedidos: Conhecimento Adicional (Você pode usar 'Identificação' uma vez por dia).",
    [
        # Nível 1
        [
            ('Compreender Idiomas', 1, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '10 min/niv', 'Não', 'Não', True, 'Compreende qualquer idioma falado ou escrito'),
            ('Detectar Magia', 1, 'CONHECIMENTO', 'Adiv', '', 'V,G', '18 m', 'Emanação em cone', 'Conc 1min/niv(D)', 'Não', 'Não', False, 'Detecta a presença de magia'),
            ('Identificação', 1, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Toque', 'Item tocado', 'Inst', 'Não', 'Não', True, 'Identifica propriedades mágicas de um item'),
            ('Ler Magias', 1, 'CONHECIMENTO', 'Adiv', '', 'V,G,F', 'Pessoal', 'Você', '10 min/niv', '1 AP', '', 'Não', False, 'Decifra pergaminhos ou grimórios'),
        ],
        # Nível 2
        [
            ('Localizar Objeto', 2, 'CONHECIMENTO', 'Adiv', '', 'V,G,F', 'Longo 120m+12m/niv', 'Objeto', '1 min/niv', 'Não', 'Não', True, 'Localiza um objeto específico'),
            ('Visão da Verdade', 2, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 3
        [
            ('Discernir Mentiras', 3, 'CONHECIMENTO', 'Adiv', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', '1 criat/niv', 'Conc 1rod/niv', '1 AP', '', 'Não', False, 'Revela mentiras deliberadas'),
            ('Idiomas', 3, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '10 min/niv', 'Não', 'Não', True, 'Permite falar qualquer idioma'),
        ],
        # Nível 4
        [
            ('Adivinhação', 4, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Obtém conselhos de uma divindade ou poder superior'),
            ('Localizar Criatura', 4, 'CONHECIMENTO', 'Adiv', '', 'V,G,F', 'Longo 120m+12m/niv', 'Criatura', '1 min/niv', 'Não', 'Não', True, 'Localiza uma criatura específica'),
        ],
        # Nível 5
        [
            ('Comunhão', 5, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Faz perguntas a uma divindade e recebe respostas sim/não'),
            ('Visão da Verdade', 5, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 6
        [
            ('Analisar Encantamento', 6, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', 'Objeto/Criatura', 'Inst', 'Não', 'Não', True, 'Revela propriedades mágicas e maldições'),
            ('Visão da Verdade', 6, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Lendas e Histórias', 7, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '10 min/niv', 'Não', 'Não', True, 'Revela informações sobre uma pessoa, lugar ou objeto'),
            ('Visão', 7, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Obtém uma visão de eventos passados, presentes ou futuros'),
        ],
        # Nível 8
        [
            ('Discernir Localização', 8, 'CONHECIMENTO', 'Adiv', '', 'V,G', 'Ilimitado', 'Criatura/Objeto', 'Inst', 'Não', 'Não', False, 'Localiza uma criatura ou objeto em qualquer lugar'),
            ('Símbolo da Verdade', 8, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Revela a verdade e impede mentiras em uma área'),
        ],
        # Nível 9
        [
            ('Precognição', 9, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 hora/niv', 'Não', 'Não', True, 'Concede um bônus de sorte em todas as jogadas'),
            ('Visão Verdadeira', 9, 'CONHECIMENTO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Concede visão verdadeira, permitindo ver através de ilusões e escuridão'),
        ],
    ],
    "Domínio da sabedoria, erudição e compreensão. Seus seguidores buscam o conhecimento em todas as suas formas, desvendando mistérios e segredos."
)

# --- DOMÍNIO DA CURA ---
DOMINIO_CURA = (
    "Cura",
    "Poderes Concedidos: Curar Ferimentos (Você pode curar 1d8 PV uma vez por dia).",
    [
        # Nível 1
        [
            ('Curar Ferimentos Leves', 1, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 1d8+1/nível de dano (máximo +5)'),
            ('Restauração Menor', 1, 'CURA', 'Conj (cura)', '', 'V,G', 'Toque', 'Criatura Tocada', 'Inst', '3 rodadas', '', 'Não', True, 'Dissipa penalidades mágicas de habilidade ou recupera 1d4 de dano de habilidade'),
        ],
        # Nível 2
        [
            ('Curar Ferimentos Moderados', 2, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 2d8 +1/nível de dano (máx. +10)'),
            ('Remover Paralisia', 2, 'CURA', 'Conjur (cura)', '', 'V,G', 'Curto 7,5m+1,5m/2niv', 'até 4 criaturas', 'Inst', '1 AP', '', 'Não', True, 'Liberta uma ou mais criaturas de Paralisia ou Lentidão'),
            ('Retardar Envenenamento', 2, 'CURA', 'Conj (cura)', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 hora/niv', '1 AP', '', 'Não', True, 'Impede que veneno cause dano ao alvo durante 1 hora/nível'),
        ],
        # Nível 3
        [
            ('Curar Ferimentos Graves', 3, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura Tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 3d8 + 1/nível de dano (máx. +15)'),
            ('Remover Cegueira / Surdez', 3, 'CURA', 'Conj (cura)', '', 'V,G', 'Toque', 'Criatura Tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura condições normais ou mágicas'),
            ('Remover Doença', 3, 'CURA', 'Conj (cura)', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura todas as doenças do alvo'),
        ],
        # Nível 4
        [
            ('Curar Ferimentos Críticos', 4, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura Tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 4d8 + 1/nível de dano (máx. +20)'),
            ('Neutralizar Venenos', 4, 'CURA', 'Conj (cura)', '', 'V,G,M/FD', 'Toque', 'Criat. Ou obj toc. (30cm³/niv)', '10 min/niv', '1 AP', '', 'Não', True, 'Desentoxica veneno em um personagem'),
            ('Restauração', 4, 'CURA', 'Conj (cura)', '', 'V,G,M', 'Toque', 'Criatura Tocada', 'Inst', '3 rodadas', '', 'Não', True, 'Recupera níveis negativos e valores de habilidade'),
        ],
        # Nível 5
        [
            ('Cura Completa', 5, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Cura 4d8 +1/nível de dano (máx. +20)'),
            ('Aliviar Ferimentos Graves', 5, 'CURA', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 3d8 +1/nível de dano em múltiplas criaturas'),
        ],
        # Nível 6
        [
            ('Curar Ferimentos Leves em Massa', 6, 'CURA', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 1d8 +1/nível de dano em múltiplas criaturas'),
            ('Restauração Maior', 6, 'CURA', 'Conj [cura]', '', 'V,G,M', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Remove todas as penalidades de habilidade e níveis negativos'),
        ],
        # Nível 7
        [
            ('Curar Ferimentos Moderados em Massa', 7, 'CURA', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 2d8 +1/nível de dano em múltiplas criaturas'),
            ('Regeneração', 7, 'CURA', 'Conj [cura]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', '1 AP', '', 'Não', True, 'Regenera membros perdidos e cura dano massivo'),
        ],
        # Nível 8
        [
            ('Curar Ferimentos Graves em Massa', 8, 'CURA', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 3d8 +1/nível de dano em múltiplas criaturas'),
            ('Palavra de Poder, Curar', 8, 'CURA', 'Conj [cura]', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Cura uma criatura com até 200 PV'),
        ],
        # Nível 9
        [
            ('Curar Ferimentos Críticos em Massa', 9, 'CURA', 'Conj [cura]', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', '1 AP', '', 'Não', True, 'Cura 4d8 +1/nível de dano em múltiplas criaturas'),
            ('Milagre', 9, 'CURA', 'Evoc', '', 'V,G,FD', 'Ilimitado', 'Variável', 'Inst', 'Não', 'Não', False, 'Realiza um milagre divino'),
        ],
    ],
    "Domínio da saúde, recuperação e vitalidade. Seus seguidores são curandeiros e protetores, dedicados a aliviar o sofrimento e restaurar a vida."
)

# --- DOMÍNIO DA DESTRUIÇÃO ---
DOMINIO_DESTRUICAO = (
    "Destruição",
    "Poderes Concedidos: Toque Destrutivo (Você pode causar 1d6 de dano extra uma vez por dia).",
    [
        # Nível 1
        [
            ('Infligir Ferimentos Leves', 1, 'DESTRUICAO', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano (máximo +5)'),
            ('Mãos Flamejantes', 1, 'DESTRUICAO', 'Evoc [fogo]', '', 'V,G', '1,5 m', 'Cone', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo em cone'),
        ],
        # Nível 2
        [
            ('Infligir Ferimentos Moderados', 2, 'DESTRUICAO', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano (máximo +10)'),
            ('Raio Ardente', 2, 'DESTRUICAO', 'Evoc [fogo]', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 ou mais raios', 'Inst', 'Não', 'Sim', False, 'Causa dano de fogo em um ou mais alvos'),
        ],
        # Nível 3
        [
            ('Infligir Ferimentos Graves', 3, 'DESTRUICAO', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano (máximo +15)'),
            ('Relâmpago', 3, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Linha 30m', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de eletricidade em linha'),
        ],
        # Nível 4
        [
            ('Infligir Ferimentos Críticos', 4, 'DESTRUICAO', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano (máximo +20)'),
            ('Tempestade de Gelo', 4, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m alt, 6m raio', 'Inst', 'Não', 'Sim', False, 'Chuva de granizo que causa dano e dificulta terreno'),
        ],
        # Nível 5
        [
            ('Coluna de Chamas', 5, 'DESTRUICAO', 'Evoc [bem]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Infligir Ferimentos Leves em Massa', 5, 'DESTRUICAO', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano em múltiplas criaturas'),
        ],
        # Nível 6
        [
            ('Corrente de Relâmpagos', 6, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Primário + 1/niv secundário', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de eletricidade em múltiplos alvos'),
            ('Infligir Ferimentos Moderados em Massa', 6, 'DESTRUICAO', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano em múltiplas criaturas'),
        ],
        # Nível 7
        [
            ('Ciclone', 7, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', '1 rod/niv', 'Fort neg', 'Sim', False, 'Cria um ciclone que arremessa criaturas'),
            ('Infligir Ferimentos Graves em Massa', 7, 'DESTRUICAO', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano em múltiplas criaturas'),
        ],
        # Nível 8
        [
            ('Infligir Ferimentos Críticos em Massa', 8, 'DESTRUICAO', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano em múltiplas criaturas'),
            ('Tempestade de Vingança', 8, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m raio, 12m alt', '1 rod/niv', 'Não', 'Sim', False, 'Cria uma tempestade devastadora'),
        ],
        # Nível 9
        [
            ('Palavra de Poder, Matar', 9, 'DESTRUICAO', 'Necr', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Mata uma criatura com até 100 PV'),
            ('Implosão', 9, 'DESTRUICAO', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
        ],
    ],
    "Domínio da aniquilação, ruína e fim. Seus seguidores buscam o poder de destruir, seja para purificar ou para impor sua vontade."
)

# --- DOMÍNIO DA ENGANAÇÃO ---
DOMINIO_ENGANCAO = (
    "Enganação",
    "Poderes Concedidos: Toque Ilusório (Você pode criar uma ilusão menor uma vez por dia).",
    [
        # Nível 1
        [
            ('Disimular Tendência', 1, 'ENGANACAO', 'Abjur', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criat/obj', '24 h', '1 AP', '', 'Não', True, 'Esconde uma tendência durante 24h'),
            ('Imagem Silenciosa', 1, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Longo 120m+12m/niv', '1 objeto/criatura', 'Conc', 'Não', 'Não', True, 'Cria uma ilusão visual sem som'),
        ],
        # Nível 2
        [
            ('Invisibilidade', 2, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Toque', 'Criatura tocada', '1 min/niv(D)', 'Não', 'Não', True, 'Torna uma criatura invisível'),
            ('Sugestão', 2, 'ENGANACAO', 'Encant', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 criatura', '1 hora/niv', 'Vontade neg', 'Sim', True, 'Sugere uma ação a uma criatura'),
        ],
        # Nível 3
        [
            ('Imagem Maior', 3, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Longo 120m+12m/niv', '1 objeto/criatura', 'Conc', 'Não', 'Não', True, 'Cria uma ilusão visual e sonora'),
            ('Falar com os Mortos', 3, 'ENGANACAO', 'Necr', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 cadáver', '10 min/niv', 'Não', 'Não', True, 'Permite conversar com um cadáver'),
        ],
        # Nível 4
        [
            ('Confusão', 4, 'ENGANACAO', 'Encant', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 3m raio', '1 rod/niv', 'Vontade neg', 'Sim', False, 'Causa confusão em múltiplas criaturas'),
            ('Modificar Memória', 4, 'ENGANACAO', 'Encant', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Vontade neg', 'Sim', False, 'Modifica as memórias de uma criatura'),
        ],
        # Nível 5
        [
            ('Enganar', 5, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Pessoal', 'Você', '1 rod/niv', 'Não', 'Não', True, 'Cria uma ilusão de si mesmo para enganar os outros'),
            ('Sugestão em Massa', 5, 'ENGANACAO', 'Encant', '', 'V,G,M', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', '1 hora/niv', 'Vontade neg', 'Sim', True, 'Sugere uma ação a múltiplas criaturas'),
        ],
        # Nível 6
        [
            ('Véu', 6, 'ENGANACAO', 'Ilusão', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', '1 hora/niv', 'Não', 'Não', False, 'Muda a aparência de um grupo de criaturas'),
            ('Visão da Verdade', 6, 'ENGANACAO', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Simulacro', 7, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Toque', 'Criatura', 'Perm', 'Não', 'Não', True, 'Cria uma cópia ilusória de uma criatura'),
            ('Palavra de Poder, Cegar', 7, 'ENGANACAO', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Cega uma criatura com até 200 PV'),
        ],
        # Nível 8
        [
            ('Mente em Branco', 8, 'ENGANACAO', 'Abjur', '', 'V,G', 'Toque', 'Criatura tocada', '24 horas', 'Não', 'Não', False, 'Protege a mente de magias de adivinhação e controle mental'),
            ('Símbolo da Loucura', 8, 'ENGANACAO', 'Encant [caos]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa loucura em criaturas próximas'),
        ],
        # Nível 9
        [
            ('Metamorfose Verdadeira', 9, 'ENGANACAO', 'Trans', '', 'V,G,M', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', True, 'Muda a forma de uma criatura para qualquer outra'),
            ('Ilusão Programada', 9, 'ENGANACAO', 'Ilusão', '', 'V,G,M', 'Longo 120m+12m/niv', '1 objeto/criatura', 'Perm', 'Não', 'Não', True, 'Cria uma ilusão complexa que se ativa sob condições específicas'),
        ],
    ],
    "Domínio da astúcia, disfarce e manipulação. Seus seguidores usam a ilusão e o engano para atingir seus objetivos, confundindo inimigos e protegendo aliados."
)

# --- DOMÍNIO DO FOGO ---
DOMINIO_FOGO = (
    "Fogo",
    "Poderes Concedidos: Mestre do Fogo (Você pode usar 'Mãos Flamejantes' uma vez por dia).",
    [
        # Nível 1
        [
            ('Mãos Flamejantes', 1, 'FOGO', 'Evoc [fogo]', '', 'V,G', '1,5 m', 'Cone', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo em cone'),
            ('Toque Chocante', 1, 'FOGO', 'Evoc [eletricidade]', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Não', 'Sim', False, 'Causa dano de eletricidade com um toque'),
        ],
        # Nível 2
        [
            ('Raio Ardente', 2, 'FOGO', 'Evoc [fogo]', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 ou mais raios', 'Inst', 'Não', 'Sim', False, 'Causa dano de fogo em um ou mais alvos'),
            ('Resistência a Elementos', 2, 'FOGO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '10 min/niv', '1 AP', '', 'Não', True, 'Ignora 10 pontos dano/ataque de um tipo de energia'),
        ],
        # Nível 3
        [
            ('Bola de Fogo', 3, 'FOGO', 'Evoc [fogo]', '', 'V,G,M', 'Longo 120m+12m/niv', 'Explosão 6m raio', 'Inst', 'Ref metade', 'Sim', True, 'Causa dano de fogo em área'),
            ('Muralha de Fogo', 3, 'FOGO', 'Evoc [fogo]', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', '1 rod/niv', 'Não', 'Sim', True, 'Cria uma muralha de fogo que causa dano'),
        ],
        # Nível 4
        [
            ('Escudo de Fogo', 4, 'FOGO', 'Evoc [fogo]', '', 'V,G,M', 'Pessoal', 'Você', '1 rod/niv', 'Não', 'Não', True, 'Cria um escudo de fogo que causa dano a quem te ataca'),
            ('Tempestade de Fogo', 4, 'FOGO', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m alt, 6m raio', 'Inst', 'Ref metade', 'Sim', False, 'Chuva de fogo que causa dano'),
        ],
        # Nível 5
        [
            ('Coluna de Chamas', 5, 'FOGO', 'Evoc [bem]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Invocar Monstro V', 5, 'FOGO', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do fogo médio'),
        ],
        # Nível 6
        [
            ('Muralha de Fogo', 6, 'FOGO', 'Evoc [fogo]', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', '1 rod/niv', 'Não', 'Sim', True, 'Cria uma muralha de fogo que causa dano'),
            ('Símbolo do Fogo', 6, 'FOGO', 'Evoc [fogo]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa dano de fogo em criaturas próximas'),
        ],
        # Nível 7
        [
            ('Explosão Solar', 7, 'FOGO', 'Evoc [fogo, luz]', '', 'V,G', 'Longo 120m+12m/niv', 'Explosão 12m raio', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo e cega criaturas'),
            ('Invocar Monstro VII', 7, 'FOGO', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do fogo grande'),
        ],
        # Nível 8
        [
            ('Incêndio', 8, 'FOGO', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', 'Explosão 12m raio', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano massivo de fogo em área'),
            ('Palavra de Poder, Atordoar', 8, 'FOGO', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Atordoa uma criatura com até 150 PV'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'FOGO', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental do fogo enorme'),
            ('Tempestade de Meteoros', 9, 'FOGO', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', '4 meteoros', 'Inst', 'Ref metade', 'Sim', False, 'Chuva de meteoros que causa dano massivo'),
        ],
    ],
    "Domínio do calor, chamas e destruição. Seus seguidores controlam o fogo em todas as suas manifestações, usando-o para purificar ou aniquilar."
)

# --- DOMÍNIO DA FORÇA ---
DOMINIO_FORCA = (
    "Força",
    "Poderes Concedidos: Força Divina (Você pode ganhar +1 de bônus de aprimoramento na Força uma vez por dia).",
    [
        # Nível 1
        [
            ('Arma Mágica', 1, 'FORCA', 'Trans', '', 'V,G,FD', 'Toque', 'Arma tocada', '1 min/niv', '1 AP', '', 'Não', True, 'Uma arma recebe +1 de bônus'),
            ('Auxílio Divino', 1, 'FORCA', 'Evoc', '', 'V,G,FD', 'Pessoal', 'Você', '1 min', '1 AP', '', 'Não', False, 'Você recebe +1 de bônus/3 níveis para ataques e dano'),
        ],
        # Nível 2
        [
            ('Força do Touro', 2, 'FORCA', 'Trans', '', 'V,G,M/FD', 'Toque', 'criatura tocada', '1 min/niv', '1 AP', '', 'Não', True, 'Alvo recebe +4 For durante 1 min/nível'),
            ('Escudo da Fé', 2, 'FORCA', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de deflexão na CA'),
        ],
        # Nível 3
        [
            ('Arma Mágica Maior', 3, 'FORCA', 'Trans', '', 'V,G,M/FD', 'Curto 7,5m+1,5m/2niv', '1 arma/50proj', '1h/niv', '1 AP', '', 'Não', True, '+1 de bônus/4 níveis (máx. +5)'),
            ('Oração', 3, 'FORCA', 'Encant', '', 'V,G,FD', '12 m', 'Explosão 12m raio', '1 rod/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 em várias jogadas e os inimigos recebem -1'),
        ],
        # Nível 4
        [
            ('Escudo da Ordem', 4, 'FORCA', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus na CA e testes de resistência'),
            ('Pele Rochosa', 4, 'FORCA', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
        ],
        # Nível 5
        [
            ('Força de Touro em Massa', 5, 'FORCA', 'Trans', '', 'V,G,M/FD', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', '1 min/niv', 'Não', 'Não', True, 'Múltiplos alvos recebem +4 For'),
            ('Muralha de Força', 5, 'FORCA', 'Evoc', '', 'V,G', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', '1 rod/niv', 'Não', 'Não', False, 'Cria uma muralha de força invisível e impenetrável'),
        ],
        # Nível 6
        [
            ('Punho Cerrado de Bigby', 6, 'FORCA', 'Evoc', '', 'V,G,M', 'Médio 30m+3m/niv', 'Mão de força', '1 rod/niv', 'Não', 'Não', True, 'Cria uma mão de força que ataca ou agarra'),
            ('Resistência à Magia', 6, 'FORCA', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede resistência à magia'),
        ],
        # Nível 7
        [
            ('Mão Interceptadora de Bigby', 7, 'FORCA', 'Evoc', '', 'V,G,M', 'Médio 30m+3m/niv', 'Mão de força', '1 rod/niv', 'Não', 'Não', True, 'Cria uma mão de força que intercepta ataques'),
            ('Palavra de Poder, Cegar', 7, 'FORCA', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Cega uma criatura com até 200 PV'),
        ],
        # Nível 8
        [
            ('Mão Esmagadora de Bigby', 8, 'FORCA', 'Evoc', '', 'V,G,M', 'Médio 30m+3m/niv', 'Mão de força', '1 rod/niv', 'Não', 'Não', True, 'Cria uma mão de força que esmaga inimigos'),
            ('Aura Sagrada', 8, 'FORCA', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
        ],
        # Nível 9
        [
            ('Mão Agarradora de Bigby', 9, 'FORCA', 'Evoc', '', 'V,G,M', 'Médio 30m+3m/niv', 'Mão de força', '1 rod/niv', 'Não', 'Não', True, 'Cria uma mão de força que agarra e esmaga inimigos'),
            ('Implosão', 9, 'FORCA', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
        ],
    ],
    "Domínio da força bruta, resistência e poder físico. Seus seguidores são guerreiros e protetores, usando a força para superar obstáculos e derrotar inimigos."
)

# --- DOMÍNIO DA GUERRA ---
DOMINIO_GUERRA = (
    "Guerra",
    "Poderes Concedidos: Fúria Divina (Você pode ganhar +1 de bônus de moral em ataques uma vez por dia).",
    [
        # Nível 1
        [
            ('Abençoar Arma', 1, 'GUERRA', 'Trans', '', 'V,G', 'Toque', 'Arma tocada', '1 min/niv', '1 A.P.', '', 'Não', False, 'Uma arma ataca com precisão contra inimigos malignos'),
            ('Bênção', 1, 'GUERRA', 'Encant', '', 'V,G,FD', '15 m', 'aliados expl. 15m', '1 min/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 para ataques e testes contra medo'),
        ],
        # Nível 2
        [
            ('Arma Espiritual', 2, 'GUERRA', 'Evoc [força]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Arma de força', '1 rod/niv', 'Não', 'Não', False, 'Cria uma arma de força que ataca inimigos'),
            ('Auxílio', 2, 'GUERRA', 'Encant', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede +1 de bônus de moral em ataques e testes de resistência'),
        ],
        # Nível 3
        [
            ('Arma Mágica Maior', 3, 'GUERRA', 'Trans', '', 'V,G,M/FD', 'Curto 7,5m+1,5m/2niv', '1 arma/50proj', '1h/niv', '1 AP', '', 'Não', True, '+1 de bônus/4 níveis (máx. +5)'),
            ('Oração', 3, 'GUERRA', 'Encant', '', 'V,G,FD', '12 m', 'Explosão 12m raio', '1 rod/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 em várias jogadas e os inimigos recebem -1'),
        ],
        # Nível 4
        [
            ('Espada Sagrada', 4, 'GUERRA', 'Evoc [bem]', '', 'V, G', 'Toque', 'Arma branca toc.', '1 rod/niv', '1 AP', '', 'Não', False, 'Arma se torna +5, e causa +2d6 de dano contra seres malignos'),
            ('Pele Rochosa', 4, 'GUERRA', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
        ],
        # Nível 5
        [
            ('Coluna de Chamas', 5, 'GUERRA', 'Evoc [bem]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Invocar Monstro V', 5, 'GUERRA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um celestial ou demônio'),
        ],
        # Nível 6
        [
            ('Heroísmo Maior', 6, 'GUERRA', 'Encant', '', 'V,G', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de moral em ataques, testes de resistência e CA'),
            ('Visão da Verdade', 6, 'GUERRA', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Espada de Força', 7, 'GUERRA', 'Evoc [força]', '', 'V,G', 'Pessoal', 'Você', '1 rod/niv', 'Não', 'Não', False, 'Cria uma espada de força que causa dano massivo'),
            ('Palavra Sagrada', 7, 'GUERRA', 'Evoc [bem]', '', 'V', '12 m', 'Explosão 12m raio', 'Inst', 'Não', 'Sim', False, 'Causa dano e efeitos negativos em criaturas malignas'),
        ],
        # Nível 8
        [
            ('Aura Sagrada', 8, 'GUERRA', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
            ('Símbolo da Morte', 8, 'GUERRA', 'Necr', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa morte em criaturas próximas'),
        ],
        # Nível 9
        [
            ('Implosão', 9, 'GUERRA', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
            ('Tempestade de Meteoros', 9, 'GUERRA', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', '4 meteoros', 'Inst', 'Ref metade', 'Sim', False, 'Chuva de meteoros que causa dano massivo'),
        ],
    ],
    "Domínio do conflito, estratégia e combate. Seus seguidores são líderes e guerreiros, buscando a vitória em batalha e a glória em nome de sua divindade."
)

# --- DOMÍNIO DA MAGIA ---
DOMINIO_MAGIA = (
    "Magia",
    "Poderes Concedidos: Conhecimento Mágico (Você pode usar 'Identificação' uma vez por dia).",
    [
        # Nível 1
        [
            ('Detectar Magia', 1, 'MAGIA', 'Adiv', '', 'V,G', '18 m', 'Emanação em cone', 'Conc 1min/niv(D)', 'Não', 'Não', False, 'Detecta a presença de magia'),
            ('Identificação', 1, 'MAGIA', 'Adiv', '', 'V,G,M', 'Toque', 'Item tocado', 'Inst', 'Não', 'Não', True, 'Identifica propriedades mágicas de um item'),
            ('Ler Magias', 1, 'MAGIA', 'Adiv', '', 'V,G,F', 'Pessoal', 'Você', '10 min/niv', '1 AP', '', 'Não', False, 'Decifra pergaminhos ou grimórios'),
        ],
        # Nível 2
        [
            ('Dissipar Magia', 2, 'MAGIA', 'Abjur', '', 'V,G', 'Médio 30m+3m/niv', '1 conj/1criat/1obj/expl. 6m raio', 'Inst', '1 AP', '', 'Não', False, 'Cancela magias e efeitos mágicos'),
            ('Resistência à Magia', 2, 'MAGIA', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede resistência à magia'),
        ],
        # Nível 3
        [
            ('Contramágica', 3, 'MAGIA', 'Abjur', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 magia', 'Inst', 'Não', 'Não', False, 'Anula uma magia sendo conjurada'),
            ('Dissipar Magia Maior', 3, 'MAGIA', 'Abjur', '', 'V,G', 'Médio 30m+3m/niv', '1 conj/1criat/1obj/expl. 6m raio', 'Inst', '1 AP', '', 'Não', False, 'Cancela magias e efeitos mágicos com maior poder'),
        ],
        # Nível 4
        [
            ('Campo Antimagia', 4, 'MAGIA', 'Abjur', '', 'V,G,M', '1,5 m', 'Emanação 3m raio', '10 min/niv', 'Não', 'Não', True, 'Cria uma área onde a magia não funciona'),
            ('Pele Rochosa', 4, 'MAGIA', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
        ],
        # Nível 5
        [
            ('Disjunção de Mordenkainen', 5, 'MAGIA', 'Abjur', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 obj/criat/área', 'Inst', 'Não', 'Sim', False, 'Destrói itens mágicos e efeitos mágicos'),
            ('Invocar Monstro V', 5, 'MAGIA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental ou criatura mágica'),
        ],
        # Nível 6
        [
            ('Analisar Encantamento', 6, 'MAGIA', 'Adiv', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', 'Objeto/Criatura', 'Inst', 'Não', 'Não', True, 'Revela propriedades mágicas e maldições'),
            ('Visão da Verdade', 6, 'MAGIA', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Palavra de Poder, Cegar', 7, 'MAGIA', 'Encant', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Cega uma criatura com até 200 PV'),
            ('Invocar Monstro VII', 7, 'MAGIA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental ou criatura mágica maior'),
        ],
        # Nível 8
        [
            ('Mente em Branco', 8, 'MAGIA', 'Abjur', '', 'V,G', 'Toque', 'Criatura tocada', '24 horas', 'Não', 'Não', False, 'Protege a mente de magias de adivinhação e controle mental'),
            ('Símbolo da Loucura', 8, 'MAGIA', 'Encant [caos]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa loucura em criaturas próximas'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'MAGIA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental ou criatura mágica colossal'),
            ('Desejo', 9, 'MAGIA', 'Conj', '', 'V', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', False, 'Realiza um desejo'),
        ],
    ],
    "Domínio da essência da magia, seus mistérios e seu controle. Seus seguidores buscam compreender e manipular as forças arcanas e divinas."
)

# --- DOMÍNIO DO MAL ---
DOMINIO_MAL = (
    "Mal",
    "Poderes Concedidos: Toque Maligno (Você pode causar 1d6 de dano extra uma vez por dia).",
    [
        # Nível 1
        [
            ('Infligir Ferimentos Leves', 1, 'MAL', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano (máximo +5)'),
            ('Proteção Contra o Bem', 1, 'MAL', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 min/niv(D)', '1 AP', '', 'Não', True, '+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares'),
        ],
        # Nível 2
        [
            ('Infligir Ferimentos Moderados', 2, 'MAL', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano (máximo +10)'),
            ('Arma Maligna', 2, 'MAL', 'Trans [mal]', '', 'V,G,FD', 'Toque', 'Arma tocada', '1 min/niv', 'Não', 'Não', False, 'Arma causa dano extra contra criaturas boas'),
        ],
        # Nível 3
        [
            ('Círculo Mágico Contra o Bem', 3, 'MAL', 'Abjur [mal]', '', 'V,G,M/FD', 'Toque', 'Eman 3m r', '10 min/niv', '1 AP', '', 'Não', False, 'Como as magias de Proteção, mas com 3 m de raio'),
            ('Infligir Ferimentos Graves', 3, 'MAL', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano (máximo +15)'),
        ],
        # Nível 4
        [
            ('Dissipar o Bem', 4, 'MAL', 'Abjur [mal]', '', 'V,G,FD', 'Toque', 'Conj.+1 extrapl. Conj+1magia em obj/criat. Toc.', '1 rod/niv', '1 AP', '', 'Não', False, '+4 de bônus contra ataques de criaturas boas'),
            ('Infligir Ferimentos Críticos', 4, 'MAL', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano (máximo +20)'),
        ],
        # Nível 5
        [
            ('Infligir Ferimentos Leves em Massa', 5, 'MAL', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano em múltiplas criaturas'),
            ('Invocar Monstro V', 5, 'MAL', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura maligna'),
        ],
        # Nível 6
        [
            ('Infligir Ferimentos Moderados em Massa', 6, 'MAL', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano em múltiplas criaturas'),
            ('Palavra Profana', 6, 'MAL', 'Evoc [mal]', '', 'V', '12 m', 'Explosão 12m raio', 'Inst', 'Não', 'Sim', False, 'Causa dano e efeitos negativos em criaturas boas'),
        ],
        # Nível 7
        [
            ('Infligir Ferimentos Graves em Massa', 7, 'MAL', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano em múltiplas criaturas'),
            ('Invocar Monstro VII', 7, 'MAL', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura maligna maior'),
        ],
        # Nível 8
        [
            ('Infligir Ferimentos Críticos em Massa', 8, 'MAL', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano em múltiplas criaturas'),
            ('Aura Profana', 8, 'MAL', 'Abjur [mal]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'MAL', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um demônio ou criatura maligna colossal'),
            ('Implosão', 9, 'MAL', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
        ],
    ],
    "Domínio da escuridão, corrupção e destruição. Seus seguidores buscam o poder para dominar e subjugar, espalhando o mal e a tirania."
)

# --- DOMÍNIO DA MORTE ---
DOMINIO_MORTE = (
    "Morte",
    "Poderes Concedidos: Toque da Morte (Você pode causar 1d6 de dano extra uma vez por dia).",
    [
        # Nível 1
        [
            ('Causar Medo', 1, 'MORTE', 'Necr', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 criatura', '1 min/niv', 'Vontade neg', 'Sim', True, 'Causa medo em uma criatura'),
            ('Infligir Ferimentos Leves', 1, 'MORTE', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano (máximo +5)'),
        ],
        # Nível 2
        [
            ('Infligir Ferimentos Moderados', 2, 'MORTE', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano (máximo +10)'),
            ('Profanar', 2, 'MORTE', 'Necr [mal]', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Emanação 6m raio', '10 min/niv', 'Não', 'Não', False, 'Cria uma área de energia negativa'),
        ],
        # Nível 3
        [
            ('Animar Mortos', 3, 'MORTE', 'Necr', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 ou mais cadáveres', 'Inst', 'Não', 'Não', True, 'Anima mortos-vivos'),
            ('Infligir Ferimentos Graves', 3, 'MORTE', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano (máximo +15)'),
        ],
        # Nível 4
        [
            ('Infligir Ferimentos Críticos', 4, 'MORTE', 'Necr', '', 'V,G', 'Toque', 'Criatura tocada', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano (máximo +20)'),
            ('Proteção Contra a Morte', 4, 'MORTE', 'Necr', '', 'V,G,FD', 'Toque', 'Criat. Viva tocada', '1 min/niv', '1 AP', '', 'Não', True, 'Fornece imunidade a magias e efeitos de morte'),
        ],
        # Nível 5
        [
            ('Infligir Ferimentos Leves em Massa', 5, 'MORTE', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 1d8+1/nível de dano em múltiplas criaturas'),
            ('Matar os Vivos', 5, 'MORTE', 'Necr', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Fort neg', 'Sim', False, 'Mata uma criatura viva'),
        ],
        # Nível 6
        [
            ('Infligir Ferimentos Moderados em Massa', 6, 'MORTE', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 2d8+1/nível de dano em múltiplas criaturas'),
            ('Criar Mortos-Vivos', 6, 'MORTE', 'Necr', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 ou mais cadáveres', 'Inst', 'Não', 'Não', True, 'Cria mortos-vivos mais poderosos'),
        ],
        # Nível 7
        [
            ('Infligir Ferimentos Graves em Massa', 7, 'MORTE', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 3d8+1/nível de dano em múltiplas criaturas'),
            ('Dedo da Morte', 7, 'MORTE', 'Necr', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Fort neg', 'Sim', False, 'Mata uma criatura com um toque'),
        ],
        # Nível 8
        [
            ('Infligir Ferimentos Críticos em Massa', 8, 'MORTE', 'Necr', '', 'V,G', 'Médio 30m+3m/niv', 'Criaturas em 9m raio', 'Inst', 'Vontade metade', 'Sim', False, 'Causa 4d8+1/nível de dano em múltiplas criaturas'),
            ('Símbolo da Morte', 8, 'MORTE', 'Necr', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa morte em criaturas próximas'),
        ],
        # Nível 9
        [
            ('Implosão', 9, 'MORTE', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
            ('Destruição', 9, 'MORTE', 'Necr', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Fort neg', 'Sim', False, 'Destrói uma criatura'),
        ],
    ],
    "Domínio do fim da vida, do submundo e dos mortos-vivos. Seus seguidores abraçam a morte como um processo natural ou buscam o poder sobre ela."
)

# --- DOMÍNIO DA PROTEÇÃO ---
DOMINIO_PROTECAO = (
    "Proteção",
    "Poderes Concedidos: Aura de Proteção (Você pode conceder +1 de bônus de deflexão na CA uma vez por dia).",
    [
        # Nível 1
        [
            ('Escudo da Fé', 1, 'PROTECAO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de deflexão na CA'),
            ('Proteção Contra o Caos/Mal', 1, 'PROTECAO', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 min/niv(D)', '1 AP', '', 'Não', True, '+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares'),
            ('Resistência', 1, 'PROTECAO', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 minuto', '1 AP', '', 'Não', True, 'Alvo recebe +1 para testes de resistência'),
        ],
        # Nível 2
        [
            ('Proteger Outro', 2, 'PROTECAO', 'Abjur', '', 'V,G,F', 'Curto 7,5m+1,5m/2niv', '1 criatura', '1 hora/niv', '1 AP', '', 'Não', True, 'Você sofre metade do dano dirigido ao alvo'),
            ('Resistência a Elementos', 2, 'PROTECAO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '10 min/niv', '1 AP', '', 'Não', True, 'Ignora 10 pontos dano/ataque de um tipo de energia'),
        ],
        # Nível 3
        [
            ('Círculo Mágico Contra o Caos/Mal', 3, 'PROTECAO', 'Abjur [bem]', '', 'V,G,M/FD', 'Toque', 'Eman 3m r', '10 min/niv', '1 AP', '', 'Não', False, 'Como as magias de Proteção, mas com 3 m de raio'),
            ('Proteção Contra Elementos', 3, 'PROTECAO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', False, 'Concede resistência a um tipo de energia'),
        ],
        # Nível 4
        [
            ('Escudo da Ordem', 4, 'PROTECAO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus na CA e testes de resistência'),
            ('Pele Rochosa', 4, 'PROTECAO', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
            ('Proteção Contra a Morte', 4, 'PROTECAO', 'Necr', '', 'V,G,FD', 'Toque', 'Criat. Viva tocada', '1 min/niv', '1 AP', '', 'Não', True, 'Fornece imunidade a magias e efeitos de morte'),
        ],
        # Nível 5
        [
            ('Campo de Força', 5, 'PROTECAO', 'Evoc [força]', '', 'V,G,M', 'Médio 30m+3m/niv', 'Cubo 3m lado', '1 min/niv', 'Não', 'Não', True, 'Cria um campo de força impenetrável'),
            ('Muralha de Força', 5, 'PROTECAO', 'Evoc', '', 'V,G', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', '1 rod/niv', 'Não', 'Não', False, 'Cria uma muralha de força invisível e impenetrável'),
        ],
        # Nível 6
        [
            ('Resistência à Magia', 6, 'PROTECAO', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede resistência à magia'),
            ('Escudo de Energia', 6, 'PROTECAO', 'Abjur', '', 'V,G', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Absorve dano de energia'),
        ],
        # Nível 7
        [
            ('Muralha de Ferro', 7, 'PROTECAO', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', 'Inst', 'Não', 'Não', True, 'Cria uma muralha de ferro'),
            ('Proteção Contra Magias', 7, 'PROTECAO', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', True, 'Concede bônus de resistência à magia'),
        ],
        # Nível 8
        [
            ('Aura Sagrada', 8, 'PROTECAO', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
            ('Mente em Branco', 8, 'PROTECAO', 'Abjur', '', 'V,G', 'Toque', 'Criatura tocada', '24 horas', 'Não', 'Não', False, 'Protege a mente de magias de adivinhação e controle mental'),
        ],
        # Nível 9
        [
            ('Campo Antimagia', 9, 'PROTECAO', 'Abjur', '', 'V,G,M', '1,5 m', 'Emanação 3m raio', '10 min/niv', 'Não', 'Não', True, 'Cria uma área onde a magia não funciona'),
            ('Prisão', 9, 'PROTECAO', 'Abjur', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Perm', 'Não', 'Sim', True, 'Prende uma criatura em uma prisão mágica'),
        ],
    ],
    "Domínio da segurança, defesa e resistência. Seus seguidores são guardiões e defensores, protegendo os fracos e os inocentes de todas as ameaças."
)

# --- DOMÍNIO DO SOL ---
DOMINIO_SOL = (
    "Sol",
    "Poderes Concedidos: Rajada Solar (Você pode causar 1d6 de dano de fogo/luz uma vez por dia).",
    [
        # Nível 1
        [
            ('Luz', 1, 'SOL', 'Evoc [luz]', '', 'V,M', 'Toque', 'Objeto tocado', '10 min/niv', 'Não', 'Não', True, 'Faz um objeto brilhar como uma tocha'),
            ('Chama Contínua', 1, 'SOL', 'Evoc [luz]', '', 'V,G,M', 'Toque', 'Objeto tocado', 'Perm', 'Não', 'Não', True, 'Cria uma chama que não consome combustível'),
        ],
        # Nível 2
        [
            ('Chama Sagrada', 2, 'SOL', 'Evoc [luz]', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Luz do Dia', 2, 'SOL', 'Evoc [luz]', '', 'V,G', 'Toque', 'Obj. tocado', '10min/niv(D)', '1 AP', '', 'Não', False, 'Ilumina 18 m de raio com uma luz brilhante'),
        ],
        # Nível 3
        [
            ('Luz do Dia', 3, 'SOL', 'Evoc [luz]', '', 'V,G', 'Toque', 'Obj. tocado', '10min/niv(D)', '1 AP', '', 'Não', False, 'Ilumina 18 m de raio com uma luz brilhante'),
            ('Cegueira/Surdez', 3, 'SOL', 'Necr', '', 'V', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Perm', 'Fort neg', 'Sim', False, 'Cega ou ensurdece uma criatura'),
        ],
        # Nível 4
        [
            ('Escudo de Fogo', 4, 'SOL', 'Evoc [fogo]', '', 'V,G,M', 'Pessoal', 'Você', '1 rod/niv', 'Não', 'Não', True, 'Cria um escudo de fogo que causa dano a quem te ataca'),
            ('Tempestade de Fogo', 4, 'SOL', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', 'Cilindro 12m alt, 6m raio', 'Inst', 'Ref metade', 'Sim', False, 'Chuva de fogo que causa dano'),
        ],
        # Nível 5
        [
            ('Coluna de Chamas', 5, 'SOL', 'Evoc [bem]', '', 'V,G,FD', 'Médio 30m+3m/niv', 'Cilindro 3m raio, 12m alt', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino'),
            ('Chama Sagrada Maior', 5, 'SOL', 'Evoc [luz]', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo divino maior'),
        ],
        # Nível 6
        [
            ('Explosão Solar', 6, 'SOL', 'Evoc [fogo, luz]', '', 'V,G', 'Longo 120m+12m/niv', 'Explosão 12m raio', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo e cega criaturas'),
            ('Símbolo do Sol', 6, 'SOL', 'Evoc [luz]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa dano de luz e cega criaturas próximas'),
        ],
        # Nível 7
        [
            ('Explosão Solar', 7, 'SOL', 'Evoc [fogo, luz]', '', 'V,G', 'Longo 120m+12m/niv', 'Explosão 12m raio', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano de fogo e cega criaturas'),
            ('Palavra Sagrada', 7, 'SOL', 'Evoc [bem]', '', 'V', '12 m', 'Explosão 12m raio', 'Inst', 'Não', 'Sim', False, 'Causa dano e efeitos negativos em criaturas malignas'),
        ],
        # Nível 8
        [
            ('Aura Sagrada', 8, 'SOL', 'Abjur [bem]', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 rod/niv', 'Não', 'Não', False, 'Concede bônus na CA, testes de resistência e resistência à magia'),
            ('Incêndio', 8, 'SOL', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', 'Explosão 12m raio', 'Inst', 'Ref metade', 'Sim', False, 'Causa dano massivo de fogo em área'),
        ],
        # Nível 9
        [
            ('Tempestade de Meteoros', 9, 'SOL', 'Evoc [fogo]', '', 'V,G', 'Longo 120m+12m/niv', '4 meteoros', 'Inst', 'Ref metade', 'Sim', False, 'Chuva de meteoros que causa dano massivo'),
            ('Milagre', 9, 'SOL', 'Evoc', '', 'V,G,FD', 'Ilimitado', 'Variável', 'Inst', 'Não', 'Não', False, 'Realiza um milagre divino'),
        ],
    ],
    "Domínio da luz, calor e vida. Seus seguidores são arautos da verdade e da esperança, dissipando as trevas e trazendo a luz."
)

# --- DOMÍNIO DA SORTE ---
DOMINIO_SORTE = (
    "Sorte",
    "Poderes Concedidos: Boa Sorte (Você pode rolar novamente um teste uma vez por dia).",
    [
        # Nível 1
        [
            ('Bênção', 1, 'SORTE', 'Encant', '', 'V,G,FD', '15 m', 'aliados expl. 15m', '1 min/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 para ataques e testes contra medo'),
            ('Proteção Contra o Caos/Mal', 1, 'SORTE', 'Abjur', '', 'V,G,M/FD', 'Toque', 'Criatura tocada', '1 min/niv(D)', '1 AP', '', 'Não', True, '+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares'),
        ],
        # Nível 2
        [
            ('Auxílio', 2, 'SORTE', 'Encant', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede +1 de bônus de moral em ataques e testes de resistência'),
            ('Escudo da Fé', 2, 'SORTE', 'Abjur', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de deflexão na CA'),
        ],
        # Nível 3
        [
            ('Oração', 3, 'SORTE', 'Encant', '', 'V,G,FD', '12 m', 'Explosão 12m raio', '1 rod/niv', '1 AP', '', 'Não', True, 'Aliados recebem +1 em várias jogadas e os inimigos recebem -1'),
            ('Remover Maldição', 3, 'SORTE', 'Abjur', '', 'V,G', 'Toque', 'Criatura/item Tocado', 'Inst', '1 AP', '', 'Não', True, 'Liberta objeto ou pessoa de maldição'),
        ],
        # Nível 4
        [
            ('Adivinhação', 4, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Obtém conselhos de uma divindade ou poder superior'),
            ('Liberdade de Movimento', 4, 'SORTE', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede imunidade a efeitos de paralisia e restrição'),
        ],
        # Nível 5
        [
            ('Comunhão', 5, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Faz perguntas a uma divindade e recebe respostas sim/não'),
            ('Símbolo da Esperança', 5, 'SORTE', 'Encant [bem]', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Inspira esperança e remove medo'),
        ],
        # Nível 6
        [
            ('Heroísmo Maior', 6, 'SORTE', 'Encant', '', 'V,G', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Concede bônus de moral em ataques, testes de resistência e CA'),
            ('Visão da Verdade', 6, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 min/niv', 'Não', 'Não', True, 'Permite ver a verdade por trás de ilusões e disfarces'),
        ],
        # Nível 7
        [
            ('Lendas e Histórias', 7, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '10 min/niv', 'Não', 'Não', True, 'Revela informações sobre uma pessoa, lugar ou objeto'),
            ('Visão', 7, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', True, 'Obtém uma visão de eventos passados, presentes ou futuros'),
        ],
        # Nível 8
        [
            ('Discernir Localização', 8, 'SORTE', 'Adiv', '', 'V,G', 'Ilimitado', 'Criatura/Objeto', 'Inst', 'Não', 'Não', False, 'Localiza uma criatura ou objeto em qualquer lugar'),
            ('Símbolo da Verdade', 8, 'SORTE', 'Adiv', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Revela a verdade e impede mentiras em uma área'),
        ],
        # Nível 9
        [
            ('Precognição', 9, 'SORTE', 'Adiv', '', 'V,G,M', 'Pessoal', 'Você', '1 hora/niv', 'Não', 'Não', True, 'Concede um bônus de sorte em todas as jogadas'),
            ('Milagre', 9, 'SORTE', 'Evoc', '', 'V,G,FD', 'Ilimitado', 'Variável', 'Inst', 'Não', 'Não', False, 'Realiza um milagre divino'),
        ],
    ],
    "Domínio da fortuna, acaso e destino. Seus seguidores buscam influenciar a sorte, seja para seu próprio benefício ou para o bem maior."
)

# --- DOMÍNIO DA TERRA ---
DOMINIO_TERRA = (
    "Terra",
    "Poderes Concedidos: Mestre da Terra (Você pode usar 'Pedra Mágica' uma vez por dia).",
    [
        # Nível 1
        [
            ('Pedra Mágica', 1, 'TERRA', 'Trans', '', 'V,G,M', 'Toque', '3 pedras', '30 min', 'Não', 'Não', True, 'Transforma pedras em projéteis mágicos'),
            ('Armadura de Pedra', 1, 'TERRA', 'Trans', '', 'V,G,M', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', True, 'Concede bônus de armadura natural'),
        ],
        # Nível 2
        [
            ('Pele Rochosa', 2, 'TERRA', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
            ('Terremoto Menor', 2, 'TERRA', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', 'Área 6m raio', 'Inst', 'Ref neg', 'Sim', False, 'Causa um pequeno terremoto'),
        ],
        # Nível 3
        [
            ('Muralha de Pedra', 3, 'TERRA', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', 'Inst', 'Não', 'Não', True, 'Cria uma muralha de pedra'),
            ('Pedra em Lama', 3, 'TERRA', 'Trans', '', 'V,G,M', 'Médio 30m+3m/niv', 'Cubo 3m lado', 'Inst', 'Não', 'Não', True, 'Transforma pedra em lama'),
        ],
        # Nível 4
        [
            ('Pele Rochosa', 4, 'TERRA', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede redução de dano'),
            ('Terremoto', 4, 'TERRA', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Área 12m raio', 'Inst', 'Ref neg', 'Sim', False, 'Causa um terremoto devastador'),
        ],
        # Nível 5
        [
            ('Invocar Monstro V', 5, 'TERRA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental da terra médio'),
            ('Muralha de Pedra', 5, 'TERRA', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', 'Inst', 'Não', 'Não', True, 'Cria uma muralha de pedra'),
        ],
        # Nível 6
        [
            ('Muralha de Ferro', 6, 'TERRA', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', 'Inst', 'Não', 'Não', True, 'Cria uma muralha de ferro'),
            ('Pedra em Carne', 6, 'TERRA', 'Trans', '', 'V,G,M', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Fort neg', 'Sim', True, 'Transforma pedra em carne'),
        ],
        # Nível 7
        [
            ('Terremoto', 7, 'TERRA', 'Evoc', '', 'V,G', 'Longo 120m+12m/niv', 'Área 12m raio', 'Inst', 'Ref neg', 'Sim', False, 'Causa um terremoto devastador'),
            ('Invocar Monstro VII', 7, 'TERRA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental da terra grande'),
        ],
        # Nível 8
        [
            ('Muralha de Pedra', 8, 'TERRA', 'Conj', '', 'V,G,M', 'Médio 30m+3m/niv', 'Muralha 6m x 6m', 'Inst', 'Não', 'Não', True, 'Cria uma muralha de pedra'),
            ('Símbolo da Terra', 8, 'TERRA', 'Evoc', '', 'V,G,M', 'Toque', 'Símbolo', '10 min/niv', 'Não', 'Não', True, 'Causa dano de terra e atordoa criaturas próximas'),
        ],
        # Nível 9
        [
            ('Invocar Monstro IX', 9, 'TERRA', 'Conj', '', 'V,G,FD', 'Curto 7,5m+1,5m/2niv', 'Criatura invocada', '1 rod/niv', 'Não', 'Não', False, 'Invoca um elemental da terra enorme'),
            ('Implosão', 9, 'TERRA', 'Evoc', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura/rod', '1 rod/niv', 'Fort neg', 'Sim', False, 'Causa implosão em uma criatura'),
        ],
    ],
    "Domínio da solidez, estabilidade e fundação. Seus seguidores são protetores da natureza e da terra, usando seu poder para defender e sustentar."
)

# --- DOMÍNIO DA VIAGEM ---
DOMINIO_VIAGEM = (
    "Viagem",
    "Poderes Concedidos: Pés Ligeiros (Você pode aumentar sua velocidade uma vez por dia).",
    [
        # Nível 1
        [
            ('Passos sem Pegadas', 1, 'VIAGEM', 'Trans', '', 'V,G', 'Toque', 'Criatura tocada', '1 hora/niv', 'Não', 'Não', False, 'Não deixa rastros e dificulta ser rastreado'),
            ('Queda Suave', 1, 'VIAGEM', 'Trans', '', 'V,G', 'Toque', 'Criatura tocada', '1 min/niv', 'Não', 'Não', False, 'Reduz a velocidade de queda'),
        ],
        # Nível 2
        [
            ('Passos Longos', 2, 'VIAGEM', 'Trans', '', 'V,G,M', 'Toque', 'Criatura tocada', '1 hora/niv', 'Não', 'Não', True, 'Aumenta a velocidade de movimento'),
            ('Localizar Objeto', 2, 'VIAGEM', 'Adiv', '', 'V,G,F', 'Longo 120m+12m/niv', 'Objeto', '1 min/niv', 'Não', 'Não', True, 'Localiza um objeto específico'),
        ],
        # Nível 3
        [
            ('Caminhar no Ar', 3, 'VIAGEM', 'Trans', '', 'V,G,FD', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', False, 'Permite que a criatura ande no ar'),
            ('Teletransporte Menor', 3, 'VIAGEM', 'Conj', '', 'V,G', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', False, 'Teletransporta-se para um local próximo'),
        ],
        # Nível 4
        [
            ('Liberdade de Movimento', 4, 'VIAGEM', 'Abjur', '', 'V,G,M', 'Toque', 'Criatura tocada', '10 min/niv', 'Não', 'Não', True, 'Concede imunidade a efeitos de paralisia e restrição'),
            ('Localizar Criatura', 4, 'VIAGEM', 'Adiv', '', 'V,G,F', 'Longo 120m+12m/niv', 'Criatura', '1 min/niv', 'Não', 'Não', True, 'Localiza uma criatura específica'),
        ],
        # Nível 5
        [
            ('Teletransporte', 5, 'VIAGEM', 'Conj', '', 'V,G', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', False, 'Teletransporta-se para um local conhecido'),
            ('Caminhar na Sombra', 5, 'VIAGEM', 'Conj', '', 'V,G', 'Pessoal', 'Você', '1 hora/niv', 'Não', 'Não', False, 'Permite viajar rapidamente através das sombras'),
        ],
        # Nível 6
        [
            ('Viagem Planar', 6, 'VIAGEM', 'Conj', '', 'V,G,F', 'Toque', 'Criatura tocada', 'Inst', 'Não', 'Não', True, 'Transporta criaturas para outro plano de existência'),
            ('Passagem Dimensional', 6, 'VIAGEM', 'Conj', '', 'V', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', False, 'Teletransporta-se para um local próximo'),
        ],
        # Nível 7
        [
            ('Teletransporte Maior', 7, 'VIAGEM', 'Conj', '', 'V,G', 'Pessoal', 'Você', 'Inst', 'Não', 'Não', False, 'Teletransporta-se para qualquer local'),
            ('Caminhar no Vento', 7, 'VIAGEM', 'Trans', '', 'V,G,FD', 'Toque', 'Criatura tocada', '1 hora/niv', 'Não', 'Não', False, 'Transforma-se em névoa e viaja com o vento'),
        ],
        # Nível 8
        [
            ('Discernir Localização', 8, 'VIAGEM', 'Adiv', '', 'V,G', 'Ilimitado', 'Criatura/Objeto', 'Inst', 'Não', 'Não', False, 'Localiza uma criatura ou objeto em qualquer lugar'),
            ('Labirinto', 8, 'VIAGEM', 'Conj', '', 'V,G', 'Curto 7,5m+1,5m/2niv', '1 criatura', 'Inst', 'Não', 'Sim', False, 'Envia uma criatura para um labirinto extradimensional'),
        ],
        # Nível 9
        [
            ('Porta Dimensional', 9, 'VIAGEM', 'Conj', '', 'V,G', 'Longo 120m+12m/niv', 'Portal', '1 rod/niv', 'Não', 'Não', False, 'Cria um portal para outro local ou plano'),
            ('Viagem Planar em Massa', 9, 'VIAGEM', 'Conj', '', 'V,G,F', 'Toque', 'Criaturas tocadas', 'Inst', 'Não', 'Não', True, 'Transporta múltiplas criaturas para outro plano de existência'),
        ],
    ],
    "Domínio do movimento, exploração e jornadas. Seus seguidores são viajantes e descobridores, buscando novos horizontes e superando distâncias."
)

# Lista de todos os domínios para iteração
ALL_DOMAINS = [
    DOMINIO_AR,
    DOMINIO_BEM,
    DOMINIO_CAOS,
    DOMINIO_CONHECIMENTO,
    DOMINIO_CURA,
    DOMINIO_DESTRUICAO,
    DOMINIO_ENGANCAO,
    DOMINIO_FOGO,
    DOMINIO_FORCA,
    DOMINIO_GUERRA,
    DOMINIO_MAGIA,
    DOMINIO_MAL,
    DOMINIO_MORTE,
    DOMINIO_PROTECAO,
    DOMINIO_SOL,
    DOMINIO_SORTE,
    DOMINIO_TERRA,
    DOMINIO_VIAGEM,
]

def seed_dominios(_db: Session, _force: bool = False) -> NoReturn:
    """
    Dados de referência permanecem em ``ALL_DOMAINS`` neste ficheiro.

    O schema atual **não** inclui tabela/modelo ORM ``Dominio``; domínios de
    clérigo estão modelados nas magias (ex.: colunas ``dominios`` /
    ``e_magia_dominio``) e seeds PHB em ``scripts/seed_magias.py`` / pipelines
    associados. Não executar este módulo como seed até existir migração + modelo
    alinhados, se for reintroduzido.
    """
    raise NotImplementedError(
        "seed_dominios: não há tabela `dominios` nem modelo `Dominio` no projeto atual. "
        "Use os seeds de magias / PHB; ver docstring do módulo."
    )

if __name__ == "__main__":
    db_session = None
    try:
        db_session = SessionLocal()
        print("🚀 Conectado ao banco de dados.")
        result = seed_dominios(db_session, force=True)
        print("\n--- Resultado Final do Seed de Domínios ---")
        print(f"Total de domínios processados: {result['total']}")
        print(f"Domínios inseridos: {result['inseridos']}")
        print(f"Domínios ignorados: {result['ignorados']}")
        print(f"Erros: {result['erros']}")
    except NotImplementedError as e:
        print(f"ℹ️  {e}")
    except Exception as e:
        print(f"Fatal error in main execution: {e}")
    finally:
        if db_session:
            db_session.close()
            print("🔌 Conexão com o banco de dados fechada.")