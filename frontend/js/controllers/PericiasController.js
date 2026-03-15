/**
 * PericiasController.js
 * SRP: Gerenciar página dedicada de perícias
 * SOLID: Single Responsibility, modular, reutilizável
 */

// ── Database de Perícias (D&D 3.5) ──
const PERICIAS_DATABASE = {
    "Força": [
        { id: "escalar", nome: "Escalar", atributo: "For", cd_basica: 10 },
        { id: "natacao", nome: "Natação", atributo: "For", cd_basica: 10 },
        { id: "saltar", nome: "Saltar", atributo: "For", cd_basica: 10 }
    ],
    "Destreza": [
        { id: "abrir_fechaduras", nome: "Abrir Fechaduras", atributo: "Des", cd_basica: 10 },
        { id: "acrobacia", nome: "Acrobacia", atributo: "Des", cd_basica: 10 },
        { id: "arte_fuga", nome: "Arte de Fuga", atributo: "Des", cd_basica: 10 },
        { id: "cavalgar", nome: "Cavalgar", atributo: "Des", cd_basica: 10 },
        { id: "equilibrio", nome: "Equilíbrio", atributo: "Des", cd_basica: 10 },
        { id: "esconder_se", nome: "Esconder-se", atributo: "Des", cd_basica: 10 },
        { id: "furtividade", nome: "Furtividade", atributo: "Des", cd_basica: 10 },
        { id: "prestigitacao", nome: "Prestigitação", atributo: "Des", cd_basica: 10 },
        { id: "usar_cordas", nome: "Usar Cordas", atributo: "Des", cd_basica: 10 }
    ],
    "Constituição": [
        { id: "resistencia", nome: "Resistência", atributo: "Con", cd_basica: 10 }
    ],
    "Inteligência": [
        { id: "avaliacao", nome: "Avaliação", atributo: "Int", cd_basica: 10 },
        { id: "decifrar_escrita", nome: "Decifrar Escrita", atributo: "Int", cd_basica: 10 },
        { id: "conh_arcano", nome: "Conh. Arcano", atributo: "Int", cd_basica: 10 },
        { id: "conh_dungeon", nome: "Conh. Dungeon", atributo: "Int", cd_basica: 10 },
        { id: "conh_historia", nome: "Conh. História", atributo: "Int", cd_basica: 10 },
        { id: "conh_local", nome: "Conh. Local", atributo: "Int", cd_basica: 10 },
        { id: "conh_natureza", nome: "Conh. Natureza", atributo: "Int", cd_basica: 10 },
        { id: "conh_nobreza", nome: "Conh. Nobreza", atributo: "Int", cd_basica: 10 },
        { id: "conh_planos", nome: "Conh. Planos", atributo: "Int", cd_basica: 10 },
        { id: "conh_religiao", nome: "Conh. Religião", atributo: "Int", cd_basica: 10 }
    ],
    "Sabedoria": [
        { id: "curar", nome: "Curar", atributo: "Sab", cd_basica: 10 },
        { id: "escuta", nome: "Escuta", atributo: "Sab", cd_basica: 10 },
        { id: "jogo_maos", nome: "Jogo de Mãos", atributo: "Sab", cd_basica: 10 },
        { id: "percepcao", nome: "Percepção", atributo: "Sab", cd_basica: 10 },
        { id: "profissao", nome: "Profissão", atributo: "Sab", cd_basica: 10 },
        { id: "sobrevivencia", nome: "Sobrevivência", atributo: "Sab", cd_basica: 10 }
    ],
    "Carisma": [
        { id: "atuacao", nome: "Atuação", atributo: "Car", cd_basica: 10 },
        { id: "blefar", nome: "Blefar", atributo: "Car", cd_basica: 10 },
        { id: "diplomacia", nome: "Diplomacia", atributo: "Car", cd_basica: 10 },
        { id: "disfarce", nome: "Disfarce", atributo: "Car", cd_basica: 10 },
        { id: "enganar", nome: "Enganar", atributo: "Car", cd_basica: 10 },
        { id: "gather_info", nome: "Reunir Informações", atributo: "Car", cd_basica: 10 },
        { id: "intimidar", nome: "Intimidar", atributo: "Car", cd_basica: 10 },
        { id: "manipulacao", nome: "Manipulação", atributo: "Car", cd_basica: 10 }
    ]
};

