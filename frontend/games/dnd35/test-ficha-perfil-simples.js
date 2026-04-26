/**
 * Test: FichaPersonagemController - Perfil Divino
 * 
 * Valida lógica de leitura e hidratação do perfil divino/moral
 * (versão simplificada sem dependências de módulo)
 * 
 * Execução:
 *   node frontend/test-ficha-perfil-simples.js
 */

// ─────────────────────────────────────────────────────────
// Simula Combatente com mapeamento de divindade
// ─────────────────────────────────────────────────────────

class Combatente {
    constructor(data) {
        this.id = data.id;
        this.nome = data.nome;
        this.tipo = data.tipo;
        this.classe = data.classe;
        this.alinhamento = data.alinhamento || '';
        this.divindade = data.divindade || data.deidade || '';  // ✅ com fallback
        this.dominios = data.dominios || '';
    }
}

// ─────────────────────────────────────────────────────────
// Simula FichaPersonagemController Helper
// ─────────────────────────────────────────────────────────

function lerPerfilDivino(combatente) {
    const alinhamento = String(combatente?.alinhamento || '').trim();
    const divindade = String(combatente?.divindade || '').trim();
    
    const dominioParts = String(combatente?.dominios || '')
        .split(',')
        .map(item => item.trim())
        .filter(Boolean);
    
    const dominio1 = dominioParts[0] || '';
    const dominio2 = dominioParts[1] || '';
    
    return { alinhamento, divindade, dominio1, dominio2 };
}

// ─────────────────────────────────────────────────────────
// Testes
// ─────────────────────────────────────────────────────────

let totalTests = 0;
let passedTests = 0;

function assert(actual, expected, message) {
    totalTests++;
    const pass = JSON.stringify(actual) === JSON.stringify(expected);
    if (pass) {
        passedTests++;
        console.log(`✅ ${message}`);
    } else {
        console.error(`❌ ${message}`);
        console.error(`   Expected: ${JSON.stringify(expected)}`);
        console.error(`   Actual: ${JSON.stringify(actual)}`);
    }
}

console.log('🧪 Iniciando testes de Perfil Divino do Clérigo\n');

// ─────────────────────────────────────────────────────────
// Teste 1: Combatente com divindade pré-preenchida
// ─────────────────────────────────────────────────────────
console.log('📋 Teste 1: Mapeamento de divindade no modelo Combatente');
const c1 = new Combatente({
    id: 1,
    nome: 'Teste Clérigo',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Leal e Bom',
    divindade: 'Pelor',
    dominios: 'Bem, Cura',
});

assert(c1.divindade, 'Pelor', 'Divindade mapeada corretamente');
assert(c1.alinhamento, 'Leal e Bom', 'Alinhamento mapeado corretamente');
assert(c1.dominios, 'Bem, Cura', 'Domínios mapeados corretamente');

// ─────────────────────────────────────────────────────────
// Teste 2: Fallback legado para campo 'deidade'
// ─────────────────────────────────────────────────────────
console.log('\n📋 Teste 2: Fallback legado de "deidade" → "divindade"');
const c2 = new Combatente({
    id: 2,
    nome: 'Teste Compatibilidade',
    tipo: 'jogador',
    classe: 'Clerigo',
    deidade: 'Heironeous',  // Campo legado
    alinhamento: 'Leal e Bom',
    dominios: 'Bem, Guerra',
});

assert(c2.divindade, 'Heironeous', 'Fallback para deidade funciona');

// ─────────────────────────────────────────────────────────
// Teste 3: Helper _lerPerfilDivino() com domínios
// ─────────────────────────────────────────────────────────
console.log('\n📋 Teste 3: Helper lerPerfilDivino() com domínios');
const c3 = new Combatente({
    id: 3,
    nome: 'Teste Helper',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Neutro e Bom',
    divindade: 'Ehlonna',
    dominios: 'Bem, Proteção',
});

const perfil = lerPerfilDivino(c3);

