/**
 * PericiaController.js
 * SRP: Orquestrar a lógica de perícias
 * SOLID: DIP via constructor injection de services
 */

import { API_CONFIG, getApiUrl } from '../config/api.config.js';
import { NotificationService } from '../services/NotificationService.js';
import { CombatenteService } from '../services/CombatenteService.js';

export class PericiaController {
    constructor() {
        this.apiConfig = API_CONFIG;
        this.combatenteService = new CombatenteService();
        this.pericias = [];
        this.combatente = null;
        this.periciasSelecionadas = [];
        this.token = localStorage.getItem('token');
        console.log('✅ PericiaController inicializado');
    }

    /**
     * Inicializa o controller carregando todos os dados
     * SRP: Apenas orquestra o carregamento
     */
    async inicializar() {
        try {
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');
            
            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido na URL');
            }

            console.log('🎯 Inicializando para combatente:', combatenteId);

            // 1. Carregar combatente (✅ FUNÇÃO CORRIGIDA)
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            console.log('✅ Combatente carregado:', this.combatente.nome);

            // 2. Carregar perícias disponíveis
            this.pericias = await this.listarPericias();
            console.log('✅ Perícias carregadas:', this.pericias.length);

            // 3. Carregar perícias do jogador
            const resultado = await this.listarPericiasJogador(parseInt(combatenteId));
            this.periciasSelecionadas = resultado.pericias || [];
            console.log('✅ Perícias do jogador carregadas:', this.periciasSelecionadas.length);

            // 4. Renderizar interface
            this.renderizar();
            NotificationService.mostrarSucesso(`Bem-vindo, ${this.combatente.nome}!`);

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error.message);
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    // ========== MÉTODOS DE PERÍCIA ==========

    /**
     * Lista todas as perícias disponíveis
     * @param {number} skip
     * @param {number} limit
     * @param {string|null} atributo - filtro por atributo
     * @returns {Promise<Array>}
     */
    async listarPericias(skip = 0, limit = 100, atributo = null) {
        try {
            let url = getApiUrl(this.apiConfig.ENDPOINTS.PERICIAS);
            url += `?skip=${skip}&limit=${limit}`;
            if (atributo) url += `&atributo=${atributo}`;

            console.log('📡 GET:', url);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ Perícias recebidas:', data.length);
            return data;

        } catch (error) {
            console.error('❌ Erro em listarPericias:', error);
            throw error;
        }
    }

    /**
     * Lista perícias do jogador
     * @param {number} combatenteId
     * @returns {Promise<Object>}
     */
    async listarPericiasJogador(combatenteId) {
        try {
            const url = getApiUrl(`${this.apiConfig.ENDPOINTS.PERICIAS}/${combatenteId}/listar`);
            console.log('📡 GET:', url);

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('✅ Perícias do jogador recebidas:', data.pericias?.length || 0);
            return data;

        } catch (error) {
            console.error('❌ Erro em listarPericiasJogador:', error);
            throw error;
        }
    }

