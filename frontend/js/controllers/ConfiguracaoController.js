/**
 * ConfiguracaoController
 * SRP: orquestrar apenas a tela de configuração de combate
 * Edição de combatentes foi movida para o Dashboard
 */
import { CombatenteService }    from '../services/CombatenteService.js';
import { CombatenteCard }       from '../ui/CombatenteCard.js';
import { Toast } from '../ui/toast.module.js';
import { getApiUrl }            from '../config/api.config.js';

export class ConfiguracaoController {

    constructor() {
        this.combatenteService       = new CombatenteService();
        this.combatentesSelecionados = [];
        this.filtroAtual             = 'todos';
        this.inicializar();
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
            console.log('🎯 Iniciando combate com IDs:', this.combatentesSelecionados);

            const combatentesCompletos = await Promise.all(
                this.combatentesSelecionados.map(id => this.combatenteService.obterPorId(id))
            );

            if (!combatentesCompletos.length) throw new Error('Erro ao carregar dados');

            document.getElementById('telaConfiguracao').classList.remove('ativa');
            document.getElementById('telaArena').classList.add('ativa');

            document.dispatchEvent(new CustomEvent('iniciarCombate', {
                detail: { combatentes: combatentesCompletos }
            }));

            Toast.success(`Combate iniciado com ${combatentesCompletos.length} combatentes! ⚔️`);
        } catch (error) {
            Toast.error('Erro ao iniciar combate');
            console.error(error);
        }
    }
}