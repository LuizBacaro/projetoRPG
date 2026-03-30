const API_URL = 'http://127.0.0.1:8000/api';

let combatentesSelecionados = [];
let combateAtivo = null;
let filtroAtual = 'todos';
let combatenteEditando = null;

// ==================== INICIALIZAÇÃO ====================

document.addEventListener('DOMContentLoaded', () => {
    carregarCombatentes();
    configurarEventListeners();
    verificarCombateAtivo();
    adicionarBotaoCadastro();
    atualizarBotaoCadastro();
    configurarUploadCadastro();
    configurarUploadEdicao();
    configurarFormularios();
});

function configurarEventListeners() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filtroAtual = e.target.dataset.tipo;
            carregarCombatentes(filtroAtual);
            atualizarBotaoCadastro();
        });
    });

    document.getElementById('btnIniciarCombate')?.addEventListener('click', iniciarCombate);
    document.getElementById('btnAvancarTurno')?.addEventListener('click', avancarTurno);
    document.getElementById('btnFinalizarCombate')?.addEventListener('click', finalizarCombate);
    document.getElementById('btnResetarCombate')?.addEventListener('click', resetarCombate);
}

// ==================== BOTÕES DE CADASTRO ====================

function adicionarBotaoCadastro() {
    const filterContainer = document.querySelector('.filters');
    if (!filterContainer) return;
    
    // Botão Novo Jogador
    if (!filterContainer.querySelector('.btn-add-jogador')) {
        const btnAddJogador = document.createElement('button');
        btnAddJogador.className = 'btn-add-jogador';
        btnAddJogador.innerHTML = '➕ Novo Jogador';
        btnAddJogador.onclick = abrirModalCadastro;
        btnAddJogador.style.display = 'none';
        filterContainer.appendChild(btnAddJogador);
    }
    
    // Botão Novo Monstro
    if (!filterContainer.querySelector('.btn-add-monstro')) {
        const btnAddMonstro = document.createElement('button');
        btnAddMonstro.className = 'btn-add-monstro';
        btnAddMonstro.innerHTML = '➕ Novo Monstro';
        btnAddMonstro.onclick = abrirModalCadastroMonstro;
        btnAddMonstro.style.display = 'none';
        filterContainer.appendChild(btnAddMonstro);
    }
    
    // Botão Novo NPC
    if (!filterContainer.querySelector('.btn-add-npc')) {
        const btnAddNPC = document.createElement('button');
        btnAddNPC.className = 'btn-add-npc';
        btnAddNPC.innerHTML = '➕ Novo NPC';
        btnAddNPC.onclick = abrirModalCadastroNPC;
        btnAddNPC.style.display = 'none';
        filterContainer.appendChild(btnAddNPC);
    }
}

function atualizarBotaoCadastro() {
    const btnAddJogador = document.querySelector('.btn-add-jogador');
    const btnAddMonstro = document.querySelector('.btn-add-monstro');
    const btnAddNPC = document.querySelector('.btn-add-npc');
    
    if (btnAddJogador) {
        btnAddJogador.style.display = filtroAtual === 'jogador' ? 'inline-flex' : 'none';
    }
    
    if (btnAddMonstro) {
        btnAddMonstro.style.display = filtroAtual === 'monstro' ? 'inline-flex' : 'none';
    }
    
    if (btnAddNPC) {
        btnAddNPC.style.display = filtroAtual === 'npc' ? 'inline-flex' : 'none';
    }
}

// ==================== CARREGAR COMBATENTES ====================

async function carregarCombatentes(tipo = 'todos') {
    try {
        const url = tipo === 'todos' 
            ? `${API_URL}/combatentes` 
            : `${API_URL}/combatentes?tipo=${tipo}`;
        
        const response = await fetch(url);
        const combatentes = await response.json();
        
        renderizarListaCombatentes(combatentes);
    } catch (error) {
        console.error('Erro ao carregar combatentes:', error);
        mostrarMensagem('Erro ao carregar combatentes', 'error');
    }
}

