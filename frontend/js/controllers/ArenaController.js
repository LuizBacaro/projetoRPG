/**
 * Controller da Arena de Combate
 * SOLID: SRP - Gerencia apenas a tela de arena
 *        DIP - Depende das abstrações CondicaoController e CombatenteService
 */
import { CombatenteService }  from '../services/CombatenteService.js';
import { CondicaoController } from './CondicaoController.js';
import { Toast }              from '../ui/Toast.js';

export class ArenaController {
    constructor() {
        this.combatenteService  = new CombatenteService();
        this.condicaoController = new CondicaoController();
        this.combatentes        = [];
        this.turnoAtual         = 0;
        this.rodadaAtual        = 1;
        this.hpVisivel          = false;
        this.caVisivel          = false;
        this._inicializar();
    }

    async _inicializar() {
        await this.condicaoController.init();
        this.configurarEventos();
    }

    configurarEventos() {
        document.addEventListener('iniciarCombate', (e) => {
            if (e.detail && e.detail.combatentes) {
                this.iniciarCombate(e.detail.combatentes);
            } else {
                Toast.error('Erro: Dados de combatentes inválidos');
            }
        });

        const btnAvancar   = document.getElementById('btnAvancarTurno');
        if (btnAvancar)   btnAvancar.addEventListener('click',   () => this.avancarTurno());

        const btnResetar   = document.getElementById('btnResetarCombate');
        if (btnResetar)   btnResetar.addEventListener('click',   () => this.resetarCombate());

        const btnFinalizar = document.getElementById('btnFinalizarCombate');
        if (btnFinalizar) btnFinalizar.addEventListener('click', () => this.finalizarCombate());
    }

    // ── Combate ───────────────────────────────────────────────────────────────

    iniciarCombate(combatentes) {
        if (!combatentes || !Array.isArray(combatentes) || combatentes.length === 0) {
            Toast.error('Erro: Nenhum combatente válido para iniciar combate');
            return;
        }
        this.combatentes = combatentes.sort((a, b) => b.iniciativa - a.iniciativa);
        this.turnoAtual  = 0;
        this.rodadaAtual = 1;
        this.hpVisivel   = false;
        this.caVisivel   = false;
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
            Toast.success('🎯 Rodada ' + this.rodadaAtual + ' iniciada!');
        }
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    toggleVisibilidadeHP() {
        this.hpVisivel = !this.hpVisivel;
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
        Toast.success(this.hpVisivel ? '👁️ HP Visível' : '🙈 HP Oculto');
    }

    toggleVisibilidadeCA() {
        this.caVisivel = !this.caVisivel;
        this.renderizarCombatenteAtivo();
        Toast.success(this.caVisivel ? '👁️ CA Visível' : '🙈 CA Oculto');
    }

    atualizarRodada() {
        const el = document.getElementById('rodadaAtual');
        if (el) el.textContent = this.rodadaAtual;
    }

    // ── Render: Ordem de Iniciativa ───────────────────────────────────────────

    renderizarOrdemIniciativa() {
        const container = document.getElementById('ordemIniciativaContainer');
        if (!container) return;

        container.innerHTML = this.combatentes.map((c, index) => {
            const ativo        = index === this.turnoAtual;
            const hpPercentual = Math.min(100, (c.hp_atual / c.hp_maximo) * 100);
            const hpCor        = hpPercentual > 50 ? '#4CAF50' : hpPercentual > 25 ? '#FF9800' : '#F44336';
            const morto        = c.hp_atual <= 0;

            return '<div class="combatente-ordem-item ' + (ativo ? 'ativo' : '') + ' ' + (morto ? 'morto' : '') + '" ' +
                        'data-combatente-id="' + c.id + '">' +
                '<span class="ordem-iniciativa-valor">' + c.iniciativa + '</span>' +
                '<div class="ordem-info">' +
                    '<span class="ordem-nome">' + c.nome + '</span>' +
                    '<div class="ordem-hp-bar">' +
                        '<div class="ordem-hp-fill" style="width:' + hpPercentual + '%;background:' + hpCor + ';"></div>' +
                    '</div>' +
                    '<div class="badges-condicao-ordem-wrapper"></div>' +
                '</div>' +
                '<span class="badge ' + this.getBadgeClass(c.tipo) + ' badge-mini">' + this.getEmojiTipo(c.tipo) + '</span>' +
            '</div>';
        }).join('');

        this.renderizarFotoAtivo();
        this._atualizarBadgesOrdemTodos();
    }

    async _atualizarBadgesOrdemTodos() {
        for (const c of this.combatentes) {
            const cardEl = document.querySelector(
                '.combatente-ordem-item[data-combatente-id="' + c.id + '"]'
            );
            if (cardEl) {
                await this.condicaoController.atualizarBadgesOrdem(cardEl, c.id);
            }
        }
    }

    // ── Render: Foto Ativo ────────────────────────────────────────────────────

