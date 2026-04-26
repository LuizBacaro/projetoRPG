import { CombatenteService     } from '/games/dnd35/js/services/CombatenteService.js?v=20260427a';
import { CondicaoController    } from '/games/dnd35/js/controllers/CondicaoController.js';
import { MagiaSlotService      } from '/games/dnd35/js/services/MagiaSlotService.js?v=20260402a';
import { MagiaPreparadaService } from '/games/dnd35/js/services/MagiaPreparadaService.js?v=20260401b';
import { Toast } from '/games/dnd35/js/ui/toast.module.js';
import { escapeHtml } from '/games/dnd35/js/utils/formatters.js';
import { isClasseConjuradora, isTipoJogador, isTipoMonstro, resolveCombatenteSpellSlots, normalizeClasseConjuradora } from '/games/dnd35/js/utils/combat-rules.js?v=20260419a';
import { getApiUrl } from '/games/dnd35/js/config/api.config.js';

export class ArenaController {

    constructor() {
        this.combatenteService     = new CombatenteService();
        this.condicaoController    = new CondicaoController();
        this.magiaSlotService      = new MagiaSlotService();
        this.magiaPreparadaService = new MagiaPreparadaService();
        this.combatentes           = [];
        this.turnoAtual            = 0;
        this.rodadaAtual           = 1;
        this.statsVisiveis         = false;
        this._cronometroSegundos   = 0;
        this._cronometroInterval   = null;
        this._cronometroAtivo      = false;
        this._jaAgiram             = [];
        this._actions              = null;
        this._cardAtivoRenderState = null;
        this._canal                = new BroadcastChannel('magias-rpg');
        this._canal.onmessage      = (event) => {
            if (event?.data?.tipo === 'magia-preparada-atualizada') {
                if (event.data?.resetSlots) {
                    var combatenteReset = this.combatentes.find(function(c) {
                        return Number(c.id) === Number(event.data.combatenteId);
                    });
                    if (combatenteReset && Array.isArray(combatenteReset.magias_slots)) {
                        combatenteReset.magias_slots = combatenteReset.magias_slots.map(function(slot) {
                            return { ...slot, usados: 0 };
                        });
                    }
                }
                this._sincronizarMagiasPreparadasCombatente(event.data.combatenteId);
            }
        };
        this.token                 = localStorage.getItem('token');
        this.combateId             = null;
        this.versaoCombate         = null;
        this._inicializar();
    }

    _obterAssinaturaOrdemIniciativa() {
        return this.combatentes.map(function(c) {
            return String(c.id);
        }).join('|');
    }

    _capturarBadgesOrdemExistentes(container) {
        var badgesPorId = new Map();
        if (!container) {
            return badgesPorId;
        }

        var wrappers = container.querySelectorAll('.combatente-ordem-item[data-combatente-id] .badges-condicao-ordem-wrapper');
        wrappers.forEach(function(wrapper) {
            var item = wrapper.closest('.combatente-ordem-item[data-combatente-id]');
            if (!item) {
                return;
            }
            badgesPorId.set(String(item.dataset.combatenteId), wrapper.innerHTML);
        });

        return badgesPorId;
    }

    _renderizarItemOrdemHTML(combatente, indice) {
        var ativo = (indice === this.turnoAtual);
        var jaAgiu = (this._jaAgiram.indexOf(combatente.id) !== -1);
        var hpPct = Math.max(0, Math.min(100, (combatente.hp_atual / combatente.hp_maximo) * 100));
        var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');
        var morto = (combatente.tipo === 'monstro') ? (combatente.hp_atual <= 0) : (combatente.hp_atual <= -10);
        var cls = 'combatente-ordem-item';

        if (ativo) cls += ' ativo';
        if (morto) cls += ' morto';
        if (jaAgiu) cls += ' ja-agiu';

        var html = '';
        html += '<div class="' + cls + '" data-combatente-id="' + combatente.id + '">';
        html += '<span class="ordem-iniciativa-valor">' + combatente.iniciativa + '</span>';
        html += '<div class="ordem-info">';
        html += '<div class="ordem-nome-linha">';
        html += '<span class="ordem-nome">' + escapeHtml(combatente.nome) + '</span>';
        if (jaAgiu) html += '<span class="ordem-agiu-badge">✓</span>';
        html += '</div>';
        html += '<div class="ordem-hp-bar">';
        html += '<div class="ordem-hp-fill" style="width:' + hpPct + '%;background:' + hpCor + ';"></div>';
        html += '</div>';
        html += '<div class="badges-condicao-ordem-wrapper"></div>';
        html += '</div>';
        html += '<span class="badge ' + this.getBadgeClass(combatente.tipo) + ' badge-mini">'
              + this.getEmojiTipo(combatente.tipo) + '</span>';
        html += '</div>';

        return html;
    }

    _reaplicarBadgesOrdem(container, badgesPorId) {
        if (!container || !(badgesPorId instanceof Map) || badgesPorId.size === 0) {
            return;
        }

        var self = this;
        badgesPorId.forEach(function(html, combatenteId) {
            var wrapper = container.querySelector(
                '.combatente-ordem-item[data-combatente-id="' + combatenteId + '"] .badges-condicao-ordem-wrapper'
            );
            if (!wrapper) {
                return;
            }
            wrapper.innerHTML = html;
        });
    }

    _podeAtualizarOrdemIncremental(container) {
        if (!container || container.children.length !== this.combatentes.length) {
            return false;
        }

        for (var i = 0; i < this.combatentes.length; i++) {
            var item = container.children[i];
            if (!item || String(item.dataset.combatenteId) !== String(this.combatentes[i].id)) {
                return false;
            }
        }

        return true;
    }

    _atualizarItemOrdemExistente(item, combatente, indice) {
        if (!item) {
            return;
        }

        var ativo = (indice === this.turnoAtual);
        var jaAgiu = (this._jaAgiram.indexOf(combatente.id) !== -1);
        var hpPct = Math.max(0, Math.min(100, (combatente.hp_atual / combatente.hp_maximo) * 100));
        var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');
        var morto = (combatente.tipo === 'monstro') ? (combatente.hp_atual <= 0) : (combatente.hp_atual <= -10);

        item.dataset.combatenteId = String(combatente.id);
        item.classList.toggle('ativo', ativo);
        item.classList.toggle('morto', morto);
        item.classList.toggle('ja-agiu', jaAgiu);

        var iniciativaEl = item.querySelector('.ordem-iniciativa-valor');
        if (iniciativaEl) {
            iniciativaEl.textContent = String(combatente.iniciativa);
        }

        var nomeEl = item.querySelector('.ordem-nome');
        if (nomeEl) {
            nomeEl.textContent = combatente.nome || '';
        }

        var nomeLinhaEl = item.querySelector('.ordem-nome-linha');
        if (nomeLinhaEl) {
            var badgeAgiuEl = nomeLinhaEl.querySelector('.ordem-agiu-badge');
            if (jaAgiu && !badgeAgiuEl) {
                badgeAgiuEl = document.createElement('span');
                badgeAgiuEl.className = 'ordem-agiu-badge';
                badgeAgiuEl.textContent = '✓';
                nomeLinhaEl.appendChild(badgeAgiuEl);
            }
            if (!jaAgiu && badgeAgiuEl) {
                badgeAgiuEl.remove();
            }
        }

        var hpFillEl = item.querySelector('.ordem-hp-fill');
        if (hpFillEl) {
            hpFillEl.style.width = hpPct + '%';
            hpFillEl.style.background = hpCor;
        }

        var tipoBadgeEl = item.querySelector('.badge-mini');
        if (tipoBadgeEl) {
            tipoBadgeEl.className = 'badge ' + this.getBadgeClass(combatente.tipo) + ' badge-mini';
            tipoBadgeEl.textContent = this.getEmojiTipo(combatente.tipo);
        }
    }

