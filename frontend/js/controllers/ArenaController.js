/**
 * ArenaController
 * SRP: gerencia apenas a tela de arena (turno, renderizacao, combate)
 * DIP: depende de CombatenteService e CondicaoController
 *
 * REGRA: usa concatenacao de strings em vez de template literals
 * para evitar corrupcao pelo editor web do GitHub
 *
 * Dispara 'combatenteAtivoMudou' — main.js delega para ArenaAtaquesMagias
 */
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

    // ── Init ──────────────────────────────────────────────────────────────

    async _inicializar() {
        this.condicaoController.init();
        this._configurarEventos();
    }

    _configurarEventos() {
        document.addEventListener('iniciarCombate', (e) => {
            if (e.detail && e.detail.combatentes) {
                this.iniciarCombate(e.detail.combatentes);
            } else {
                Toast.error('Erro: Dados de combatentes invalidos');
            }
        });
    }

    // ── Combate ───────────────────────────────────────────────────────────

    iniciarCombate(combatentes) {
        if (!combatentes || !Array.isArray(combatentes) || !combatentes.length) {
            Toast.error('Erro: Nenhum combatente valido para iniciar combate');
            return;
        }
        this.combatentes   = combatentes.sort(function(a, b) { return b.iniciativa - a.iniciativa; });
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
        const el = document.getElementById('rodadaAtual');
        if (el) el.textContent = this.rodadaAtual;
    }

    atualizarInterface() {
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    // ── Ordem de Iniciativa ───────────────────────────────────────────────

    renderizarOrdemIniciativa() {
        const container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;

        const self = this;
        container.innerHTML = this.combatentes.map(function(c, index) {
            const ativo        = index === self.turnoAtual;
            const hpPercentual = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
            const hpCor        = hpPercentual > 50 ? '#4CAF50' : hpPercentual > 25 ? '#FF9800' : '#F44336';
            const morto        = c.hp_atual <= 0;
            return (
                '<div class="combatente-ordem-item ' + (ativo ? 'ativo' : '') + ' ' + (morto ? 'morto' : '') + '"' +
                     ' data-combatente-id="' + c.id + '">' +
                    '<span class="ordem-iniciativa-valor">' + c.iniciativa + '</span>' +
                    '<div class="ordem-info">' +
                        '<span class="ordem-nome">' + c.nome + '</span>' +
                        '<div class="ordem-hp-bar">' +
                            '<div class="ordem-hp-fill" style="width:' + hpPercentual + '%;background:' + hpCor + ';"></div>' +
                        '</div>' +
                        '<div class="badges-condicao-ordem-wrapper"></div>' +
                    '</div>' +
                    '<span class="badge ' + self.getBadgeClass(c.tipo) + ' badge-mini">' + self.getEmojiTipo(c.tipo) + '</span>' +
                '</div>'
            );
        }).join('');

        this.renderizarFotoAtivo();
        this._atualizarBadgesOrdemTodos();
    }

    async _atualizarBadgesOrdemTodos() {
        for (const c of this.combatentes) {
            const cardEl = document.querySelector('.combatente-ordem-item[data-combatente-id="' + c.id + '"]');
            if (cardEl) await this.condicaoController.atualizarBadgesOrdem(cardEl, c.id);
        }
    }

    // ── Foto Ativo ────────────────────────────────────────────────────────

    renderizarFotoAtivo() {
        const container  = document.getElementById('arenaFotoAtivo');
        if (!container) return;
        const combatente = this.combatentes[this.turnoAtual];
        if (!combatente) { container.innerHTML = ''; return; }
        container.innerHTML = combatente.foto_url
            ? '<img src="' + combatente.foto_url + '" alt="' + combatente.nome + '" style="width:100%;height:100%;object-fit:cover;">'
            : '<div class="arena-foto-vertical-placeholder">' + this.getEmojiTipo(combatente.tipo) + '</div>';
    }

    // ── Combatente Ativo ──────────────────────────────────────────────────
    //
    // Injeta containers vazios para ataques e magias
    // e dispara 'combatenteAtivoMudou' — main.js delega para ArenaAtaquesMagias
    // OCP: ArenaController nao conhece ArenaAtaquesMagias diretamente

    renderizarCombatenteAtivo() {
        const container  = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        const combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        this.renderizarFotoAtivo();

        const hpPercentual = Math.min(100, (combatente.hp_atual / combatente.hp_maximo) * 100);
        const hpCor        = hpPercentual > 50 ? '#4CAF50' : hpPercentual > 25 ? '#FF9800' : '#F44336';

        // Valores com fallback seguro — sem ?? para evitar corrupcao
        const ca       = combatente.ca        !== null && combatente.ca        !== undefined ? combatente.ca        : 10;
        const toque    = combatente.toque     !== null && combatente.toque     !== undefined ? combatente.toque     : 10;
        const surpresa = combatente.surpresa  !== null && combatente.surpresa  !== undefined ? combatente.surpresa  : 10;
        const fort     = combatente.fortitude !== null && combatente.fortitude !== undefined ? combatente.fortitude : 0;
        const reflex   = combatente.reflexos  !== null && combatente.reflexos  !== undefined ? combatente.reflexos  : 0;
        const vont     = combatente.vontade   !== null && combatente.vontade   !== undefined ? combatente.vontade   : 0;
        const nivel    = combatente.nivel  || 1;
        const classe   = combatente.classe || 'Aventureiro';

        const mod   = function(val) { const m = Math.floor(((val || 10) - 10) / 2); return m >= 0 ? '+' + m : '' + m; };
        const sinal = function(val) { return val >= 0 ? '+' + val : '' + val; };

        const olhoIcon  = this.statsVisiveis ? '👁️' : '🙈';
        const olhoTitle = this.statsVisiveis ? 'Ocultar stats' : 'Mostrar stats';

        const pvValor  = this.statsVisiveis ? combatente.hp_atual + '/' + combatente.hp_maximo : '???/???';
        const pvClasse = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        const caValor  = this.statsVisiveis ? ca       : '?';
        const caClasse = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        const sValor   = this.statsVisiveis ? surpresa : '?';
        const sClasse  = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        const tValor   = this.statsVisiveis ? toque    : '?';
        const tClasse  = this.statsVisiveis ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';

        const self = this;
        const atributosHTML = [
            ['For', combatente.forca        || 10],
            ['Des', combatente.destreza     || 10],
            ['Con', combatente.constituicao || 10],
            ['Int', combatente.inteligencia || 10],
            ['Sab', combatente.sabedoria    || 10],
            ['Car', combatente.carisma      || 10]
        ].map(function(item) {
            return (
                '<div class="arena-atributo-box">' +
                    '<span class="arena-atributo-nome">' + item[0] + '</span>' +
                    '<span class="arena-atributo-valor">' + item[1] + '</span>' +
                    '<span class="arena-atributo-mod">' + mod(item[1]) + '</span>' +
                '</div>'
            );
        }).join('');

        const fotoTopo = combatente.foto_url
            ? '<img src="' + combatente.foto_url + '" alt="' + combatente.nome + '">'
            : '<div class="arena-foto-placeholder">' + this.getEmojiTipo(combatente.tipo) + '</div>';

        container.innerHTML =
            '<div class="arena-card">' +

                '<div class="arena-topo">' +
                    '<div class="arena-foto-nome">' +
                        '<div class="arena-foto">' + fotoTopo + '</div>' +
                        '<div class="arena-nome-info">' +
                            '<h2 class="arena-nome">' + combatente.nome + ' (' + nivel + ' nivel)</h2>' +
                            '<span class="arena-classe">' + classe +
                                '<span class="badge ' + this.getBadgeClass(combatente.tipo) + '">' + combatente.tipo + '</span>' +
                            '</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-topo-acoes">' +
                        '<button class="btn-toggle-stats" onclick="window._toggleStats()" title="' + olhoTitle + '">' +
                            olhoIcon + ' ' + (this.statsVisiveis ? 'Ocultar' : 'Revelar') + ' Stats' +
                        '</button>' +
                        '<button class="btn-encerrar-combate" onclick="window._finalizarCombate()" title="Encerrar combate">' +
                            'Encerrar combate' +
                        '</button>' +
                    '</div>' +
                '</div>' +

                '<div class="arena-stats-linha">' +
                    '<div class="arena-stat-box arena-stat-pv">' +
                        '<span class="arena-stat-label">PV</span>' +
                        '<span class="' + pvClasse + '">' + pvValor + '</span>' +
                        '<div class="arena-hp-bar">' +
                            '<div class="arena-hp-fill" style="width:' + hpPercentual + '%;background:' + hpCor + ';"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-ca">' +
                        '<span class="arena-stat-label">CA</span>' +
                        '<span class="' + caClasse + '">' + caValor + '</span>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-surpresa">' +
                        '<span class="arena-stat-label">Surpresa</span>' +
                        '<span class="' + sClasse + '">' + sValor + '</span>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-toque">' +
                        '<span class="arena-stat-label">Toque</span>' +
                        '<span class="' + tClasse + '">' + tValor + '</span>' +
                    '</div>' +
                '</div>' +

                '<div class="arena-grade-central">' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Atributos</h3>' +
                        '<div class="arena-atributos-grid">' + atributosHTML + '</div>' +
                    '</div>' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Resistencias</h3>' +
                        '<div class="arena-resistencias-lista">' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Fortitude</span><span class="arena-resistencia-valor">' + sinal(fort)  + '</span></div>' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Reflexos</span><span class="arena-resistencia-valor">'  + sinal(reflex) + '</span></div>' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Vontade</span><span class="arena-resistencia-valor">'   + sinal(vont)   + '</span></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Condicoes</h3>' +
                        '<div class="arena-condicoes-lista">' +
                            '<span class="arena-condicao-vazia">Nenhuma condicao ativa</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-secao arena-acoes-col">' +
                        '<h3 class="arena-secao-titulo">Aplicar</h3>' +
                        '<button class="arena-btn-dano-cura" onclick="window._abrirDanoCura()">Dano / Cura</button>' +
                        '<button class="arena-btn-condicao"  onclick="window._abrirCondicao()">Condicao</button>' +
                        '<button class="arena-btn-proximo"   onclick="window._avancarTurno()">Encerrar turno</button>' +
                    '</div>' +
                '</div>' +

                // Containers dinamicos — preenchidos pelo ArenaAtaquesMagias via evento
                '<div class="arena-linha-inferior">' +
                    '<div id="arenaAtaquesContainer"></div>' +
                    '<div id="arenaMagiasContainer"></div>' +
                    '<div class="arena-secao arena-futuro-secao">' +
                        '<div class="arena-futuro-placeholder">Quadro para futuro uso</div>' +
                    '</div>' +
                '</div>' +

            '</div>';

        // Funções globais dos botões
        window._abrirDanoCura    = function() { if (window.modalDanoCuraInstance) window.modalDanoCuraInstance.abrir(self.combatentes); };
        window._abrirCondicao    = function() { if (window.modalCondicaoInstance) window.modalCondicaoInstance.abrir(); else console.error('modalCondicaoInstance nao inicializado'); };
        window._toggleStats      = function() { self.toggleVisibilidadeStats(); };
        window._avancarTurno     = function() { self.avancarTurno(); };
        window._finalizarCombate = function() { self.finalizarCombate(); };

        this.condicaoController.carregarCondicoesDoCombatente(combatente.id);

        // Dispara evento — main.js escuta e delega para ArenaAtaquesMagias
        document.dispatchEvent(new CustomEvent('combatenteAtivoMudou', {
            detail: { combatente: combatente }
        }));
    }

    // ── Helpers ───────────────────────────────────────────────────────────

    calcularModificador(valor) { return Math.floor((valor - 10) / 2); }

    getBadgeClass(tipo) {
        const mapa = { jogador: 'badge-jogador', monstro: 'badge-monstro', npc: 'badge-npc' };
        return mapa[tipo] || 'badge-default';
    }

    getEmojiTipo(tipo) {
        const mapa = { jogador: '🧙', monstro: '👹', npc: '🤝' };
        return mapa[tipo] || '⚔️';
    }

    // ── Ações de combate ──────────────────────────────────────────────────

    resetarCombate() {
        if (!confirm('Deseja resetar o combate? Todos os combatentes voltarao ao HP maximo.')) return;
        const self = this;
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
        const telaArena        = document.getElementById('telaArena');
        const telaConfiguracao = document.getElementById('telaConfiguracao');
        if (telaArena)        telaArena.classList.remove('ativa');
        if (telaConfiguracao) telaConfiguracao.classList.add('ativa');
        Toast.success('Combate finalizado!');
    }
}