function renderizarListaCombatentes(combatentes) {
    const container = document.getElementById('listaCombatentes');
    
    if (combatentes.length === 0) {
        container.innerHTML = '<p class="empty-message">Nenhum combatente encontrado</p>';
        return;
    }
    
    container.innerHTML = combatentes.map(c => `
        <div class="combatente-card ${combatentesSelecionados.includes(c.id) ? 'selected' : ''}" data-id="${c.id}">
            <div style="display: flex; gap: 1rem; align-items: center; flex: 1;" onclick="selecionarCombatente(${c.id})">
                ${c.foto_url 
                    ? `<img src="${c.foto_url}" alt="${c.nome}" class="combatente-foto">` 
                    : '<div class="combatente-foto combatente-foto-placeholder">👤</div>'}
                <div class="combatente-info">
                    <div class="combatente-header">
                        <h3>${c.nome}</h3>
                        <span class="badge badge-${c.tipo}">${c.tipo}</span>
                    </div>
                    <p class="combatente-classe">${c.classe}</p>
                    <div class="combatente-stats">
                        <div class="stat">
                            <span class="stat-label">HP:</span>
                            <span class="stat-value">${c.hp_atual}/${c.hp_maximo}</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Ini:</span>
                            <span class="stat-value">${c.iniciativa}</span>
                        </div>
                    </div>
                </div>
            </div>
            <button class="btn-editar" onclick="event.stopPropagation(); abrirModalEdicao(${c.id})">✏️ Editar</button>
        </div>
    `).join('');
}

// ==================== SELEÇÃO DE COMBATENTES ====================

function selecionarCombatente(id) {
    const index = combatentesSelecionados.indexOf(id);
    const card = document.querySelector(`[data-id="${id}"]`);
    
    if (index > -1) {
        combatentesSelecionados.splice(index, 1);
        card.classList.remove('selected');
    } else {
        combatentesSelecionados.push(id);
        card.classList.add('selected');
    }
    
    atualizarCombatentesSelecionados();
}

async function atualizarCombatentesSelecionados() {
    const container = document.getElementById('combatentesSelecionados');
    const counter = document.getElementById('contadorSelecionados');
    
    if (!container || !counter) return;
    
    counter.textContent = combatentesSelecionados.length;
    
    if (combatentesSelecionados.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhum combatente selecionado</p>
                <small>Clique nos personagens ao lado para adicionar</small>
            </div>
        `;
        return;
    }
    
    try {
        const promises = combatentesSelecionados.map(id => 
            fetch(`${API_URL}/combatentes/${id}`).then(r => r.json())
        );
        const combatentes = await Promise.all(promises);
        
        container.innerHTML = combatentes.map(c => {
            const isCritico = c.hp_atual < c.hp_maximo * 0.25;
            
            return `
                <div class="combatente-selecionado-card">
                    <div class="selecionado-foto-container">
                        ${c.foto_url ? `<img src="${c.foto_url}" alt="${c.nome}" class="selecionado-foto">` : '<div class="selecionado-foto-placeholder">👤</div>'}
                    </div>
                    <div class="selecionado-info">
                        <div class="selecionado-header">
                            <h4>${c.nome}</h4>
                            <span class="badge badge-${c.tipo}">${c.tipo}</span>
                        </div>
                        <div class="selecionado-stats">
                            <div class="selecionado-stat-hp">
                                <span class="stat-icon">❤️</span>
                                <span class="stat-label">HP:</span>
                                <span class="stat-value ${isCritico ? 'hp-critical-text' : ''}">${c.hp_atual}</span>
                                <span class="stat-separator">/</span>
                                <input 
                                    type="number" 
                                    class="hp-input-selecionado" 
                                    value="${c.hp_maximo}" 
                                    min="1"
                                    onchange="validarHPMaxSelecionado(this, ${c.id}, ${c.hp_atual})"
                                    onclick="event.stopPropagation()"
                                    title="HP Máximo (editável)"
                                >
                            </div>
                            <div class="selecionado-stat-ini">
                                <span class="stat-icon">⚡</span>
                                <span class="stat-label">Ini:</span>
                                <input 
                                    type="number" 
                                    class="ini-input-selecionado" 
                                    value="${c.iniciativa}" 
                                    min="0"
                                    onchange="validarIniciativaSelecionado(this, ${c.id})"
                                    onclick="event.stopPropagation()"
                                    title="Iniciativa (editável)"
                                >
                            </div>
                        </div>
                    </div>
                    <button class="btn-remove-selecionado" onclick="selecionarCombatente(${c.id})" title="Remover">
                        ✕
                    </button>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro ao atualizar selecionados:', error);
    }
}

// ==================== VALIDAÇÃO HP MÁXIMO NOS SELECIONADOS ====================

