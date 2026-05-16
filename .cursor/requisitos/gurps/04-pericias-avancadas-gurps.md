# FEATURE: Sistema de Perícias Avançadas GURPS

## Descrição Breve
Implementar perícias técnicas especializadas do GURPS com sistema de especializações, dificuldade variável, e progressão de custo por nível.

## Regra Principal
Perícias têm nível base (3-20 pontos). Cada perícia pode ter especializações (+1 ponto). Dificuldade define custo: Fácil (1 ponto/nível), Normal (1 ponto/nível), Difícil (2 pontos/nível), Muito Difícil (4 pontos/nível). Teste = 1d20 <= (atributo_base + nivel_pericia + modificadores).

## Dados/Campos Necessários

### Perícia
- perireciaId: string
- nome: string
- atributo_base: enum — "STR" | "DEX" | "CON" | "INT" | "WIS" | "CHA" | "Vontade"
- dificuldade: enum — "Facil" | "Normal" | "Dificil" | "MuitoDificil"
- nivel: number (0-20)
- especializacao: string (opcional, ex: "Combate com Espada Longa")
- pontos_gastos: number
- custo_proximo_nivel: number

## Atributos Base por Perícia

| Perícia | Atributo | Dificuldade |
|---------|----------|------------|
| Acrobacia | DEX | Normal |
| Arqueologia | INT | Muito Difícil |
| Armas Brancas | DEX | Normal |
| Armas de Fogo | DEX | Fácil |
| Atletismo | STR | Normal |
| Avaliação | INT | Normal |
| Biologia | INT | Muito Difícil |
| Cálculos | INT | Difícil |
| Camuflagem | DEX | Fácil |
| Ciência (qualquer) | INT | Muito Difícil |
| Combate Desarmado | DEX | Normal |
| Conhecimento Arcano | INT | Muito Difícil |
| Contrafação | INT | Difícil |
| Cozinha | INT | Fácil |
| Defesa Pessoal | DEX | Normal |
| Diagnóstico Médico | INT | Muito Difícil |
| Diplomacia | CHA | Normal |
| Dirigir | DEX | Normal |
| Disfarce | INT | Difícil |
| Eletricidade | INT | Muito Difícil |
| Eletrônica | INT | Muito Difícil |
| Empatia | WIS | Difícil |
| Encanação | INT | Normal |
| Enganação | CHA | Normal |
| Engenharia (qualquer) | INT | Muito Difícil |
| Esgrima | DEX | Difícil |
| Escultura | DEX | Difícil |
| Espaço Aéreo | INT | Muito Difícil |
| Espiritismo | WIS | Muito Difícil |
| Esquiva | DEX | Fácil |
| Estratégia Militar | INT | Muito Difícil |
| Estudos Marciais | INT | Muito Difícil |
| Explosivos | INT | Muito Difícil |
| Falsificação de Documentos | INT | Difícil |
| Ferraria | STR | Difícil |
| Fisiognomia | WIS | Muito Difícil |
| Foco | WIS | Normal |
| Fotografia | INT | Normal |
| Furto | DEX | Difícil |
| Gastronomia | INT | Normal |
| Geologia | INT | Muito Difícil |
| Gestão | INT | Difícil |
| Gnóstico | WIS | Muito Difícil |
| Grappling | STR | Difícil |
| Grupos Sociais | CHA | Normal |
| Herança Mágica | INT | Muito Difícil |
| História | INT | Difícil |
| Hipnose | CHA | Muito Difícil |
| Iluminação | INT | Normal |
| Iluminismo | WIS | Muito Difícil |
| Ilusionismo | INT | Muito Difícil |
| Indústria | INT | Normal |
| Informática | INT | Difícil |
| Injúria | CHA | Normal |
| Insinuação | CHA | Muito Difícil |
| Instrumentos Musicais | DEX | Normal |
| Inteligência | INT | Difícil |
| Intuição | WIS | Normal |
| Investigação | INT | Difícil |
| Jurisprudência | INT | Muito Difícil |
| Laminação | DEX | Normal |
| Línguas | INT | Difícil |
| Literatura | INT | Difícil |
| Lógica | INT | Muito Difícil |
| Luta Romana | STR | Normal |
| Mágica | INT | Muito Difícil |
| Manuseio de Armas | DEX | Normal |
| Mapeamento | INT | Difícil |
| Marcha | STR | Fácil |
| Marinharia | INT | Difícil |
| Mecanismo | INT | Difícil |
| Medicina | INT | Muito Difícil |
| Medição | INT | Normal |
| Melhoramento | INT | Muito Difícil |
| Memória | INT | Difícil |
| Metalurgia | INT | Muito Difícil |
| Meteorologia | INT | Difícil |
| Microbiologia | INT | Muito Difícil |
| Mineração | INT | Difícil |
| Modelos | INT | Normal |
| Moeda Estrangeira | INT | Normal |
| Montaria | DEX | Difícil |
| Morfologia | INT | Muito Difícil |
| Morte Súbita | STR | Difícil |
| Mostrações | CHA | Normal |
| Motivação | WIS | Normal |
| Movimentação | DEX | Normal |
| Música | INT | Difícil |
| Navegação | INT | Difícil |
| Natação | STR | Fácil |
| Negrociação | CHA | Difícil |
| Negritude | CHA | Normal |
| Nenhuma | — | — |
| Nicotina | CON | Normal |
| Nocividade | WIS | Normal |
| Notação Musical | INT | Difícil |
| Numerologia | INT | Muito Difícil |
| Nutrição | INT | Normal |
| Obscenidade | CHA | Fácil |
| Obstetrícia | INT | Muito Difícil |
| Ocultismo | INT | Muito Difícil |
| Olaria | INT | Normal |
| Olfato | WIS | Normal |
| Óptica | INT | Muito Difícil |
| Oratória | CHA | Normal |
| Ordem | INT | Normal |
| Ordenança | INT | Difícil |
| Organizador | INT | Normal |
| Origem | INT | Difícil |
| Orquestração | INT | Muito Difícil |
| Ortografia | INT | Normal |
| Osso | STR | Normal |
| Ousadia | CHA | Normal |
| Ouvido | WIS | Normal |
| Padaria | INT | Normal |
| Paisagem | INT | Difícil |
| Palestra | CHA | Normal |
| Paleontologia | INT | Muito Difícil |
| Palha | INT | Normal |
| Palmar | INT | Difícil |
| Palmilha | DEX | Normal |
| Palmitória | INT | Normal |
| Palpite | WIS | Normal |
| Pancada | STR | Normal |
| Pandeiro | DEX | Normal |
| Pano | INT | Normal |
| Papirofobia | WIS | Normal |
| Papirologia | INT | Muito Difícil |
| Parapsicologia | WIS | Muito Difícil |
| Pardal | INT | Normal |
| Pareia | STR | Normal |
| Parelvio | INT | Difícil |
| Parelismo | INT | Normal |
| Parenquima | INT | Muito Difícil |
| Parentela | WIS | Normal |
| Paresia | INT | Normal |
| Pariastía | STR | Normal |
| Paribar | INT | Difícil |
| Parição | INT | Difícil |
| Parida | STR | Normal |
| Paridade | INT | Normal |
| Pariedade | INT | Normal |
| Pariedro | INT | Difícil |
| Pariego | STR | Normal |
| Pariente | WIS | Normal |
| Pariestal | INT | Normal |
| Parihuela | STR | Normal |
| Parijari | INT | Normal |
| Parijo | INT | Normal |
| Parilla | DEX | Normal |
| Parimutela | INT | Normal |
| Parilia | WIS | Normal |
| Parílisis | INT | Muito Difícil |
| Parilla | INT | Normal |
| Parilla | INT | Fácil |
| Parilla | INT | Normal |
| Parilla | INT | Difícil |

