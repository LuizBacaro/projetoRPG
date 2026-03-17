/**
 * PericiaController.js - REFATORADO
 * SRP: Orquestrar lógica de perícias
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
        
        this.combatente = null;
        this.pericias = [];
        this.periciasFiltradasAtualmente = [];
        this.token = localStorage.getItem('token');
        
        console.log('✅ PericiaController inicializado');
    }

    /**
     * Inicializa o controller carregando dados
     */
    async inicializar() {
        try {
            const params = new URLSearchParams(window.location.search);
            // ✅ CORRIGIDO: Aceita 'id' OU 'combatente_id'
            const combatenteId = params.get('id') || params.get('combatente_id');
            
            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido na URL');
            }

            console.log('🎯 Carregando combatente:', combatenteId);
            
            // Carregar combatente
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            this.atualizarHeaderCombatente();

            // Carregar perícias
            this.pericias = await this.periciaService.listarPericias();
            this.periciasFiltradasAtualmente = [...this.pericias];
            
            // Renderizar
            this.renderizar();
            console.log('✅ Inicialização completa');

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            throw error;
        }
    }

    /**
     * Atualiza o header com informações do combatente
     */
    atualizarHeaderCombatente() {
        const nomeElement = document.getElementById('combatente-nome');
        const tipoElement = document.getElementById('combatente-tipo');

        if (nomeElement) {
            nomeElement.textContent = `👤 ${this.combatente.nome}`;
        }
        if (tipoElement) {
            tipoElement.textContent = `(${this.combatente.tipo || 'jogador'})`;
        }

        console.log('✅ Header atualizado:', this.combatente.nome);
    }

    /**
     * Filtra perícias por atributo
     */
    async filtrarPorAtributo(atributo) {
        try {
            if (!atributo) {
                this.periciasFiltradasAtualmente = [...this.pericias];
            } else {
                this.periciasFiltradasAtualmente = this.pericias.filter(
                    p => p.atributo === atributo.toUpperCase()
                );
            }

            this.renderizar();
            console.log('✅ Filtrado por atributo:', atributo || 'Todas');

        } catch (error) {
            console.error('❌ Erro ao filtrar:', error);
            NotificationService.mostrarErro('Erro ao filtrar perícias');
        }
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
        console.log('✅ Busca realizada:', termo);
    }

    /**
     * Renderiza todas as perícias
     */
    renderizar() {
        const container = document.getElementById('pericias-container');
        if (!container) {
            console.error('❌ Container não encontrado');
            return;
        }

        // Agrupar por atributo
        const grupos = this.periciaService.agruparPorAtributo(this.periciasFiltradasAtualmente);
        
        container.innerHTML = '';

        const atributosOrdenados = ['FOR', 'DES', 'CON', 'INT', 'SAB', 'CAR'];

        atributosOrdenados.forEach(atributo => {
            const pericias = grupos[atributo];
            if (pericias.length === 0) return;

            const info = this.periciaService.obterInfoAtributo(atributo);
            
            const secao = document.createElement('section');
            secao.className = 'pericias-secao';
            
            const titulo = document.createElement('h2');
            titulo.className = 'secao-titulo';
            titulo.textContent = `${info.emoji} ${info.label} (${atributo})`;
            secao.appendChild(titulo);

            const grid = document.createElement('div');
            grid.className = 'pericias-grid';

            pericias.forEach(pericia => {
                const card = this.criarCardPericia(pericia);
                grid.appendChild(card);
            });

            secao.appendChild(grid);
            container.appendChild(secao);
        });

        if (this.periciasFiltradasAtualmente.length === 0) {
            container.innerHTML = '<p class="vazio">❌ Nenhuma perícia encontrada</p>';
        }

        console.log('✅ Renderização completa:', this.periciasFiltradasAtualmente.length);
    }

    /**
     * Cria um card de perícia
     */
    criarCardPericia(pericia) {
        const card = document.createElement('div');
        card.className = 'pericia-card';

        const header = document.createElement('div');
        header.className = 'pericia-header';

        const nome = document.createElement('h3');
        nome.className = 'pericia-nome';
        nome.textContent = pericia.nome;

        const atributo = document.createElement('span');
        atributo.className = 'pericia-atributo';
        atributo.textContent = pericia.atributo;

        header.appendChild(nome);
        header.appendChild(atributo);
        card.appendChild(header);

        if (pericia.descricao) {
            const descricao = document.createElement('p');
            descricao.className = 'pericia-descricao';
            descricao.textContent = pericia.descricao;
            card.appendChild(descricao);
        }

        if (pericia.tipo) {
            const tipo = document.createElement('span');
            tipo.className = 'pericia-tipo';
            tipo.textContent = pericia.tipo;
            card.appendChild(tipo);
        }

        const botao = document.createElement('button');
        botao.className = 'btn-adicionar-pericia';
        botao.textContent = '➕ Adicionar';
        botao.addEventListener('click', () => this.adicionarPericia(pericia));
        card.appendChild(botao);

        return card;
    }

    /**
     * Adiciona uma perícia (placeholder para futura integração)
     */
    async adicionarPericia(pericia) {
        console.log('➕ Período clicada:', pericia.nome);
        NotificationService.mostrarSucesso(`Perícia "${pericia.nome}" selecionada!`);
        // TODO: Integrar com backend para salvar
    }
}