async function validarHPMaxSelecionado(input, combatenteId, hpAtual) {
    let valor = parseInt(input.value);
    
    if (isNaN(valor) || valor < 1) {
        input.value = 1;
        valor = 1;
    }
    
    let novoHPAtual = hpAtual;
    if (hpAtual > valor) {
        novoHPAtual = valor;
    }
    
    try {
        const response = await fetch(`${API_URL}/combatentes/${combatenteId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                hp_maximo: valor,
                hp_atual: novoHPAtual
            })
        });
        
        if (!response.ok) throw new Error('Erro ao atualizar HP máximo');
        
        mostrarMensagem('HP máximo atualizado!', 'success');
        await atualizarCombatentesSelecionados();
        carregarCombatentes(filtroAtual);
    } catch (error) {
        console.error('Erro ao atualizar HP máximo:', error);
        mostrarMensagem('Erro ao atualizar HP máximo', 'error');
        input.value = hpAtual;
    }
    
    return valor;
}

// ==================== VALIDAÇÃO INICIATIVA NOS SELECIONADOS ====================

async function validarIniciativaSelecionado(input, combatenteId) {
    let valor = parseInt(input.value);
    
    if (isNaN(valor) || valor < 0) {
        input.value = 0;
        valor = 0;
    }
    
    try {
        const response = await fetch(`${API_URL}/combatentes/${combatenteId}/iniciativa`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ iniciativa: valor })
        });
        
        if (!response.ok) throw new Error('Erro ao atualizar iniciativa');
        
        mostrarMensagem('Iniciativa atualizada!', 'success');
        carregarCombatentes(filtroAtual);
    } catch (error) {
        console.error('Erro ao atualizar iniciativa:', error);
        mostrarMensagem('Erro ao atualizar iniciativa', 'error');
    }
    
    return valor;
}

// ==================== COMBATE ====================

async function iniciarCombate() {
    if (combatentesSelecionados.length === 0) {
        mostrarMensagem('Selecione pelo menos um combatente', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/combate/iniciar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ combatente_ids: combatentesSelecionados })
        });
        
        if (!response.ok) throw new Error('Erro ao iniciar combate');
        
        const data = await response.json();
        combateAtivo = data;
        
        mostrarMensagem('Combate iniciado!', 'success');
        renderizarCombate(data);
        alternarTelas('arena');
    } catch (error) {
        console.error('Erro ao iniciar combate:', error);
        mostrarMensagem(error.message, 'error');
    }
}

async function verificarCombateAtivo() {
    try {
        const response = await fetch(`${API_URL}/combate/status`);
        const data = await response.json();
        
        if (data.ativo) {
            combateAtivo = data;
            renderizarCombate(data);
            alternarTelas('arena');
        }
    } catch (error) {
        console.error('Erro ao verificar combate:', error);
    }
}

function renderizarCombate(data) {
    const container = document.getElementById('arenaContainer');
    
    container.innerHTML = data.combatentes.map((c, index) => {
        const isAtivo = c.id === data.combatente_ativo_id;
        const isMorto = c.hp_atual <= 0;
        const hpPercentual = (c.hp_atual / c.hp_maximo) * 100;
        const isCritico = c.hp_atual < c.hp_maximo * 0.25;
        
        return `
            <div class="arena-combatente ${isAtivo ? 'ativo' : ''} ${isMorto ? 'morto' : ''}">
                ${c.foto_url ? `<img src="${c.foto_url}" alt="${c.nome}" class="arena-combatente-foto">` : ''}
                <div class="arena-combatente-info">
                    <div class="arena-combatente-header">
                        <h3>${c.nome} ${isAtivo ? '🎯' : ''} ${isMorto ? '💀' : ''}</h3>
                        <span class="badge badge-${c.tipo}">${c.classe}</span>
                    </div>
                    <div class="arena-combatente-hp">
                        <div class="hp-bar">
                            <div class="hp-fill" style="width: ${hpPercentual}%"></div>
                        </div>
                        <div class="hp-text-editable">
                            <span>HP:</span>
                            <input 
                                type="number" 
                                class="hp-input ${isCritico ? 'hp-critical' : ''}" 
                                value="${c.hp_atual}" 
                                min="0" 
                                max="${c.hp_maximo}"
                                onchange="validarHP(this, ${c.hp_maximo}); atualizarHPDireto(${c.id}, this.value)"
                                ${isMorto ? 'disabled' : ''}
                            >
                            <span>/ ${c.hp_maximo}</span>
                        </div>
                    </div>
                    <div class="arena-combatente-actions">
                        <button class="btn btn-danger" onclick="aplicarDano(${c.id}, 10)" ${isMorto ? 'disabled' : ''}>
                            -10 HP
                        </button>
                        <button class="btn btn-danger" onclick="aplicarDano(${c.id}, 20)" ${isMorto ? 'disabled' : ''}>
                            -20 HP
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function aplicarDano(combatenteId, dano) {
    try {
        if (!combateAtivo?.versao) {
            await atualizarStatusCombate();
        }

        const headers = { 'Content-Type': 'application/json' };
        if (combateAtivo?.versao) {
            headers['If-Match'] = combateAtivo.versao;
        }

        const response = await fetch(`${API_URL}/combate/aplicar-dano`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ combatente_id: combatenteId, dano: dano })
        });

        if (!response.ok) {
            if (response.status === 409 || response.status === 428) {
                await atualizarStatusCombate();
                throw new Error('O combate foi atualizado por outro usuário. Estado sincronizado, tente novamente.');
            }
            throw new Error('Erro ao aplicar dano');
        }
        
        await atualizarStatusCombate();
        mostrarMensagem(`-${dano} HP aplicado!`, 'info');
    } catch (error) {
        console.error('Erro ao aplicar dano:', error);
        mostrarMensagem(error.message, 'error');
    }
}