// ── Estado Global ──
let combatenteEmEdicao = null;
let periciasSelecionadas = new Set();
let todasAsPericias = [];

/**
 * Inicializa a página de perícias
 */
function inicializarPericiasPage() {
    extrairDadosDaURL();
    renderizarPericiasModal();
    setupEventListeners();
    atualizarContador();
}

/**
 * Extrai dados do combatente da URL (query params)
 */
function extrairDadosDaURL() {
    const params = new URLSearchParams(window.location.search);
    
    const id = params.get('combatente_id');
    const nome = params.get('nome') || 'Combatente';
    const tipo = params.get('tipo') || 'jogador';
    const pericias = params.get('pericias') ? JSON.parse(decodeURIComponent(params.get('pericias'))) : [];

    combatenteEmEdicao = { id, nome, tipo };
    periciasSelecionadas = new Set(pericias);

    // Atualizar header
    document.getElementById('nomeCombatente').textContent = nome;
    document.getElementById('tipoCombatente').textContent = tipo.charAt(0).toUpperCase() + tipo.slice(1);
}

/**
 * Renderiza as perícias agrupadas por atributo
 */
function renderizarPericiasModal() {
    const container = document.getElementById('periciasPorAtributo');
    const semResultados = document.getElementById('semPericias');

    container.innerHTML = '';
    todasAsPericias = [];

    Object.entries(PERICIAS_DATABASE).forEach(([atributo, pericias]) => {
        todasAsPericias.push(...pericias);

        const grupoHTML = `
            <div class="pericia-atributo-group">
                <div class="pericia-atributo-header" onclick="toggleGrupoPericia(this)">
                    <span>${atributo}</span>
                    <span class="pericia-atributo-toggle">▶</span>
                </div>
                <div class="pericia-atributo-content">
                    ${pericias.map(pericia => `
                        <div class="pericia-item ${periciasSelecionadas.has(pericia.id) ? 'selected' : ''}" 
                             onclick="togglePericia(event, '${pericia.id}')">
                            <input 
                                type="checkbox" 
                                id="pericia_${pericia.id}"
                                data-id="${pericia.id}"
                                ${periciasSelecionadas.has(pericia.id) ? 'checked' : ''}
                                onchange="atualizarPericia('${pericia.id}', this.checked)">
                            <label for="pericia_${pericia.id}">${pericia.nome}</label>
                            <span class="pericia-info">${pericia.atributo}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML += grupoHTML;
    });

    semResultados.style.display = todasAsPericias.length === 0 ? 'block' : 'none';
}

/**
 * Toggle expandir/colapsar grupo de perícias
 */
function toggleGrupoPericia(elemento) {
    const content = elemento.nextElementSibling;
    const toggle = elemento.querySelector('.pericia-atributo-toggle');

    content.classList.toggle('collapsed');
    toggle.classList.toggle('collapsed');
}

/**
 * Toggle pericia (clicando no item inteiro)
 */
function togglePericia(event, periciaId) {
    const checkbox = document.getElementById(`pericia_${periciaId}`);
    checkbox.checked = !checkbox.checked;
    atualizarPericia(periciaId, checkbox.checked);
}

/**
 * Atualiza pericia selecionada
 */
function atualizarPericia(periciaId, checked) {
    const item = document.querySelector(`[data-id="${periciaId}"]`).closest('.pericia-item');

    if (checked) {
        periciasSelecionadas.add(periciaId);
        item.classList.add('selected');
    } else {
        periciasSelecionadas.delete(periciaId);
        item.classList.remove('selected');
    }

    atualizarContador();
}

/**
 * Atualiza contador de perícias selecionadas
 */
function atualizarContador() {
    const contador = document.getElementById('totalPericiasSelect');
    contador.textContent = periciasSelecionadas.size;
}

/**
 * Setup de event listeners
 */
function setupEventListeners() {
    // Botão voltar
    document.getElementById('btnVoltar').addEventListener('click', () => {
        window.history.back();
    });

    // Botão cancelar
    document.getElementById('btnCancelarPericias').addEventListener('click', () => {
        window.history.back();
    });

    // Botão limpar seleção
    document.getElementById('btnLimparPericias').addEventListener('click', () => {
        limparSelecao();
    });

    // Botão salvar
    document.getElementById('btnSalvarPericias').addEventListener('click', () => {
        salvarPericias();
    });

    // Busca/filtro
    document.getElementById('inputBuscaPericia').addEventListener('input', (e) => {
        filtrarPericias(e.target.value);
    });
}

