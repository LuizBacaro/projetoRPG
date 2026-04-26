/**
 * ConfiguracaoController
 * SRP: orquestrar apenas a tela de configuração de combate
 * Edição de combatentes foi movida para o Dashboard
 */
import { CombatenteService }    from '/games/dnd35/js/services/CombatenteService.js?v=20260427a';
import { CombatenteCard }       from '/games/dnd35/js/ui/CombatenteCard.js';
import { Toast } from '/games/dnd35/js/ui/toast.module.js';
import { getApiUrl }            from '/games/dnd35/js/config/api.config.js';

export class ConfiguracaoController {

    constructor() {
        this.combatenteService       = new CombatenteService();
        this.combatentesSelecionados = [];
        this.filtroAtual             = 'todos';
        this.token                   = localStorage.getItem('token');
        this.inicializar();
    }

    _authHeaders(includeJson = false) {
        const headers = {};
        if (includeJson) {
            headers['Content-Type'] = 'application/json';
        }
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    // ── Init ──────────────────────────────────────────────────────────────

    inicializar() {
        this.configurarFiltros();
        this.carregarCombatentes();
        this.configurarBotaoIniciar();
    }

    // ── Filtros ───────────────────────────────────────────────────────────

    configurarFiltros() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filtroAtual = e.target.dataset.tipo;
                this.carregarCombatentes();
            });
        });
    }

    // ── Carrega combatentes ───────────────────────────────────────────────

    async carregarCombatentes() {
        try {
            const tipo        = this.filtroAtual === 'todos' ? null : this.filtroAtual;
            const combatentes = await this.combatenteService.listar(tipo);
            this.renderizarLista(combatentes);
        } catch (error) {
            Toast.error('Erro ao carregar combatentes');
            console.error(error);
        }
    }

    // ── Renderiza lista ───────────────────────────────────────────────────

    renderizarLista(combatentes) {
        const container = document.getElementById('listaCombatentes');
        container.innerHTML = '';

        if (!combatentes.length) {
            container.innerHTML = '<p class="empty-message">Nenhum combatente encontrado</p>';
            return;
        }

        combatentes.forEach(combatente => {
            const selecionado = this.combatentesSelecionados.includes(combatente.id);

            // REMOVIDO: callback onEdit — edição só existe no Dashboard
            const card = CombatenteCard.render(
                combatente,
                selecionado,
                (id) => this.toggleSelecao(id)
            );
            container.appendChild(card);
        });
    }

    // ── Toggle seleção ────────────────────────────────────────────────────

    toggleSelecao(id) {
        const index = this.combatentesSelecionados.indexOf(id);
        if (index > -1) {
            this.combatentesSelecionados.splice(index, 1);
        } else {
            this.combatentesSelecionados.push(id);
        }
        this.atualizarSelecionados();
        this.carregarCombatentes();
    }

    // ── Atualiza painel de selecionados ───────────────────────────────────

    async atualizarSelecionados() {
        const container = document.getElementById('combatentesSelecionados');
        const counter   = document.getElementById('contadorSelecionados');

        counter.textContent = this.combatentesSelecionados.length;

        if (!this.combatentesSelecionados.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nenhum combatente selecionado</p>
                    <small>Clique nos personagens ao lado para adicionar</small>
                </div>`;
            return;
        }

        try {
            const combatentes = await Promise.all(
                this.combatentesSelecionados.map(id => this.combatenteService.obterPorId(id))
            );

            container.innerHTML = '';
            combatentes.forEach(combatente => {
                const card = CombatenteCard.renderSelecionado(
                    combatente,
                    (id)               => this.toggleSelecao(id),
                    (id, hpAtual, max) => this.atualizarHPMaximo(id, hpAtual, max),
                    (id, ini)          => this.atualizarIniciativa(id, ini)
                );
                container.appendChild(card);
            });
        } catch (error) {
            Toast.error('Erro ao atualizar selecionados');
            console.error(error);
        }
    }

    // ── Atualiza HP máximo ────────────────────────────────────────────────

    async atualizarHPMaximo(id, hpAtual, novoHPMax) {
        try {
            const novoHPAtual = hpAtual > novoHPMax ? novoHPMax : hpAtual;
            await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method:  'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ hp_maximo: novoHPMax, hp_atual: novoHPAtual })
            });
            Toast.success('HP máximo atualizado!');
            await this.atualizarSelecionados();
            await this.carregarCombatentes();
        } catch (error) {
            Toast.error('Erro ao atualizar HP máximo');
            console.error(error);
        }
    }

    // ── Atualiza iniciativa ───────────────────────────────────────────────

    async atualizarIniciativa(id, novaIniciativa) {
        try {
            await this.combatenteService.atualizarIniciativa(id, novaIniciativa);
            Toast.success('Iniciativa atualizada!');
            await this.carregarCombatentes();
        } catch (error) {
            Toast.error('Erro ao atualizar iniciativa');
            console.error(error);
        }
    }

    // ── Iniciar combate ───────────────────────────────────────────────────

    configurarBotaoIniciar() {
        const btn = document.getElementById('btnIniciarCombate');
        if (btn) btn.addEventListener('click', () => this.iniciarCombate());
    }

    async iniciarCombate() {
        if (this.combatentesSelecionados.length < 2) {
            Toast.error('Selecione pelo menos 2 combatentes');
            return;
        }

        try {

            const response = await fetch(getApiUrl('/combate/iniciar'), {
                method: 'POST',
                headers: this._authHeaders(true),
                body: JSON.stringify({ combatente_ids: this.combatentesSelecionados }),
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `Erro ao iniciar combate (HTTP ${response.status})`);
            }

            const statusCombate = await response.json();
            if (!statusCombate?.ativo) {
                throw new Error('API não retornou um combate ativo após iniciar.');
            }

            document.getElementById('telaConfiguracao').classList.remove('ativa');
            document.getElementById('telaArena').classList.add('ativa');

            document.dispatchEvent(new CustomEvent('iniciarCombate', {
                detail: { status: statusCombate }
            }));

            Toast.success(`Combate iniciado com ${statusCombate.combatentes_ids.length} combatentes! ⚔️`);
        } catch (error) {
            Toast.error(error.message || 'Erro ao iniciar combate');
            console.error(error);
        }
    }
}