async function avancarTurno() {
    try {
        if (!combateAtivo?.versao) {
            await atualizarStatusCombate();
        }

        const headers = {};
        if (combateAtivo?.versao) {
            headers['If-Match'] = combateAtivo.versao;
        }

        const response = await fetch(`${API_URL}/combate/avancar-turno`, {
            method: 'POST',
            headers
        });

        if (!response.ok) {
            if (response.status === 409 || response.status === 428) {
                await atualizarStatusCombate();
                throw new Error('Outro usuário já avançou o turno. Estado sincronizado.');
            }
            throw new Error('Erro ao avançar turno');
        }
        
        await atualizarStatusCombate();
        mostrarMensagem('Turno avançado!', 'success');
    } catch (error) {
        console.error('Erro ao avançar turno:', error);
        mostrarMensagem(error.message, 'error');
    }
}

async function finalizarCombate() {
    if (!confirm('Deseja finalizar o combate?')) return;
    
    try {
        if (!combateAtivo?.versao) {
            await atualizarStatusCombate();
        }

        const headers = {};
        if (combateAtivo?.versao) {
            headers['If-Match'] = combateAtivo.versao;
        }

        const response = await fetch(`${API_URL}/combate/finalizar`, {
            method: 'POST',
            headers
        });

        if (!response.ok) {
            if (response.status === 409 || response.status === 428) {
                await atualizarStatusCombate();
                throw new Error('Conflito ao finalizar: o estado do combate mudou.');
            }
            throw new Error('Erro ao finalizar combate');
        }
        
        combateAtivo = null;
        mostrarMensagem('Combate finalizado!', 'success');
        alternarTelas('configuracao');
        limparSelecao();
    } catch (error) {
        console.error('Erro ao finalizar combate:', error);
        mostrarMensagem(error.message, 'error');
    }
}

async function resetarCombate() {
    if (!confirm('Deseja resetar todos os combatentes?')) return;
    
    try {
        const response = await fetch(`${API_URL}/combate/resetar`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error('Erro ao resetar combate');
        
        combateAtivo = null;
        mostrarMensagem('Combate resetado!', 'success');
        alternarTelas('configuracao');
        limparSelecao();
        carregarCombatentes();
    } catch (error) {
        console.error('Erro ao resetar combate:', error);
        mostrarMensagem(error.message, 'error');
    }
}

async function atualizarStatusCombate() {
    try {
        const response = await fetch(`${API_URL}/combate/status`);
        const data = await response.json();
        
        if (data.ativo) {
            combateAtivo = data;
            renderizarCombate(data);
        } else {
            combateAtivo = null;
            alternarTelas('configuracao');
        }
    } catch (error) {
        console.error('Erro ao atualizar status:', error);
    }
}

// ==================== HP EDITÁVEL NA ARENA ====================

async function atualizarHPDireto(combatenteId, novoHP) {
    try {
        const response = await fetch(`${API_URL}/combatentes/${combatenteId}/hp`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ hp_atual: parseInt(novoHP) })
        });
        
        if (!response.ok) throw new Error('Erro ao atualizar HP');
        
        await atualizarStatusCombate();
        mostrarMensagem('HP atualizado!', 'success');
    } catch (error) {
        console.error('Erro ao atualizar HP:', error);
        mostrarMensagem('Erro ao atualizar HP', 'error');
    }
}

function validarHP(input, hpMaximo) {
    let valor = parseInt(input.value);
    
    if (isNaN(valor) || valor < 0) {
        input.value = 0;
        valor = 0;
    } else if (valor > hpMaximo) {
        input.value = hpMaximo;
        valor = hpMaximo;
    }
    
    if (valor < hpMaximo * 0.25) {
        input.classList.add('hp-critical');
    } else {
        input.classList.remove('hp-critical');
    }
    
    return valor;
}