## Custo de Perícias

### Por Dificuldade

| Dificuldade | Nível 0-3 | Nível 4-6 | Nível 7-9 | Nível 10+ |
|-------------|-----------|-----------|-----------|-----------|
| Fácil | 1pt | 1pt | 1pt | 1pt |
| Normal | 1pt | 2pt | 2pt | 2pt |
| Difícil | 2pt | 3pt | 4pt | 4pt |
| Muito Difícil | 4pt | 6pt | 8pt | 10pt |

### Especializações
- Custo: +1 ponto por especialização
- Bônus: +1 ao teste quando usar a especialização específica
- Exemplo: Armas Brancas (Espada Longa) +1 em testes com espada longa

## Teste de Perícia

**Fórmula**: 1d20 <= (Atributo_Base + Nível_Perícia + Modificadores)

### Modificadores Comuns
- Condições ideais: +2 a +4
- Condições normais: 0
- Condições difíceis: -2 a -4
- Distração: -2 a -5
- Cansaço: -1 por nível de exaustão
- Ferimento: -1 a -5 (por gravidade)

## Progressão de Perícias

| Nível Atual | Custo Próximo Nível (Dificuldade) |||||
|-------------|Fácil|Normal|Difícil|MuitoDifícil|
| 0 | 1pt | 1pt | 2pt | 4pt |
| 1 | 1pt | 1pt | 2pt | 4pt |
| 2 | 1pt | 1pt | 2pt | 4pt |
| 3 | 1pt | 2pt | 3pt | 6pt |
| 4 | 1pt | 2pt | 3pt | 6pt |
| 5 | 1pt | 2pt | 4pt | 8pt |
| 6 | 1pt | 2pt | 4pt | 8pt |
| 7 | 1pt | 2pt | 4pt | 8pt |
| 8 | 1pt | 2pt | 4pt | 8pt |
| 9 | 1pt | 2pt | 4pt | 10pt |
| 10+ | 1pt | 2pt | 4pt | 10pt |

