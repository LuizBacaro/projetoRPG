/**
 * FichaPersonagemController.js
 * SRP: Controlar renderização da ficha do personagem
 * SOLID: DIP via constructor injection de services
 * ✅ NOVO: BroadcastChannel sync arena→ficha em tempo real
 */

import { CombatenteService } from '../services/CombatenteService.js';
import { getApiUrl } from '../config/api.config.js';

export class FichaPersonagemController {

    constructor() {
        this.combatenteService = new CombatenteService();
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

            console.log('✅ Ficha carregada com sucesso');

        } catch (error) {
            console.error('❌ Erro ao inicializar ficha:', error);
            this.mostrarErro('Erro ao carregar ficha: ' + error.message);
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
            const elValor = document.getElementById(`ficha${abrev}`);
            const elMod   = document.getElementById(`ficha${abrev}Mod`);
            if (elValor) elValor.textContent = valor;
            if (elMod)   elMod.textContent   = mod >= 0 ? `+${mod}` : `${mod}`;
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
                    </div>
                </div>
                <span class="ficha-pericia-total ${total >= 0 ? 'positivo' : 'negativo'}">
                    ${total >= 0 ? '+' : ''}${total}
                </span>
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
    }}// ── Inicializar quando DOM estiver pronto ──
    document.addEventListener('DOMContentLoaded', async () => {
    const controller = new FichaPersonagemController();
    await controller.inicializar();
    }
);