// ==================== EDIÇÃO DE COMBATENTES ====================

function abrirModalEdicao(combatenteId) {
    combatenteEditando = combatenteId;
    
    fetch(`${API_URL}/combatentes/${combatenteId}`)
        .then(response => response.json())
        .then(combatente => {
            console.log('Combatente carregado:', combatente);
            
            document.getElementById('editId').value = combatente.id;
            document.getElementById('editNome').value = combatente.nome;
            document.getElementById('editHP').value = combatente.hp_maximo;
            document.getElementById('editIniciativa').value = combatente.iniciativa;
            document.getElementById('editClasse').value = combatente.classe;
            document.getElementById('editTipo').value = combatente.tipo;
            
            const editNivel = document.getElementById('editNivel');
            const editPontos = document.getElementById('editPontos');
            if (editNivel) editNivel.value = combatente.nivel || 1;
            if (editPontos) editPontos.value = combatente.pontos || 0;
            
            const editFOR = document.getElementById('editFOR');
            const editDES = document.getElementById('editDES');
            const editCON = document.getElementById('editCON');
            const editINT = document.getElementById('editINT');
            const editSAB = document.getElementById('editSAB');
            const editCAR = document.getElementById('editCAR');
            
            if (editFOR) {
                editFOR.value = combatente.forca || 10;
                atualizarModificador(editFOR);
            }
            if (editDES) {
                editDES.value = combatente.destreza || 10;
                atualizarModificador(editDES);
            }
            if (editCON) {
                editCON.value = combatente.constituicao || 10;
                atualizarModificador(editCON);
            }
            if (editINT) {
                editINT.value = combatente.inteligencia || 10;
                atualizarModificador(editINT);
            }
            if (editSAB) {
                editSAB.value = combatente.sabedoria || 10;
                atualizarModificador(editSAB);
            }
            if (editCAR) {
                editCAR.value = combatente.carisma || 10;
                atualizarModificador(editCAR);
            }
            
            if (combatente.foto_url) {
                document.getElementById('editPreviewImage').src = combatente.foto_url;
                document.getElementById('editUploadPlaceholder').style.display = 'none';
                document.getElementById('editUploadPreview').style.display = 'block';
            } else {
                document.getElementById('editUploadPlaceholder').style.display = 'block';
                document.getElementById('editUploadPreview').style.display = 'none';
            }

            recuperarPericiasDoSessionStorage();
            window.combatenteEmEdicao = combatente;
            
            document.getElementById('modalEdicao').classList.add('show');
        })
        .catch(error => {
            console.error('Erro ao carregar combatente:', error);
            mostrarMensagem('Erro ao carregar dados do combatente', 'error');
        });
}

function fecharModalEdicao() {
    document.getElementById('modalEdicao').classList.remove('show');
    document.getElementById('formEdicaoCombatente').reset();
    removerImagemEdicao();
    combatenteEditando = null;
}

async function confirmarDelecao() {
    if (!combatenteEditando) return;
    
    if (!confirm('Tem certeza que deseja deletar este combatente? Esta ação não pode ser desfeita!')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/combatentes/${combatenteEditando}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Erro ao deletar combatente');
        
        mostrarMensagem('Combatente deletado com sucesso!', 'success');
        fecharModalEdicao();
        carregarCombatentes(filtroAtual);
    } catch (error) {
        console.error('Erro ao deletar combatente:', error);
        mostrarMensagem('Erro ao deletar combatente', 'error');
    }
}

function removerImagemEdicao() {
    const editFoto = document.getElementById('editFoto');
    const placeholder = document.getElementById('editUploadPlaceholder');
    const preview = document.getElementById('editUploadPreview');
    
    if (editFoto) editFoto.value = '';
    if (placeholder) placeholder.style.display = 'block';
    if (preview) preview.style.display = 'none';
}

// ==================== MODAL DE CADASTRO ====================

function abrirModalCadastro() {
    const modal = document.getElementById('modalCadastro');
    if (modal) modal.classList.add('show');
}

function fecharModalCadastro() {
    const modal = document.getElementById('modalCadastro');
    if (modal) modal.classList.remove('show');
    
    const form = document.getElementById('formCadastroJogador');
    if (form) form.reset();
    
    removerImagem();
}

function removerImagem() {
    const inputFoto = document.getElementById('inputFoto');
    const placeholder = document.getElementById('uploadPlaceholder');
    const preview = document.getElementById('uploadPreview');
    
    if (inputFoto) inputFoto.value = '';
    if (placeholder) placeholder.style.display = 'block';
    if (preview) preview.style.display = 'none';
}

