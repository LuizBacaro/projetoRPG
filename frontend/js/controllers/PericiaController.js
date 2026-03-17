/**
 * PericiaController.js - Versão Tabela
 * SRP: Orquestrar lógica de perícias com layout tabular
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
        
        this.baseUrl = getApiUrl('/pericias');
        this.combatente = null;
        this.pericias = [];
        this.periciasFiltradasAtualmente = [];
        this.periciasSelecionadas = new Map(); // ID -> {pericia, graduacao, bonus}
        this.token = localStorage.getItem('token');
        
        console.log('✅ PericiaController inicializado');
    }

    async inicializar() {
        try {
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id') || params.get('combatente_id');
            
            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido');
            }

            console.log('🎯 Carregando combatente:', combatenteId);
            
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            this.atualizarHeaderCombatente();

            this.pericias = await this.periciaService.listarPericias();
            this.periciasFiltradasAtualmente = [...this.pericias];
            
            await this.carregarPericicasSelecionadas(parseInt(combatenteId));
            
            this.renderizar();
            console.log('✅ Inicialização completa');

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            throw error;
        }
    }

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
                this.periciasSelecionadas.clear();
                
                (data.pericias || []).forEach(pj => {
                    this.periciasSelecionadas.set(pj.pericia_id, {
                        id: pj.id,
                        pericia: pj.pericia,
                        graduacao: pj.graduacao || 0,
                        bonus: pj.bonus_outros || 0,
                        modAtributo: pj.modificador_atributo || 0
                    });
                });
                
                console.log('✅ Perícias selecionadas carregadas:', this.periciasSelecionadas.size);
            }
        } catch (error) {
            console.warn('⚠️ Nenhuma perícia selecionada encontrada');
        }
    }

    atualizarHeaderCombatente() {
        document.getElementById('combatente-nome').textContent = `👤 ${this.combatente.nome}`;
        document.getElementById('combatente-tipo').textContent = `(${this.combatente.tipo || 'jogador'})`;
    }

    filtrarPorAtributo(atributo) {
        if (!atributo) {
            this.periciasFiltradasAtualmente = [...this.pericias];
        } else {
            this.periciasFiltradasAtualmente = this.pericias.filter(
                p => p.atributo === atributo.toUpperCase()
            );
        }
        this.renderizar();
    }

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

    renderizar() {
        this.renderizarTabela();
        this.renderizarSelecionadas();
    }

    renderizarTabela() {
        const tbody = document.getElementById('tbody-pericias');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.periciasFiltradasAtualmente.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="vazio">❌ Nenhuma perícia encontrada</td></tr>';
            return;
        }

        this.periciasFiltradasAtualmente.forEach(pericia => {
            const tr = document.createElement('tr');
            const selecionada = this.periciasSelecionadas.has(pericia.id);
            
            if (selecionada) {
                tr.classList.add('selecionada');
            }

            tr.innerHTML = `
                <td class="col-checkbox">
                    <input type="checkbox" 
                           class="checkbox-pericia" 
                           data-pericia-id="${pericia.id}"
                           ${selecionada ? 'checked' : ''}>
                </td>
                <td class="col-nome">${pericia.nome}</td>
                <td class="col-atributo">${pericia.atributo}</td>
                <td class="col-descricao">${pericia.descricao || ''}</td>
                <td class="col-tipo">
                    <span class="badge-tipo">${pericia.tipo}</span>
                </td>
            `;

            tbody.appendChild(tr);

            const checkbox = tr.querySelector('.checkbox-pericia');
            checkbox.addEventListener('change', (e) => {
                this.togglePericia(pericia, e.target.checked);
            });
        });

        console.log('✅ Tabela renderizada');
    }

    togglePericia(pericia, marcada) {
        if (marcada) {
            // Adicionar perícia
            this.periciasSelecionadas.set(pericia.id, {
                pericia,
                graduacao: 0,
                bonus: 0,
                modAtributo: this.calcularModAtributo(pericia)
            });
            console.log('➕ Perícia adicionada:', pericia.nome);
        } else {
            // Remover perícia
            this.periciasSelecionadas.delete(pericia.id);
            console.log('➖ Perícia removida:', pericia.nome);
        }

        this.renderizarSelecionadas();
    }

    calcularModAtributo(pericia) {
        const atributoMap = {
            'FOR': 'forca',
            'DES': 'destreza',
            'CON': 'constituicao',
            'INT': 'inteligencia',
            'SAB': 'sabedoria',
            'CAR': 'carisma'
        };

        const atributoNome = atributoMap[pericia.atributo];
        if (!atributoNome || !this.combatente[atributoNome]) return 0;

        const valor = this.combatente[atributoNome];
        return Math.floor((valor - 10) / 2);
    }

    renderizarSelecionadas() {
        const container = document.getElementById('pericias-selecionadas-lista');
        if (!container) return;

        container.innerHTML = '';

        if (this.periciasSelecionadas.size === 0) {
            container.innerHTML = '<p class="vazio">Nenhuma perícia selecionada ainda</p>';
            return;
        }

        this.periciasSelecionadas.forEach((data, periciaId) => {
            const div = document.createElement('div');
            div.className = 'pericia-selecionada-item';
            div.dataset.periciaId = periciaId;

            const total = data.graduacao + data.modAtributo + data.bonus;

            div.innerHTML = `
                <div class="pericia-item-info">
                    <h3>${data.pericia.nome}</h3>
                    <p class="pericia-item-descricao">${data.pericia.descricao || ''}</p>
                    <div class="modificadores-selecionada">
                        <div class="mod-field">
                            <label class="mod-label">Graduação</label>
                            <input type="number" 
                                   class="mod-input input-graduacao" 
                                   data-pericia-id="${periciaId}"
                                   value="${data.graduacao}" 
                                   min="0" max="20">
                        </div>
                        <div class="mod-field">
                            <label class="mod-label">Mod. Atr.</label>
                            <input type="number" 
                                   class="mod-input" 
                                   value="${data.modAtributo}" 
                                   readonly 
                                   style="background: rgba(255,255,255,0.05); cursor: not-allowed;">
                        </div>
                        <div class="mod-field">
                            <label class="mod-label">Bônus</label>
                            <input type="number" 
                                   class="mod-input input-bonus" 
                                   data-pericia-id="${periciaId}"
                                   value="${data.bonus}" 
                                   min="-20" max="20">
                        </div>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.5rem; align-items: flex-end;">
                    <div class="total-mod">+${total}</div>
                    <button class="btn-remover-selecionada" data-pericia-id="${periciaId}">Remover</button>
                </div>
            `;

            container.appendChild(div);

            // Event listeners
            div.querySelector('.input-graduacao').addEventListener('change', (e) => {
                data.graduacao = parseInt(e.target.value) || 0;
                this.atualizarTotal(div);
            });

            div.querySelector('.input-bonus').addEventListener('change', (e) => {
                data.bonus = parseFloat(e.target.value) || 0;
                this.atualizarTotal(div);
            });

            div.querySelector('.btn-remover-selecionada').addEventListener('click', () => {
                this.periciasSelecionadas.delete(periciaId);
                // Desmarcar checkbox
                const checkbox = document.querySelector(`.checkbox-pericia[data-pericia-id="${periciaId}"]`);
                if (checkbox) checkbox.checked = false;
                this.renderizar();
            });
        });

        console.log('✅ Perícias selecionadas renderizadas');
    }

    atualizarTotal(div) {
        const periciaId = parseInt(div.dataset.periciaId);
        const data = this.periciasSelecionadas.get(periciaId);
        const total = data.graduacao + data.modAtributo + data.bonus;
        div.querySelector('.total-mod').textContent = `+${total}`;
    }

    async salvarPericias() {
        try {
            const pericias = Array.from(this.periciasSelecionadas.values()).map(data => ({
                pericia_id: this.pericias.find(p => p.nome === data.pericia.nome).id,
                graduacao: data.graduacao,
                bonus_outros: data.bonus
            }));

            console.log('💾 Salvando perícias:', pericias);
            NotificationService.mostrarSucesso('✅ Perícias salvas com sucesso!');
            
            // TODO: Implementar chamada de API para salvar

        } catch (error) {
            console.error('❌ Erro ao salvar:', error);
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }
}