/**
 * Arena D&D 5e — layout e fluxo alinhados ao dnd35.
 */
import { CombatenteCard } from '/games/dnd35/js/ui/CombatenteCard.js';
import { Dnd5eCombatenteAtivoView } from '../ui/Dnd5eCombatenteAtivoView.js';
import { Dnd5eCondicaoModal } from '../ui/Dnd5eCondicaoModal.js';
import {
    Dnd5eArenaMagiasHelper,
    MODO_CONJURADOR,
} from '../arena/Dnd5eArenaMagiasHelper.js';
import { Dnd5eArenaMagiasView } from '../ui/Dnd5eArenaMagiasView.js';
import { Dnd5eArenaConjuracaoModal } from '../ui/Dnd5eArenaConjuracaoModal.js';
import {
    magiaPrecisaAlvo,
    montarPayloadConjurar,
    modAtributo,
} from '../arena/Dnd5eArenaConjuracaoHelper.js';
import { parseBonusAtaque, parseDanoFicha } from '../arena/Dnd5eArenaAtaquesHelper.js';
import { Dnd5eGrimorioService } from '../services/Dnd5eGrimorioService.js';
import { Dnd5eConjuracaoFichaService } from '../services/Dnd5eConjuracaoFichaService.js';

const ps = new Dnd5ePersonagemService();
const cs = new Dnd5eCombateService();
const rs = new Dnd5eRegrasService();
const CU = Dnd5eCondicoesUtil;
const DURACAO_PERMANENTE = CU.DURACAO_PERMANENTE;

class Dnd5eArenaController {
    constructor() {
        this.personagensDisponiveis = [];
        this.combatentes = [];
        this.selecionados = new Set();
        this.filtroTipo = 'todos';
        this.turnoAtual = 0;
        this.rodadaAtual = 1;
        this.combateAtivo = false;
        this.catalogoCondicoes = [];
        this.catalogoClasses = [];
        this.uidManual = 0;
        this.modalCondicao = null;
        this.grimorioService = new Dnd5eGrimorioService();
        this.conjuracaoFichaService = new Dnd5eConjuracaoFichaService();
        this.ehMestre = false;
        this._init();
    }

    static ehMestreUsuario() {
        return typeof AuthService.isMestre === 'function' && AuthService.isMestre();
    }

    el(id) {
        return document.getElementById(id);
    }

    async _init() {
        AuthService.configurarHeaderUsuario?.();
        const nomeEl = this.el('nomeUsuarioArena');
        if (nomeEl && AuthService.getNome) nomeEl.textContent = AuthService.getNome();

        this.el('btnTrocarJogoArena')?.addEventListener('click', () => {
            window.location.href = '/pages/selecionar-jogo.html';
        });
        this.el('btnLogoutArena')?.addEventListener('click', () => {
            AuthService.logout?.();
        });

        document.querySelectorAll('.filter-btn').forEach((btn) => {
            btn.addEventListener('click', async () => {
                document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
                this.filtroTipo = btn.dataset.tipo || 'todos';
                await this.carregarPersonagens();
            });
        });

        this.el('btnRecarregarPersonagens')?.addEventListener('click', () => this.carregarPersonagens());
        this.el('btnAddManual')?.addEventListener('click', () => this.addManual());
        this.el('btnIniciarCombate')?.addEventListener('click', () => this.iniciarCombate());
        this.el('btnEncerrarCombate')?.addEventListener('click', () => this.encerrarCombate());
        this.el('btnAbrirModalDanoCura')?.addEventListener('click', () => this.abrirModalDanoCura());
        this.el('btnAbrirModalCondicao')?.addEventListener('click', () =>
            this.modalCondicao?.abrir(this.combatenteAtual()?.id)
        );
        this.el('btnSyncPv')?.addEventListener('click', () => this.syncFichasArena());
        this.el('btnFecharModalDanoCuraTopo')?.addEventListener('click', () => this.fecharModalDanoCura());
        this.el('btnCancelarModalDanoCura')?.addEventListener('click', () => this.fecharModalDanoCura());
        this.el('btnAplicarModalDanoCura')?.addEventListener('click', () => this.aplicarModalDanoCura());
        this.el('btnAtaque')?.addEventListener('click', () => this.testarAtaque());
        this.el('btnDano')?.addEventListener('click', () => this.rolarDano());
        this.el('toolAlvoDano')?.addEventListener('change', () => this.sincronizarToolAcComAlvo());

        const danoInp = this.el('inputDanoModal');
        const curaInp = this.el('inputCuraModal');
        danoInp?.addEventListener('input', () => {
            if (parseInt(danoInp.value, 10) > 0 && curaInp) curaInp.value = '0';
        });
        curaInp?.addEventListener('input', () => {
            if (parseInt(curaInp.value, 10) > 0 && danoInp) danoInp.value = '0';
        });

        try {
            const meta = await rs.combate();
            this.catalogoCondicoes = meta.condicoes || [];
        } catch {
            this.catalogoCondicoes = [];
        }
        try {
            const data = await rs.classes();
            this.catalogoClasses = data.classes || [];
        } catch {
            this.catalogoClasses = [];
        }

        this.modalCondicao = new Dnd5eCondicaoModal(this);
        this.modalConjuracao = new Dnd5eArenaConjuracaoModal(this);
        this.ehMestre = Dnd5eArenaController.ehMestreUsuario();
        this._configurarUiMestre();
        await this.carregarPersonagens();
    }

