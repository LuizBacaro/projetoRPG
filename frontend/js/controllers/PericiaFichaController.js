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
        this.operacoesEmAndamento = new Set();
        this.token = localStorage.getItem('token');
        console.log('✅ PericiaFichaController inicializado');
    }

    _chaveOperacao(tipo, periciaId) {
        return `${tipo}:${periciaId}`;
    }

    _iniciarOperacao(tipo, periciaId) {
        const chave = this._chaveOperacao(tipo, periciaId);
        if (this.operacoesEmAndamento.has(chave)) {
            return false;
        }
        this.operacoesEmAndamento.add(chave);
        return true;
    }

    _finalizarOperacao(tipo, periciaId) {
        this.operacoesEmAndamento.delete(this._chaveOperacao(tipo, periciaId));
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

            // Carregar perícias disponíveis
            const classe = this.combatente.classe || 'Guerreiro';
            this.pericias = await this.periciaService.listarPericiasComCusto(classe, 0, 100);
            console.log(`✅ Perícias carregadas: ${this.pericias.length}`);

            // Carregar perícias já adicionadas
            await this.carregarPericiasAdicionadas(parseInt(combatenteId));

            // Atualizar header (após carregar perícias e adicionadas para calcular pontos)
            this.atualizarHeader();

            // Renderizar tabela
            this.periciasFiltradas = [...this.pericias];
            this.renderizar();

        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            NotificationService.mostrarErro('❌ ' + error.message);
            throw error;
        }
    }

    atualizarHeader() {
        const nome = this.combatente?.nome || 'Desconhecido';
        const classe = this.combatente?.classe || 'Guerreiro';
        const pontosGastos = this._calcularPontosGastos();

        document.getElementById('pericias-combatente-nome').textContent = nome;
        document.getElementById('pericias-combatente-classe').textContent = classe;
        document.getElementById('pericias-pontos-disponiveis').textContent = pontosGastos;
    }

    _calcularPontosGastos() {
        let total = 0;
        for (const [periciaId, dados] of this.periciasAdicionadas) {
            const pericia = this.pericias.find(p => p.id === periciaId);
            const custo = pericia?.custo_para_classe || 1;
            total += (dados.graduacao || 0) * custo;
        }
        return total;
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
            tbody.innerHTML = '<tr><td colspan="8" class="pericias-vazio">❌ Nenhuma perícia encontrada</td></tr>';
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
                           style="text-align: center;"
                           ${!adicionada ? 'disabled' : ''}>
                </td>
                <td style="text-align: center; font-weight: bold;">
                    ${adicionada ? (dados.modificador_atributo >= 0 ? '+' : '') + dados.modificador_atributo.toFixed(0) : '-'}
                </td>
                <td>
                    <input type="number" class="pericias-input input-bonus"
                           data-pericia-id="${pericia.id}"
                           min="0" max="20"
                           value="${dados ? dados.bonus : 0}"
                           style="text-align: center;"
                           ${!adicionada ? 'disabled' : ''}>
                </td>
                <td style="text-align: center; font-weight: bold; min-width: 50px;">
                    ${adicionada
                        ? `${dados.total >= 0 ? '+' : ''}${dados.total}`
                        : '-'
                    }
                </td>
                <td style="text-align: center;">
                    ${adicionada
                        ? `<button class="pericias-btn-adicionar" data-action="remover" data-pericia-id="${pericia.id}">🗑️</button>`
                        : `<button class="pericias-btn-adicionar" data-action="adicionar" data-pericia-id="${pericia.id}">➕</button>`
                    }
                </td>
            `;

            tbody.appendChild(tr);
        });

        tabela.style.display = 'table';

        // Adicionar event listeners para atualizar valores
        this.adicionarEventListenersEdicao();

        tbody.querySelectorAll('.pericias-btn-adicionar').forEach((button) => {
            button.addEventListener('click', () => {
                const periciaId = Number(button.dataset.periciaId);
                if (!Number.isFinite(periciaId)) return;

                if (button.dataset.action === 'remover') {
                    this.removerPericia(periciaId, button);
                    return;
                }

                this.adicionarPericia(periciaId, button);
            });
        });
    }

    adicionarEventListenersEdicao() {
        const self = this;

        // Event listeners para graduação
        document.querySelectorAll('.input-grad').forEach(input => {
            input.addEventListener('change', async function() {
                const periciaId = parseInt(this.dataset.periciaId);
                const novaGraduacao = parseInt(this.value) || 0;

                if (self.periciasAdicionadas.has(periciaId)) {
                    const dados = self.periciasAdicionadas.get(periciaId);
                    await self.atualizarPericiaNoBackend(
                        self.combatente.id,
                        dados.id,
                        novaGraduacao,
                        dados.bonus
                    );
                }
            });
        });

        // Event listeners para bônus
        document.querySelectorAll('.input-bonus').forEach(input => {
            input.addEventListener('change', async function() {
                const periciaId = parseInt(this.dataset.periciaId);
                const novoBonus = parseFloat(this.value) || 0;

                if (self.periciasAdicionadas.has(periciaId)) {
                    const dados = self.periciasAdicionadas.get(periciaId);
                    await self.atualizarPericiaNoBackend(
                        self.combatente.id,
                        dados.id,
                        dados.graduacao,
                        novoBonus
                    );
                }
            });
        });
    }

    async atualizarPericiaNoBackend(combatenteId, periciaJogadorId, graduacao, bonusOutros) {
        try {
            const response = await this.periciaService.atualizarPericia(
                combatenteId,
                periciaJogadorId,
                graduacao,
                bonusOutros
            );

            // Atualizar o mapa local
            const periciaId = Array.from(this.periciasAdicionadas).find(
                ([_, dados]) => dados.id === periciaJogadorId
            )?.[0];

            if (periciaId) {
                const dados = this.periciasAdicionadas.get(periciaId);
                dados.graduacao = graduacao;
                dados.bonus = bonusOutros;
                dados.total = (graduacao || 0) + (dados.modificador_atributo || 0) + (bonusOutros || 0);
            }

            console.log('✅ Perícia atualizada:', response);
        } catch (error) {
            console.error('❌ Erro ao atualizar perícia:', error);
            NotificationService.mostrarErro('❌ Erro: ' + error.message);
            // Re-renderizar para desfazer as mudanças
            this.renderizar();
        }
    }

    async adicionarPericia(periciaId, btnElement) {
        if (!this._iniciarOperacao('adicionar', periciaId)) {
            return;
        }

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

            NotificationService.mostrarSucesso('✅ Perícia adicionada com sucesso!');

        } catch (error) {
            console.error('❌ Erro ao adicionar perícia:', error);
            NotificationService.mostrarErro('❌ ' + error.message);
            if (btnElement && btnElement.isConnected) {
                btnElement.disabled = false;
                btnElement.textContent = '➕';
            }
        } finally {
            this._finalizarOperacao('adicionar', periciaId);
        }
    }

    removerPericia(periciaId, btnElement) {
        const dados = this.periciasAdicionadas.get(periciaId);
        if (!dados) return;

        ModalConfirm.mostrar({
            icone: '🗑️',
            titulo: 'Remover Perícia',
            texto: 'Tem certeza que deseja remover essa perícia?',
            textoCancelar: 'Cancelar',
            textoConfirmar: '🗑️ Remover',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: () => this._executarRemocao(periciaId, btnElement),
        });
    }

    async _executarRemocao(periciaId, btnElement) {
        if (!this._iniciarOperacao('remover', periciaId)) {
            return;
        }

        try {
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

            NotificationService.mostrarSucesso('✅ Perícia removida com sucesso!');

        } catch (error) {
            console.error('❌ Erro ao remover perícia:', error);
            NotificationService.mostrarErro('❌ ' + error.message);
            btnElement.disabled = false;
            btnElement.textContent = '🗑️';
        } finally {
            this._finalizarOperacao('remover', periciaId);
        }
    }
}
