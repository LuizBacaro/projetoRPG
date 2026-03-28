/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 * ✅ NOVO: BroadcastChannel sync arena→ficha em tempo real
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { EquipamentoService } from '../services/EquipamentoService.js';
import { TalentoService } from '../services/TalentoService.js';
import { PericiaService } from '../services/PericiaService.js';
import { getApiUrl } from '../config/api.config.js';

export class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.equipamentoService = new EquipamentoService();
        this.talentoService = new TalentoService();
        this.periciaService = new PericiaService();
        this.token             = localStorage.getItem('token');
        this.combatente        = null;

        // ✅ NOVO: canal de escuta arena → ficha
        this._canal = null;
        this._configurarCanalSync();

        console.log('✅ FichaPersonagemController inicializado');
    }

    async inicializar() {
        try {
            const params       = new URLSearchParams(window.location.search);
            const combatenteId = params.get('id');

            if (!combatenteId) throw new Error('ID do combatente não fornecido');

            console.log('🎯 Carregando ficha do combatente:', combatenteId);

            this.combatente = await this.combatenteService.obterCombatente(parseInt(combatenteId));

            // ✅ Expor globalmente para debug no console
            window._fichaController = this;

            console.log('✅ Combatente carregado:', this.combatente.nome);
            console.log('📦 magias_slots recebidos:', this.combatente.magias_slots);
            console.log('⚔️ ataques recebidos:', this.combatente.ataques);

            // ── Renderizar tudo ──
            this.renderizarIdentidade();
            this.renderizarAtributos();
            this.renderizarDefesa();
            this.renderizarResistencias();
            this.renderizarAtaques();
            this.renderizarSlotsDeMapia();
            await this.carregarRenderizarPericias(parseInt(combatenteId));
            await this.carregarRenderizarEquipamentos(parseInt(combatenteId));
            await this.carregarRenderizarTalentos(parseInt(combatenteId));

            // ── Configurar eventos ──
            this._configurarEventos();

            console.log('✅ Ficha carregada com sucesso');

        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
        }
    }

    _configurarEventos() {
        const btnAdicionarEq = document.getElementById('btnAdicionarEquipamento');
        if (btnAdicionarEq) {
            btnAdicionarEq.addEventListener('click', () => this.abrirModalEquipamentos());
        }

        const btnAdicionarTal = document.getElementById('btnAdicionarTalento');
        if (btnAdicionarTal) {
            btnAdicionarTal.addEventListener('click', () => this.abrirModalTalentos());
        }
    }

    // ─────────────────────────────────────────────────────────
    // ✅ NOVO: SINCRONIZAÇÃO COM ARENA
    // ─────────────────────────────────────────────────────────

    /**
     * ✅ NOVO: Configura escuta do BroadcastChannel
     * SRP: apenas setup do canal — processamento delegado a _processarEventoMagia()
     */
    _configurarCanalSync() {
        try {
            this._canal = new BroadcastChannel('magias-rpg');
            this._canal.onmessage = (event) => {
                if (event.data?.tipo === 'magia-usada') {
                    this._processarEventoMagia(event.data);
                }
            };
            console.log('✅ FichaController: canal sync arena→ficha ativo');
        } catch (err) {
            console.warn('⚠️ BroadcastChannel indisponível:', err.message);
        }
    }

    /**
     * ✅ NOVO: Processa evento de magia lançada na arena
     * Atualiza o painel de slots (fichaMagiasGrid) em tempo real
     * SRP: apenas roteamento — atualização de UI delegada a métodos específicos
     * @param {{ combatenteId, magiaId, nivel, usada, disponiveis, total }} payload
     */
    _processarEventoMagia(payload) {
        // Ignora eventos de outros combatentes
        if (!this.combatente || this.combatente.id !== payload.combatenteId) {
            return;
        }

        console.log('📡 Sync magia recebida na ficha:', payload);

        // 1. Atualiza painel de slots na ficha
        this._atualizarPainelSlotsFicha(payload.nivel, payload.disponiveis, payload.total);

        // 2. Pulsa o slot para dar feedback visual
        this._pulsarSlot(payload.nivel);

        // 3. Atualiza painel de slots no grimório (se estiver aberto)
        if (window._grimorioController) {
            this._atualizarPainelSlotsGrimorio(payload.nivel, payload.disponiveis, payload.total);
        }
    }

    /**
     * ✅ NOVO: Atualiza o painel de slots na ficha (fichaMagiasGrid)
     * SRP: apenas DOM da ficha — sem lógica de negócio
     * @param {number} nivel
     * @param {number} disponiveis
     * @param {number} total
     */
    _atualizarPainelSlotsFicha(nivel, disponiveis, total) {
        const grid = document.getElementById('fichaMagiasGrid');
        if (!grid) return;

        // Encontra a linha do slot por nível
        const linhas = grid.querySelectorAll('.ficha-slot-linha');
        let slotLinha = null;

        for (const linha of linhas) {
            const nivelSpan = linha.querySelector('.ficha-slot-nivel');
            if (!nivelSpan) continue;

            const labelNivel = nivel === 0 ? 'Truques' : `${nivel}° Nível`;
            if (nivelSpan.textContent.trim() === labelNivel) {
                slotLinha = linha;
                break;
            }
        }

        if (!slotLinha) return; // Slot não existe na ficha

        // Atualiza contagem
        const contagemEl = slotLinha.querySelector('.ficha-slot-contagem');
        if (contagemEl) {
            contagemEl.textContent = `${disponiveis}/${total}`;
        }

        // Atualiza barra de progresso
        const fill = slotLinha.querySelector('.ficha-slot-barra-fill');
        if (fill) {
            const pct = total > 0 ? (disponiveis / total) * 100 : 0;
            fill.style.width = `${pct}%`;

            // Cor baseada na disponibilidade
            let cor = '#4ade80'; // Verde
            if (pct <= 50) cor = '#facc15'; // Amarelo
            if (pct <= 25) cor = '#f87171'; // Vermelho
            fill.style.background = cor;
        }

        console.log(`📊 Slot nível ${nivel} atualizado: ${disponiveis}/${total}`);
    }

    /**
     * ✅ NOVO: Atualiza painel de slots no grimório (se aberto)
     * SRP: apenas integração com GrimorioController
     * @param {number} nivel
     * @param {number} disponiveis
     * @param {number} total
     */
    _atualizarPainelSlotsGrimorio(nivel, disponiveis, total) {
        try {
            const gc = window._grimorioController;
            if (!gc || !gc.slotsDisponiveis) return;

            if (gc.slotsDisponiveis[nivel]) {
                gc.slotsDisponiveis[nivel].preparadas = total;
                gc.slotsDisponiveis[nivel].disponivel = disponiveis;
                gc._renderizarPainelSlots();
                console.log(`📖 Grimório: slot nível ${nivel} sincronizado`);
            }
        } catch (err) {
            console.warn('⚠️ Erro ao sincronizar grimório:', err.message);
        }
    }

    /**
     * ✅ NOVO: Pulsa visualmente o slot que foi alterado
     * SRP: apenas feedback visual — sem lógica de estado
     * @param {number} nivel
     */
    _pulsarSlot(nivel) {
        const grid = document.getElementById('fichaMagiasGrid');
        if (!grid) return;

        const linhas = grid.querySelectorAll('.ficha-slot-linha');
        for (const linha of linhas) {
            const nivelSpan = linha.querySelector('.ficha-slot-nivel');
            if (!nivelSpan) continue;

            const labelNivel = nivel === 0 ? 'Truques' : `${nivel}° Nível`;
            if (nivelSpan.textContent.trim() === labelNivel) {
                // Força reflow para reiniciar animação
                linha.classList.remove('ficha-slot-pulse');
                void linha.offsetWidth;
                linha.classList.add('ficha-slot-pulse');

                // Remove classe após animação
                setTimeout(() => {
                    linha.classList.remove('ficha-slot-pulse');
                }, 600);
                break;
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // IDENTIDADE
    // ─────────────────────────────────────────────────────────

    renderizarIdentidade() {
        const nome        = document.getElementById('fichaNome');
        const raca        = document.getElementById('fichaRaca');
        const classe      = document.getElementById('fichaClasse');
        const tipo        = document.getElementById('fichaTipo');
        const nivel       = document.getElementById('fichaNivel');
        const placeholder = document.getElementById('fichaFotoPlaceholder');
        const foto        = document.getElementById('fichaFoto');

        if (nome)   nome.textContent   = this.combatente.nome;
        if (raca)   raca.textContent   = this.combatente.raca   || '—';
        if (classe) classe.textContent = this.combatente.classe || '—';
        if (tipo)   tipo.textContent   = this.combatente.tipo   || 'jogador';
        if (nivel)  nivel.textContent  = this.combatente.nivel  || 1;

        if (this.combatente.foto_url) {
            if (foto) {
                foto.src = this.combatente.foto_url;
                foto.classList.add('carregada');
            }
            if (placeholder) placeholder.style.display = 'none';
        } else {
            const emojiMap = { jogador: '🧙', npc: '🤝', monstro: '👹' };
            if (placeholder) placeholder.textContent = emojiMap[this.combatente.tipo] || '⚔️';
        }

        console.log('✅ Identidade renderizada');
    }

    // ─────────────────────────────────────────────────────────
    // ATRIBUTOS
    // ─────────────────────────────────────────────────────────

    renderizarAtributos() {
        const map = {
            forca:         'For',
            destreza:      'Des',
            constituicao:  'Con',
            inteligencia:  'Int',
            sabedoria:     'Sab',
            carisma:       'Car',
        };

        Object.entries(map).forEach(([attr, abrev]) => {
            const valor   = this.combatente[attr] || 10;
            const mod     = Math.floor((valor - 10) / 2);
            
            // Renderizar na coluna central
            const elValor = document.getElementById(`ficha${abrev}`);
            const elMod   = document.getElementById(`ficha${abrev}Mod`);
            if (elValor) elValor.textContent = valor;
            if (elMod)   elMod.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
            
            // Renderizar na coluna esquerda (resumo)
            const elValorResumo = document.getElementById(`ficha${abrev}Resumo`);
            const elModResumo   = document.getElementById(`ficha${abrev}ModResumo`);
            if (elValorResumo) elValorResumo.textContent = valor;
            if (elModResumo)   elModResumo.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
        });

        console.log('✅ Atributos renderizados');
    }

    // ─────────────────────────────────────────────────────────
    // DEFESA
    // ─────────────────────────────────────────────────────────

    renderizarDefesa() {
        const ca         = document.getElementById('fichaCa');
        const toque      = document.getElementById('fichaToque');
        const surpresa   = document.getElementById('fichaSurpresa');
        const pv         = document.getElementById('fichaPv');
        const pvFill     = document.getElementById('fichaPvFill');
        const iniciativa = document.getElementById('fichaIniciativa');

        if (ca)       ca.textContent      = this.combatente.ca       ?? 10;
        if (toque)    toque.textContent    = this.combatente.toque    ?? 10;
        if (surpresa) surpresa.textContent = this.combatente.surpresa ?? 10;

        if (pv) pv.textContent = `${this.combatente.hp_atual ?? 0}/${this.combatente.hp_maximo ?? 0}`;

        if (pvFill) {
            const pct = (this.combatente.hp_maximo || 0) > 0
                ? ((this.combatente.hp_atual || 0) / this.combatente.hp_maximo) * 100
                : 0;
            pvFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
        }

        if (iniciativa) {
            const ini = this.combatente.iniciativa || 0;
            iniciativa.textContent = ini >= 0 ? `+${ini}` : `${ini}`;
        }

        console.log('✅ Defesa renderizada');
    }

    // ─────────────────────────────────────────────────────────
    // RESISTÊNCIAS
    // ─────────────────────────────────────────────────────────

    renderizarResistencias() {
        const fort   = document.getElementById('fichaFort');
        const reflex = document.getElementById('fichaReflex');
        const vont   = document.getElementById('fichaVont');

        const fmt = v => v >= 0 ? `+${v}` : `${v}`;
        if (fort)   fort.textContent   = fmt(this.combatente.fortitude || 0);
        if (reflex) reflex.textContent = fmt(this.combatente.reflexos  || 0);
        if (vont)   vont.textContent   = fmt(this.combatente.vontade   || 0);

        console.log('✅ Resistências renderizadas');
    }

    // ─────────────────────────────────────────────────────────
    // ATAQUES
    // ─────────────────────────────────────────────────────────

    renderizarAtaques() {
        const lista = document.getElementById('fichaAtaquesLista');
        if (!lista) return;

        const ataques = this.combatente.ataques || [];

        if (ataques.length === 0) {
            lista.innerHTML = '<div class="ficha-ataque-vazio">Nenhum ataque cadastrado</div>';
            return;
        }

        lista.innerHTML = ataques.map(a => `
            <div class="ficha-ataque-linha">
                <span class="ficha-ataque-nome">${a.nome || '—'}</span>
                <span class="ficha-ataque-bonus">${a.bonus_ataque || '+0'}</span>
                <span class="ficha-ataque-dano">${a.dano || '—'}</span>
            </div>
        `).join('');

        console.log('✅ Ataques renderizados:', ataques.length);
    }

    // ─────────────────────────────────────────────────────────
    // SLOTS DE MAGIA
    // ─────────────────────────────────────────────────────────

    renderizarSlotsDeMapia() {
        const grid      = document.getElementById('fichaMagiasGrid');
        const secao     = document.getElementById('secaoMagias');
        if (!grid) {
            console.warn('⚠️ #fichaMagiasGrid não encontrado no DOM');
            return;
        }

        const slots      = this.combatente.magias_slots || [];
        const slotsAtivos = slots.filter(s => (s.total || 0) > 0);

        console.log('🔮 Todos os slots:', slots);
        console.log('🔮 Slots ativos (total > 0):', slotsAtivos);

        if (secao && this.combatente.tipo === 'jogador') {
            secao.style.display = 'flex';
        }

        if (slotsAtivos.length === 0) {
            grid.innerHTML = '<div class="ficha-magia-vazio">Nenhum slot cadastrado</div>';
            console.log('ℹ️ Nenhum slot de magia ativo');
            return;
        }

        slotsAtivos.sort((a, b) => a.nivel - b.nivel);

        grid.innerHTML = slotsAtivos.map(slot => {
            const usados      = slot.usados || 0;
            const total       = slot.total  || 0;
            const disponiveis = total - usados;
            const pct         = total > 0 ? (disponiveis / total) * 100 : 0;
            const labelNivel  = slot.nivel === 0 ? 'Truques' : `${slot.nivel}° Nível`;

            const corBarra = pct > 50 ? '#4ade80' : pct > 25 ? '#facc15' : '#f87171';

            return `
                <div class="ficha-slot-linha">
                    <div class="ficha-slot-topo">
                        <span class="ficha-slot-nivel">${labelNivel}</span>
                        <span class="ficha-slot-contagem">${disponiveis}/${total}</span>
                    </div>
                    <div class="ficha-slot-barra-wrap">
                        <div class="ficha-slot-barra-fill"
                            style="width:${pct}%; background:${corBarra}">
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        console.log('✅ Slots de magia renderizados:', slotsAtivos.length);
    }

    // ─────────────────────────────────────────────────────────
    // PERÍCIAS
    // ─────────────────────────────────────────────────────────

    async carregarRenderizarPericias(combatenteId) {
        try {
            const url = getApiUrl(`/pericias/${combatenteId}/listar`);
            const res = await fetch(url, {
                headers: {
                    'Content-Type':  'application/json',
                    'Authorization': `Bearer ${this.token}`,
                }
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data    = await res.json();
            const pericias = data.pericias || [];
            console.log('✅ Perícias carregadas:', pericias.length);
            this.renderizarPericiasNaFicha(pericias);

        } catch (error) {
            console.warn('⚠️ Erro ao carregar perícias:', error);
            this.renderizarPericiasVazias();
        }
    }

    renderizarPericiasNaFicha(pericias) {
        const container = document.getElementById('fichaPericiasLista');
        if (!container) return;

        if (pericias.length === 0) {
            container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
            return;
        }

        container.innerHTML = '';
        pericias.forEach(pj => {
            const total = pj.graduacao + pj.modificador_atributo + (pj.bonus_outros || 0);
            const item  = document.createElement('div');
            item.className = 'ficha-pericia-item';
            item.title     = pj.pericia?.descricao || '';
            item.innerHTML = `
                <span class="ficha-pericia-nome">${pj.pericia?.nome || '—'}</span>
                <span class="ficha-pericia-atributo">${pj.pericia?.atributo || '—'}</span>
                <div class="ficha-pericia-mods">
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Gra</span>
                        <span class="ficha-pericia-mod-valor">${pj.graduacao}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Atr</span>
                        <span class="ficha-pericia-mod-valor">${pj.modificador_atributo >= 0 ? '+' : ''}${pj.modificador_atributo}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Bôn</span>
                        <span class="ficha-pericia-mod-valor">${pj.bonus_outros >= 0 ? '+' : ''}${pj.bonus_outros || 0}</span>
                    </div>
                    <div class="ficha-pericia-mod">
                        <span class="ficha-pericia-mod-label">Total</span>
                        <span class="ficha-pericia-total-valor ${total >= 0 ? 'positivo' : 'negativo'}">
                            ${total >= 0 ? '+' : ''}${total}
                        </span>
                    </div>
                </div>
            `;
            container.appendChild(item);
        });

        console.log('✅ Perícias renderizadas:', pericias.length);
    }

    renderizarPericiasVazias() {
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = '<span class="ficha-vazio">Nenhuma perícia selecionada</span>';
    }

    // ─────────────────────────────────────────────────────────
    // ERRO
    // ─────────────────────────────────────────────────────────

    mostrarErro(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaPericiasLista');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async carregarRenderizarEquipamentos(combatenteId) {
        try {
            const equipamentos = await this.equipamentoService.listarEquipamentosJogador(combatenteId);
            console.log('✅ Equipamentos carregados:', equipamentos.length);
            
            this.renderizarEquipamentos(equipamentos);
        } catch (error) {
            console.error('❌ Erro ao carregar equipamentos:', error);
            this.mostrarErroEquipamentos('Erro ao carregar equipamentos');
        }
    }

    renderizarEquipamentos(equipamentos) {
        const lista = document.getElementById('fichaEquipamentos');
        if (!lista) return;

        if (!equipamentos || equipamentos.length === 0) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum equipamento cadastrado</span>';
            return;
        }

        lista.innerHTML = `
            <div class="ficha-equipamentos-tabela">
                <div class="ficha-equipamento-header">
                    <span>Item</span>
                    <span>Descrição</span>
                    <span>Pág. Ref</span>
                    <span>Qtd</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-equipamentos-lista-items">
                    ${equipamentos.map(eq => `
                        <div class="ficha-equipamento-linha">
                            <span class="ficha-equipamento-nome">${eq.nome}</span>
                            <span class="ficha-equipamento-desc">${eq.descricao || '—'}</span>
                            <span class="ficha-equipamento-pag">${eq.pagina_referencia || '—'}</span>
                            <span class="ficha-equipamento-qtd">${eq.quantidade}</span>
                            <button class="btn-deletar-eq" data-eq-id="${eq.id}" data-eq-nome="${eq.nome}" title="Deletar ${eq.nome}">🗑️</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Configurar eventos dos botões de deletar
        const self = this;
        lista.querySelectorAll('.btn-deletar-eq').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const eqId = e.target.dataset.eqId;
                const eqNome = e.target.dataset.eqNome;
                self.deletarEquipamento(eqId, eqNome);
            });
        });

        console.log('✅ Equipamentos renderizados:', equipamentos.length);
    }

    mostrarErroEquipamentos(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaEquipamentos');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async abrirModalEquipamentos() {
        try {
            const modal = document.getElementById('modalEquipamentos');
            if (!modal) return;

            // Carregar lista de equipamentos disponíveis
            const equipamentos = await this.equipamentoService.listarEquipamentos(0, 100);
            console.log('📦 Equipamentos disponíveis:', equipamentos.length);

            // Armazenar para uso no filtro
            this.equipamentosDisponiveis = equipamentos;
            
            // Renderizar lista inicial
            this.renderizarListaEquipamentos(equipamentos);

            // Mostrar modal
            modal.style.display = 'flex';

            // Expor para onclick
            window._fichaController = this;

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao carregar equipamentos');
            }
        }
    }

    fecharModalEquipamentos() {
        const modal = document.getElementById('modalEquipamentos');
        if (modal) modal.style.display = 'none';
    }

    renderizarListaEquipamentos(equipamentos) {
        const lista = document.getElementById('equipamentosLista');
        if (!lista) return;

        if (!equipamentos || equipamentos.length === 0) {
            lista.innerHTML = '<p class="equipamentos-vazio">Nenhum equipamento encontrado</p>';
            return;
        }

        lista.innerHTML = equipamentos.map(eq => `
            <div class="equipamento-item">
                <div class="equipamento-info">
                    <div class="equipamento-nome">${eq.nome}</div>
                    <div class="equipamento-desc">${eq.descricao || '—'}</div>
                    <div class="equipamento-pag">${eq.pagina_referencia || '—'}</div>
                </div>
                <button class="equipamento-btn-adicionar" 
                        onclick="window._fichaController.adicionarEquipamentoClic(${eq.id})">
                    ➕
                </button>
            </div>
        `).join('');
    }

    filtrarEquipamentos() {
        const termo = document.getElementById('equipamentosBusca')?.value || '';
        const filtrados = this.equipamentoService.filtrarPorBusca(
            this.equipamentosDisponiveis,
            termo
        );
        this.renderizarListaEquipamentos(filtrados);
    }

    async adicionarEquipamentoClic(equipamentoId) {
        try {
            const qntdInput = document.getElementById('equipamentosQuantidade');
            const quantidade = parseInt(qntdInput?.value || '1');

            if (!this.combatente?.id) {
                if (window.NotificationService) {
                    window.NotificationService.erro('❌ ID do combatente não encontrado');
                }
                return;
            }

            // Pegar o nome do equipamento do modal
            const eqNomeElement = document.querySelector('#conteudoListar .ficha-equipamento-linha:last-child .ficha-equipamento-nome');
            const nomeEquipamento = eqNomeElement?.textContent || 'Equipamento';

            await this.equipamentoService.adicionarEquipamento(this.combatente.id, {
                equipamento_id: equipamentoId,
                quantidade: quantidade
            });

            console.log('✅ Equipamento adicionado');

            // Recarregar equipamentos
            await this.carregarRenderizarEquipamentos(this.combatente.id);

            // Resetar quantidade
            qntdInput.value = '1';

            // Mostrar notificação de sucesso
            if (window.NotificationService) {
                window.NotificationService.sucesso(`✅ Equipamento adicionado ao inventário!`);
            }

        } catch (error) {
            console.error('❌ Erro ao adicionar equipamento:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao adicionar equipamento');
            }
        }
    }

    async deletarEquipamento(equipamentoId, nomeEquipamento) {
        if (!this.combatente?.id) {
            if (window.NotificationService) {
                window.NotificationService.erro('❌ ID do combatente não encontrado');
            }
            return;
        }

        const self = this;
        console.log('🗑️ deletarEquipamento chamado com ID:', equipamentoId, 'Nome:', nomeEquipamento);

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Equipamento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeEquipamento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    console.log('🗑️ Deletando equipamento:', equipamentoId, 'do combatente:', self.combatente.id);
                    await self.equipamentoService.removerEquipamento(self.combatente.id, equipamentoId);

                    console.log('✅ Equipamento removido');

                    // Recarregar equipamentos
                    await self.carregarRenderizarEquipamentos(self.combatente.id);

                    // Mostrar notificação
                    if (window.NotificationService) {
                        window.NotificationService.sucesso(`✅ ${nomeEquipamento} removido!`);
                    }

                } catch (error) {
                    console.error('❌ Erro ao deletar equipamento:', error);
                    if (window.NotificationService) {
                        window.NotificationService.erro('❌ Erro ao remover equipamento');
                    }
                }
            }
        };
        
        window.ModalConfirm.mostrar(opcoes);
    }

    abrirAbaListar() {
        document.getElementById('abaListar').classList.add('ativa');
        document.getElementById('abaCriar').classList.remove('ativa');
        document.getElementById('conteudoListar').classList.add('ativo');
        document.getElementById('conteudoCriar').classList.remove('ativo');
    }

    abrirAbaCriar() {
        document.getElementById('abaCriar').classList.add('ativa');
        document.getElementById('abaListar').classList.remove('ativa');
        document.getElementById('conteudoCriar').classList.add('ativo');
        document.getElementById('conteudoListar').classList.remove('ativo');
    }

    async salvarEquipamentoCustomizado() {
        try {
            const nome = document.getElementById('criarNome')?.value || '';
            const descricao = document.getElementById('criarDescricao')?.value || '';
            const paginaRef = document.getElementById('criarPaginaRef')?.value || '';
            const quantidade = parseInt(document.getElementById('criarQuantidade')?.value || '1');

            if (!nome.trim()) {
                if (window.NotificationService) {
                    window.NotificationService.aviso('⚠️ Nome do equipamento é obrigatório');
                }
                return;
            }

            // Criar equipamento via API
            const novoEquipamento = await this.equipamentoService.criarEquipamento({
                nome: nome.trim(),
                descricao: descricao.trim(),
                pagina_referencia: paginaRef.trim(),
                ativo: true
            });

            console.log('✅ Equipamento criado:', novoEquipamento);

            // Adicionar ao combatente
            await this.equipamentoService.adicionarEquipamento(this.combatente.id, {
                equipamento_id: novoEquipamento.id,
                quantidade: quantidade
            });

            // Recarregar equipamentos
            await this.carregarRenderizarEquipamentos(this.combatente.id);

            // Limpar formulário
            document.getElementById('formCriarEquipamento').reset();

            // Voltar para aba de listar
            this.abrirAbaListar();

            // Notificação
            if (window.NotificationService) {
                window.NotificationService.sucesso(`✅ Equipamento "${nome}" criado e adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao criar equipamento:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao criar equipamento: ' + error.message);
            }
        }
    }

    // ── TALENTOS ──

    async carregarRenderizarTalentos(combatenteId) {
        try {
            const talentos = await this.talentoService.listarTalentosJogador(combatenteId);
            console.log('✅ Talentos carregados:', talentos.length);
            
            this.renderizarTalentos(talentos);
        } catch (error) {
            console.error('❌ Erro ao carregar talentos:', error);
            this.mostrarErroTalentos('Erro ao carregar talentos');
        }
    }

    renderizarTalentos(talentos) {
        const lista = document.getElementById('fichaTalentos');
        if (!lista) return;

        if (!talentos || talentos.length === 0) {
            lista.innerHTML = '<span class="ficha-vazio">Nenhum talento cadastrado</span>';
            return;
        }

        lista.innerHTML = `
            <div class="ficha-talentos-tabela">
                <div class="ficha-talento-header">
                    <span>Talento</span>
                    <span>Descrição</span>
                    <span>Pág. Ref</span>
                    <span>Ação</span>
                </div>
                <div class="ficha-talentos-lista-items">
                    ${talentos.map(tal => `
                        <div class="ficha-talento-linha">
                            <span class="ficha-talento-nome">${tal.nome}</span>
                            <span class="ficha-talento-desc">${tal.descricao || '—'}</span>
                            <span class="ficha-talento-pag">${tal.pagina_referencia || '—'}</span>
                            <button class="btn-deletar-tal" data-tal-id="${tal.id}" data-tal-nome="${tal.nome}" title="Deletar ${tal.nome}">🗑️</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        // Configurar eventos dos botões de deletar
        const self = this;
        lista.querySelectorAll('.btn-deletar-tal').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const talId = e.target.dataset.talId;
                const talNome = e.target.dataset.talNome;
                self.deletarTalento(talId, talNome);
            });
        });

        console.log('✅ Talentos renderizados:', talentos.length);
    }

    mostrarErroTalentos(mensagem) {
        console.error('❌', mensagem);
        const container = document.getElementById('fichaTalentos');
        if (container) container.innerHTML = `<span class="ficha-vazio">❌ ${mensagem}</span>`;
    }

    async abrirModalTalentos() {
        try {
            const modal = document.getElementById('modalTalentos');
            if (!modal) {
                if (window.NotificationService) {
                    window.NotificationService.erro('❌ Modal de talentos não encontrado');
                }
                return;
            }

            // Carregar lista de talentos disponíveis
            const talentos = await this.talentoService.listarTalentos(0, 100);
            console.log('📦 Talentos disponíveis:', talentos.length);

            // Armazenar para uso no filtro
            this.talentosDisponiveis = talentos;
            
            // Renderizar lista inicial
            this.renderizarListaTalentos(talentos);

            // Mostrar modal
            modal.style.display = 'flex';

            // Expor para onclick
            window._fichaController = this;

        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao carregar talentos: ' + error.message);
            }
        }
    }

    renderizarListaTalentos(talentos) {
        const container = document.getElementById('conteudoListarTalentos');
        if (!container) return;

        if (!talentos || talentos.length === 0) {
            container.innerHTML = '<p class="equipamentos-vazio">Nenhum talento disponível</p>';
            return;
        }

        container.innerHTML = `
            <div class="equipamentos-lista-grid">
                ${talentos.map(tal => `
                    <div class="equipamentos-card">
                        <h4>${tal.nome}</h4>
                        <p class="equipamentos-desc">${tal.descricao || '—'}</p>
                        <p class="equipamentos-pag">📄 ${tal.pagina_referencia || '—'}</p>
                        <button class="equipamentos-btn-adicionar" 
                                onclick="window._fichaController && window._fichaController.adicionarTalentoClic(${tal.id})">
                            ➕ Adicionar
                        </button>
                    </div>
                `).join('')}
            </div>
        `;

        console.log('✅ Lista de talentos renderizada:', talentos.length);
    }

    filtrarTalentos() {
        const filtro = document.getElementById('equipamentosFiltro')?.value?.toLowerCase() || '';
        if (!this.talentosDisponiveis) return;

        const filtrados = this.talentosDisponiveis.filter(tal => 
            tal.nome.toLowerCase().includes(filtro) || 
            (tal.descricao && tal.descricao.toLowerCase().includes(filtro))
        );

        this.renderizarListaTalentos(filtrados);
    }

    async adicionarTalentoClic(talentoId) {
        try {
            if (!this.combatente?.id) {
                if (window.NotificationService) {
                    window.NotificationService.erro('❌ ID do combatente não encontrado');
                }
                return;
            }

            await this.talentoService.adicionarTalento(this.combatente.id, {
                talento_id: talentoId
            });

            console.log('✅ Talento adicionado');

            // Recarregar talentos
            await this.carregarRenderizarTalentos(this.combatente.id);

            // Mostrar notificação de sucesso
            if (window.NotificationService) {
                window.NotificationService.sucesso(`✅ Talento adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao adicionar talento:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao adicionar talento');
            }
        }
    }

    async deletarTalento(talentoId, nomeTalento) {
        if (!this.combatente?.id) {
            if (window.NotificationService) {
                window.NotificationService.erro('❌ ID do combatente não encontrado');
            }
            return;
        }

        const self = this;
        console.log('🗑️ deletarTalento chamado com ID:', talentoId, 'Nome:', nomeTalento);

        // Usar ModalConfirm em vez de confirm()
        const opcoes = {
            icone: '🗑️',
            titulo: 'Deletar Talento',
            texto: `Tem certeza que deseja deletar <strong>"${nomeTalento}"</strong>?`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    console.log('🗑️ Deletando talento:', talentoId, 'do combatente:', self.combatente.id);
                    await self.talentoService.removerTalento(self.combatente.id, talentoId);

                    console.log('✅ Talento removido');

                    // Recarregar talentos
                    await self.carregarRenderizarTalentos(self.combatente.id);

                    // Mostrar notificação
                    if (window.NotificationService) {
                        window.NotificationService.sucesso(`✅ ${nomeTalento} removido!`);
                    }

                } catch (error) {
                    console.error('❌ Erro ao deletar talento:', error);
                    if (window.NotificationService) {
                        window.NotificationService.erro('❌ Erro ao remover talento');
                    }
                }
            }
        };

        window.ModalConfirm.mostrar(opcoes);
    }

    fecharModalTalentos() {
        const modal = document.getElementById('modalTalentos');
        if (modal) modal.style.display = 'none';
    }

    abrirAbaListarTalentos() {
        const abaLista = document.getElementById('abaListarTalentos');
        const abaCriar = document.getElementById('abaCriarTalento');
        if (abaLista) abaLista.classList.add('ativa');
        if (abaCriar) abaCriar.classList.remove('ativa');
        
        const conteudoLista = document.getElementById('conteudoListarTalentos');
        const conteudoCriar = document.getElementById('conteudoCriarTalento');
        if (conteudoLista) conteudoLista.classList.add('ativo');
        if (conteudoCriar) conteudoCriar.classList.remove('ativo');
    }

    abrirAbaCriarTalento() {
        const abaLista = document.getElementById('abaListarTalentos');
        const abaCriar = document.getElementById('abaCriarTalento');
        if (abaCriar) abaCriar.classList.add('ativa');
        if (abaLista) abaLista.classList.remove('ativa');
        
        const conteudoLista = document.getElementById('conteudoListarTalentos');
        const conteudoCriar = document.getElementById('conteudoCriarTalento');
        if (conteudoCriar) conteudoCriar.classList.add('ativo');
        if (conteudoLista) conteudoLista.classList.remove('ativo');
    }

    async salvarTalentoCustomizado() {
        try {
            const nome = document.getElementById('criarNomeTalento')?.value || '';
            const descricao = document.getElementById('criarDescricaoTalento')?.value || '';
            const paginaRef = document.getElementById('criarPaginaRefTalento')?.value || '';

            if (!nome.trim()) {
                if (window.NotificationService) {
                    window.NotificationService.aviso('⚠️ Nome do talento é obrigatório');
                }
                return;
            }

            // Criar talento via API
            const novoTalento = await this.talentoService.criarTalento({
                nome: nome.trim(),
                descricao: descricao.trim(),
                pagina_referencia: paginaRef.trim(),
                ativo: true
            });

            console.log('✅ Talento criado:', novoTalento);

            // Adicionar ao combatente
            await this.talentoService.adicionarTalento(this.combatente.id, {
                talento_id: novoTalento.id
            });

            // Recarregar talentos
            await this.carregarRenderizarTalentos(this.combatente.id);

            // Limpar formulário
            document.getElementById('formCriarTalento').reset();

            // Voltar para aba de listar
            this.abrirAbaListarTalentos();

            // Notificação
            if (window.NotificationService) {
                window.NotificationService.sucesso(`✅ Talento "${nome}" criado e adicionado!`);
            }

        } catch (error) {
            console.error('❌ Erro ao criar talento:', error);
            if (window.NotificationService) {
                window.NotificationService.erro('❌ Erro ao criar talento: ' + error.message);
            }
        }
    }

    // ─────────────────────────────────────────────────────────
    // PERÍCIAS
    // ─────────────────────────────────────────────────────────


    abrirPaginaPericias() {
        if (!this.combatente?.id) {
            window.NotificationService?.erro('❌ Selecione um combatente primeiro');
            return;
        }

        try {
            const params = new URLSearchParams({
                combatente_id: this.combatente.id
            });

            window.location.href = `/pages/pericias-ficha.html?${params.toString()}`;
        } catch (err) {
            window.NotificationService?.erro('❌ Erro ao abrir perícias');
            console.error(err);
        }
    }

    }

// ── Inicializar quando DOM estiver pronto ──
document.addEventListener('DOMContentLoaded', async () => {
    const controller = new FichaPersonagemController();
    window._fichaController = controller;
    await controller.inicializar();
});
