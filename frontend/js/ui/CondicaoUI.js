/**
 * ModalCondicao
 * Classe global (sem export) — carregada via <script> no index.html
 * SOLID: SRP - gerencia UI do modal de condição
 * ✅ Trata duracao_turnos undefined/null como permanente
 */
class ModalCondicao {
    constructor(condicaoService, arenaController) {
        this.condicaoService         = condicaoService;
        this.arenaController         = arenaController;
        this.todasCondicoes          = [];
        this.combatentesSelecionados = new Set();
        this.modalElement            = null;
        this._inicializar();
    }

    async _inicializar() {
        await this._carregarCatalogo();
        this._criarModal();
        this._vincularEventos();
    }

    async _carregarCatalogo() {
        try {
            this.todasCondicoes = await this.condicaoService.listarTodas();
            console.log('✅ Catálogo de condições carregado:', this.todasCondicoes.length);
        } catch (err) {
            console.error('❌ Erro ao carregar catálogo:', err);
        }
    }

    _criarModal() {
        const existente = document.getElementById('modal-condicao');
        if (existente) existente.remove();

        document.body.insertAdjacentHTML('beforeend', `
            <div id="modal-condicao" class="modal-condicao-overlay" style="display:none;">
                <div class="modal-condicao-container">
                    <div class="modal-condicao-header">
                        <h2>🔮 Aplicar Condição</h2>
                        <button id="btn-fechar-modal-condicao" class="modal-condicao-fechar">✕</button>
                    </div>
                    <div class="modal-condicao-body">
                        <div class="condicao-layout">
                            <div class="condicao-combatentes-selecao">
                                <h3>🎯 Selecionar Combatentes:</h3>
                                <div id="lista-combatentes-condicao" class="lista-checkbox-combatentes"></div>
                            </div>
                            <div class="condicao-valores-aplicacao">
                                <div class="campo-grupo">
                                    <label for="select-condicao" class="modal-label">Condição:</label>
                                    <select id="select-condicao" class="modal-select-condicao">
                                        <option value="">Selecione uma condição...</option>
                                    </select>
                                </div>
                                <div id="condicao-descricao" class="condicao-descricao-preview" style="display:none;"></div>
                                
                                <!-- ✅ NOVO: Campo de duração com hint -->
                                <div class="campo-grupo">
                                    <label for="input-duracao" class="modal-label">⏰ Duração (turnos):</label>
                                    <div class="duracao-input-wrapper">
                                        <input 
                                            type="number" 
                                            id="input-duracao" 
                                            class="modal-input-duracao"
                                            value="-1" 
                                            min="-1"
                                            max="99"
                                            title="-1 = permanente, 0+ = número de turnos"
                                        >
                                        <span class="duracao-hint">(-1 = permanente)</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-condicao-footer">
                        <button id="btn-cancelar-condicao" class="btn-cancelar-condicao">❌ Cancelar</button>
                        <button id="btn-aplicar-condicao" class="btn-aplicar-condicao">✅ Aplicar Condição</button>
                    </div>
                </div>
            </div>
        `);

        this.modalElement = document.getElementById('modal-condicao');
    }

    _vincularEventos() {
        document.getElementById('btn-fechar-modal-condicao')
            ?.addEventListener('click', () => this.fechar());

        document.getElementById('btn-cancelar-condicao')
            ?.addEventListener('click', () => this.fechar());

        document.getElementById('btn-aplicar-condicao')
            ?.addEventListener('click', () => this.aplicar());

        this.modalElement?.addEventListener('click', (e) => {
            if (e.target === this.modalElement) this.fechar();
        });

        document.getElementById('select-condicao')
            ?.addEventListener('change', (e) => this._mostrarEfeito(e.target.value));
    }

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

    // ✅ REFATORADO: aplicar com duração
    async aplicar() {
        const condicaoId       = Number(document.getElementById('select-condicao')?.value);
        const durationTurnos   = Number(document.getElementById('input-duracao')?.value ?? -1);

        if (this.combatentesSelecionados.size === 0) {
            if (typeof Toast !== 'undefined') Toast.error('⚠️ Selecione pelo menos um combatente');
            return;
        }
        if (!condicaoId) {
            if (typeof Toast !== 'undefined') Toast.error('⚠️ Selecione uma condição');
            return;
        }

        const condicao = this.todasCondicoes.find(c => c.id === condicaoId);
        const ids      = Array.from(this.combatentesSelecionados);

        try {
            // ✅ Passar duração_turnos ao aplicar
            await Promise.all(ids.map(cid => 
                this.condicaoService.aplicar(cid, condicaoId, durationTurnos)
            ));

            const durStr = durationTurnos === -1 ? 'permanente' : `${durationTurnos} turno(s)`;
            if (typeof Toast !== 'undefined') {
                Toast.success(`🔮 "${condicao?.nome}" (${durStr}) aplicada a ${ids.length} combatente(s)`);
            }

            if (this.arenaController) {
                const ativo = this.arenaController.combatentes[this.arenaController.turnoAtual];
                if (ativo) {
                    await this.arenaController.condicaoController
                        .carregarCondicoesDoCombatente(ativo.id);
                }
                await this.arenaController._atualizarBadgesOrdemTodos();
            }

            this.fechar();
        } catch (err) {
            console.error('❌ Erro ao aplicar condição:', err);
            if (typeof Toast !== 'undefined') Toast.error(`❌ Erro: ${err.message}`);
        }
    }