assert(perfil.alinhamento, 'Neutro e Bom', 'Helper extrai alinhamento corretamente');
assert(perfil.divindade, 'Ehlonna', 'Helper extrai divindade corretamente');
assert(perfil.dominio1, 'Bem', 'Helper extrai domínio 1 corretamente');
assert(perfil.dominio2, 'Proteção', 'Helper extrai domínio 2 corretamente');

// ─────────────────────────────────────────────────────────
// Teste 4: Helper com domínios vazios
// ─────────────────────────────────────────────────────────
console.log('\n📋 Teste 4: Helper com domínios vazios');
const c4 = new Combatente({
    id: 4,
    nome: 'Teste Vazio',
    tipo: 'jogador',
    classe: 'Mago',  // não é clérigo
    alinhamento: 'Caótico e Bom',
    divindade: '',  // vazio
    dominios: '',  // vazio
});

const perfil2 = lerPerfilDivino(c4);

assert(perfil2.alinhamento, 'Caótico e Bom', 'Helper normaliza alinhamento padrão corretamente');
assert(perfil2.divindade, '', 'Helper normaliza divindade vazia corretamente');
assert(perfil2.dominio1, '', 'Helper normaliza domínio 1 vazio corretamente');
assert(perfil2.dominio2, '', 'Helper normaliza domínio 2 vazio corretamente');

// ─────────────────────────────────────────────────────────
// Teste 5: Persistência após simulação de atualização
// ─────────────────────────────────────────────────────────
console.log('\n📋 Teste 5: Persistência de perfil após mudança');
const c5 = new Combatente({
    id: 5,
    nome: 'Teste Persistência',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Leal e Bom',
    divindade: 'Heironeous',
    dominios: 'Bem, Guerra',
});

// Simula resposta da API após salvar
const c5Updated = new Combatente({
    id: 5,
    nome: 'Teste Persistência',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Leal e Mau',  // alterado
    divindade: 'Hextor',  // alterado
    dominios: 'Mal, Guerra',  // alterado
});

assert(c5Updated.alinhamento, 'Leal e Mau', 'Alinhamento persiste após atualização');
assert(c5Updated.divindade, 'Hextor', 'Divindade persiste após atualização');
assert(c5Updated.dominios, 'Mal, Guerra', 'Domínios persistem após atualização');

// ─────────────────────────────────────────────────────────
// Teste 6: Editor modal round-trip (preenchimento → salva → recarrega)
// ─────────────────────────────────────────────────────────
console.log('\n📋 Teste 6: Round-trip de preenchimento modal');
const c6Original = new Combatente({
    id: 6,
    nome: 'Teste Round-trip',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Leal e Bom',
    divindade: 'St. Cuthbert',
    dominios: 'Bem, Proteção',
});

// Step 1: Abrir modal e ler valores atuais
const step1 = lerPerfilDivino(c6Original);
assert(step1.divindade, 'St. Cuthbert', 'Modal preenche divindade inicial corretamente');

// Step 2: Simular edição do usuário + response da API
const c6Updated = new Combatente({
    id: 6,
    nome: 'Teste Round-trip',
    tipo: 'jogador',
    classe: 'Clerigo',
    alinhamento: 'Leal e Bom',
    divindade: 'Kord',  // editado
    dominios: 'Bem, Força',  // editado
});

// Step 3: Reabre modal e valida persistência
const step3 = lerPerfilDivino(c6Updated);
assert(step3.divindade, 'Kord', 'Modal reabre com divindade atualizada');
assert(step3.dominio1, 'Bem', 'Modal reabre com primeiro domínio correto');
assert(step3.dominio2, 'Força', 'Modal reabre com segundo domínio atualizado');

// ─────────────────────────────────────────────────────────
// Resultado Final
// ─────────────────────────────────────────────────────────
console.log(`\n${'─'.repeat(60)}`);
console.log(`📊 Resultado: ${passedTests}/${totalTests} testes passando`);
console.log(`${'─'.repeat(60)}\n`);

if (passedTests === totalTests) {
    console.log('🎉 Todos os testes passaram!');
    process.exit(0);
} else {
    console.error(`⚠️  ${totalTests - passedTests} teste(s) falharam.`);
    process.exit(1);
}
