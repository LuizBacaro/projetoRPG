/**
 * PericiaController.js - VERSÃO MELHORADA
 * SRP: Orquestrar lógica de perícias com nova UI
 * SOLID: DIP via constructor injection
 */

import { API_CONFIG, getApiUrl } from '../config/api.config.js';
import { NotificationService } from '../services/NotificationService.js';
import { CombatenteService } from '../services/CombatenteService.js';
import { PericiaService } from '../services/PericiaService.js';

export class PericiaController {
    constructor() {
        this.apiConfig = API_CONFIG;
        this.combatenteService = new CombatenteService();
        this.periciaService = new PericiaService();
        
        // ➕ ADICIONAR ISTO:
        this.baseUrl = getApiUrl('/pericias');
        
        this.combatente = null;
        this.pericias = [];
        this.periciasFiltradasAtualmente = [];
        this.periciasSelecionadas = [];
        this.token = localStorage.getItem('token');
        
        console.log('✅ PericiaController inicializado');
    }

    /**
     * Inicializa o controller
     */
    async inicializar() {
        try {
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id') || params.get('combatente_id');
            
            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido');
            }

            console.log('🎯 Carregando combatente:', combatenteId);
            
            // Carregar combatente
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            this.atualizarHeaderCombatente();

            // Carregar perícias
            this.pericias = await this.periciaService.listarPericias();
            this.periciasFiltradasAtualmente = [...this.pericias];
            
            // Carregar perícias selecionadas
            await this.carregarPericicasSelecionadas(parseInt(combatenteId));
            
            // Renderizar
            this.renderizar();
            console.log('✅ Inicialização completa');

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            throw error;
        }
    }

    /**
     * Carrega perícias selecionadas do combatente
     */
    async carregarPericicasSelecionadas(combatenteId) {
        try {
            const url = `${this.baseUrl}/${combatenteId}/listar`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.periciasSelecionadas = data.pericias || [];
                console.log('✅ Perícias selecionadas carregadas:', this.periciasSelecionadas.length);
            }
        } catch (error) {
            console.warn('⚠️ Nenhuma perícia selecionada encontrada');
        }
    }

    /**
     * Atualiza o header com informações do combatente
     */
    atualizarHeaderCombatente() {
        document.getElementById('combatente-nome').textContent = `👤 ${this.combatente.nome}`;
        document.getElementById('combatente-tipo').textContent = `(${this.combatente.tipo || 'jogador'})`;
        console.log('✅ Header atualizado:', this.combatente.nome);
    }

    /**
     * Filtra perícias por atributo
     */
    async filtrarPorAtributo(atributo) {
        if (!atributo) {
            this.periciasFiltradasAtualmente = [...this.pericias];
        } else {
            this.periciasFiltradasAtualmente = this.pericias.filter(
                p => p.atributo === atributo.toUpperCase()
            );
        }
        this.renderizar();
    }

    /**
     * Busca perícias por termo
     */
    buscarPericias(termo) {
        if (!termo || termo.trim() === '') {
            this.periciasFiltradasAtualmente = [...this.pericias];
        } else {
            const termoLower = termo.toLowerCase();
            this.periciasFiltradasAtualmente = this.pericias.filter(p =>
                p.nome.toLowerCase().includes(termoLower) ||
                (p.descricao && p.descricao.toLowerCase().includes(termoLower))
            );
        }
        this.renderizar();
    }

    /**
     * Renderiza todas as perícias
     */
    renderizar() {
        this.renderizarPericiasDisponiveis();
        this.renderizarPericicasSelecionadas();
        this.atualizarEstatisticas();
    }

    /**
     * Renderiza perícias disponíveis
     */
    renderizarPericiasDisponiveis() {
        const container = document.getElementById('pericias-disponivel-grid');
        if (!container) return;

        container.innerHTML = '';

        if (this.periciasFiltradasAtualmente.length === 0) {
            container.innerHTML = '<p class="vazio">❌ Nenhuma perícia encontrada</p>';
            return;
        }

        this.periciasFiltradasAtualmente.forEach(pericia => {
            const jaAdicionada = this.periciasSelecionadas.some(p => p.pericia_id === pericia.id);
            const card = this.criarCardPericia(pericia, jaAdicionada);
            container.appendChild(card);
        });

        console.log('✅ Perícias disponíveis renderizadas:', this.periciasFiltradasAtualmente.length);
    }

    /**
     * Cria um card de perícia disponível
     */
    criarCardPericia(pericia, jaAdicionada) {
        const card = document.createElement('div');
        card.className = 'pericia-card-disponivel';
        if (jaAdicionada) card.style.opacity = '0.6';

        const header = document.createElement('div');
        header.className = 'pericia-header-disp';

        const nome = document.createElement('h3');
        nome.className = 'pericia-nome-disp';
        nome.textContent = pericia.nome;

        const atributo = document.createElement('span');
        atributo.className = 'pericia-atributo-badge';
        atributo.textContent = pericia.atributo;

        header.appendChild(nome);
        header.appendChild(atributo);
        card.appendChild(header);

        if (pericia.descricao) {
            const descricao = document.createElement('p');
            descricao.className = 'pericia-descricao-disp';
            descricao.textContent = pericia.descricao;
            card.appendChild(descricao);
        }

        if (!jaAdicionada) {
            const botao = document.createElement('button');
            botao.className = 'btn-adicionar';
            botao.textContent = '➕ Adicionar';
            botao.addEventListener('click', () => this.adicionarPericia(pericia));
            card.appendChild(botao);
        } else {
            const badge = document.createElement('span');
            badge.style.color = 'var(--cor-dourada)';
            badge.style.fontSize = '0.9rem';
            badge.style.fontWeight = 'bold';
            badge.textContent = '✅ Já adicionada';
            card.appendChild(badge);
        }

        return card;
    }

    /**
     * Renderiza perícias selecionadas
     */
    renderizarPericicasSelecionadas() {
        const container = document.getElementById('pericias-selecionada-grid');
        if (!container) return;

        container.innerHTML = '';

        if (this.periciasSelecionadas.length === 0) {
            container.innerHTML = '<p class="vazio">Nenhuma perícia adicionada ainda</p>';
            return;
        }

        this.periciasSelecionadas.forEach(pj => {
            const card = this.criarCardPericiaSelecionada(pj);
            container.appendChild(card);
        });

        console.log('✅ Perícias selecionadas renderizadas:', this.periciasSelecionadas.length);
    }

    /**
     * Cria um card de perícia selecionada
     */
    criarCardPericiaSelecionada(periciaJogador) {
        const card = document.createElement('div');
        card.className = 'pericia-card-selecionada';

        const header = document.createElement('div');
        header.className = 'pericia-selecionada-header';

        const nome = document.createElement('h3');
        nome.className = 'pericia-selecionada-nome';
        nome.textContent = periciaJogador.pericia.nome;

        const btnRemover = document.createElement('button');
        btnRemover.className = 'btn-remover-pericia';
        btnRemover.textContent = '❌ Remover';
        btnRemover.addEventListener('click', () => this.removerPericia(periciaJogador.id));

        header.appendChild(nome);
        header.appendChild(btnRemover);
        card.appendChild(header);

        // Grid de modificadores
        const grid = document.createElement('div');
        grid.className = 'modificadores-grid';

        // Graduação
        const divGraduacao = document.createElement('div');
        divGraduacao.className = 'modificador-item';
        divGraduacao.innerHTML = `
            <label class="modificador-label">Graduação</label>
            <input type="number" class="modificador-input input-graduacao" value="${periciaJogador.graduacao || 0}" min="0" max="20">
        `;
        grid.appendChild(divGraduacao);

        // Modificador de Atributo
        const divModAtributo = document.createElement('div');
        divModAtributo.className = 'modificador-item';
        divModAtributo.innerHTML = `
            <label class="modificador-label">Mod. Atributo</label>
            <input type="number" class="modificador-input input-mod-atributo" value="${periciaJogador.modificador_atributo || 0}" readonly style="background: rgba(255,255,255,0.05); cursor: not-allowed;">
        `;
        grid.appendChild(divModAtributo);

        // Bônus Outros
        const divBonus = document.createElement('div');
        divBonus.className = 'modificador-item';
        divBonus.innerHTML = `
            <label class="modificador-label">Bônus Outros</label>
            <input type="number" class="modificador-input input-bonus-outros" value="${periciaJogador.bonus_outros || 0}" min="-20" max="20">
        `;
        grid.appendChild(divBonus);

        // Total
        const divTotal = document.createElement('div');
        divTotal.className = 'modificador-item';
        divTotal.innerHTML = `
            <label class="modificador-label">Total</label>
            <input type="number" class="modificador-input input-total" value="${this.calcularTotal(periciaJogador)}" readonly style="background: rgba(255,215,0,0.1); font-size: 1.1rem;">
        `;
        grid.appendChild(divTotal);

        card.appendChild(grid);

        // Event listeners para atualizar total
        const inputsModificadores = card.querySelectorAll('.input-graduacao, .input-bonus-outros');
        inputsModificadores.forEach(input => {
            input.addEventListener('change', () => {
                const novoTotal = 
                    parseInt(card.querySelector('.input-graduacao').value || 0) +
                    parseFloat(card.querySelector('.input-mod-atributo').value || 0) +
                    parseFloat(card.querySelector('.input-bonus-outros').value || 0);
                card.querySelector('.input-total').value = novoTotal.toFixed(1);
                this.atualizarEstatisticas();
            });
        });

        return card;
    }

    /**
     * Calcula o total de modificadores
     */
    calcularTotal(periciaJogador) {
        return periciaJogador.graduacao + periciaJogador.modificador_atributo + (periciaJogador.bonus_outros || 0);
    }

    /**
     * Adiciona uma perícia
     */
    async adicionarPericia(pericia) {
        try {
            const url = `${this.baseUrl}/${this.combatente.id}/adicionar`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    pericia_id: pericia.id,
                    graduacao: 0,
                    bonus_outros: 0
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao adicionar perícia');
            }

            NotificationService.mostrarSucesso(`✅ "${pericia.nome}" adicionada!`);
            
            // Recarregar perícias
            await this.carregarPericicasSelecionadas(this.combatente.id);
            this.renderizar();

        } catch (error) {
            console.error('❌ Erro ao adicionar perícia:', error);
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    /**
     * Remove uma perícia
     */
    async removerPericia(periciaJogadorId) {
        if (!confirm('Tem certeza que deseja remover esta perícia?')) return;

        try {
            const url = `${this.baseUrl}/${this.combatente.id}/pericia/${periciaJogadorId}`;
            
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao remover perícia');
            }

            NotificationService.mostrarSucesso('✅ Perícia removida!');
            
            // Recarregar perícias
            await this.carregarPericicasSelecionadas(this.combatente.id);
            this.renderizar();

        } catch (error) {
            console.error('❌ Erro ao remover perícia:', error);
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    /**
     * Atualiza estatísticas
     */
    atualizarEstatisticas() {
        const total = this.periciasSelecionadas.length;
        const pontos = this.periciasSelecionadas.reduce((sum, p) => sum + (p.graduacao || 0), 0);

        const statTotal = document.getElementById('stat-total');
        const statGastos = document.getElementById('stat-gastos');

        if (statTotal) statTotal.textContent = total;
        if (statGastos) statGastos.textContent = pontos;

        console.log('✅ Estatísticas atualizadas');
    }
}