// ==================== MODAIS DE CADASTRO - MONSTRO ====================

function abrirModalCadastroMonstro() {
    const modal = document.getElementById('modalCadastroMonstro');
    if (modal) modal.classList.add('show');
}

function fecharModalCadastroMonstro() {
    const modal = document.getElementById('modalCadastroMonstro');
    if (modal) modal.classList.remove('show');
    
    const form = document.getElementById('formCadastroMonstro');
    if (form) form.reset();
    
    removerImagemMonstro();
}

function removerImagemMonstro() {
    const inputFoto = document.getElementById('inputFotoMonstro');
    const placeholder = document.getElementById('uploadPlaceholderMonstro');
    const preview = document.getElementById('uploadPreviewMonstro');
    
    if (inputFoto) inputFoto.value = '';
    if (placeholder) placeholder.style.display = 'block';
    if (preview) preview.style.display = 'none';
}

// ==================== MODAIS DE CADASTRO - NPC ====================

function abrirModalCadastroNPC() {
    const modal = document.getElementById('modalCadastroNPC');
    if (modal) modal.classList.add('show');
}

function fecharModalCadastroNPC() {
    const modal = document.getElementById('modalCadastroNPC');
    if (modal) modal.classList.remove('show');
    
    const form = document.getElementById('formCadastroNPC');
    if (form) form.reset();
    
    removerImagemNPC();
}

function removerImagemNPC() {
    const inputFoto = document.getElementById('inputFotoNPC');
    const placeholder = document.getElementById('uploadPlaceholderNPC');
    const preview = document.getElementById('uploadPreviewNPC');
    
    if (inputFoto) inputFoto.value = '';
    if (placeholder) placeholder.style.display = 'block';
    if (preview) preview.style.display = 'none';
}

// ==================== UPLOAD DE IMAGENS ====================

