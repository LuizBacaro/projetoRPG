# Normas de qualidade do backend (CI / deploy)

Documento **obrigatório** antes de abrir PR ou dar push em branches que disparam o workflow [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) (`feature/**`, `develop`, `main`, etc.).

Objetivo: evitar falhas recorrentes no job **Backend Tests** por formatação (`black`), ordenação de imports (`isort`) e estilo (`flake8`).

---

## 1. O que o CI executa (espelhar localmente)

Diretório de trabalho no runner: `backend/`.

| Ferramenta | Versão (CI) | Comando |
|------------|---------------|---------|
| **black** | 24.10.0 | `black --check --diff app/ tests/` |
| **isort** | 5.13.2 | `isort --check-only --diff --profile black app/ tests/` |
| **flake8** | 7.1.1 | `flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503,E402,E501,E712,F401,F403,F541,F841` |

Instalação (mesmas versões do CI):

```bash
cd backend
pip install black==24.10.0 isort==5.13.2 flake8==7.1.1
```

### Hook git (recomendado — evita falha no deploy)

Instale **uma vez** por clone do repositório:

```bash
make install-hooks
# ou: ./scripts/install-git-hooks.sh
```

Isso configura `core.hooksPath=.githooks` e instala **black** + **isort** (versões em `backend/requirements-dev.txt`).

Antes de cada `git commit`, o script `.githooks/pre-commit` executa automaticamente em ficheiros `.py` staged em `backend/app/` e `backend/tests/`:

1. **black** (formata)
2. **isort** com `--profile black` (ordena imports)
3. Re-adiciona os ficheiros formatados ao stage
4. Valida com `--check` / `--check-only`

Se algo falhar, o commit é bloqueado.

Comandos úteis:

```bash
make pre-commit-run      # formata tudo + valida black/isort
make format-backend      # corrige black + isort manualmente
make ci-backend-lint     # verificação completa (inclui flake8), igual ao CI
```