    _configurarUiMestre() {
        document.querySelectorAll('.filter-btn-mestre').forEach((btn) => {
            btn.hidden = !this.ehMestre;
        });
    }

    nomeClasse(slug) {
        const c = this.catalogoClasses.find((x) => x.slug === slug);
        return c ? c.nome : slug || '—';
    }

    mapPersonagem(p) {
        const f = p.ficha || {};
        const hpMax = Math.max(1, p.hp_max || 1);
        const hpAtual = p.hp_atual != null ? Math.min(hpMax, Math.max(0, p.hp_atual)) : hpMax;
        return {
            id: `p-${p.id}`,
            personagemId: p.id,
            nome: p.nome,
            tipo: p.tipo || 'jogador',
            classe: f.classe_slug || '',
            classe_label: this.nomeClasse(f.classe_slug),
            raca: f.raca_slug || '',
            nivel: p.nivel || 1,
            hp_maximo: hpMax,
            hp_atual: hpAtual,
            iniciativa: p.dexterity_mod ?? 0,
            foto_url: p.foto_url,
            ca: f.ca_total != null ? f.ca_total : 10 + (p.dexterity_mod || 0),
            dex_mod: p.dexterity_mod ?? 0,
            condicoes: CU.normalizarLista(f.arena_condicoes || []),
            death_failures: 0,
            death_successes: 0,
            status_vida: 'vivo',
            mod_medicina: this._modMedicinaDePersonagem(p, f),
            economia: {
                acao_usada: false,
                bonus_acao_usada: false,
                movimento_usado_metros: 0,
                reacao_usada: false,
                velocidade_metros: 9,
            },
            forca: p.strength,
            destreza: p.dexterity,
            constituicao: p.constitution,
            inteligencia: p.intelligence,
            sabedoria: p.wisdom,
            carisma: p.charisma,
            strength_mod: p.strength_mod ?? 0,
            dexterity_mod: p.dexterity_mod ?? 0,
            constitution_mod: p.constitution_mod ?? 0,
            intelligence_mod: p.intelligence_mod ?? 0,
            wisdom_mod: p.wisdom_mod ?? 0,
            charisma_mod: p.charisma_mod ?? 0,
            bonus_proficiencia: p.bonus_proficiencia ?? 2,
            magia_concentracao_id: null,
            salvamentos: this._salvamentosDePersonagem(p, f),
            ataques: Array.isArray(f.inventario?.ataques)
                ? f.inventario.ataques.map((a) => ({ ...a }))
                : [],
        };
    }

    _modMedicinaDePersonagem(p, f) {
        const pericias = f.pericias;
        if (Array.isArray(pericias)) {
            const med = pericias.find((x) => x.slug === 'medicina');
            if (med != null) return Number(med.bonus) || 0;
        }
        const profs = f.pericias_proficientes || [];
        const sabMod =
            p.wisdom_mod ?? Math.floor(((Number(p.wisdom) || 10) - 10) / 2);
        const profBonus = profs.includes('medicina') ? p.bonus_proficiencia ?? 2 : 0;
        return sabMod + profBonus;
    }

    _salvamentosDePersonagem(p, f) {
        const pericias = f.pericias_proficientes;
        if (!Array.isArray(pericias)) return [];
        const map = {
            strength: 'FOR',
            dexterity: 'DES',
            constitution: 'CON',
            intelligence: 'INT',
            wisdom: 'SAB',
            charisma: 'CAR',
        };
        const defs = [
            { slug: 'fortitude', key: 'constitution', label: 'Fortitude' },
            { slug: 'reflexos', key: 'dexterity', label: 'Reflexos' },
            { slug: 'vontade', key: 'wisdom', label: 'Vontade' },
        ];
        return defs.map((d) => {
            const mod = p[`${d.key}_mod`] ?? 0;
            return { slug: d.slug, tipo: d.slug, label: d.label, bonus: mod };
        });
    }

    async carregarPersonagens() {
        try {
            const params = {};
            if (this.ehMestre) {
                if (this.filtroTipo && this.filtroTipo !== 'todos') {
                    params.tipo = this.filtroTipo;
                }
            } else {
                params.meus = true;
            }
            this.personagensDisponiveis = await ps.listar(params);
            this.renderListaDisponiveis();
        } catch (e) {
            Toast.error(e.message || 'Erro ao carregar personagens');
        }
    }

    renderListaDisponiveis() {
        const container = this.el('listaCombatentes');
        if (!container) return;
        container.innerHTML = '';
        const lista = this.personagensDisponiveis.filter((p) => {
            if (this.filtroTipo === 'todos') return true;
            return (p.tipo || 'jogador') === this.filtroTipo;
        });
        if (!lista.length) {
            container.innerHTML =
                '<p class="empty-state" style="padding:1rem">Nenhum personagem neste filtro.</p>';
            return;
        }
        lista.forEach((p) => {
            const cardData = this.mapPersonagem(p);
            const selecionado = this.selecionados.has(cardData.id);
            const card = CombatenteCard.render(cardData, selecionado, (id) =>
                this.toggleSelecionado(id)
            );
            container.appendChild(card);
        });
    }

    toggleSelecionado(id) {
        if (this.selecionados.has(id)) {
            this.selecionados.delete(id);
            this.combatentes = this.combatentes.filter((c) => c.id !== id);
        } else {
            const p = this.personagensDisponiveis.find((x) => `p-${x.id}` === id);
            if (p) {
                this.selecionados.add(id);
                this.combatentes.push(this.mapPersonagem(p));
            } else {
                const manual = this.combatentes.find((c) => c.id === id);
                if (manual) this.selecionados.add(id);
            }
        }
        this.renderSelecionados();
        this.renderListaDisponiveis();
    }

