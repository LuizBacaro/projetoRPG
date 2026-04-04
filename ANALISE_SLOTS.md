# 📚 ANÁLISE: SPELL SLOTS NO GRIMÓRIO

## 1️⃣ COMO CARREGA OS MAGIAS_SLOTS

### Frontend - FichaPersonagemController.js
```javascript
// Linha 38: Carrega combatente com magias_slots
this.combatente = await this.combatenteService.obterCombatente(id);
// Retorna: { ..., magias_slots: [{id, nivel, total, usados}, ...] }

// Linha 53: Renderiza slots na ficha
this.renderizarSlotsDeMapia();
```

### Backend - Endpoint
```
GET /api/v1/combatentes/{combatente_id}/magias

ataques.py (54-61) → AtaqueService.listar_magias()
                  → AtaqueRepository.listar_magias_por_combatente()
                  → SELECT * FROM magias_slots WHERE combatente_id = ?
```

### Modelo BD - ataque.py
```python
class MagiaSlot(Base):
    __tablename__ = "magias_slots"
    id = Column(Integer, primary_key=True)
    combatente_id = Column(Integer, ForeignKey("combatentes.id"))
    nivel = Column(Integer)  # 0-9 (0=truques, 1-9=níveis)
    total = Column(Integer)  # slots disponíveis
    usados = Column(Integer) # slots gastos hoje
```

---

## 2️⃣ FILTRO POR CLASSE

### ✅ FRONTEND - MagiaService.js (Linhas 30-40)
```javascript
_normalizarClasse(classe) {
    let classNorm = classe.toUpperCase().trim();
    if (classNorm === 'FEITICEIRO') {
        classNorm = 'MAGO';  // ✅ Mapeia!
    }
    return classNorm;
}

async listarPorClasse(classe) {
    const classeNormalizada = this._normalizarClasse(classe);
    // GET /magias/?classe=MAGO&limit=500
}
```

### ❌ BACKEND - magias.py (Linhas 36-37)
```python
if classe:
    query = query.filter(Magia.classe == classe)  # ← SEM MAPEAMENTO!
```

### 🔴 PROBLEMA
Se BD tem `classe='FEITICEIRO'` mas FE envia `classe=MAGO` → retorna 0 resultados

### 🔧 SOLUÇÃO
Adicionar em `magias.py` (após linha 36):
```python
if classe:
    classe_norm = classe.upper()
    if classe_norm == 'FEITICEIRO':
        classe_norm = 'MAGO'  # ← Mapeamento!
    query = query.filter(Magia.classe == classe_norm)
```

---

## 3️⃣ ENDPOINTS RELACIONADOS

| Endpoint | Tipo | Arquivo | Função |
|----------|------|---------|--------|
| `/combatentes/{id}/magias` | GET | ataques.py:54 | Listar slots |
| `/combatentes/{id}/magias` | PUT | ataques.py:64 | Salvar slots (bulk) |
| `/magias_slots/{id}/usados` | PATCH | ataques.py:76 | Atualizar usados |
| `/magias-preparadas/{id}` | GET | magias_preparadas.py:35 | Listar preparadas |
| `/magias-preparadas/{id}` | POST | magias_preparadas.py:45 | Preparar magia |
| `/magias/?classe=MAGO` | GET | magias.py:18 | Buscar magias por classe |

---

## 4️⃣ FLUXO COMPLETO: ABRIR GRIMÓRIO