/**
 * Limpa a seleção de perícias
 */
function limparSelecao() {
    periciasSelecionadas.clear();
    document.querySelectorAll('.pericia-item').forEach(item => {
        item.classList.remove('selected');
        const checkbox = item.querySelector('input[type="checkbox"]');
        if (checkbox) checkbox.checked = false;
    });
    atualizarContador();
    mostrarToast('🗑️ Seleção limpa', 'info');
}

/**
 * Filtra perícias por busca
 */
function filtrarPericias(termo) {
    const termo_lower = termo.toLowerCase();
    const itens = document.querySelectorAll('.pericia-item');
    const grupos = document.querySelectorAll('.pericia-atributo-group');

    let algumVisivel = false;

    grupos.forEach(grupo => {
        const itensGrupo = grupo.querySelectorAll('.pericia-item');
        let grupoTemVisivel = false;

        itensGrupo.forEach(item => {
            const nome = item.querySelector('label').textContent.toLowerCase();
            const match = nome.includes(termo_lower);
            item.style.display = match ? 'flex' : 'none';
            if (match) grupoTemVisivel = true;
        });

        grupo.style.display = grupoTemVisivel ? 'block' : 'none';
        if (grupoTemVisivel) algumVisivel = true;
    });

    document.getElementById('periciasPorAtributo').style.display = algumVisivel ? 'flex' : 'none';
    document.getElementById('semPericias').style.display = algumVisivel ? 'none' : 'block';
}

/**
 * Salva perícias selecionadas
 */
function salvarPericias() {
    if (!combatenteEmEdicao) {
        mostrarToast('❌ Erro ao salvar perícias', 'error');
        return;
    }

    // Armazenar em sessionStorage para recuperar na página anterior
    sessionStorage.setItem('periciasEdit', JSON.stringify(Array.from(periciasSelecionadas)));
    sessionStorage.setItem('combatenteEditId', combatenteEmEdicao.id);

    mostrarToast(`✅ ${periciasSelecionadas.size} perícia(s) salva(s)!`, 'success');

    // Voltar para página anterior após 1 segundo
    setTimeout(() => {
        window.history.back();
    }, 1000);
}

/**
 * Função Toast (pode vir de módulo externo)
 */
function mostrarToast(mensagem, tipo = 'info') {
    if (window.Toast) {
        window.Toast.show(mensagem, tipo);
    } else {
        console.log(`[${tipo.toUpperCase()}] ${mensagem}`);
    }
}

/**
 * Inicializa quando DOM carrega
 */
document.addEventListener('DOMContentLoaded', () => {
    inicializarPericiasPage();
});

/**
 * Abre página de perícias em nova aba/redirect
 * SRP: Navegar para página de perícias
 */
function abrirPaginaPericias() {
    if (!window.combatenteEmEdicao || !window.combatenteEmEdicao.id) {
        mostrarToast('❌ Selecione um combatente primeiro', 'error');
        return;
    }

    const { id, nome, tipo } = window.combatenteEmEdicao;
    const pericias = window.combatenteEmEdicao.pericias || [];

    // Construir URL com query params
    const params = new URLSearchParams({
        combatente_id: id,
        nome: nome,
        tipo: tipo,
        pericias: JSON.stringify(pericias)
    });

    // Abrir página de perícias
    window.location.href = `/pages/pericias.html?${params.toString()}`;
}

/**
 * Recupera perícias salvas da página de perícias
 * Chamada ao carregar modal de edição
 */
function recuperarPericiasDoSessionStorage() {
    const periciasEdit = sessionStorage.getItem('periciasEdit');
    const combatenteId = sessionStorage.getItem('combatenteEditId');

    if (periciasEdit && combatenteId === window.combatenteEmEdicao?.id) {
        window.combatenteEmEdicao.pericias = JSON.parse(periciasEdit);
        sessionStorage.removeItem('periciasEdit');
        sessionStorage.removeItem('combatenteEditId');
        mostrarToast('✅ Perícias carregadas', 'success');
    }
}

// Chamar ao abrir modal de edição (adicione na função que abre o modal)
// Exemplo: logo após popular os campos do formulário