    renderizarFotoAtivo() {
        const container  = document.getElementById('arenaFotoAtivo');
        if (!container) return;

        const combatente = this.combatentes[this.turnoAtual];
        if (!combatente) { container.innerHTML = ''; return; }

        container.innerHTML = combatente.foto_url
            ? '<img src="' + combatente.foto_url + '" alt="' + combatente.nome + '" style="width:100%;height:100%;object-fit:cover;">'
            : '<div class="arena-foto-vertical-placeholder">' + this.getEmojiTipo(combatente.tipo) + '</div>';
    }

    // ── Render: Combatente Ativo ──────────────────────────────────────────────

    renderizarCombatenteAtivo() {
        const container  = document.getElementById('combatenteAtivoContainer');
        if (!container) return;

        const combatente = this.combatentes[this.turnoAtual];
        if (!combatente) return;

        this.renderizarFotoAtivo();

        const hpPercentual = Math.min(100, (combatente.hp_atual / combatente.hp_maximo) * 100);
        const hpCor        = hpPercentual > 50 ? '#4CAF50' : hpPercentual > 25 ? '#FF9800' : '#F44336';

        const ca       = combatente.ca        !== undefined ? combatente.ca        : 10;
        const toque    = combatente.toque     !== undefined ? combatente.toque     : 10;
        const surpresa = combatente.surpresa  !== undefined ? combatente.surpresa  : 10;
        const fort     = combatente.fortitude !== undefined ? combatente.fortitude : 0;
        const reflex   = combatente.reflexos  !== undefined ? combatente.reflexos  : 0;
        const vont     = combatente.vontade   !== undefined ? combatente.vontade   : 0;
        const nivel    = combatente.nivel     || 1;
        const classe   = combatente.classe    || 'Aventureiro';

        const mod   = (val) => { const m = Math.floor(((val || 10) - 10) / 2); return m >= 0 ? '+' + m : '' + m; };
        const sinal = (val) => val >= 0 ? '+' + val : '' + val;

        const caValor  = this.caVisivel ? ca    : '?';
        const caClasse = this.caVisivel ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        const caOlho   = this.caVisivel ? '👁️' : '🙈';
        const pvValor  = this.hpVisivel ? (combatente.hp_atual + '/' + combatente.hp_maximo) : '???/???';
        const pvClasse = this.hpVisivel ? 'arena-stat-valor' : 'arena-stat-valor hp-oculto';
        const pvOlho   = this.hpVisivel ? '👁️' : '🙈';

        const atributosHTML = [
            ['For', combatente.forca        || 10],
            ['Des', combatente.destreza     || 10],
            ['Con', combatente.constituicao || 10],
            ['Int', combatente.inteligencia || 10],
            ['Sab', combatente.sabedoria    || 10],
            ['Car', combatente.carisma      || 10]
        ].map(([nome, val]) =>
            '<div class="arena-atributo-box">' +
                '<span class="arena-atributo-nome">'  + nome     + '</span>' +
                '<span class="arena-atributo-valor">' + val      + '</span>' +
                '<span class="arena-atributo-mod">'   + mod(val) + '</span>' +
            '</div>'
        ).join('');

        const magiasHTML = [0,1,2,3,4,5,6,7,8,9].map(n =>
            '<div class="arena-magia-linha">' +
                '<span class="arena-magia-nivel">NÍV ' + n + '</span>' +
                '<div class="arena-magia-controle">' +
                    '<button class="arena-magia-btn">−</button>' +
                    '<span class="arena-magia-valor">0</span>' +
                    '<button class="arena-magia-btn">+</button>' +
                '</div>' +
                '<span class="arena-magia-usados">0</span>' +
            '</div>'
        ).join('');

        const fotoTopo = combatente.foto_url
            ? '<img src="' + combatente.foto_url + '" alt="' + combatente.nome + '">'
            : '<div class="arena-foto-placeholder">' + this.getEmojiTipo(combatente.tipo) + '</div>';

        container.innerHTML =
            '<div class="arena-card">' +
                '<div class="arena-topo">' +
                    '<div class="arena-foto-nome">' +
                        '<div class="arena-foto">' + fotoTopo + '</div>' +
                        '<div class="arena-nome-info">' +
                            '<h2 class="arena-nome">' + combatente.nome + ' (' + nivel + '° nível)</h2>' +
                            '<span class="arena-classe">' + classe +
                                ' <span class="badge ' + this.getBadgeClass(combatente.tipo) + '">' + combatente.tipo + '</span>' +
                            '</span>' +
                        '</div>' +
                    '</div>' +
                    '<button class="btn-encerrar-combate" onclick="document.getElementById(\'btnFinalizarCombate\').click()">✖ Encerrar combate</button>' +
                '</div>' +

                '<div class="arena-stats-linha">' +
                    '<div class="arena-stat-box arena-stat-ca">' +
                        '<span class="arena-stat-label">CA</span>' +
                        '<button class="arena-hp-toggle" onclick="window._toggleCA()" title="Mostrar/Ocultar CA">' + caOlho + '</button>' +
                        '<span class="' + caClasse + '">' + caValor + '</span>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-pv">' +
                        '<span class="arena-stat-label">PV</span>' +
                        '<button class="arena-hp-toggle" onclick="window._toggleHP()" title="Mostrar/Ocultar HP">' + pvOlho + '</button>' +
                        '<span class="' + pvClasse + '">' + pvValor + '</span>' +
                        '<div class="arena-hp-bar"><div class="arena-hp-fill" style="width:' + hpPercentual + '%;background:' + hpCor + ';"></div></div>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-surpresa">' +
                        '<span class="arena-stat-label">S</span>' +
                        '<span class="arena-stat-valor">' + surpresa + '</span>' +
                    '</div>' +
                    '<div class="arena-stat-box arena-stat-toque">' +
                        '<span class="arena-stat-label">T</span>' +
                        '<span class="arena-stat-valor">' + toque + '</span>' +
                    '</div>' +
                '</div>' +

                '<div class="arena-grade-central">' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Atributos</h3>' +
                        '<div class="arena-atributos-grid">' + atributosHTML + '</div>' +
                    '</div>' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Resistências</h3>' +
                        '<div class="arena-resistencias-lista">' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Fortitude</span><span class="arena-resistencia-valor">' + sinal(fort)   + '</span></div>' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Reflexos</span><span class="arena-resistencia-valor">'   + sinal(reflex) + '</span></div>' +
                            '<div class="arena-resistencia-item"><span class="arena-resistencia-nome">Vontade</span><span class="arena-resistencia-valor">'    + sinal(vont)   + '</span></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Condições</h3>' +
                        '<div class="arena-condicoes-lista">' +
                            '<span class="arena-condicao-vazia">Nenhuma condição ativa</span>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-secao arena-acoes-col">' +
                        '<h3 class="arena-secao-titulo">Aplicar</h3>' +
                        '<button class="arena-btn-dano-cura" onclick="window._abrirDanoCura()">⚔️ Dano / Cura</button>' +
                        '<button class="arena-btn-condicao" data-acao="condicao" data-combatente-id="' + combatente.id + '">🔮 Condição</button>' +
                        '<button class="arena-btn-proximo" onclick="window._avancarTurno()">✅ Encerrar turno</button>' +
                    '</div>' +
                '</div>' +

                '<div class="arena-linha-inferior">' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Ataques</h3>' +
                        '<div class="arena-ataques-lista">' +
                            '<div class="arena-ataque-header"><span>Nome</span><span>Ataque</span><span>Dano</span></div>' +
                            '<div class="arena-ataque-item arena-ataque-placeholder"><span>— Ataques serão exibidos aqui —</span></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="arena-secao">' +
                        '<h3 class="arena-secao-titulo">Controle de magias</h3>' +
                        '<div class="arena-magias-grid">' + magiasHTML + '</div>' +
                    '</div>' +
                    '<div class="arena-secao arena-futuro-secao">' +
                        '<div class="arena-futuro-placeholder">Quadro para futuro uso de outras informações</div>' +
                    '</div>' +
                '</div>' +
            '</div>';

        window._abrirDanoCura = () => {
            if (typeof modalDanoCuraInstance !== 'undefined') {
                modalDanoCuraInstance.abrir(this.combatentes);
            }
        };
        window._avancarTurno = () => this.avancarTurno();
        window._toggleHP     = () => this.toggleVisibilidadeHP();
        window._toggleCA     = () => this.toggleVisibilidadeCA();

        this.condicaoController.carregarCondicoesDoCombatente(combatente.id);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    calcularModificador(valor) { return Math.floor((valor - 10) / 2); }

    getCorHP(percentual) {
        if (percentual > 50) return 'linear-gradient(90deg, #32CD32 0%, #228B22 100%)';
        if (percentual > 25) return 'linear-gradient(90deg, #FFA500 0%, #FF8C00 100%)';
        return 'linear-gradient(90deg, #DC143C 0%, #8B0000 100%)';
    }

    getBadgeClass(tipo) {
        return { jogador: 'badge-jogador', monstro: 'badge-monstro', npc: 'badge-npc' }[tipo] || 'badge-default';
    }

    getEmojiTipo(tipo) {
        return { jogador: '🧙', monstro: '👹', npc: '🤝' }[tipo] || '⚔️';
    }

    resetarCombate() {
        if (!confirm('⚠️ Deseja realmente resetar o combate?\n\nTodos os combatentes retornarão ao HP máximo.')) return;
        this.combatentes.forEach(c => {
            c.hp_atual = c.hp_maximo;
            this.combatenteService.atualizarHP(c.id, c.hp_maximo).catch(console.error);
        });
        this.turnoAtual  = 0;
        this.rodadaAtual = 1;
        this.hpVisivel   = false;
        this.caVisivel   = false;
        this.atualizarRodada();
        Toast.success('Combate resetado! 🔄');
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    atualizarInterface() {
        this.renderizarOrdemIniciativa();
        this.renderizarCombatenteAtivo();
    }

    finalizarCombate() {
        if (!confirm('⚠️ Deseja finalizar o combate e voltar para a configuração?')) return;
        document.getElementById('telaArena').classList.remove('ativa');
        document.getElementById('telaConfiguracao').classList.add('ativa');
        Toast.success('Combate finalizado! 🏁');
    }
}