```
┌─ PASSO 1: Inicializar ─────────────────────────────┐
│ GrimorioController(combatente, token, magiaService) │
│ this.classe = this._normalizarClasse(combatente.classe)
└───────────────────────────────────────────────────┘

┌─ PASSO 2: Abrir Grimório ─────────────────────────┐
│ abrirGrimorio()                                    │
│   if (!this._carregado) {                          │
│     await this._carregarMagias()                   │
│     await this._carregarPreparadas()               │
│     this._calcularSlotsDisponiveis()               │
│     this._carregado = true                         │
│   }                                                │
│   this._renderizarPainelSlots()                    │
│   this._renderizarFiltroEscolas()                  │
│   this._renderizarLista()                          │
└───────────────────────────────────────────────────┘

┌─ PASSO 3: Carregar Magias ────────────────────────┐
│ async _carregarMagias()                            │
│ this.magias = await magiaService.listarPorClasse()│
│ // GET /magias/?classe=MAGO → [Bola de Fogo, ...] │
└───────────────────────────────────────────────────┘

┌─ PASSO 4: Carregar Preparadas ────────────────────┐
│ async _carregarPreparadas()                        │
│ // GET /magias-preparadas/{combatente_id}         │
│ this.preparadas = Set([magia_id, ...])             │
│ this.usadas = Set([magia_id, ...])  // usadas hoje │
└───────────────────────────────────────────────────┘

┌─ PASSO 5: Calcular Slots D&D 3.5 ─────────────────┐
│ _calcularSlotsDisponiveis()                        │
│ tabelaClasse = TABELA_MAGIAS_DIA['Mago'][nivel]   │
│ // [4, 5, 4, 2, 1, ...] para nível 10              │
│                                                   │
│ atributo = combatente.inteligencia (para Mago)    │
│ bonus = (atributo - 10) / 2                        │
│                                                   │
│ Para cada nível:                                  │
│   total = base + bonus                             │
│   preparadas = count(this.preparadas com nível)   │
│   usadas = count(this.usadas com nível)           │
│   disponivel = total - preparadas                 │
│                                                   │
│ Result: {                                          │
│   0: {total: 4, preparadas: 0, usadas: 0, ...},   │
│   1: {total: 6, preparadas: 2, usadas: 1, ...},   │
│   3: {total: 2, preparadas: 2, usadas: 0, ...},   │
│ }                                                  │
└───────────────────────────────────────────────────┘

┌─ PASSO 6: User Clica em Magia ────────────────────┐
│ [Click em "Bola de Fogo" - nível 3]               │
│   ↓                                                │
│ _togglePreparacao(magiaId, nivelMagia)             │
│   ↓                                                │
│ if (preparadas.has(magiaId)) {                     │
│   _desmarcarMagia()  // DELETE                     │
│ } else {                                           │
│   _prepararMagia()   // POST                       │
│ }                                                  │
└───────────────────────────────────────────────────┘

┌─ PASSO 7: Validar ────────────────────────────────┐
│ async _prepararMagia(magiaId, nivelMagia)          │
│ const slot = slotsDisponiveis[nivelMagia]          │
│                                                   │
│ if (nivelMagia === 0) {  // Truques OK             │
│   await _persistirPreparacao()                     │
│ } else if (!slot || slot.disponivel <= 0) {       │
│   mostrarToast('Slots esgotados!')                 │
│ } else {                                           │
│   await _persistirPreparacao()                     │
│ }                                                  │
└───────────────────────────────────────────────────┘

┌─ PASSO 8: Persistir ────────────────────────────┐
│ async _persistirPreparacao(magiaId, nivelMagia)  │
│ POST /magias-preparadas/{combatente_id}          │
│ body: { magia_id: magiaId, nivel_slot: nivelMagia}
│                                                  │
│ Backend cria:                                    │
│ MagiaPreparada(                                  │
│   combatente_id: 5,                              │
│   magia_id: 5,                                   │
│   nivel_slot: 3,                                 │
│   usada: False                                   │
│ )                                                │
└──────────────────────────────────────────────────┘

┌─ PASSO 9: Atualizar UI ───────────────────────────┐
│ this.preparadas.add(magiaId)                       │
│ this._calcularSlotsDisponiveis()  // recalcula    │
│ this._renderizarPainelSlots()     // atualiza barra
│ this._atualizarCard()             // atualiza card │
│ mostrarToast('✅ Magia preparada!')                │
└───────────────────────────────────────────────────┘
```

---

## 5️⃣ ARQUIVOS CRÍTICOS

### Backend (Python)
- `app/api/v1/ataques.py` (54-85) - Endpoints
- `app/api/v1/magias.py` (18-45) - **← FALTA MAPEAMENTO AQUI**
- `app/services/ataque_service.py` (40-56) - Serviço
- `app/repositories/ataque_repository.py` (50-85) - Queries
- `app/models/ataque.py` (25-36) - MagiaSlot model

### Frontend (JavaScript)
- `js/controllers/GrimorioController.js` (1-1039) - Grimório completo
- `js/services/MagiaService.js` (1-156) - **✅ JÁ TEM MAPEAMENTO**
- `js/services/AtaqueService.js` (1-90) - HTTP calls
- `js/controllers/FichaPersonagemController.js` (1-~800) - Renderizar slots
- `js/models/Combatente.js` (1-47) - Model

---

## 🎯 RESUMO FINAL

| Item | Status | Local |
|------|--------|-------|
| Carregar magias_slots | ✅ OK | FE: GET /combatentes/{id} |
| Renderizar slots na ficha | ✅ OK | FE: renderizarSlotsDeMapia() |
| Abrir Grimório | ✅ OK | FE: GrimorioController |
| Carregar magias por classe | ✅ Parcial | FE normaliza ✅, BE não ❌ |
| Selecionar/preparar magia | ✅ OK | POST /magias-preparadas/ |
| Calcular slots D&D | ✅ OK | TABELA_MAGIAS_DIA + bônus |
| **Feiticeiro → Mago** | ❌ Incompleto | FE OK, BE não mapeia |

---

## 🔧 AÇÃO NECESSÁRIA

**Adicionar mapeamento em `/backend/app/api/v1/magias.py` após linha 36:**

```python
if classe:
    classe_norm = classe.upper()
    if classe_norm == 'FEITICEIRO':
        classe_norm = 'MAGO'
    query = query.filter(Magia.classe == classe_norm)
```

Isso garante que Feiticeiro sempre retorna as magias de Mago! ✅

