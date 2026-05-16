# Fluxo de especificação mínima (SDD leve)

Objetivo: ter **fonte de verdade curta e viva** para contratos e comportamento, sem burocracia de documentos longos que não se atualizam.

Este fluxo **complementa** [AGENTS.md](../AGENTS.md), [.github/instructions](../.github/instructions) e as skills em `.cursor/skills/` quando o domínio for RPG (regras de livro).

---

## 1. Issue ou PR (sempre que houver ticket)

Incluir em **5–12 linhas**:

- **Comportamento esperado** (o que o utilizador ou sistema faz).
- **Fora de escopo** explícito (opcional, mas útil em regras de jogo).
- **Critérios de aceite** em lista numerada (3–7 itens verificáveis).
- **Riscos / compatibilidade** (breaking change em API, dados legados, multi-jogo).

Não é obrigatório ficheiro `.md` separado por tarefa pequena; o corpo do PR/issue basta.

---

## 2. Backend (nova rota ou mudança de contrato)

| Obrigatório | Notas |
|-------------|--------|
| **Schemas Pydantic** alinhados ao request/response reais | FastAPI já expõe OpenAPI; manter nomes e tipos coerentes. |
| **Pelo menos um teste** que exercite o caminho feliz (e erro esperado se for regra crítica) | Preferir `tests/` existentes com SQLite em memória quando aplicável. |
| **Sem breaking change** em JSON público sem decisão explícita | Se inevitável: versionar rota ou documentar migração no PR. |

Rotas finas, regra em `services`, persistência em `repositories` — ver [backend.instructions.md](../.github/instructions/backend.instructions.md).

---

## 3. Frontend (nova integração ou alteração de payload)

| Obrigatório | Notas |
|-------------|--------|
| **Chamadas via `getApiUrl()`** | Sem URL hardcoded. |
| **Alinhar campos** ao schema/contrato backend | Nomes e tipos iguais aos do OpenAPI ou ao teste de referência. |
| **Cache-busting `?v=`** em HTML quando alterar JS/CSS servido por página | Ver convenção em [AGENTS.md](../AGENTS.md). |

Se a feature for só visual sem mudança de contrato, critérios de aceite no PR focam em UI e regressões visuais.

---

## 4. Regras de jogo (D&D 3.5, Tormenta, GURPS, etc.)

| Quando | O quê |
|--------|--------|
| Mecânica nova ou ambígua | Usar [.github/prompts/levantamento-requisitos-rpg.prompt.md](../.github/prompts/levantamento-requisitos-rpg.prompt.md) ou agente **RPG Requirements Analyst** antes de codar em massa. |
| Domínio já coberto | Atualizar ou referenciar **skill** ou **doc** existente (ex.: conjuração, progressão, GURPS) em vez de duplicar parágrafos no código. |

Separação útil: **regra da fonte** (livro) vs **interpretação de produto** (o que a Arena implementa) — o PR pode ter uma linha cada.

---

## 5. ADR (Architecture Decision Record)

Criar ficheiro curto em `docs/adr/` **só** quando:

- mudar modelo de dados ou contrato multi-serviço de forma difícil de reverter;
- introduzir padrão novo (ex.: outro jogo no `games_catalog`, outro storage);
- decisão de produto que vá contra uma convenção já documentada.

Formato sugerido: `docs/adr/0001-titulo-kebab.md` com contexto, decisão e consequências (meia página).

---

## 6. O que não é obrigatório

- Especificação formal completa antes de qualquer linha de código em spikes exploratórios (documentar decisão no fim do spike).
- Duplicar o mesmo texto em `AGENTS.md`, README e doc de feature — **um sítio canónico** + links.

---

## Resumo executável

**Nova rota API:** schemas + 1 teste + critérios de aceite no PR.  
**Nova tela ou serviço JS:** `getApiUrl` + alinhamento ao contrato + `?v=` se aplicável.  
**Regra de livro:** levantamento RPG ou skill/doc atualizada.  
**Decisão estrutural:** ADR curto em `docs/adr/`.

Manter isto **leve** evita specs mortas e ainda dá rastreabilidade para humanos e agentes.
