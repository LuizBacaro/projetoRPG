"""
seed_pericias.py

Propósito: Popular a tabela de perícias com dados do D&D 3.5 (Tabela 4-3 — Perícias, Livro do Jogador).

Notas:
- Os nomes seguem a lista canônica da Tabela 4-3 (incluindo as especialidades de Conhecimento).
- A ordem da lista é alfabética (idêntica à do livro).
- Atuação aparece no livro como uma linha; a especialidade (canto, dança, instrumento etc.) é
  escolhida na ficha do personagem e registrada como descrição, sem gerar linhas separadas.
"""

# PERICIAS_DATA
# Estrutura: {
#   "nome": str,
#   "descricao": str,
#   "atributo": str,
#   "classes": [classe1, classe2, ...] # Classes com acesso como perícia de classe
# }

PERICIAS_DATA = [
    {
        "nome": "Abrir Fechaduras",
        "descricao": "Abrir fechaduras e trancas sem a chave, usando ferramentas adequadas.",
        "atributo": "Des",
        "classes": ["Ladino"],
    },
    {
        "nome": "Acrobacias",
        "descricao": "Executar manobras acrob\u00e1ticas em combate (passar por \u00e1reas amea\u00e7adas sem provocar ataques de oportunidade, rolar para reduzir dano de queda, atravessar superf\u00edcies perigosas).",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino", "Monge"],
    },
    {
        "nome": "Adestrar Animais",
        "descricao": "Treinar e comandar animais. Inclui ensinar \u2018truques\u2019, lidar com animais assustados, for\u00e7ar um animal a realizar algo n\u00e3o treinado, ou criar um animal para fins espec\u00edficos (montaria, guarda, ca\u00e7a).",
        "atributo": "Car",
        "classes": ["B\u00e1rbaro", "Druida", "Guerreiro", "Paladino", "Ranger"],
    },
    {
        "nome": "Arte da Fuga",
        "descricao": "Escapar de amarras, algemas, redes, agarr\u00f5es e espa\u00e7os apertados. Pode substituir testes relacionados (por exemplo, para se esgueirar por aberturas pequenas) e, em algumas situa\u00e7\u00f5es, op\u00f5e-se a testes de amarrar/segurar.",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino", "Monge"],
    },
    {
        "nome": "Atua\u00e7\u00e3o",
        "descricao": "Entreter ou impressionar uma plateia usando uma forma de arte escolhida no momento do teste (canto, dan\u00e7a, dramaturgia, humor, instrumentos de corda/percuss\u00e3o/sopro/teclas ou orat\u00f3ria). Pode render dinheiro, fama ou acesso social, e serve de base para efeitos de classe (ex.: m\u00fasica de bardo).",
        "atributo": "Car",
        "classes": ["Bardo", "Ladino", "Monge"],
    },
    {
        "nome": "Avalia\u00e7\u00e3o",
        "descricao": "Estimar o valor de itens, identificar pe\u00e7as valiosas e perceber adultera\u00e7\u00f5es \u00f3bvias (sem substituir magia de identifica\u00e7\u00e3o). \u00datil em com\u00e9rcio, tesouros e barganhas.",
        "atributo": "Int",
        "classes": ["Bardo", "Ladino"],
    },
    {
        "nome": "Blefar",
        "descricao": "Enganar com mentiras, omiss\u00f5es e encena\u00e7\u00f5es; inclui blefes r\u00e1pidos em conversa, distrair guardas e fingir inten\u00e7\u00f5es. Em combate, pode sustentar engodos sociais; em muitos casos \u00e9 resistido por Sentir Motiva\u00e7\u00e3o.",
        "atributo": "Car",
        "classes": ["Bardo", "Feiticeiro", "Ladino"],
    },
    {
        "nome": "Cavalgar",
        "descricao": "Controlar montarias em deslocamento e combate montado. Inclui manter-se na sela, guiar com as pernas, saltar obst\u00e1culos, lutar sem penalidades e reagir a quedas ou impactos.",
        "atributo": "Des",
        "classes": ["B\u00e1rbaro", "Druida", "Guerreiro", "Paladino", "Ranger"],
    },
    {
        "nome": "Concentra\u00e7\u00e3o",
        "descricao": "Manter foco sob dor, distra\u00e7\u00e3o ou condi\u00e7\u00f5es adversas. Muito usada para conjura\u00e7\u00e3o (evitar perder magias) e para manter efeitos que exigem aten\u00e7\u00e3o cont\u00ednua.",
        "atributo": "Con",
        "classes": ["Bardo", "Cl\u00e9rigo", "Druida", "Feiticeiro", "Mago", "Monge", "Paladino", "Ranger"],
    },
    {
        "nome": "Conhecimento (arcano)",
        "descricao": "Saber acad\u00eamico e erudito sobre arcanismo. Serve para lembrar fatos, identificar assuntos, e interpretar pistas m\u00edsticas sobre: mist\u00e9rios antigos, tradi\u00e7\u00f5es m\u00e1gicas, s\u00edmbolos arcanos, frases e\nconstru\u00e7\u00f5es ocultas, drag\u00f5es e bestas m\u00e1gicas.",
        "atributo": "Int",
        "classes": ["Cl\u00e9rigo", "Feiticeiro", "Mago", "Monge"],
    },
    {
        "nome": "Conhecimento (arquitetura e engenharia)",
        "descricao": "Saber acad\u00eamico e erudito sobre arquitetura e engenharia. Serve para lembrar identificar constru\u00e7\u00f5es e padr\u00f5es de constru\u00e7\u00f5es, e interpretar pistas sobre: constru\u00e7\u00f5es, aquedutos, pontes, fortifica\u00e7\u00f5es.",
        "atributo": "Int",
        "classes": ["Mago"],
    },
    {
        "nome": "Conhecimento (geografia)",
        "descricao": "Saber acad\u00eamico e erudito sobre geografia. Serve para lembrar de locais, terrenos e quest\u00f5es naturais, e interpretar pistas sobre: terras, terrenos, climas, povos.",
        "atributo": "Int",
        "classes": ["Mago", "Ranger"],
    },
    {
        "nome": "Conhecimento (hist\u00f3ria)",
        "descricao": "Saber acad\u00eamico e erudito sobre hist\u00f3ria. Serve para lembrar fatos, identificar assuntos e coisas hist\u00f3ricas, e interpretar pistas sobre: realeza, guerras, col\u00f4nias, migra\u00e7\u00f5es, funda\u00e7\u00e3o de cidades.",
        "atributo": "Int",
        "classes": ["Cl\u00e9rigo", "Mago"],
    },
    {
        "nome": "Conhecimento (local)",
        "descricao": "Saber acad\u00eamico e erudito sobre o locais. Serve para lembrar fatos, identificar criaturas/assuntos, e interpretar pistas sobre: lendas, personalidades, habitantes, leis, costumes, tradi\u00e7\u00f5es, human\u00f3ides.",
        "atributo": "Int",
        "classes": ["Ladino", "Mago"],
    },
    {
        "nome": "Conhecimento (masmorras)",
        "descricao": "Saber acad\u00eamico e erudito sobre masmorras. Serve para lembrar fatos, identificar criaturas/assuntos, e interpretar pistas sobre: cavernas, limos, estudo das cavernas, estruturas e tipos de masmorras.",
        "atributo": "Int",
        "classes": ["Mago", "Ranger"],
    },
    {
        "nome": "Conhecimento (natureza)",
        "descricao": "Saber acad\u00eamico e erudito sobre natureza. Serve para lembrar fatos, identificar detalhes sobre a fauna e flora, e interpretar pistas sobre: animais, fadas, gigantes, human\u00f3ides monstruosos, plantas, esta\u00e7\u00f5es\ne ciclos, clima, insetos.",
        "atributo": "Int",
        "classes": ["Druida", "Mago", "Ranger"],
    },
    {
        "nome": "Conhecimento (nobreza e realeza)",
        "descricao": "Saber acad\u00eamico e erudito sobre a nobreza e a realeza. Serve para lembrar fatos, identificar pessoas/assuntos, e interpretar pistas sobre: linhagens, her\u00e1ldica, \u00e1rvores geneal\u00f3gicas, ditados e\ncita\u00e7\u00f5es, personalidades.",
        "atributo": "Int",
        "classes": ["Mago", "Paladino"],
    },
    {
        "nome": "Conhecimento (planos)",
        "descricao": "Saber acad\u00eamico e erudito sobre planos. Serve para lembrar fatos, identificar assuntos, e interpretar pistas sobre: Planos Interiores, Planos Exteriores, Plano Astral, Plano Et\u00e9reo,\nextra-planares, elementais, magia relacionada aos planos.",
        "atributo": "Int",
        "classes": ["Cl\u00e9rigo", "Mago"],
    },
    {
        "nome": "Conhecimento (religi\u00e3o)",
        "descricao": "Saber acad\u00eamico e erudito sobre religi\u00e3o e ritos clericais. Serve para lembrar fatos, identificar ritos, criaturas/assuntos, e interpretar pistas sobre: divindades, hist\u00f3ria m\u00edtica, tradi\u00e7\u00f5es eclesi\u00e1sticas, s\u00edmbolos as\ngrados, mortos-vivos.",
        "atributo": "Int",
        "classes": ["Cl\u00e9rigo", "Mago", "Monge", "Paladino"],
    },
    {
        "nome": "Cura",
        "descricao": "Primeiros socorros e medicina pr\u00e1tica: estabilizar moribundos, tratar venenos/doen\u00e7as, acelerar recupera\u00e7\u00e3o com cuidados prolongados e prestar socorro em combate (ex.: parar sangramento e estabilizar).",
        "atributo": "Sab",
        "classes": ["Cl\u00e9rigo", "Druida", "Paladino", "Ranger"],
    },
    {
        "nome": "Decifrar Escrita",
        "descricao": "Interpretar escrita incomum, c\u00f3digos e linguagens arcanas. Tamb\u00e9m pode permitir ler pergaminhos ou inscri\u00e7\u00f5es m\u00e1gicas quando apropriado (muitas vezes em conjunto com Identificar Magia).",
        "atributo": "Int",
        "classes": ["Bardo", "Ladino", "Mago"],
    },
    {
        "nome": "Diplomacia",
        "descricao": "Influenciar atitudes, negociar e mediar conflitos. Usada para melhorar a disposi\u00e7\u00e3o de PDMs, conseguir favores, obter permiss\u00e3o ou reduzir hostilidade \u2014 geralmente exige intera\u00e7\u00e3o social e algum tempo.\nUso comum: ajustar a atitude de um PDM (hostil \u2192 indiferente \u2192 amig\u00e1vel), negociar termos e pedir favores plaus\u00edveis; quanto maior a mudan\u00e7a desejada, maior a CD e/ou o tempo exigido.",
        "atributo": "Car",
        "classes": ["Bardo", "Cl\u00e9rigo", "Druida", "Ladino", "Monge", "Paladino"],
    },
    {
        "nome": "Disfarces",
        "descricao": "Alterar apar\u00eancia para parecer outra pessoa/ra\u00e7a/condi\u00e7\u00e3o social. Inclui maquiagem, roupas, maneirismos e falsos adere\u00e7os; testes podem ser resistidos por Observar e/ou por intera\u00e7\u00f5es pr\u00f3ximas.",
        "atributo": "Car",
        "classes": ["Bardo", "Ladino"],
    },
    {
        "nome": "Equil\u00edbrio",
        "descricao": "Manter-se de p\u00e9 em superf\u00edcies estreitas, escorregadias ou inst\u00e1veis, evitando quedas. Movimentos r\u00e1pidos ou terreno ruim aumentam a dificuldade.",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino", "Monge"],
    },
    {
        "nome": "Escalar",
        "descricao": "Subir e se mover por paredes, cordas e superf\u00edcies \u00edngremes. A CD varia pela textura e inclina\u00e7\u00e3o; em falhas grandes voc\u00ea pode cair.",
        "atributo": "For",
        "classes": ["B\u00e1rbaro", "Bardo", "Guerreiro", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Esconder-se",
        "descricao": "Evitar ser visto usando cobertura, sombras e distra\u00e7\u00f5es. Normalmente exige algum tipo de oculta\u00e7\u00e3o/cobertura; testes s\u00e3o resistidos por Observar e podem ser refeitos conforme voc\u00ea se move ou a situa\u00e7\u00e3o muda.",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Falar Idioma",
        "descricao": "Aprende idiomas adicionais: cada gradua\u00e7\u00e3o representa um idioma que voc\u00ea fala e entende fluentemente. No livro n\u00e3o h\u00e1 teste de per\u00edcia padr\u00e3o para falar; o atributo (INT) na ficha segue a conven\u00e7\u00e3o SRD.",
        "atributo": "Int",
        "classes": [
            "B\u00e1rbaro",
            "Bardo",
            "Cl\u00e9rigo",
            "Druida",
            "Feiticeiro",
            "Guerreiro",
            "Ladino",
            "Mago",
            "Monge",
            "Paladino",
            "Ranger",
        ],
    },
    {
        "nome": "Falsifica\u00e7\u00e3o",
        "descricao": "Criar ou alterar documentos (cartas, selos, registros) de modo convincente. Em geral \u00e9 resistido por Avalia\u00e7\u00e3o/Percep\u00e7\u00e3o do examinador e recebe modificadores pelo tempo gasto e pela qualidade do material.",
        "atributo": "Int",
        "classes": ["Ladino"],
    },
    {
        "nome": "Furtividade",
        "descricao": "Mover-se sem ser ouvido. Testes s\u00e3o resistidos por Ouvir; terreno barulhento, armadura e pressa dificultam.",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Identificar Magia",
        "descricao": "Analisar fen\u00f4menos m\u00e1gicos: identificar magias sendo conjuradas, efeitos em andamento, propriedades gerais de itens, e reconhecer s\u00edmbolos/selos arcanos. Normalmente requer observa\u00e7\u00e3o e, \u00e0s vezes, acesso ao item/efeito.",
        "atributo": "Int",
        "classes": ["Bardo", "Cl\u00e9rigo", "Druida", "Feiticeiro", "Mago"],
    },
    {
        "nome": "Intimida\u00e7\u00e3o",
        "descricao": "Coagir por amea\u00e7a, presen\u00e7a ou viol\u00eancia impl\u00edcita. Pode for\u00e7ar coopera\u00e7\u00e3o moment\u00e2nea, arrancar informa\u00e7\u00e3o ou impor medo; muitas vezes envolve circunst\u00e2ncias e pode ter consequ\u00eancias sociais.",
        "atributo": "Car",
        "classes": ["B\u00e1rbaro", "Guerreiro", "Ladino"],
    },
    {
        "nome": "Nata\u00e7\u00e3o",
        "descricao": "Mover-se na \u00e1gua, lidar com correnteza, turbul\u00eancia e obst\u00e1culos. A CD depende da \u00e1gua (calma, agitada, tempestuosa) e de carga/armadura. Falhas podem fazer voc\u00ea afundar ou engolir \u00e1gua.",
        "atributo": "For",
        "classes": ["B\u00e1rbaro", "Bardo", "Druida", "Guerreiro", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Observar",
        "descricao": "Perceber detalhes visuais, notar criaturas escondidas, armadilhas visuais e movimentos sutis. \u00c9 frequentemente resistido por Esconder-se e pode ser afetado por dist\u00e2ncia, ilumina\u00e7\u00e3o e cobertura.",
        "atributo": "Sab",
        "classes": ["Druida", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Obter Informa\u00e7\u00e3o",
        "descricao": "Coletar boatos, pistas e not\u00edcias em comunidades (tavernas, mercados, becos). Exige tempo e intera\u00e7\u00e3o social; o resultado depende do tamanho do local e da disposi\u00e7\u00e3o das pessoas.",
        "atributo": "Car",
        "classes": ["Bardo", "Ladino"],
    },
    {
        "nome": "Of\u00edcios",
        "descricao": "Produzir e consertar itens mundanos (ferraria, carpintaria, alquimia mundana a crit\u00e9rio do livro, etc.). Voc\u00ea escolhe um of\u00edcio espec\u00edfico; progresso costuma ser calculado por semana de trabalho e pode exigir ferramentas/mat\u00e9ria-prima.",
        "atributo": "Int",
        "classes": ["B\u00e1rbaro", "Bardo", "Cl\u00e9rigo", "Druida", "Feiticeiro", "Guerreiro", "Ladino", "Mago", "Monge", "Paladino", "Ranger"],
    },
    {
        "nome": "Operar Mecanismo",
        "descricao": "Desarmar armadilhas e manipular mecanismos (trancas complexas, gatilhos, dispositivos). Muitas vezes exige ferramentas adequadas. Desarmar armadilhas exige antes detect\u00e1-las (normalmente via Procurar).",
        "atributo": "Int",
        "classes": ["Ladino"],
    },
    {
        "nome": "Ouvir",
        "descricao": "Perceber sons, detectar aproxima\u00e7\u00f5es e localizar origem de ru\u00eddos. \u00c9 resistido por Furtividade e sofre modificadores por dist\u00e2ncia, portas, vento e distra\u00e7\u00f5es.",
        "atributo": "Sab",
        "classes": ["B\u00e1rbaro", "Bardo", "Druida", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Prestidigita\u00e7\u00e3o",
        "descricao": "Truques de m\u00e3o: esconder, sacar, plantar ou \u2018sumir\u2019 com objetos sem ser notado. Resistido por Observar; pode ser usado para pequenas manipula\u00e7\u00f5es durante conversas ou confus\u00f5es.",
        "atributo": "Des",
        "classes": ["Bardo", "Ladino"],
    },
    {
        "nome": "Procurar",
        "descricao": "Investigar uma \u00e1rea para achar armadilhas, compartimentos secretos, pistas e detalhes escondidos. Em muitas mesas, \u00e9 a per\u00edcia-chave para \u2018achar a coisa\u2019 antes que ela te ache.\nObserva\u00e7\u00e3o: algumas armadilhas t\u00eam CD de Procurar; outras exigem descri\u00e7\u00e3o ativa do jogador (mexer, bater, medir) al\u00e9m do teste.",
        "atributo": "Int",
        "classes": ["Ladino", "Ranger"],
    },
    {
        "nome": "Profiss\u00e3o",
        "descricao": "Compet\u00eancia em uma ocupa\u00e7\u00e3o (marinheiro, mercador, escriba etc.). Serve para ganhar a vida, conhecer rotinas do of\u00edcio e resolver tarefas t\u00edpicas daquela profiss\u00e3o.",
        "atributo": "Sab",
        "classes": ["Bardo", "Cl\u00e9rigo", "Druida", "Feiticeiro", "Ladino", "Mago", "Monge", "Paladino", "Ranger"],
    },
    {
        "nome": "Saltar",
        "descricao": "Realizar saltos longos/altos e ultrapassar obst\u00e1culos. A CD depende da dist\u00e2ncia/altura e do impulso.",
        "atributo": "For",
        "classes": ["B\u00e1rbaro", "Bardo", "Guerreiro", "Ladino", "Monge", "Ranger"],
    },
    {
        "nome": "Sentir Motiva\u00e7\u00e3o",
        "descricao": "Ler inten\u00e7\u00f5es, perceber mentiras e avaliar linguagem corporal. Frequentemente \u00e9 resistido por Blefar; tamb\u00e9m ajuda a notar manipula\u00e7\u00f5es e incoer\u00eancias em depoimentos.",
        "atributo": "Sab",
        "classes": ["Bardo", "Ladino", "Monge", "Paladino"],
    },
    {
        "nome": "Sobreviv\u00eancia",
        "descricao": "Orientar-se, rastrear, ca\u00e7ar, prever tempo e sobreviver em ambientes hostis. Pode substituir ou apoiar outros recursos de explora\u00e7\u00e3o (mapas, guias, etc.).",
        "atributo": "Sab",
        "classes": ["B\u00e1rbaro", "Druida", "Ranger"],
    },
    {
        "nome": "Usar Cordas",
        "descricao": "Fazer n\u00f3s, amarrar, prender, la\u00e7ar e usar cordas de modo seguro. Pode ser resistido por Arte da Fuga (quando algu\u00e9m tenta se soltar).",
        "atributo": "Des",
        "classes": ["Ladino", "Ranger"],
    },
    {
        "nome": "Usar Instrumento M\u00e1gico",
        "descricao": "Ativar itens m\u00e1gicos sem atender pr\u00e9-requisitos (classe, lista de magias, alinhamento etc.). Normalmente envolve testes espec\u00edficos por tipo de item e falhas podem impedir novas tentativas por um tempo.",
        "atributo": "Car",
        "classes": ["Bardo", "Ladino"],
    },
]

# Total: 45 perícias (Tabela 4-3 do Livro do Jogador D&D 3.5, página 55)