    _renderizarOrdemIniciativaCompleta(container, atualizarBadges) {
        var badgesPreservadas = atualizarBadges ? new Map() : this._capturarBadgesOrdemExistentes(container);
        var html = '';

        for (var i = 0; i < this.combatentes.length; i++) {
            html += this._renderizarItemOrdemHTML(this.combatentes[i], i);
        }

        container.innerHTML = html;

        if (!atualizarBadges) {
            this._reaplicarBadgesOrdem(container, badgesPreservadas);
        }
    }

    _atualizarOrdemIniciativaIncremental(container) {
        for (var i = 0; i < this.combatentes.length; i++) {
            this._atualizarItemOrdemExistente(container.children[i], this.combatentes[i], i);
        }
    }

    _inicializar() {
        this.condicaoController.init();
        this._configurarEventos();
        this._restaurarCombateAtivo();
    }

    _configurarEventos() {
        var self = this;
        document.addEventListener('iniciarCombate', async function(e) {
            if (e.detail && e.detail.status) {
                await self._aplicarStatusCombate(e.detail.status);
                return;
            }

            if (e.detail && e.detail.combatentes) {
                self.iniciarCombate(e.detail.combatentes);
            } else {
                Toast.error('Erro: Dados de combatentes invalidos');
            }
        });
    }

    _headers(includeJson = false, includeVersion = false) {
        const headers = {};
        if (includeJson) {
            headers['Content-Type'] = 'application/json';
        }
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        if (includeVersion && this.versaoCombate) {
            headers['If-Match'] = this.versaoCombate;
        }
        return headers;
    }

    _ordenarCombatentesPorStatus(combatentes, idsOrdenados) {
        if (!Array.isArray(combatentes) || !Array.isArray(idsOrdenados)) {
            return combatentes || [];
        }
        const mapa = new Map((combatentes || []).map(c => [c.id, c]));
        return idsOrdenados.map(id => mapa.get(id)).filter(Boolean);
    }

    async _aplicarStatusCombate(status) {
        if (!status || !status.ativo) {
            return;
        }

        const possuiCombatentesCompletos = Array.isArray(status.combatentes);
        const statusResumidoSemCombatentes = status.resumido === true && !possuiCombatentesCompletos;
        const turnoAnterior = Number(this.turnoAtual || 0);

        this.combateId = status.id || null;
        this.versaoCombate = status.versao || null;
        this.turnoAtual = Number(status.turno_atual || 0);
        this.rodadaAtual = Number(status.rodada_atual || 1);

        if (!statusResumidoSemCombatentes) {
            this.combatentes = this._ordenarCombatentesPorStatus(status.combatentes || [], status.combatentes_ids || []);
            this._jaAgiram = [];
            await this._carregarMagiasPreparadasTodos();
        }

        const telaArena = document.getElementById('telaArena');
        const telaConfiguracao = document.getElementById('telaConfiguracao');
        if (telaConfiguracao) telaConfiguracao.classList.remove('ativa');
        if (telaArena) telaArena.classList.add('ativa');

        this._resetarCronometro();
        this._iniciarCronometro();
        this.atualizarRodada();

        if (statusResumidoSemCombatentes) {
            this.renderizarOrdemIniciativa({ atualizarBadges: false });

            const idsParaAtualizar = new Set();
            const combatenteAnterior = this.combatentes[turnoAnterior];
            const combatenteAtual = this.combatentes[this.turnoAtual];

            if (combatenteAnterior && combatenteAnterior.id != null) {
                idsParaAtualizar.add(Number(combatenteAnterior.id));
            }
            if (combatenteAtual && combatenteAtual.id != null) {
                idsParaAtualizar.add(Number(combatenteAtual.id));
            }

            await Promise.all(Array.from(idsParaAtualizar).map((combatenteId) => {
                return this._atualizarBadgeOrdemCombatente(combatenteId, {
                    usarCache: false,
                    forcarRefresh: true,
                });
            }));
        } else {
            this.renderizarOrdemIniciativa();
        }

        this.renderizarCombatenteAtivo();
    }

    async _restaurarCombateAtivo() {
        try {
            const response = await fetch(getApiUrl('/combate/status'), {
                headers: this._headers(false, false),
            });

            if (!response.ok) {
                return;
            }

            const status = await response.json();
            if (status?.ativo) {
                await this._aplicarStatusCombate(status);
                Toast.info('Combate ativo restaurado apos recarregar a pagina.');
            }
        } catch (error) {
            console.warn('⚠️ Nao foi possivel restaurar combate ativo:', error?.message || error);
        }
    }

