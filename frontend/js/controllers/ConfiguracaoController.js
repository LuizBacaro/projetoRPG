/**
 * Controller de Configuração
 * Princípio SOLID: Single Responsibility - orquestrar tela de configuração
 */
import { CombatenteService } from '../services/CombatenteService.js';
import { CombatenteCard } from '../ui/CombatenteCard.js';
import { Toast } from '../ui/Toast.js';
import { getApiUrl } from '../config/api.config.js';

export class ConfiguracaoController {
    
    constructor() {
        this.combatenteService = new CombatenteService();
        this.combatentesSelecionados = [];
        this.filtroAtual = 'todos';
        
        this.inicializar();
    }
    
    /**
     * Inicializa o controller
     */
    inicializar() {
        this.configurarFiltros();
        this.carregarCombatentes();
        this.configurarBotaoIniciar();
    }
    
    /**
     * Configura event listeners dos filtros
     */
    configurarFiltros() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Atualizar botões ativos
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                // Atualizar filtro
                this.filtroAtual = e.target.dataset.tipo;
                this.carregarCombatentes();
            });
        });
    }
    
    /**
     * Carrega combatentes da API
     */
    async carregarCombatentes() {
        try {
            const tipo = this.filtroAtual === 'todos' ? null : this.filtroAtual;
            const combatentes = await this.combatenteService.listar(tipo);
            this.renderizarLista(combatentes);
        } catch (error) {
            Toast.error('Erro ao carregar combatentes');
            console.error(error);
        }
    }
    
    /**
     * Renderiza a lista de combatentes
     */
    renderizarLista(combatentes) {
        const container = document.getElementById('listaCombatentes');
        container.innerHTML = '';
        
        if (combatentes.length === 0) {
            container.innerHTML = '<p class="empty-message">Nenhum combatente encontrado</p>';
            return;
        }
        
        combatentes.forEach(combatente => {
            const selecionado = this.combatentesSelecionados.includes(combatente.id);
            const card = CombatenteCard.render(
                combatente,
                selecionado,
                (id) => this.toggleSelecao(id),
                (id) => this.abrirEdicao(id)
            );
            container.appendChild(card);
        });
    }
    
    /**
     * Toggle seleção de combatente
     */
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
    
    /**
     * Atualiza painel de selecionados
     */
    async atualizarSelecionados() {
        const container = document.getElementById('combatentesSelecionados');
        const counter = document.getElementById('contadorSelecionados');
        
        counter.textContent = this.combatentesSelecionados.length;
        
        if (this.combatentesSelecionados.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nenhum combatente selecionado</p>
                    <small>Clique nos personagens ao lado para adicionar</small>
                </div>
            `;
            return;
        }
        
        try {
            const promises = this.combatentesSelecionados.map(id => 
                this.combatenteService.obterPorId(id)
            );
            const combatentes = await Promise.all(promises);
            
            container.innerHTML = '';
            
            combatentes.forEach(combatente => {
                const card = CombatenteCard.renderSelecionado(
                    combatente,
                    (id) => this.toggleSelecao(id),
                    (id, hpAtual, novoHPMax) => this.atualizarHPMaximo(id, hpAtual, novoHPMax),
                    (id, novaIni) => this.atualizarIniciativa(id, novaIni)
                );
                container.appendChild(card);
            });
        } catch (error) {
            Toast.error('Erro ao atualizar selecionados');
            console.error(error);
        }
    }
    
    /**
     * Atualiza HP máximo de combatente selecionado
     */
    async atualizarHPMaximo(id, hpAtual, novoHPMax) {
        try {
            // Ajustar HP atual se necessário
            let novoHPAtual = hpAtual;
            if (hpAtual > novoHPMax) {
                novoHPAtual = novoHPMax;
            }
            
            // Atualizar via PATCH
            await fetch(`${getApiUrl('/combatentes')}/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ hp_maximo: novoHPMax, hp_atual: novoHPAtual })
            });
            
            Toast.success('HP máximo atualizado!');
            await this.atualizarSelecionados();
            await this.carregarCombatentes();
        } catch (error) {
            Toast.error('Erro ao atualizar HP máximo');
            console.error(error);
        }
    }
    
    /**
     * Atualiza iniciativa de combatente selecionado
     */
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
    
    /**
     * Abre modal de edição
     */
    abrirEdicao(id) {
        // Disparar evento customizado para o ModalEdicao
        const event = new CustomEvent('abrirEdicao', { detail: { id } });
        document.dispatchEvent(event);
    }
    
    /**
     * Configura botão de iniciar combate
     */
    configurarBotaoIniciar() {
        const btn = document.getElementById('btnIniciarCombate');
        btn.addEventListener('click', () => this.iniciarCombate());
    }
    
    /**
     * Inicia o combate
     */
    async iniciarCombate() {
        if (this.combatentesSelecionados.length < 2) {
            Toast.error('Selecione pelo menos 2 combatentes');
            return;
        }

        try {
            console.log('🎯 Iniciando combate com IDs:', this.combatentesSelecionados);
            
            // Buscar dados completos dos combatentes selecionados
            const combatentesCompletos = await Promise.all(
                this.combatentesSelecionados.map(id => 
                    this.combatenteService.obterPorId(id)
                )
            );

            console.log('✅ Combatentes carregados:', combatentesCompletos);

            // CRÍTICO: Validar que temos dados válidos
            if (!Array.isArray(combatentesCompletos) || combatentesCompletos.length === 0) {
                throw new Error('Erro ao carregar dados dos combatentes');
            }

            // Mudar para tela de arena
            document.getElementById('telaConfiguracao').classList.remove('ativa');
            document.getElementById('telaArena').classList.add('ativa');

            // CRÍTICO: Disparar evento COM os dados corretos
            const evento = new CustomEvent('iniciarCombate', {
                detail: { combatentes: combatentesCompletos }
            });
            
            console.log('📤 Disparando evento iniciarCombate com:', evento.detail);
            document.dispatchEvent(evento);

            Toast.success(`Combate iniciado com ${combatentesCompletos.length} combatentes! ⚔️`);

        } catch (error) {
            console.error('❌ Erro ao iniciar combate:', error);
            Toast.error('Erro ao iniciar combate');
        }
    }
}