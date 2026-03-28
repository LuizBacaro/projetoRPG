/**
 * PericiaFichaController.js
 * Controller especializado para página de perícias com estilo ficha-personagem
 * Calcula custos baseado em classe (1 ponto se da classe, 2 se não é)
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { PericiaService } from '../services/PericiaService.js';
import { NotificationService } from '../services/NotificationService.js';

export class PericiaFichaController {
    constructor() {
        this.combatenteService = new CombatenteService();
        this.periciaService = new PericiaService();
        this.combatente = null;
        this.pericias = [];
        this.periciasFiltradas = [];
        this.periciasAdicionadas = new Map();
        this.token = localStorage.getItem('token') || sessionStorage.getItem('token');
        console.log('✅ PericiaFichaController inicializado');
    }

    async inicializar() {
        try {
            // Obter ID do combatente da URL
            const params = new URLSearchParams(window.location.search);
            const combatenteId = params.get('combatente_id');

            if (!combatenteId) {
                throw new Error('ID do combatente não fornecido na URL');
            }

            console.log('🎯 Carregando combatente:', combatenteId);
            
            // Carregar combatente
            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            console.log('✅ Combatente carregado:', this.combatente.nome);

            // Atualizar header
            this.atualizarHeader();

            // Carregar perícias disponíveis
            const classe = this.combatente.classe || 'Guerreiro';
            this.pericias = await this.periciaService.listarPericiasComCusto(classe, 0, 100);
            console.log(`✅ Perícias carregadas: ${this.pericias.length}`);

            // Carregar perícias já adicionadas
            await this.carregarPericiasAdicionadas(parseInt(combatenteId));

            // Renderizar tabela
            this.periciasFiltradas = [...this.pericias];
            this.renderizar();

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            NotificationService.erro('❌ ' + error.message);
            throw error;
        }
    }

    atualizarHeader() {
        const nome = this.combatente?.nome || 'Desconhecido';
        const classe = this.combatente?.classe || 'Guerreiro';
        const pontos = this.combatente?.pontos || 0;

        document.getElementById('pericias-combatente-nome').textContent = nome;
        document.getElementById('pericias-combatente-classe').textContent = classe;
        document.getElementById('pericias-pontos-disponiveis').textContent = pontos;
    }

    async carregarPericiasAdicionadas(combatenteId) {
        try {
            const url = `${this.periciaService.baseUrl}/${combatenteId}/listar`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.pericias && Array.isArray(data.pericias)) {
                    data.pericias.forEach(p => {
                        this.periciasAdicionadas.set(p.pericia_id, {
                            id: p.id,
                            graduacao: p.graduacao,
                            modificador_atributo: p.modificador_atributo || 0,
                            bonus: p.bonus_outros || 0,
                            total: (p.graduacao || 0) + (p.modificador_atributo || 0) + (p.bonus_outros || 0)
                        });
                    });
                    console.log(`✅ ${this.periciasAdicionadas.size} perícias já adicionadas`);
                }
            }
        } catch (error) {
            console.error('⚠️ Erro ao carregar perícias adicionadas:', error);
        }
    }

    filtrar() {
        const termo = document.getElementById('pericias-busca').value.toLowerCase();
        
        if (!termo) {
            this.periciasFiltradas = [...this.pericias];
        } else {
            this.periciasFiltradas = this.pericias.filter(p =>
                p.nome.toLowerCase().includes(termo) ||
                (p.descricao && p.descricao.toLowerCase().includes(termo))
            );
        }

        this.renderizar();
    }

    renderizar() {
        const tbody = document.getElementById('pericias-tbody');
        const tabela = document.getElementById('pericias-tabela');
        const loading = document.getElementById('pericias-loading');

        if (!tbody || !tabela) return;

        loading.style.display = 'none';
        tbody.innerHTML = '';

        if (this.periciasFiltradas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="pericias-vazio">❌ Nenhuma perícia encontrada</td></tr>';
            tabela.style.display = 'table';
            return;
        }

        this.periciasFiltradas.forEach(pericia => {
            const custo = pericia.custo_para_classe || 1;
            const isClasse = custo === 1;
            const adicionada = this.periciasAdicionadas.has(pericia.id);
            const dados = adicionada ? this.periciasAdicionadas.get(pericia.id) : null;

            const tr = document.createElement('tr');
            tr.dataset.periciaId = pericia.id;

            tr.innerHTML = `
                <td>
                    <div class="pericias-nome">${pericia.nome}</div>
                    <div class="pericias-descricao">${pericia.descricao || 'Sem descrição'}</div>
                </td>
                <td class="pericias-atributo">${pericia.atributo}</td>
                <td class="pericias-custo ${isClasse ? 'classe' : 'nao-classe'}">
                    ${custo} pt${custo > 1 ? 's' : ''}
                    <div style="font-size: 0.75rem; margin-top: 2px;">
                        ${isClasse ? '✓ Classe' : '✗ Não'}
                    </div>
                </td>
                <td>
                    <input type="number" class="pericias-input input-grad"
                           data-pericia-id="${pericia.id}"
                           min="0" max="20"
                           value="${dados ? dados.graduacao : 0}"
                           ${!adicionada ? 'disabled' : ''}>
                </td>
                <td>
                    <input type="number" class="pericias-input input-bonus"
                           data-pericia-id="${pericia.id}"
                           min="0" max="20"
                           value="${dados ? dados.bonus : 0}"
                           ${!adicionada ? 'disabled' : ''}>
                </td>
                <td style="text-align: center; font-weight: bold; min-width: 50px;">
                    ${adicionada
                        ? `${dados.total}`
                        : '-'
                    }
                </td>
                <td style="text-align: center;">
                    ${adicionada
                        ? `<button class="pericias-btn-adicionar" onclick="window.periciasFichaController.removerPericia(${pericia.id}, this)">🗑️</button>`
                        : `<button class="pericias-btn-adicionar" onclick="window.periciasFichaController.adicionarPericia(${pericia.id}, this)">➕</button>`
                    }
                </td>
            `;

            tbody.appendChild(tr);
        });

        tabela.style.display = 'table';
    }

    async adicionarPericia(periciaId, btnElement) {
        try {
            const tr = btnElement.closest('tr');
            const inputGrad = tr.querySelector('.input-grad');
            const graduacao = parseInt(inputGrad.value) || 0;

            const classe = this.combatente?.classe || 'Guerreiro';

            console.log(`📝 Adicionando perícia ${periciaId} com ${graduacao} graduação...`);

            btnElement.disabled = true;
            btnElement.textContent = '⏳';

            const response = await this.periciaService.adicionarPericia(
                this.combatente.id,
                periciaId,
                graduacao,
                classe
            );

            console.log('✅ Perícia adicionada:', response);

            // Marcar como adicionada
            this.periciasAdicionadas.set(periciaId, {
                id: response.id,
                graduacao: response.graduacao,
                modificador_atributo: response.modificador_atributo || 0,
                bonus: response.bonus_outros || 0,
                total: (response.graduacao || 0) + (response.modificador_atributo || 0) + (response.bonus_outros || 0)
            });

            // Recarregar combatente para atualizar pontos
            this.combatente = await this.combatenteService.obterCombatente(this.combatente.id);
            this.atualizarHeader();

            // Re-renderizar
            this.renderizar();

            NotificationService.sucesso('✅ Perícia adicionada com sucesso!');

        } catch (error) {
            console.error('❌ Erro ao adicionar perícia:', error);
            NotificationService.erro('❌ ' + error.message);
        }
    }

    async removerPericia(periciaId, btnElement) {
        try {
            if (!confirm('Tem certeza que deseja remover essa perícia?')) {
                return;
            }

            const dados = this.periciasAdicionadas.get(periciaId);
            if (!dados) return;

            console.log(`🗑️ Removendo perícia ${periciaId}...`);

            btnElement.disabled = true;
            btnElement.textContent = '⏳';

            // Chamar API para remover
            const url = `${this.periciaService.baseUrl}/${this.combatente.id}/pericia/${dados.id}`;
            const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            console.log('✅ Perícia removida');

            // Remover do mapa
            this.periciasAdicionadas.delete(periciaId);

            // Recarregar combatente
            this.combatente = await this.combatenteService.obterCombatente(this.combatente.id);
            this.atualizarHeader();

            // Re-renderizar
            this.renderizar();

            NotificationService.sucesso('✅ Perícia removida com sucesso!');

        } catch (error) {
            console.error('❌ Erro ao remover perícia:', error);
            NotificationService.erro('❌ ' + error.message);
        }
    }
}
