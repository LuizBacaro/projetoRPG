/**
 * ModalCondicao
 * Classe global (sem export) — mesmo padrão do ModalDanoCura
 * SOLID: SRP - apenas gerencia UI do modal de condição
 */
class ModalCondicao {
    constructor(condicaoService, arenaController) {
        this.condicaoService     = condicaoService;
        this.arenaController     = arenaController;
        this.todasCondicoes      = [];
        this.combatentesSelecionados = new Set();
        this.modalElement        = null;
        this._inicializar();
    }

    async _inicializar() {
        await this._carregarCatalogo();
        this._criarModal();
        this._vincularEventos();
    }

    // ── Catálogo 

    async _carregarCatalogo() {
        try {
            this.todasCondicoes = await this.condicaoService.listarTodas();
        } catch (err) {
            console.error('❌ Erro ao carregar catálogo de condições:', err);
        }
    }

    // ── Criação do Modal 

    _criarModal() {
        // Remove modal existente se houver (evita duplicação)
        const existente = document.getElementById('modal-condicao');
        if (existente) existente.remove();

        const html = `
            <div id="modal-condicao" class="modal-condicao-overlay" style="display:none;">
                <div class="modal-condicao-container">

                    <div class="modal-condicao-header">
                        <h2>🔮 Aplicar Condição</h2>
                        <button id="btn-fechar-modal-condicao" class="modal-condicao-fechar">✕</button>
                    </div>

                    <div class="modal-condicao-body">
                        <div class="condicao-layout">

                            <!-- Coluna esquerda: lista de combatentes -->
                            <div class="condicao-combatentes-selecao">
                                <h3>🎯 Selecionar Combatentes:</h3>
                                <div id="lista-combatentes-condicao" class="lista-checkbox-combatentes">
                                    <!-- preenchido dinamicamente -->
                                </div>
                            </div>

                            <!-- Coluna direita: select de condição + preview -->
                            <div class="condicao-valores-aplicacao">
                                <div class="campo-grupo">
                                    <label for="select-condicao" class="modal-label">Condição:</label>
                                    <select id="select-condicao" class="modal-select-condicao">
                                        <option value="">Selecione uma condição...</option>
                                    </select>
                                </div>
                                <div id="condicao-descricao" class="condicao-descricao-preview" style="display:none;"></div>
                            </div>

                        </div>
                    </div>

                    <div class="modal-condicao-footer">
                        <button id="btn-cancelar-condicao" class="btn-cancelar-condicao">❌ Cancelar</button>
                        <button id="btn-aplicar-condicao" class="btn-aplicar-condicao">✅ Aplicar Condição</button>
                    </div>

                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
        this.modalElement = document.getElementById('modal-condicao');
    }

    // ── Eventos 

    _vincularEventos() {
        document.getElementById('btn-fechar-modal-condicao')
            ?.addEventListener('click', () => this.fechar());

        document.getElementById('btn-cancelar-condicao')
            ?.addEventListener('click', () => this.fechar());

        document.getElementById('btn-aplicar-condicao')
            ?.addEventListener('click', () => this.aplicar());

        // Fecha ao clicar fora
        this.modalElement?.addEventListener('click', (e) => {
            if (e.target === this.modalElement) this.fechar();
        });

        // Preview do efeito ao selecionar condição
        document.getElementById('select-condicao')
            ?.addEventListener('change', (e) => this._mostrarEfeito(e.target.value));
    }

    // ── API Pública 

    abrir() {
        this.combatentesSelecionados.clear();
        this._popularCombatentes();
        this._popularSelect();
        this._limparDescricao();
        if (this.modalElement) this.modalElement.style.display = 'flex';
    }

    fechar() {
        if (this.modalElement) this.modalElement.style.display = 'none';
        this._limparDescricao();
    }

    toggleCombatente(combatenteId) {
        if (this.combatentesSelecionados.has(combatenteId)) {
            this.combatentesSelecionados.delete(combatenteId);
        } else {
            this.combatentesSelecionados.add(combatenteId);
        }
    }

    async aplicar() {
        const condicaoId = Number(document.getElementById('select-condicao')?.value);

        if (this.combatentesSelecionados.size === 0) {
            this._toast('⚠️ Selecione pelo menos um combatente', 'error');
            return;
        }
        if (!condicaoId) {
            this._toast('⚠️ Selecione uma condição', 'error');
            return;
        }

        const condicao = this.todasCondicoes.find(c => c.id === condicaoId);
        const ids      = Array.from(this.combatentesSelecionados);

        try {
            // Aplica a condição em cada combatente selecionado em paralelo
            await Promise.all(
                ids.map(cid => this.condicaoService.aplicar(cid, condicaoId))
            );

            this._toast(`🔮 "${condicao?.nome}" aplicada a ${ids.length} combatente(s)`, 'success');

            // Atualiza a seção de condições do combatente ativo na arena
            if (this.arenaController?.condicaoController) {
                const combatenteAtivo = this.arenaController.combatentes[this.arenaController.turnoAtual];
                if (combatenteAtivo) {
                    await this.arenaController.condicaoController
                        .carregarCondicoesDoCombatente(combatenteAtivo.id);
                }
                // Atualiza badges na ordem de iniciativa
                await this.arenaController._atualizarBadgesOrdemTodos();
            }

            this.fechar();

        } catch (err) {
            console.error('❌ Erro ao aplicar condição:', err);
            this._toast(`❌ Erro: ${err.message}`, 'error');
        }
    }

    // ── Privados 

    _popularCombatentes() {
        const container  = document.getElementById('lista-combatentes-condicao');
        const combatentes = this.arenaController?.combatentes || [];

        if (!combatentes.length) {
            container.innerHTML = '<p class="sem-combatentes">⚠️ Nenhum combatente disponível</p>';
            return;
        }

        container.innerHTML = combatentes.map(c => `
            <div class="checkbox-combatente-item">
                <input
                    type="checkbox"
                    id="cond-check-${c.id}"
                    value="${c.id}"
                    onchange="modalCondicaoInstance.toggleCombatente(${c.id})"
                >
                <label for="cond-check-${c.id}">
                    <span class="combatente-nome">${c.nome}</span>
                    <span class="combatente-hp">${c.hp_atual}/${c.hp_maximo} PV</span>
                    <span class="badge-tipo badge-${c.tipo.toLowerCase()}">${c.tipo}</span>
                </label>
            </div>
        `).join('');
    }

    _popularSelect() {
        const select = document.getElementById('select-condicao');
        if (!select) return;

        select.innerHTML = '<option value="">Selecione uma condição...</option>';

        this.todasCondicoes.forEach(c => {
            const opt       = document.createElement('option');
            opt.value       = c.id;
            opt.textContent = c.nome;
            opt.title       = c.efeito;
            select.appendChild(opt);
        });
    }

    _mostrarEfeito(condicaoId) {
        const descEl = document.getElementById('condicao-descricao');
        if (!descEl) return;

        const c = this.todasCondicoes.find(c => c.id === Number(condicaoId));
        if (c) {
            descEl.textContent   = c.efeito;
            descEl.style.display = 'block';
        } else {
            descEl.textContent   = '';
            descEl.style.display = 'none';
        }
    }

    _limparDescricao() {
        const select = document.getElementById('select-condicao');
        const descEl = document.getElementById('condicao-descricao');
        if (select)  select.value        = '';
        if (descEl) { descEl.textContent = ''; descEl.style.display = 'none'; }
    }

    _toast(mensagem, tipo = 'success') {
        if (typeof Toast !== 'undefined') {
            tipo === 'success' ? Toast.success(mensagem) : Toast.error(mensagem);
        } else {
            console.log(mensagem);
        }
    }

    // ── Renderização de condições ativas (usada pelo CondicaoController) ──────

    renderizarCondicoesAtivas(condicoes, combatenteId, onRemover) {
        const container = document.querySelector('.arena-condicoes-lista');
        if (!container) return;

        container.innerHTML = '';

        if (!condicoes.length) {
            container.innerHTML = '<span class="arena-condicao-vazia">Nenhuma condição ativa</span>';
            return;
        }

        condicoes.forEach(c => {
            const slug       = c.nome.toLowerCase()
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-');
            const span       = document.createElement('span');
            span.className   = `arena-condicao arena-condicao-${slug}`;
            span.dataset.id  = c.id;
            span.title       = c.efeito;

            span.innerHTML = `
                ${c.nome}
                <button class="btn-remover-condicao" title="Remover ${c.nome}" data-id="${c.id}">✕</button>
            `;

            span.querySelector('.btn-remover-condicao').addEventListener('click', (e) => {
                e.stopPropagation();
                onRemover(combatenteId, c.id);
            });

            container.appendChild(span);
        });
    }

    renderizarBadgesOrdem(cardEl, condicoes) {
        const wrapper = cardEl.querySelector('.badges-condicao-ordem-wrapper');
        if (!wrapper) return;

        wrapper.innerHTML = '';
        if (!condicoes.length) return;

        const visiveis = condicoes.slice(0, 3);
        const extras   = condicoes.length - visiveis.length;

        visiveis.forEach(c => {
            const badge       = document.createElement('span');
            badge.className   = 'badge-condicao-ordem';
            badge.textContent = c.nome.slice(0, 3).toUpperCase();
            badge.title       = c.efeito;
            wrapper.appendChild(badge);
        });

        if (extras > 0) {
            const mais       = document.createElement('span');
            mais.className   = 'badge-condicao-ordem badge-condicao-mais';
            mais.textContent = `+${extras}`;
            mais.title       = condicoes.slice(3).map(c => c.nome).join(', ');
            wrapper.appendChild(mais);
        }
    }
}