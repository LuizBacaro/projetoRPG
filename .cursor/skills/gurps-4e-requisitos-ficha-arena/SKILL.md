---
name: gurps-4e-requisitos-ficha-arena
description: Requisitos funcionais GURPS 4ª ed. (Lite + Personagens) para ficha digital e arena; contrato com o código em backend/frontend GURPS. Usar ao planejar ficha, combate, perícias, migração de regras ou prompts de agente GURPS.
---

# GURPS 4E — Requisitos para ficha e arena (Arena TTRPG)

## Fontes e método

| Fonte | Papel |
|--------|--------|
| `GURPS 4E - Módulo Básico - Lite.pdf` | Regras condensadas: testes 3d6, combate Lite, dano, armaduras simplificadas, lista curta de perícias/vantagens. |
| `GURPS 4E - Módulo Básico - Personagens.pdf` | Livro completo: criação por pontos, planilha, listas extensas, opções avançadas. |

**Extração usada para este levantamento:** texto nativo via `pdftotext -layout` (confiável para índice e mecânica; diagramas/tabelas complexas podem exigir conferência visual no PDF).

**Propriedade intelectual:** não copiar passagens longas dos PDFs em issues/PRs; usar os livros como referência na mesa e este skill como **checklist de comportamento** do software.

**Planilha “Ficha Aprimorada”:** `GURPS 4E - Ficha de Personagem (Aprimorada 1).pdf` no workspace — útil como **lista de campos** da ficha física; cruzar com `extras_json` e colunas SQL em `GurpsPersonagem`.

---

## Princípios mecânicos (Lite) que o software deve respeitar

1. **Teste de habilidade:** 3d6; sucesso se total ≤ nível efetivo (perícia ou atributo); margem de sucesso/falha; 3–4 sucesso decisivo; 17–18 falha crítica (com ressalvas por NH); modificadores somam ao **alvo**, não aos dados.
2. **Dano:** expressão `Nd + bônus`; tipos GDP (golpe ponta) e BAL (balanço) derivados da **ST** por tabela; RD subtrai do dano recebido (combate Lite).
3. **Características secundárias (derivadas dos atributos na Lite):** PV base = ST; PF base = HT; Vontade base = IQ; Percepção base = IQ; Velocidade básica = (HT+DX)/4 (frações importam); deslocamento básico relacionado à velocidade básica; **Esquiva** = Velocidade básica + 3 (ignorar fração na esquiva).
4. **Combate por segundo / turno:** ordem de ação por **Velocidade básica** (maior primeiro; empates DX, depois sorteio); turno ≈ 1 s; manobras (Fazer Nada, Ataque, Defesa Total, Ataque Total, Deslocamento, Mudança de Posição, Apontar, Preparar, Concentrar, etc.) alteram ataques, defesas ativas e movimento.
5. **Ataque:** jogada de ataque = teste contra NH efetivo da arma/perícia; depois defesa ativa do alvo (Esquiva, Aparar, Bloqueio); se falhar defesa, avaliar dano.
6. **Defesas ativas:** valores na ficha; modificadores por posição (em pé, agachado, etc. na Lite); múltiplas defesas com penalidades cumulativas (regra completa no livro; Lite resume o fluxo).
7. **Lesão e fadiga:** redução de PV/PF; efeitos de 0 ou negativos (Lite: choque, desmaio, morte — há trechos específicos no PDF).

O **Módulo Personagens** amplia: custos em pontos, centenas de vantagens/desvantagens/perícias, equipamento detalhado — o produto pode **fasear**: Lite jogável primeiro, depois paridade com o capítulo correspondente do livro grande.

---

## Requisitos funcionais — Criação e ficha (RF-F)

- **RF-F01** — O sistema deve permitir definir **ST, DX, IQ, HT** com custo em pontos e valor final, coerente com a construção por pontos (limites de campanha configuráveis no futuro).
- **RF-F02** — Calcular e exibir **PV máximo** e **PF (fadiga) máximo** alinhados à regra base (Lite: PV = ST, PF = HT, salvo vantagens/modificadores).
- **RF-F03** — Calcular e persistir **Vontade** e **Percepção**; default IQ quando não sobrescrito.
- **RF-F04** — Calcular **Velocidade básica** como (HT+DX)/4 sem arredondamento indevido; **Deslocamento** compatível com a regra usada na campanha (Lite: partir da velocidade básica menos fração; exibir m/s ou equivalente na UI).
- **RF-F05** — Calcular **dano GDP e BAL** a partir da ST via **tabela de dano** do Lite; exibir na ficha (ex.: `1d/2d-1`).
- **RF-F06** — Calcular **Esquiva** = parte inteira ou regra Lite (VB + 3, ignorando fração de VB para esquiva).
- **RF-F07** — Registrar **perícias** com NH, tipo (E/M/H), relação opcional com atributo base; custo em pontos quando em modo construção.
- **RF-F08** — Registrar **vantagens** e **desvantagens** (nome + custo); validar pré-requisitos quando o catálogo estiver modelado (Personagens).
- **RF-F09** — Suportar **Combate sem armas** mínimo (soco/chute) com dano derivado e NH (DX ou Briga/Caratê quando existir no catálogo).
- **RF-F10** — **Defesas ativas:** Esquiva, Aparar, Bloqueio (e escudo RD) — valores base + modificadores de campanha; bloqueio pode ser texto (ex.: escudo +2) até virar objeto estruturado.
- **RF-F11** — **Equipamento:** armas com dano, alcance, tipo de dano; armadura com RD; compatível com listas Lite primeiro.
- **RF-F12** — **extras_json** documentado: encargos, localizações de acerto, armas rápidas, notas — não substituir campos canônicos; migrar para colunas quando um campo for estável.

