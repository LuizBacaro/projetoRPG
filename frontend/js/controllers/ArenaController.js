import { CombatenteService     } from '../services/CombatenteService.js';
import { CondicaoController    } from './CondicaoController.js';
import { MagiaSlotService      } from '../services/MagiaSlotService.js';
import { MagiaPreparadaService } from '../services/MagiaPreparadaService.js';
import { Toast } from '/js/ui/toast.module.js';

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
        this._canal                = new BroadcastChannel('magias-rpg');
        this._inicializar();
    }

    _inicializar() {
        this.condicaoController.init();
        this._configurarEventos();
    }

    _configurarEventos() {
        var self = this;
        document.addEventListener('iniciarCombate', function(e) {
            if (e.detail && e.detail.combatentes) {
                self.iniciarCombate(e.detail.combatentes);
            } else {
                Toast.error('Erro: Dados de combatentes invalidos');
            }
        });
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
        const CLASSES_CONJURADORAS = new Set([
            'mago','feiticeiro','clérigo','clerigo','druida',
            'bardo','paladino','ranger',
            'Mago','Feiticeiro','Clérigo','Clerigo','Druida',
            'Bardo','Paladino','Ranger',
        ]);
        const promessas = this.combatentes
            .filter(c => c.tipo === 'jogador' && CLASSES_CONJURADORAS.has(c.classe))
            .map(async c => {
                try {
                    const preparadas    = await this.magiaPreparadaService.listar(c.id);
                    c._magiasPreparadas = preparadas;
                    c._magiasGrupos     = this.magiaPreparadaService.agruparPorNivel(preparadas);
                    console.log(`✅ ${c.nome}: ${preparadas.length} magias preparadas`);
                } catch (err) {
                    console.warn(`⚠️ Sem magias preparadas para ${c.nome}:`, err.message);
                    c._magiasPreparadas = [];
                    c._magiasGrupos     = {};
                }
            });
        await Promise.all(promessas);
    }

    avancarTurno() {
        var idAtual = this.combatentes[this.turnoAtual]
            ? this.combatentes[this.turnoAtual].id : null;
        if (idAtual !== null && this._jaAgiram.indexOf(idAtual) === -1) {
            this._jaAgiram.push(idAtual);
        }
        
        // ✅ NOVO: Decrementar duração das condições do combatente atual ANTES de passar turno
        if (idAtual !== null && typeof this.condicaoController !== 'undefined') {
            this._decrementarDuracaoCondicoes(idAtual);
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

    // ✅ NOVO: Método para decrementar duração das condições
    async _decrementarDuracaoCondicoes(combatenteId) {
        try {
            const url = window.getApiUrl(`/condicoes/combatentes/${combatenteId}/avancar-turno`);
            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (!res.ok) {
                console.warn('⚠️ Erro ao decrementar duração das condições:', res.status);
                return;
            }
            
            const data = await res.json();
            const combatente = this.combatentes[this.turnoAtual];
            
            // Recarregar condições na UI
            if (combatente && typeof this.condicaoController !== 'undefined') {
                await this.condicaoController.carregarCondicoesDoCombatente(combatente.id);
            }
            
            console.log(`⏰ Duração das condições de #${combatenteId} decrementada`);
        } catch (err) {
            console.error('❌ Erro ao decrementar condições:', err);
            // Não quebra o fluxo do jogo — apenas loga o erro
        }
    }

    toggleVisibilidadeStats() {
        this.statsVisiveis = !this.statsVisiveis;
        this.renderizarOrdemIniciativa();
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
        if (!slotId || slotId === 'null') {
            Toast.error('Slot de magia nao encontrado para este nivel');
            return;
        }
        var combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        var slot = null;
        for (var k = 0; k < (combatente.magias_slots || []).length; k++) {
            if (combatente.magias_slots[k].nivel === nivel) {
                slot = combatente.magias_slots[k]; break;
            }
        }
        if (!slot) return;

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
            await this.magiaSlotService.atualizarUsados(slotId, novoUsados);
            slot.usados = novoUsados;
            this._atualizarUISlot(nivel, slot);
            Toast.success('NIV ' + nivel + ': ' + (slot.total - novoUsados) + '/' + slot.total + ' disponiveis');
        } catch (err) {
            Toast.error('Erro ao atualizar magia: ' + (err.message || ''));
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

    async _lancarMagiaPreparada(combatenteId, magiaId, nivel) {
        var combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        var grupo = (combatente._magiasGrupos || {})[nivel];
        if (!grupo) { Toast.error('Nenhuma magia preparada no nível ' + nivel); return; }

        var magiaPrep = grupo.preparadas.find(function(p) { return p.magia_id === magiaId; });
        if (!magiaPrep) { Toast.error('Magia não encontrada nas preparadas'); return; }

        try {
            var data = await this.magiaPreparadaService.toggleUsada(combatenteId, magiaId);
            magiaPrep.usada = data.usada;
            grupo.usadas    = grupo.preparadas.filter(function(p) { return p.usada; }).length;
            this._atualizarUIPreparada(nivel, grupo, magiaId, data.usada);
            this._publicarEventoMagia(combatenteId, magiaId, nivel, data.usada, grupo);
            Toast.success(data.usada
                ? '🔥 ' + (magiaPrep.magia_nome || 'Magia') + ' lançada!'
                : '↩️ ' + (magiaPrep.magia_nome || 'Magia') + ' restaurada'
            );
        } catch (err) {
            Toast.error('Erro ao lançar magia: ' + (err.message || ''));
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

    renderizarOrdemIniciativa() {
        var container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;
        var self = this;
        var html = '';
        for (var i = 0; i < this.combatentes.length; i++) {
            var c      = this.combatentes[i];
            var ativo  = (i === this.turnoAtual);
            var jaAgiu = (this._jaAgiram.indexOf(c.id) !== -1);
            var hpPct  = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
            var hpCor  = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');
            var morto  = (c.hp_atual <= 0);
            var cls    = 'combatente-ordem-item';
            if (ativo)  cls += ' ativo';
            if (morto)  cls += ' morto';
            if (jaAgiu) cls += ' ja-agiu';

            html += '<div class="' + cls + '" data-combatente-id="' + c.id + '">';
            html += '<span class="ordem-iniciativa-valor">' + c.iniciativa + '</span>';
            html += '<div class="ordem-info">';
            html += '<div class="ordem-nome-linha">';
            html += '<span class="ordem-nome">' + c.nome + '</span>';
            if (jaAgiu) html += '<span class="ordem-agiu-badge">✓</span>';
            html += '</div>';
            html += '<div class="ordem-hp-bar">';
            html += '<div class="ordem-hp-fill" style="width:' + hpPct + '%;background:' + hpCor + ';"></div>';
            html += '</div>';
            html += '<div class="badges-condicao-ordem-wrapper"></div>';
            html += '</div>';
            html += '<span class="badge ' + self.getBadgeClass(c.tipo) + ' badge-mini">'
                  + self.getEmojiTipo(c.tipo) + '</span>';
            html += '</div>';
        }
        container.innerHTML = html;
        this.renderizarFotoAtivo();
        this._atualizarBadgesOrdemTodos();
    }

    _atualizarBadgesOrdemTodos() {
        var self = this;
        var i = 0;
        function next() {
            if (i >= self.combatentes.length) return;
            var c  = self.combatentes[i++];
            var el = document.querySelector(
                '.combatente-ordem-item[data-combatente-id="' + c.id + '"]'
            );
            if (el) self.condicaoController.atualizarBadgesOrdem(el, c.id).then(next);
            else    next();
        }
        next();
    }

    renderizarFotoAtivo() {
        var container = document.getElementById('arenaFotoAtivo');
        if (!container) return;
        var c = this.combatentes[this.turnoAtual];
        if (!c) { container.innerHTML = ''; return; }
        container.innerHTML = c.foto_url
            ? '<img src="' + c.foto_url + '" alt="' + c.nome
              + '" style="width:100%;height:100%;object-fit:cover;border-radius:8px;">'
            : '<div class="arena-foto-vertical-placeholder">' + this.getEmojiTipo(c.tipo) + '</div>';
    }

    // ─── Render: Combatente Ativo ───────────────────────────

    renderizarCombatenteAtivo() {
        var container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        var c = this.combatentes[this.turnoAtual];
        if (!c) return;

        this.renderizarFotoAtivo();

        var hpPct = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
        var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');

        var ca       = c.ca        ?? 10;
        var toque    = c.toque     ?? 10;
        var surpresa = c.surpresa  ?? 10;
        var fort     = c.fortitude ?? 0;
        var reflex   = c.reflexos  ?? 0;
        var vont     = c.vontade   ?? 0;
        var nivel    = c.nivel     || 1;
        var classe   = c.classe    || 'Aventureiro';
        var raca     = c.raca      || '';

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
            atributosHTML += '<div class="arena-atributo-box">'
                + '<span class="arena-atributo-nome">'  + atribs[j][0] + '</span>'
                + '<span class="arena-atributo-valor">' + atribs[j][1] + '</span>'
                + '<span class="arena-atributo-mod">'   + mod(atribs[j][1]) + '</span>'
                + '</div>';
        }

        var ataquesHTML = this._renderizarAtaques(c.ataques || []);
        
        // ✅ NOVO: Verificar se tem magias antes de renderizar
        var temMagias = (c._magiasGrupos && Object.keys(c._magiasGrupos).length > 0) ||
                        (c.magias_slots && c.magias_slots.length > 0 && 
                        c.magias_slots.some(function(s) { return s.total > 0; }));
        
        var magiasHTML = temMagias
            ? ((c._magiasGrupos && Object.keys(c._magiasGrupos).length > 0)
                ? this._renderizarMagiasPreparadas(c._magiasGrupos, c.id)
                : this._renderizarMagias(c.magias_slots || [], c.tipo))
            : '';  // ✅ String vazia se não tem magias com slots > 0

        var refBadge = (c.tipo === 'monstro' && c.pagina_referencia)
            ? ' <span class="arena-badge-referencia" title="Referência do livro">📖 '
            + c.pagina_referencia + '</span>'
            : '';

        var html = '';
        html += '<div class="arena-card">';

        // ── Header ──
        html += '<div class="arena-header">';
        html += '<div class="arena-header-nome">';
        html += '<h2 class="arena-nome">' + c.nome
            + ' <span class="arena-nivel">(' + nivel + '° nivel)</span></h2>';
        html += '<span class="arena-raca-classe">'
            + (raca ? raca + ' / ' : '') + classe
            + ' <span class="badge ' + this.getBadgeClass(c.tipo) + '">' + c.tipo + '</span>'
            + refBadge
            + '</span>';
        html += '</div>';
        html += '<div class="arena-header-acoes">';
        html += '<div class="arena-cronometro-inline">';
        html += '<span class="arena-cronometro-display '
            + (cronAtivo ? 'cronometro-ativo' : 'cronometro-pausado')
            + '" id="cronometroDisplay">' + tempoAtual + '</span>';
        html += '<button id="btnToggleCronometro" class="btn-cronometro '
            + (cronAtivo ? 'btn-cronometro-pausar' : 'btn-cronometro-retomar')
            + '" onclick="window._toggleCronometro()">'
            + (cronAtivo ? '⏸' : '▶') + '</button>';
        html += '<button class="btn-cronometro btn-cronometro-reset"'
            + ' onclick="window._resetarCronometro()">↺</button>';
        html += '</div>';
        html += '<button class="btn-toggle-stats" onclick="window._toggleStats()">'
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
        html += '<div class="arena-atributo-box"><span class="arena-atributo-nome">Fort</span>'
            + '<span class="arena-atributo-valor">' + sinal(fort) + '</span></div>';
        html += '<div class="arena-atributo-box"><span class="arena-atributo-nome">Reflex</span>'
            + '<span class="arena-atributo-valor">' + sinal(reflex) + '</span></div>';
        html += '<div class="arena-atributo-box"><span class="arena-atributo-nome">Vont</span>'
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
            + '<span class="arena-defesa-valor-sm ' + (this.statsVisiveis ? '' : 'hp-oculto') + '">'
            + sValor + '</span></div>';
        html += '<div class="arena-defesa-item"><span class="arena-defesa-label-sm">Toque</span>'
            + '<span class="arena-defesa-valor-sm ' + (this.statsVisiveis ? '' : 'hp-oculto') + '">'
            + tValor + '</span></div>';
        html += '</div></div>';
        html += '<div class="arena-pv-box">';
        html += '<span class="arena-defesa-label">PV</span>';
        html += '<span class="arena-pv-valor ' + (this.statsVisiveis ? '' : 'hp-oculto') + '">'
            + pvValor + '</span>';
        html += '<div class="arena-hp-bar"><div class="arena-hp-fill" style="width:'
            + hpPct + '%;background:' + hpCor + ';"></div></div>';
        html += '</div>';
        html += '<button class="arena-btn-proximo" onclick="window._avancarTurno()">'
            + 'Encerrar turno</button>';
        html += '</div>';  // fim coluna-direita
        html += '</div>';  // fim layout-principal
        html += '</div>';  // fim arena-card

        container.innerHTML = html;

        var self = this;
        window._abrirDanoCura     = function() {
            if (typeof modalDanoCuraInstance !== 'undefined') modalDanoCuraInstance.abrir(self.combatentes);
        };
        window._abrirCondicao     = function() {
            if (typeof modalCondicaoInstance !== 'undefined') modalCondicaoInstance.abrir();
            else console.error('modalCondicaoInstance nao inicializado');
        };
        window._toggleStats       = function() { self.toggleVisibilidadeStats(); };
        window._avancarTurno      = function() { self.avancarTurno(); };
        window._finalizarCombate  = function() { self.finalizarCombate(); };
        window._toggleCronometro  = function() { self.toggleCronometro(); };
        window._resetarCronometro = function() {
            self._resetarCronometro(); self._iniciarCronometro();
        };

        this._configurarEventosMagias(container);
        this.condicaoController.carregarCondicoesDoCombatente(c.id);
    }

    // ✅ NOVO: Método para decrementar duração das condições
    async _decrementarDuracaoCondicoes(combatenteId) {
        try {
            console.log(`⏰ Decrementando duração de condições para combatente #${combatenteId}...`);
            
            const url = window.getApiUrl(`/condicoes/combatentes/${combatenteId}/avancar-turno`);
            const token = localStorage.getItem('token');
            
            if (!token) {
                console.warn('⚠️ Token não encontrado');
                return;
            }

            const res = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (!res.ok) {
                console.warn(`⚠️ Erro ao decrementar duração: HTTP ${res.status}`);
                const errMsg = await res.text();
                console.warn('   Resposta:', errMsg);
                return;
            }
            
            const data = await res.json();
            console.log(`✅ Duração decrementada. Condições ativas: ${data.condicoes?.length || 0}`);
            
            // Recarregar condições no combatente ativo PRÓXIMO
            if (this.turnoAtual < this.combatentes.length) {
                const proximoCombatente = this.combatentes[this.turnoAtual];
                if (proximoCombatente && typeof this.condicaoController !== 'undefined') {
                    await this.condicaoController.carregarCondicoesDoCombatente(proximoCombatente.id);
                }
            }
            
        } catch (err) {
            console.error('❌ Erro ao decrementar duração das condições:', err);
            // Não quebra o fluxo do jogo — apenas loga o erro
        }
    }

    // ✅ REFATORADO: avancarTurno() com decremento de duração
    avancarTurno() {
        var idAtual = this.combatentes[this.turnoAtual]
            ? this.combatentes[this.turnoAtual].id : null;
        
        if (idAtual !== null && this._jaAgiram.indexOf(idAtual) === -1) {
            this._jaAgiram.push(idAtual);
        }
        
        // ✅ NOVO: Decrementar duração das condições do combatente atual ANTES de passar turno
        if (idAtual !== null && typeof this.condicaoController !== 'undefined') {
            this._decrementarDuracaoCondicoes(idAtual);
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
                self._lancarMagiaPreparada(combatenteId, magiaId, nivel);
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
                html += '<div class="arena-prep-magia-row ' + (usada ? 'arena-prep-usada' : '') + '">';
                html += '<span class="arena-prep-nome ' + (usada ? 'arena-prep-nome-usada' : '') + '"'
                      + ' data-magia-id="' + prep.magia_id + '">'
                      + (prep.magia_nome || 'Magia #' + prep.magia_id) + '</span>';
                if (prep.magia_escola) {
                    html += '<span class="arena-prep-escola">' + prep.magia_escola + '</span>';
                }
                html += '<button class="arena-prep-btn ' + (usada ? 'arena-prep-btn-usada' : '') + '"'
                      + ' data-combatente-id="' + combatenteId + '"'
                      + ' data-magia-id="' + prep.magia_id + '"'
                      + ' data-nivel="' + nivel + '"'
                      + ' title="' + (usada ? 'Restaurar magia' : 'Lançar magia') + '">'
                      + (usada ? '↩️' : '🔥') + '</button>';
                html += '</div>';
            });

            html += '</div>';
        });

        html += '</div></div>';
        return html;
    }

    _renderizarMagias(slots, tipo) {
        var isJogador = (tipo === 'jogador');
        var self      = this;
        var html      = '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">Controle de Magias</h3>';
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
        var slotId      = slot ? slot.id     : null;
        var disAumentar = (!isJogador || total === 0 || usados >= total) ? 'disabled' : '';
        var disDiminuir = (!isJogador || total === 0 || usados <= 0)    ? 'disabled' : '';
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
            onConfirmar: function() {
                self._pararCronometro();
                try { self._canal.close(); } catch(e) {}
                var telaArena        = document.getElementById('telaArena');
                var telaConfiguracao = document.getElementById('telaConfiguracao');
                if (telaArena)        telaArena.classList.remove('ativa');
                if (telaConfiguracao) telaConfiguracao.classList.add('ativa');
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
            onConfirmar: function() {
                self.combatentes.forEach(function(c) {
                    c.hp_atual = c.hp_maximo;
                    self.combatenteService.atualizarHP(c.id, c.hp_maximo).catch(console.error);
                });
                self.turnoAtual    = 0;
                self.rodadaAtual   = 1;
                self.statsVisiveis = false;
                self._jaAgiram     = [];
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