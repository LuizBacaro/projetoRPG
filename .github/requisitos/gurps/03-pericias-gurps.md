# FEATURE: Sistema de Perícias GURPS 4E

## Descrição Breve
Implementar 40+ perícias com custo em pontos, atributo base, nível de dificuldade e testes de sucesso.

## Regra Principal
Cada perícia tem custo fixo (1-4 pontos por nível) e está ligada a um atributo base (ST/DX/HT/IQ). Nível da perícia = atributo base + bônus. Teste: 1d20 <= nível da perícia.

## Dados/Campos Necessários

### Perícia
- skillId: string
- nome: string
- atributoBase: enum — "ST" | "DX" | "HT" | "IQ"
- dificuldade: enum — "Fácil" | "Média" | "Difícil" | "Muito Difícil"
- custoPorPonto: number — pontos por nível (1-4)
- nivel: number (0-20+) — nível adquirido
- especializacao: string (opcional) — ex: "Espada Longa", "Eletrônica"
- descricao: string

## Custos por Dificuldade

| Dificuldade | Custo/Nível | Tempo de Aprendizado |
|-------------|------------|---------------------|
| Fácil | 1 pt | 1 semana |
| Média | 2 pts | 2 semanas |
| Difícil | 4 pts | 1 mês |
| Muito Difícil | 8 pts | 2 meses |

## Perícias Principais por Atributo Base

### Perícias de Força (ST)
- **Levantamento de Peso**: Fácil — capacidade de carga
- **Pulo**: Média — distância de pulo
- **Remo**: Média — remar barcos
- **Equilíbrio**: Média — não cair

### Perícias de Destreza (DX)
- **Acrobacia**: Difícil — saltos, rolamentos
- **Acuidade Visual**: Fácil — perceber detalhes
- **Arco**: Média — usar arco e flecha
- **Arma de Fogo**: Média — pistola, rifle
- **Combate Desarmado**: Média — lutar sem armas
- **Esgrima**: Média — combate com espada
- **Furtividade**: Média — se esconder
- **Lançamento**: Fácil — lançar objetos
- **Pilotagem**: Média — dirigir, navegar
- **Prestidigitação**: Difícil — truques manuais
- **Salto**: Média — altura de pulo

### Perícias de Constituição (HT)
- **Aguçar Sentidos**: Média — concentrar em som/cheiro
- **Resistência**: Fácil — cansaço
- **Corrida**: Fácil — rapidez de movimento
- **Sobrevivência**: Média — em ambientes selvagens

### Perícias de Inteligência (IQ)
- **Administração**: Média — gerir negócios
- **Arqueologia**: Difícil — estudar artefatos antigos
- **Artesanato**: Média — criar objetos
- **Ciência** (várias especialidades): Muito Difícil — física, química, etc.
- **Comércio**: Média — negociação
- **Conhecimento Acadêmico** (vários): Difícil — história, mitologia, etc.
- **Culinária**: Fácil — cozinhar
- **Diplomacia**: Difícil — negociar
- **Educação**: Fácil — saber geral
- **Eletrônica**: Difícil — circuitos, reparos
- **Engenharia** (várias): Difícil — pontes, máquinas, etc.
- **Estratégia**: Muito Difícil — planejamento militar
- **Falsificação**: Difícil — criar documentos falsos
- **Farmacologia**: Muito Difícil — drogas e venenos
- **Fotografia**: Fácil — tirar fotos
- **História**: Difícil — eventos passados
- **Investigação**: Difícil — buscar pistas
- **Ladinagem**: Média — abrir fechaduras
- **Linguística**: Difícil — aprender idiomas
- **Magia**: Muito Difícil — conjurar feitiços (requer vantagem Magia)
- **Mecânica**: Difícil — máquinas
- **Medicina**: Difícil — curar ferimentos
- **Metafísica**: Muito Difícil — magia, deus, sobrenatural
- **Navegação**: Média — encontrar caminho
- **Oculismo**: Difícil — fatos secretos
- **Ocultismo**: Difícil — magia, ritual
- **Ofício** (vários): Média — carpintaria, etc.
- **Orientação**: Fácil — saber direção
- **Oratória**: Média — discursos
- **Psicologia**: Difícil — comportamento humano
- **Tática**: Difícil — combate
- **Teologia**: Difícil — religião

## Teste de Perícia

**Fórmula**: 1d20 <= nível da perícia

- **Sucesso**: resultado <= nível da perícia
- **Falha Crítica**: resultado 20 natural (sempre falha)
- **Sucesso Crítico**: resultado 3 ou menos (sempre sucesso, se nível >= 3)

### Nível de Perícia
nivelPericia = atributoBase + pontosInvestidos


**Exemplo - Esgrima (DX)**:
- DX = 12
- Pontos em Esgrima = 4
- Nível de Esgrima = 12 + 4 = 16

## Exemplo de Teste

### Situação: Ladino tenta abrir fechadura com Ladinagem 15

**Teste**: 1d20 <= 15
- Resultado 1-15: **Sucesso** — fechadura abre
- Resultado 16-20: **Falha** — não consegue abrir (agora)
- Resultado 20 (natural): **Falha Crítica** — quebra a fechadura, faz barulho

## Especializações

Cada perícia pode ter especializações com +3 bônus:
- **Arma de Fogo (Pistola)**: +3 ao usar pistolas especificamente
- **Espada (Longa)**: +3 ao usar espada longa especificamente
- **Eletrônica (Computadores)**: +3 em eletrônica de computadores

## Validações
- Nível de perícia mínimo 0 (sem treinamento = teste contra atributo base)
- Nível máximo ilimitado
- Custo em pontos respeita tabela de dificuldade
- Teste 1d20 compara contra nível

## Cálculos

### Custo Total de Perícia

ustoTotal(nivel, dificuldade) =
nivel × custoPorPonto[dificuldade]
### Teste de PeríciatestoBemSucedido(resultado, nivel) =
resultado <= nivel


## Exemplo Completo: Personagem com Esgrima 16

### Setup
- DX = 13
- Esgrima (Difícil, especialidade Espada Longa)
- Pontos investidos: 5 (nível 13 + 5 = 18)
- Com especialização Espada Longa: 18 + 3 = 21 (apenas para espada longa)

### Teste Contra Oponente
- Teste: 1d20 vs. 18 (ou 21 com espada longa)
- Resultado 12: **Sucesso** (12 <= 18)
- Ataque com bônus

## Referência do Livro
Capítulo 4: Perícias | Lista de perícias, custos, atributos base, testes

