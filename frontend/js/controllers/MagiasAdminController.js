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
            btnNova: document.getElementById('btnNovaMagia'),
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
            grupoDominios: document.getElementById('grupoDominiosMagia'),
            selectEscola: document.getElementById('inputEscolaMagia'),
        };
    }

    async init() {
        this._preencherHeaderSessao();
        this._bindEvents();
        this._preencherOpcoesEscolas();
        await this._carregarClasses();
        await this._carregarMagias();
    }

    _preencherHeaderSessao() {
        if (window.AuthService) {
            if (this.elements.nomeAdminAtual) this.elements.nomeAdminAtual.textContent = window.AuthService.getNome();
            if (this.elements.perfilAdminAtual) this.elements.perfilAdminAtual.textContent = window.AuthService.getPerfil();
        }
    }

    _bindEvents() {
        const reload = () => this._carregarMagias();

        if (this.elements.filtroNome) {
            this.elements.filtroNome.addEventListener('input', () => {
                clearTimeout(this._debounceBusca);
                this._debounceBusca = setTimeout(reload, 250);
            });
        }

        [this.elements.filtroClasse, this.elements.filtroNivel, this.elements.filtroEscola, this.elements.filtroStatus]
            .filter(Boolean)
            .forEach((el) => el.addEventListener('change', reload));

        if (this.elements.btnNova) {
            this.elements.btnNova.addEventListener('click', () => this._abrirModalNova());
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

    async _carregarMagias() {
        this._setTabelaLoading(true);
        try {
            const filtros = this._coletarFiltros();
            const { items, total } = await this.service.listar(filtros);
            this.magias = Array.isArray(items) ? items : [];
            this.total = Number(total || this.magias.length || 0);
            this._renderTabela();
            this._atualizarResumo();
        } catch (error) {
            this._setTabelaErro(error.message || 'Erro ao carregar magias.');
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
            this.elements.resumoFiltrado.textContent = `${this.magias.length} resultado(s) carregados.`;
        }
    }

    _abrirModalNova() {
        this.editingId = null;
        if (this.elements.modalTitulo) this.elements.modalTitulo.textContent = 'Nova Magia';
        if (this.elements.form) this.elements.form.reset();
        if (this.elements.listaClasses) this.elements.listaClasses.innerHTML = '';
        if (this.elements.grupoDominios) this.elements.grupoDominios.style.display = 'none';
        if (this.elements.modal) this.elements.modal.classList.add('show');
        this._adicionarClasseNivelLinha({ classe: this.classes[0] || 'MAGO', nivel: 0 });
    }

    async _abrirModalEdicao(magiaId) {
        this.editingId = magiaId;
        try {
            const magia = await this.service.obter(magiaId);
            if (this.elements.modalTitulo) this.elements.modalTitulo.textContent = `Editar Magia #${magiaId}`;
            this._preencherFormulario(magia);
            if (this.elements.modal) this.elements.modal.classList.add('show');
        } catch (error) {
            this._toast('error', error.message || 'Nao foi possivel carregar dados da magia.');
        }
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
            dominios: eMagiaDominio ? dominios : null,
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

    async _handleTabelaClick(event) {
        const actionButton = event.target.closest('button[data-action]');
        if (!actionButton) return;

        const rowActions = actionButton.closest('[data-magia-id]');
        if (!rowActions) return;

        const magiaId = Number(rowActions.dataset.magiaId);
        const action = actionButton.dataset.action;

        if (!Number.isFinite(magiaId)) return;

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
        }
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
        else console.log(message);
    }
}

export { MagiasAdminController };
