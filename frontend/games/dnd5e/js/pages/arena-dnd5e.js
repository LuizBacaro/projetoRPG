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
            forca: p.strength,
            destreza: p.dexterity,
            constituicao: p.constitution,
            inteligencia: p.intelligence,
            sabedoria: p.wisdom,
            carisma: p.charisma,
            salvamentos: this._salvamentosDePersonagem(p, f),
        };
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
        return ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
            .slice(0, 3)
            .map((key, i) => {
                const labels = ['Fortitude', 'Reflexos', 'Vontade'];
                const mod = p[`${key}_mod`] ?? 0;
                const prof = p.bonus_proficiencia ?? 2;
                return { label: labels[i] || map[key], bonus: mod };
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
            if (!silencioso) Toast.success(`Ficha de ${c.nome} atualizada.`);
        } catch (e) {
            Toast.error(`${c.nome}: ${e.message}`);
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
                const ia = ordemMap.get(a.id)?.iniciativa ?? 0;
                const ib = ordemMap.get(b.id)?.iniciativa ?? 0;
                return ib - ia;
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
                return `
                <div class="combatente-ordem-item ${ativo ? 'ativo' : ''}" data-idx="${idx}">
                    <span class="ordem-iniciativa-valor">${c.iniciativa ?? '—'}</span>
                    <div class="ordem-info">
                        <div class="ordem-nome-linha">
                            <span class="ordem-nome">${window.escapeHtml(c.nome)}</span>
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
            () => this.proximoTurno()
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

        host.innerHTML = Dnd5eArenaMagiasView.render(grupos, modo, slotBruxo);

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
        const nivelMagia = Number(magia?.magia_nivel ?? nivel) || 0;
        try {
            combatente._conjEstado = await this.conjuracaoFichaService.gastarSlot(
                combatente.personagemId,
                nivelMagia,
                1,
                magiaId
            );
        } catch (e) {
            Toast.error(e.message || 'Sem espaços de magia disponíveis.');
            return;
        }
        Toast.success(
            `🔥 ${magia?.magia_nome || 'Magia'}${nivelMagia ? ` (NIV ${nivelMagia})` : ''}`
        );
        this._renderMagiasHost(
            document.getElementById('dnd5eArenaMagiasHost'),
            combatente
        );
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
        Toast.success(`↩️ ${magia?.magia_nome || 'Magia'} restaurada`);
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

    async aplicarDano(id, valor) {
        const c = this.combatentePorId(id);
        if (!c) return;
        c.hp_atual = Math.max(0, c.hp_atual - valor);
        await this.syncHpCondicoes(c);
        this.atualizarUiCombate();
    }

    async aplicarCura(id, valor) {
        const c = this.combatentePorId(id);
        if (!c) return;
        c.hp_atual = Math.min(c.hp_maximo, c.hp_atual + valor);
        await this.syncHpCondicoes(c);
        this.atualizarUiCombate();
    }

    async proximoTurno() {
        const atual = this.combatenteAtual();
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
                elRes.textContent = res.acerto
                    ? `Acertou (${res.total} ≥ CA ${ac})`
                    : `Errou (${res.total} vs CA ${ac})`;
                elRes.dataset.criticoAuto = res.critico_automatico ? '1' : '';
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
        const critico =
            this.el('toolAtaqueRes')?.dataset.criticoAuto === '1' ||
            this.slugsCondicoes(alvo).includes('incapacitado');
        try {
            const res = await cs.dano({
                dano: this.el('toolDano')?.value?.trim() || '1d8',
                mod_atributo: parseInt(this.el('toolDanoMod')?.value, 10) || 0,
                is_critico: critico && this.el('toolCorpoACorpo')?.checked,
            });
            await this.aplicarDano(alvo.id, res.dano_total);
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
