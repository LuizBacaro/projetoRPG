import { CombatenteService  } from '../services/CombatenteService.js';
import { CondicaoController } from './CondicaoController.js';
import { Toast              } from '../ui/Toast.js';

export class ArenaController {

    constructor() {
        this.combatenteService  = new CombatenteService();
        this.condicaoController = new CondicaoController();
        this.combatentes        = [];
        this.turnoAtual         = 0;
        this.rodadaAtual        = 1;
        this.statsVisiveis      = false;
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
        if (!combatentes || !Array.isArray(combatentes) || !combatentes.length) {
            Toast.error('Nenhum combatente valido');
            return;
        }
        this.combatentes = combatentes.sort(function(a, b) {
            return b.iniciativa - a.iniciativa;
        });
        this.turnoAtual    = 0;
        this.rodadaAtual   = 1;
        this.statsVisiveis = false;
        this.atualizarRodada();
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    avancarTurno() {
        this.turnoAtual++;
        if (this.turnoAtual >= this.combatentes.length) {
            this.turnoAtual = 0;
            this.rodadaAtual++;
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

    renderizarOrdemIniciativa() {
        var container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;
        var self = this;
        var html = '';
        for (var i = 0; i &lt; this.combatentes.length; i++) {
            var c     = this.combatentes[i];
            var ativo = (i === this.turnoAtual);
            var hpPct = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
            var hpCor = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');
            var morto = (c.hp_atual &lt;= 0);
            var cls   = 'combatente-ordem-item' + (ativo ? ' ativo' : '') + (morto ? ' morto' : '');
            html += '<div class="' + cls + '" data-combatente-id="' + c.id + '">';
            html += '<span class="ordem-iniciativa-valor">' + c.iniciativa + '</span>';
            html += '<div class="ordem-info">';
            html += '<span class="ordem-nome">' + c.nome + '</span>';
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
            var c = self.combatentes[i++];
            var cardEl = document.querySelector('.combatente-ordem-item[data-combatente-id="' + c.id + '"]');
            if (cardEl) {
                self.condicaoController.atualizarBadgesOrdem(cardEl, c.id).then(next);
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
        if (c.foto_url) {
            container.innerHTML = '<img src="' + c.foto_url + '" alt="' + c.nome + '" style="width:100%;height:100%;object-fit:cover;">';
        } else {
            container.innerHTML = '<div class="arena-foto-vertical-placeholder">' + this.getEmojiTipo(c.tipo) + '</div>';
        }
    }

    renderizarCombatenteAtivo() {
        var container = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        var c = this.combatentes[this.turnoAtual];
        if (!c) return;

        this.renderizarFotoAtivo();

        var hpPct  = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
        var hpCor  = hpPct > 50 ? '#4CAF50' : (hpPct > 25 ? '#FF9800' : '#F44336');

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
        for (var j = 0; j &lt; atribs.length; j++) {
            atributosHTML += '<div class="arena-atributo-box">';
            atributosHTML += '<span class="arena-atributo-nome">' + atribs[j][0] + '</span>';
            atributosHTML += '<span class="arena-atributo-valor">' + atribs[j][1] + '</span>';
            atributosHTML += '<span class="arena-atributo-mod">' + mod(atribs[j][1]) + '</span>';
            atributosHTML += '</div>';
        }

        var fotoTopo = c.foto_url
            ? '<img src="' + c.foto_url + '" alt="' + c.nome + '">'
            : '<div class="arena-foto-placeholder">' + this.getEmojiTipo(c.tipo) + '</div>';

        var html = '';
        html += '<div class="arena-card">';
        html += '<div class="arena-topo">';
        html += '<div class="arena-foto-nome">';
        html += '<div class="arena-foto">' + fotoTopo + '</div>';
        html += '<div class="arena-nome-info">';
        html += '<h2 class="arena-nome">' + c.nome + ' (' + nivel + ' nivel)</h2>';
        html += '<span class="arena-classe">' + classe;
        html += '<span class="badge ' + this.getBadgeClass(c.tipo) + '">' + c.tipo + '</span>';
        html += '</span></div></div>';
        html += '<div class="arena-topo-acoes">';
        html += '<button class="btn-toggle-stats" onclick="window._toggleStats()">' + olhoTxt + '</button>';
        html += '<button class="btn-encerrar-combate" onclick="window._finalizarCombate()">Encerrar combate</button>';
        html += '</div></div>';

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

        html += '<div class="arena-linha-inferior">';
        html += '<div id="arenaAtaquesContainer"></div>';
        html += '<div id="arenaMagiasContainer"></div>';
        html += '<div class="arena-secao arena-futuro-secao"><div class="arena-futuro-placeholder">Quadro para futuro uso</div></div>';
        html += '</div>';
        html += '</div>';

        container.innerHTML = html;

        var self = this;
        window._abrirDanoCura    = function() { if (window.modalDanoCuraInstance) window.modalDanoCuraInstance.abrir(self.combatentes); };
        window._abrirCondicao    = function() { if (window.modalCondicaoInstance) window.modalCondicaoInstance.abrir(); else console.error('modalCondicaoInstance nao inicializado'); };
        window._toggleStats      = function() { self.toggleVisibilidadeStats(); };
        window._avancarTurno     = function() { self.avancarTurno(); };
        window._finalizarCombate = function() { self.finalizarCombate(); };

        this.condicaoController.carregarCondicoesDoCombatente(c.id);

        document.dispatchEvent(new CustomEvent('combatenteAtivoMudou', {
            detail: { combatente: c }
        }));
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
        this.atualizarRodada();
        Toast.success('Combate resetado!');
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    finalizarCombate() {
        if (!confirm('Deseja finalizar o combate e voltar para a configuracao?')) return;
        var telaArena        = document.getElementById('telaArena');
        var telaConfiguracao = document.getElementById('telaConfiguracao');
        if (telaArena)        telaArena.classList.remove('ativa');
        if (telaConfiguracao) telaConfiguracao.classList.add('ativa');
        Toast.success('Combate finalizado!');
    }
}