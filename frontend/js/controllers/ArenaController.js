/**
 * Controller da Arena de Combate
 * Princípio SOLID: Single Responsibility - orquestrar tela de arena
 */
import { CombateService } from '../services/CombateService.js';
import { CombatenteService } from '../services/CombatenteService.js';
import { ArenaView } from '../ui/ArenaView.js';
import { OrdemIniciativa } from '../ui/OrdemIniciativa.js';
import { CombatenteAtivoView } from '../ui/CombatenteAtivoView.js';
import { Toast } from '../ui/Toast.js';

export class ArenaController {
    
    constructor() {
        this.combateService = new CombateService();
        this.combatenteService = new CombatenteService();
        this.combateAtual = null;
        this.view = new ArenaView();
        
        this.inicializar();
    }
    
    /**
     * Inicializa o controller
     */
    inicializar() {
        this.configurarEventos();
        this.verificarCombateAtivo();
    }
    
    /**
     * Configura event listeners
     */
    configurarEventos() {
        // Evento customizado: iniciar combate
        document.addEventListener('iniciarCombate', (e) => {
            this.iniciarCombate(e.detail.ids);
        });
        
        // Botão avançar turno
        const btnAvancar = document.getElementById('btnAvancarTurno');
        if (btnAvancar) {
            btnAvancar.addEventListener('click', () => this.avancarTurno());
        }
        
        // Botão finalizar combate
        const btnFinalizar = document.getElementById('btnFinalizarCombate');
        if (btnFinalizar) {
            btnFinalizar.addEventListener('click', () => this.finalizarCombate());
        }
        
        // Botão resetar combate
        const btnResetar = document.getElementById('btnResetarCombate');
        if (btnResetar) {
            btnResetar.addEventListener('click', () => this.resetarCombate());
        }
    }
    
    /**
     * Verifica se existe combate ativo ao carregar a página
     */
    async verificarCombateAtivo() {
        try {
            const combate = await this.combateService.obterStatus();
            
            if (combate && combate.estaAtivo()) {
                this.combateAtual = combate;
                this.mostrarArena();
                this.renderizarArena();
            }
        } catch (error) {
            console.error('Erro ao verificar combate ativo:', error);
        }
    }
    
    /**
     * Inicia um novo combate
     */
    async iniciarCombate(combatenteIds) {
        try {
            const combate = await this.combateService.iniciar(combatenteIds);
            this.combateAtual = combate;
            
            Toast.success('Combate iniciado!');
            this.mostrarArena();
            this.renderizarArena();
        } catch (error) {
            Toast.error(error.message || 'Erro ao iniciar combate');
            console.error(error);
        }
    }
    
    /**
     * Avança para o próximo turno
     */
    async avancarTurno() {
        try {
            const combate = await this.combateService.avancarTurno();
            this.combateAtual = combate;
            
            this.renderizarArena();
            Toast.info('Próximo turno!');
        } catch (error) {
            Toast.error(error.message || 'Erro ao avançar turno');
            
            // Se combate finalizou, voltar para configuração
            if (error.message.includes('finalizado')) {
                setTimeout(() => this.voltarParaConfiguracao(), 2000);
            }
        }
    }
    
    /**
     * Aplica dano a um combatente
     */
    async aplicarDano(combatenteId, dano) {
        try {
            await this.combateService.aplicarDano(combatenteId, dano);
            
            // Atualizar status do combate
            const combate = await this.combateService.obterStatus();
            this.combateAtual = combate;
            
            this.renderizarArena();
            Toast.success(`${dano} de dano aplicado!`);
        } catch (error) {
            Toast.error('Erro ao aplicar dano');
            console.error(error);
        }
    }
    
    /**
     * Aplica cura a um combatente
     */
    async aplicarCura(combatenteId, cura) {
        try {
            const combatente = this.combateAtual.combatentes.find(c => c.id === combatenteId);
            const novoHP = Math.min(combatente.hp_atual + cura, combatente.hp_maximo);
            
            await this.combatenteService.atualizarHP(combatenteId, novoHP);
            
            // Atualizar status do combate
            const combate = await this.combateService.obterStatus();
            this.combateAtual = combate;
            
            this.renderizarArena();
            Toast.success(`${cura} HP restaurado!`);
        } catch (error) {
            Toast.error('Erro ao aplicar cura');
            console.error(error);
        }
    }
    
    /**
     * Aplicar condição (por enquanto só placeholder)
     */
    async aplicarCondicao(combatenteId) {
        Toast.info('Funcionalidade "Aplicar Condição" será implementada em breve!');
        console.log('Aplicar condição ao combatente:', combatenteId);
    }
    
    /**
     * Atualiza HP diretamente
     */
    async atualizarHP(combatenteId, novoHP) {
        try {
            await this.combatenteService.atualizarHP(combatenteId, novoHP);
            
            // Atualizar status do combate
            const combate = await this.combateService.obterStatus();
            this.combateAtual = combate;
            
            this.renderizarArena();
        } catch (error) {
            Toast.error('Erro ao atualizar HP');
            console.error(error);
        }
    }
    
    /**
     * Finaliza o combate
     */
    async finalizarCombate() {
        if (!confirm('Deseja finalizar o combate?')) {
            return;
        }
        
        try {
            await this.combateService.finalizar();
            Toast.success('Combate finalizado!');
            
            setTimeout(() => this.voltarParaConfiguracao(), 1500);
        } catch (error) {
            Toast.error('Erro ao finalizar combate');
            console.error(error);
        }
    }
    
    /**
     * Reseta todos os combatentes
     */
    async resetarCombate() {
        if (!confirm('Resetar todos os combatentes? (HP volta ao máximo)')) {
            return;
        }
        
        try {
            await this.combateService.resetar();
            Toast.success('Combate resetado!');
            
            setTimeout(() => this.voltarParaConfiguracao(), 1500);
        } catch (error) {
            Toast.error('Erro ao resetar combate');
            console.error(error);
        }
    }
    
    /**
     * Renderiza a arena
     */
    renderizarArena() {
        if (!this.combateAtual) return;
        
        // Atualizar rodada no header
        const rodadaElement = document.getElementById('rodadaAtual');
        if (rodadaElement) {
            rodadaElement.textContent = this.combateAtual.rodada_atual || 1;
        }
        
        // Renderizar ordem de iniciativa
        OrdemIniciativa.render(this.combateAtual);
        
        // Obter combatente ativo
        const combatenteAtivo = this.combateAtual.combatentes.find(
            c => c.id === this.combateAtual.combatente_ativo_id
        );
        
        // Renderizar combatente ativo
        CombatenteAtivoView.render(
            combatenteAtivo,
            (id, dano) => this.aplicarDano(id, dano),
            (id, cura) => this.aplicarCura(id, cura),
            (id) => this.aplicarCondicao(id)
        );
    }
    
    /**
     * Mostra a tela da arena
     */
    mostrarArena() {
        document.getElementById('telaConfiguracao').classList.remove('ativa');
        document.getElementById('telaArena').classList.add('ativa');
    }
    
    /**
     * Volta para a tela de configuração
     */
    voltarParaConfiguracao() {
        document.getElementById('telaArena').classList.remove('ativa');
        document.getElementById('telaConfiguracao').classList.add('ativa');
        
        // Disparar evento para recarregar lista
        const event = new CustomEvent('voltarConfiguracao');
        document.dispatchEvent(event);
    }
}