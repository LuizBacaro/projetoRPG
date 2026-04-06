/**
 * PericiaController.js - Versão Tabela Unificada
 * SRP: Orquestrar lógica de perícias com layout tabular compacto
 */

import { API_CONFIG, getApiUrl } from '../config/api.config.js';
import { NotificationService }   from '../services/NotificationService.js';
import { CombatenteService }     from '../services/CombatenteService.js';
import { PericiaService }        from '../services/PericiaService.js';
//import { ModalConfirm }          from '../ui/ModalConfirm.js';   // ✅ import centralizado

export class PericiaController {
    constructor() {
        this.apiConfig    = API_CONFIG;
        this.combatenteService = new CombatenteService();
        this.periciaService    = new PericiaService();
        this.baseUrl           = getApiUrl('/pericias');
        this.combatente        = null;
        this.pericias          = [];
        this.periciasFiltradasAtualmente = [];
        this.periciasSelecionadas        = new Map();
        this.token = localStorage.getItem('token');
    }

    async inicializar() {
        try {
            const params       = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id') || params.get('combatente_id');
            if (!combatenteId) throw new Error('ID do combatente não fornecido');

            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));
            this.atualizarHeaderCombatente();

            this.pericias                    = await this.periciaService.listarPericias();
            this.periciasFiltradasAtualmente = [...this.pericias];

