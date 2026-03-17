/**
 * PericiaController.js
 * SRP: Orquestrar a lógica de perícias
 * SOLID: DIP via constructor injection
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

    async inicializar() {
        try {
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');
            
            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido na URL');
            }

            console.log('🎯 Inicializando para combatente:', combatenteId);

            // Carregar combatente
            this.combatente = await this.combatenteService.obterCombatente(combatenteId);
            console.log('✅ Combatente carregado:', this.combatente.nome);

            // Carregar perícias
            this.pericias = await this.listarPericias();
            console.log('✅ Perícias carregadas:', this.pericias.length);

            // Carregar perícias do jogador
            const resultado = await this.listarPericiasJogador(combatenteId);
            this.periciasSelecionadas = resultado.pericias || [];
            console.log('✅ Perícias do jogador carregadas:', this.periciasSelecionadas.length);

            // Renderizar
            this.renderizar();
            NotificationService.mostrarSucesso(`Bem-vindo, ${this.combatente.nome}!`);

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error.message);
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    // ========== MÉTODOS DE PERÍCIA ==========

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
            console.log('✅ Perícias do jogador recebidas:', data.pericias.length);
            return data;

        } catch (error) {
            console.error('❌ Erro em listarPericiasJogador:', error);
            throw error;
        }
    }

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

    renderizar() {
        this.renderizarPericias();
        this.renderizarPericiasJogador();
        this.atualizarEstatisticas();
    }

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

        document.querySelectorAll('.btn-adicionar-pericia').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.abrirModalAdicionar(e.target.dataset.periciaId);
            });
        });
    }

    renderizarPericiasJogador() {
        const container = document.getElementById('pericias-jogador');
        if (!container) return;

        container.innerHTML = '';

        if (this.periciasSelecionadas.length === 0) {
            container.innerHTML = '<p class="vazio">Nenhuma perícia adicionada</p>';
            return;
        }

        this.periciasSelecionadas.forEach(pj => {
            const totalMod = pj.graduacao + pj.modificador_atributo + pj.bonus_outros;
            
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

        document.querySelectorAll('.btn-remover-pj').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.removerPericiaJogador(e.target.dataset.pjId);
            });
        });
    }

    abrirModalAdicionar(periciaId) {
        const pericia = this.pericias.find(p => p.id === parseInt(periciaId));
        if (!pericia) return;

        const modal = document.getElementById('modal-adicionar-pericia');
        document.getElementById('modal-pericia-nome').textContent = pericia.nome;

        modal.querySelector('form').onsubmit = (e) => {
            e.preventDefault();
            this.adicionarPericia(periciaId);
        };

        modal.classList.add('show');
    }

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
            
            const resultado = await this.listarPericiasJogador(this.combatente.id);
            this.periciasSelecionadas = resultado.pericias || [];
            this.renderizar();

        } catch (error) {
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    async removerPericiaJogador(periciaJogadorId) {
        if (!confirm('Remover perícia?')) return;

        try {
            await this.deletarPericiaJogador(this.combatente.id, periciaJogadorId);
            NotificationService.mostrarSucesso('Perícia removida!');
            
            const resultado = await this.listarPericiasJogador(this.combatente.id);
            this.periciasSelecionadas = resultado.pericias || [];
            this.renderizar();

        } catch (error) {
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    atualizarEstatisticas() {
        const statsDiv = document.getElementById('pericias-stats');
        if (!statsDiv) return;

        const pontos_gastos = this.periciasSelecionadas.reduce((sum, p) => sum + p.graduacao, 0);
        const pontos_disponiveis = (this.combatente.nivel * 3) - pontos_gastos;

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
    }
}