    renderSelecionados() {
        const container = this.el('combatentesSelecionados');
        const contador = this.el('contadorSelecionados');
        if (contador) contador.textContent = String(this.selecionados.size);
        if (!container) return;

        if (!this.selecionados.size) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>Nenhum combatente selecionado</p>
                    <small>Clique nos cards à esquerda para adicionar</small>
                </div>`;
            return;
        }

        container.innerHTML = '';
        this.combatentes
            .filter((c) => this.selecionados.has(c.id))
            .forEach((c) => {
                const card = CombatenteCard.renderSelecionado(
                    c,
                    (id) => this.toggleSelecionado(id),
                    () => {},
                    () => {}
                );
                container.appendChild(card);
            });
    }

    addManual() {
        const nome = prompt('Nome do combatente:');
        if (!nome?.trim()) return;
        let tipo = 'jogador';
        if (this.ehMestre) {
            const t = prompt('Tipo (jogador / monstro / npc):', 'monstro');
            if (t === null) return;
            const norm = (t || 'jogador').toLowerCase().trim();
            if (['jogador', 'monstro', 'npc'].includes(norm)) tipo = norm;
        }
        const dex = parseInt(prompt('Modificador de DES:', '0'), 10) || 0;
        const ac = parseInt(prompt('CA:', '12'), 10) || 12;
        const hp = parseInt(prompt('PV máx.:', '10'), 10) || 10;
        const id = `m-${++this.uidManual}`;
        const c = {
            id,
            personagemId: null,
            nome: nome.trim(),
            tipo,
            classe: '',
            classe_label: 'Manual',
            nivel: 1,
            hp_maximo: hp,
            hp_atual: hp,
            iniciativa: dex,
            foto_url: null,
            ca: ac,
            dex_mod: dex,
            condicoes: [],
            forca: 10,
            destreza: 10 + dex * 2,
            constituicao: 10,
            inteligencia: 10,
            sabedoria: 10,
            carisma: 10,
            salvamentos: [],
            death_failures: 0,
            death_successes: 0,
            status_vida: 'vivo',
            mod_medicina: 0,
            economia: {
                acao_usada: false,
                bonus_acao_usada: false,
                movimento_usado_metros: 0,
                reacao_usada: false,
                velocidade_metros: 9,
            },
            ataques: [],
        };
        this.combatentes.push(c);
        this.selecionados.add(id);
        this.renderSelecionados();
    }

    combatentePorId(id) {
        return this.combatentes.find((c) => c.id === id);
    }

    combatenteAtual() {
        if (!this.combateAtivo || !this.combatentes.length) return null;
        return this.combatentes[this.turnoAtual] || null;
    }

    async syncHpCondicoes(c) {
        if (!c) return;
        try {
            const res = await cs.sincronizarCondicoesHp(c.hp_atual, c.condicoes || []);
            c.condicoes = CU.normalizarLista(res.condicoes || []);
            await this.persistirCondicoesNaFicha(c, true);
        } catch (e) {
            Toast.error(e.message || 'Erro ao sincronizar condições');
        }
    }

    async persistirCondicoesNaFicha(c, silencioso) {
        if (!c.personagemId) return;
        try {
            await ps.atualizar(c.personagemId, {
                hp_atual: c.hp_atual,
                ficha: { arena_condicoes: c.condicoes || [] },
            });
            await this._persistirConcentracaoNaFicha(c, true);
            if (!silencioso) Toast.success(`Ficha de ${c.nome} atualizada.`);
        } catch (e) {
            Toast.error(`${c.nome}: ${e.message}`);
        }
    }

    async _persistirConcentracaoNaFicha(c, silencioso) {
        if (!c.personagemId || !this.conjuracaoFichaService) return;
        try {
            const estado = await this.conjuracaoFichaService.definirConcentracao(
                c.personagemId,
                c.magia_concentracao_id ?? null
            );
            c._conjEstado = estado;
            if (!silencioso) Toast.success(`Concentração de ${c.nome} salva na ficha.`);
        } catch (e) {
            if (!silencioso) Toast.error(`${c.nome}: ${e.message}`);
        }
    }

    async adicionarCondicao(id, slug, duracaoTurnos) {
        const c = this.combatentePorId(id);
        if (!c) return;
        const d =
            duracaoTurnos == null || duracaoTurnos === ''
                ? DURACAO_PERMANENTE
                : parseInt(duracaoTurnos, 10);
        const duracao = Number.isFinite(d) ? d : DURACAO_PERMANENTE;
        const lista = (c.condicoes || []).filter((x) => x.slug !== slug);
        lista.push({ slug, duracao_turnos: duracao });
        c.condicoes = lista.sort((a, b) => a.slug.localeCompare(b.slug));
        await this.syncHpCondicoes(c);
        this.atualizarUiCombate();
    }

    async iniciarCombate() {
        const ativos = this.combatentes.filter((c) => this.selecionados.has(c.id));
        if (!ativos.length) {
            Toast.error('Selecione ao menos um combatente.');
            return;
        }
        this.combatentes = ativos;
        try {
            const payload = this.combatentes.map((c) => ({
                id: c.id,
                nome: c.nome,
                dex_mod: c.dex_mod,
            }));
            const res = await cs.iniciativa(payload);
            const ordemMap = new Map(res.ordem.map((r) => [r.id, r]));
            this.combatentes.sort((a, b) => {
                const ra = ordemMap.get(a.id);
                const rb = ordemMap.get(b.id);
                const ia = ra?.iniciativa ?? 0;
                const ib = rb?.iniciativa ?? 0;
                if (ib !== ia) return ib - ia;
                const da = ra?.dex_mod ?? a.dex_mod ?? 0;
                const db = rb?.dex_mod ?? b.dex_mod ?? 0;
                if (db !== da) return db - da;
                return (a.nome || '').localeCompare(b.nome || '');
            });
            this.combatentes.forEach((c) => {
                const r = ordemMap.get(c.id);
                if (r) {
                    c.iniciativa = r.iniciativa;
                    c.rolagem_ini = r.rolagem;
                }
            });
            this.turnoAtual = 0;
            this.rodadaAtual = 1;
            this.combateAtivo = true;
            this.el('telaConfiguracao')?.classList.remove('ativa');
            this.el('telaArena')?.classList.add('ativa');
            this.atualizarUiCombate();
            Toast.success('Combate iniciado!');
        } catch (e) {
            Toast.error(e.message || 'Erro na iniciativa');
        }
    }

    encerrarCombate() {
        this.combateAtivo = false;
        this.el('telaArena')?.classList.remove('ativa');
        this.el('telaConfiguracao')?.classList.add('ativa');
        this.selecionados = new Set(this.combatentes.map((c) => c.id));
        this.renderSelecionados();
        this.renderListaDisponiveis();
    }

    renderFotoAtivo() {
        const container = this.el('arenaFotoAtivo');
        const c = this.combatenteAtual();
        if (!container) return;
        if (!c) {
            container.innerHTML = '<div class="arena-foto-vertical-placeholder">👤</div>';
            return;
        }
        if (c.foto_url) {
            container.innerHTML = `<img data-role="arena-foto-ativo" src="${c.foto_url}" alt="${c.nome}" style="width:100%;height:100%;object-fit:cover;border-radius:8px" />`;
        } else {
            container.innerHTML =
                '<div class="arena-foto-vertical-placeholder" style="display:flex;align-items:center;justify-content:center;font-size:2rem;opacity:0.3;height:100%">👤</div>';
        }
    }

    renderOrdemIniciativa() {
        const container = this.el('ordemIniciativaContainer');
        if (!container) return;
        container.innerHTML = this.combatentes
            .map((c, idx) => {
                const ativo = idx === this.turnoAtual;
                const hpPct = Math.max(
                    0,
                    Math.min(100, (c.hp_atual / (c.hp_maximo || 1)) * 100)
                );
                const hpCor = hpPct > 50 ? '#4CAF50' : hpPct > 25 ? '#FF9800' : '#F44336';
                const cond = (c.condicoes || [])
                    .map((x) => {
                        const nome =
                            this.catalogoCondicoes.find((m) => m.slug === x.slug)?.nome ||
                            x.slug;
                        return `<span class="badge-condicao-mini">${nome}</span>`;
                    })
                    .join('');
                const sv = c.status_vida || (c.hp_atual > 0 ? 'vivo' : 'inconsciente');
                const statusMini =
                    sv === 'morto'
                        ? '<span class="dnd5e-ordem-status dnd5e-status-morto">☠</span>'
                        : sv === 'estabilizado'
                          ? '<span class="dnd5e-ordem-status dnd5e-status-estabilizado">💤</span>'
                          : sv === 'inconsciente' && c.hp_atual === 0
                            ? '<span class="dnd5e-ordem-status dnd5e-status-morrendo">0</span>'
                            : '';
                return `
                <div class="combatente-ordem-item ${ativo ? 'ativo' : ''} ${sv === 'morto' ? 'dnd5e-ordem-morto' : ''}" data-idx="${idx}">
                    <span class="ordem-iniciativa-valor">${c.iniciativa ?? '—'}</span>
                    <div class="ordem-info">
                        <div class="ordem-nome-linha">
                            <span class="ordem-nome">${window.escapeHtml(c.nome)}</span>
                            ${statusMini}
                        </div>
                        <div class="ordem-hp-bar"><div class="ordem-hp-fill" style="width:${hpPct}%;background:${hpCor}"></div></div>
                        <div class="badges-condicao-ordem-wrapper">${cond}</div>
                    </div>
                </div>`;
            })
            .join('');

        container.querySelectorAll('.combatente-ordem-item').forEach((item) => {
            item.addEventListener('click', () => {
                const idx = parseInt(item.dataset.idx, 10);
                if (Number.isFinite(idx)) {
                    this.turnoAtual = idx;
                    this.atualizarUiCombate();
                }
            });
        });

        if (this.el('rodadaAtual')) {
            this.el('rodadaAtual').textContent = String(this.rodadaAtual);
        }
    }

    atualizarUiCombate() {
        this.renderOrdemIniciativa();
        this.renderFotoAtivo();
        const atual = this.combatenteAtual();
        Dnd5eCombatenteAtivoView.render(
            atual,
            this.catalogoCondicoes,
            (id, v) => this.aplicarDano(id, v),
            (id, v) => this.aplicarCura(id, v),
            (id) => this.modalCondicao?.abrir(id),
            () => this.proximoTurno(),
            {
                onDeathSave: (id) => this.rolarDeathSave(id),
                onEstabilizar: (id, metodo, modMedicina) =>
                    this.estabilizarCombatente(id, metodo, modMedicina),
                onMedicinaModChange: (id, mod) => this.atualizarModMedicina(id, mod),
                onEconomia: (tipo, metros) => this.gastarEconomia(tipo, metros),
                getAlvosAtaque: () => this.combatentes,
                onAtaqueFicha: (atacanteId, alvoId, idx) =>
                    this.executarAtaqueFicha(atacanteId, alvoId, idx),
            }
        );
        this._renderPainelConjuracao(atual);
        this.atualizarSelectAlvos();
    }

    async _renderPainelConjuracao(combatente) {
        const host = document.getElementById('dnd5eArenaMagiasHost');
        if (!host) return;
        if (!combatente?.personagemId || !combatente.classe) {
            host.innerHTML = '';
            return;
        }
        if (!Dnd5eArenaMagiasHelper.ehConjurador(combatente.classe)) {
            host.innerHTML = '';
            return;
        }
        try {
            await this._carregarDadosConjuracao(combatente);
        } catch (e) {
            host.innerHTML = '';
            console.warn('⚠️ Falha ao carregar conjuração:', e?.message || e);
            return;
        }
        this._renderMagiasHost(host, combatente);
    }

    async _carregarDadosConjuracao(combatente) {
        const [estado, grimorio] = await Promise.all([
            this.conjuracaoFichaService.obter(combatente.personagemId).catch(() => null),
            this.grimorioService
                .listar(combatente.personagemId, {
                    classe: combatente.classe,
                    limit: 200,
                })
                .catch(() => ({ items: [] })),
        ]);
        combatente._conjEstado = estado;
        combatente._magiasGrimorio = grimorio?.items || [];
        combatente.magia_concentracao_id =
            estado?.magia_concentracao_id ?? combatente.magia_concentracao_id ?? null;
    }

    _renderMagiasHost(host, combatente) {
        const modo = Dnd5eArenaMagiasHelper.modo(
            combatente.classe,
            combatente._conjEstado
        );
        if (modo === MODO_CONJURADOR.NENHUM) {
            host.innerHTML = '';
            return;
        }
        const lancadas = combatente._conjEstado?.magias_lancadas_ids || [];
        const grupos = Dnd5eArenaMagiasHelper.agruparPorNivel(
            combatente._magiasGrimorio,
            combatente._conjEstado,
            modo,
            lancadas
        );
        const slotBruxo =
            modo === MODO_CONJURADOR.BRUXO
                ? Dnd5eArenaMagiasHelper.slotBruxo(combatente._conjEstado)
                : null;

        host.innerHTML = Dnd5eArenaMagiasView.render(
            grupos,
            modo,
            slotBruxo,
            combatente._conjEstado
        );

        Dnd5eArenaMagiasView.bindEvents(host, {
            onLancar: (magiaId, nivel) =>
                this._lancarMagia(combatente, magiaId, nivel),
            onRestaurar: (magiaId, nivel) =>
                this._restaurarMagia(combatente, magiaId, nivel),
            onSlotDelta: (nivel, delta) =>
                this._ajustarSlot(combatente, nivel, delta),
        });
    }

    async _lancarMagia(combatente, magiaId, nivel) {
        const magia = (combatente._magiasGrimorio || []).find(
            (m) => Number(m.magia_id) === Number(magiaId)
        );
        if (!magia) {
            Toast.error('Magia não encontrada no grimório.');
            return;
        }
        const nivelMagia = Number(magia?.magia_nivel ?? nivel) || 0;
        if (nivelMagia >= 1) {
            const slotNivel = (combatente._conjEstado?.slots || []).find(
                (s) => Number(s.nivel) === nivelMagia
            );
            if (slotNivel && Number(slotNivel.disponiveis) <= 0) {
                Toast.error(`Sem espaços de magia disponíveis no nível ${nivelMagia}.`);
                return;
            }
        }
        const executar = (opts) =>
            this._executarConjuracao(combatente, magia, nivelMagia, opts);
        if (magiaPrecisaAlvo(magia) || magia.ritual || magia.material_consumido) {
            this.modalConjuracao.abrir({
                combatente,
                magia,
                nivel: nivelMagia,
                estado: combatente._conjEstado,
                onConfirm: executar,
            });
            return;
        }
        await executar({});
    }

    async _executarConjuracao(combatente, magia, nivelMagia, opts) {
        const payload = montarPayloadConjurar(
            combatente,
            magia,
            combatente._conjEstado,
            opts
        );
        try {
            const res = await cs.conjurarMagia(payload);
            if (!res.sucesso) {
                Toast.error(res.mensagem || 'Falha ao conjurar.');
                return;
            }

            if (!res.conjurada_como_ritual) {
                const slotGasto = res.nivel_slot_gasto ?? nivelMagia;
                combatente._conjEstado = await this.conjuracaoFichaService.gastarSlot(
                    combatente.personagemId,
                    slotGasto,
                    1,
                    magia.magia_id
                );
            } else {
                combatente._conjEstado = await this.conjuracaoFichaService.gastarSlot(
                    combatente.personagemId,
                    0,
                    0,
                    magia.magia_id
                );
            }

            if (res.requer_concentracao) {
                combatente.magia_concentracao_id = res.magia_concentracao_id ?? null;
                await this._persistirConcentracaoNaFicha(combatente, true);
            }

            const dano =
                res.dano_aplicar != null ? res.dano_aplicar : res.dano_total;
            if (dano != null && dano > 0 && opts.alvo) {
                await this.aplicarDano(opts.alvo.id, dano, {
                    is_critico: !!res.ataque_critico,
                });
            }

            Toast.success(res.mensagem || `${magia.magia_nome} conjurada.`);
            this._renderPainelConjuracao(combatente);
            this.renderPainelAtivo();
        } catch (e) {
            Toast.error(e.message || 'Erro ao conjurar magia.');
        }
    }

    async _testarConcentracaoAposDano(combatente, dano) {
        if (!combatente?.magia_concentracao_id || dano <= 0) return;
        try {
            const res = await cs.testeConcentracao({
                conjurador_id: combatente.id,
                dano_recebido: dano,
                mod_constituicao: modAtributo(combatente, 'con'),
                bonus_proficiencia: combatente.bonus_proficiencia ?? 2,
                magia_concentracao_id: combatente.magia_concentracao_id,
            });
            if (!res.manteve_concentracao) {
                combatente.magia_concentracao_id = null;
                await this._persistirConcentracaoNaFicha(combatente, true);
                Toast.warning(
                    res.mensagem || `${combatente.nome} perdeu a concentração.`
                );
            }
        } catch (e) {
            console.warn('Concentração:', e?.message || e);
        }
    }

    async _restaurarMagia(combatente, magiaId, nivel) {
        const magia = (combatente._magiasGrimorio || []).find(
            (m) => Number(m.magia_id) === Number(magiaId)
        );
        const nivelMagia = Number(magia?.magia_nivel ?? nivel) || 0;
        try {
            combatente._conjEstado =
                await this.conjuracaoFichaService.devolverSlot(
                    combatente.personagemId,
                    nivelMagia,
                    1,
                    magiaId
                );
        } catch (e) {
            Toast.error(e.message || 'Não foi possível devolver o espaço.');
            return;
        }
        Toast.success(
            nivelMagia
                ? `↩️ Espaço de NIV ${nivelMagia} devolvido`
                : `↩️ Marcação de ${magia?.magia_nome || 'truque'} removida`
        );
        this._renderMagiasHost(
            document.getElementById('dnd5eArenaMagiasHost'),
            combatente
        );
    }

    async _ajustarSlot(combatente, nivel, delta) {
        try {
            if (delta > 0) {
                combatente._conjEstado =
                    await this.conjuracaoFichaService.gastarSlot(
                        combatente.personagemId,
                        nivel,
                        1
                    );
            } else {
                combatente._conjEstado =
                    await this.conjuracaoFichaService.devolverSlot(
                        combatente.personagemId,
                        nivel,
                        1
                    );
            }
        } catch (e) {
            Toast.error(e.message || 'Não foi possível ajustar o espaço.');
            return;
        }
        this._renderMagiasHost(
            document.getElementById('dnd5eArenaMagiasHost'),
            combatente
        );
    }

    _aplicarResultadoMorte(c, res) {
        c.hp_atual = res.hp_atual ?? c.hp_atual;
        c.death_failures = res.death_failures ?? c.death_failures ?? 0;
        c.death_successes = res.death_successes ?? c.death_successes ?? 0;
        c.status_vida = res.status_vida || c.status_vida || 'vivo';
    }

    async aplicarDano(id, valor, { is_critico = false } = {}) {
        const c = this.combatentePorId(id);
        if (!c || c.status_vida === 'morto') return;
        try {
            const res = await cs.danoHp({
                hp_atual: c.hp_atual,
                hp_max: c.hp_maximo,
                dano: valor,
                death_failures: c.death_failures || 0,
                death_successes: c.death_successes || 0,
                is_critico,
                status_vida: c.status_vida || 'vivo',
            });
            this._aplicarResultadoMorte(c, res);
            await this._testarConcentracaoAposDano(c, valor);
            if (res.morte_instantanea) {
                Toast.error(`${c.nome}: morte instantânea!`);
            } else if (res.status_vida === 'morto') {
                Toast.error(`${c.nome} está morto.`);
            } else if (res.mensagem) {
                Toast.success(res.mensagem);
            }
            await this.syncHpCondicoes(c);
            this.atualizarUiCombate();
        } catch (e) {
            Toast.error(e.message || 'Erro ao aplicar dano');
        }
    }

    async aplicarCura(id, valor) {
        const c = this.combatentePorId(id);
        if (!c) return;
        c.hp_atual = Math.min(c.hp_maximo, c.hp_atual + valor);
        if (c.hp_atual > 0) {
            c.death_failures = 0;
            c.death_successes = 0;
            c.status_vida = 'vivo';
        }
        await this.syncHpCondicoes(c);
        this.atualizarUiCombate();
    }

    async rolarDeathSave(id) {
        const c = this.combatentePorId(id);
        if (!c || c.hp_atual > 0 || c.status_vida === 'morto') return;
        if (c.status_vida === 'estabilizado') return;
        try {
            const res = await cs.deathSave({
                hp_atual: c.hp_atual,
                death_failures: c.death_failures || 0,
                death_successes: c.death_successes || 0,
            });
            this._aplicarResultadoMorte(c, res);
            Toast.success(`Salvamento: ${res.rolagem} — ${res.mensagem}`);
            if (res.status_vida === 'morto') {
                Toast.error(`${c.nome} está morto.`);
            } else if (res.status_vida === 'estabilizado') {
                Toast.success(`${c.nome} estabilizou (3 sucessos).`);
            }
            if (res.hp_atual > 0) {
                await this.syncHpCondicoes(c);
            }
            this.atualizarUiCombate();
        } catch (e) {
            Toast.error(e.message || 'Erro no salvamento');
        }
    }

    atualizarModMedicina(id, mod) {
        const c = this.combatentePorId(id);
        if (!c) return;
        c.mod_medicina = Number(mod) || 0;
    }

    async estabilizarCombatente(id, metodo = 'medicina', modMedicina = null) {
        const c = this.combatentePorId(id);
        if (!c || c.hp_atual > 0 || c.status_vida === 'morto') return;
        const mod =
            modMedicina != null ? Number(modMedicina) : Number(c.mod_medicina) || 0;
        try {
            const res = await cs.estabilizar({
                hp_atual: c.hp_atual,
                death_failures: c.death_failures || 0,
                death_successes: c.death_successes || 0,
                metodo,
                mod_medicina: mod,
            });
            c.death_failures = res.death_failures;
            c.death_successes = res.death_successes;
            c.status_vida = res.status_vida;
            if (res.sucesso) {
                Toast.success(res.mensagem || `${c.nome} estabilizado.`);
            } else {
                Toast.error(res.mensagem || 'Falha ao estabilizar.');
            }
            this.atualizarUiCombate();
        } catch (e) {
            Toast.error(e.message || 'Erro ao estabilizar');
        }
    }

    async gastarEconomia(tipo, metros = 0) {
        const c = this.combatenteAtual();
        if (!c) return;
        try {
            const res = await cs.economiaTurno({
                tipo,
                metros,
                economia: c.economia || {},
            });
            c.economia = res.economia;
            if (res.mensagem) Toast.success(res.mensagem);
            this.atualizarUiCombate();
        } catch (e) {
            Toast.error(e.message || 'Ação indisponível');
        }
    }

    async proximoTurno() {
        const atual = this.combatenteAtual();
        if (atual?.hp_atual === 0 && atual.status_vida === 'inconsciente') {
            await this.rolarDeathSave(atual.id);
        }
        if (atual?.condicoes?.length) {
            try {
                const res = await cs.decrementarCondicoesTurno(atual.condicoes);
                atual.condicoes = res.condicoes || [];
                await this.persistirCondicoesNaFicha(atual, true);
            } catch (e) {
                Toast.error(e.message);
            }
        }
        this.turnoAtual += 1;
        if (this.turnoAtual >= this.combatentes.length) {
            this.turnoAtual = 0;
            this.rodadaAtual += 1;
        }
        const prox = this.combatenteAtual();
        if (prox) {
            try {
                const res = await cs.economiaTurno({
                    tipo: 'reset',
                    economia: prox.economia || {},
                });
                prox.economia = res.economia;
            } catch {
                prox.economia = {
                    acao_usada: false,
                    bonus_acao_usada: false,
                    movimento_usado_metros: 0,
                    reacao_usada: false,
                    velocidade_metros: 9,
                };
            }
        }
        this.atualizarUiCombate();
    }

    abrirModalDanoCura() {
        const modal = this.el('modalDanoCura');
        if (modal) modal.classList.add('show');
        this.renderListaModalDanoCura();
    }

    fecharModalDanoCura() {
        this.el('modalDanoCura')?.classList.remove('show');
    }

    renderListaModalDanoCura() {
        const box = this.el('listaCombatentesDanoCura');
        if (!box) return;
        box.innerHTML = this.combatentes
            .map(
                (c) => `
            <div class="checkbox-combatente-item">
                <input type="checkbox" id="dano5e-${c.id}" value="${c.id}" />
                <label for="dano5e-${c.id}">
                    <span class="combatente-nome">${window.escapeHtml(c.nome)}</span>
                    <span class="combatente-hp">${c.hp_atual}/${c.hp_maximo} PV</span>
                </label>
            </div>`
            )
            .join('');
    }

    async aplicarModalDanoCura() {
        const dano = parseInt(this.el('inputDanoModal')?.value, 10) || 0;
        const cura = parseInt(this.el('inputCuraModal')?.value, 10) || 0;
        const checks = this.el('listaCombatentesDanoCura')?.querySelectorAll(
            'input[type=checkbox]:checked'
        );
        if (!checks?.length) {
            Toast.error('Selecione ao menos um combatente.');
            return;
        }
        if ((dano > 0 && cura > 0) || (dano <= 0 && cura <= 0)) {
            Toast.error('Informe apenas dano ou apenas cura.');
            return;
        }
        for (const cb of checks) {
            if (dano > 0) await this.aplicarDano(cb.value, dano);
            else await this.aplicarCura(cb.value, cura);
        }
        this.fecharModalDanoCura();
        Toast.success('Valores aplicados.');
    }

    async syncFichasArena() {
        const comFicha = this.combatentes.filter((c) => c.personagemId);
        if (!comFicha.length) {
            Toast.error('Nenhum combatente vinculado a ficha.');
            return;
        }
        let ok = 0;
        for (const c of comFicha) {
            try {
                await this.persistirCondicoesNaFicha(c, true);
                ok += 1;
            } catch {
                /* toast em persistir */
            }
        }
        if (ok) Toast.success(`PV e condições salvos em ${ok} ficha(s).`);
    }

    atualizarSelectAlvos() {
        const sel = this.el('toolAlvoDano');
        if (!sel) return;
        const prev = sel.value;
        sel.innerHTML = this.combatentes
            .map(
                (c) =>
                    `<option value="${c.id}">${window.escapeHtml(c.nome)} (CA ${c.ca})</option>`
            )
            .join('');
        if (prev && this.combatentes.some((c) => c.id === prev)) sel.value = prev;
        this.sincronizarToolAcComAlvo();
    }

    sincronizarToolAcComAlvo() {
        const alvo = this.combatentePorId(this.el('toolAlvoDano')?.value);
        if (alvo && this.el('toolAc')) this.el('toolAc').value = String(alvo.ca);
    }

    slugsCondicoes(c) {
        return CU.slugs(c?.condicoes || []);
    }

    async executarAtaqueFicha(atacanteId, alvoId, ataqueIdx) {
        const atacante = this.combatentePorId(atacanteId);
        const alvo = this.combatentePorId(alvoId);
        if (!atacante || !alvo) {
            Toast.error('Combatente inválido.');
            return;
        }
        if (alvo.status_vida === 'morto') {
            Toast.error('Alvo está morto.');
            return;
        }
        const ataque = (atacante.ataques || [])[ataqueIdx];
        if (!ataque) return;

        if (atacante.economia?.acao_usada) {
            Toast.warning('Ação já usada neste turno (use o painel de economia se necessário).');
        }

        const bonusExtra = parseBonusAtaque(ataque.bonus_ataque);
        try {
            const res = await cs.ataque({
                mod_atributo: 0,
                bonus_proficiencia: 0,
                proficiente: false,
                bonus_extra: bonusExtra,
                ac_alvo: alvo.ca ?? 10,
                condicoes_atacante: this.slugsCondicoes(atacante),
                condicoes_alvo: this.slugsCondicoes(alvo),
                corpo_a_corpo: true,
            });

            const critTxt = res.is_critico ? ' — CRÍTICO!' : '';
            if (res.acerto) {
                Toast.success(
                    `${ataque.nome}: acertou (${res.total} ≥ CA ${alvo.ca})${critTxt}`
                );
                if (ataque.dano) {
                    const { dano, mod } = parseDanoFicha(ataque.dano);
                    const danoRes = await cs.dano({
                        dano,
                        mod_atributo: mod,
                        is_critico: !!res.is_critico,
                    });
                    await this.aplicarDano(alvo.id, danoRes.dano_total, {
                        is_critico: !!res.is_critico,
                    });
                }
            } else {
                Toast.warning(`${ataque.nome}: errou (${res.total} vs CA ${alvo.ca})`);
            }

            if (!atacante.economia?.acao_usada) {
                try {
                    const eco = await cs.economiaTurno({
                        tipo: 'acao',
                        metros: 0,
                        economia: atacante.economia || {},
                    });
                    atacante.economia = eco.economia;
                } catch {
                    /* economia opcional */
                }
            }
            this.atualizarUiCombate();
        } catch (e) {
            Toast.error(e.message || 'Erro ao resolver ataque');
        }
    }

    async testarAtaque() {
        const alvo = this.combatentePorId(this.el('toolAlvoDano')?.value);
        const ac = alvo ? alvo.ca : parseInt(this.el('toolAc')?.value, 10) || 10;
        const atacante = this.combatenteAtual();
        try {
            const res = await cs.ataque({
                mod_atributo: parseInt(this.el('toolMod')?.value, 10) || 0,
                bonus_proficiencia: parseInt(this.el('toolProf')?.value, 10) || 2,
                ac_alvo: ac,
                condicoes_atacante: atacante ? this.slugsCondicoes(atacante) : [],
                condicoes_alvo: alvo ? this.slugsCondicoes(alvo) : [],
                corpo_a_corpo: this.el('toolCorpoACorpo')?.checked,
            });
            const elRes = this.el('toolAtaqueRes');
            if (elRes) {
                const crit = res.is_critico ? ' CRÍTICO!' : '';
                elRes.textContent = res.acerto
                    ? `Acertou (${res.total} ≥ CA ${ac})${crit}`
                    : `Errou (${res.total} vs CA ${ac})`;
                elRes.dataset.criticoAuto =
                    res.is_critico || res.critico_automatico ? '1' : '';
            }
        } catch (e) {
            Toast.error(e.message);
        }
    }

    async rolarDano() {
        const alvo = this.combatentePorId(this.el('toolAlvoDano')?.value);
        if (!alvo) {
            Toast.error('Selecione um alvo.');
            return;
        }
        const critico = this.el('toolAtaqueRes')?.dataset.criticoAuto === '1';
        try {
            const res = await cs.dano({
                dano: this.el('toolDano')?.value?.trim() || '1d8',
                mod_atributo: parseInt(this.el('toolDanoMod')?.value, 10) || 0,
                is_critico: critico,
            });
            await this.aplicarDano(alvo.id, res.dano_total, { is_critico: critico });
            const elRes = this.el('toolDanoRes');
            if (elRes) {
                elRes.textContent = `${res.dano_total} em ${alvo.nome} (PV ${alvo.hp_atual})`;
            }
            if (this.el('toolAtaqueRes')) this.el('toolAtaqueRes').dataset.criticoAuto = '';
        } catch (e) {
            Toast.error(e.message);
        }
    }
}

// Avançar turno ao clicar na ordem ou via teclado — botão não estava no HTML dnd35 lateral; adicionamos listener duplo-clique na ordem
document.addEventListener('DOMContentLoaded', () => {
    const arena = new Dnd5eArenaController();
    window.dnd5eArena = arena;
    document.addEventListener('keydown', (e) => {
        if (e.key === ' ' && arena.combateAtivo) {
            e.preventDefault();
            arena.proximoTurno();
        }
    });
});