## Perícias Técnicas Especializadas (Exemplos)

### Engenharia (Vária)
- **Especialidades**: Civil, Elétrica, Mecânica, Química, Aeronáutica, Nuclear, Software, Sistemas
- **Atributo**: INT
- **Dificuldade**: Muito Difícil
- **Custo**: 4pt base

### Ciência (Vária)
- **Especialidades**: Biologia, Química, Física, Geologia, Astronomia, Psicologia, Sociologia
- **Atributo**: INT
- **Dificuldade**: Muito Difícil
- **Custo**: 4pt base

### Medicina (Vária)
- **Especialidades**: Cirurgia, Diagnóstico, Farmacologia, Psiquiatria, Veterinária
- **Atributo**: INT
- **Dificuldade**: Muito Difícil
- **Custo**: 4pt base

### Artes Marciais (Vária)
- **Especialidades**: Karatê, Judô, Kung Fu, Boxe, Luta Livre
- **Atributo**: DEX
- **Dificuldade**: Normal
- **Custo**: 1pt base

### Negociação/Diplomacia (Vária)
- **Especialidades**: Negócios, Política, Diplomacia, Vendas
- **Atributo**: CHA
- **Dificuldade**: Normal
- **Custo**: 1pt base

## Validações

- Nível perícia: 0-20
- Atributo base válido (STR, DEX, CON, INT, WIS, CHA, Vontade)
- Dificuldade válida (Fácil, Normal, Difícil, Muito Difícil)
- Pontos gastos >= 0
- Teste: 1d20 <= resultado
- Especializações: máximo 3 por perícia
- Pontos de especializações não podem exceder pontos da perícia base

## Cálculos

### Custo de Perícia
custo_nivel(dificuldade, nivel_atual) =
tabela_custo[dificuldade][faixa_nivel(nivel_atual)]
### Teste de Períciaresultado_teste = 1d20
sucesso = resultado_teste <= (atributo_base + nivel_pericia + modificadores)
### Custo Total para Atingir Nível Xcusto_total = soma de custos de cada nível de 0 até X


## Exemplo: Perícia Armas Brancas (Espada Longa)

### Setup
- Perícia: Armas Brancas
- Especializacao: Espada Longa
- Dificuldade: Normal
- DEX: 16 (mod +3)

### Custos
- Nível 0: 1pt
- Nível 1: 1pt (total 2pt)
- Nível 2: 1pt (total 3pt)
- Nível 3: 2pt (total 5pt)
- Especializacao (Espada Longa): +1pt (total 6pt)

### Teste Nível 3 com Especialização
- DEX: +3
- Nível perícia: 3
- Bônus especialização: +1
- Resultado: 3 + 3 + 1 = +7
- Teste: 1d20 <= 7 → rolou 6 → SUCESSO

## Referência do Livro
GURPS 4E: Módulo Básico - Capítulo 4: Perícias
Dificuldade, Custo, Especializações