---

## Requisitos funcionais — Resolução e dados (RF-R)

- **RF-R01** — Serviço ou utilitário de **rolagem 3d6** com opção de mostrar margem, sucesso decisivo e falha crítica segundo Lite.
- **RF-R02** — Função de **nível efetivo** = NH base + modificadores situacionais (penumbra, posição, etc.) para exibir alvo do teste.
- **RF-R03** — Parser ou tabela para **rolar dano** (`Nd+M`) e aplicar RD mínimo onde couber.

---

## Requisitos funcionais — Arena de combate (RF-A)

- **RF-A01** — **Ordem de combate:** iniciativa da arena deve refletir **Velocidade básica** (e desempates DX, depois aleatório), não um campo “iniciativa” arbitrário persistido, **a menos** que a campanha use regra opcional — documentar decisão de produto.
- **RF-A02** — **Turno:** um combatente escolhe **manobra** por turno; estado atual da manobra afeta defesas ativas e movimento até o próximo turno.
- **RF-A03** — **Ataque:** escolher alvo em alcance; rolar ataque vs NH; alvo rola defesa ativa; se falhar, aplicar dano aos PV (e efeitos).
- **RF-A04** — **Múltiplas defesas:** aplicar penalidade cumulativa conforme regra GURPS usada na mesa (parâmetro configurável se necessário).
- **RF-A05** — **Posição corporal:** mínimo Lite (em pé, agachado, deitado) com modificadores de ataque/defesa/alvo/movimento.
- **RF-A06** — **Fadiga** em combate: esforço, surtos opcionais — fase 2.
- **RF-A07** — **Condições:** atordoado, agachado, etc., com efeito em manobra “Fazer Nada” e recuperação por HT (Lite).

---

## Cobertura atual (visão de alto nível — verificar no código ao implementar)

| Área | Estado típico no repo | Lacuna principal |
|------|------------------------|------------------|
| Atributos ST/DX/IQ/HT + VON/PER | Modelo + ficha | RD completo de armaduras; dano GDP/BAL automático por ST |
| PV/PF | Campos + arena mostra PV/FAD | PF nome “fadiga”; regras de esgotamento |
| Vel / deslocamento | Decimal no modelo | Exibição e uso consistente com Lite |
| Esquiva / aparar / bloqueio | Campos | Recalcular esquiva a partir de VB; aparar com perícia de arma |
| Perícias / V / D | Tabelas filhas | Catálogo Lite → depois livro completo |
| Ordem na arena | `iniciativa` numérica | Migrar para **Basic Speed** + desempate |
| Manobras | Não | Modelar estado de combate por turno |
| Rolagens 3d6 | Parcial / UI placeholder | Serviço único de teste |

---

## Uso como prompt de agente

Colar no agente especializado:

> Você implementa GURPS 4E no Arena TTRPG. Siga o skill `gurps-4e-requisitos-ficha-arena`: priorize **GURPS Lite** para combate e ficha mínima; estenda para **Módulo Personagens** quando o ticket pedir. Não copie texto dos PDFs. Ao alterar ficha, mantenha contrato API (`GurpsPersonagem*`) e migrações Alembic. Para arena, alinhe ordem de turno à **Velocidade básica** e introduza **manobras** antes de regras opcionais avançadas.

---

## Próximos passos sugeridos (produto)

1. Decisão explícita: **iniciativa** = Basic Speed (padrão GURPS) vs manter campo legado com sincronização.
2. Implementar **tabela de dano ST → thr/swing** e exibição na ficha.
3. **Manobra atual** no estado de combate GURPS + efeito em defesas.
4. **Motor de teste 3d6** reutilizável (front + opcional back).
5. Importar ou codificar **subconjunto Lite** de perícias/armas/armaduras.
