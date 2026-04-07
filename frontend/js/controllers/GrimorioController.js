import { MagiaService } from '../services/MagiaService.js';
import { GrimorioService } from '../services/GrimorioService.js';
import { MagiaPreparadaService } from '../services/MagiaPreparadaService.js?v=20260401b';
import { getApiUrl } from '../config/api.config.js';
import { escapeHtml } from '../utils/formatters.js';
import {
    installGlobalErrorGuards,
    reportDegradedMode,
    safeBootstrap,
} from '../utils/graceful-degradation.js';
import {
    isClasseConjuradora,
    normalizeClasseConjuradora,
    resolveCombatenteSpellSlots,
} from '../utils/combat-rules.js?v=20260331a';

const ESCOLAS_ORDEM = [
    'Abjuracao',
    'Adivinhacao',
    'Conjuracao',
    'Encantamento',
    'Evocacao',
    'Ilusao',
    'Necromancia',
    'Transmutacao',
    'Universal',
];

const COMPONENTES = ['V', 'G', 'M', 'F', 'FD', 'XP'];

class GrimorioController {
    constructor(combatente, token, magiaService = null, grimorioService = null) {
        this.combatente = combatente;
        this.token = token || localStorage.getItem('token');
        this.magiaService = magiaService || new MagiaService(this.token);
        this.grimorioService = grimorioService || new GrimorioService(this.token);
        this.magiaPreparadaService = new MagiaPreparadaService(this.token);
        this._canal = null;
        try {
            this._canal = new BroadcastChannel('magias-rpg');
        } catch (_error) {
            this._canal = null;
        }

        this.classesConjuradoras = this._extrairClassesConjuradoras(combatente?.classe);
        this.classeAtiva = this.classesConjuradoras[0] || normalizeClasseConjuradora(combatente?.classe) || '';

        this.itensGrimorio = [];
        this.catalogoClasse = [];
        this.catalogoIndex = new Map();
        this.magiasPreparadas = [];
        this.magiasPreparadasMap = new Map();
        this.preparacaoQuantidadesDraft = new Map();
        this.slotsDisponiveis = {};

        this.itensFiltrados = [];
        this.historicoTrocas = [];
        this.notificacoes = [];
        this.indiceDetalheAtual = -1;
        this.nivelAtivo = 'todos';
        this.escolaAtiva = 'todas';
        this.componenteAtivo = 'todos';
        this.favoritasApenas = false;
        this.preparadasApenas = false;
        this.magiaAdicionarSelecionadaId = null;
        this.magiasDisponiveisAdicionar = [];

        this.cardsAbertos = new Set();
        this._carregado = false;
        this._onAdicionarKeydown = null;
        this._adicionarMagiaEmAndamento = false;
        this._ultimoAdicionarAt = 0;
        this._feedbackAdicionar = null;
    }

    async abrirGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (!overlay) return;

        overlay.classList.add('show');
        document.body.style.overflow = 'hidden';