function configurarUploadCadastro() {
    // Upload Jogador
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.addEventListener('click', () => {
            document.getElementById('inputFoto')?.click();
        });
    }

    const inputFoto = document.getElementById('inputFoto');
    if (inputFoto) {
        inputFoto.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('previewImage').src = e.target.result;
                    document.getElementById('uploadPlaceholder').style.display = 'none';
                    document.getElementById('uploadPreview').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Upload Monstro
    const uploadAreaMonstro = document.getElementById('uploadAreaMonstro');
    if (uploadAreaMonstro) {
        uploadAreaMonstro.addEventListener('click', () => {
            document.getElementById('inputFotoMonstro')?.click();
        });
    }

    const inputFotoMonstro = document.getElementById('inputFotoMonstro');
    if (inputFotoMonstro) {
        inputFotoMonstro.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('previewImageMonstro').src = e.target.result;
                    document.getElementById('uploadPlaceholderMonstro').style.display = 'none';
                    document.getElementById('uploadPreviewMonstro').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Upload NPC
    const uploadAreaNPC = document.getElementById('uploadAreaNPC');
    if (uploadAreaNPC) {
        uploadAreaNPC.addEventListener('click', () => {
            document.getElementById('inputFotoNPC')?.click();
        });
    }

    const inputFotoNPC = document.getElementById('inputFotoNPC');
    if (inputFotoNPC) {
        inputFotoNPC.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('previewImageNPC').src = e.target.result;
                    document.getElementById('uploadPlaceholderNPC').style.display = 'none';
                    document.getElementById('uploadPreviewNPC').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

function configurarUploadEdicao() {
    const editUploadArea = document.getElementById('editUploadArea');
    if (editUploadArea) {
        editUploadArea.addEventListener('click', () => {
            document.getElementById('editFoto')?.click();
        });
    }

    const editFoto = document.getElementById('editFoto');
    if (editFoto) {
        editFoto.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('editPreviewImage').src = e.target.result;
                    document.getElementById('editUploadPlaceholder').style.display = 'none';
                    document.getElementById('editUploadPreview').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// ==================== FORMULÁRIOS ====================

function configurarFormularios() {
    // Fechar modais ao clicar fora
    document.getElementById('modalCadastro')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalCadastro') fecharModalCadastro();
    });
    
    document.getElementById('modalCadastroMonstro')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalCadastroMonstro') fecharModalCadastroMonstro();
    });
    
    document.getElementById('modalCadastroNPC')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalCadastroNPC') fecharModalCadastroNPC();
    });
    
    document.getElementById('modalEdicao')?.addEventListener('click', (e) => {
        if (e.target.id === 'modalEdicao') fecharModalEdicao();
    });
    
    // Submit formulário de cadastro JOGADOR
    const formCadastro = document.getElementById('formCadastroJogador');
    if (formCadastro) {
        formCadastro.addEventListener('submit', async (e) => {
            e.preventDefault();
            await cadastrarCombatente(e.target, 'jogador', 'Jogador');
        });
    }
    
    // Submit formulário de cadastro MONSTRO
    const formCadastroMonstro = document.getElementById('formCadastroMonstro');
    if (formCadastroMonstro) {
        formCadastroMonstro.addEventListener('submit', async (e) => {
            e.preventDefault();
            await cadastrarCombatente(e.target, 'monstro', 'Monstro');
        });
    }
    
    // Submit formulário de cadastro NPC
    const formCadastroNPC = document.getElementById('formCadastroNPC');
    if (formCadastroNPC) {
        formCadastroNPC.addEventListener('submit', async (e) => {
            e.preventDefault();
            await cadastrarCombatente(e.target, 'npc', 'NPC');
        });
    }
    
    // Submit formulário de edição
    const formEdicao = document.getElementById('formEdicaoCombatente');
    if (formEdicao) {
        formEdicao.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!combatenteEditando) {
                console.error('Nenhum combatente sendo editado');
                return;
            }
            
            const formData = new FormData();
            formData.append('nome', document.getElementById('editNome').value);
            formData.append('hp_maximo', document.getElementById('editHP').value);
            formData.append('iniciativa', document.getElementById('editIniciativa').value);
            formData.append('classe', document.getElementById('editClasse').value);
            formData.append('tipo', document.getElementById('editTipo').value);
            
            const editNivel = document.getElementById('editNivel');
            const editPontos = document.getElementById('editPontos');
            if (editNivel) formData.append('nivel', editNivel.value);
            if (editPontos) formData.append('pontos', editPontos.value);
            
            const editFOR = document.getElementById('editFOR');
            const editDES = document.getElementById('editDES');
            const editCON = document.getElementById('editCON');
            const editINT = document.getElementById('editINT');
            const editSAB = document.getElementById('editSAB');
            const editCAR = document.getElementById('editCAR');
            
            if (editFOR) formData.append('forca', editFOR.value);
            if (editDES) formData.append('destreza', editDES.value);
            if (editCON) formData.append('constituicao', editCON.value);
            if (editINT) formData.append('inteligencia', editINT.value);
            if (editSAB) formData.append('sabedoria', editSAB.value);
            if (editCAR) formData.append('carisma', editCAR.value);
            
            const fotoInput = document.getElementById('editFoto');
            if (fotoInput && fotoInput.files.length > 0) {
                formData.append('foto', fotoInput.files[0]);
            }
            
            try {
                const response = await fetch(`${API_URL}/combatentes/${combatenteEditando}`, {
                    method: 'PUT',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Erro ao atualizar combatente');
                }
                
                mostrarMensagem('Combatente atualizado com sucesso!', 'success');
                fecharModalEdicao();
                carregarCombatentes(filtroAtual);
            } catch (error) {
                console.error('Erro ao atualizar combatente:', error);
                mostrarMensagem(error.message || 'Erro ao atualizar combatente', 'error');
            }
        });
    }
} 

// ==================== FUNÇÃO GENÉRICA DE CADASTRO ====================

