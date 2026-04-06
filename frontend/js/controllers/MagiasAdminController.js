import { escapeHtml } from '../utils/formatters.js';
import { MagiasAdminService } from '../services/MagiasAdminService.js';

const CLASSES_FALLBACK = [
    'BARDO',
    'CLERIGO',
    'DRUIDA',
    'MAGO',
    'PALADINO',
    'RANGER',
    'FEITICEIRO',
];

const ESCOLAS = [
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

const DOMINIOS_FALLBACK = [
    'Ar',
    'Bem',
    'Caos',
    'Conhecimento',
    'Cura',
    'Destruicao',
    'Enganacao',
    'Fogo',
    'Forca',
    'Guerra',
    'Magia',
    'Mal',
    'Morte',
    'Protecao',
    'Sol',
    'Sorte',
    'Terra',
    'Viagem',
];

function normalizeClasse(classe) {
    return String(classe || '').trim().toUpperCase();
}

function classeDisplay(classe) {
    const value = normalizeClasse(classe);
    if (!value) return '';
    if (value === 'CLERIGO') return 'Clerigo';
    if (value === 'FEITICEIRO') return 'Feiticeiro';
    return value.charAt(0) + value.slice(1).toLowerCase();
}

function toBooleanFromSelect(value) {
    if (value === 'true') return true;
    if (value === 'false') return false;
    return null;
}

class MagiasAdminController {
    constructor() {
        this.service = new MagiasAdminService();
        this.magias = [];
        this.total = 0;
        this.classes = [...CLASSES_FALLBACK];
        this.editingId = null;
        this.importPreview = null;
        this.importErrors = [];
        this.pageSize = 20;
        this.currentPage = 1;
        this.currentSkip = 0;
        this.sortBy = 'nome';
        this.sortDir = 'asc';
        this.dominiosPermitidos = [...DOMINIOS_FALLBACK];
        this.visualizacaoAtual = null;
        this.visualizacaoIdioma = 'pt';

        this.elements = {
            nomeAdminAtual: document.getElementById('nomeAdminAtual'),
            perfilAdminAtual: document.getElementById('perfilAdminAtual'),
            statTotal: document.getElementById('statTotalMagias'),
            statAtivas: document.getElementById('statMagiasAtivas'),
            statInativas: document.getElementById('statMagiasInativas'),
            resumoFiltrado: document.getElementById('resumoFiltradoMagias'),
            tabela: document.getElementById('tabelaMagias'),
            filtroNome: document.getElementById('filtroNomeMagia'),
            filtroClasse: document.getElementById('filtroClasseMagia'),
            filtroNivel: document.getElementById('filtroNivelMagia'),
            filtroEscola: document.getElementById('filtroEscolaMagia'),
            filtroStatus: document.getElementById('filtroStatusMagia'),
            filtroOrdenacaoCampo: document.getElementById('filtroOrdenacaoCampoMagia'),
            filtroOrdenacaoDirecao: document.getElementById('filtroOrdenacaoDirecaoMagia'),
            filtroLimite: document.getElementById('filtroLimiteMagia'),
            btnPaginaAnterior: document.getElementById('btnPaginaAnteriorMagia'),
            btnPaginaProxima: document.getElementById('btnPaginaProximaMagia'),
            indicadorPagina: document.getElementById('indicadorPaginaMagia'),
            btnNova: document.getElementById('btnNovaMagia'),
            btnImportar: document.getElementById('btnImportarMagias'),
            btnFecharModal: document.getElementById('btnFecharModalMagia'),
            btnCancelarModal: document.getElementById('btnCancelarModalMagia'),
            modal: document.getElementById('modalMagia'),
            modalTitulo: document.getElementById('modalMagiaTitulo'),
            form: document.getElementById('formMagia'),
            selectClasseNova: document.getElementById('novaClasseMagia'),
            inputNivelNova: document.getElementById('novoNivelClasseMagia'),
            btnAddClasse: document.getElementById('btnAdicionarClasseNivel'),
            listaClasses: document.getElementById('listaClassesNiveis'),
            inputDominio: document.getElementById('inputMagiaDominio'),
            inputDominios: document.getElementById('inputDominiosMagia'),
            listaDominios: document.getElementById('listaDominiosMagia'),
            hintDominios: document.getElementById('listaDominiosPermitidosMagia'),
            grupoDominios: document.getElementById('grupoDominiosMagia'),
            selectEscola: document.getElementById('inputEscolaMagia'),
            modalImportacao: document.getElementById('modalImportacaoMagias'),
            btnFecharModalImportacao: document.getElementById('btnFecharModalImportacao'),
            btnCancelarModalImportacao: document.getElementById('btnCancelarModalImportacao'),
            btnBaixarModeloImportacao: document.getElementById('btnBaixarModeloImportacao'),
            inputArquivoImportacao: document.getElementById('inputArquivoImportacaoMagias'),
            btnPreviewImportacao: document.getElementById('btnPreviewImportacaoMagias'),
            resumoImportacao: document.getElementById('resumoImportacaoMagias'),
            tabelaPreviewImportacao: document.getElementById('tabelaPreviewImportacaoMagias'),
            listaErrosImportacao: document.getElementById('listaErrosImportacaoMagias'),
            btnBaixarRelatorioImportacao: document.getElementById('btnBaixarRelatorioImportacaoMagias'),
            btnConfirmarImportacao: document.getElementById('btnConfirmarImportacaoMagias'),
            modalHistorico: document.getElementById('modalHistoricoMagias'),
            tituloModalHistorico: document.getElementById('tituloModalHistoricoMagias'),
            listaHistorico: document.getElementById('listaHistoricoMagias'),
            btnFecharModalHistorico: document.getElementById('btnFecharModalHistoricoMagias'),
            btnFecharRodapeModalHistorico: document.getElementById('btnFecharRodapeModalHistoricoMagias'),
            modalVisualizacao: document.getElementById('modalVisualizacaoMagias'),
            tituloModalVisualizacao: document.getElementById('tituloModalVisualizacaoMagias'),
            subtituloModalVisualizacao: document.getElementById('subtituloModalVisualizacaoMagias'),
            conteudoVisualizacaoPt: document.getElementById('conteudoVisualizacaoPtMagias'),
            conteudoVisualizacaoEn: document.getElementById('conteudoVisualizacaoEnMagias'),
            btnFecharModalVisualizacao: document.getElementById('btnFecharModalVisualizacaoMagias'),
            btnFecharRodapeModalVisualizacao: document.getElementById('btnFecharRodapeModalVisualizacaoMagias'),
            btnEditarPelaVisualizacao: document.getElementById('btnEditarPelaVisualizacaoMagias'),
            viewLangButtons: Array.from(document.querySelectorAll('[data-view-lang]')),
            viewPanels: Array.from(document.querySelectorAll('[data-view-panel]')),
            tabs: Array.from(document.querySelectorAll('[data-tab-target]')),
            tabPanels: Array.from(document.querySelectorAll('[data-tab-panel]')),
        };
    }

    async init() {
        this._preencherHeaderSessao();
        this._bindEvents();
        this._preencherOpcoesEscolas();
        await this._carregarClasses();
        await this._carregarDominiosPermitidos();
        await this._carregarMagias();
    }

    _preencherHeaderSessao() {
        if (window.AuthService) {
            if (this.elements.nomeAdminAtual) this.elements.nomeAdminAtual.textContent = window.AuthService.getNome();
            if (this.elements.perfilAdminAtual) this.elements.perfilAdminAtual.textContent = window.AuthService.getPerfil();
        }
    }

    _bindEvents() {
        const reload = () => {
            this.currentPage = 1;
            this.currentSkip = 0;
            this._carregarMagias();
        };

        if (this.elements.filtroNome) {
            this.elements.filtroNome.addEventListener('input', () => {
                clearTimeout(this._debounceBusca);
                this._debounceBusca = setTimeout(reload, 250);
            });
        }

        [
            this.elements.filtroClasse,
            this.elements.filtroNivel,
            this.elements.filtroEscola,
            this.elements.filtroStatus,
            this.elements.filtroOrdenacaoCampo,
            this.elements.filtroOrdenacaoDirecao,
        ]
            .filter(Boolean)
            .forEach((el) => el.addEventListener('change', reload));

        if (this.elements.filtroLimite) {
            this.elements.filtroLimite.value = String(this.pageSize);
            this.elements.filtroLimite.addEventListener('change', () => {
                const limit = Number(this.elements.filtroLimite.value || 20);
                this.pageSize = [20, 50, 100].includes(limit) ? limit : 20;
                this.currentPage = 1;
                this.currentSkip = 0;
                this._carregarMagias();
            });
        }

        if (this.elements.btnPaginaAnterior) {
            this.elements.btnPaginaAnterior.addEventListener('click', () => {
                if (this.currentPage <= 1) return;
                this.currentPage -= 1;
                this.currentSkip = (this.currentPage - 1) * this.pageSize;
                this._carregarMagias();
            });
        }

        if (this.elements.btnPaginaProxima) {
            this.elements.btnPaginaProxima.addEventListener('click', () => {
                const totalPages = Math.max(1, Math.ceil(this.total / this.pageSize));
                if (this.currentPage >= totalPages) return;
                this.currentPage += 1;
                this.currentSkip = (this.currentPage - 1) * this.pageSize;
                this._carregarMagias();
            });
        }

        if (this.elements.btnNova) {
            this.elements.btnNova.addEventListener('click', () => this._abrirModalNova());
        }

        if (this.elements.btnImportar) {
            this.elements.btnImportar.addEventListener('click', () => this._abrirModalImportacao());
        }

        if (this.elements.btnFecharModal) {
            this.elements.btnFecharModal.addEventListener('click', () => this._fecharModal());
        }

        if (this.elements.btnCancelarModal) {
            this.elements.btnCancelarModal.addEventListener('click', () => this._fecharModal());
        }

        if (this.elements.modal) {
            this.elements.modal.addEventListener('click', (event) => {
                if (event.target === this.elements.modal) this._fecharModal();
            });
        }

        if (this.elements.btnFecharModalImportacao) {
            this.elements.btnFecharModalImportacao.addEventListener('click', () => this._fecharModalImportacao());
        }

        if (this.elements.btnCancelarModalImportacao) {
            this.elements.btnCancelarModalImportacao.addEventListener('click', () => this._fecharModalImportacao());
        }

        if (this.elements.modalImportacao) {
            this.elements.modalImportacao.addEventListener('click', (event) => {
                if (event.target === this.elements.modalImportacao) this._fecharModalImportacao();
            });
        }

        if (this.elements.btnBaixarModeloImportacao) {
            this.elements.btnBaixarModeloImportacao.addEventListener('click', () => this._baixarModeloImportacao());
        }

        if (this.elements.btnPreviewImportacao) {
            this.elements.btnPreviewImportacao.addEventListener('click', () => this._gerarPreviewImportacao());
        }

        if (this.elements.btnConfirmarImportacao) {
            this.elements.btnConfirmarImportacao.addEventListener('click', () => this._confirmarImportacao());
        }

        if (this.elements.btnBaixarRelatorioImportacao) {
            this.elements.btnBaixarRelatorioImportacao.addEventListener('click', () => this._baixarRelatorioErrosImportacao());
        }

        if (this.elements.btnFecharModalHistorico) {
            this.elements.btnFecharModalHistorico.addEventListener('click', () => this._fecharModalHistorico());
        }

        if (this.elements.btnFecharRodapeModalHistorico) {
            this.elements.btnFecharRodapeModalHistorico.addEventListener('click', () => this._fecharModalHistorico());
        }

        if (this.elements.modalHistorico) {
            this.elements.modalHistorico.addEventListener('click', (event) => {
                if (event.target === this.elements.modalHistorico) this._fecharModalHistorico();
            });
        }

        if (this.elements.btnFecharModalVisualizacao) {
            this.elements.btnFecharModalVisualizacao.addEventListener('click', () => this._fecharModalVisualizacao());
        }

        if (this.elements.btnFecharRodapeModalVisualizacao) {
            this.elements.btnFecharRodapeModalVisualizacao.addEventListener('click', () => this._fecharModalVisualizacao());
        }

        if (this.elements.btnEditarPelaVisualizacao) {
            this.elements.btnEditarPelaVisualizacao.addEventListener('click', async () => {
                const magiaId = Number(this.visualizacaoAtual?.id || 0);
                if (!magiaId) return;
                this._fecharModalVisualizacao();
                await this._abrirModalEdicao(magiaId);
            });
        }

        if (Array.isArray(this.elements.viewLangButtons) && this.elements.viewLangButtons.length) {
            this.elements.viewLangButtons.forEach((button) => {
                button.addEventListener('click', () => {
                    const lang = button.dataset.viewLang;
                    if (lang) this._setIdiomaVisualizacao(lang);
                });
            });
        }

        if (this.elements.modalVisualizacao) {
            this.elements.modalVisualizacao.addEventListener('click', (event) => {
                if (event.target === this.elements.modalVisualizacao) this._fecharModalVisualizacao();
            });
        }

        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (event) => this._handleSubmit(event));
        }

        if (this.elements.btnAddClasse) {
            this.elements.btnAddClasse.addEventListener('click', () => {
                const classe = this.elements.selectClasseNova?.value || '';
                const nivel = Number(this.elements.inputNivelNova?.value || 0);
                this._adicionarClasseNivelLinha({ classe, nivel });
            });
        }

        if (this.elements.listaClasses) {
            this.elements.listaClasses.addEventListener('click', (event) => {
                const button = event.target.closest('button[data-remove-classe]');
                if (!button) return;
                const item = button.closest('.magias-classe-item');
                if (item) item.remove();
            });
        }

        if (this.elements.tabela) {
            this.elements.tabela.addEventListener('click', (event) => this._handleTabelaClick(event));
        }

        if (this.elements.inputDominio) {
            this.elements.inputDominio.addEventListener('change', () => {
                const ativo = !!this.elements.inputDominio.checked;
                if (this.elements.grupoDominios) {
                    this.elements.grupoDominios.style.display = ativo ? 'flex' : 'none';
                }
            });
        }

        if (Array.isArray(this.elements.tabs) && this.elements.tabs.length) {
            this.elements.tabs.forEach((tabButton) => {
                tabButton.addEventListener('click', () => {
                    const target = tabButton.dataset.tabTarget;
                    if (target) this._ativarAbaFormulario(target);
                });
            });
        }
    }

    _preencherOpcoesEscolas() {
        if (!this.elements.selectEscola) return;
        this.elements.selectEscola.innerHTML = ESCOLAS
            .map((escola) => `<option value="${escapeHtml(escola)}">${escapeHtml(escola)}</option>`)
            .join('');
    }

    async _carregarClasses() {
        try {
            const classes = await this.service.listarClasses();
            if (Array.isArray(classes) && classes.length > 0) {
                this.classes = classes.map((classe) => normalizeClasse(classe));
            }
        } catch (_error) {
            this._toast('warning', 'Nao foi possivel carregar classes dinamicas. Usando lista padrao.');
        }

        const options = this.classes
            .map((classe) => `<option value="${escapeHtml(classe)}">${escapeHtml(classeDisplay(classe))}</option>`)
            .join('');

        if (this.elements.filtroClasse) {
            this.elements.filtroClasse.innerHTML = `<option value="">Todas as classes</option>${options}`;
        }

        if (this.elements.selectClasseNova) {
            this.elements.selectClasseNova.innerHTML = options;
        }
    }

    async _carregarDominiosPermitidos() {
        try {
            const dominios = await this.service.listarDominios();
            if (Array.isArray(dominios) && dominios.length > 0) {
                this.dominiosPermitidos = dominios.map((d) => String(d).trim()).filter(Boolean);
            }
        } catch (_error) {
            this._toast('warning', 'Nao foi possivel carregar dominios fixos do backend. Usando lista padrao.');
        }

        if (this.elements.listaDominios) {
            this.elements.listaDominios.innerHTML = this.dominiosPermitidos
                .map((dominio) => `<option value="${escapeHtml(dominio)}"></option>`)
                .join('');
        }

        if (this.elements.hintDominios) {
            this.elements.hintDominios.textContent = `Permitidos: ${this.dominiosPermitidos.join(', ')}.`;
        }
    }

    async _carregarMagias() {
        this._setTabelaLoading(true);
        try {
            const filtros = this._coletarFiltros();
            const { items, total, skip } = await this.service.listar(filtros);
            this.magias = Array.isArray(items) ? items : [];
            this.total = Number(total || this.magias.length || 0);
            this.currentSkip = Number(skip || 0);
            this.currentPage = Math.floor(this.currentSkip / this.pageSize) + 1;
            this._renderTabela();
            this._atualizarResumo();
            this._atualizarPaginacao();
        } catch (error) {
            this._setTabelaErro(error.message || 'Erro ao carregar magias.');
            this._atualizarPaginacao();
        }
    }

    _coletarFiltros() {
        const ativo = toBooleanFromSelect(this.elements.filtroStatus?.value || '');
        return {
            nome: this.elements.filtroNome?.value?.trim() || undefined,
            classe: this.elements.filtroClasse?.value || undefined,
            nivel: this.elements.filtroNivel?.value || undefined,
            escola: this.elements.filtroEscola?.value || undefined,
            ativo,
            sort_by: this.elements.filtroOrdenacaoCampo?.value || this.sortBy,
            sort_dir: this.elements.filtroOrdenacaoDirecao?.value || this.sortDir,
            skip: this.currentSkip,
            limit: this.pageSize,
        };
    }

    _setTabelaLoading(isLoading) {
        if (!this.elements.tabela) return;
        if (!isLoading) return;
        this.elements.tabela.innerHTML = '<tr><td colspan="6" class="magias-loading">Carregando magias...</td></tr>';
    }

    _setTabelaErro(message) {
        if (!this.elements.tabela) return;
        this.elements.tabela.innerHTML = `<tr><td colspan="6" class="magias-loading">${escapeHtml(message)}</td></tr>`;
    }

    _renderTabela() {
        if (!this.elements.tabela) return;

        if (!this.magias.length) {
            this.elements.tabela.innerHTML = '<tr><td colspan="6" class="magias-loading">Nenhuma magia encontrada para os filtros atuais.</td></tr>';
            return;
        }

        this.elements.tabela.innerHTML = this.magias.map((magia) => {
            const classes = this._formatClassesNiveis(magia.classes_niveis);
            const badgeStatus = magia.ativo
                ? '<span class="magias-badge magias-badge-ativo">Ativa</span>'
                : '<span class="magias-badge magias-badge-inativo">Inativa</span>';

            return `
                <tr>
                    <td>${escapeHtml(magia.nome || '-')}</td>
                    <td>${escapeHtml(magia.escola || '-')}</td>
                    <td>${escapeHtml(classes || '-')}</td>
                    <td>${escapeHtml(magia.componentes || '-')}</td>
                    <td>${badgeStatus}</td>
                    <td>
                        <div class="magias-acoes" data-magia-id="${Number(magia.id)}">
                            <button type="button" class="btn-acao" data-action="visualizar">Visualizar</button>
                            <button type="button" class="btn-acao" data-action="historico">Historico</button>
                            <button type="button" class="btn-acao" data-action="editar">Editar</button>
                            <button type="button" class="btn-acao" data-action="toggle">${magia.ativo ? 'Desativar' : 'Reativar'}</button>
                            <button type="button" class="btn-acao btn-acao-danger" data-action="excluir">Excluir</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    _formatClassesNiveis(items) {
        if (!Array.isArray(items) || !items.length) return '';
        return items
            .slice()
            .sort((a, b) => Number(a.nivel) - Number(b.nivel) || String(a.classe).localeCompare(String(b.classe)))
            .map((item) => `${classeDisplay(item.classe)} ${item.nivel}`)
            .join(' • ');
    }

    _atualizarResumo() {
        const ativas = this.magias.filter((magia) => magia.ativo).length;
        const inativas = this.magias.filter((magia) => !magia.ativo).length;

        if (this.elements.statTotal) this.elements.statTotal.textContent = String(this.total);
        if (this.elements.statAtivas) this.elements.statAtivas.textContent = String(ativas);
        if (this.elements.statInativas) this.elements.statInativas.textContent = String(inativas);
        if (this.elements.resumoFiltrado) {
            const inicio = this.total === 0 ? 0 : this.currentSkip + 1;
            const fim = this.currentSkip + this.magias.length;
            this.elements.resumoFiltrado.textContent = `${this.magias.length} resultado(s) nesta pagina. Exibindo ${inicio}-${fim} de ${this.total}.`;
        }
    }

    _atualizarPaginacao() {
        const totalPages = Math.max(1, Math.ceil(this.total / this.pageSize));
        const hasPrev = this.currentPage > 1;
        const hasNext = this.currentPage < totalPages;

        if (this.elements.indicadorPagina) {
            this.elements.indicadorPagina.textContent = `Pagina ${this.currentPage} de ${totalPages}`;
        }
        if (this.elements.btnPaginaAnterior) {
            this.elements.btnPaginaAnterior.disabled = !hasPrev;
        }
        if (this.elements.btnPaginaProxima) {
            this.elements.btnPaginaProxima.disabled = !hasNext;
        }
    }

    _abrirModalNova() {
        this.editingId = null;
        if (this.elements.modalTitulo) this.elements.modalTitulo.textContent = 'Nova Magia';
        if (this.elements.form) this.elements.form.reset();
        if (this.elements.listaClasses) this.elements.listaClasses.innerHTML = '';
        if (this.elements.grupoDominios) this.elements.grupoDominios.style.display = 'none';
        this._ativarAbaFormulario('pt');
        if (this.elements.modal) this.elements.modal.classList.add('show');
        this._adicionarClasseNivelLinha({ classe: this.classes[0] || 'MAGO', nivel: 0 });
    }

    async _abrirModalEdicao(magiaId) {
        this.editingId = magiaId;
        try {
            const magia = await this.service.obter(magiaId);
            if (this.elements.modalTitulo) this.elements.modalTitulo.textContent = `Editar Magia #${magiaId}`;
            this._preencherFormulario(magia);
            this._ativarAbaFormulario('pt');
            if (this.elements.modal) this.elements.modal.classList.add('show');
        } catch (error) {
            this._toast('error', error.message || 'Nao foi possivel carregar dados da magia.');
        }
    }

    _ativarAbaFormulario(target) {
        if (!Array.isArray(this.elements.tabs) || !Array.isArray(this.elements.tabPanels)) return;

        this.elements.tabs.forEach((tab) => {
            const active = tab.dataset.tabTarget === target;
            tab.classList.toggle('active', active);
            tab.setAttribute('aria-selected', active ? 'true' : 'false');
        });

        this.elements.tabPanels.forEach((panel) => {
            const active = panel.dataset.tabPanel === target;
            panel.classList.toggle('active', active);
            panel.hidden = !active;
        });
    }

    _preencherFormulario(magia) {
        if (!this.elements.form) return;

        const setValue = (id, value) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = value == null ? '' : String(value);
        };

        setValue('inputNomeMagia', magia.nome);
        setValue('inputNomeEnMagia', magia.nome_en);
        setValue('inputEscolaMagia', magia.escola);
        setValue('inputSubEscolaMagia', magia.sub_escola);
        setValue('inputDescritorMagia', magia.descritor);
        setValue('inputComponentesMagia', magia.componentes);
        setValue('inputComponenteExtraMagia', magia.componente_extra);
        setValue('inputAlcanceMagia', magia.alcance);
        setValue('inputAreaEfeitoMagia', magia.area_efeito);
        setValue('inputDuracaoMagia', magia.duracao);
        setValue('inputTempoConjuracaoMagia', magia.tempo_conjuracao);
        setValue('inputDanoMagia', magia.dano);
        setValue('inputTesteResistenciaMagia', magia.teste_resistencia);
        setValue('inputResistenciaTextoMagia', magia.resistencia_magia_texto);
        setValue('inputDescricaoMagia', magia.descricao);
        setValue('inputDescricaoEnMagia', magia.descricao_en);
        setValue('inputDominiosMagia', magia.dominios);
        setValue('inputPaginaReferenciaMagia', magia.pagina_referencia);

        const resistenciaMagica = document.getElementById('inputResistenciaMagicaMagia');
        if (resistenciaMagica) resistenciaMagica.checked = !!magia.resistencia_magica;

        if (this.elements.inputDominio) {
            this.elements.inputDominio.checked = !!magia.e_magia_dominio;
        }

        if (this.elements.grupoDominios) {
            this.elements.grupoDominios.style.display = magia.e_magia_dominio ? 'flex' : 'none';
        }

        if (this.elements.listaClasses) {
            this.elements.listaClasses.innerHTML = '';
            const classes = Array.isArray(magia.classes_niveis) ? magia.classes_niveis : [];
            if (!classes.length) {
                this._adicionarClasseNivelLinha({ classe: this.classes[0] || 'MAGO', nivel: Number(magia.nivel || 0) });
            } else {
                classes.forEach((item) => this._adicionarClasseNivelLinha({
                    classe: normalizeClasse(item.classe),
                    nivel: Number(item.nivel || 0),
                }));
            }
        }
    }

    _adicionarClasseNivelLinha(item) {
        if (!this.elements.listaClasses) return;

        const classe = normalizeClasse(item?.classe || this.classes[0] || 'MAGO');
        const nivel = Number.isFinite(Number(item?.nivel)) ? Number(item.nivel) : 0;

        const row = document.createElement('div');
        row.className = 'magias-classe-item';

        const options = this.classes
            .map((value) => `<option value="${escapeHtml(value)}" ${value === classe ? 'selected' : ''}>${escapeHtml(classeDisplay(value))}</option>`)
            .join('');

        row.innerHTML = `
            <select class="magias-classe-select" data-classe>
                ${options}
            </select>
            <input type="number" min="0" max="9" value="${nivel}" class="magias-classe-nivel" data-nivel>
            <button type="button" class="btn-acao btn-acao-danger" data-remove-classe>Remover</button>
        `;

        this.elements.listaClasses.appendChild(row);
    }

    _fecharModal() {
        if (this.elements.modal) this.elements.modal.classList.remove('show');
        this.editingId = null;
    }

    _abrirModalImportacao() {
        this.importPreview = null;
        this.importErrors = [];
        if (this.elements.inputArquivoImportacao) this.elements.inputArquivoImportacao.value = '';
        this._renderPreviewImportacao([]);
        this._renderErrosImportacao([]);
        if (this.elements.resumoImportacao) {
            this.elements.resumoImportacao.textContent = 'Nenhum arquivo analisado ainda.';
        }
        if (this.elements.btnConfirmarImportacao) this.elements.btnConfirmarImportacao.disabled = true;
        if (this.elements.btnBaixarRelatorioImportacao) this.elements.btnBaixarRelatorioImportacao.disabled = true;
        if (this.elements.modalImportacao) this.elements.modalImportacao.classList.add('show');
    }

    _fecharModalImportacao() {
        if (this.elements.modalImportacao) this.elements.modalImportacao.classList.remove('show');
    }

    async _baixarModeloImportacao() {
        try {
            const blob = await this.service.baixarModeloImportacao();
            this._downloadBlob(blob, 'modelo_importacao_magias.xlsx');
            this._toast('success', 'Modelo de importacao baixado com sucesso.');
        } catch (error) {
            this._toast('error', error.message || 'Falha ao baixar modelo de importacao.');
        }
    }

    async _gerarPreviewImportacao() {
        const file = this.elements.inputArquivoImportacao?.files?.[0];
        if (!file) {
            this._toast('warning', 'Selecione um arquivo .xlsx ou .xls para gerar preview.');
            return;
        }

        if (this.elements.btnPreviewImportacao) this.elements.btnPreviewImportacao.disabled = true;
        if (this.elements.resumoImportacao) this.elements.resumoImportacao.textContent = 'Processando arquivo...';

        try {
            const preview = await this.service.previewImportacao(file);
            this.importPreview = preview;
            this.importErrors = Array.isArray(preview.erros) ? preview.erros : [];

            this._renderPreviewImportacao(Array.isArray(preview.preview) ? preview.preview : []);
            this._renderErrosImportacao(this.importErrors);

            if (this.elements.resumoImportacao) {
                this.elements.resumoImportacao.textContent = [
                    `Linhas: ${Number(preview.total_linhas || 0)}`,
                    `Validas: ${Number(preview.validas || 0)}`,
                    `Invalidas: ${Number(preview.invalidas || 0)}`,
                ].join(' | ');
            }

            if (this.elements.btnConfirmarImportacao) {
                this.elements.btnConfirmarImportacao.disabled = !preview.import_id || Number(preview.validas || 0) <= 0;
            }
            if (this.elements.btnBaixarRelatorioImportacao) {
                this.elements.btnBaixarRelatorioImportacao.disabled = this.importErrors.length === 0;
            }

            if (Number(preview.validas || 0) === 0) {
                this._toast('warning', 'Nenhuma linha valida encontrada no arquivo.');
            } else {
                this._toast('success', 'Preview gerado. Revise as linhas antes de confirmar.');
            }
        } catch (error) {
            this.importPreview = null;
            this.importErrors = [];
            this._renderPreviewImportacao([]);
            this._renderErrosImportacao([]);
            if (this.elements.btnConfirmarImportacao) this.elements.btnConfirmarImportacao.disabled = true;
            if (this.elements.btnBaixarRelatorioImportacao) this.elements.btnBaixarRelatorioImportacao.disabled = true;
            this._toast('error', error.message || 'Falha ao processar arquivo para preview.');
            if (this.elements.resumoImportacao) this.elements.resumoImportacao.textContent = 'Falha no preview.';
        } finally {
            if (this.elements.btnPreviewImportacao) this.elements.btnPreviewImportacao.disabled = false;
        }
    }

    async _confirmarImportacao() {
        const importId = this.importPreview?.import_id;
        if (!importId) {
            this._toast('warning', 'Gere um preview valido antes de confirmar a importacao.');
            return;
        }

        if (this.elements.btnConfirmarImportacao) this.elements.btnConfirmarImportacao.disabled = true;

        try {
            const result = await this.service.confirmarImportacao(importId);
            const importadas = Number(result.importadas || 0);
            const falhas = Number(result.falhas || 0);
            const erros = Array.isArray(result.erros) ? result.erros : [];
            this.importErrors = erros;
            this._renderErrosImportacao(erros);
            if (this.elements.btnBaixarRelatorioImportacao) {
                this.elements.btnBaixarRelatorioImportacao.disabled = erros.length === 0;
            }

            this._toast('success', `Importacao concluida: ${importadas} importada(s), ${falhas} falha(s).`);
            await this._carregarMagias();

            if (this.elements.resumoImportacao) {
                this.elements.resumoImportacao.textContent = `Resultado final | Importadas: ${importadas} | Falhas: ${falhas}`;
            }

            this.importPreview = null;
            if (this.elements.btnConfirmarImportacao) this.elements.btnConfirmarImportacao.disabled = true;
        } catch (error) {
            this._toast('error', error.message || 'Falha ao confirmar importacao.');
            if (this.elements.btnConfirmarImportacao) this.elements.btnConfirmarImportacao.disabled = false;
        }
    }

    _renderPreviewImportacao(items) {
        if (!this.elements.tabelaPreviewImportacao) return;

        if (!Array.isArray(items) || items.length === 0) {
            this.elements.tabelaPreviewImportacao.innerHTML = '<tr><td colspan="4" class="magias-loading">Sem preview.</td></tr>';
            return;
        }

        this.elements.tabelaPreviewImportacao.innerHTML = items.slice(0, 20).map((item) => {
            const classes = this._formatClassesNiveis(item.classes_niveis || []);
            const dominio = item.e_magia_dominio ? (item.dominios || '-') : 'Nao';
            return `
                <tr>
                    <td>${escapeHtml(item.nome || '-')}</td>
                    <td>${escapeHtml(item.escola || '-')}</td>
                    <td>${escapeHtml(classes || '-')}</td>
                    <td>${escapeHtml(dominio)}</td>
                </tr>
            `;
        }).join('');
    }

    _renderErrosImportacao(erros) {
        if (!this.elements.listaErrosImportacao) return;
        if (!Array.isArray(erros) || erros.length === 0) {
            this.elements.listaErrosImportacao.innerHTML = '<li>Nenhum erro para exibir.</li>';
            return;
        }
        this.elements.listaErrosImportacao.innerHTML = erros.map((erro) => {
            const linha = Number(erro.linha || 0);
            const campo = String(erro.campo || 'geral');
            const mensagem = String(erro.mensagem || 'Erro desconhecido');
            return `<li>Linha ${linha} | ${escapeHtml(campo)} | ${escapeHtml(mensagem)}</li>`;
        }).join('');
    }

    _baixarRelatorioErrosImportacao() {
        if (!Array.isArray(this.importErrors) || this.importErrors.length === 0) {
            this._toast('warning', 'Nao ha erros para exportar no relatorio.');
            return;
        }

        const lines = [
            'linha,campo,mensagem',
            ...this.importErrors.map((erro) => {
                const linha = Number(erro.linha || 0);
                const campo = String(erro.campo || '').replaceAll('"', '""');
                const mensagem = String(erro.mensagem || '').replaceAll('"', '""');
                return `${linha},"${campo}","${mensagem}"`;
            }),
        ];
        const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
        const fileName = `relatorio_erros_importacao_magias_${Date.now()}.csv`;
        this._downloadBlob(blob, fileName);
    }

    _downloadBlob(blob, fileName) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }

    async _handleSubmit(event) {
        event.preventDefault();

        const payload = this._coletarPayloadFormulario();
        if (!payload) return;

        try {
            if (this.editingId) {
                await this.service.atualizar(this.editingId, payload);
                this._toast('success', 'Magia atualizada com sucesso.');
            } else {
                await this.service.criar(payload);
                this._toast('success', 'Magia criada com sucesso.');
            }

            this._fecharModal();
            await this._carregarMagias();
        } catch (error) {
            this._toast('error', error.message || 'Falha ao salvar magia.');
        }
    }

    _coletarPayloadFormulario() {
        const get = (id) => document.getElementById(id);
        const value = (id) => (get(id)?.value || '').trim();

        const classes_niveis = this._coletarClassesNiveis();
        if (!classes_niveis.length) {
            this._toast('warning', 'Adicione ao menos uma classe com nivel para a magia.');
            return null;
        }

        const nome = value('inputNomeMagia');
        const escola = value('inputEscolaMagia');
        const descricao = value('inputDescricaoMagia');

        if (!nome || !escola || !descricao) {
            this._toast('warning', 'Preencha os campos obrigatorios: nome, escola e descricao.');
            return null;
        }

        const eMagiaDominio = !!get('inputMagiaDominio')?.checked;
        const dominios = value('inputDominiosMagia');
        if (eMagiaDominio && !dominios) {
            this._toast('warning', 'Informe dominios para magias marcadas como dominio.');
            return null;
        }

        let dominiosNormalizados = null;
        if (eMagiaDominio) {
            const validacao = this._validarDominios(dominios);
            if (!validacao.ok) {
                this._toast('warning', validacao.mensagem);
                return null;
            }
            dominiosNormalizados = validacao.valor;
        }

        const payload = {
            nome,
            nome_en: value('inputNomeEnMagia') || null,
            escola,
            sub_escola: value('inputSubEscolaMagia') || null,
            descritor: value('inputDescritorMagia') || null,
            componentes: value('inputComponentesMagia') || null,
            componente_extra: value('inputComponenteExtraMagia') || null,
            alcance: value('inputAlcanceMagia') || null,
            area_efeito: value('inputAreaEfeitoMagia') || null,
            duracao: value('inputDuracaoMagia') || null,
            tempo_conjuracao: value('inputTempoConjuracaoMagia') || null,
            dano: value('inputDanoMagia') || null,
            teste_resistencia: value('inputTesteResistenciaMagia') || null,
            resistencia_magica: !!get('inputResistenciaMagicaMagia')?.checked,
            resistencia_magia_texto: value('inputResistenciaTextoMagia') || null,
            descricao,
            descricao_en: value('inputDescricaoEnMagia') || null,
            e_magia_dominio: eMagiaDominio,
            dominios: eMagiaDominio ? dominiosNormalizados : null,
            pagina_referencia: value('inputPaginaReferenciaMagia') ? Number(value('inputPaginaReferenciaMagia')) : null,
            classes_niveis,
        };

        return payload;
    }

    _coletarClassesNiveis() {
        if (!this.elements.listaClasses) return [];

        const rows = this.elements.listaClasses.querySelectorAll('.magias-classe-item');
        const classes = [];
        const used = new Set();

        rows.forEach((row) => {
            const classe = normalizeClasse(row.querySelector('[data-classe]')?.value || '');
            const nivel = Number(row.querySelector('[data-nivel]')?.value || 0);
            if (!classe) return;
            if (!Number.isFinite(nivel) || nivel < 0 || nivel > 9) return;
            if (used.has(classe)) return;
            used.add(classe);
            classes.push({ classe, nivel });
        });

        return classes;
    }

    _validarDominios(raw) {
        const allowMap = new Map(
            this.dominiosPermitidos.map((dominio) => [this._normalizarDominio(dominio), dominio]),
        );
        const itens = String(raw || '')
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean);

        if (!itens.length) {
            return { ok: false, mensagem: 'Informe ao menos um dominio valido.' };
        }

        const vistos = new Set();
        const canonical = [];
        const invalidos = [];

        itens.forEach((item) => {
            const key = this._normalizarDominio(item);
            const dominio = allowMap.get(key);
            if (!dominio) {
                invalidos.push(item);
                return;
            }
            if (vistos.has(key)) return;
            vistos.add(key);
            canonical.push(dominio);
        });

        if (invalidos.length) {
            return {
                ok: false,
                mensagem: `Dominio invalido: ${invalidos.join(', ')}. Permitidos: ${this.dominiosPermitidos.join(', ')}.`,
            };
        }

        return { ok: true, valor: canonical.join(', ') };
    }

    _normalizarDominio(value) {
        return String(value || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim()
            .toUpperCase();
    }

    async _handleTabelaClick(event) {
        const actionButton = event.target.closest('button[data-action]');
        if (!actionButton) return;

        const rowActions = actionButton.closest('[data-magia-id]');
        if (!rowActions) return;

        const magiaId = Number(rowActions.dataset.magiaId);
        const action = actionButton.dataset.action;

        if (!Number.isFinite(magiaId)) return;

        if (action === 'visualizar') {
            await this._abrirModalVisualizacao(magiaId);
            return;
        }

        if (action === 'historico') {
            await this._abrirModalHistorico(magiaId);
            return;
        }

        if (action === 'editar') {
            await this._abrirModalEdicao(magiaId);
            return;
        }

        const magia = this.magias.find((item) => Number(item.id) === magiaId);
        if (!magia) return;

        if (action === 'toggle') {
            await this._confirmarToggleStatus(magia);
            return;
        }

        if (action === 'excluir') {
            await this._confirmarExclusao(magia);
            return;
        }
    }

    async _abrirModalHistorico(magiaId) {
        const magia = this.magias.find((item) => Number(item.id) === Number(magiaId));
        if (this.elements.tituloModalHistorico) {
            this.elements.tituloModalHistorico.textContent = `Historico | ${magia?.nome || `Magia #${magiaId}`}`;
        }
        if (this.elements.listaHistorico) {
            this.elements.listaHistorico.innerHTML = '<article class="magias-history-item"><header><strong>Carregando historico...</strong></header></article>';
        }
        if (this.elements.modalHistorico) this.elements.modalHistorico.classList.add('show');

        try {
            const items = await this.service.listarHistorico(magiaId, 80);
            this._renderHistorico(items);
        } catch (error) {
            this._renderHistorico([]);
            this._toast('error', error.message || 'Falha ao carregar historico da magia.');
        }
    }

    _fecharModalHistorico() {
        if (this.elements.modalHistorico) this.elements.modalHistorico.classList.remove('show');
    }

    async _abrirModalVisualizacao(magiaId) {
        try {
            const magia = await this.service.obter(magiaId);
            this.visualizacaoAtual = magia;
            this.visualizacaoIdioma = 'pt';

            if (this.elements.tituloModalVisualizacao) {
                this.elements.tituloModalVisualizacao.textContent = `Visualizacao | ${magia?.nome || `Magia #${magiaId}`}`;
            }
            if (this.elements.subtituloModalVisualizacao) {
                this.elements.subtituloModalVisualizacao.textContent = this._formatClassesNiveis(magia?.classes_niveis || []);
            }

            this._renderVisualizacaoMagia(magia);
            this._setIdiomaVisualizacao('pt');
            if (this.elements.modalVisualizacao) this.elements.modalVisualizacao.classList.add('show');
        } catch (error) {
            this._toast('error', error.message || 'Nao foi possivel carregar detalhes da magia.');
        }
    }

    _fecharModalVisualizacao() {
        if (this.elements.modalVisualizacao) this.elements.modalVisualizacao.classList.remove('show');
        this.visualizacaoAtual = null;
    }

    _setIdiomaVisualizacao(lang) {
        this.visualizacaoIdioma = lang === 'en' ? 'en' : 'pt';

        if (Array.isArray(this.elements.viewLangButtons)) {
            this.elements.viewLangButtons.forEach((button) => {
                const active = button.dataset.viewLang === this.visualizacaoIdioma;
                button.classList.toggle('active', active);
                button.setAttribute('aria-selected', active ? 'true' : 'false');
            });
        }

        if (Array.isArray(this.elements.viewPanels)) {
            this.elements.viewPanels.forEach((panel) => {
                const active = panel.dataset.viewPanel === this.visualizacaoIdioma;
                panel.classList.toggle('active', active);
                panel.hidden = !active;
            });
        }
    }

    _renderVisualizacaoMagia(magia) {
        const row = (label, value) => `
            <article class="magias-view-field">
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value == null || value === '' ? '-' : String(value))}</strong>
            </article>
        `;

        const boolText = (value) => (value ? 'Sim' : 'Nao');
        const classes = this._formatClassesNiveis(magia?.classes_niveis || []);

        if (this.elements.conteudoVisualizacaoPt) {
            this.elements.conteudoVisualizacaoPt.innerHTML = [
                row('Nome', magia?.nome),
                row('Escola', magia?.escola),
                row('Sub Escola', magia?.sub_escola),
                row('Descritor', magia?.descritor),
                row('Classes/Niveis', classes),
                row('Componentes', magia?.componentes),
                row('Componente extra', magia?.componente_extra),
                row('Tempo de conjuracao', magia?.tempo_conjuracao),
                row('Alcance', magia?.alcance),
                row('Area/Efeito', magia?.area_efeito),
                row('Duracao', magia?.duracao),
                row('Dano', magia?.dano),
                row('Teste de resistencia', magia?.teste_resistencia),
                row('Resistencia magica', boolText(!!magia?.resistencia_magica)),
                row('Resistencia a magia (texto)', magia?.resistencia_magia_texto),
                row('Magia de dominio', boolText(!!magia?.e_magia_dominio)),
                row('Dominios', magia?.dominios),
                row('Pagina de referencia', magia?.pagina_referencia),
                row('Status', magia?.ativo ? 'Ativa' : 'Inativa'),
                row('Descricao PT', magia?.descricao),
            ].join('');
        }

        if (this.elements.conteudoVisualizacaoEn) {
            this.elements.conteudoVisualizacaoEn.innerHTML = [
                row('Name (EN)', magia?.nome_en),
                row('Description (EN)', magia?.descricao_en),
                row('School (PT source)', magia?.escola),
                row('Class levels', classes),
                row('Status', magia?.ativo ? 'Active' : 'Inactive'),
            ].join('');
        }
    }

    _renderHistorico(items) {
        if (!this.elements.listaHistorico) return;
        if (!Array.isArray(items) || items.length === 0) {
            this.elements.listaHistorico.innerHTML = '<article class="magias-history-item"><header><strong>Sem registros de historico para esta magia.</strong></header></article>';
            return;
        }

        this.elements.listaHistorico.innerHTML = items.map((item) => {
            const quando = item.criado_em ? new Date(item.criado_em).toLocaleString('pt-BR') : '-';
            const usuario = Number(item.usuario_id || 0) > 0 ? `Usuario #${item.usuario_id}` : 'Usuario desconhecido';
            const mudancas = this._calcularMudancasHistorico(item?.dados_anteriores, item?.dados_novos);
            const resumoMudancas = mudancas.length
                ? mudancas.map((m) => `<li>${escapeHtml(m)}</li>`).join('')
                : '<li>Sem diff detalhado disponivel.</li>';

            return `
                <article class="magias-history-item">
                    <header>
                        <strong>${escapeHtml(item.acao || 'ACAO')}</strong>
                        <span>${escapeHtml(quando)}</span>
                    </header>
                    <p>${escapeHtml(usuario)}</p>
                    <ul>${resumoMudancas}</ul>
                </article>
            `;
        }).join('');
    }

    _calcularMudancasHistorico(antes, depois) {
        const oldData = (antes && typeof antes === 'object') ? antes : {};
        const newData = (depois && typeof depois === 'object') ? depois : {};
        const keys = Array.from(new Set([...Object.keys(oldData), ...Object.keys(newData)]));

        const normalizeValue = (value) => {
            if (Array.isArray(value)) return JSON.stringify(value);
            if (value && typeof value === 'object') return JSON.stringify(value);
            if (value === null || value === undefined) return '';
            return String(value);
        };

        const changes = [];
        for (const key of keys) {
            if (key === 'id') continue;
            const oldValue = normalizeValue(oldData[key]);
            const newValue = normalizeValue(newData[key]);
            if (oldValue === newValue) continue;

            if (oldValue && !newValue) {
                changes.push(`${key}: removido (${oldValue})`);
            } else if (!oldValue && newValue) {
                changes.push(`${key}: definido como ${newValue}`);
            } else {
                changes.push(`${key}: ${oldValue} -> ${newValue}`);
            }
        }
        return changes.slice(0, 12);
    }

    async _confirmarToggleStatus(magia) {
        const title = magia.ativo ? 'Desativar magia' : 'Reativar magia';
        const text = magia.ativo
            ? `Deseja desativar ${magia.nome}? Ela deixara de aparecer nas buscas padrao.`
            : `Deseja reativar ${magia.nome}?`;

        this._confirmar({
            titulo: title,
            texto: text,
            textoConfirmar: magia.ativo ? 'Desativar' : 'Reativar',
            classeConfirmar: magia.ativo ? 'modal-confirm-btn-perigo' : 'modal-confirm-ok',
            onConfirmar: async () => {
                try {
                    if (magia.ativo) await this.service.desativar(magia.id);
                    else await this.service.reativar(magia.id);
                    this._toast('success', `Magia ${magia.ativo ? 'desativada' : 'reativada'} com sucesso.`);
                    await this._carregarMagias();
                } catch (error) {
                    this._toast('error', error.message || 'Falha ao alterar status da magia.');
                }
            },
        });
    }

    async _confirmarExclusao(magia) {
        this._confirmar({
            titulo: 'Excluir magia',
            texto: `Deseja excluir permanentemente ${magia.nome}? Esta acao e irreversivel.`,
            textoConfirmar: 'Excluir',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await this.service.excluir(magia.id);
                    this._toast('success', 'Magia excluida com sucesso.');
                    await this._carregarMagias();
                } catch (error) {
                    this._toast('error', error.message || 'Falha ao excluir magia.');
                }
            },
        });
    }

    _confirmar(options) {
        if (window.ModalConfirm && typeof window.ModalConfirm.mostrar === 'function') {
            window.ModalConfirm.mostrar(options);
            return;
        }

        const ok = window.confirm(options.texto || 'Deseja continuar?');
        if (ok && typeof options.onConfirmar === 'function') {
            options.onConfirmar();
        }
    }

    _toast(type, message) {
        if (window.Toast && typeof window.Toast[type] === 'function') {
            window.Toast[type](message);
            return;
        }
        if (type === 'error') console.error(message);
    }
}

export { MagiasAdminController };