        await this._recarregarDados();
        this._configurarFiltros();
    }

    fecharGrimorio() {
        const overlay = document.getElementById('modalGrimorio');
        if (overlay) overlay.classList.remove('show');
        this._sincronizarModoPainelAdicionar(false);
        document.body.style.overflow = '';
    }

    _sincronizarModoPainelAdicionar(ativo) {
        const overlay = document.getElementById('modalGrimorio');
        const container = overlay?.querySelector('.grimorio-container');
        if (!container) return;

        container.classList.toggle('grimorio-container--catalogo', !!ativo);
    }

    _definirPainelAdicionarVisivel(visivel) {
        const painel = document.getElementById('grimorioPainelAdicionar');
        const painelTroca = document.getElementById('grimorioPainelTroca');
        const painelNotificacoes = document.getElementById('grimorioPainelNotificacoes');
        if (!painel) return false;

        if (visivel) {
            painelTroca?.classList.remove('show');
            painelNotificacoes?.classList.remove('show');
            painel.classList.add('show');
            this._sincronizarModoPainelAdicionar(true);
            this._renderizarPainelAdicionar();
            setTimeout(() => {
                document.getElementById('grimorioAdicionarBusca')?.focus();
            }, 30);
            return true;
        }

        painel.classList.remove('show');
        this._sincronizarModoPainelAdicionar(false);
        return false;
    }

    filtrar() {
        const busca = (document.getElementById('grimorioBusca')?.value || '').toLowerCase().trim();

        this.itensFiltrados = this.itensGrimorio.filter((item) => {
            const magia = item.magia || {};

            const matchNivel = this.nivelAtivo === 'todos' || String(magia.nivel ?? '') === String(this.nivelAtivo);
            const escolaNormalizada = this._normalizarEscola(magia.escola || '');
            const matchEscola = this.escolaAtiva === 'todas' || escolaNormalizada === this.escolaAtiva;

            const matchComponente = this.componenteAtivo === 'todos'
                || String(magia.componentes || '').toUpperCase().includes(this.componenteAtivo);

            const matchFavorita = !this.favoritasApenas || !!item.favorita;
            const matchPreparada = !this.preparadasApenas || this.magiasPreparadasMap.has(Number(item.magia_id));

            if (!busca) return matchNivel && matchEscola && matchComponente && matchFavorita && matchPreparada;

            const alvoBusca = [
                magia.nome,
                magia.escola,
                magia.descricao,
                magia.componentes,
                item.anotacoes,
            ].filter(Boolean).join(' ').toLowerCase();

            return matchNivel && matchEscola && matchComponente && matchFavorita && matchPreparada && alvoBusca.includes(busca);
        });

        this._renderizarLista();
    }

    async _recarregarDados() {
        this._mostrarLoading(true);
        try {
            await this._carregarCatalogoClasse();
            await Promise.all([
                this._carregarItensGrimorio(),
                this._carregarNotificacoes(),
                this._carregarMagiasPreparadas(),
                this._carregarHistoricoTrocas(),
            ]);

            this._renderizarCabecalho();
            this._renderizarSeletorClasses();
            this._renderizarFiltroEscolas();
            this._renderizarIndicadores();
            this._atualizarVisibilidadeAcoesClasse();
            this._renderizarPainelSlots();
            this._renderizarHistoricoTrocas();
            this._renderizarNotificacoes();
            this._atualizarBadgeTrocaDisponivel();
            this.filtrar();
            this._renderizarPainelAdicionar();
            this._renderizarPainelTroca();
            this._carregado = true;
        } catch (error) {
            this._mostrarToast(error.message || 'Não foi possível carregar o grimório.', 'erro');
        } finally {
            this._mostrarLoading(false);
        }
    }

    async _carregarCatalogoClasse() {
        if (!this.classeAtiva) {
            this.catalogoClasse = [];
            this.catalogoIndex = new Map();
            return;
        }

        this.catalogoClasse = await this.magiaService.listarPorClasse(this.classeAtiva);
        this.catalogoIndex = new Map(this.catalogoClasse.map((magia) => [Number(magia.id), magia]));
    }

    async _carregarItensGrimorio() {
        if (!this.combatente?.id || !this.classeAtiva) {
            this.itensGrimorio = [];
            return;
        }

        const itens = await this.grimorioService.listar(this.combatente.id, { classe: this.classeAtiva });
        this.itensGrimorio = itens.map((item) => this._mapearItemGrimorio(item));
        this._mesclarCatalogoDisponivelNoGrimorio();
    }

    async _carregarNotificacoes() {
        if (!this.combatente?.id || !this.classeAtiva) {
            this.notificacoes = [];
            return;
        }

        try {
            this.notificacoes = await this.grimorioService.listarNotificacoes(this.combatente.id, {
                classe: this.classeAtiva,
                limit: 25,
            });
        } catch (_error) {
            this.notificacoes = [];
        }
    }

    _mapearItemGrimorio(item, extras = {}) {
        const magiaDetalhada = this.catalogoIndex.get(Number(item.magia_id ?? item.id));
        const nivelFallback = Number(item.magia_nivel ?? item.nivel ?? magiaDetalhada?.nivel ?? 0);
        const dominioFallback = item.magia_e_magia_dominio ?? item.e_magia_dominio ?? magiaDetalhada?.e_magia_dominio ?? false;
        const dominiosFallback = item.magia_dominios ?? item.dominios ?? magiaDetalhada?.dominios ?? '';
        const magiaMesclada = {
            ...(magiaDetalhada || {}),
            ...(item.magia || {}),
            id: Number(item.magia_id ?? item.id),
            nome: item.magia_nome || item.nome || magiaDetalhada?.nome || `Magia ${item.magia_id ?? item.id}`,
            escola: item.magia_escola || item.escola || magiaDetalhada?.escola || '',
            nivel: Number.isNaN(nivelFallback) ? 0 : nivelFallback,
            componentes: item.magia_componentes || item.componentes || magiaDetalhada?.componentes || '',
            e_magia_dominio: !!dominioFallback,
            dominios: dominiosFallback,
            descricao: item.descricao || magiaDetalhada?.descricao || '',
            sub_escola: item.sub_escola || item.subescola || magiaDetalhada?.sub_escola || magiaDetalhada?.subescola || '',
            subescola: item.sub_escola || item.subescola || magiaDetalhada?.sub_escola || magiaDetalhada?.subescola || '',
            area_efeito: item.area_efeito || item.area_efeito_alvo || magiaDetalhada?.area_efeito || magiaDetalhada?.area_efeito_alvo || '',
            area_efeito_alvo: item.area_efeito || item.area_efeito_alvo || magiaDetalhada?.area_efeito || magiaDetalhada?.area_efeito_alvo || '',
            resistencia_magia: item.resistencia_magia || magiaDetalhada?.resistencia_magia || magiaDetalhada?.resistencia_magia_texto || '',
        };

        return {
            ...item,
            ...extras,
            magia_id: Number(item.magia_id ?? item.id),
            classe: item.classe || this.classeAtiva,
            favorita: !!item.favorita,
            anotacoes: item.anotacoes || '',
            magia: magiaMesclada,
        };
    }

    _classePermiteGerenciarConhecidas() {
        const classeNorm = this._normalizarClasse(this.classeAtiva);
        return classeNorm === 'Mago' || classeNorm === 'Bardo' || classeNorm === 'Feiticeiro';
    }

    _classeEhEspontanea() {
        const classeNorm = this._normalizarClasse(this.classeAtiva);
        return classeNorm === 'Bardo' || classeNorm === 'Feiticeiro';
    }

    _classeExibeCatalogoCompleto() {
        const classeNorm = String(this._normalizarClasse(this.classeAtiva) || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toLowerCase();
        // Clérigo e Druida têm acesso automático a todas as magias do nível
        return classeNorm === 'clerigo' || classeNorm === 'druida';
    }

    _mesclarCatalogoDisponivelNoGrimorio() {
        if (!this._classeExibeCatalogoCompleto()) return;

        const maxNivelConjuravel = this._maxNivelConjuravel(this.classeAtiva, Number(this.combatente?.nivel || 1));
        const itensPorId = new Map(this.itensGrimorio.map((item) => [Number(item.magia_id), item]));

        this.catalogoClasse
            .filter((magia) => Number(magia.nivel || 0) <= maxNivelConjuravel)
            .forEach((magia) => {
                const magiaId = Number(magia.id);
                if (itensPorId.has(magiaId)) return;
                itensPorId.set(magiaId, this._mapearItemGrimorio(magia, {
                    magia_id: magiaId,
                    origem: 'CATALOGO_CLASSE',
                    _catalogo_expandido: true,
                }));
            });

        this.itensGrimorio = [...itensPorId.values()]
            .sort((a, b) => {
                const nivelA = Number(a.magia?.nivel || 0);
                const nivelB = Number(b.magia?.nivel || 0);
                if (nivelA !== nivelB) return nivelA - nivelB;
                return String(a.magia?.nome || '').localeCompare(String(b.magia?.nome || ''), 'pt-BR');
            });
    }

    async _carregarMagiasPreparadas() {
        if (!this.combatente?.id) {
            this.magiasPreparadas = [];
            this.magiasPreparadasMap = new Map();
            this.slotsDisponiveis = {};
            return;
        }

        try {
            const preparadas = await this.magiaPreparadaService.listar(this.combatente.id);
            this.magiasPreparadas = Array.isArray(preparadas) ? preparadas : [];
        } catch (_error) {
            this.magiasPreparadas = [];
        }

        this.magiasPreparadasMap = new Map(
            this.magiasPreparadas.map((item) => [Number(item.magia_id), item])
        );
        this.preparacaoQuantidadesDraft = new Map(
            this.magiasPreparadas.map((item) => [Number(item.magia_id), this._quantidadePreparada(item)])
        );
        if (this.combatente) {
            this.combatente.magias_preparadas = [...this.magiasPreparadas];
        }
        this._hidratarSlotsDisponiveis();
    }

    _quantidadePreparada(registro) {
        return Math.max(1, Number(registro?.quantidade || 1));
    }

    _quantidadeUsada(registro) {
        const quantidade = this._quantidadePreparada(registro);
        const usos = Number(registro?.usos_realizados ?? (registro?.usada ? 1 : 0) ?? 0);
        return Math.max(0, Math.min(quantidade, usos));
    }

    _obterQuantidadePreparacaoRapida(magiaId, preparo) {
        const draft = this.preparacaoQuantidadesDraft.get(Number(magiaId));
        const min = preparo?.preparada ? 0 : (preparo?.temEspaco ? 1 : 0);
        const fallback = preparo?.preparada ? Number(preparo.quantidadeAtual || 0) : min;
        const max = Math.max(min, Number(preparo?.quantidadeMaxima || fallback || 0));
        const valorBase = draft ?? fallback;
        return Math.max(min, Math.min(max, Number(valorBase || 0)));
    }

    _atualizarQuantidadePreparacaoRapida(magiaId, valor) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return 0;

        const preparo = this._obterInfoPreparacao(item);
        const min = preparo.preparada ? 0 : (preparo.temEspaco ? 1 : 0);
        const max = Math.max(min, Number(preparo.quantidadeMaxima || min || 0));
        const valorNumero = Math.trunc(Number(valor));
        const normalizado = Math.max(min, Math.min(max, Number.isFinite(valorNumero) ? valorNumero : min));

        this.preparacaoQuantidadesDraft.set(Number(magiaId), normalizado);
        return normalizado;
    }

    _lerQuantidadePreparacaoCard(magiaId) {
        const input = document.querySelector(`.grimorio-preparo-input[data-magia-id="${Number(magiaId)}"]`);
        const valor = this._atualizarQuantidadePreparacaoRapida(magiaId, input?.value);
        if (input) {
            input.value = String(valor);
        }
        return valor;
    }

    _hidratarSlotsDisponiveis() {
        const slots = resolveCombatenteSpellSlots(this.combatente, this.classeAtiva);
        const mapa = {};

        if (this.combatente) {
            this.combatente.magias_slots = slots;
        }

        slots.forEach((slot) => {
            const nivel = Number(slot?.nivel || 0);
            const total = Math.max(0, Number(slot?.total || 0));
            const preparadas = this.magiasPreparadas
                .filter((item) => Number(item.nivel_slot || 0) === nivel)
                .reduce((soma, item) => soma + this._quantidadePreparada(item), 0);
            const usadas = this.magiasPreparadas
                .filter((item) => Number(item.nivel_slot || 0) === nivel)
                .reduce((soma, item) => soma + this._quantidadeUsada(item), 0);
            mapa[nivel] = {
                nivel,
                total,
                preparadas,
                usadas,
                disponivel: Math.max(total - preparadas, 0),
            };
        });

        this.slotsDisponiveis = mapa;
    }

    _renderizarPainelSlots() {
        const grid = document.querySelector('#modalGrimorio .grimorio-slots-grid');
        if (!grid) return;

        const slots = Object.values(this.slotsDisponiveis || {})
            .filter((slot) => Number(slot.total || 0) > 0)
            .sort((a, b) => a.nivel - b.nivel);

        if (!slots.length) {
            grid.innerHTML = '<span class="grimorio-slots-vazio">Nenhum slot de magia ativo para esta classe.</span>';
            return;
        }

        grid.innerHTML = slots.map((slot) => {
            const cor = slot.disponivel <= 0 ? '#f87171' : slot.disponivel < slot.total ? '#facc15' : '#4ade80';
            const label = Number(slot.nivel) === 0 ? 'Truque' : `N${slot.nivel}`;
            const largura = slot.total > 0 ? Math.max(8, (slot.disponivel / slot.total) * 100) : 0;
            return `
                <div class="grimorio-slot-box">
                    <span class="grimorio-slot-nivel">${label}</span>
                    <div class="grimorio-slot-barra-wrap">
                        <div class="grimorio-slot-barra-fill" style="width:${largura}%; background:${cor}"></div>
                    </div>
                    <span class="grimorio-slot-contagem" style="color:${cor}">${slot.preparadas}/${slot.total}</span>
                    <span class="grimorio-slot-usadas">${slot.usadas} usada(s)</span>
                </div>
            `;
        }).join('');
    }

    _atualizarVisibilidadeAcoesClasse() {
        const wrapAcoes = document.querySelector('#modalGrimorio .grimorio-adicionar-wrap');
        const acoes = document.querySelector('#modalGrimorio .grimorio-adicionar-acoes');
        const painelAdicionar = document.getElementById('grimorioPainelAdicionar');
        const painelTroca = document.getElementById('grimorioPainelTroca');
        const painelNotificacoes = document.getElementById('grimorioPainelNotificacoes');
        const mostrarAcoes = this._classePermiteGerenciarConhecidas();

        if (wrapAcoes) {
            wrapAcoes.style.display = mostrarAcoes ? 'flex' : 'none';
        }

        if (acoes) {
            acoes.style.display = mostrarAcoes ? 'flex' : 'none';
        }

        if (!mostrarAcoes) {
            painelAdicionar?.classList.remove('show');
            painelTroca?.classList.remove('show');
            painelNotificacoes?.classList.remove('show');
            this._sincronizarModoPainelAdicionar(false);
        }
    }

    _obterInfoPreparacao(item) {
        const magiaId = Number(item?.magia_id ?? item?.id ?? 0);
        const nivelSlot = Number(item?.magia?.nivel ?? item?.nivel ?? 0);
        const registro = this.magiasPreparadasMap.get(magiaId) || null;
        const slot = this.slotsDisponiveis[nivelSlot] || {
            nivel: nivelSlot,
            total: 0,
            preparadas: 0,
            usadas: 0,
            disponivel: 0,
        };
        const quantidadeAtual = registro ? this._quantidadePreparada(registro) : 0;
        const usosRealizados = registro ? this._quantidadeUsada(registro) : 0;
        const quantidadeMaxima = Number(slot.total || 0) > 0
            ? Math.max(quantidadeAtual, Number(slot.disponivel || 0) + quantidadeAtual)
            : quantidadeAtual;

        return {
            magiaId,
            nivelSlot,
            registro,
            preparada: quantidadeAtual > 0,
            usada: usosRealizados > 0,
            parcialmenteUsada: usosRealizados > 0 && usosRealizados < quantidadeAtual,
            totalmenteUsada: quantidadeAtual > 0 && usosRealizados >= quantidadeAtual,
            quantidadeAtual,
            usosRealizados,
            quantidadeMaxima,
            slot,
            podePreparar: Number(slot.total || 0) > 0 || quantidadeAtual > 0,
            temEspaco: Number(slot.disponivel || 0) > 0 || quantidadeAtual > 0,
        };
    }

    _renderizarCabecalho() {
        const subtitulo = document.getElementById('grimorioSubtitulo');
        if (!subtitulo || !this.combatente) return;

        const classes = this.classesConjuradoras.join(' / ') || 'Nao conjurador';
        subtitulo.textContent = `${this.combatente.nome} - ${classes} - Nivel ${this.combatente.nivel}`;
    }

    _renderizarSeletorClasses() {
        const wrap = document.getElementById('grimorioClasseWrap');
        const select = document.getElementById('grimorioClasseSelect');
        if (!wrap || !select) return;

        if (this.classesConjuradoras.length <= 1) {
            wrap.style.display = 'none';
            return;
        }

        wrap.style.display = 'flex';
        select.innerHTML = this.classesConjuradoras
            .map((classe) => `<option value="${escapeHtml(classe)}">${escapeHtml(classe)}</option>`)
            .join('');
        select.value = this.classeAtiva;

        const novoSelect = select.cloneNode(true);
        select.parentNode.replaceChild(novoSelect, select);
        novoSelect.addEventListener('change', async (event) => {
            this.classeAtiva = event.target.value;
            this.cardsAbertos.clear();
            this.favoritasApenas = false;
            this.preparadasApenas = false;
            await this._recarregarDados();
            this._configurarFiltros();
        });
    }

    _renderizarIndicadores() {
        const totalEl = document.getElementById('grimorioTotalMagias');
        const paginaEl = document.getElementById('grimorioTotalPaginas');
        const paginaNivelWrap = document.getElementById('grimorioPaginasPorNivelWrap');
        const paginaNivelEl = document.getElementById('grimorioPaginasPorNivel');
        const classeNorm = this._normalizarClasse(this.classeAtiva);

        if (totalEl) totalEl.textContent = `${this.itensGrimorio.length}`;

        if (!paginaEl) return;
        if (classeNorm !== 'Mago') {
            paginaEl.textContent = '-';
            if (paginaNivelWrap) paginaNivelWrap.style.display = 'none';
            if (paginaNivelEl) paginaNivelEl.textContent = '-';
            return;
        }

        const paginasPorNivel = new Map();
        const totalPaginas = this.itensGrimorio.reduce((sum, item) => {
            const nivel = Number(item.magia?.nivel || 0);
            const paginas = nivel <= 0 ? 1 : nivel;
            paginasPorNivel.set(nivel, (paginasPorNivel.get(nivel) || 0) + paginas);
            return sum + paginas;
        }, 0);

        paginaEl.textContent = `${totalPaginas}`;
        if (paginaNivelWrap) paginaNivelWrap.style.display = 'inline-flex';
        if (paginaNivelEl) {
            paginaNivelEl.textContent = [...paginasPorNivel.entries()]
                .sort((a, b) => a[0] - b[0])
                .map(([nivel, paginas]) => `N${nivel}: ${paginas}`)
                .join(' | ');
        }
    }

    _classeSemAcessoMagias() {
        const classe = this._normalizarClasse(this.classeAtiva);
        const nivel = Number(this.combatente?.nivel || 1);
        return (classe === 'Ranger' || classe === 'Paladino') && nivel < 4;
    }

    _renderizarAvisoClasse() {
        const avisoEl = document.getElementById('grimorioAvisoClasse');
        if (!avisoEl) return;

        if (!this._classeSemAcessoMagias()) {
            if (!this._classeAtivaEhClerigo()) {
                avisoEl.style.display = 'none';
                avisoEl.textContent = '';
                avisoEl.classList.remove('grimorio-aviso-classe--alerta', 'grimorio-aviso-classe--clerigo');
                return;
            }

            const alinhamento = escapeHtml(this._formatarAlinhamentoCombatente());
            const dominios = this._dominiosCombatenteFormatados();
            const dominiosTexto = dominios.length > 0
                ? escapeHtml(dominios.join(', '))
                : 'nenhum informado';

            avisoEl.style.display = 'block';
            avisoEl.classList.remove('grimorio-aviso-classe--alerta');
            avisoEl.classList.add('grimorio-aviso-classe--clerigo');
            avisoEl.innerHTML = `
                <strong>Regras automaticas de clerigo ativas:</strong>
                alinhamento <strong>${alinhamento}</strong> •
                dominios selecionados <strong>${dominiosTexto}</strong> •
                magias de dominio exigem o dominio correspondente •
                dominios opostos podem bloquear magias (Bem x Mal, Ordem/Lei x Caos, Protecao x Destruicao).
            `;
            return;
        }

        const nivel = Number(this.combatente?.nivel || 1);
        avisoEl.style.display = 'block';
        avisoEl.classList.remove('grimorio-aviso-classe--clerigo');
        avisoEl.classList.add('grimorio-aviso-classe--alerta');
        avisoEl.textContent = `Esta classe so recebe acesso a magias no nivel 4. Nivel atual: ${nivel}.`;
    }

    _formatarAlinhamentoCombatente() {
        const bruto = String(this.combatente?.alinhamento || this.combatente?.tendencia || '').trim();
        if (!bruto) return 'nao informado';

        return bruto
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[\/_-]+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .split(' ')
            .map((parte) => parte.charAt(0).toUpperCase() + parte.slice(1).toLowerCase())
            .join(' ');
    }

    _dominiosCombatenteFormatados() {
        const candidatos = [
            this.combatente?.dominios,
            this.combatente?.dominio,
            this.combatente?.dominio_1,
            this.combatente?.dominio_2,
            this.combatente?.dominio1,
            this.combatente?.dominio2,
        ];

        const unicos = new Map();
        candidatos.forEach((valor) => {
            String(valor || '')
                .split(/[,/;|]/)
                .map((parte) => parte.trim())
                .filter(Boolean)
                .forEach((parte) => {
                    const chave = parte
                        .normalize('NFD')
                        .replace(/[\u0300-\u036f]/g, '')
                        .toLowerCase();
                    if (!chave) return;
                    if (unicos.has(chave)) return;
                    const rotulo = parte.charAt(0).toUpperCase() + parte.slice(1).toLowerCase();
                    unicos.set(chave, rotulo);
                });
        });

        return [...unicos.values()]
            .sort((a, b) => a.localeCompare(b, 'pt-BR'));
    }

    _renderizarFiltroEscolas() {
        const container = document.getElementById('grimorioFiltroEscolas');
        if (!container) return;

        const escolas = new Set();
        const origens = []
            .concat(Array.isArray(this.itensGrimorio)
                ? this.itensGrimorio.map((item) => item?.magia?.escola || item?.magia_escola || item?.escola || '')
                : [])
            .concat(Array.isArray(this.catalogoClasse)
                ? this.catalogoClasse.map((magia) => magia?.escola || '')
                : []);

        origens.forEach((valor) => {
            const escola = this._normalizarEscola(valor);
            if (escola) escolas.add(escola);
        });

        const escolasOrdenadas = [
            ...ESCOLAS_ORDEM.filter((escola) => escolas.has(escola)),
            ...[...escolas]
                .filter((escola) => !ESCOLAS_ORDEM.includes(escola))
                .sort((a, b) => a.localeCompare(b, 'pt-BR')),
        ];

        if (this.escolaAtiva !== 'todas' && !escolas.has(this.escolaAtiva)) {
            this.escolaAtiva = 'todas';
        }

        container.innerHTML = `
            <button class="grimorio-escola-btn ${this.escolaAtiva === 'todas' ? 'ativo' : ''}" data-escola="todas">Todas</button>
            ${escolasOrdenadas.map((escola) => `
                <button class="grimorio-escola-btn ${this.escolaAtiva === escola ? 'ativo' : ''}" data-escola="${escapeHtml(escola)}">${escapeHtml(escola)}</button>
            `).join('')}
        `;

        container.querySelectorAll('.grimorio-escola-btn').forEach((button) => {
            button.addEventListener('click', () => {
                this.escolaAtiva = button.dataset.escola;
                this.filtrar();
                this._renderizarFiltroEscolas();
            });
        });
    }

    _configurarFiltros() {
        this._bindNiveis();
        this._bindFavoritas();
        this._bindPreparadas();
        this._bindComponente();
        this._bindDescansoLongo();
        this._bindAdicionarMagia();
        this._bindFiltrosAdicionar();
        this._bindAtalhosAdicionar();
        this._bindTrocaMagia();
        this._bindNotificacoes();
    }

    _bindDescansoLongo() {
        const btnDescanso = document.getElementById('btnDescansoLongoGrimorio');
        if (!btnDescanso) return;

        const clone = btnDescanso.cloneNode(true);
        btnDescanso.parentNode.replaceChild(clone, btnDescanso);
        clone.addEventListener('click', () => {
            this._confirmarDescansoLongo();
        });
    }

    _bindNotificacoes() {
        const btnAbrir = document.getElementById('btnNotificacoesGrimorio');
        const painel = document.getElementById('grimorioPainelNotificacoes');
        const btnFechar = document.getElementById('btnFecharPainelNotificacoes');

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
                this._definirPainelAdicionarVisivel(false);
                painel.classList.toggle('show');
            });
        }

        if (btnFechar && painel) {
            const cloneFechar = btnFechar.cloneNode(true);
            btnFechar.parentNode.replaceChild(cloneFechar, btnFechar);
            cloneFechar.addEventListener('click', () => {
                painel.classList.remove('show');
            });
        }
    }

    _bindNiveis() {
        document.querySelectorAll('.grimorio-nivel-btn').forEach((btn) => {
            const clone = btn.cloneNode(true);
            btn.parentNode.replaceChild(clone, btn);
            clone.addEventListener('click', () => {
                this.nivelAtivo = clone.dataset.nivel;
                document.querySelectorAll('.grimorio-nivel-btn').forEach((item) => item.classList.remove('ativo'));
                clone.classList.add('ativo');
                this.filtrar();
            });
        });
    }

    _bindFavoritas() {
        const btn = document.getElementById('btnFiltroFavoritas');
        if (!btn) return;

        const clone = btn.cloneNode(true);
        btn.parentNode.replaceChild(clone, btn);
        clone.classList.toggle('ativo', this.favoritasApenas);
        clone.addEventListener('click', () => {
            this.favoritasApenas = !this.favoritasApenas;
            clone.classList.toggle('ativo', this.favoritasApenas);
            this.filtrar();
        });
    }

    _bindPreparadas() {
        const btn = document.getElementById('btnFiltroPreparagas');
        if (!btn) return;

        // Mostra o botão apenas para classes que preparam magias (não-espontâneas)
        const classeNorm = String(this._normalizarClasse(this.classeAtiva) || '')
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
        const classesQuePrep = ['clerigo', 'mago', 'druida', 'ranger', 'paladino'];
        btn.style.display = classesQuePrep.includes(classeNorm) ? '' : 'none';

        const clone = btn.cloneNode(true);
        btn.parentNode.replaceChild(clone, btn);
        clone.classList.toggle('ativo', this.preparadasApenas);
        clone.addEventListener('click', () => {
            this.preparadasApenas = !this.preparadasApenas;
            clone.classList.toggle('ativo', this.preparadasApenas);
            this.filtrar();
        });
    }

    _bindComponente() {
        const select = document.getElementById('grimorioFiltroComponente');
        if (!select) return;

        select.value = this.componenteAtivo;
        const clone = select.cloneNode(true);
        select.parentNode.replaceChild(clone, select);
        clone.value = this.componenteAtivo;

        clone.addEventListener('change', () => {
            this.componenteAtivo = clone.value;
            this.filtrar();
        });
    }

    _bindAdicionarMagia() {
        const btnAbrir = document.getElementById('btnAdicionarMagiaGrimorio');
        const btnFechar = document.getElementById('btnFecharPainelAdicionar');
        const painel = document.getElementById('grimorioPainelAdicionar');

        if (btnAbrir) {
            const permiteAdicionar = this._classePermiteGerenciarConhecidas();
            const semAcesso = !permiteAdicionar || this._classeSemAcessoMagias();
            btnAbrir.disabled = semAcesso;
            btnAbrir.title = !permiteAdicionar
                ? 'Esta classe recebe magias automaticamente — sem seleção manual'
                : (this._classeSemAcessoMagias()
                    ? 'Disponivel apenas a partir do nivel 4 para Ranger/Paladino'
                    : 'Adicionar magia conhecida');
            btnAbrir.style.opacity = semAcesso ? '0.5' : '1';
            btnAbrir.style.cursor = semAcesso ? 'not-allowed' : 'pointer';
        }

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
                if (!this._classePermiteGerenciarConhecidas()) {
                    this._mostrarToast('Esta classe recebe magias automaticamente — sem seleção manual.', 'info');
                    return;
                }
                if (this._classeSemAcessoMagias()) {
                    this._mostrarToast('Ranger e Paladino só recebem magias a partir do nível 4.', 'info');
                    return;
                }
                this._definirPainelAdicionarVisivel(!painel.classList.contains('show'));
            });
        }

        if (btnFechar && painel) {
            const cloneFechar = btnFechar.cloneNode(true);
            btnFechar.parentNode.replaceChild(cloneFechar, btnFechar);
            cloneFechar.addEventListener('click', () => {
                this._definirPainelAdicionarVisivel(false);
            });
        }
    }

    _bindTrocaMagia() {
        const btnAbrir = document.getElementById('btnTrocarMagiaGrimorio');
        const btnFechar = document.getElementById('btnFecharPainelTroca');
        const painel = document.getElementById('grimorioPainelTroca');
        const btnConfirmar = document.getElementById('btnConfirmarTrocaMagia');

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
                this._definirPainelAdicionarVisivel(false);
                painel.classList.toggle('show');
            });
        }

        if (btnFechar && painel) {
            const cloneFechar = btnFechar.cloneNode(true);
            btnFechar.parentNode.replaceChild(cloneFechar, btnFechar);
            cloneFechar.addEventListener('click', () => {
                painel.classList.remove('show');
            });
        }

        if (btnConfirmar) {
            const cloneConfirmar = btnConfirmar.cloneNode(true);
            btnConfirmar.parentNode.replaceChild(cloneConfirmar, btnConfirmar);
            cloneConfirmar.addEventListener('click', async () => {
                const removida = Number(document.getElementById('grimorioTrocaRemovida')?.value || 0);
                const adicionada = Number(document.getElementById('grimorioTrocaAdicionada')?.value || 0);
                if (!removida || !adicionada) {
                    this._mostrarToast('Selecione magia removida e magia adicionada.', 'erro');
                    return;
                }
                if (removida === adicionada) {
                    this._mostrarToast('A magia removida deve ser diferente da adicionada.', 'erro');
                    return;
                }

                try {
                    await this.grimorioService.trocar(this.combatente.id, {
                        classe: this.classeAtiva,
                        magia_removida_id: removida,
                        magia_adicionada_id: adicionada,
                    });
                    this._mostrarToast('Troca de magia realizada com sucesso.', 'sucesso');
                    await this._recarregarDados();
                } catch (error) {
                    this._mostrarToast(error.message || 'Não foi possível realizar a troca.', 'erro');
                }
            });
        }
    }

    _bindFiltrosAdicionar() {
        const filtros = [
            { id: 'grimorioAdicionarBusca', evento: 'input' },
            { id: 'grimorioAdicionarEscola', evento: 'change' },
            { id: 'grimorioAdicionarNivel', evento: 'change' },
            { id: 'grimorioAdicionarComponente', evento: 'change' },
        ];

        filtros.forEach(({ id, evento }) => {
            const el = document.getElementById(id);
            if (!el) return;
            const clone = el.cloneNode(true);
            el.parentNode.replaceChild(clone, el);
            clone.addEventListener(evento, () => this._renderizarPainelAdicionar());
        });
    }

    _bindAtalhosAdicionar() {
        if (this._onAdicionarKeydown) {
            document.removeEventListener('keydown', this._onAdicionarKeydown);
        }

        this._onAdicionarKeydown = (event) => {
            const painel = document.getElementById('grimorioPainelAdicionar');
            if (!painel || !painel.classList.contains('show')) return;

            const tecla = event.key;
            const teclasNavegacao = ['ArrowDown', 'ArrowUp', 'PageDown', 'PageUp', 'Home', 'End', 'Enter', 'Escape'];
            if (!teclasNavegacao.includes(tecla)) return;

            const alvo = event.target;
            const digitando = alvo
                && (alvo.tagName === 'INPUT'
                    || alvo.tagName === 'TEXTAREA'
                    || alvo.tagName === 'SELECT'
                    || alvo.isContentEditable);
            if (digitando) return;

            const disponiveis = Array.isArray(this.magiasDisponiveisAdicionar)
                ? this.magiasDisponiveisAdicionar
                : [];

            if (tecla === 'Escape') {
                event.preventDefault();
                this._definirPainelAdicionarVisivel(false);
                return;
            }

            if (!disponiveis.length) return;

            const indiceAtual = Math.max(
                0,
                disponiveis.findIndex((magia) => Number(magia.id) === Number(this.magiaAdicionarSelecionadaId))
            );

            if (tecla === 'Enter') {
                event.preventDefault();
                const atual = disponiveis[indiceAtual];
                if (atual) {
                    this._adicionarMagia(Number(atual.id));
                }
                return;
            }

            event.preventDefault();
            let proximoIndice = indiceAtual;

            if (tecla === 'Home') proximoIndice = 0;
            else if (tecla === 'End') proximoIndice = disponiveis.length - 1;
            else {
                const delta = tecla === 'ArrowDown' || tecla === 'PageDown' ? 1 : -1;
                proximoIndice = (indiceAtual + delta + disponiveis.length) % disponiveis.length;
            }

            const proxima = disponiveis[proximoIndice];
            if (!proxima) return;

            this.magiaAdicionarSelecionadaId = Number(proxima.id);
            this._atualizarSelecaoAdicionarUI(this.magiaAdicionarSelecionadaId);
            this._renderizarPreviewAdicionar(disponiveis, this.magiaAdicionarSelecionadaId);
            this._atualizarResumoAdicionar(disponiveis, this.magiaAdicionarSelecionadaId);

            const itemSelecionado = document.querySelector(`.grimorio-add-btn-selecionar[data-id="${Number(proxima.id)}"]`);
            itemSelecionado?.closest('.grimorio-add-item')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        };

        document.addEventListener('keydown', this._onAdicionarKeydown);
    }

    _atualizarResumoAdicionar(disponiveis, magiaIdSelecionada) {
        const resumo = document.getElementById('grimorioAdicionarResumo');
        if (!resumo) return;

        const lista = Array.isArray(disponiveis) ? disponiveis : [];
        const selecionada = lista.find((magia) => Number(magia.id) === Number(magiaIdSelecionada));

        if (!lista.length) {
            resumo.textContent = '0 resultados';
            return;
        }

        if (!selecionada) {
            resumo.textContent = `${lista.length} resultado(s)`;
            return;
        }

        const posicao = lista.findIndex((magia) => Number(magia.id) === Number(magiaIdSelecionada));
        const indiceHumano = posicao >= 0 ? posicao + 1 : 1;
        resumo.textContent = `${lista.length} resultado(s) • ${indiceHumano}/${lista.length} selecionada: ${selecionada.nome || 'Magia'}`;
    }

    _normalizarTextoBasico(valor) {
        return String(valor || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    }

    _feedbackErroAdicionarPorMensagem(mensagem) {
        const texto = String(mensagem || '').trim();
        const normalizado = this._normalizarTextoBasico(texto);

        if (!texto) {
            return {
                tipo: 'erro',
                titulo: 'Falha ao adicionar magia',
                detalhe: 'Nao foi possivel concluir a inclusao desta magia no grimorio.',
            };
        }

        if (normalizado.includes('alinhamento')) {
            return {
                tipo: 'bloqueio',
                titulo: 'Bloqueada por alinhamento',
                detalhe: 'Esta magia esta vinculada a um dominio que conflita com o alinhamento atual do personagem.',
            };
        }

        if (normalizado.includes('dominio oposto')) {
            return {
                tipo: 'bloqueio',
                titulo: 'Bloqueada por dominio oposto',
                detalhe: 'Esta magia esta associada a dominio oposto a um dos dominios selecionados pelo clerigo.',
            };
        }

        if (normalizado.includes('dominio') && normalizado.includes('incompativel')) {
            return {
                tipo: 'bloqueio',
                titulo: 'Dominio nao permitido',
                detalhe: 'Esta magia exige dominio especifico e o personagem nao possui o dominio necessario.',
            };
        }

        return {
            tipo: 'erro',
            titulo: 'Falha ao adicionar magia',
            detalhe: texto,
        };
    }

    _renderizarPainelAdicionar() {
        const lista = document.getElementById('grimorioAdicionarLista');
        const preview = document.getElementById('grimorioAdicionarPreview');
        if (!lista || !preview) return;

        if (!this._classePermiteGerenciarConhecidas()) {
            this.magiasDisponiveisAdicionar = [];
            this._atualizarResumoAdicionar([], null);
            lista.innerHTML = '<div class="grimorio-vazio">Esta classe recebe magias automaticamente. Apenas Mago, Bardo e Feiticeiro selecionam magias manualmente.</div>';
            preview.innerHTML = '<div class="grimorio-historico-vazio">As demais classes recebem automaticamente todas as magias do nível ao subir de nível.</div>';
            return;
        }

        if (this._classeSemAcessoMagias()) {
            this.magiasDisponiveisAdicionar = [];
            this._atualizarResumoAdicionar([], null);
            lista.innerHTML = '<div class="grimorio-vazio">Ranger e Paladino so podem adicionar magias a partir do nivel 4.</div>';
            preview.innerHTML = '<div class="grimorio-historico-vazio">Sem acesso a magias nesta classe/nível.</div>';
            return;
        }

        const escolaSelect = document.getElementById('grimorioAdicionarEscola');
        if (escolaSelect) {
            const escolaAtual = escolaSelect.value || 'todas';
            const escolas = [...new Set(this.catalogoClasse
                .map((magia) => this._normalizarEscola(magia.escola || ''))
                .filter(Boolean))]
                .sort((a, b) => a.localeCompare(b, 'pt-BR'));
            escolaSelect.innerHTML = ['<option value="todas">Todas</option>']
                .concat(escolas.map((escola) => `<option value="${escapeHtml(escola)}">${escapeHtml(escola)}</option>`))
                .join('');
            escolaSelect.value = escolas.includes(escolaAtual) ? escolaAtual : 'todas';
        }

        const termo = (document.getElementById('grimorioAdicionarBusca')?.value || '').toLowerCase().trim();
        const escolaFiltro = document.getElementById('grimorioAdicionarEscola')?.value || 'todas';
        const nivelFiltro = document.getElementById('grimorioAdicionarNivel')?.value || 'todos';
        const componenteFiltro = document.getElementById('grimorioAdicionarComponente')?.value || 'todos';
        const idsExistentes = new Set(this.itensGrimorio.map((item) => Number(item.magia_id)));
        const maxNivelConjuravel = this._maxNivelConjuravel(this.classeAtiva, Number(this.combatente?.nivel || 1));

        let disponiveis = this.catalogoClasse.filter((magia) => !idsExistentes.has(Number(magia.id)));
        disponiveis = disponiveis.filter((magia) => Number(magia.nivel || 0) <= maxNivelConjuravel);

        disponiveis = disponiveis.filter((magia) => {
            const escolaNormalizada = this._normalizarEscola(magia.escola || '');
            const matchEscola = escolaFiltro === 'todas' || escolaNormalizada === escolaFiltro;
            const matchNivel = nivelFiltro === 'todos' || String(Number(magia.nivel || 0)) === String(nivelFiltro);
            const componentes = this._extrairComponentes(magia.componentes || '');
            const matchComponente = componenteFiltro === 'todos' || componentes.has(String(componenteFiltro).toUpperCase());

            if (!termo) return matchEscola && matchNivel && matchComponente;

            const alvo = [magia.nome, magia.escola, magia.componentes, magia.descricao]
                .filter(Boolean)
                .join(' ')
                .toLowerCase();
            return matchEscola && matchNivel && matchComponente && alvo.includes(termo);
        });

        if (disponiveis.length === 0) {
            this.magiasDisponiveisAdicionar = [];
            this._atualizarResumoAdicionar([], null);
            lista.innerHTML = '<div class="grimorio-vazio">Nenhuma magia encontrada com os filtros atuais.</div>';
            preview.innerHTML = '<div class="grimorio-historico-vazio">Nenhuma magia corresponde aos filtros selecionados.</div>';
            return;
        }

        this.magiasDisponiveisAdicionar = disponiveis;

        if (!disponiveis.some((magia) => Number(magia.id) === Number(this.magiaAdicionarSelecionadaId))) {
            this.magiaAdicionarSelecionadaId = Number(disponiveis[0].id);
        }

        lista.innerHTML = disponiveis.map((magia) => `
            <div class="grimorio-add-item">
                <div class="grimorio-add-info">
                    <strong>${escapeHtml(magia.nome)}</strong>
                    <span>Nivel ${Number(magia.nivel || 0)} - ${escapeHtml(this._normalizarEscola(magia.escola || ''))}</span>
                </div>
                <button class="grimorio-add-btn grimorio-add-btn-selecionar" data-id="${magia.id}">Preview</button>
            </div>
        `).join('');

        lista.querySelectorAll('.grimorio-add-btn').forEach((button) => {
            button.addEventListener('click', () => {
                const magiaId = Number(button.dataset.id);
                this.magiaAdicionarSelecionadaId = magiaId;
                this._atualizarSelecaoAdicionarUI(magiaId);
                this._renderizarPreviewAdicionar(disponiveis, magiaId);
                this._atualizarResumoAdicionar(disponiveis, magiaId);
            });
        });

        this._atualizarSelecaoAdicionarUI(this.magiaAdicionarSelecionadaId);
        this._renderizarPreviewAdicionar(disponiveis, this.magiaAdicionarSelecionadaId);
        this._atualizarResumoAdicionar(disponiveis, this.magiaAdicionarSelecionadaId);
    }

    _atualizarSelecaoAdicionarUI(magiaId) {
        const lista = document.getElementById('grimorioAdicionarLista');
        if (!lista) return;

        lista.querySelectorAll('.grimorio-add-item').forEach((item) => {
            item.classList.remove('is-selected');
        });

        lista.querySelectorAll('.grimorio-add-btn-selecionar').forEach((button) => {
            button.classList.remove('ativo');
            const corresponde = Number(button.dataset.id) === Number(magiaId);
            button.setAttribute('aria-pressed', corresponde ? 'true' : 'false');
            if (corresponde) {
                button.classList.add('ativo');
                button.closest('.grimorio-add-item')?.classList.add('is-selected');
            }
        });
    }

    _renderizarPreviewAdicionar(disponiveis, magiaId) {
        const preview = document.getElementById('grimorioAdicionarPreview');
        if (!preview) return;

        const magia = (disponiveis || []).find((item) => Number(item.id) === Number(magiaId));
        if (!magia) {
            preview.innerHTML = '<div class="grimorio-historico-vazio">Selecione uma magia para visualizar os detalhes antes de adicionar ao grimorio.</div>';
            return;
        }

        const feedback = this._feedbackAdicionar && Number(this._feedbackAdicionar.magiaId) === Number(magia.id)
            ? this._feedbackAdicionar
            : null;
        const feedbackHtml = feedback
            ? `
                <div class="grimorio-add-feedback grimorio-add-feedback--${escapeHtml(feedback.tipo || 'erro')}">
                    <strong>${escapeHtml(feedback.titulo || 'Falha ao adicionar')}</strong>
                    <p>${escapeHtml(feedback.detalhe || '')}</p>
                </div>
            `
            : '';

        preview.innerHTML = `
            <div class="grimorio-add-preview-titulo">${escapeHtml(magia.nome || 'Magia')}</div>
            ${feedbackHtml}
            <div class="grimorio-add-preview-grid">
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Nivel</span><span class="grimorio-add-preview-valor">${Number(magia.nivel || 0)}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Escola</span><span class="grimorio-add-preview-valor">${escapeHtml(this._normalizarEscola(magia.escola || '-'))}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Componentes</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.componentes || '-')}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Conjuracao</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Alcance</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.alcance || '-')}</span></div>
            </div>
            <div class="grimorio-add-preview-descricao">${escapeHtml((magia.descricao || 'Sem descrição.').slice(0, 320))}</div>
            <button class="grimorio-add-btn grimorio-add-preview-acao" id="btnConfirmarAdicionarPreview">Adicionar magia conhecida</button>
            <div class="grimorio-add-preview-hint">Atalhos: setas navegam, PgUp/PgDn alternam, Home/End pulam extremos, Enter adiciona a magia conhecida.</div>
        `;

        preview.querySelector('#btnConfirmarAdicionarPreview')?.addEventListener('click', async () => {
            await this._adicionarMagia(Number(magia.id));
        });
    }

    _extrairComponentes(valor) {
        const partes = String(valor || '')
            .toUpperCase()
            .split(/[^A-Z]+/)
            .map((item) => item.trim())
            .filter(Boolean);
        return new Set(partes);
    }

    _renderizarPainelTroca() {
        const selectRemovida = document.getElementById('grimorioTrocaRemovida');
        const selectAdicionada = document.getElementById('grimorioTrocaAdicionada');
        if (!selectRemovida || !selectAdicionada) return;

        const itensClasse = this.itensGrimorio;

        selectRemovida.innerHTML = ['<option value="">Selecione a magia removida</option>']
            .concat(itensClasse.map((item) => `
                <option value="${item.magia_id}">${escapeHtml(item.magia?.nome || `Magia ${item.magia_id}`)} (N${Number(item.magia?.nivel || 0)})</option>
            `))
            .join('');

        const idsExistentes = new Set(itensClasse.map((item) => Number(item.magia_id)));
        const maxNivelConjuravel = this._maxNivelConjuravel(this.classeAtiva, Number(this.combatente?.nivel || 1));
        const disponiveis = this.catalogoClasse
            .filter((magia) => !idsExistentes.has(Number(magia.id)))
            .filter((magia) => Number(magia.nivel || 0) <= maxNivelConjuravel);
        selectAdicionada.innerHTML = ['<option value="">Selecione a magia adicionada</option>']
            .concat(disponiveis.map((magia) => `
                <option value="${magia.id}">${escapeHtml(magia.nome)} (N${Number(magia.nivel || 0)})</option>
            `))
            .join('');
    }

    _maxNivelConjuravel(classe, nivelPersonagem) {
        const classeNorm = String(this._normalizarClasse(classe) || '').toLowerCase();
        const nivel = Math.max(1, Number(nivelPersonagem || 1));

        if (['clerigo', 'druida', 'mago'].includes(classeNorm)) {
            return Math.min(9, Math.floor((nivel + 1) / 2));
        }

        if (['ranger', 'paladino'].includes(classeNorm)) {
            if (nivel < 4) return 0;
            return Math.min(4, Math.floor((nivel - 1) / 3));
        }

        if (classeNorm === 'feiticeiro') {
            const progressao = {
                1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 10: 5,
                11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9, 18: 9, 19: 9, 20: 9,
            };
            return progressao[Math.min(20, nivel)] || 1;
        }

        if (classeNorm === 'bardo') {
            const progressao = {
                1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 3, 9: 4, 10: 4,
                11: 4, 12: 5, 13: 5, 14: 5, 15: 6, 16: 6, 17: 6, 18: 6, 19: 6, 20: 6,
            };
            return progressao[Math.min(20, nivel)] || 0;
        }

        return 0;
    }

    async _carregarHistoricoTrocas() {
        try {
            this.historicoTrocas = await this.grimorioService.listarHistoricoTroca(this.combatente.id, {
                classe: this.classeAtiva,
                limit: 10,
            });
        } catch (_error) {
            this.historicoTrocas = [];
        }
    }

    _renderizarHistoricoTrocas() {
        const el = document.getElementById('grimorioHistoricoTroca');
        if (!el) return;
        const classeEspontanea = this._classeEhEspontanea();

        if (!this.historicoTrocas.length) {
            el.innerHTML = classeEspontanea
                ? '<div class="grimorio-historico-vazio">Sem historico de troca de magias conhecidas para esta classe.</div>'
                : '<div class="grimorio-historico-vazio">Sem historico de troca para esta classe.</div>';
            return;
        }

        el.innerHTML = this.historicoTrocas.map((item) => {
            const removida = item.magia_removida_nome || `#${item.magia_removida_id}`;
            const adicionada = item.magia_adicionada_nome || `#${item.magia_adicionada_id}`;
            if (classeEspontanea) {
                return `<div class="grimorio-historico-item">Nvl ${item.nivel_personagem}: troca de magia conhecida ${escapeHtml(removida)} -> ${escapeHtml(adicionada)}</div>`;
            }
            return `<div class="grimorio-historico-item">Nvl ${item.nivel_personagem}: ${escapeHtml(removida)} -> ${escapeHtml(adicionada)}</div>`;
        }).join('');
    }

    _renderizarNotificacoes() {
        const container = document.getElementById('grimorioListaNotificacoes');
        const badge = document.getElementById('grimorioNotificacoesBadge');
        if (!container) return;

        const naoLidas = this.notificacoes.filter((item) => !item.lida).length;
        if (badge) {
            badge.style.display = naoLidas > 0 ? 'inline-flex' : 'none';
            badge.textContent = `${naoLidas}`;
        }

        if (!this.notificacoes.length) {
            container.innerHTML = '<div class="grimorio-historico-vazio">Sem notificacoes para esta classe.</div>';
            return;
        }

        container.innerHTML = this.notificacoes.map((item) => {
            const classeLida = item.lida ? 'lida' : 'nao-lida';
            const texto = this._textoNotificacao(item);
            const tipoClasse = this._classeNotificacao(item);
            return `
                <div class="grimorio-notificacao-item ${classeLida} ${tipoClasse}" data-id="${item.id}">
                    <div class="grimorio-notificacao-topo">
                        <strong>${escapeHtml(item.tipo || 'NOTIFICACAO')}</strong>
                        <span>${new Date(item.criada_em).toLocaleDateString('pt-BR')}</span>
                    </div>
                    <p>${escapeHtml(texto)}</p>
                    <div class="grimorio-notificacao-acoes">
                        <button class="grimorio-notif-lida" data-id="${item.id}">${item.lida ? 'Marcar não lida' : 'Marcar lida'}</button>
                        <button class="grimorio-notif-descartar" data-id="${item.id}">Descartar</button>
                    </div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.grimorio-notif-lida').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const id = Number(btn.dataset.id);
                const alvo = this.notificacoes.find((item) => Number(item.id) === id);
                if (!alvo) return;
                try {
                    await this.grimorioService.marcarNotificacaoLida(this.combatente.id, id, !alvo.lida);
                    alvo.lida = !alvo.lida;
                    this._renderizarNotificacoes();
                    this._atualizarBadgeTrocaDisponivel();
                } catch (error) {
                    this._mostrarToast(error.message || 'Não foi possível atualizar a notificação.', 'erro');
                }
            });
        });

        container.querySelectorAll('.grimorio-notif-descartar').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const id = Number(btn.dataset.id);
                try {
                    await this.grimorioService.descartarNotificacao(this.combatente.id, id);
                    this.notificacoes = this.notificacoes.filter((item) => Number(item.id) !== id);
                    this._renderizarNotificacoes();
                    this._atualizarBadgeTrocaDisponivel();
                } catch (error) {
                    this._mostrarToast(error.message || 'Não foi possível descartar a notificação.', 'erro');
                }
            });
        });
    }

    _classeNotificacao(item) {
        if (item?.tipo === 'CONVERSAO_DIVINA') return 'grimorio-notificacao-auto';
        if (item?.tipo === 'MAGIAS_ADICIONADAS') return 'grimorio-notificacao-auto';
        if (item?.tipo === 'SEM_MAGIAS_ATE_NIVEL_4') return 'grimorio-notificacao-bloqueio';
        return '';
    }

    _textoNotificacao(item) {
        const dados = item.dados || {};
        const classeEspontanea = this._classeEhEspontanea();
        if (item.tipo === 'SEM_MAGIAS_ATE_NIVEL_4') {
            return 'Ranger e Paladino so recebem magias quando alcancam o nivel 4.';
        }
        if (item.tipo === 'TROCA_DISPONIVEL') {
            return classeEspontanea
                ? 'Uma troca de magia conhecida esta disponivel para esta classe.'
                : 'Uma troca de magia está disponível para esta classe.';
        }
        if (item.tipo === 'SELECAO_PENDENTE') {
            const qtd = Number(dados.quantidade_pendente || 0);
            const porNivel = dados.por_nivel && typeof dados.por_nivel === 'object' ? dados.por_nivel : {};
            const niveis = Object.entries(porNivel)
                .map(([nivel, quantidade]) => ({ nivel: Number(nivel), quantidade: Number(quantidade || 0) }))
                .filter((itemNivel) => Number.isFinite(itemNivel.nivel) && itemNivel.quantidade > 0)
                .sort((a, b) => a.nivel - b.nivel)
                .map((itemNivel) => `${itemNivel.quantidade} no nível ${itemNivel.nivel}`)
                .join(', ');

            if (niveis) {
                return classeEspontanea
                    ? `Você possui ${qtd} magia(s) conhecida(s) disponível(is) para seleção (${niveis}).`
                    : `Você possui ${qtd} magia(s) disponível(is) para seleção (${niveis}).`;
            }

            return classeEspontanea
                ? `Você possui ${qtd} magia(s) conhecida(s) disponível(is) para seleção no catálogo.`
                : `Você possui ${qtd} magia(s) disponível(is) para seleção no catálogo.`;
        }
        if (item.tipo === 'MAGIAS_ADICIONADAS') {
            const qtd = Number(dados.quantidade || 0);
            const nomes = Array.isArray(dados.magias_nomes)
                ? dados.magias_nomes.map((nome) => String(nome || '').trim()).filter(Boolean)
                : [];
            if (nomes.length > 0) {
                const resumo = nomes.slice(0, 4).join(', ');
                const sufixo = nomes.length > 4 ? ` e mais ${nomes.length - 4}` : '';
                return classeEspontanea
                    ? `${qtd} nova(s) magia(s) conhecida(s) foram adicionadas ao grimório: ${resumo}${sufixo}.`
                    : `${qtd} nova(s) magia(s) foram adicionadas automaticamente ao grimório: ${resumo}${sufixo}.`;
            }
            return classeEspontanea
                ? `${qtd} nova(s) magia(s) conhecida(s) foram adicionadas ao grimório.`
                : `${qtd} nova(s) magia(s) foram adicionadas automaticamente ao grimório.`;
        }
        if (item.tipo === 'CONVERSAO_DIVINA') {
            const modo = String(dados.modo || '').toUpperCase();
            const divindade = String(dados.divindade || '').trim();
            const alinhamento = String(dados.alinhamento || '').trim();

            if (modo === 'CURAR_OBRIGATORIO') {
                return divindade
                    ? `Conversão divina: este clérigo deve converter para Curar (${divindade}).`
                    : 'Conversão divina: este clérigo deve converter para Curar.';
            }
            if (modo === 'INFLIGIR_OBRIGATORIO') {
                return divindade
                    ? `Conversão divina: este clérigo deve converter para Infligir (${divindade}).`
                    : 'Conversão divina: este clérigo deve converter para Infligir.';
            }

            return alinhamento
                ? `Conversão divina: este clérigo pode escolher Curar ou Infligir (${alinhamento}).`
                : 'Conversão divina: este clérigo pode escolher Curar ou Infligir.';
        }
        return 'Notificação do grimório.';
    }

    _atualizarBadgeTrocaDisponivel() {
        const badge = document.getElementById('grimorioTrocaBadge');
        const btnTroca = document.getElementById('btnTrocarMagiaGrimorio');
        const painelTroca = document.getElementById('grimorioPainelTroca');

        const classe = this._normalizarClasse(this.classeAtiva);
        const nivel = Number(this.combatente?.nivel || 1);
        const classeSuportaTroca = classe === 'Feiticeiro' || classe === 'Bardo';
        const disponivelPorRegra = (classe === 'Feiticeiro' && nivel >= 4 && nivel % 2 === 0)
            || (classe === 'Bardo' && [5, 8, 11, 14, 17, 20].includes(nivel));
        const disponivelPorNotificacao = this.notificacoes.some(
            (item) => item.tipo === 'TROCA_DISPONIVEL' && !item.lida
        );
        const disponivel = disponivelPorRegra || disponivelPorNotificacao;

        if (btnTroca) btnTroca.style.display = classeSuportaTroca ? 'inline-flex' : 'none';
        if (painelTroca && !classeSuportaTroca) painelTroca.classList.remove('show');
        if (badge) badge.style.display = disponivel ? 'inline-flex' : 'none';
    }

    _renderizarLista() {
        const lista = document.getElementById('grimorioLista');
        if (!lista) return;

        this._renderizarAvisoClasse();

        const classeClerigo = this._classeAtivaEhClerigo();
        const itensDominio = classeClerigo
            ? this.itensFiltrados.filter((item) => this._ehMagiaDominio(item))
            : [];
        const itensPadrao = classeClerigo
            ? this.itensFiltrados.filter((item) => !this._ehMagiaDominio(item))
            : this.itensFiltrados;

        if (itensDominio.length === 0 && itensPadrao.length === 0) {
            if (this._classeSemAcessoMagias()) {
                lista.innerHTML = '<div class="grimorio-vazio">Grimório acessível, mas sem magias: Ranger e Paladino recebem magias a partir do nível 4.</div>';
                return;
            }
            if (this.itensGrimorio.length === 0) {
                if (this._classeEhEspontanea()) {
                    lista.innerHTML = '<div class="grimorio-vazio">Você ainda não selecionou magias conhecidas. Use o botão <strong>Adicionar magia conhecida</strong> para montar seu grimório.</div>';
                } else if (this._classePermiteGerenciarConhecidas()) {
                    lista.innerHTML = '<div class="grimorio-vazio">Seu grimório está vazio. Use o botão <strong>Adicionar magia conhecida</strong> para registrar as magias que seu personagem aprendeu.</div>';
                } else {
                    lista.innerHTML = '<div class="grimorio-vazio">Nenhuma magia encontrada com os filtros atuais.</div>';
                }
                return;
            }
            lista.innerHTML = '<div class="grimorio-vazio">Nenhuma magia encontrada com os filtros atuais.</div>';
            return;
        }

        const partes = [];
        if (classeClerigo && itensDominio.length > 0) {
            partes.push(`
                <div class="grimorio-grupo grimorio-grupo-dominio">
                    <div class="grimorio-grupo-titulo">Magias de Dominio <span class="grimorio-grupo-slots">${itensDominio.length} magia(s)</span></div>
                    ${this._renderizarCardsPorNivel(itensDominio)}
                </div>
            `);
        }

        if (itensPadrao.length > 0) {
            partes.push(this._renderizarGruposPorNivel(itensPadrao));
        }

        lista.innerHTML = partes.join('');

        lista.querySelectorAll('.grimorio-favorita-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                event.stopPropagation();
                const magiaId = Number(button.dataset.magiaId);
                await this._toggleFavorita(magiaId);
            });
        });

        lista.querySelectorAll('.grimorio-anotacao-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                event.stopPropagation();
                const magiaId = Number(button.dataset.magiaId);
                await this._editarAnotacoes(magiaId);
            });
        });

        lista.querySelectorAll('.grimorio-remover-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                event.stopPropagation();
                const magiaId = Number(button.dataset.magiaId);
                await this._removerMagia(magiaId);
            });
        });

        lista.querySelectorAll('.grimorio-expandir-btn').forEach((button) => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                this._toggleCard(Number(button.dataset.id));
            });
        });

        lista.querySelectorAll('.grimorio-preparo-step').forEach((button) => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                const magiaId = Number(button.dataset.magiaId);
                const delta = Number(button.dataset.delta || 0);
                const atual = this._lerQuantidadePreparacaoCard(magiaId);
                const input = document.querySelector(`.grimorio-preparo-input[data-magia-id="${magiaId}"]`);
                const novoValor = this._atualizarQuantidadePreparacaoRapida(magiaId, atual + delta);
                if (input) input.value = String(novoValor);
            });
        });

        lista.querySelectorAll('.grimorio-preparo-input').forEach((input) => {
            input.addEventListener('click', (event) => event.stopPropagation());
            input.addEventListener('input', (event) => {
                event.stopPropagation();
                const magiaId = Number(input.dataset.magiaId);
                input.value = String(this._atualizarQuantidadePreparacaoRapida(magiaId, input.value));
            });
        });

        lista.querySelectorAll('.grimorio-preparar-btn').forEach((button) => {
            button.addEventListener('click', async (event) => {
                event.stopPropagation();
                const magiaId = Number(button.dataset.magiaId);
                const quantidade = this._lerQuantidadePreparacaoCard(magiaId);
                await this._togglePreparada(magiaId, quantidade);
            });
        });

        lista.querySelectorAll('.grimorio-magia-card').forEach((card) => {
            card.addEventListener('click', (event) => {
                if (event.target.closest('.grimorio-acoes-card')) return;
                if (event.target.closest('.grimorio-expandir-btn')) return;
                if (event.target.closest('.grimorio-preparo-inline')) return;
                if (event.target.closest('.grimorio-preparar-btn')) return;
                this._abrirModalDetalhes(Number(card.dataset.id));
            });
        });
    }

    _renderizarGruposPorNivel(itens) {
        const grupos = new Map();
        itens.forEach((item) => {
            const nivel = Number(item.magia?.nivel || 0);
            if (!grupos.has(nivel)) grupos.set(nivel, []);
            grupos.get(nivel).push(item);
        });

        return [...grupos.keys()]
            .sort((a, b) => a - b)
            .map((nivel) => {
                const itensGrupo = grupos.get(nivel);
                return `
                    <div class="grimorio-grupo">
                        <div class="grimorio-grupo-titulo">Nivel ${nivel} <span class="grimorio-grupo-slots">${itensGrupo.length} magia(s)</span></div>
                        ${itensGrupo.map((item) => this._renderizarCard(item)).join('')}
                    </div>
                `;
            }).join('');
    }

    _renderizarCardsPorNivel(itens) {
        return [...itens]
            .sort((a, b) => Number(a.magia?.nivel || 0) - Number(b.magia?.nivel || 0))
            .map((item) => this._renderizarCard(item))
            .join('');
    }

    _classeAtivaEhClerigo() {
        const classe = String(this._normalizarClasse(this.classeAtiva) || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toLowerCase();
        return classe === 'clerigo';
    }

    _ehMagiaDominio(item) {
        return !!(item?.magia?.e_magia_dominio || item?.magia_e_magia_dominio);
    }

    _renderizarCard(item) {
        const magia = item.magia || {};
        const id = Number(item.magia_id);
        const aberta = this.cardsAbertos.has(id);
        const classeMago = this._normalizarClasse(this.classeAtiva) === 'Mago';
        const classeEspontanea = this._classeEhEspontanea(); // Bardo/Feiticeiro não preparam magias
        const itemPersistido = !item._catalogo_expandido;
        const escola = this._normalizarEscola(magia.escola || '');
        const magiaDominio = this._ehMagiaDominio(item);
        const dominios = String(magia.dominios || item.magia_dominios || '').trim();
        const preparo = this._obterInfoPreparacao(item);
        const origemLabel = item._catalogo_expandido ? 'DISPONIVEL_HOJE' : (item.origem || 'SELECAO_MANUAL');
        const quantidadeRapida = this._obterQuantidadePreparacaoRapida(id, preparo);
        const descricaoPreparacao = classeEspontanea
            ? 'Conjuracao espontanea: use os slots de magia na arena para controlar os usos do dia.'
            : (preparo.preparada
                ? `Preparada ${preparo.quantidadeAtual}x no nível ${preparo.nivelSlot}${preparo.usosRealizados ? ` • ${preparo.usosRealizados} usada(s)` : ''}`
                : (preparo.podePreparar ? `Slots livres: ${preparo.slot.disponivel}/${preparo.slot.total}` : 'Sem slot disponível para este nível'));
        const textoPreparar = preparo.preparada
            ? `✅ Preparada ×${preparo.quantidadeAtual}`
            : '🪄 Preparar hoje';
        const tituloPreparar = !preparo.temEspaco && !preparo.preparada
            ? 'Todos os slots deste nível já foram preenchidos'
            : (preparo.preparada
                ? 'Clique para ajustar ou remover a quantidade preparada'
                : `Marcar ${magia.nome || 'magia'} como preparada hoje`);

        const detalhes = `
            <div class="grimorio-card-detalhes ${aberta ? 'show' : ''}">
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Escola</span><span class="grimorio-detalhe-valor">${escapeHtml(escola || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Componentes</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.componentes || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Conjuracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Alcance</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.alcance || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Duracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.duracao || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Resistencia</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.teste_resistencia || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">${classeEspontanea ? 'Conjuracao' : 'Preparacao'}</span><span class="grimorio-detalhe-valor">${descricaoPreparacao}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Descricao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.descricao || '-')}</span></div>
                ${item.anotacoes ? `<div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Anotacoes</span><span class="grimorio-detalhe-valor">${escapeHtml(item.anotacoes)}</span></div>` : ''}
            </div>
        `;

        return `
            <article class="grimorio-magia-card ${item.favorita ? 'favorita' : ''} ${preparo.preparada ? 'preparada' : ''} ${preparo.usada ? 'ja-usada' : ''} ${(!preparo.temEspaco && !preparo.preparada) ? 'sem-slot' : ''}" data-id="${id}">
                <div class="grimorio-card-topo">
                    <div>
                        <span class="grimorio-card-nome ${preparo.preparada ? 'preparada-nome' : ''} ${preparo.usada ? 'usada-nome' : ''}">${escapeHtml(magia.nome || `Magia ${id}`)}</span>
                        <div class="grimorio-card-badges">
                            <span class="grimorio-badge grimorio-badge-escola">${escapeHtml(escola || 'Sem escola')}</span>
                            <span class="grimorio-badge grimorio-badge-comp">N${Number(magia.nivel || 0)} - ${escapeHtml(magia.componentes || '-')}</span>
                            <span class="grimorio-badge grimorio-badge-origem">${escapeHtml(String(origemLabel).replace(/_/g, ' '))}</span>
                            ${(!classeEspontanea && preparo.preparada) ? `<span class="grimorio-badge grimorio-badge-preparada">${preparo.usosRealizados ? `${preparo.usosRealizados}/${preparo.quantidadeAtual} usada(s)` : `Preparada ×${preparo.quantidadeAtual}`}</span>` : ''}
                            ${classeEspontanea ? '<span class="grimorio-badge grimorio-badge-conhecida">Magia conhecida</span>' : ''}
                            ${magiaDominio ? `<span class="grimorio-badge grimorio-badge-dominio">Dominio${dominios ? `: ${escapeHtml(dominios)}` : ''}</span>` : ''}
                        </div>
                    </div>
                    <div class="grimorio-acoes-card">
                        ${itemPersistido ? `<button class="grimorio-favorita-btn ${item.favorita ? 'ativa' : ''}" data-magia-id="${id}" title="Favoritar">★</button>` : ''}
                        ${itemPersistido ? `<button class="grimorio-anotacao-btn" data-magia-id="${id}" title="Anotacoes">✎</button>` : ''}
                        ${classeMago && itemPersistido ? `<button class="grimorio-remover-btn" data-magia-id="${id}" title="Remover">🗑</button>` : ''}
                    </div>
                </div>
                <div class="grimorio-card-meta" aria-label="Resumo rapido da magia">
                    <div class="grimorio-meta-item">
                        <span class="grimorio-meta-label">Conjuracao</span>
                        <span class="grimorio-meta-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span>
                    </div>
                    <div class="grimorio-meta-item">
                        <span class="grimorio-meta-label">Alcance</span>
                        <span class="grimorio-meta-valor">${escapeHtml(magia.alcance || '-')}</span>
                    </div>
                </div>
                <p class="grimorio-card-descricao">${escapeHtml((magia.descricao || '').slice(0, 200) || 'Sem descricao.')}</p>
                ${detalhes}
                <div class="grimorio-card-rodape">
                    <button class="grimorio-expandir-btn" data-id="${id}">${aberta ? '▲ Menos detalhes' : '▼ Ver detalhes'}</button>
                        ${!classeEspontanea ? `<div class="grimorio-rodape-direita">
                            <div class="grimorio-preparo-inline ${(!preparo.temEspaco && !preparo.preparada) ? 'is-disabled' : ''}" data-magia-id="${id}">
                                <span class="grimorio-preparo-inline-label">Qtd</span>
                                <button class="grimorio-preparo-step" type="button" data-magia-id="${id}" data-delta="-1" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>−</button>
                                <input class="grimorio-preparo-input" data-magia-id="${id}" type="number" min="${preparo.preparada ? 0 : (preparo.temEspaco ? 1 : 0)}" max="${Math.max(quantidadeRapida, preparo.quantidadeMaxima || 0)}" step="1" value="${quantidadeRapida}" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>
                                <button class="grimorio-preparo-step" type="button" data-magia-id="${id}" data-delta="1" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>+</button>
                                <span class="grimorio-preparo-inline-max">máx ${Math.max(quantidadeRapida, preparo.quantidadeMaxima || 0)}</span>
                            </div>
                            <button class="grimorio-preparar-btn ${preparo.preparada ? 'ativa' : ''}" data-magia-id="${id}" title="${escapeHtml(tituloPreparar)}" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>${textoPreparar}</button>
                            ${item.anotacoes ? '<span class="grimorio-preparada-badge">Com anotacoes</span>' : (item._catalogo_expandido ? '<span class="grimorio-preparada-badge">Disponível hoje</span>' : '')}
                        </div>` : ''}
                </div>
            </article>
        `;
    }

    async _adicionarMagia(magiaId) {
        if (this._adicionarMagiaEmAndamento) return;

        const agora = Date.now();
        if (agora - this._ultimoAdicionarAt < 400) return;

        this._adicionarMagiaEmAndamento = true;
        this._ultimoAdicionarAt = agora;
        try {
            await this.grimorioService.adicionar(this.combatente.id, {
                magia_id: magiaId,
                classe: this.classeAtiva,
                origem: 'SELECAO_MANUAL',
            });
            this._feedbackAdicionar = null;
            this._mostrarToast('Magia adicionada ao grimório.', 'sucesso');
            await this._recarregarDados();
        } catch (error) {
            const feedback = this._feedbackErroAdicionarPorMensagem(error.message || 'Não foi possível adicionar a magia.');
            this._feedbackAdicionar = {
                magiaId: Number(magiaId),
                ...feedback,
            };

            this._renderizarPreviewAdicionar(this.magiasDisponiveisAdicionar, magiaId);
            this._mostrarToast(error.message || 'Não foi possível adicionar a magia.', 'erro');
        } finally {
            this._adicionarMagiaEmAndamento = false;
        }
    }

    async _desmarcarMagiaPreparada(magiaId) {
        if (typeof this.magiaPreparadaService?.desmarcar === 'function') {
            return this.magiaPreparadaService.desmarcar(this.combatente.id, magiaId);
        }

        const res = await fetch(getApiUrl(`/magias-preparadas/${this.combatente.id}/${magiaId}`), {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${this.token}` },
        });

        if (!res.ok) {
            let detalhe = 'Não foi possível remover a magia das preparadas de hoje.';
            try {
                const data = await res.json();
                if (typeof data?.detail === 'string' && data.detail.trim()) {
                    detalhe = data.detail.trim();
                }
            } catch (_error) {
                // Mantém mensagem padrão.
            }
            throw new Error(detalhe);
        }

        return true;
    }

    async _prepararMagiaHoje(magiaId, nivelSlot, quantidade = 1) {
        const payload = {
            magia_id: magiaId,
            nivel_slot: nivelSlot,
            quantidade: Math.max(1, Number(quantidade || 1)),
            classe: this.classeAtiva,
        };

        if (typeof this.magiaPreparadaService?.preparar === 'function') {
            return this.magiaPreparadaService.preparar(this.combatente.id, payload);
        }

        const res = await fetch(getApiUrl(`/magias-preparadas/${this.combatente.id}`), {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            let detalhe = 'Não foi possível preparar a magia para hoje.';
            try {
                const data = await res.json();
                if (typeof data?.detail === 'string' && data.detail.trim()) {
                    detalhe = data.detail.trim();
                }
            } catch (_error) {
                // Mantém mensagem padrão.
            }
            throw new Error(detalhe);
        }

        return res.json();
    }

    async _togglePreparada(magiaId, quantidadeDesejada = null) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return;

        const preparo = this._obterInfoPreparacao(item);
        if (!preparo.podePreparar && !preparo.preparada) {
            this._mostrarToast('Esta magia não possui slot disponível para ser preparada hoje.', 'info');
            return;
        }

        if (!preparo.preparada && !preparo.temEspaco) {
            this._mostrarToast(`Todos os slots do nível ${preparo.nivelSlot} já foram preenchidos.`, 'info');
            return;
        }

        const usandoQuantidadeCustomizada = quantidadeDesejada !== null && quantidadeDesejada !== undefined;
        let quantidadeFinal = usandoQuantidadeCustomizada
            ? Math.max(0, Number(quantidadeDesejada || 0))
            : (preparo.preparada ? 0 : 1);

        if (usandoQuantidadeCustomizada && quantidadeFinal > preparo.quantidadeMaxima) {
            quantidadeFinal = preparo.quantidadeMaxima;
            this._mostrarToast(`Limite ajustado para ${preparo.quantidadeMaxima} preparo(s) neste nível.`, 'info');
        }

        try {
            if (quantidadeFinal <= 0) {
                if (!preparo.preparada) {
                    this._mostrarToast('Informe ao menos 1 preparo para esta magia.', 'info');
                    return;
                }
                await this._desmarcarMagiaPreparada(magiaId);
                this._mostrarToast('Magia removida das preparadas de hoje.', 'sucesso');
            } else {
                await this._prepararMagiaHoje(magiaId, preparo.nivelSlot, quantidadeFinal);
                const labelQuantidade = quantidadeFinal === 1 ? '1 preparo salvo.' : `${quantidadeFinal} preparos salvos.`;
                this._mostrarToast(`Magia preparada para hoje • ${labelQuantidade}`, 'sucesso');
            }

            await this._carregarMagiasPreparadas();
            this._renderizarPainelSlots();
            this.filtrar();
            if (document.getElementById('grimorioModalDetalhes')) {
                this._renderizarModalDetalhes();
            }
            this._broadcastPreparacaoAtualizada();
        } catch (error) {
            this._mostrarToast(error.message || 'Não foi possível atualizar a preparação da magia.', 'erro');
        }
    }

    _broadcastPreparacaoAtualizada(extra = {}) {
        if (!this._canal || !this.combatente?.id) return;
        try {
            this._canal.postMessage({
                tipo: 'magia-preparada-atualizada',
                combatenteId: this.combatente.id,
                timestamp: Date.now(),
                ...extra,
            });
        } catch (_error) {
            // Broadcast é opcional.
        }
    }

    _aplicarDescansoLongoEstadoLocal() {
        this.magiasPreparadas = [];
        this.magiasPreparadasMap = new Map();
        this.preparacaoQuantidadesDraft = new Map();

        if (this.combatente && Array.isArray(this.combatente.magias_slots)) {
            this.combatente.magias_slots = this.combatente.magias_slots.map((slot) => ({
                ...slot,
                usados: 0,
            }));
        }

        this._hidratarSlotsDisponiveis();
        this._renderizarPainelSlots();
        this.filtrar();
    }

    _confirmarDescansoLongo() {
        this._mostrarModalConfirmacao({
            icone: '🌙',
            titulo: 'Descanso longo',
            texto: 'Isso limpará todas as magias preparadas do dia e zerará os usos de slots para que você possa redecorar amanhã. Deseja continuar?',
            textoConfirmar: 'Confirmar descanso',
            textoCancelar: 'Cancelar',
            onConfirmar: async () => {
                try {
                    await this.magiaPreparadaService.descansoLongo(this.combatente.id, true);
                    this._aplicarDescansoLongoEstadoLocal();
                    await this._recarregarDados();
                    if (window._fichaController?.renderizarSlotsDeMapia) {
                        window._fichaController.renderizarSlotsDeMapia();
                    }
                    this._broadcastPreparacaoAtualizada({ resetSlots: true, origem: 'descanso-longo' });
                    this._mostrarToast('Descanso longo realizado. As magias preparadas de hoje foram limpas.', 'sucesso');
                } catch (error) {
                    this._mostrarToast(error.message || 'Não foi possível realizar o descanso longo.', 'erro');
                }
            },
        });
    }

    async _toggleFavorita(magiaId) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return;

        try {
            await this.grimorioService.atualizar(this.combatente.id, magiaId, this.classeAtiva, {
                favorita: !item.favorita,
            });
            item.favorita = !item.favorita;
            this._mostrarToast(item.favorita ? 'Magia marcada como favorita.' : 'Magia removida dos favoritos.', 'info');
            this.filtrar();
        } catch (error) {
            this._mostrarToast(error.message || 'Não foi possível atualizar favorito.', 'erro');
        }
    }

    async _editarAnotacoes(magiaId) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return;

        this._mostrarModalAnotacoes({
            titulo: item.magia?.nome || 'Anotações da magia',
            valorInicial: item.anotacoes || '',
            onSalvar: async (novoTexto) => {
                try {
                    await this.grimorioService.atualizar(this.combatente.id, magiaId, this.classeAtiva, {
                        anotacoes: novoTexto,
                    });
                    item.anotacoes = novoTexto;
                    this._mostrarToast('Anotação salva com sucesso.', 'sucesso');
                    this.filtrar();
                } catch (error) {
                    this._mostrarToast(error.message || 'Erro ao salvar anotação.', 'erro');
                }
            },
        });
    }

    async _removerMagia(magiaId) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return;

        this._mostrarModalConfirmacao({
            icone: '⚠',
            titulo: 'Remover magia',
            texto: `Tem certeza que deseja remover '${item.magia?.nome || 'esta magia'}' do grimório?`,
            textoConfirmar: 'Remover',
            textoCancelar: 'Cancelar',
            onConfirmar: async () => {
                try {
                    await this.grimorioService.remover(this.combatente.id, magiaId, this.classeAtiva);
                    this._mostrarToast('Magia removida do grimório.', 'sucesso');
                    await this._recarregarDados();
                } catch (error) {
                    this._mostrarToast(error.message || 'Não foi possível remover a magia.', 'erro');
                }
            },
        });
    }

    _toggleCard(magiaId) {
        if (this.cardsAbertos.has(magiaId)) this.cardsAbertos.delete(magiaId);
        else this.cardsAbertos.add(magiaId);

        this._renderizarLista();
    }

    _abrirModalDetalhes(magiaId) {
        const index = this.itensFiltrados.findIndex((entry) => Number(entry.magia_id) === Number(magiaId));
        if (index < 0) return;
        this.indiceDetalheAtual = index;
        this._renderizarModalDetalhes();
    }

    _fecharModalDetalhes() {
        const anterior = document.getElementById('grimorioModalDetalhes');
        if (anterior?._grimorioKeydownHandler) {
            document.removeEventListener('keydown', anterior._grimorioKeydownHandler);
        }
        if (anterior) anterior.remove();
    }

    fecharModalDetalhes() {
        this._fecharModalDetalhes();
    }

    _navegarModalDetalhes(delta) {
        if (!this.itensFiltrados.length) return;
        const tamanho = this.itensFiltrados.length;
        this.indiceDetalheAtual = (this.indiceDetalheAtual + delta + tamanho) % tamanho;
        this._renderizarModalDetalhes();
    }

    _renderizarModalDetalhes() {
        if (!this.itensFiltrados.length || this.indiceDetalheAtual < 0) return;
        const item = this.itensFiltrados[this.indiceDetalheAtual];
        if (!item) return;

        const magia = item.magia || {};
        const classeMago = this._normalizarClasse(this.classeAtiva) === 'Mago';
        const itemPersistido = !item._catalogo_expandido;
        const preparo = this._obterInfoPreparacao(item);
        const componentesDetalhados = this._componentesDetalhados(magia);
        const niveisPorClasse = this._formatarNiveisPorClasse(magia, item);
        const posicaoAtual = this.indiceDetalheAtual + 1;
        const totalItens = this.itensFiltrados.length;
        const quantidadeSugerida = preparo.preparada ? preparo.quantidadeAtual : (preparo.temEspaco ? 1 : 0);
        const limiteQuantidade = Math.max(quantidadeSugerida, preparo.quantidadeMaxima || 0);
        const textoBotaoPreparar = preparo.preparada ? '💾 Salvar preparo' : '🪄 Preparar hoje';

        const anterior = document.getElementById('grimorioModalDetalhes');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id = 'grimorioModalDetalhes';
        overlay.className = 'grimorio-confirm-overlay show grimorio-detalhe-overlay';
        overlay.innerHTML = `
            <div class="grimorio-confirm-box grimorio-detalhe-box">
                <div class="grimorio-confirm-header">
                    <div class="grimorio-detalhe-header-main">
                        <span class="grimorio-confirm-icone">✨</span>
                        <h3 class="grimorio-confirm-titulo">${escapeHtml(magia.nome || `Magia ${item.magia_id}`)}</h3>
                    </div>
                    <span class="grimorio-detalhe-posicao">${posicaoAtual}/${totalItens}</span>
                </div>
                <div class="grimorio-detalhe-grid-modal">
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Escola</span><span class="grimorio-detalhe-valor">${escapeHtml(this._normalizarEscola(magia.escola || '-'))}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Subescola</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.sub_escola || magia.subescola || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Descritor</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.descritor || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Nivel</span><span class="grimorio-detalhe-valor">${Number(magia.nivel || 0)}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Classe</span><span class="grimorio-detalhe-valor">${escapeHtml(item.classe || this.classeAtiva || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Niveis por classe</span><span class="grimorio-detalhe-valor">${escapeHtml(niveisPorClasse)}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Componentes</span><span class="grimorio-detalhe-valor">${escapeHtml(componentesDetalhados)}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Conjuracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Alcance</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.alcance || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Alvo/Area</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.area_efeito || magia.area_efeito_alvo || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Duracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.duracao || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Resistencia</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.teste_resistencia || '-')}</span></div>
                    <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">RM</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.resistencia_magia || magia.resistencia_magica || magia.resistencia_magia_texto || '-')}</span></div>
                    <div class="grimorio-detalhe-linha grimorio-detalhe-linha-descricao"><span class="grimorio-detalhe-chave">Descricao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.descricao || 'Sem descricao.')}</span></div>
                    <div class="grimorio-detalhe-linha grimorio-detalhe-linha-descricao"><span class="grimorio-detalhe-chave">Anotacoes</span><span class="grimorio-detalhe-valor">${escapeHtml(item.anotacoes || 'Sem anotacoes pessoais.')}</span></div>
                </div>
                <div class="grimorio-detalhe-preparo-box ${(!preparo.temEspaco && !preparo.preparada) ? 'is-disabled' : ''}">
                    <div class="grimorio-detalhe-preparo-topo">
                        <span class="grimorio-detalhe-preparo-titulo">Preparos de hoje</span>
                        <span class="grimorio-detalhe-preparo-status">${preparo.preparada ? `${preparo.quantidadeAtual} preparada(s)` : `0/${preparo.slot.total || 0}`}</span>
                    </div>
                    <div class="grimorio-detalhe-quantidade-row">
                        <button class="grimorio-detalhe-stepper" id="grimorioDetalheQtdMenos" type="button" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>−</button>
                        <input class="grimorio-detalhe-quantidade-input" id="grimorioDetalheQuantidade" type="number" min="0" max="${limiteQuantidade}" step="1" value="${quantidadeSugerida}" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>
                        <button class="grimorio-detalhe-stepper" id="grimorioDetalheQtdMais" type="button" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>+</button>
                    </div>
                    <div class="grimorio-detalhe-preparo-ajuda">Máximo neste nível: ${limiteQuantidade}. Se preparar 2x, a Arena exibirá duas cópias da magia.</div>
                </div>
                <div class="grimorio-confirm-botoes grimorio-detalhe-botoes">
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheAnterior">← Anterior</button>
                    <button class="grimorio-confirm-btn ${preparo.preparada ? 'grimorio-confirm-ok' : 'grimorio-confirm-cancelar'}" id="grimorioDetalhePreparar" ${(!preparo.temEspaco && !preparo.preparada) ? 'disabled' : ''}>${textoBotaoPreparar}</button>
                    ${preparo.preparada ? '<button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheLimparPreparo">Limpar preparo</button>' : ''}
                    ${itemPersistido ? `<button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheFavorita">${item.favorita ? '★ Favorita' : '☆ Favoritar'}</button>` : ''}
                    ${itemPersistido ? '<button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheAnotacao">✎ Anotacoes</button>' : ''}
                    ${classeMago && itemPersistido ? '<button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioDetalheRemover">Remover</button>' : ''}
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheProxima">Proxima →</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioDetalheFechar">Fechar</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        overlay.querySelector('#grimorioDetalheAnterior')?.addEventListener('click', () => this._navegarModalDetalhes(-1));
        overlay.querySelector('#grimorioDetalheProxima')?.addEventListener('click', () => this._navegarModalDetalhes(1));
        overlay.querySelector('#grimorioDetalheFechar')?.addEventListener('click', () => this._fecharModalDetalhes());

        const quantidadeInput = overlay.querySelector('#grimorioDetalheQuantidade');
        const btnPreparar = overlay.querySelector('#grimorioDetalhePreparar');
        const limitePreparos = Number(limiteQuantidade || 0);
        const normalizarQuantidadeInput = () => {
            if (!quantidadeInput) return 0;
            const valor = Math.max(0, Math.min(limitePreparos, Number(quantidadeInput.value || 0)));
            quantidadeInput.value = String(Number.isFinite(valor) ? valor : 0);
            if (btnPreparar) {
                if (valor <= 0 && preparo.preparada) btnPreparar.textContent = '🧹 Remover preparo';
                else if (preparo.preparada) btnPreparar.textContent = '💾 Salvar preparo';
                else btnPreparar.textContent = '🪄 Preparar hoje';
            }
            return valor;
        };

        overlay.querySelector('#grimorioDetalheQtdMenos')?.addEventListener('click', () => {
            if (!quantidadeInput) return;
            quantidadeInput.value = String(Math.max(0, Number(quantidadeInput.value || 0) - 1));
            normalizarQuantidadeInput();
        });
        overlay.querySelector('#grimorioDetalheQtdMais')?.addEventListener('click', () => {
            if (!quantidadeInput) return;
            quantidadeInput.value = String(Math.min(limitePreparos, Number(quantidadeInput.value || 0) + 1));
            normalizarQuantidadeInput();
        });
        quantidadeInput?.addEventListener('input', normalizarQuantidadeInput);
        normalizarQuantidadeInput();

        overlay.querySelector('#grimorioDetalhePreparar')?.addEventListener('click', async () => {
            const quantidadeDesejada = normalizarQuantidadeInput();
            await this._togglePreparada(item.magia_id, quantidadeDesejada);
        });

        overlay.querySelector('#grimorioDetalheLimparPreparo')?.addEventListener('click', async () => {
            if (quantidadeInput) quantidadeInput.value = '0';
            await this._togglePreparada(item.magia_id, 0);
        });

        overlay.querySelector('#grimorioDetalheFavorita')?.addEventListener('click', async () => {
            await this._toggleFavorita(item.magia_id);
            this._renderizarModalDetalhes();
        });

        overlay.querySelector('#grimorioDetalheAnotacao')?.addEventListener('click', async () => {
            await this._editarAnotacoes(item.magia_id);
            this._renderizarModalDetalhes();
        });

        overlay.querySelector('#grimorioDetalheRemover')?.addEventListener('click', async () => {
            await this._removerMagia(item.magia_id);
            this._fecharModalDetalhes();
        });

        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) this._fecharModalDetalhes();
        });

        const onKeydown = (event) => {
            if (event.key === 'Escape') this._fecharModalDetalhes();
            if (event.key === 'ArrowLeft') this._navegarModalDetalhes(-1);
            if (event.key === 'ArrowRight') this._navegarModalDetalhes(1);
        };
        document.addEventListener('keydown', onKeydown);
        overlay.dataset.keydownBound = 'true';
        overlay._grimorioKeydownHandler = onKeydown;
    }

    _componentesDetalhados(magia) {
        const mapa = {
            V: 'Verbal (V)',
            G: 'Gestual (G)',
            M: 'Material (M)',
            F: 'Foco (F)',
            FD: 'Foco Divino (FD)',
            XP: 'Custo de XP (XP)',
        };
        const componentesRaw = String(magia?.componentes || '').toUpperCase();
        const componentes = this._extrairComponentes(componentesRaw);
        const nomes = COMPONENTES
            .filter((sigla) => componentes.has(sigla))
            .map((sigla) => mapa[sigla] || sigla);
        const componenteExtra = String(magia?.componente_extra || '').trim();
        if (componenteExtra) nomes.push(`Detalhe: ${componenteExtra}`);
        return nomes.join(', ') || '-';
    }

    _formatarNiveisPorClasse(magia, item) {
        const linhas = Array.isArray(magia?.classes_niveis) ? magia.classes_niveis : [];
        if (linhas.length > 0) {
            const pares = linhas
                .map((cn) => ({
                    classe: this._normalizarClasse(cn?.classe || ''),
                    nivel: Number(cn?.nivel ?? 0),
                }))
                .filter((cn) => cn.classe)
                .sort((a, b) => a.nivel - b.nivel || a.classe.localeCompare(b.classe, 'pt-BR'))
                .map((cn) => `${cn.classe} ${cn.nivel}`);
            if (pares.length > 0) return pares.join(', ');
        }

        const classeFallback = this._normalizarClasse(item?.classe || this.classeAtiva || '-') || '-';
        const nivelFallback = Number(magia?.nivel || 0);
        return `${classeFallback} ${nivelFallback}`;
    }

    _mostrarModalConfirmacao(opcoes) {
        const anterior = document.getElementById('grimorioModalConfirmacao');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id = 'grimorioModalConfirmacao';
        overlay.className = 'grimorio-confirm-overlay show';
        overlay.innerHTML = `
            <div class="grimorio-confirm-box">
                <div class="grimorio-confirm-header">
                    <span class="grimorio-confirm-icone">${opcoes.icone || '⚠'}</span>
                    <h3 class="grimorio-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="grimorio-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="grimorio-confirm-botoes">
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioConfirmCancelar">${opcoes.textoCancelar || 'Cancelar'}</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioConfirmOk">${opcoes.textoConfirmar || 'Confirmar'}</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        const fechar = () => overlay.remove();

        overlay.querySelector('#grimorioConfirmCancelar')?.addEventListener('click', () => {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        });

        overlay.querySelector('#grimorioConfirmOk')?.addEventListener('click', () => {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        });

        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) fechar();
        });
    }

    _mostrarModalAnotacoes({ titulo, valorInicial, onSalvar }) {
        const anterior = document.getElementById('grimorioModalAnotacoes');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id = 'grimorioModalAnotacoes';
        overlay.className = 'grimorio-confirm-overlay show';
        overlay.innerHTML = `
            <div class="grimorio-confirm-box grimorio-anotacao-box">
                <div class="grimorio-confirm-header">
                    <span class="grimorio-confirm-icone">✎</span>
                    <h3 class="grimorio-confirm-titulo">${escapeHtml(titulo)}</h3>
                </div>
                <textarea id="grimorioAnotacaoTexto" class="grimorio-anotacao-texto" rows="6" placeholder="Escreva sua anotacao...">${escapeHtml(valorInicial || '')}</textarea>
                <div class="grimorio-confirm-botoes">
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioAnotacaoCancelar">Cancelar</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioAnotacaoSalvar">Salvar</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        const fechar = () => overlay.remove();

        overlay.querySelector('#grimorioAnotacaoCancelar')?.addEventListener('click', fechar);
        overlay.querySelector('#grimorioAnotacaoSalvar')?.addEventListener('click', () => {
            const texto = overlay.querySelector('#grimorioAnotacaoTexto')?.value || '';
            fechar();
            if (onSalvar) onSalvar(texto);
        });

        overlay.addEventListener('click', (event) => {
            if (event.target === overlay) fechar();
        });
    }

    _mostrarToast(msg, tipo = 'sucesso') {
        const toast = document.createElement('div');
        toast.className = `grimorio-toast grimorio-toast-${tipo}`;
        toast.textContent = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2600);
    }

    _mostrarLoading(visivel) {
        const el = document.getElementById('grimorioLoading');
        const lista = document.getElementById('grimorioLista');
        if (el) el.style.display = visivel ? 'flex' : 'none';
        if (lista) lista.style.display = visivel ? 'none' : 'block';
    }

    _normalizarClasse(classe) {
        return normalizeClasseConjuradora(classe) || String(classe || '').trim();
    }

    _extrairClassesConjuradoras(valorClasse) {
        const classes = String(valorClasse || '')
            .split(/[,/;|]/)
            .map((entry) => this._normalizarClasse(entry))
            .filter(Boolean)
            .filter((entry, index, arr) => arr.indexOf(entry) === index)
            .filter((entry) => isClasseConjuradora(entry));
        return classes;
    }

    _normalizarEscola(escola) {
        const base = String(escola || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/\s+/g, ' ')
            .trim();

        if (!base) return '';

        const baseLower = base.toLowerCase();
        const valoresIgnorados = new Set(['escola', 'escola de magia', 'sem escola', 'nenhuma', 'n/a', 'null', '-']);
        if (valoresIgnorados.has(baseLower)) {
            return '';
        }

        const aliases = [
            ['abjur', 'Abjuracao'],
            ['adiv', 'Adivinhacao'],
            ['conj', 'Conjuracao'],
            ['enca', 'Encantamento'],
            ['evoc', 'Evocacao'],
            ['ilus', 'Ilusao'],
            ['necr', 'Necromancia'],
            ['trans', 'Transmutacao'],
            ['univ', 'Universal'],
        ];

        const encontrado = aliases.find(([prefixo]) => baseLower.startsWith(prefixo));
        if (encontrado) {
            return encontrado[1];
        }

        const formatado = base.charAt(0).toUpperCase() + base.slice(1).toLowerCase();
        return formatado;
    }
}

