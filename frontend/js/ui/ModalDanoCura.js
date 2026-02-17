/**
 * Componente UI responsável pelo modal de aplicação de dano/cura
 * Single Responsibility Principle: apenas gerencia a UI do modal
 */
class ModalDanoCura {
    constructor(danoCuraService, arenaController) {
        this.danoCuraService = danoCuraService;
        this.arenaController = arenaController;
        this.modalElement = null;
        this.combatentesSelecionados = new Set();
        this.inicializar();
    }

    /**
     * Inicializa o modal e cria elementos no DOM
     */
    inicializar() {
        this.criarModal();
        this.vincularEventos();
    }

    /**
     * Cria estrutura HTML do modal
     */
    criarModal() {
        const modalHTML = `
            <div id="modalDanoCura" class="modal">
                <div class="modal-content modal-dano-cura">
                    <div class="modal-header">
                        <h2>⚔️ Aplicar Dano / Cura</h2>
                        <button class="modal-close" onclick="modalDanoCuraInstance.fechar()">✖</button>
                    </div>
                    <div class="modal-body">
                        <div class="dano-cura-layout">
                            <!-- Lista de Combatentes -->
                            <div class="combatentes-selecao">
                                <h3>🎯 Selecionar Combatentes:</h3>
                                <div id="listaCombatentesDanoCura" class="lista-checkbox-combatentes">
                                    <!-- Preenchido dinamicamente -->
                                </div>
                            </div>

                            <!-- Campos de Dano e Cura -->
                            <div class="valores-aplicacao">
                                <div class="campo-grupo">
                                    <label for="inputDanoModal">⚔️ DANO:</label>
                                    <input 
                                        type="number" 
                                        id="inputDanoModal" 
                                        class="input-valor-modal" 
                                        min="0" 
                                        placeholder="0"
                                        value="0"
                                    >
                                </div>

                                <div class="campo-grupo">
                                    <label for="inputCuraModal">💚 CURA:</label>
                                    <input 
                                        type="number" 
                                        id="inputCuraModal" 
                                        class="input-valor-modal" 
                                        min="0" 
                                        placeholder="0"
                                        value="0"
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-actions">
                        <button class="btn-cancelar" onclick="modalDanoCuraInstance.fechar()">
                            ❌ Cancelar
                        </button>
                        <button class="btn-aplicar-principal" onclick="modalDanoCuraInstance.aplicar()">
                            ✅ Aplicar Dano / Cura
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modalElement = document.getElementById('modalDanoCura');
    }

    /**
     * Vincula eventos de mudança nos inputs
     */
    vincularEventos() {
        const inputDano = document.getElementById('inputDanoModal');
        const inputCura = document.getElementById('inputCuraModal');

        // Quando preencher dano, limpa cura
        inputDano.addEventListener('input', () => {
            if (inputDano.value && parseInt(inputDano.value) > 0) {
                inputCura.value = '0';
            }
        });

        // Quando preencher cura, limpa dano
        inputCura.addEventListener('input', () => {
            if (inputCura.value && parseInt(inputCura.value) > 0) {
                inputDano.value = '0';
            }
        });
    }

    /**
     * Abre o modal e carrega combatentes
     */
    abrir() {
        this.carregarCombatentes();
        this.combatentesSelecionados.clear();
        this.limparInputs();
        this.modalElement.classList.add('show');
    }

    /**
     * Fecha o modal
     */
    fechar() {
        this.modalElement.classList.remove('show');
    }

    /**
     * Limpa os campos de entrada
     */
    limparInputs() {
        document.getElementById('inputDanoModal').value = '0';
        document.getElementById('inputCuraModal').value = '0';
    }

    /**
     * Carrega lista de combatentes no modal
     */
    carregarCombatentes() {
        const combatentes = combatenteStorage.obterTodos();
        const container = document.getElementById('listaCombatentesDanoCura');
        
        if (!combatentes || combatentes.length === 0) {
            container.innerHTML = '<p class="sem-combatentes">⚠️ Nenhum combatente disponível</p>';
            return;
        }

        container.innerHTML = combatentes.map(c => `
            <div class="checkbox-combatente-item">
                <input 
                    type="checkbox" 
                    id="combatente-${c.id}" 
                    value="${c.id}"
                    onchange="modalDanoCuraInstance.toggleCombatente(${c.id})"
                >
                <label for="combatente-${c.id}">
                    <span class="combatente-nome">${c.nome}</span>
                    <span class="combatente-hp">${c.hp_atual}/${c.hp_maximo}</span>
                    <span class="badge-tipo badge-${c.tipo.toLowerCase()}">${c.tipo}</span>
                </label>
            </div>
        `).join('');
    }

    /**
     * Adiciona/remove combatente da seleção
     * @param {number} combatenteId 
     */
    toggleCombatente(combatenteId) {
        if (this.combatentesSelecionados.has(combatenteId)) {
            this.combatentesSelecionados.delete(combatenteId);
        } else {
            this.combatentesSelecionados.add(combatenteId);
        }
    }

    /**
     * Aplica dano ou cura aos combatentes selecionados
     */
    async aplicar() {
        try {
            // Validação: combatentes selecionados
            if (this.combatentesSelecionados.size === 0) {
                mostrarToast('⚠️ Selecione pelo menos um combatente', 'error');
                return;
            }

            // Obter valores
            const valorDano = parseInt(document.getElementById('inputDanoModal').value) || 0;
            const valorCura = parseInt(document.getElementById('inputCuraModal').value) || 0;

            // Validação: dano/cura mutuamente exclusivos
            const validacao = this.danoCuraService.validarEntrada(valorDano, valorCura);
            
            if (!validacao.valido) {
                mostrarToast(`⚠️ ${validacao.erro}`, 'error');
                return;
            }

            // Aplicar dano ou cura
            const ids = Array.from(this.combatentesSelecionados);
            
            if (validacao.tipo === 'dano') {
                await this.danoCuraService.aplicarDanoEmMassa(ids, validacao.valor);
                mostrarToast(`⚔️ Dano de ${validacao.valor} aplicado a ${ids.length} combatente(s)`, 'success');
            } else {
                await this.danoCuraService.aplicarCuraEmMassa(ids, validacao.valor);
                mostrarToast(`💚 Cura de ${validacao.valor} aplicada a ${ids.length} combatente(s)`, 'success');
            }

            // Atualizar UI
            this.arenaController.atualizarInterface();
            this.fechar();

        } catch (erro) {
            console.error('Erro ao aplicar dano/cura:', erro);
            mostrarToast(`❌ Erro: ${erro.message}`, 'error');
        }
    }
}

// Instância global (será inicializada no app.js)
let modalDanoCuraInstance;