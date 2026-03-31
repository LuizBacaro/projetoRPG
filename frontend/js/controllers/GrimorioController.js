import { MagiaService } from '../services/MagiaService.js';
import { GrimorioService } from '../services/GrimorioService.js';
import { escapeHtml } from '../utils/formatters.js';
import {
    installGlobalErrorGuards,
    reportDegradedMode,
    safeBootstrap,
} from '../utils/graceful-degradation.js';
import {
    isClasseConjuradora,
    normalizeClasseConjuradora,
} from '../utils/combat-rules.js';

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

        this.classesConjuradoras = this._extrairClassesConjuradoras(combatente?.classe);
        this.classeAtiva = this.classesConjuradoras[0] || normalizeClasseConjuradora(combatente?.classe) || '';

        this.itensGrimorio = [];
        this.catalogoClasse = [];
        this.catalogoIndex = new Map();

        this.itensFiltrados = [];
        this.historicoTrocas = [];
        this.notificacoes = [];
        this.indiceDetalheAtual = -1;
        this.nivelAtivo = 'todos';
        this.escolaAtiva = 'todas';
        this.componenteAtivo = 'todos';
        this.favoritasApenas = false;
        this.magiaAdicionarSelecionadaId = null;

        this.cardsAbertos = new Set();
        this._carregado = false;
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
        document.body.style.overflow = '';
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

            if (!busca) return matchNivel && matchEscola && matchComponente && matchFavorita;

            const alvoBusca = [
                magia.nome,
                magia.escola,
                magia.descricao,
                magia.componentes,
                item.anotacoes,
            ].filter(Boolean).join(' ').toLowerCase();

            return matchNivel && matchEscola && matchComponente && matchFavorita && alvoBusca.includes(busca);
        });

        this._renderizarLista();
    }

    async _recarregarDados() {
        this._mostrarLoading(true);
        try {
            await Promise.all([
                this._carregarCatalogoClasse(),
                this._carregarItensGrimorio(),
                this._carregarNotificacoes(),
            ]);

            this._renderizarCabecalho();
            this._renderizarSeletorClasses();
            this._renderizarFiltroEscolas();
            this._renderizarIndicadores();
            await this._carregarHistoricoTrocas();
            this._renderizarHistoricoTrocas();
            this._renderizarNotificacoes();
            this._atualizarBadgeTrocaDisponivel();
            this.filtrar();
            this._renderizarPainelAdicionar();
            this._renderizarPainelTroca();
            this._carregado = true;
        } catch (error) {
            this._mostrarToast(error.message || 'Nao foi possivel carregar o grimorio.', 'erro');
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

        this.itensGrimorio = itens.map((item) => {
            const magiaDetalhada = this.catalogoIndex.get(Number(item.magia_id));
            const nivelFallback = Number(item.magia_nivel ?? magiaDetalhada?.nivel ?? 0);
            const dominioFallback = item.magia_e_magia_dominio ?? magiaDetalhada?.e_magia_dominio ?? false;
            const dominiosFallback = item.magia_dominios ?? magiaDetalhada?.dominios ?? '';
            const magiaMesclada = {
                ...(magiaDetalhada || {}),
                id: Number(item.magia_id),
                nome: item.magia_nome || magiaDetalhada?.nome || `Magia ${item.magia_id}`,
                escola: item.magia_escola || magiaDetalhada?.escola || '',
                nivel: Number.isNaN(nivelFallback) ? 0 : nivelFallback,
                componentes: item.magia_componentes || magiaDetalhada?.componentes || '',
                e_magia_dominio: !!dominioFallback,
                dominios: dominiosFallback,
                descricao: magiaDetalhada?.descricao || '',
                sub_escola: magiaDetalhada?.sub_escola || magiaDetalhada?.subescola || '',
                subescola: magiaDetalhada?.sub_escola || magiaDetalhada?.subescola || '',
                area_efeito: magiaDetalhada?.area_efeito || magiaDetalhada?.area_efeito_alvo || '',
                area_efeito_alvo: magiaDetalhada?.area_efeito || magiaDetalhada?.area_efeito_alvo || '',
                resistencia_magia: magiaDetalhada?.resistencia_magia || magiaDetalhada?.resistencia_magia_texto || '',
            };

            return {
                ...item,
                magia_id: Number(item.magia_id),
                favorita: !!item.favorita,
                magia: magiaMesclada,
            };
        });
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
            avisoEl.style.display = 'none';
            avisoEl.textContent = '';
            return;
        }

        const nivel = Number(this.combatente?.nivel || 1);
        avisoEl.style.display = 'block';
        avisoEl.textContent = `Esta classe so recebe acesso a magias no nivel 4. Nivel atual: ${nivel}.`;
    }

    _renderizarFiltroEscolas() {
        const container = document.getElementById('grimorioFiltroEscolas');
        if (!container) return;

        const escolas = new Set();
        this.itensGrimorio.forEach((item) => {
            const escola = this._normalizarEscola(item.magia?.escola || '');
            if (escola) escolas.add(escola);
        });

        const escolasOrdenadas = ESCOLAS_ORDEM.filter((escola) => escolas.has(escola));

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
        this._bindComponente();
        this._bindAdicionarMagia();
        this._bindFiltrosAdicionar();
        this._bindTrocaMagia();
        this._bindNotificacoes();
    }

    _bindNotificacoes() {
        const btnAbrir = document.getElementById('btnNotificacoesGrimorio');
        const painel = document.getElementById('grimorioPainelNotificacoes');
        const btnFechar = document.getElementById('btnFecharPainelNotificacoes');

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
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
            const semAcesso = this._classeSemAcessoMagias();
            btnAbrir.disabled = semAcesso;
            btnAbrir.title = semAcesso
                ? 'Disponivel apenas a partir do nivel 4 para Ranger/Paladino'
                : 'Adicionar magia conhecida';
            btnAbrir.style.opacity = semAcesso ? '0.5' : '1';
            btnAbrir.style.cursor = semAcesso ? 'not-allowed' : 'pointer';
        }

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
                if (this._classeSemAcessoMagias()) {
                    this._mostrarToast('Ranger e Paladino so recebem magias a partir do nivel 4.', 'info');
                    return;
                }
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

    _bindTrocaMagia() {
        const btnAbrir = document.getElementById('btnTrocarMagiaGrimorio');
        const btnFechar = document.getElementById('btnFecharPainelTroca');
        const painel = document.getElementById('grimorioPainelTroca');
        const btnConfirmar = document.getElementById('btnConfirmarTrocaMagia');

        if (btnAbrir && painel) {
            const clone = btnAbrir.cloneNode(true);
            btnAbrir.parentNode.replaceChild(clone, btnAbrir);
            clone.addEventListener('click', () => {
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
                    this._mostrarToast(error.message || 'Nao foi possivel realizar a troca.', 'erro');
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

    _renderizarPainelAdicionar() {
        const lista = document.getElementById('grimorioAdicionarLista');
        const preview = document.getElementById('grimorioAdicionarPreview');
        if (!lista || !preview) return;

        if (this._classeSemAcessoMagias()) {
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
            lista.innerHTML = '<div class="grimorio-vazio">Nenhuma magia disponivel para adicionar.</div>';
            preview.innerHTML = '<div class="grimorio-historico-vazio">Nenhuma magia corresponde aos filtros selecionados.</div>';
            return;
        }

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
                this._renderizarPreviewAdicionar(disponiveis, magiaId);
            });
        });

        this._renderizarPreviewAdicionar(disponiveis, this.magiaAdicionarSelecionadaId);
    }

    _renderizarPreviewAdicionar(disponiveis, magiaId) {
        const preview = document.getElementById('grimorioAdicionarPreview');
        if (!preview) return;

        const magia = (disponiveis || []).find((item) => Number(item.id) === Number(magiaId));
        if (!magia) {
            preview.innerHTML = '<div class="grimorio-historico-vazio">Selecione uma magia para visualizar o preview antes de adicionar.</div>';
            return;
        }

        preview.innerHTML = `
            <div class="grimorio-add-preview-titulo">${escapeHtml(magia.nome || 'Magia')}</div>
            <div class="grimorio-add-preview-grid">
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Nivel</span><span class="grimorio-add-preview-valor">${Number(magia.nivel || 0)}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Escola</span><span class="grimorio-add-preview-valor">${escapeHtml(this._normalizarEscola(magia.escola || '-'))}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Componentes</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.componentes || '-')}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Conjuracao</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span></div>
                <div class="grimorio-add-preview-linha"><span class="grimorio-add-preview-chave">Alcance</span><span class="grimorio-add-preview-valor">${escapeHtml(magia.alcance || '-')}</span></div>
            </div>
            <div class="grimorio-add-preview-descricao">${escapeHtml((magia.descricao || 'Sem descrição.').slice(0, 320))}</div>
            <button class="grimorio-add-btn grimorio-add-preview-acao" id="btnConfirmarAdicionarPreview">Adicionar esta magia</button>
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

        if (!this.historicoTrocas.length) {
            el.innerHTML = '<div class="grimorio-historico-vazio">Sem historico de troca para esta classe.</div>';
            return;
        }

        el.innerHTML = this.historicoTrocas.map((item) => {
            const removida = item.magia_removida_nome || `#${item.magia_removida_id}`;
            const adicionada = item.magia_adicionada_nome || `#${item.magia_adicionada_id}`;
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
                    this._mostrarToast(error.message || 'Nao foi possivel atualizar a notificacao.', 'erro');
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
                    this._mostrarToast(error.message || 'Nao foi possivel descartar a notificacao.', 'erro');
                }
            });
        });
    }

    _classeNotificacao(item) {
        if (item?.tipo === 'MAGIAS_ADICIONADAS') return 'grimorio-notificacao-auto';
        if (item?.tipo === 'SEM_MAGIAS_ATE_NIVEL_4') return 'grimorio-notificacao-bloqueio';
        return '';
    }

    _textoNotificacao(item) {
        const dados = item.dados || {};
        if (item.tipo === 'SEM_MAGIAS_ATE_NIVEL_4') {
            return 'Ranger e Paladino so recebem magias quando alcancam o nivel 4.';
        }
        if (item.tipo === 'TROCA_DISPONIVEL') {
            return 'Uma troca de magia está disponível para esta classe.';
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
                return `Você possui ${qtd} magia(s) disponível(is) para seleção (${niveis}).`;
            }

            return `Você possui ${qtd} magia(s) disponível(is) para seleção no catálogo.`;
        }
        if (item.tipo === 'MAGIAS_ADICIONADAS') {
            const qtd = Number(dados.quantidade || 0);
            const nomes = Array.isArray(dados.magias_nomes)
                ? dados.magias_nomes.map((nome) => String(nome || '').trim()).filter(Boolean)
                : [];
            if (nomes.length > 0) {
                const resumo = nomes.slice(0, 4).join(', ');
                const sufixo = nomes.length > 4 ? ` e mais ${nomes.length - 4}` : '';
                return `${qtd} nova(s) magia(s) foram adicionadas automaticamente ao grimório: ${resumo}${sufixo}.`;
            }
            return `${qtd} nova(s) magia(s) foram adicionadas automaticamente ao grimório.`;
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
                lista.innerHTML = '<div class="grimorio-vazio">Grimorio acessivel, mas sem magias: Ranger e Paladino recebem magias a partir do nivel 4.</div>';
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

        lista.querySelectorAll('.grimorio-magia-card').forEach((card) => {
            card.addEventListener('click', (event) => {
                if (event.target.closest('.grimorio-acoes-card')) return;
                if (event.target.closest('.grimorio-expandir-btn')) return;
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
        const escola = this._normalizarEscola(magia.escola || '');
        const magiaDominio = this._ehMagiaDominio(item);
        const dominios = String(magia.dominios || item.magia_dominios || '').trim();

        const detalhes = `
            <div class="grimorio-card-detalhes ${aberta ? 'show' : ''}">
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Escola</span><span class="grimorio-detalhe-valor">${escapeHtml(escola || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Componentes</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.componentes || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Conjuracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.tempo_conjuracao || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Alcance</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.alcance || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Duracao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.duracao || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Resistencia</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.teste_resistencia || '-')}</span></div>
                <div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Descricao</span><span class="grimorio-detalhe-valor">${escapeHtml(magia.descricao || '-')}</span></div>
                ${item.anotacoes ? `<div class="grimorio-detalhe-linha"><span class="grimorio-detalhe-chave">Anotacoes</span><span class="grimorio-detalhe-valor">${escapeHtml(item.anotacoes)}</span></div>` : ''}
            </div>
        `;

        return `
            <article class="grimorio-magia-card ${item.favorita ? 'favorita' : ''}" data-id="${id}">
                <div class="grimorio-card-topo">
                    <div>
                        <span class="grimorio-card-nome">${escapeHtml(magia.nome || `Magia ${id}`)}</span>
                        <div class="grimorio-card-badges">
                            <span class="grimorio-badge grimorio-badge-escola">${escapeHtml(escola || 'Sem escola')}</span>
                            <span class="grimorio-badge grimorio-badge-comp">N${Number(magia.nivel || 0)} - ${escapeHtml(magia.componentes || '-')}</span>
                            <span class="grimorio-badge grimorio-badge-origem">${escapeHtml(item.origem || 'SELECAO_MANUAL')}</span>
                            ${magiaDominio ? `<span class="grimorio-badge grimorio-badge-dominio">Dominio${dominios ? `: ${escapeHtml(dominios)}` : ''}</span>` : ''}
                        </div>
                    </div>
                    <div class="grimorio-acoes-card">
                        <button class="grimorio-favorita-btn ${item.favorita ? 'ativa' : ''}" data-magia-id="${id}" title="Favoritar">★</button>
                        <button class="grimorio-anotacao-btn" data-magia-id="${id}" title="Anotacoes">✎</button>
                        ${classeMago ? `<button class="grimorio-remover-btn" data-magia-id="${id}" title="Remover">🗑</button>` : ''}
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
                    ${item.anotacoes ? '<span class="grimorio-preparada-badge">Com anotacoes</span>' : ''}
                </div>
            </article>
        `;
    }

    async _adicionarMagia(magiaId) {
        try {
            await this.grimorioService.adicionar(this.combatente.id, {
                magia_id: magiaId,
                classe: this.classeAtiva,
                origem: 'SELECAO_MANUAL',
            });
            this._mostrarToast('Magia adicionada ao grimorio.', 'sucesso');
            await this._recarregarDados();
        } catch (error) {
            this._mostrarToast(error.message || 'Nao foi possivel adicionar a magia.', 'erro');
        }
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
            this._mostrarToast(error.message || 'Nao foi possivel atualizar favorito.', 'erro');
        }
    }

    async _editarAnotacoes(magiaId) {
        const item = this.itensGrimorio.find((entry) => Number(entry.magia_id) === Number(magiaId));
        if (!item) return;

        this._mostrarModalAnotacoes({
            titulo: item.magia?.nome || 'Anotacoes da magia',
            valorInicial: item.anotacoes || '',
            onSalvar: async (novoTexto) => {
                try {
                    await this.grimorioService.atualizar(this.combatente.id, magiaId, this.classeAtiva, {
                        anotacoes: novoTexto,
                    });
                    item.anotacoes = novoTexto;
                    this._mostrarToast('Anotacao salva com sucesso.', 'sucesso');
                    this.filtrar();
                } catch (error) {
                    this._mostrarToast(error.message || 'Erro ao salvar anotacao.', 'erro');
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
            texto: `Tem certeza que deseja remover '${item.magia?.nome || 'esta magia'}' do grimorio?`,
            textoConfirmar: 'Remover',
            textoCancelar: 'Cancelar',
            onConfirmar: async () => {
                try {
                    await this.grimorioService.remover(this.combatente.id, magiaId, this.classeAtiva);
                    this._mostrarToast('Magia removida do grimorio.', 'sucesso');
                    await this._recarregarDados();
                } catch (error) {
                    this._mostrarToast(error.message || 'Nao foi possivel remover a magia.', 'erro');
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
        const componentesDetalhados = this._componentesDetalhados(magia);
        const niveisPorClasse = this._formatarNiveisPorClasse(magia, item);
        const posicaoAtual = this.indiceDetalheAtual + 1;
        const totalItens = this.itensFiltrados.length;

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
                <div class="grimorio-confirm-botoes grimorio-detalhe-botoes">
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheAnterior">← Anterior</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheFavorita">${item.favorita ? '★ Favorita' : '☆ Favoritar'}</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheAnotacao">✎ Anotacoes</button>
                    ${classeMago ? '<button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioDetalheRemover">Remover</button>' : ''}
                    <button class="grimorio-confirm-btn grimorio-confirm-cancelar" id="grimorioDetalheProxima">Proxima →</button>
                    <button class="grimorio-confirm-btn grimorio-confirm-ok" id="grimorioDetalheFechar">Fechar</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        overlay.querySelector('#grimorioDetalheAnterior')?.addEventListener('click', () => this._navegarModalDetalhes(-1));
        overlay.querySelector('#grimorioDetalheProxima')?.addEventListener('click', () => this._navegarModalDetalhes(1));
        overlay.querySelector('#grimorioDetalheFechar')?.addEventListener('click', () => this._fecharModalDetalhes());

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
            .trim();

        if (!base) return '';

        const mapa = {
            Abjuracao: 'Abjuracao',
            Adivinhacao: 'Adivinhacao',
            Conjuracao: 'Conjuracao',
            Encantamento: 'Encantamento',
            Evocacao: 'Evocacao',
            Ilusao: 'Ilusao',
            Necromancia: 'Necromancia',
            Transmutacao: 'Transmutacao',
            Universal: 'Universal',
        };

        const formatado = base.charAt(0).toUpperCase() + base.slice(1).toLowerCase();
        return mapa[formatado] || formatado;
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
            if (!classe || classe === '-') return;

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