async function cadastrarCombatente(form, tipo, tipoNome) {
    const formData = new FormData(form);
    
    try {
        const response = await fetch(`${API_URL}/combatentes`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ao cadastrar ${tipoNome.toLowerCase()}`);
        }
        
        mostrarMensagem(`${tipoNome} cadastrado com sucesso!`, 'success');
        
        if (tipo === 'jogador') fecharModalCadastro();
        else if (tipo === 'monstro') fecharModalCadastroMonstro();
        else if (tipo === 'npc') fecharModalCadastroNPC();
        
        filtroAtual = tipo;
        document.querySelector(`[data-tipo="${tipo}"]`)?.classList.add('active');
        document.querySelectorAll('.filter-btn').forEach(b => {
            if (b.dataset.tipo !== tipo) b.classList.remove('active');
        });
        
        carregarCombatentes(tipo);
        atualizarBotaoCadastro();
    } catch (error) {
        console.error(`Erro ao cadastrar ${tipoNome.toLowerCase()}:`, error);
        mostrarMensagem(error.message || `Erro ao cadastrar ${tipoNome.toLowerCase()}`, 'error');
    }
}

// ==================== CÁLCULO DE MODIFICADORES D&D ====================

function calcularModificador(valor) {
    return Math.floor((valor - 10) / 2);
}

function atualizarModificador(input) {
    const valor = parseInt(input.value) || 10;
    const modificador = calcularModificador(valor);
    const modificadorTexto = modificador >= 0 ? `+${modificador}` : `${modificador}`;
    
    const modificadorSpan = input.parentElement.querySelector('.atributo-modificador');
    if (modificadorSpan) {
        modificadorSpan.textContent = modificadorTexto;
    }
}

// ==================== UTILITÁRIOS ====================

function alternarTelas(tela) {
    const telaConfig = document.getElementById('telaConfiguracao');
    const telaArena = document.getElementById('telaArena');
    
    if (telaConfig && telaArena) {
        telaConfig.style.display = tela === 'configuracao' ? 'block' : 'none';
        telaArena.style.display = tela === 'arena' ? 'block' : 'none';
    }
}

function limparSelecao() {
    combatentesSelecionados = [];
    document.querySelectorAll('.combatente-card').forEach(card => {
        card.classList.remove('selected');
    });
    atualizarCombatentesSelecionados();
}

function mostrarMensagem(texto, tipo) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.textContent = texto;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// INICIALIZAÇÃO DO MODAL DANO/CURA
// ============================================

// Inicializar após o carregamento da página
document.addEventListener('DOMContentLoaded', function() {
    // Supondo que você já tenha combatenteRepository definido
    if (typeof combatenteRepository !== 'undefined') {
        window.danoCuraService = new DanoCuraService(combatenteRepository);
        window.modalDanoCuraInstance = new ModalDanoCura(danoCuraService, arenaController);
        console.log('✅ Modal de Dano/Cura inicializado');
    }
});

/**
 * Função global para abrir o modal
 */
function abrirModalDanoCura() {
    if (window.modalDanoCuraInstance) {
        window.modalDanoCuraInstance.abrir();
    } else {
        console.error('Modal de Dano/Cura não foi inicializado');
        mostrarToast('❌ Erro ao abrir modal', 'error');
    }
}

/**
 * abrirPaginaPericias()
 * SRP: Navegar para página de perícias com parâmetros do combatente
 * SOLID: Single Responsibility — apenas navegação
 */
function abrirPaginaPericias() {
    // ✅ Validar se existe combatente em edição
    if (!combatenteEditando) {
        mostrarMensagem('❌ Nenhum combatente selecionado', 'error');
        return;
    }

    try {
        const id = combatenteEditando;
        const nome = document.getElementById('editNome').value;
        const tipo = document.getElementById('editTipo').value;
        const pericias = window.combatenteEmEdicao?.pericias || [];

        // ✅ Construir URL com query params
        const params = new URLSearchParams({
            combatente_id: id,
            nome: nome,
            tipo: tipo,
            pericias: JSON.stringify(pericias)
        });

        console.log('🔗 Navegando para perícias:', {
            id,
            nome,
            tipo,
            periciasCount: pericias.length
        });

        // ✅ Redirecionar para página de perícias
        window.location.href = `/pages/pericias.html?${params.toString()}`;
    } catch (erro) {
        console.error('❌ Erro ao navegar para perícias:', erro);
        mostrarMensagem('❌ Erro ao abrir perícias', 'error');
    }
}

/**
 * recuperarPericiasDoSessionStorage()
 * SRP: Recuperar perícias salvas da página de perícias
 * SOLID: Single Responsibility — apenas recuperação de dados
 */
function recuperarPericiasDoSessionStorage() {
    const periciasEdit = sessionStorage.getItem('periciasEdit');
    const combatenteId = sessionStorage.getItem('combatenteEditId');

    if (periciasEdit && combatenteId) {
        try {
            const pericias = JSON.parse(periciasEdit);
            
            // ✅ Atualizar combatente em edição se for o mesmo
            if (window.combatenteEmEdicao && window.combatenteEmEdicao.id == combatenteId) {
                window.combatenteEmEdicao.pericias = pericias;
                mostrarMensagem(`✅ ${pericias.length} perícia(s) carregada(s)`, 'success');
                
                console.log('📚 Perícias recuperadas:', pericias);
            }

            // ✅ Limpar sessionStorage
            sessionStorage.removeItem('periciasEdit');
            sessionStorage.removeItem('combatenteEditId');
        } catch (erro) {
            console.error('❌ Erro ao recuperar perícias:', erro);
            mostrarMensagem('⚠️ Erro ao carregar perícias salvas', 'error');
        }
    }
}