            await this.carregarPericicasSelecionadas(parseInt(combatenteId));
            this.renderizar();
        } catch (error) {
            console.error('❌ Erro ao inicializar:', error);
            throw error;
        }
    }

    async carregarPericicasSelecionadas(combatenteId) {
        try {
            const url      = `${this.baseUrl}/${combatenteId}/listar`;
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type':  'application/json',
                    'Authorization': `Bearer ${this.token}`,
                }
            });
            if (response.ok) {
                const data = await response.json();
                this.periciasSelecionadas.clear();
                (data.pericias || []).forEach(pj => {
                    const dadosPericia = {
                        id:          pj.id,
                        pericia:     pj.pericia,
                        graduacao:   pj.graduacao       || 0,
                        bonus:       pj.bonus_outros    || 0,
                        modAtributo: pj.modificador_atributo || 0,
                    };
                    this.periciasSelecionadas.set(pj.pericia_id, dadosPericia);
                });
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
        this.periciasFiltradasAtualmente = !atributo
            ? [...this.pericias]
            : this.pericias.filter(p => p.atributo === atributo.toUpperCase());
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

    renderizar() { this.renderizarTabela(); }

    renderizarTabela() {
        const tbody = document.getElementById('tbody-pericias');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.periciasFiltradasAtualmente.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="vazio">❌ Nenhuma perícia encontrada</td></tr>';
            return;
        }

        this.periciasFiltradasAtualmente.forEach(pericia => {
            const tr         = document.createElement('tr');
            const selecionada = this.periciasSelecionadas.has(pericia.id);
            const dados       = selecionada ? this.periciasSelecionadas.get(pericia.id) : null;
            if (selecionada) tr.classList.add('selecionada');

            const total = dados ? (dados.graduacao + dados.modAtributo + dados.bonus) : 0;
            
            // ✅ SEMPRE calcular o modificador para referência (mesmo sem seleção)
            const modAtributoCalculado = this.calcularModAtributo(pericia);

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
                <td class="col-tipo"><span class="badge-tipo">${pericia.tipo}</span></td>
                <td class="col-modificadores">
                    <div class="modificadores-inline">
                        <input type="number" class="mod-input-inline input-graduacao"
                               data-pericia-id="${pericia.id}"
                               value="${dados ? dados.graduacao : 0}"
                               min="0" max="20" ${!selecionada ? 'disabled' : ''}>
                        <input type="number" class="mod-input-inline"
                               value="${dados ? dados.modAtributo : modAtributoCalculado}" readonly>
                        <input type="number" class="mod-input-inline input-bonus"
                               data-pericia-id="${pericia.id}"
                               value="${dados ? dados.bonus : 0}"
                               min="-20" max="20" ${!selecionada ? 'disabled' : ''}>
                        <input type="number" class="mod-input-inline input-total"
                               value="${total}" readonly>
                    </div>
                </td>
            `;

            tbody.appendChild(tr);

            tr.querySelector('.checkbox-pericia')
              .addEventListener('change', (e) => this.togglePericia(pericia, e.target.checked));

            if (selecionada) {
                const inputGraduacao = tr.querySelector('.input-graduacao');
                const inputBonus     = tr.querySelector('.input-bonus');
                inputGraduacao.addEventListener('change', () => {
                    dados.graduacao = parseInt(inputGraduacao.value) || 0;
                    this.atualizarTotal(tr, dados);
                });
                inputBonus.addEventListener('change', () => {
                    dados.bonus = parseFloat(inputBonus.value) || 0;
                    this.atualizarTotal(tr, dados);
                });
            }
        });

    }

    togglePericia(pericia, marcada) {
        if (marcada) {
            const modAtributo = this.calcularModAtributo(pericia);
            this.periciasSelecionadas.set(pericia.id, {
                pericia,
                graduacao:   0,
                bonus:       0,
                modAtributo: modAtributo,
            });
        } else {
            this.periciasSelecionadas.delete(pericia.id);
        }
        this.renderizar();
    }

    calcularModAtributo(pericia) {
        const atributoMap = {
            FOR: 'forca', DES: 'destreza', CON: 'constituicao',
            INT: 'inteligencia', SAB: 'sabedoria', CAR: 'carisma',
        };
        const atributoNome = atributoMap[pericia.atributo];
        const valorAtributo = this.combatente[atributoNome];
        
        if (!atributoNome || !valorAtributo) {
            console.warn(`⚠️ Atributo "${pericia.atributo}" não mapeado ou combatente sem "${atributoNome}"`);
            return 0;
        }
        
        const modificador = Math.floor((valorAtributo - 10) / 2);
        return modificador;
    }

    atualizarTotal(tr, dados) {
        tr.querySelector('.input-total').value =
            dados.graduacao + dados.modAtributo + dados.bonus;
    }

    // ✅ REFATORADO: usa ModalConfirm centralizado
    limparSelecao() {
        ModalConfirm.mostrar({
            icone:          '🧹',
            titulo:         'Limpar Seleção',
            texto:          'Deseja limpar todas as perícias selecionadas?',
            textoConfirmar: '🧹 Limpar',
            onConfirmar:    () => this._executarLimparSelecao(),
        });
    }

    _executarLimparSelecao() {
        this.periciasSelecionadas.clear();
        this.renderizar();
        NotificationService.mostrarSucesso('✅ Seleção limpa');
    }

    async salvarPericias() {
        const btnSalvar = document.getElementById('btn-salvar-pericias');
        const loadingOptions = {
            loadingText: '⏳ Salvando...',
            idleText: '💾 Salvar Perícias',
        };

        try {
            const executarSalvar = async () => {
                await this.removerPericiasNaoSelecionadas();
                await this.adicionarOuAtualizarPericias();
                await this.carregarPericicasSelecionadas(this.combatente.id);
                this.renderizar();
            };

            if (window.AsyncButtonState?.run) {
                await window.AsyncButtonState.run(btnSalvar, loadingOptions, executarSalvar);
            } else {
                if (btnSalvar) {
                    btnSalvar.disabled = true;
                    btnSalvar.textContent = loadingOptions.loadingText;
                }
                await executarSalvar();
                if (btnSalvar) {
                    btnSalvar.disabled = false;
                    btnSalvar.textContent = loadingOptions.idleText;
                }
            }

            NotificationService.mostrarSucesso('✅ Perícias salvas com sucesso!');
        } catch (error) {
            console.error('❌ Erro ao salvar:', error);
            if (!window.AsyncButtonState?.run && btnSalvar) {
                btnSalvar.disabled = false;
                btnSalvar.textContent = loadingOptions.idleText;
            }
            NotificationService.mostrarErro('Erro: ' + error.message);
        }
    }

    async removerPericiasNaoSelecionadas() {
        try {
            const url      = `${this.baseUrl}/${this.combatente.id}/listar`;
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` }
            });
            if (!response.ok) return;

            const data          = await response.json();
            const periciasAtuals = data.pericias || [];
            for (const pj of periciasAtuals) {
                if (!this.periciasSelecionadas.has(pj.pericia_id)) {
                    await this.removerPericiaAPI(pj.id);
                }
            }
        } catch (error) {
            console.error('⚠️ Erro ao remover perícias:', error);
        }
    }

    async removerPericiaAPI(periciaJogadorId) {
        const url      = `${this.baseUrl}/${this.combatente.id}/pericia/${periciaJogadorId}`;
        const response = await fetch(url, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.token}` }
        });
        if (!response.ok) throw new Error(`Erro ao remover perícia: ${response.status}`);
    }

    async adicionarOuAtualizarPericias() {
        const url      = `${this.baseUrl}/${this.combatente.id}/listar`;
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` }
        });
        const data          = response.ok ? await response.json() : { pericias: [] };
        const periciasAtuals = new Map(data.pericias.map(pj => [pj.pericia_id, pj]));

        for (const [periciaId, dadosLocal] of this.periciasSelecionadas) {
            const periciaAtual = periciasAtuals.get(periciaId);
            if (periciaAtual) {
                if (periciaAtual.graduacao !== dadosLocal.graduacao ||
                    periciaAtual.bonus_outros !== dadosLocal.bonus) {
                    await this.atualizarPericiaAPI(periciaAtual.id, dadosLocal);
                }
            } else {
                await this.adicionarPericiaAPI(periciaId, dadosLocal);
            }
        }
    }

    async adicionarPericiaAPI(periciaId, dados) {
        const url      = `${this.baseUrl}/${this.combatente.id}/adicionar`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
            body: JSON.stringify({ pericia_id: periciaId, graduacao: dados.graduacao, bonus_outros: dados.bonus })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao adicionar perícia');
        }
    }

    async atualizarPericiaAPI(periciaJogadorId, dados) {
        const url      = `${this.baseUrl}/${this.combatente.id}/pericia/${periciaJogadorId}`;
        const response = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` },
            body: JSON.stringify({ graduacao: dados.graduacao, bonus_outros: dados.bonus })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao atualizar perícia');
        }
    }
}