Alternativa opcional: [pre-commit framework](https://pre-commit.com/) via `.pre-commit-config.yaml` (`pip install pre-commit && pre-commit install`).

### Comando único recomendado (antes de cada push)

Na raiz do repositório:

```bash
make ci-backend-lint
```

Ou, manualmente:

```bash
cd backend
black app/ tests/
isort --profile black app/ tests/
flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503,E402,E501,E712,F401,F403,F541,F841
black --check app/ tests/
isort --check-only --profile black app/ tests/
```

**Regra:** se `black --check` ou `isort --check-only` falhar localmente, o deploy/CI também falhará.

---

## 2. Black — formatação automática

### 2.1 Regras gerais

- Sempre rodar **black** nos ficheiros `.py` alterados em `backend/app/` e `backend/tests/`.
- Não “formatar à mão” linhas longas se o black pode quebrá-las.
- Após editar código, preferir `black <ficheiros>` e rever o diff, em vez de ajustar espaçamento manualmente.

### 2.2 Padrões que o CI reprova (exemplos reais)

| Situação | Incorreto | Correto (black aplica) |
|----------|-----------|-------------------------|
| Linha em branco após docstring do módulo | Docstring + `from __future__` colados | Uma linha vazia entre docstring e imports |
| Dict comprehension longa | Tudo numa linha | Chaves/valores em várias linhas |
| `raise ValueError(...)` longo | String numa linha só | Argumento quebrado com parênteses |
| Import multilinha no fim do ficheiro | `# noqa` na linha seguinte | `# noqa: F401, E402` na **mesma linha** do `import` (ver secção 4) |

### 2.3 Ficheiros sensíveis (companheiro animal e similares)

Estes ficheiros já falharam no CI; ao alterá-los, rodar black de imediato:

- `app/games/dnd35/catalogs/companheiros_especies.py`
- `app/games/dnd35/rules/companheiro_animal.py`
- `app/games/dnd35/services/companheiro_animal_service.py`
- `app/games/dnd35/models/combatente.py`
- `app/games/dnd35/api/v1/companheiros_animais.py`

---

## 3. isort — ordenação de imports (`--profile black`)

O isort deve estar **alinhado ao black**. Nunca usar isort sem `--profile black` neste projeto.

### 3.1 Ordem alfabética

Imports do **mesmo grupo** ficam em ordem **alfabética** pelo nome do módulo/símbolo.

Exemplo em `app/main.py` — `companheiros_animais` vem **antes** de `condicoes` (não depois):

```python
from .games.dnd35.api.v1 import combatentes as dnd35_combatentes
from .games.dnd35.api.v1 import companheiros_animais as dnd35_companheiros_animais
from .games.dnd35.api.v1 import condicoes as dnd35_condicoes
```

Exemplo em `app/models/__init__.py` — `companheiro_animal` **depois** de `combatente` / `combatente_condicao`:

```python
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.combatente_condicao import CombatenteCondicao
from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
```

### 3.2 Imports curtos numa linha

O isort do CI **colapsa** imports pequenos do mesmo módulo numa linha:

```python
# Preferido pelo isort neste repo
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
```

Evitar quebrar em multilinha sem necessidade (o CI reformata).

### 3.3 Repositories e services em `app/core/deps/dnd35.py`

Ao adicionar repositório ou service novo, inserir na posição **alfabética**:

- `companheiro_animal_repository` entre `combatente_repository` e `condicao_repository`
- `companheiro_animal_service` entre `combatente_service` e `condicao_service`

---

## 4. Imports tardios e mappers SQLAlchemy

### 4.1 `app/main.py` — ordem dos models

Ao registar models para o Alembic/mapper, imports em **ordem alfabética** pelo nome do ficheiro, com atenção a dependências de relationship:

- `companheiro_animal` importado **antes** de `combatente` quando `Combatente` referencia `CompanheiroAnimal` (evita erro de mapper no startup).

Padrão atual (manter ao evoluir):

```python
from .games.dnd35.models import companheiro_animal as companheiro_animal_model
from .games.dnd35.models import combatente as combatente_model
```

(Ordem alfabética: `companheiro` < `combatente`.)

### 4.2 `combatente.py` — import após a classe

Relação 1:1 com `CompanheiroAnimal` exige import **no fim** do ficheiro. Formato exigido pelo **black + isort**:

```python
# Registro do mapper para relationship("CompanheiroAnimal") — import após a classe.
from app.games.dnd35.models.companheiro_animal import (  # noqa: F401, E402
    CompanheiroAnimal,
)
```

- `# noqa: F401, E402` na **linha do `import`**, não na linha do parêntese de fecho.
- Não remover este import: sem ele, `POST /combate/iniciar` e carregamento de combatentes podem falhar com erro de mapper.

### 4.3 Checklist ao adicionar model com `relationship()`

1. Criar model em `app/games/dnd35/models/`.
2. Exportar em `app/models/__init__.py` (ordem alfabética).
3. Importar no `app/main.py` (ordem alfabética / dependência de mapper).
4. Se houver `relationship("OutroModel")`, garantir que `OutroModel` está importado no registry (import tardio no fim do ficheiro, se necessário).
5. Rodar `black` + `isort --profile black` nos ficheiros tocados.

---

## 5. flake8 — avisos comuns

| Código | Significado | Ação |
|--------|-------------|------|
| E402 | import não no topo | Aceito com `# noqa: E402` em imports tardios de mapper |
| F401 | import não usado | Aceito com `# noqa: F401` em imports só para registrar mapper |
| E501 | linha longa | Black costuma resolver; flake8 ignora E501 no CI |
| F841 | variável não usada | Remover ou usar a variável |

---

## 6. Checklist obrigatório (desenvolvedor e agente)

Antes de **commit / push / PR**:

- [ ] `cd backend && black app/ tests/` (ou `make format-backend`)
- [ ] `cd backend && isort --profile black app/ tests/`
- [ ] `make ci-backend-lint` passou sem erro
- [ ] `cd backend && python -m pytest tests/ -q --ignore=tests/e2e` (testes das áreas alteradas, no mínimo)
- [ ] Novos imports em `main.py`, `models/__init__.py`, `core/deps/dnd35.py` em ordem alfabética
- [ ] Se alterou `relationship()` em models, validou ordem de import no `main.py` e import tardio com `# noqa`

**Agentes de IA:** após editar qualquer `.py` em `backend/`, executar os comandos acima antes de considerar a tarefa concluída. Não assumir que “o código compila” implica que o CI de lint passa.

---

## 7. Integração com a governança do projeto

| Documento | Uso |
|-----------|-----|
| [AGENTS.md](../AGENTS.md) | Fonte normativa principal — referencia este ficheiro |
| [.github/instructions/backend.instructions.md](../.github/instructions/backend.instructions.md) | Regras aplicadas a `backend/**/*.py` |
| [passo-a-passo-ci-cd.md](../passo-a-passo-ci-cd.md) | Visão da pipeline e deploy |
| [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | Definição exata dos comandos e versões |

---

## 8. Histórico de falhas que motivaram este documento

Registro para não repetir no deploy:

1. **black** — 4 ficheiros do módulo companheiro animal (`companheiros_especies.py`, `combatente.py`, `companheiro_animal.py`, `companheiro_animal_service.py`): docstrings, dict comprehension, imports multilinha.
2. **isort** — 6 ficheiros: ordem de `companheiros_animais` vs `condicoes` em `main.py`; ordem de models; imports colapsados em `companheiros_animais.py` e testes; `# noqa` na linha correta em `combatente.py`; ordem em `core/deps/dnd35.py`.

Sempre que o CI falhar em `Lint and format code`, copiar o diff do log, aplicar `black` + `isort --profile black` localmente e commitar **apenas** as alterações de formatação (ou no mesmo commit da feature, já formatado).

---

*Última atualização: maio/2026 — alinhado a `ci.yml` (black 24.10.0, isort 5.13.2, flake8 7.1.1).*