    async iniciarCombate(combatentes) {
        if (!combatentes || !Array.isArray(combatentes) || combatentes.length === 0) {
            Toast.error('Nenhum combatente valido para iniciar combate');
            return;
        }
        this.combatentes = combatentes.sort(function(a, b) {
            return b.iniciativa - a.iniciativa;
        });
        this.turnoAtual          = 0;
        this.rodadaAtual         = 1;
        this.statsVisiveis       = false;
        this._jaAgiram           = [];
        this._cronometroSegundos = 0;
        this._pararCronometro();
        await this._carregarMagiasPreparadasTodos();
        this._iniciarCronometro();
        this.atualizarRodada();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    async _carregarMagiasPreparadasTodos() {
        const promessas = this.combatentes
            .filter((c) => {
                c.magias_slots = resolveCombatenteSpellSlots(c);
                var isConj = isClasseConjuradora(c.classe)
                    || (c.magias_slots && c.magias_slots.some((s) => Number(s.total || 0) > 0));
                if (isConj) {
                    c._isConjurador = true;
                    var classeCanon = normalizeClasseConjuradora(c.classe);
                    if (classeCanon === 'Bardo' || classeCanon === 'Feiticeiro') {
                        c._isConjuradorEspontaneo = true;
                    }
                }
                return isConj;
            })
            .map(async (c) => {
                try {
                    if (c._isConjuradorEspontaneo) {
                        const possuiSlotSemId = (c.magias_slots || []).some((slot) => {
                            const id = Number(slot?.id ?? slot?.slot_id ?? 0);
                            return Number(slot?.total || 0) > 0 && !id;
                        });
                        if (possuiSlotSemId) {
                            c._slotsSyncEmAndamento = true;
                            try {
                                const slotsPersistidos = await this.magiaSlotService.salvarPorCombatente(c.id, c.magias_slots || []);
                                c.magias_slots = resolveCombatenteSpellSlots({ ...c, magias_slots: slotsPersistidos });
                            } finally {
                                c._slotsSyncEmAndamento = false;
                            }
                        }
                        c._magiasPreparadas = [];
                        c._magiasGrupos = {};
                        return;
                    }
                    const preparadas = await this.magiaPreparadaService.listar(c.id);
                    c._magiasPreparadas = preparadas;
                    c._magiasGrupos = this.magiaPreparadaService.agruparPorNivel(preparadas, c.magias_slots || []);
                } catch (err) {
                    console.warn(`⚠️ Sem magias preparadas para ${c.nome}:`, err.message);
                    c._magiasPreparadas = [];
                    c._magiasGrupos = {};
                }
            });
        await Promise.all(promessas);
    }

    async _sincronizarMagiasPreparadasCombatente(combatenteId) {
        if (!combatenteId) return;

        var combatente = this.combatentes.find(function(c) {
            return Number(c.id) === Number(combatenteId);
        });
        if (!combatente) return;

        combatente.magias_slots = resolveCombatenteSpellSlots(combatente);

        try {
            if (combatente._isConjuradorEspontaneo) {
                const possuiSlotSemId = (combatente.magias_slots || []).some(function(slot) {
                    var id = Number(slot?.id ?? slot?.slot_id ?? 0);
                    return Number(slot?.total || 0) > 0 && !id;
                });
                if (possuiSlotSemId) {
                    combatente._slotsSyncEmAndamento = true;
                    this._renderizarCardAtivoSeAtual(combatenteId, { carregarCondicoes: false });
                    try {
                        var slotsPersistidos = await this.magiaSlotService.salvarPorCombatente(combatente.id, combatente.magias_slots || []);
                        combatente.magias_slots = resolveCombatenteSpellSlots({ ...combatente, magias_slots: slotsPersistidos });
                    } finally {
                        combatente._slotsSyncEmAndamento = false;
                    }
                }
                this._renderizarCardAtivoSeAtual(combatenteId, { carregarCondicoes: false });
                return;
            }
            var preparadas = await this.magiaPreparadaService.listar(combatente.id);
            combatente._magiasPreparadas = preparadas;
            combatente._magiasGrupos = this.magiaPreparadaService.agruparPorNivel(preparadas, combatente.magias_slots || []);

            this._renderizarCardAtivoSeAtual(combatente.id, { carregarCondicoes: false });
        } catch (err) {
            console.warn(`⚠️ Falha ao sincronizar magias preparadas de ${combatente.nome}:`, err.message);
        }
    }

    _renderizarCardAtivoSeAtual(combatenteId, opcoes = {}) {
        var ativoAtual = this.combatentes[this.turnoAtual];
        if (!ativoAtual) {
            return;
        }

        if (Number(ativoAtual.id) !== Number(combatenteId)) {
            return;
        }

        this.renderizarCombatenteAtivo(opcoes);
    }

    async avancarTurno() {
        var idAtual = this.combatentes[this.turnoAtual]
            ? this.combatentes[this.turnoAtual].id : null;
        
        if (idAtual !== null && this._jaAgiram.indexOf(idAtual) === -1) {
            this._jaAgiram.push(idAtual);
        }
        
        this.turnoAtual++;
        if (this.turnoAtual >= this.combatentes.length) {
            this.turnoAtual  = 0;
            this.rodadaAtual++;
            this._jaAgiram   = [];
            this.atualizarRodada();
            Toast.success('Rodada ' + this.rodadaAtual + ' iniciada!');
        }
        this._resetarCronometro();
        this._iniciarCronometro();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    // ✅ CORRETO - SEM /v1 (getApiUrl já adiciona)
    async _decrementarDuracaoCondicoes(combatenteId) {
        try {
            
            const baseUrl = getApiUrl(`/condicoes/combatentes/${combatenteId}/avancar-turno`);
            
            const token = localStorage.getItem('token');
            
            if (!token) {
                console.warn('⚠️ Token não encontrado');
                return;
            }

            
            const res = await fetch(baseUrl, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            });
            
            if (!res.ok) {
                const errorText = await res.text();
                console.warn(`⚠️ HTTP ${res.status}: ${errorText}`);
                return;
            }
            
            const data = await res.json();
            
            // Recarregar condições do combatente atual
            const combatenteAtual = this.combatentes[this.turnoAtual];
            if (combatenteAtual && typeof this.condicaoController !== 'undefined') {
                await this.condicaoController.carregarCondicoesDoCombatente(combatenteAtual.id, {
                    forcarRefresh: true,
                });
            }
            
        } catch (err) {
            console.error('❌ Erro ao decrementar:', err);
        }
    }    

    toggleVisibilidadeStats() {
        this.statsVisiveis = !this.statsVisiveis;
        this.renderizarCombatenteAtivo();
        Toast.success(this.statsVisiveis ? 'Stats visiveis' : 'Stats ocultos');
    }

    atualizarRodada() {
        var el = document.getElementById('rodadaAtual');
        if (el) el.textContent = this.rodadaAtual;
    }

    atualizarInterface() {
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    atualizarInterfaceRapidaDanoCura(combatentesAfetados) {
        var idsAfetados = new Set((combatentesAfetados || []).map(function(id) {
            return Number(id);
        }));

        this.renderizarOrdemIniciativa({ atualizarBadges: false });

        var ativo = this.combatentes[this.turnoAtual];
        if (ativo && idsAfetados.has(Number(ativo.id))) {
            this.renderizarCombatenteAtivo();
        }
    }

    // ─── Cronômetro ────────────────────────────────────────

    _iniciarCronometro() {
        var self = this;
        this._cronometroAtivo    = true;
        this._cronometroInterval = setInterval(function() {
            self._cronometroSegundos++;
            self._atualizarDisplayCronometro();
        }, 1000);
        this._atualizarDisplayCronometro();
        this._atualizarBotaoCronometro();
    }

    _pararCronometro() {
        if (this._cronometroInterval) {
            clearInterval(this._cronometroInterval);
            this._cronometroInterval = null;
        }
        this._cronometroAtivo = false;
        this._atualizarBotaoCronometro();
    }

    _resetarCronometro() {
        this._pararCronometro();
        this._cronometroSegundos = 0;
        this._atualizarDisplayCronometro();
    }

    toggleCronometro() {
        if (this._cronometroAtivo) this._pararCronometro();
        else this._iniciarCronometro();
    }

    _formatarTempo(segundos) {
        var h  = Math.floor(segundos / 3600);
        var m  = Math.floor((segundos % 3600) / 60);
        var s  = segundos % 60;
        var hh = h > 0 ? ((h < 10 ? '0' + h : '' + h) + ':') : '';
        var mm = m < 10 ? '0' + m : '' + m;
        var ss = s < 10 ? '0' + s : '' + s;
        return hh + mm + ':' + ss;
    }

    _atualizarDisplayCronometro() {
        var el = document.getElementById('cronometroDisplay');
        if (el) el.textContent = this._formatarTempo(this._cronometroSegundos);
    }

    _atualizarBotaoCronometro() {
        var btn = document.getElementById('btnToggleCronometro');
        if (!btn) return;
        btn.textContent = this._cronometroAtivo ? '⏸' : '▶';
        btn.className   = 'btn-cronometro ' + (this._cronometroAtivo
            ? 'btn-cronometro-pausar' : 'btn-cronometro-retomar');
    }

    // ─── Magias via MagiaSlot (monstros/NPCs) ──────────────

    async _alterarUsadosMagia(slotId, nivel, acao) {
        var combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        var slot = null;
        for (var k = 0; k < (combatente.magias_slots || []).length; k++) {
            if (combatente.magias_slots[k].nivel === nivel) {
                slot = combatente.magias_slots[k]; break;
            }
        }
        if (!slot) return;

        var slotIdNum = Number(slotId);
        if (!slotIdNum) {
            slotIdNum = Number(slot.id ?? slot.slot_id ?? 0);
        }
        if (!slotIdNum) {
            Toast.error('Slot de magia ainda nao sincronizado para este nivel');
            return;
        }

        var novoUsados = slot.usados;
        if (acao === 'aumentar') {
            if (slot.usados >= slot.total) {
                Toast.error('Todos os slots do nivel ' + nivel + ' ja foram usados!'); return;
            }
            novoUsados = slot.usados + 1;
        } else {
            if (slot.usados <= 0) {
                Toast.error('Nenhum slot usado no nivel ' + nivel); return;
            }
            novoUsados = slot.usados - 1;
        }

        try {
            await this.magiaSlotService.atualizarUsados(slotIdNum, novoUsados);
            slot.usados = novoUsados;
            this._atualizarUISlot(nivel, slot);
            Toast.success('NIV ' + nivel + ': ' + (slot.total - novoUsados) + '/' + slot.total + ' disponiveis');
        } catch (err) {
            Toast.error(
                err.message || ('Erro ao atualizar slots de magia no nível ' + nivel + ' para ' + (combatente.nome || 'combatente atual'))
            );
        }
    }

    _atualizarUISlot(nivel, slot) {
        var spanValor   = document.querySelector('.arena-magia-valor[data-nivel="' + nivel + '"]');
        var btnConsumir = document.querySelector('.arena-magia-btn[data-acao="aumentar"][data-nivel="' + nivel + '"]');
        var btnDevolver = document.querySelector('.arena-magia-btn[data-acao="diminuir"][data-nivel="' + nivel + '"]');
        if (spanValor)   spanValor.textContent = (slot.total - slot.usados);
        if (btnConsumir) btnConsumir.disabled  = (slot.usados >= slot.total);
        if (btnDevolver) btnDevolver.disabled  = (slot.usados <= 0);
    }

    async _lancarMagiaPreparada(combatenteId, magiaId, nivel, acaoPreparo, instancia) {
        var combatente = this.combatentes.find(function(c) {
            return Number(c.id) === Number(combatenteId);
        }) || this.combatentes[this.turnoAtual];
        if (!combatente) return;

        var grupo = (combatente._magiasGrupos || {})[nivel];
        if (!grupo) { Toast.error('Nenhuma magia preparada no nível ' + nivel); return; }

        var magiaPrep = grupo.preparadas.find(function(p) {
            return Number(p.magia_id) === Number(magiaId)
                && Number(p._instanceIndex || 1) === Number(instancia || 1);
        }) || grupo.preparadas.find(function(p) { return Number(p.magia_id) === Number(magiaId); });
        if (!magiaPrep) { Toast.error('Magia não encontrada nas preparadas'); return; }

        try {
            var data = await this.magiaPreparadaService.toggleUsada(combatenteId, magiaId, acaoPreparo || 'usar');
            await this._sincronizarMagiasPreparadasCombatente(combatenteId);

            var combatenteAtualizado = this.combatentes.find(function(c) {
                return Number(c.id) === Number(combatenteId);
            }) || combatente;
            var grupoAtualizado = (combatenteAtualizado._magiasGrupos || {})[nivel] || grupo;

            this._publicarEventoMagia(combatenteId, magiaId, nivel, data.usada, grupoAtualizado);
            Toast.success((acaoPreparo === 'restaurar' ? '↩️ ' : '🔥 ')
                + (magiaPrep.magia_nome || 'Magia')
                + (acaoPreparo === 'restaurar' ? ' restaurada' : ' lançada!'));
        } catch (err) {
            var nomeMagia = magiaPrep.magia_nome || ('magia #' + magiaId);
            Toast.error(err.message || ('Erro ao lançar ' + nomeMagia + ' no nível ' + nivel));
        }
    }

    _publicarEventoMagia(combatenteId, magiaId, nivel, usada, grupo) {
        try {
            this._canal.postMessage({
                tipo:         'magia-usada',
                combatenteId: combatenteId,
                magiaId:      magiaId,
                nivel:        nivel,
                usada:        usada,
                disponiveis:  grupo.total - grupo.usadas,
                total:        grupo.total,
                timestamp:    Date.now(),
            });
        } catch (err) {
            console.warn('⚠️ BroadcastChannel indisponível:', err.message);
        }
    }

    _atualizarUIPreparada(nivel, grupo, magiaId, usada) {
        var spanDisp = document.querySelector(
            '.arena-magia-preparada-nivel[data-nivel="' + nivel + '"] .arena-prep-disponiveis'
        );
        if (spanDisp) {
            var disponiveis = grupo.total - grupo.usadas;
            spanDisp.textContent = disponiveis + '/' + grupo.total;
            spanDisp.style.color = disponiveis === 0 ? '#f87171'
                                 : grupo.usadas > 0  ? '#facc15'
                                 :                     '#4ade80';
        }
        var btn = document.querySelector('.arena-prep-btn[data-magia-id="' + magiaId + '"]');
        if (btn) {
            btn.textContent = usada ? '↩️' : '🔥';
            btn.title       = usada ? 'Restaurar magia' : 'Lançar magia';
            btn.classList.toggle('arena-prep-btn-usada', usada);
        }
        var nome = document.querySelector('.arena-prep-nome[data-magia-id="' + magiaId + '"]');
        if (nome) nome.classList.toggle('arena-prep-nome-usada', usada);
    }

    // ─── Render: Ordem de Iniciativa ───────────────────────

    renderizarOrdemIniciativa(opcoes = {}) {
        var container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;
        var atualizarBadges = opcoes.atualizarBadges !== false;

        if (this._podeAtualizarOrdemIncremental(container)) {
            this._atualizarOrdemIniciativaIncremental(container);
        } else {
            this._renderizarOrdemIniciativaCompleta(container, atualizarBadges);
        }

        this.renderizarFotoAtivo();
        if (atualizarBadges) {
            this._atualizarBadgesOrdemTodos();
        }
    }

    async _atualizarBadgesOrdemTodos() {
        var tamanhoLote = 4;

        for (var i = 0; i < this.combatentes.length; i += tamanhoLote) {
            var lote = this.combatentes.slice(i, i + tamanhoLote);

            await Promise.all(lote.map(async (c) => {
                await this._atualizarBadgeOrdemCombatente(c.id, { usarCache: true });
            }));
        }
    }

    async _atualizarBadgeOrdemCombatente(combatenteId, opcoes = {}) {
        var el = document.querySelector(
            '.combatente-ordem-item[data-combatente-id="' + combatenteId + '"]'
        );
        if (!el) return;

        try {
            await this.condicaoController.atualizarBadgesOrdem(el, combatenteId, opcoes);
        } catch (err) {
            console.warn('⚠️ Falha ao atualizar badge de condição:', combatenteId, err?.message || err);
        }
    }

    renderizarFotoAtivo() {
        var container = document.getElementById('arenaFotoAtivo');
        if (!container) return;
        var c = this.combatentes[this.turnoAtual];
        if (!c) {
            container.replaceChildren();
            delete container.dataset.fotoKey;
            return;
        }

        var fotoKey = [String(c.id || ''), c.foto_url || '', c.nome || '', c.tipo || ''].join('|');
        if (container.dataset.fotoKey === fotoKey) {
            return;
        }

        container.dataset.fotoKey = fotoKey;

        if (c.foto_url) {
            var imagem = container.querySelector('img[data-role="arena-foto-ativo"]');
            if (!imagem) {
                imagem = document.createElement('img');
                imagem.setAttribute('data-role', 'arena-foto-ativo');
                imagem.style.width = '100%';
                imagem.style.height = '100%';
                imagem.style.objectFit = 'cover';
                imagem.style.borderRadius = '8px';
                container.replaceChildren(imagem);
            }
            imagem.src = c.foto_url;
            imagem.alt = c.nome || '';
            return;
        }

        var placeholder = container.querySelector('.arena-foto-vertical-placeholder');
        if (!placeholder) {
            placeholder = document.createElement('div');
            placeholder.className = 'arena-foto-vertical-placeholder';
            container.replaceChildren(placeholder);
        }
        placeholder.textContent = this.getEmojiTipo(c.tipo);
    }

    _obterAssinaturaMagiasCardAtivo(combatente) {
        if (!combatente) {
            return 'sem-magias';
        }

        if (combatente._isConjuradorEspontaneo) {
            return 'slots:' + (combatente.magias_slots || []).map(function(slot) {
                return [
                    Number(slot?.nivel ?? -1),
                    Number(slot?.total ?? 0),
                    Number(slot?.usados ?? 0),
                    Number(slot?.id ?? slot?.slot_id ?? 0),
                ].join(':');
            }).join('|');
        }

        if (combatente._isConjurador) {
            return 'preparadas:' + Object.keys(combatente._magiasGrupos || {})
                .sort(function(a, b) { return Number(a) - Number(b); })
                .map(function(nivel) {
                    var grupo = combatente._magiasGrupos[nivel] || {};
                    var preparadas = (grupo.preparadas || []).map(function(prep) {
                        return [
                            Number(prep?.magia_id ?? 0),
                            prep?.usada ? '1' : '0',
                            Number(prep?._instanceIndex ?? 1),
                            Number(prep?._instanceTotal ?? 1),
                        ].join(':');
                    }).join(',');
                    return [
                        Number(nivel),
                        Number(grupo.total ?? 0),
                        Number(grupo.usadas ?? 0),
                        preparadas,
                    ].join(':');
                }).join('|');
        }

        return 'sem-magias';
    }

    _obterAssinaturaEstruturalCardAtivo(combatente) {
        if (!combatente) {
            return null;
        }

        var ataquesAssinatura = (combatente.ataques || []).map(function(ataque) {
            return String(ataque?.id ?? ataque?.nome ?? '');
        }).join('|');
        var modoMagia = combatente._isConjuradorEspontaneo
            ? 'slots'
            : (combatente._isConjurador ? 'preparadas' : 'nenhum');

        return [
            String(combatente.id || ''),
            modoMagia,
            ataquesAssinatura,
            this._obterAssinaturaMagiasCardAtivo(combatente),
        ].join('::');
    }

    _atualizarEstadoRenderCardAtivo(combatente) {
        this._cardAtivoRenderState = combatente ? {
            combatenteId: Number(combatente.id),
            estruturaKey: this._obterAssinaturaEstruturalCardAtivo(combatente),
        } : null;
    }

    _podeAtualizarCardAtivoIncremental(container, combatente) {
        if (!container || !combatente || !this._cardAtivoRenderState) {
            return false;
        }

        if (Number(this._cardAtivoRenderState.combatenteId) !== Number(combatente.id)) {
            return false;
        }

        if (this._cardAtivoRenderState.estruturaKey !== this._obterAssinaturaEstruturalCardAtivo(combatente)) {
            return false;
        }

        return Boolean(
            container.querySelector('.arena-card')
            && container.querySelector('.arena-nome-text')
            && container.querySelector('.arena-raca-classe')
            && container.querySelector('.arena-pv-valor')
            && container.querySelector('.arena-hp-fill')
            && container.querySelector('.arena-condicoes-lista')
        );
    }

    _renderizarMetaCombatenteAtivo(combatente) {
        var raca = combatente.raca || '';
        var classe = combatente.classe || 'Aventureiro';
        var refBadge = (isTipoMonstro(combatente.tipo) && combatente.pagina_referencia)
            ? ' <span class="arena-badge-referencia" title="Referência do livro">📖 '
            + escapeHtml(String(combatente.pagina_referencia)) + '</span>'
            : '';

        return escapeHtml(raca ? (raca + ' / ') : '')
            + escapeHtml(classe)
            + ' <span class="badge ' + this.getBadgeClass(combatente.tipo) + '">'
            + escapeHtml(String(combatente.tipo || '')) + '</span>'
            + refBadge;
    }

    _atualizarCabecalhoCardAtivo(container, combatente) {
        var nomeEl = container.querySelector('.arena-nome-text');
        if (nomeEl) {
            nomeEl.textContent = combatente.nome || '';
        }

        var nivelEl = container.querySelector('.arena-nivel');
        if (nivelEl) {
            nivelEl.textContent = '(' + (combatente.nivel || 1) + '° nivel)';
        }

        var metaEl = container.querySelector('.arena-raca-classe');
        if (metaEl) {
            metaEl.innerHTML = this._renderizarMetaCombatenteAtivo(combatente);
        }
    }

    _atualizarDefesasCardAtivo(container, combatente) {
        var hpPct = Math.max(0, Math.min(100, (combatente.hp_atual / combatente.hp_maximo) * 100));
        var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');
        var statsVisiveis = this.statsVisiveis;
        var pvValor = statsVisiveis
            ? ((combatente.hp_atual ?? 0) + '/' + (combatente.hp_maximo ?? 0))
            : '???/???';

        var pvEl = container.querySelector('.arena-pv-valor');
        if (pvEl) {
            pvEl.textContent = pvValor;
            pvEl.classList.toggle('hp-oculto', !statsVisiveis);
        }

        var hpFillEl = container.querySelector('.arena-hp-fill');
        if (hpFillEl) {
            hpFillEl.style.width = hpPct + '%';
            hpFillEl.style.background = hpCor;
        }

        var caEl = container.querySelector('.arena-ca-valor');
        if (caEl) {
            caEl.textContent = statsVisiveis ? String(combatente.ca ?? 10) : '?';
            caEl.classList.toggle('hp-oculto', !statsVisiveis);
        }

        var surpresaEl = container.querySelector('[data-role="defesa-surpresa"]');
        if (surpresaEl) {
            surpresaEl.textContent = statsVisiveis ? String(combatente.surpresa ?? 10) : '?';
            surpresaEl.classList.toggle('hp-oculto', !statsVisiveis);
        }

        var toqueEl = container.querySelector('[data-role="defesa-toque"]');
        if (toqueEl) {
            toqueEl.textContent = statsVisiveis ? String(combatente.toque ?? 10) : '?';
            toqueEl.classList.toggle('hp-oculto', !statsVisiveis);
        }
    }

    _atualizarAtributosCardAtivo(container, combatente) {
        var self = this;
        var atributos = {
            forca: combatente.forca || 10,
            destreza: combatente.destreza || 10,
            constituicao: combatente.constituicao || 10,
            inteligencia: combatente.inteligencia || 10,
            sabedoria: combatente.sabedoria || 10,
            carisma: combatente.carisma || 10,
        };

        Object.keys(atributos).forEach(function(chave) {
            var valor = atributos[chave];
            var valorEl = container.querySelector('[data-atributo="' + chave + '"] .arena-atributo-valor');
            var modEl = container.querySelector('[data-atributo="' + chave + '"] .arena-atributo-mod');
            if (valorEl) {
                valorEl.textContent = String(valor);
            }
            if (modEl) {
                var modificador = self.calcularModificador(valor);
                modEl.textContent = modificador >= 0 ? ('+' + modificador) : String(modificador);
            }
        });
    }

    _atualizarResistenciasCardAtivo(container, combatente) {
        ['fortitude', 'reflexos', 'vontade'].forEach(function(chave) {
            var valor = Number(combatente[chave] ?? 0);
            var el = container.querySelector('[data-resistencia="' + chave + '"] .arena-atributo-valor');
            if (el) {
                el.textContent = valor >= 0 ? ('+' + valor) : String(valor);
            }
        });
    }

    _atualizarControlesBasicosCardAtivo(container) {
        var btnToggleStatsArena = container.querySelector('#btnToggleStatsArena');
        if (btnToggleStatsArena) {
            btnToggleStatsArena.textContent = this.statsVisiveis ? 'Ocultar Stats' : 'Revelar Stats';
        }

        var displayCronometro = container.querySelector('#cronometroDisplay');
        if (displayCronometro) {
            displayCronometro.classList.toggle('cronometro-ativo', this._cronometroAtivo);
            displayCronometro.classList.toggle('cronometro-pausado', !this._cronometroAtivo);
        }

        this._atualizarDisplayCronometro();
        this._atualizarBotaoCronometro();
    }

    _atualizarPlaceholderCondicoesCardAtivo(container) {
        var lista = container.querySelector('.arena-condicoes-lista');
        if (!lista) {
            return;
        }

        var possuiCondicoes = Array.from(lista.children).some(function(filho) {
            return !filho.classList.contains('arena-condicao-vazia');
        });
        var placeholder = lista.querySelector('.arena-condicao-vazia');

        if (possuiCondicoes) {
            if (placeholder) {
                placeholder.remove();
            }
            return;
        }

        if (!placeholder) {
            placeholder = document.createElement('span');
            placeholder.className = 'arena-condicao-vazia';
            placeholder.textContent = 'Nenhuma condição ativa';
            lista.replaceChildren(placeholder);
            return;
        }

        if (lista.children.length > 1) {
            lista.replaceChildren(placeholder);
        }
    }

    _atualizarCardAtivoIncremental(container, combatente) {
        this.renderizarFotoAtivo();
        this._atualizarCabecalhoCardAtivo(container, combatente);
        this._atualizarDefesasCardAtivo(container, combatente);
        this._atualizarAtributosCardAtivo(container, combatente);
        this._atualizarResistenciasCardAtivo(container, combatente);
        this._atualizarControlesBasicosCardAtivo(container);
        this._atualizarPlaceholderCondicoesCardAtivo(container);
        this._atualizarEstadoRenderCardAtivo(combatente);
    }

    // ─── Render: Combatente Ativo ───────────────────────────

    renderizarCombatenteAtivo(opcoes = {}) {
        var carregarCondicoes = opcoes.carregarCondicoes !== false;
        var container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        var c = this.combatentes[this.turnoAtual];
        if (!c) {
            container.replaceChildren();
            this._atualizarEstadoRenderCardAtivo(null);
            return;
        }

        if (this._podeAtualizarCardAtivoIncremental(container, c)) {
            this._atualizarCardAtivoIncremental(container, c);
            if (carregarCondicoes) {
                this.condicaoController.carregarCondicoesDoCombatente(c.id);
            }
            return;
        }

        this.renderizarFotoAtivo();

        var hpPct = Math.max(0, Math.min(100, (c.hp_atual / c.hp_maximo) * 100));
        var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');

        var ca       = c.ca        ?? 10;
        var toque    = c.toque     ?? 10;
        var surpresa = c.surpresa  ?? 10;
        var fort     = c.fortitude ?? 0;
        var reflex   = c.reflexos  ?? 0;
        var vont     = c.vontade   ?? 0;
        var nivel    = c.nivel     || 1;

        function mod(val) {
            var m = Math.floor(((val || 10) - 10) / 2);
            return m >= 0 ? ('+' + m) : ('' + m);
        }
        function sinal(val) { return val >= 0 ? ('+' + val) : ('' + val); }

        var pvValor = this.statsVisiveis ? (c.hp_atual + '/' + c.hp_maximo) : '???/???';
        var caValor = this.statsVisiveis ? ca       : '?';
        var sValor  = this.statsVisiveis ? surpresa : '?';
        var tValor  = this.statsVisiveis ? toque    : '?';
        var olhoTxt = this.statsVisiveis ? 'Ocultar Stats' : 'Revelar Stats';
        var cronAtivo  = this._cronometroAtivo;
        var tempoAtual = this._formatarTempo(this._cronometroSegundos);

        var atribs = [
            ['For', c.forca        || 10], ['Des', c.destreza     || 10],
            ['Con', c.constituicao || 10], ['Int', c.inteligencia || 10],
            ['Sab', c.sabedoria    || 10], ['Car', c.carisma      || 10],
        ];

        var atributosHTML = '';
        for (var j = 0; j < atribs.length; j++) {
            atributosHTML += '<div class="arena-atributo-box" data-atributo="'
                + ({ For:'forca', Des:'destreza', Con:'constituicao', Int:'inteligencia', Sab:'sabedoria', Car:'carisma' })[atribs[j][0]]
                + '">'
                + '<span class="arena-atributo-nome">'  + atribs[j][0] + '</span>'
                + '<span class="arena-atributo-valor">' + atribs[j][1] + '</span>'
                + '<span class="arena-atributo-mod">'   + mod(atribs[j][1]) + '</span>'
                + '</div>';
        }

        var ataquesHTML = this._renderizarAtaques(c.ataques || []);
        
        // Conjuradores sempre usam estilo "magias preparadas"
        var magiasHTML = '';
        if (c._isConjuradorEspontaneo) {
            magiasHTML = this._renderizarMagias(c.magias_slots || [], c.tipo, '⚡ Slots de Magia', !!c._slotsSyncEmAndamento);
        } else if (c._isConjurador) {
            magiasHTML = this._renderizarMagiasPreparadas(c._magiasGrupos || {}, c.id);
        }

        var html = '';
        html += '<div class="arena-card">';

        // ── Header ──
        html += '<div class="arena-header">';
        html += '<div class="arena-header-nome">';
        html += '<h2 class="arena-nome"><span class="arena-nome-text">' + escapeHtml(c.nome || '')
            + '</span> <span class="arena-nivel">(' + nivel + '° nivel)</span></h2>';
        html += '<span class="arena-raca-classe">' + this._renderizarMetaCombatenteAtivo(c) + '</span>';
        html += '</div>';
        html += '<div class="arena-header-acoes">';
        html += '<div class="arena-cronometro-inline">';
        html += '<span class="arena-cronometro-display '
            + (cronAtivo ? 'cronometro-ativo' : 'cronometro-pausado')
            + '" id="cronometroDisplay">' + tempoAtual + '</span>';
        html += '<button id="btnToggleCronometro" class="btn-cronometro '
            + (cronAtivo ? 'btn-cronometro-pausar' : 'btn-cronometro-retomar')
            + '">'
            + (cronAtivo ? '⏸' : '▶') + '</button>';
        html += '<button class="btn-cronometro btn-cronometro-reset" id="btnResetarCronometro">↺</button>';
        html += '</div>';
        html += '<button class="btn-toggle-stats" id="btnToggleStatsArena">'
            + olhoTxt + '</button>';
        html += '</div></div>';

        // ── Layout principal ──
        html += '<div class="arena-layout-principal">';

        // Coluna esquerda
        html += '<div class="arena-coluna-esquerda">';
        html += '<div class="arena-linha-info">';
        html += '<div class="arena-secao arena-secao-atributos">';
        html += '<h3 class="arena-secao-titulo">Atributos</h3>';
        html += '<div class="arena-atributos-grid">' + atributosHTML + '</div>';
        html += '</div>';
        html += '<div class="arena-secao arena-secao-resistencias">';
        html += '<h3 class="arena-secao-titulo">Resistencias</h3>';
        html += '<div class="arena-resistencias-grid">';
        html += '<div class="arena-atributo-box" data-resistencia="fortitude"><span class="arena-atributo-nome">Fort</span>'
            + '<span class="arena-atributo-valor">' + sinal(fort) + '</span></div>';
        html += '<div class="arena-atributo-box" data-resistencia="reflexos"><span class="arena-atributo-nome">Reflex</span>'
            + '<span class="arena-atributo-valor">' + sinal(reflex) + '</span></div>';
        html += '<div class="arena-atributo-box" data-resistencia="vontade"><span class="arena-atributo-nome">Vont</span>'
            + '<span class="arena-atributo-valor">' + sinal(vont) + '</span></div>';
        html += '</div></div>';
        html += '<div class="arena-secao arena-secao-condicoes">';
        html += '<h3 class="arena-secao-titulo">Condicoes</h3>';
        html += '<div class="arena-condicoes-lista">'
            + '<span class="arena-condicao-vazia">Nenhuma condição ativa</span></div>';
        html += '</div>';
        html += '</div></div>';

        // Coluna central
        html += '<div class="arena-coluna-central">';
        html += ataquesHTML;
        html += magiasHTML;  // ✅ Será vazio se não tem magias
        html += '</div>';

        // Coluna direita
        html += '<div class="arena-coluna-direita">';
        html += '<div class="arena-defesa-box">';
        html += '<div class="arena-ca-principal">';
        html += '<span class="arena-defesa-label">CA</span>';
        html += '<span class="arena-ca-valor ' + (this.statsVisiveis ? '' : 'hp-oculto') + '">'
            + caValor + '</span>';
        html += '</div>';
        html += '<div class="arena-defesa-secundaria">';
        html += '<div class="arena-defesa-item"><span class="arena-defesa-label-sm">Surpresa</span>'
            + '<span class="arena-defesa-valor-sm ' + (this.statsVisiveis ? '' : 'hp-oculto') + '" data-role="defesa-surpresa">'
            + sValor + '</span></div>';
        html += '<div class="arena-defesa-item"><span class="arena-defesa-label-sm">Toque</span>'
            + '<span class="arena-defesa-valor-sm ' + (this.statsVisiveis ? '' : 'hp-oculto') + '" data-role="defesa-toque">'
            + tValor + '</span></div>';
        html += '</div></div>';
        html += '<div class="arena-pv-box">';
        html += '<span class="arena-defesa-label">PV</span>';
        html += '<span class="arena-pv-valor ' + (this.statsVisiveis ? '' : 'hp-oculto') + '">'
            + pvValor + '</span>';
        html += '<div class="arena-hp-bar"><div class="arena-hp-fill" style="width:'
            + hpPct + '%;background:' + hpCor + ';"></div></div>';
        html += '</div>';
        html += '<button class="arena-btn-proximo" id="btnAvancarTurnoArena">'
            + 'Encerrar turno</button>';
        html += '</div>';  // fim coluna-direita
        html += '</div>';  // fim layout-principal
        html += '</div>';  // fim arena-card

        container.innerHTML = html;

        this._registrarAcoesGlobais();
        this._configurarControlesCardAtivo(container);

        this._configurarEventosMagias(container);
        this._atualizarEstadoRenderCardAtivo(c);
        if (carregarCondicoes) {
            this.condicaoController.carregarCondicoesDoCombatente(c.id);
        }
    }

    _configurarControlesCardAtivo(container) {
        var btnToggleCronometro = container.querySelector('#btnToggleCronometro');
        if (btnToggleCronometro) {
            btnToggleCronometro.addEventListener('click', () => this.toggleCronometro());
        }

        var btnResetarCronometro = container.querySelector('#btnResetarCronometro');
        if (btnResetarCronometro) {
            btnResetarCronometro.addEventListener('click', () => {
                this._resetarCronometro();
                this._iniciarCronometro();
            });
        }

        var btnToggleStatsArena = container.querySelector('#btnToggleStatsArena');
        if (btnToggleStatsArena) {
            btnToggleStatsArena.addEventListener('click', () => this.toggleVisibilidadeStats());
        }

        var btnAvancarTurnoArena = container.querySelector('#btnAvancarTurnoArena');
        if (btnAvancarTurnoArena) {
            btnAvancarTurnoArena.addEventListener('click', () => this.avancarTurno());
        }
    }

    _registrarAcoesGlobais() {
        if (this._actions) {
            return;
        }

        var self = this;
        this._actions = {
            abrirDanoCura: function() {
                if (typeof modalDanoCuraInstance !== 'undefined') {
                    modalDanoCuraInstance.abrir(self.combatentes);
                }
            },
            abrirCondicao: function() {
                if (typeof modalCondicaoInstance !== 'undefined') {
                    modalCondicaoInstance.abrir();
                } else {
                    console.error('modalCondicaoInstance nao inicializado');
                }
            },
            toggleStats: function() { self.toggleVisibilidadeStats(); },
            avancarTurno: function() { self.avancarTurno(); },
            finalizarCombate: function() { self.finalizarCombate(); },
            toggleCronometro: function() { self.toggleCronometro(); },
            resetarCronometro: function() {
                self._resetarCronometro();
                self._iniciarCronometro();
            }
        };

        window.arenaActions = this._actions;
    }

    // Fluxo principal usa apenas /combate/avancar-turno para avancar e decrementar condicoes.
    async avancarTurno() {
        var idAtual = this.combatentes[this.turnoAtual]
            ? this.combatentes[this.turnoAtual].id : null;
        
        if (idAtual !== null && this._jaAgiram.indexOf(idAtual) === -1) {
            this._jaAgiram.push(idAtual);
        }
        
        if (this.combateId) {
            try {
                const rodadaAnterior = this.rodadaAtual;
                const response = await fetch(getApiUrl('/combate/avancar-turno?resumido=true'), {
                    method: 'POST',
                    headers: this._headers(false, true),
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.detail || `Erro ao avançar turno (HTTP ${response.status})`);
                }

                const status = await response.json();
                await this._aplicarStatusCombate(status);
                if (this.rodadaAtual > rodadaAnterior) {
                    this._jaAgiram = [];
                    Toast.success('Rodada ' + this.rodadaAtual + ' iniciada!');
                }
                return;
            } catch (error) {
                Toast.error(error.message || 'Erro ao avançar turno');
                return;
            }
        }

        this.turnoAtual++;
        if (this.turnoAtual >= this.combatentes.length) {
            this.turnoAtual = 0;
            this.rodadaAtual++;
            this._jaAgiram = [];
            this.atualizarRodada();
            Toast.success('Rodada ' + this.rodadaAtual + ' iniciada!');
        }
        this._resetarCronometro();
        this._iniciarCronometro();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    _configurarEventosMagias(container) {
        var self = this;
        container.querySelectorAll('.arena-magia-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var slotId = btn.getAttribute('data-slot-id');
                var acao   = btn.getAttribute('data-acao');
                var nivel  = parseInt(btn.getAttribute('data-nivel'));
                self._alterarUsadosMagia(slotId, nivel, acao);
            });
        });
        container.querySelectorAll('.arena-prep-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var combatenteId = parseInt(btn.getAttribute('data-combatente-id'));
                var magiaId      = parseInt(btn.getAttribute('data-magia-id'));
                var nivel        = parseInt(btn.getAttribute('data-nivel'));
                var acaoPreparo  = btn.getAttribute('data-acao-preparo') || 'usar';
                var instancia    = parseInt(btn.getAttribute('data-instancia') || '1');
                self._lancarMagiaPreparada(combatenteId, magiaId, nivel, acaoPreparo, instancia);
            });
        });
    }

    _renderizarAtaques(ataques) {
        var html = '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">Ataques</h3>';
        html += '<div class="arena-ataques-lista">';
        html += '<div class="arena-ataque-header"><span>Nome</span><span>Ataque</span><span>Dano</span></div>';
        if (!ataques || ataques.length === 0) {
            html += '<div class="arena-ataque-item arena-ataque-placeholder"><span>Nenhum ataque cadastrado</span></div>';
        } else {
            for (var i = 0; i < ataques.length; i++) {
                var a    = ataques[i];
                var tipo = a.tipo_dano ? ' (' + a.tipo_dano + ')' : '';
                html += '<div class="arena-ataque-item"><span>' + a.nome + '</span>'
                      + '<span>' + a.bonus_ataque + '</span>'
                      + '<span>' + a.dano + tipo + '</span></div>';
            }
        }
        html += '</div></div>';
        return html;
    }

    _renderizarMagiasPreparadas(grupos, combatenteId) {
        var niveisOrdenados = Object.keys(grupos).map(Number).sort(function(a, b) { return a - b; });

        if (niveisOrdenados.length === 0) {
            return '<div class="arena-secao">'
                 + '<h3 class="arena-secao-titulo">Magias Preparadas</h3>'
                 + '<div class="arena-magia-vazio">Nenhuma magia preparada hoje.<br>'
                 + '<small>Abra o Grimório na ficha do personagem.</small></div>'
                 + '</div>';
        }

        var html = '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">🔮 Magias Preparadas</h3>';
        html += '<div class="arena-magias-preparadas-lista">';

        niveisOrdenados.forEach(function(nivel) {
            var grupo       = grupos[nivel];
            var disponiveis = grupo.total - grupo.usadas;
            var corDisp     = disponiveis === 0 ? '#f87171'
                            : grupo.usadas > 0  ? '#facc15'
                            :                     '#4ade80';

            html += '<div class="arena-magia-preparada-nivel" data-nivel="' + nivel + '">';
            html += '<div class="arena-prep-nivel-header">';
            html += '<span class="arena-prep-nivel-label">NIV ' + nivel + '</span>';
            html += '<span class="arena-prep-disponiveis" style="color:' + corDisp + '">'
                  + disponiveis + '/' + grupo.total + '</span>';
            html += '</div>';

            grupo.preparadas.forEach(function(prep) {
                var usada = prep.usada;
                var instanciaAtual = Number(prep._instanceIndex || 1);
                var instanciaTotal = Number(prep._instanceTotal || 1);
                html += '<div class="arena-prep-magia-row ' + (usada ? 'arena-prep-usada' : '') + '">';
                html += '<span class="arena-prep-nome ' + (usada ? 'arena-prep-nome-usada' : '') + '"'
                      + ' data-magia-id="' + prep.magia_id + '" data-instancia="' + instanciaAtual + '">'
                      + (prep.magia_nome || 'Magia #' + prep.magia_id) + '</span>';
                if (instanciaTotal > 1) {
                    html += '<span class="arena-prep-instancia">' + instanciaAtual + '/' + instanciaTotal + '</span>';
                }
                if (prep.magia_escola) {
                    html += '<span class="arena-prep-escola">' + prep.magia_escola + '</span>';
                }
                html += '<button class="arena-prep-btn ' + (usada ? 'arena-prep-btn-usada' : '') + '"'
                      + ' data-combatente-id="' + combatenteId + '"'
                      + ' data-magia-id="' + prep.magia_id + '"'
                      + ' data-nivel="' + nivel + '"'
                      + ' data-instancia="' + instanciaAtual + '"'
                      + ' data-acao-preparo="' + (usada ? 'restaurar' : 'usar') + '"'
                      + ' title="' + (usada ? 'Restaurar esta cópia' : 'Lançar esta cópia') + '">'
                      + (usada ? '↩️' : '🔥') + '</button>';
                html += '</div>';
            });

            html += '</div>';
        });

        html += '</div></div>';
        return html;
    }

    _renderizarMagias(slots, tipo, titulo, sincronizando) {
        var isJogador = isTipoJogador(tipo);
        var self      = this;
        var html      = '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">' + (titulo || 'Controle de Magias') + '</h3>';
        if (sincronizando) {
            html += '<div class="arena-magia-vazio"><small>Sincronizando slots para uso na arena...</small></div>';
        }
        html += '<div class="arena-magias-duas-colunas">';
        html += '<div class="arena-magias-coluna">';
        html += '<div class="arena-magias-coluna-titulo">NIV 0–4</div>';
        for (var n1 = 0; n1 <= 4; n1++) html += self._renderizarMagiaLinha(slots, n1, isJogador);
        html += '</div>';
        html += '<div class="arena-magias-coluna">';
        html += '<div class="arena-magias-coluna-titulo">NIV 5–9</div>';
        for (var n2 = 5; n2 <= 9; n2++) html += self._renderizarMagiaLinha(slots, n2, isJogador);
        html += '</div>';
        html += '</div></div>';
        return html;
    }

    _renderizarMagiaLinha(slots, nivel, isJogador) {
        var slot = null;
        for (var k = 0; k < slots.length; k++) {
            if (slots[k].nivel === nivel) { slot = slots[k]; break; }
        }
        var total       = slot ? slot.total  : 0;
        var usados      = slot ? slot.usados : 0;
        var disponiveis = total - usados;
        var slotId      = slot ? Number(slot.id ?? slot.slot_id ?? 0) : 0;
        var semId       = !slotId;
        var disAumentar = (!isJogador || total === 0 || usados >= total || semId) ? 'disabled' : '';
        var disDiminuir = (!isJogador || total === 0 || usados <= 0 || semId)    ? 'disabled' : '';
        var linhaClass  = 'arena-magia-linha' + (total === 0 ? ' magia-sem-slot' : '');

        var html = '<div class="' + linhaClass + '" data-nivel="' + nivel + '">';
        html += '<span class="arena-magia-nivel">NIV ' + nivel + '</span>';
        html += '<div class="arena-magia-controle">';
        html += '<button class="arena-magia-btn arena-magia-btn-diminuir"'
              + ' data-slot-id="' + slotId + '" data-acao="aumentar" data-nivel="' + nivel + '"'
              + ' ' + disAumentar + '>-</button>';
        html += '<span class="arena-magia-valor" data-nivel="' + nivel + '">' + disponiveis + '</span>';
        html += '<span class="arena-magia-sep">/</span>';
        html += '<span class="arena-magia-total-inline">' + total + '</span>';
        html += '<button class="arena-magia-btn arena-magia-btn-aumentar"'
              + ' data-slot-id="' + slotId + '" data-acao="diminuir" data-nivel="' + nivel + '"'
              + ' ' + disDiminuir + '>+</button>';
        html += '</div></div>';
        return html;
    }

    calcularModificador(valor) { return Math.floor((valor - 10) / 2); }

    getBadgeClass(tipo) {
        return { jogador:'badge-jogador', monstro:'badge-monstro', npc:'badge-npc' }[tipo] || 'badge-default';
    }

    getEmojiTipo(tipo) {
        return { jogador:'🧙', monstro:'👹', npc:'🤝' }[tipo] || '⚔️';
    }

    _mostrarModalConfirmacao(opcoes) {
        var overlay = document.createElement('div');
        overlay.id        = 'modalConfirmacaoArena';
        overlay.className = 'arena-modal-overlay';
        overlay.innerHTML =
            '<div class="arena-modal-confirmacao">'
          + '<div class="arena-modal-confirmacao-header">'
          + '<span class="arena-modal-confirmacao-icone">' + (opcoes.icone || '⚔️') + '</span>'
          + '<h3 class="arena-modal-confirmacao-titulo">' + (opcoes.titulo || 'Confirmar') + '</h3>'
          + '</div>'
          + '<p class="arena-modal-confirmacao-texto">' + (opcoes.texto || 'Deseja continuar?') + '</p>'
          + '<div class="arena-modal-confirmacao-botoes">'
          + '<button class="arena-modal-btn arena-modal-btn-cancelar" id="btnModalCancelar">'
          + (opcoes.textoCancelar || 'Cancelar') + '</button>'
          + '<button class="arena-modal-btn arena-modal-btn-confirmar" id="btnModalConfirmar">'
          + (opcoes.textoConfirmar || 'Confirmar') + '</button>'
          + '</div></div>';

        document.body.appendChild(overlay);
        requestAnimationFrame(function() { overlay.classList.add('arena-modal-overlay-show'); });

        var self = this;
        function fechar() {
            overlay.classList.remove('arena-modal-overlay-show');
            setTimeout(function() {
                if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
            }, 250);
        }

        document.getElementById('btnModalCancelar').addEventListener('click', function() {
            fechar(); if (opcoes.onCancelar) opcoes.onCancelar();
        });
        document.getElementById('btnModalConfirmar').addEventListener('click', function() {
            fechar(); if (opcoes.onConfirmar) opcoes.onConfirmar();
        });
        overlay.addEventListener('click', function(e) { if (e.target === overlay) fechar(); });
    }

    finalizarCombate() {
        var self = this;
        this._mostrarModalConfirmacao({
            icone: '🏳️', titulo: 'Encerrar Combate',
            texto: 'Deseja finalizar o combate e voltar para a configuração?',
            textoCancelar: '← Continuar Combate', textoConfirmar: 'Encerrar ✓',
            onConfirmar: async function() {
                if (self.combateId) {
                    try {
                        const response = await fetch(getApiUrl('/combate/finalizar'), {
                            method: 'POST',
                            headers: self._headers(false, true),
                        });

                        if (!response.ok) {
                            const err = await response.json().catch(() => ({}));
                            throw new Error(err.detail || `Erro ao finalizar combate (HTTP ${response.status})`);
                        }
                    } catch (error) {
                        Toast.error(error.message || 'Erro ao finalizar combate');
                        return;
                    }
                }

                self._pararCronometro();
                try { self._canal.close(); } catch(e) {}
                var telaArena        = document.getElementById('telaArena');
                var telaConfiguracao = document.getElementById('telaConfiguracao');
                if (telaArena)        telaArena.classList.remove('ativa');
                if (telaConfiguracao) telaConfiguracao.classList.add('ativa');
                self._atualizarEstadoRenderCardAtivo(null);
                self.combateId = null;
                self.versaoCombate = null;
                Toast.success('Combate finalizado!');
            }
        });
    }

    resetarCombate() {
        var self = this;
        this._mostrarModalConfirmacao({
            icone: '🔄', titulo: 'Resetar Combate',
            texto: 'Deseja resetar o combate? Todos voltarão ao HP máximo.',
            textoCancelar: '← Cancelar', textoConfirmar: 'Resetar ✓',
            onConfirmar: async function() {
                if (self.combateId) {
                    try {
                        const response = await fetch(getApiUrl('/combate/resetar'), {
                            method: 'POST',
                            headers: self._headers(false, false),
                        });
                        if (!response.ok) {
                            const err = await response.json().catch(() => ({}));
                            throw new Error(err.detail || `Erro ao resetar combate (HTTP ${response.status})`);
                        }
                    } catch (error) {
                        Toast.error(error.message || 'Erro ao resetar combate');
                        return;
                    }
                } else {
                    self.combatentes.forEach(function(c) {
                        c.hp_atual = c.hp_maximo;
                        self.combatenteService.atualizarHP(c.id, c.hp_maximo).catch(console.error);
                    });
                }

                self.turnoAtual    = 0;
                self.rodadaAtual   = 1;
                self.statsVisiveis = false;
                self._jaAgiram     = [];
                self.combateId     = null;
                self.versaoCombate = null;
                self._resetarCronometro();
                self._iniciarCronometro();
                self.atualizarRodada();
                Toast.success('Combate resetado!');
                self.renderizarOrdemIniciativa();
                self.renderizarCombatenteAtivo();
            }
        });
    }
}