// Inicializacao

document.addEventListener('DOMContentLoaded', () => {
    installGlobalErrorGuards('grimorio-page');
    const tentarInicializar = setInterval(() => {
        try {
            const classeEl = document.getElementById('fichaClasse');
            if (!classeEl) return;

            const classe = classeEl.textContent?.trim();
            if (!classe || classe === '-' || classe === '—') return;

            const combatente = window._fichaController?.combatente;
            if (!combatente) return;

            clearInterval(tentarInicializar);

            const token = localStorage.getItem('token');
            const magiaService = new MagiaService(token);
            const grimorioService = new GrimorioService(token);

            window._grimorioController = safeBootstrap(
                'grimorio-controller',
                () => new GrimorioController(combatente, token, magiaService, grimorioService),
                'Falha ao iniciar grimorio. A ficha continuara disponivel sem a aba de magias.'
            );

            if (!window._grimorioController) return;

            const classesConjuradoras = String(classe || '')
                .split(/[,/;|]/)
                .map((entry) => normalizeClasseConjuradora(entry))
                .filter(Boolean);

            if (isClasseConjuradora(classe) || classesConjuradoras.length > 0) {
                const btnHeader = document.getElementById('btnGrimorio');
                const secaoMagia = document.getElementById('secaoMagias');
                if (btnHeader) btnHeader.style.display = 'inline-flex';
                if (secaoMagia) secaoMagia.style.display = 'flex';
            }

            document.getElementById('modalGrimorio')?.addEventListener('click', (event) => {
                if (event.target.id === 'modalGrimorio') window._grimorioController.fecharGrimorio();
            });

            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape') {
                    const modalDetalhes = document.getElementById('grimorioModalDetalhes');
                    if (modalDetalhes) {
                        window._grimorioController?.fecharModalDetalhes();
                        return;
                    }
                    window._grimorioController?.fecharGrimorio();
                }
            });
        } catch (error) {
            reportDegradedMode(
                'grimorio-bootstrap',
                error,
                'Falha ao carregar grimorio. Os demais recursos da ficha continuam ativos.'
            );
            clearInterval(tentarInicializar);
        }
    }, 250);
});

export { GrimorioController, COMPONENTES };