    // ✅ REFATORADO: renderizar com tratamento de undefined
    renderizarCondicoesAtivas(condicoes, combatenteId, onRemover) {
        const container = document.querySelector('.arena-condicoes-lista');
        if (!container) return;

        container.innerHTML = '';

        if (!condicoes || condicoes.length === 0) {
            container.innerHTML = '<span class="arena-condicao-vazia">Nenhuma condição ativa</span>';
            return;
        }

        condicoes.forEach(c => {
            const slug     = c.nome.toLowerCase()
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-');
            const span     = document.createElement('span');
            span.className = `arena-condicao arena-condicao-${slug}`;
            
            // ✅ Tratar duracao_turnos undefined/null como permanente
            const duracao = c.duracao_turnos ?? -1;
            const durStr  = duracao === -1 ? 'permanente' : `${duracao} turno(s)`;
            span.title    = `${c.efeito}\n⏰ Duração: ${durStr}`;
            
            // ✅ Exibir duração na badge se não permanente
            const durBadge = (duracao && duracao !== -1)
                ? `<span class="condicao-duracao">⏱️${duracao}</span>`
                : '';
            
            span.innerHTML = `
                ${c.nome}
                ${durBadge}
                <button class="btn-remover-condicao" title="Remover ${c.nome}" data-id="${c.id}">✕</button>
            `;
            span.querySelector('.btn-remover-condicao').addEventListener('click', (e) => {
                e.stopPropagation();
                onRemover(combatenteId, c.id);
            });
            container.appendChild(span);
        });
    }

    // ✅ REFATORADO: badges na ordem de iniciativa com duração
    renderizarBadgesOrdem(cardEl, condicoes) {
        const wrapper = cardEl.querySelector('.badges-condicao-ordem-wrapper');
        if (!wrapper) return;

        wrapper.innerHTML = '';
        if (!condicoes || condicoes.length === 0) return;

        condicoes.slice(0, 3).forEach(c => {
            const badge = document.createElement('span');
            badge.className = 'badge-condicao-ordem';
            
            const duracao = c.duracao_turnos ?? -1;
            const durDisplay = (duracao && duracao !== -1)
                ? `⏱️${duracao}`
                : c.nome.slice(0, 3).toUpperCase();
            
            badge.textContent = durDisplay;
            badge.title = `${c.nome}${(duracao && duracao !== -1) ? ` (${duracao} turno(s))` : ' (permanente)'}`;
            wrapper.appendChild(badge);
        });

        const extras = condicoes.length - 3;
        if (extras > 0) {
            const mais = document.createElement('span');
            mais.className = 'badge-condicao-ordem badge-condicao-mais';
            mais.textContent = `+${extras}`;
            mais.title = condicoes.slice(3).map(c => {
                const duracao = c.duracao_turnos ?? -1;
                return `${c.nome}${(duracao && duracao !== -1) ? ` (${duracao} turno(s))` : ' (permanente)'}`;
            }).join(', ');
            wrapper.appendChild(mais);
        }
    }

    _popularCombatentes() {
        const container   = document.getElementById('lista-combatentes-condicao');
        const combatentes = this.arenaController?.combatentes || [];

        if (!combatentes.length) {
            container.innerHTML = '<p style="color:#888;font-style:italic;">Nenhum combatente disponível</p>';
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
                    <span class="badge badge-${c.tipo}">${c.tipo}</span>
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
        if (c) { descEl.textContent = c.efeito; descEl.style.display = 'block'; }
        else   { descEl.textContent = '';        descEl.style.display = 'none';  }
    }

    _limparDescricao() {
        const select = document.getElementById('select-condicao');
        const descEl = document.getElementById('condicao-descricao');
        const durEl  = document.getElementById('input-duracao');
        if (select)  select.value        = '';
        if (descEl) { descEl.textContent = ''; descEl.style.display = 'none'; }
        if (durEl)   durEl.value         = '-1';  // ✅ Reset duração para permanente
    }
}