    /**
     * Adiciona uma perícia ao jogador
     * @param {number} combatenteId
     * @param {Object} periciaJogadorData
     * @returns {Promise<Object>}
     */
    async adicionarPericiaJogador(combatenteId, periciaJogadorData) {
        try {
            const url = getApiUrl(`${this.apiConfig.ENDPOINTS.PERICIAS}/${combatenteId}/adicionar`);
            console.log('📡 POST:', url, periciaJogadorData);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify(periciaJogadorData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log('✅ Perícia adicionada');
            return data;

        } catch (error) {
            console.error('❌ Erro em adicionarPericiaJogador:', error);
            throw error;
        }
    }

    /**
     * Deleta uma perícia do jogador
     * @param {number} combatenteId
     * @param {number} periciaJogadorId
     * @returns {Promise<void>}
     */
    async deletarPericiaJogador(combatenteId, periciaJogadorId) {
        try {
            const url = getApiUrl(`${this.apiConfig.ENDPOINTS.PERICIAS}/${combatenteId}/pericia/${periciaJogadorId}`);
            console.log('📡 DELETE:', url);

            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            console.log('✅ Perícia deletada');

        } catch (error) {
            console.error('❌ Erro em deletarPericiaJogador:', error);
            throw error;
        }
    }

    // ========== RENDERIZAÇÃO ==========

    /**
     * Renderiza toda a interface
     * SRP: Orquestra a renderização
     */
    renderizar() {
        this.renderizarPericias();
        this.renderizarPericiasJogador();
        this.atualizarEstatisticas();
    }

    /**
     * Renderiza a lista de perícias disponíveis
     * SRP: Apenas renderiza perícias
     */
    renderizarPericias() {
        const container = document.getElementById('pericias-disponiveis');
        if (!container) {
            console.error('❌ Container pericias-disponiveis não encontrado');
            return;
        }

        container.innerHTML = '';

        this.pericias.forEach(pericia => {
            const jaAdicionada = this.periciasSelecionadas.some(p => p.pericia_id === pericia.id);
            
            const card = document.createElement('div');
            card.className = `pericia-card ${jaAdicionada ? 'adicionada' : ''}`;
            card.innerHTML = `
                <div class="pericia-header">
                    <h3>${pericia.nome}</h3>
                    <span class="pericia-atributo">${pericia.atributo}</span>
                </div>
                <p class="pericia-descricao">${pericia.descricao || 'Sem descrição'}</p>
                ${!jaAdicionada ? `
                    <button class="btn-adicionar-pericia" data-pericia-id="${pericia.id}">
                        + Adicionar
                    </button>
                ` : `
                    <span class="badge-adicionada">✓ Adicionada</span>
                `}
            `;

            container.appendChild(card);
        });

        // Event listeners para adicionar perícia
        document.querySelectorAll('.btn-adicionar-pericia').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.abrirModalAdicionar(e.target.dataset.periciaId);
            });
        });

        console.log('✅ Perícias renderizadas');
    }

    /**
     * Renderiza as perícias do jogador
     * SRP: Apenas renderiza perícias do jogador
     */
    renderizarPericiasJogador() {
        const container = document.getElementById('pericias-jogador');
        if (!container) return;

        container.innerHTML = '';

        if (this.periciasSelecionadas.length === 0) {
            container.innerHTML = '<p class="vazio">Nenhuma perícia adicionada</p>';
            return;
        }

        this.periciasSelecionadas.forEach(pj => {
            const totalMod = pj.graduacao + (pj.modificador_atributo || 0) + (pj.bonus_outros || 0);
            
            const card = document.createElement('div');
            card.className = 'pericia-jogador-card';
            card.innerHTML = `
                <div class="pj-header">
                    <h4>${pj.pericia.nome}</h4>
                    <span class="pj-total-mod">${totalMod >= 0 ? '+' : ''}${totalMod}</span>
                </div>
                <div class="pj-actions">
                    <button class="btn-remover-pj" data-pj-id="${pj.id}">Remover</button>
                </div>
            `;

            container.appendChild(card);
        });

        // Event listeners para remover perícia
        document.querySelectorAll('.btn-remover-pj').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.removerPericiaJogador(e.target.dataset.pjId);
            });
        });

        console.log('✅ Perícias do jogador renderizadas');
    }

    /**
     * Abre o modal de adicionar perícia
     * @param {number} periciaId
     */
    abrirModalAdicionar(periciaId) {
        const pericia = this.pericias.find(p => p.id === parseInt(periciaId));
        if (!pericia) {
            console.error('❌ Perícia não encontrada');
            return;
        }

        const modal = document.getElementById('modal-adicionar-pericia');
        const form = modal?.querySelector('form');

        if (!modal || !form) {
            console.error('❌ Modal ou form não encontrado');
            return;
        }

        document.getElementById('modal-pericia-nome').textContent = pericia.nome;

        form.onsubmit = (e) => {
            e.preventDefault();
            this.adicionarPericia(periciaId);
        };

        modal.classList.add('show');
        console.log('✅ Modal aberto para perícia:', pericia.nome);
    }

    /**
     * Adiciona uma perícia ao jogador via modal
     * @param {number} periciaId
     */
    async adicionarPericia(periciaId) {
        try {
            const graduacao = parseInt(document.getElementById('input-graduacao').value) || 0;
            const bonusOutros = parseFloat(document.getElementById('input-bonus-outros').value) || 0;

            await this.adicionarPericiaJogador(this.combatente.id, {
                pericia_id: parseInt(periciaId),
                graduacao,
                bonus_outros: bonusOutros
            });

            NotificationService.mostrarSucesso('Perícia adicionada!');
            document.getElementById('modal-adicionar-pericia').classList.remove('show');
            
            // Recarregar perícias do jogador
            const resultado = await this.listarPericiasJogador(this.combatente.id);
            this.periciasSelecionadas = resultado.pericias || [];
            this.renderizar();

        } catch (error) {
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    /**
     * Remove uma perícia do jogador
     * @param {number} periciaJogadorId
     */
    async removerPericiaJogador(periciaJogadorId) {
        if (!confirm('Remover perícia?')) return;

        try {
            await this.deletarPericiaJogador(this.combatente.id, periciaJogadorId);
            NotificationService.mostrarSucesso('Perícia removida!');
            
            // Recarregar perícias do jogador
            const resultado = await this.listarPericiasJogador(this.combatente.id);
            this.periciasSelecionadas = resultado.pericias || [];
            this.renderizar();

        } catch (error) {
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    /**
     * Atualiza e exibe estatísticas de perícias
     * SRP: Apenas atualiza estatísticas
     */
    atualizarEstatisticas() {
        const statsDiv = document.getElementById('pericias-stats');
        if (!statsDiv) return;

        const pontos_gastos = this.periciasSelecionadas.reduce((sum, p) => sum + (p.graduacao || 0), 0);
        const pontos_disponiveis = ((this.combatente.nivel || 1) * 3) - pontos_gastos;

        statsDiv.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total:</span>
                <span class="stat-valor">${this.periciasSelecionadas.length}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Pontos Gastos:</span>
                <span class="stat-valor">${pontos_gastos}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Disponíveis:</span>
                <span class="stat-valor">${pontos_disponiveis}</span>
            </div>
        `;

        console.log('✅ Estatísticas atualizadas');
    }
}