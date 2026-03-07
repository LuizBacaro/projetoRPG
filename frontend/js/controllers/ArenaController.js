import { CombatenteService  } from '../services/CombatenteService.js';
import { CondicaoController } from './CondicaoController.js';
import { MagiaSlotService   } from '../services/MagiaSlotService.js';
import { Toast              } from '../ui/Toast.js';

export class ArenaController {

    constructor() {
        this.combatenteService   = new CombatenteService();
        this.condicaoController  = new CondicaoController();
        this.magiaSlotService    = new MagiaSlotService();
        this.combatentes         = [];
        this.turnoAtual          = 0;
        this.rodadaAtual         = 1;
        this.statsVisiveis       = false;
        this._cronometroSegundos = 0;
        this._cronometroInterval = null;
        this._cronometroAtivo    = false;
        this._jaAgiram           = [];
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

    iniciarCombate(combatentes) {
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
        this._iniciarCronometro();
        this.atualizarRodada();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    avancarTurno() {
        var idAtual = this.combatentes[this.turnoAtual] ? this.combatentes[this.turnoAtual].id : null;
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
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
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

    // ─── Cronometro ────────────────────────────────────────

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
        if (this._cronometroAtivo) {
            this._pararCronometro();
        } else {
            this._iniciarCronometro();
        }
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
        btn.textContent = this._cronometroAtivo ? '⏸ Pausar' : '▶ Retomar';
        btn.className   = 'btn-cronometro ' + (this._cronometroAtivo ? 'btn-cronometro-pausar' : 'btn-cronometro-retomar');
    }

    // ─── Magias: lógica funcional ──────────────────────────

    async _alterarUsadosMagia(slotId, nivel, acao) {
        if (!slotId || slotId === 'null') {
            Toast.error('Slot de magia nao encontrado para este nivel');
            return;
        }

        var combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        var slot = null;
        for (var k = 0; k < combatente.magias_slots.length; k++) {
            if (combatente.magias_slots[k].nivel === nivel) {
                slot = combatente.magias_slots[k];
                break;
            }
        }
        if (!slot) return;

        var novoUsados = slot.usados;
        if (acao === 'aumentar') {
            if (slot.usados >= slot.total) {
                Toast.error('Todos os slots do nivel ' + nivel + ' ja foram usados!');
                return;
            }
            novoUsados = slot.usados + 1;
        } else {
            if (slot.usados <= 0) {
                Toast.error('Nenhum slot usado no nivel ' + nivel);
                return;
            }
            novoUsados = slot.usados - 1;
        }

        try {
            await this.magiaSlotService.atualizarUsados(slotId, novoUsados);
            slot.usados = novoUsados;

            // Atualiza display sem re-renderizar o card inteiro
            var spanValor = document.querySelector('.arena-magia-valor[data-nivel="' + nivel + '"]');
            if (spanValor) spanValor.textContent = novoUsados;

            // Atualiza estado visual dos botoes
            var btnDiminuir = document.querySelector('.arena-magia-btn[data-acao="diminuir"][data-nivel="' + nivel + '"]');
            var btnAumentar = document.querySelector('.arena-magia-btn[data-acao="aumentar"][data-nivel="' + nivel + '"]');
            if (btnDiminuir) btnDiminuir.disabled = (novoUsados <= 0);
            if (btnAumentar) btnAumentar.disabled = (novoUsados >= slot.total);

            var msg = acao === 'aumentar'
                ? 'Slot nivel ' + nivel + ' usado (' + novoUsados + '/' + slot.total + ')'
                : 'Slot nivel ' + nivel + ' recuperado (' + novoUsados + '/' + slot.total + ')';
            Toast.success(msg);
        } catch (err) {
            Toast.error('Erro ao atualizar magia: ' + (err.message || ''));
            console.error(err);
        }
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
            html += '<span class="badge ' + self.getBadgeClass(c.tipo) + ' badge-mini">' + self.getEmojiTipo(c.tipo) + '</span>';
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
            var el = document.querySelector('.combatente-ordem-item[data-combatente-id="' + c.id + '"]');
            if (el) {
                self.condicaoController.atualizarBadgesOrdem(el, c.id).then(next);
            } else {
                next();
            }
        }
        next();
    }

    renderizarFotoAtivo() {
        var container = document.getElementById('arenaFotoAtivo');
        if (!container) return;
        var c = this.combatentes[this.turnoAtual];
        if (!c) { container.innerHTML = ''; return; }
        container.innerHTML = c.foto_url
            ? '<img src="' + c.foto_url + '" alt="' + c.nome + '" style="width:100%;height:100%;object-fit:cover;">'
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

        var ca       = (c.ca        !== null && c.ca        !== undefined) ? c.ca        : 10;
        var toque    = (c.toque     !== null && c.toque     !== undefined) ? c.toque     : 10;
        var surpresa = (c.surpresa  !== null && c.surpresa  !== undefined) ? c.surpresa  : 10;
        var fort     = (c.fortitude !== null && c.fortitude !== undefined) ? c.fortitude : 0;
        var reflex   = (c.reflexos  !== null && c.reflexos  !== undefined) ? c.reflexos  : 0;
        var vont     = (c.vontade   !== null && c.vontade   !== undefined) ? c.vontade   : 0;
        var nivel    = c.nivel  || 1;
        var classe   = c.classe || 'Aventureiro';

        function mod(val) {
            var m = Math.floor(((val || 10) - 10) / 2);
            return m >= 0 ? ('+' + m) : ('' + m);
        }
        function sinal(val) {
            return val >= 0 ? ('+' + val) : ('' + val);
        }

        var pvValor  = this.statsVisiveis ? (c.hp_atual + '/' + c.hp_maximo) : '???/???';
        var pvClasse = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        var caValor  = this.statsVisiveis ? ca       : '?';
        var caClasse = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        var sValor   = this.statsVisiveis ? surpresa : '?';
        var sClasse  = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        var tValor   = this.statsVisiveis ? toque    : '?';
        var tClasse  = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        var olhoTxt  = this.statsVisiveis ? 'Ocultar Stats' : 'Revelar Stats';

        var atribs = [
            ['For', c.forca        || 10],
            ['Des', c.destreza     || 10],
            ['Con', c.constituicao || 10],
            ['Int', c.inteligencia || 10],
            ['Sab', c.sabedoria    || 10],
            ['Car', c.carisma      || 10]
        ];
        var atributosHTML = '';
        for (var j = 0; j < atribs.length; j++) {
            atributosHTML += '<div class="arena-atributo-box">';
            atributosHTML += '<span class="arena-atributo-nome">' + atribs[j][0] + '</span>';
            atributosHTML += '<span class="arena-atributo-valor">' + atribs[j][1] + '</span>';
            atributosHTML += '<span class="arena-atributo-mod">' + mod(atribs[j][1]) + '</span>';
            atributosHTML += '</div>';
        }

        var ataquesHTML = this._renderizarAtaques(c.ataques || []);
        var magiasHTML  = this._renderizarMagias(c.magias_slots || [], c.tipo);

        var fotoTopo = c.foto_url
            ? '<img src="' + c.foto_url + '" alt="' + c.nome + '">'
            : '<div class="arena-foto-placeholder">' + this.getEmojiTipo(c.tipo) + '</div>';

        var cronAtivo  = this._cronometroAtivo;
        var tempoAtual = this._formatarTempo(this._cronometroSegundos);

        var html = '';
        html += '<div class="arena-card">';

        // ── Topo
        html += '<div class="arena-topo">';
        html += '<div class="arena-foto-nome">';
        html += '<div class="arena-foto">' + fotoTopo + '</div>';
        html += '<div class="arena-nome-info">';
        html += '<h2 class="arena-nome">' + c.nome + ' (' + nivel + ' nivel)</h2>';
        html += '<span class="arena-classe">' + classe;
        html += '<span class="badge ' + this.getBadgeClass(c.tipo) + '">' + c.tipo + '</span>';
        html += '</span></div></div>';
        html += '<div class="arena-topo-acoes">';
        html += '<div class="arena-cronometro-inline">';
        html += '<span class="arena-cronometro-display ' + (cronAtivo ? 'cronometro-ativo' : 'cronometro-pausado') + '" id="cronometroDisplay">' + tempoAtual + '</span>';
        html += '<button id="btnToggleCronometro" class="btn-cronometro ' + (cronAtivo ? 'btn-cronometro-pausar' : 'btn-cronometro-retomar') + '" onclick="window._toggleCronometro()">' + (cronAtivo ? '⏸' : '▶') + '</button>';
        html += '<button class="btn-cronometro btn-cronometro-reset" onclick="window._resetarCronometro()">↺</button>';
        html += '</div>';
        html += '<button class="btn-toggle-stats" onclick="window._toggleStats()">' + olhoTxt + '</button>';
        html += '<button class="btn-encerrar-combate" onclick="window._finalizarCombate()">Encerrar combate</button>';
        html += '</div></div>';

        // ── Stats
        html += '<div class="arena-stats-linha">';
        html += '<div class="arena-stat-box arena-stat-pv">';
        html += '<span class="arena-stat-label">PV</span>';
        html += '<span class="' + pvClasse + '">' + pvValor + '</span>';
        html += '<div class="arena-hp-bar"><div class="arena-hp-fill" style="width:' + hpPct + '%;background:' + hpCor + ';"></div></div>';
        html += '</div>';
        html += '<div class="arena-stat-box arena-stat-ca"><span class="arena-stat-label">CA</span><span class="' + caClasse + '">' + caValor + '</span></div>';
        html += '<div class="arena-stat-box arena-stat-surpresa"><span class="arena-stat-label">Surpresa</span><span class="' + sClasse + '">' + sValor + '</span></div>';
        html += '<div class="arena-stat-box arena-stat-toque"><span class="arena-stat-label">Toque</span><span class="' + tClasse + '">' + tValor + '</span></div>';
        html += '</div>';

        // ── Grade central
        html += '<div class="arena-grade-central">';
        html += '<div class="arena-secao"><h3 class="arena-secao-titulo">Atributos</h3><div class="arena-atributos-grid">' + atributosHTML + '</div></div>';
        html += '<div class="arena-secao"><h3 class="arena-secao-titulo">Resistencias</h3><div class="arena-resistencias-lista">';
        html += '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Fortitude</span><span class="arena-resistencia-valor">' + sinal(fort)   + '</span></div>';
        html += '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Reflexos</span><span class="arena-resistencia-valor">'  + sinal(reflex) + '</span></div>';
        html += '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Vontade</span><span class="arena-resistencia-valor">'   + sinal(vont)   + '</span></div>';
        html += '</div></div>';
        html += '<div class="arena-secao"><h3 class="arena-secao-titulo">Condicoes</h3>';
        html += '<div class="arena-condicoes-lista"><span class="arena-condicao-vazia">Nenhuma condicao ativa</span></div></div>';
        html += '<div class="arena-secao arena-acoes-col"><h3 class="arena-secao-titulo">Aplicar</h3>';
        html += '<button class="arena-btn-dano-cura" onclick="window._abrirDanoCura()">Dano / Cura</button>';
        html += '<button class="arena-btn-condicao"  onclick="window._abrirCondicao()">Condicao</button>';
        html += '<button class="arena-btn-proximo"   onclick="window._avancarTurno()">Encerrar turno</button>';
        html += '</div></div>';

        // ── Linha inferior — SEM div futuro
        html += '<div class="arena-linha-inferior">';
        html += ataquesHTML;
        html += magiasHTML;
        html += '</div>';
        html += '</div>';

        container.innerHTML = html;

        var self = this;
        window._abrirDanoCura     = function() { if (typeof modalDanoCuraInstance !== 'undefined') modalDanoCuraInstance.abrir(self.combatentes); };
        window._abrirCondicao     = function() { if (typeof modalCondicaoInstance !== 'undefined') modalCondicaoInstance.abrir(); else console.error('modalCondicaoInstance nao inicializado'); };
        window._toggleStats       = function() { self.toggleVisibilidadeStats(); };
        window._avancarTurno      = function() { self.avancarTurno(); };
        window._finalizarCombate  = function() { self.finalizarCombate(); };
        window._toggleCronometro  = function() { self.toggleCronometro(); };
        window._resetarCronometro = function() { self._resetarCronometro(); self._iniciarCronometro(); };

        // ── Eventos dos botoes de magia (delegação no container)
        this._configurarEventosMagias(container);

        this.condicaoController.carregarCondicoesDoCombatente(c.id);
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
    }

    _renderizarAtaques(ataques) {
        var html = '';
        html += '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">Ataques</h3>';
        html += '<div class="arena-ataques-lista">';
        html += '<div class="arena-ataque-header"><span>Nome</span><span>Ataque</span><span>Dano</span></div>';
        if (!ataques || ataques.length === 0) {
            html += '<div class="arena-ataque-item arena-ataque-placeholder"><span>Nenhum ataque cadastrado</span></div>';
        } else {
            for (var i = 0; i < ataques.length; i++) {
                var a    = ataques[i];
                var tipo = a.tipo_dano ? ' (' + a.tipo_dano + ')' : '';
                html += '<div class="arena-ataque-item">';
                html += '<span>' + a.nome + '</span>';
                html += '<span>' + a.bonus_ataque + '</span>';
                html += '<span>' + a.dano + tipo + '</span>';
                html += '</div>';
            }
        }
        html += '</div></div>';
        return html;
    }

    _renderizarMagias(slots, tipo) {
        var isJogador = (tipo === 'jogador');
        var html = '';
        html += '<div class="arena-secao">';
        html += '<h3 class="arena-secao-titulo">Controle de Magias</h3>';
        html += '<div class="arena-magias-grid">';

        for (var nivel = 0; nivel <= 9; nivel++) {
            var slot = null;
            for (var k = 0; k < slots.length; k++) {
                if (slots[k].nivel === nivel) { slot = slots[k]; break; }
            }
            var total    = slot ? slot.total  : 0;
            var usados   = slot ? slot.usados : 0;
            var slotId   = slot ? slot.id     : null;

            // Botoes so ativos se for jogador, tiver total > 0 e dentro dos limites
            var disAumentar = (!isJogador || total === 0 || usados >= total) ? 'disabled' : '';
            var disDiminuir = (!isJogador || total === 0 || usados <= 0)    ? 'disabled' : '';

            // Calcula restante para exibir visualmente
            var restante = total - usados;
            var linhaClass = 'arena-magia-linha' + (total === 0 ? ' magia-sem-slot' : '');

            html += '<div class="' + linhaClass + '" data-nivel="' + nivel + '">';
            html += '<span class="arena-magia-nivel">NIV ' + nivel + '</span>';
            html += '<div class="arena-magia-controle">';
            html += '<button class="arena-magia-btn arena-magia-btn-diminuir" data-slot-id="' + slotId + '" data-acao="diminuir" data-nivel="' + nivel + '" ' + disDiminuir + '>-</button>';
            html += '<span class="arena-magia-valor" data-nivel="' + nivel + '">' + usados + '</span>';
            html += '<button class="arena-magia-btn arena-magia-btn-aumentar" data-slot-id="' + slotId + '" data-acao="aumentar" data-nivel="' + nivel + '" ' + disAumentar + '>+</button>';
            html += '</div>';
            html += '<div class="arena-magia-slots-info">';
            html += '<span class="arena-magia-usados-label">' + usados + '/' + total + '</span>';
            html += '<div class="arena-magia-pips">';
            for (var p = 0; p < total; p++) {
                var pipClass = p < usados ? 'pip pip-usado' : 'pip pip-livre';
                html += '<span class="' + pipClass + '"></span>';
            }
            html += '</div></div>';
            html += '</div>';
        }

        html += '</div></div>';
        return html;
    }

    calcularModificador(valor) { return Math.floor((valor - 10) / 2); }

    getBadgeClass(tipo) {
        var mapa = { jogador: 'badge-jogador', monstro: 'badge-monstro', npc: 'badge-npc' };
        return mapa[tipo] || 'badge-default';
    }

    getEmojiTipo(tipo) {
        var mapa = { jogador: '🧙', monstro: '👹', npc: '🤝' };
        return mapa[tipo] || '⚔️';
    }

    resetarCombate() {
        if (!confirm('Deseja resetar o combate? Todos voltarao ao HP maximo.')) return;
        var self = this;
        this.combatentes.forEach(function(c) {
            c.hp_atual = c.hp_maximo;
            self.combatenteService.atualizarHP(c.id, c.hp_maximo).catch(console.error);
        });
        this.turnoAtual    = 0;
        this.rodadaAtual   = 1;
        this.statsVisiveis = false;
        this._jaAgiram     = [];
        this._resetarCronometro();
        this._iniciarCronometro();
        this.atualizarRodada();
        Toast.success('Combate resetado!');
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    finalizarCombate() {
        if (!confirm('Deseja finalizar o combate e voltar para a configuracao?')) return;
        this._pararCronometro();
        var telaArena        = document.getElementById('telaArena');
        var telaConfiguracao = document.getElementById('telaConfiguracao');
        if (telaArena)        telaArena.classList.remove('ativa');
        if (telaConfiguracao) telaConfiguracao.classList.add('ativa');
        Toast.success('Combate finalizado!');
    }
}