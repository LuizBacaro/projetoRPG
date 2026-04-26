/**
 * DashboardController.js
 * SOLID: SRP - gerencia apenas dashboard de combatentes
 * Dependências globais: AuthService, Toast, ModalConfirm, AtaqueService
 *
 * Nota: a escolha/edicao de Divindade foi movida para a ficha do personagem.
 * O dashboard apenas preserva o valor ja gravado atraves de um input hidden.
 */

class DashboardController {

    constructor() {
        // ✅ Validar dependências críticas
        if (typeof AuthService === 'undefined') {
            console.error('❌ AuthService não disponível');
            return;
        }
        if (typeof Toast === 'undefined') {
            console.error('❌ Toast não disponível');
            return;
        }
        if (typeof ModalConfirm === 'undefined') {
            console.error('⚠️ ModalConfirm não disponível (funcionalidade de exclusão comprometida)');
        }

        this.service            = new CombatenteServiceGlobal();
        this.ataqueService      = new AtaqueService();
        this.divindadeService   = (typeof DivindadeCustomService !== 'undefined')
            ? new DivindadeCustomService()
            : null;
        this.campanhaService    = (typeof CampanhaService !== 'undefined')
            ? new CampanhaService()
            : null;
        this.filtroAtual        = 'todos';
        this.escopoMestre       = this._lerEscopoMestrePersistido();
        this.combatenteEmEdicao = null;
        this.actions             = {};
        this.perfil              = AuthService.getPerfil();
        // Cache local das divindades do catalogo oficial (carregado sob demanda ao
        // abrir o modal "Nova Divindade"). Usado para popular o select de domínios.
        this._dominiosCatalogoCache = null;
        this.racasDisponiveis    = [];
        this.racaSlugPorNome     = new Map();
        this.racaDetalheCache    = new Map();
        this.campanhas           = [];
        this.sessoesCampanha     = [];
        this.sessaoEmEdicaoId    = null;
        this.filtroTipoParticipanteCampanha = 'todos';
        this.personagensDisponiveisCampanha = [];
        this.campanhaEmEdicaoId  = null;
        this.snapshotCampanhaEmEdicao = null;
        this.rules               = window.CombatRules || {
            isTipoRestritoParaMestre: (tipo) => tipo === 'monstro' || tipo === 'npc',
            tipoPermitidoParaPerfil: (tipo, isMestre) => {
                if (isMestre) return tipo || null;
                if (!tipo || tipo === 'monstro' || tipo === 'npc') return 'jogador';
                return tipo;
            },
            countByTipo: (combatentes, tipo) => (combatentes || []).filter(c => c.tipo === tipo).length,
            isTipoJogador: (tipo) => tipo === 'jogador',
            isTipoMonstro: (tipo) => tipo === 'monstro',
        };

        this._registrarGlobais();
        this._inicializar();
    }

    _isMestre() {
        return this.perfil === 'mestre' || this.perfil === 'administrador';
    }

    _registrarGlobais() {
        const self = this;

        this.actions.fecharModalCadastro = () => self._fecharModal('modalCadastroJogador');
        this.actions.fecharModalCadastroMonstro = () => self._fecharModal('modalCadastroMonstro');
        this.actions.fecharModalCadastroNPC = () => self._fecharModal('modalCadastroNPC');
        this.actions.fecharSeletorTipo = () => self._fecharModal('seletorTipo');
        this.actions.fecharModalEdicao = () => self._fecharModal('modalEdicaoDashboard');

        this.actions.abrirModalCadastro = (tipo) => {
            if (!self._isMestre() && self.rules.isTipoRestritoParaMestre(tipo)) {
                Toast.error('Acesso restrito: apenas Mestre pode cadastrar monstros e NPCs.');
                return;
            }
            self._fecharModal('seletorTipo');
            const mapa = { jogador: 'modalCadastroJogador', monstro: 'modalCadastroMonstro', npc: 'modalCadastroNPC' };
            self._abrirModal(mapa[tipo]);
        };

        this.actions.confirmarDelecao = () => self._deletarCombatente();
        this.actions.atualizarModificador = (input) => self._calcularModificador(input);
        this.actions.previewImagemUpload = (input, previewId, imgId, placeholderId) => self._previewImagem(input, previewId, imgId, placeholderId);
        this.actions.removerImagem = () => self._removerImagem('', false);
        this.actions.removerImagemMonstro = () => self._removerImagem('Monstro', false);
        this.actions.removerImagemNPC = () => self._removerImagem('NPC', false);
        this.actions.removerImagemEdicao = () => self._removerImagem('', true);
        this.actions.adicionarLinhaAtaque = () => self._adicionarLinhaAtaque();
        this.actions.removerLinhaAtaque = (btn) => btn.closest('.ataque-linha').remove();
        this.actions.abrirPaginaPericias = () => self._abrirPaginaPericias();

        // Um único namespace global para ações inline do dashboard.
        window.dashboardActions = this.actions;
    }

    _inicializar() {
        // ✅ NOVO: Configurar header do usuário
        window.AuthService.configurarHeaderUsuario();
        this._configurarLinksGovernanca();

        this._aplicarRestricoesPerfil();
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarFiltroEscopo();
        this._configurarBotaoNovo();
        this._configurarCombosRaca();
        this._carregarRacasCatalogo();
        this._configurarFormCadastro('formCadastroJogador', 'jogador', 'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro', 'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC', 'npc', 'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarAcoesModaisSemInline();
        this._configurarUpload('');
        this._configurarUpload('Monstro');
        this._configurarUpload('NPC');
        this._configurarUploadEdicao();
        this._configurarDivindadesCustom();
        this._configurarFecharPainelCampanhas();
        this._configurarSubAbasCampanhas();
        this._configurarCampanhas();
        this.carregarCombatentes();
    }

    _getAuthHeader() {
        const h = {};
        if (typeof AuthService !== 'undefined') {
            const token = AuthService.getToken();
            if (token) h.Authorization = `Bearer ${token}`;
        }
        return h;
    }

    _configurarLinksGovernanca() {
        const linkMagias = document.getElementById('linkMagias');
        if (linkMagias) {
            linkMagias.style.display = this._isMestre() ? '' : 'none';
        }
        const btnNovaDiv = document.getElementById('btnNovaDivindade');
        if (btnNovaDiv) {
            btnNovaDiv.style.display = this._isMestre() ? '' : 'none';
        }
        const tabCampanhas = document.querySelector('.nav-tab[data-tab="campanhas"]');
        if (tabCampanhas) {
            tabCampanhas.style.display = this._isMestre() ? '' : 'none';
        }
    }

    _aplicarRestricoesPerfil() {
        if (this._isMestre()) return;

        // Jogador vê o botão '+ Novo Combatente' (abre direto o modal de jogador)
        const elementos = [
            { query: '.nav-tab[data-tab="arena"]', id: null },
            { query: '.filter-btn[data-tipo="monstro"]', id: null },
            { query: '.filter-btn[data-tipo="npc"]', id: null },
            { id: 'totalMonstros', closest: '.resumo-card', query: null },
            { id: 'totalNPCs', closest: '.resumo-card', query: null }
        ];

        elementos.forEach(el => {
            const elem = el.id ? document.getElementById(el.id) : document.querySelector(el.query);
            if (elem) {
                const target = el.closest ? elem.closest(el.closest) : elem;
                if (target) target.style.display = 'none';
            }
        });
    }

    _configurarAbas() {
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
            });
        });
    }

    _configurarFiltros() {
        const self = this;
        document.querySelectorAll('.filter-btn[data-tipo]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!self._isMestre() && self.rules.isTipoRestritoParaMestre(btn.dataset.tipo)) return;
                document.querySelectorAll('.filter-btn[data-tipo]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                self.filtroAtual = btn.dataset.tipo;
                self.carregarCombatentes();
            });
        });
    }

    _configurarFiltroEscopo() {
        const container = document.getElementById('filtroEscopoMestre');
        if (!container) return;
        if (!this._isMestre()) {
            container.style.display = 'none';
            return;
        }
        container.style.display = '';
        this._atualizarEstadoBotoesEscopo();

        container.querySelectorAll('[data-escopo]').forEach((btn) => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('[data-escopo]').forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
                this.escopoMestre = btn.getAttribute('data-escopo') || 'todos';
                this._persistirEscopoMestre(this.escopoMestre);
                this.carregarCombatentes();
            });
        });
    }

    _atualizarEstadoBotoesEscopo() {
        const container = document.getElementById('filtroEscopoMestre');
        if (!container) return;
        const alvo = this.escopoMestre === 'meus' ? 'meus' : 'todos';
        container.querySelectorAll('[data-escopo]').forEach((b) => b.classList.remove('active'));
        const btnInicial = container.querySelector(`[data-escopo="${alvo}"]`);
        if (btnInicial) btnInicial.classList.add('active');
    }

    _atualizarIndicadorEscopoVazio(combatentes) {
        const indicador = document.getElementById('indicadorEscopoMestreVazio');
        if (!indicador || !this._isMestre()) return;
        const semResultados = this.escopoMestre === 'meus' && Array.isArray(combatentes) && combatentes.length === 0;
        if (!semResultados) {
            indicador.style.display = 'none';
            indicador.textContent = '';
            return;
        }
        indicador.textContent = 'Escopo "Meus": 0 combatentes.';
        indicador.style.display = '';
    }

    _lerEscopoMestrePersistido() {
        try {
            const valor = localStorage.getItem('dashboard:escopo-mestre');
            return valor === 'meus' ? 'meus' : 'todos';
        } catch (_err) {
            return 'todos';
        }
    }

    _persistirEscopoMestre(valor) {
        try {
            localStorage.setItem('dashboard:escopo-mestre', valor === 'meus' ? 'meus' : 'todos');
        } catch (_err) {
            // sem falha para modo privado/storage indisponível
        }
    }

    _configurarBotaoNovo() {
        const btn = document.getElementById('btnNovoCombatente');
        if (!btn) return;
        if (this._isMestre()) {
            btn.addEventListener('click', () => this._abrirModal('seletorTipo'));
        } else {
            // Jogador cria apenas personagem do tipo jogador — sem seletor de tipo
            btn.addEventListener('click', () => this._abrirModal('modalCadastroJogador'));
        }
    }

    _configurarFormCadastro(formId, tipo, modalId) {
        const self = this;
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            self._sincronizarCamposRaca(form);
            const btn = form.querySelector('[type="submit"]');
            const loadingOptions = {
                loadingText: 'Salvando...',
                idleText: `✅ Cadastrar ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`,
            };
            
            try {
                if (window.AsyncButtonState?.run) {
                    await window.AsyncButtonState.run(btn, loadingOptions, async () => {
                        const c = await self.service.criar(new FormData(form));
                        Toast.success(`${c.nome} cadastrado com sucesso!`);
                        self._fecharModal(modalId);
                        self._limparForm(form, tipo);
                        self.carregarCombatentes();
                    });
                } else {
                    btn.disabled = true;
                    btn.textContent = loadingOptions.loadingText;
                    const c = await self.service.criar(new FormData(form));
                    Toast.success(`${c.nome} cadastrado com sucesso!`);
                    self._fecharModal(modalId);
                    self._limparForm(form, tipo);
                    self.carregarCombatentes();
                    btn.disabled = false;
                    btn.textContent = loadingOptions.idleText;
                }
            } catch (err) {
                Toast.error(err.message || 'Erro ao cadastrar');
                console.error(err);
                if (!window.AsyncButtonState?.run && btn) {
                    btn.disabled = false;
                    btn.textContent = loadingOptions.idleText;
                }
            }
        });
    }

    _configurarCombosRaca() {
        const combos = [
            { selectId: 'cadastroJogadorRacaSelect', finalId: 'cadastroJogadorRacaFinal', customId: 'cadastroJogadorRacaCustom', previewId: 'cadastroJogadorRacaPreview' },
            { selectId: 'cadastroNpcRacaSelect', finalId: 'cadastroNpcRacaFinal', customId: 'cadastroNpcRacaCustom', previewId: 'cadastroNpcRacaPreview' },
            { selectId: 'dashEditRacaSelect', finalId: 'dashEditRaca', customId: 'dashEditRacaCustom', previewId: 'dashEditRacaPreview' },
        ];

        combos.forEach((cfg) => {
            const selectEl = document.getElementById(cfg.selectId);
            const finalEl = document.getElementById(cfg.finalId);
            const customEl = document.getElementById(cfg.customId);
            const previewEl = document.getElementById(cfg.previewId);

            if (!selectEl || !finalEl || !customEl) return;

            const slugEl = document.getElementById(cfg.selectId.replace('Select', 'Slug'));
            this._preencherSelectRaca(selectEl);
            selectEl.addEventListener('change', () => this._atualizarCampoRaca(selectEl, finalEl, customEl, slugEl, previewEl));
            customEl.addEventListener('input', () => this._atualizarCampoRaca(selectEl, finalEl, customEl, slugEl, previewEl));

            this._atualizarCampoRaca(selectEl, finalEl, customEl, slugEl, previewEl, true);
        });
    }

    _preencherSelectRaca(selectEl) {
        if (!selectEl) return;
        const valorAtual = String(selectEl.value || '');
        const valorOutro = '__OUTRO__';
        const racas = this._listarRacasParaSelect();
        selectEl.innerHTML = '';
        const opVazio = document.createElement('option');
        opVazio.value = '';
        opVazio.textContent = '-- Selecione uma raça --';
        selectEl.appendChild(opVazio);
        racas.forEach((raca) => {
            const op = document.createElement('option');
            op.value = raca.nome;
            op.textContent = this._normalizarNomeRacaParaExibicao(raca.nome);
            selectEl.appendChild(op);
        });
        const opOutro = document.createElement('option');
        opOutro.value = valorOutro;
        opOutro.textContent = 'Outro';
        selectEl.appendChild(opOutro);
        if ([...selectEl.options].some((opt) => opt.value === valorAtual)) {
            selectEl.value = valorAtual;
        }
    }

    _listarRacasParaSelect() {
        if (Array.isArray(this.racasDisponiveis) && this.racasDisponiveis.length) {
            return this.racasDisponiveis;
        }
        const fallback = window.RacasPHB?.listar?.() || [];
        return fallback.map((nome) => ({
            nome: String(nome || '').trim(),
            slug: String(nome || '').trim(),
        })).filter((item) => item.nome);
    }

    _normalizarNomeRacaParaExibicao(nomeRaca) {
        const nome = String(nomeRaca || '').trim();
        if (!nome) return '';
        const mapaSingular = {
            humanos: 'Humano',
            elfos: 'Elfo',
            anoes: 'Anão',
            'anões': 'Anão',
            halflings: 'Halfling',
            gnomos: 'Gnomo',
            meioelfos: 'Meio-elfo',
            'meio-elfos': 'Meio-elfo',
            meioorcs: 'Meio-orc',
            'meio-orcs': 'Meio-orc',
        };
        const chave = nome.toLowerCase();
        return mapaSingular[chave] || nome;
    }

    async _carregarRacasCatalogo() {
        try {
            const response = await fetch(window.getApiUrl('/racas'), {
                headers: this._getAuthHeader(),
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            const racas = Array.isArray(data) ? data : [];
            this.racasDisponiveis = racas
                .map((item) => ({
                    nome: String(item?.nome || '').trim(),
                    slug: String(item?.slug || '').trim(),
                }))
                .filter((item) => item.nome && item.slug);
            this.racaSlugPorNome = new Map(this.racasDisponiveis.map((item) => [item.nome, item.slug]));
            this._configurarCombosRaca();
        } catch (error) {
            console.warn('⚠️ Não foi possível carregar catálogo de raças pela API:', error);
        }
    }

    _atualizarCampoRaca(selectEl, finalEl, customEl, slugEl = null, previewEl = null, limparCustom = false) {
        if (!selectEl || !finalEl || !customEl) return;

        const valorOutro = '__OUTRO__';
        const selecionouOutro = selectEl.value === valorOutro;

        if (selecionouOutro) {
            customEl.style.display = 'block';
            if (limparCustom) customEl.value = '';
            finalEl.value = String(customEl.value || '').trim();
            if (slugEl) slugEl.value = '';
            this._renderizarPreviewRaca(previewEl, null);
            return;
        }

        if (limparCustom) customEl.value = '';
        customEl.style.display = 'none';
        const nomeRaca = String(selectEl.value || '').trim();
        finalEl.value = nomeRaca;
        const slug = this.racaSlugPorNome.get(nomeRaca) || '';
        if (slugEl) {
            slugEl.value = slug;
        }
        this._renderizarPreviewRaca(previewEl, slug || null);
    }

    _sincronizarCamposRaca(form, limparCustom = false) {
        if (!form) return;

        const selects = form.querySelectorAll('[data-raca-select]');
        selects.forEach((selectEl) => {
            const key = selectEl.getAttribute('data-raca-key');
            if (!key) return;

            const finalEl = form.querySelector(`[data-raca-final][data-raca-key="${key}"]`);
            const customEl = form.querySelector(`[data-raca-custom][data-raca-key="${key}"]`);
            const slugEl = form.querySelector(`[data-raca-slug][data-raca-key="${key}"]`);
            const previewEl = form.querySelector(`#${key === 'jogador' ? 'cadastroJogadorRacaPreview' : key === 'npc' ? 'cadastroNpcRacaPreview' : 'dashEditRacaPreview'}`);
            this._atualizarCampoRaca(selectEl, finalEl, customEl, slugEl, previewEl, limparCustom);
        });
    }

    async _obterDetalheRacaPorSlug(slug) {
        const key = String(slug || '').trim();
        if (!key) return null;
        if (this.racaDetalheCache.has(key)) return this.racaDetalheCache.get(key);
        try {
            const response = await fetch(window.getApiUrl(`/racas/${encodeURIComponent(key)}`), {
                headers: this._getAuthHeader(),
            });
            if (!response.ok) return null;
            const detail = await response.json();
            this.racaDetalheCache.set(key, detail);
            return detail;
        } catch (_err) {
            return null;
        }
    }

    async _renderizarPreviewRaca(previewEl, slug) {
        if (!previewEl) return;

        const setEmpty = (msg, isFallback = false) => {
            previewEl.classList.toggle('is-fallback', Boolean(isFallback));
            previewEl.replaceChildren();
            const p = document.createElement('p');
            p.className = 'dash-raca-preview-empty';
            p.textContent = msg;
            previewEl.appendChild(p);
        };

        if (!slug) {
            setEmpty('Selecione uma raça para ver pré-definições.');
            return;
        }

        const detail = await this._obterDetalheRacaPorSlug(slug);
        if (!detail) {
            setEmpty('Pré-definições indisponíveis para esta raça.', true);
            return;
        }

        previewEl.classList.remove('is-fallback');
        previewEl.replaceChildren();

        const inner = document.createElement('div');
        inner.className = 'dash-raca-preview-inner';

        const modsRow = document.createElement('div');
        modsRow.className = 'dash-raca-preview-line dash-raca-preview-line--mods';
        const modsLabel = document.createElement('span');
        modsLabel.className = 'dash-raca-preview-k';
        modsLabel.textContent = 'Atributos';
        modsRow.appendChild(modsLabel);

        const modsWrap = document.createElement('div');
        modsWrap.className = 'dash-raca-preview-badges';
        const mods = Array.isArray(detail.modificadores_habilidade) ? detail.modificadores_habilidade : [];
        if (!mods.length) {
            const muted = document.createElement('span');
            muted.className = 'dash-raca-preview-muted';
            muted.textContent = '—';
            modsWrap.appendChild(muted);
        } else {
            mods.forEach((m) => {
                const v = Number(m?.valor);
                const attr = String(m?.atributo || '').toUpperCase();
                const b = document.createElement('span');
                b.className = 'dash-raca-badge';
                if (v > 0) b.classList.add('dash-raca-badge--pos');
                else if (v < 0) b.classList.add('dash-raca-badge--neg');
                else b.classList.add('dash-raca-badge--zero');
                b.textContent = `${v >= 0 ? '+' : ''}${v} ${attr}`;
                modsWrap.appendChild(b);
            });
        }
        modsRow.appendChild(modsWrap);
        inner.appendChild(modsRow);

        const addLinha = (rotulo, texto) => {
            const line = document.createElement('div');
            line.className = 'dash-raca-preview-line';
            const k = document.createElement('span');
            k.className = 'dash-raca-preview-k';
            k.textContent = rotulo;
            const v = document.createElement('span');
            v.className = 'dash-raca-preview-v';
            v.textContent = texto;
            line.appendChild(k);
            line.appendChild(v);
            inner.appendChild(line);
        };

        addLinha('Tamanho', detail.tamanho ? String(detail.tamanho) : '—');
        const deslocamento = Number.isFinite(Number(detail.deslocamento_metros))
            ? `${detail.deslocamento_metros} m`
            : '—';
        addLinha('Deslocamento', deslocamento);
        const idiomas = Array.isArray(detail.idiomas_iniciais) && detail.idiomas_iniciais.length
            ? detail.idiomas_iniciais.join(', ')
            : '—';
        addLinha('Idiomas', idiomas);

        previewEl.appendChild(inner);
    }

    _configurarAcoesModaisSemInline() {
        const bindClick = (id, handler) => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('click', handler);
        };

        bindClick('btnFecharSeletorTipo', () => this._fecharModal('seletorTipo'));
        bindClick('btnTipoJogador', () => this.actions.abrirModalCadastro('jogador'));
        bindClick('btnTipoMonstro', () => this.actions.abrirModalCadastro('monstro'));
        bindClick('btnTipoNPC', () => this.actions.abrirModalCadastro('npc'));

        bindClick('btnFecharCadastroJogador', () => this._fecharModal('modalCadastroJogador'));
        bindClick('btnCancelarCadastroJogador', () => this._fecharModal('modalCadastroJogador'));
        bindClick('btnRemoverImagemJogador', () => this._removerImagem('', false));

        bindClick('btnFecharCadastroMonstro', () => this._fecharModal('modalCadastroMonstro'));
        bindClick('btnCancelarCadastroMonstro', () => this._fecharModal('modalCadastroMonstro'));
        bindClick('btnRemoverImagemMonstro', () => this._removerImagem('Monstro', false));

        bindClick('btnFecharCadastroNPC', () => this._fecharModal('modalCadastroNPC'));
        bindClick('btnCancelarCadastroNPC', () => this._fecharModal('modalCadastroNPC'));
        bindClick('btnRemoverImagemNPC', () => this._removerImagem('NPC', false));

        bindClick('btnFecharModalEdicao', () => this._fecharModal('modalEdicaoDashboard'));
        bindClick('btnCancelarEdicao', () => this._fecharModal('modalEdicaoDashboard'));
        bindClick('btnDeletarCombatenteEdicao', () => this._deletarCombatente());
        bindClick('btnAdicionarAtaqueEdicao', () => this._adicionarLinhaAtaque());
        bindClick('btnRemoverImagemEdicao', () => this._removerImagem('', true));

        document.querySelectorAll('.dash-atributo-input').forEach((input) => {
            input.addEventListener('input', () => {
                this._calcularModificador(input);
                if (input.id === 'dashEditDES') {
                    this._preencherIniciativaSugeridaPorDestrezaEdicao();
                }
            });
        });
    }

    _configurarFormEdicao() {
        const self = this;
        const form = document.getElementById('formEdicaoDashboard');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            self._sincronizarCamposRaca(form);
            const btn = form.querySelector('[type="submit"]');
            const loadingOptions = {
                loadingText: 'Salvando...',
                idleText: 'Salvar Alterações',
            };
            
            try {
                if (window.AsyncButtonState?.run) {
                    await window.AsyncButtonState.run(btn, loadingOptions, async () => {
                        const id = parseInt(document.getElementById('dashEditId').value);
                        await self.service.atualizar(id, new FormData(form));
                        await self._salvarAtaquesEdicao(id);
                        await self._salvarPericiasEdicao(id);

                        self._fecharModal('modalEdicaoDashboard');
                        self.combatenteEmEdicao = null;
                        self.carregarCombatentes();
                        Toast.success('Alterações salvas com sucesso!');
                    });
                } else {
                    btn.disabled = true;
                    btn.textContent = loadingOptions.loadingText;
                    const id = parseInt(document.getElementById('dashEditId').value);
                    await self.service.atualizar(id, new FormData(form));
                    await self._salvarAtaquesEdicao(id);
                    await self._salvarPericiasEdicao(id);

                    self._fecharModal('modalEdicaoDashboard');
                    self.combatenteEmEdicao = null;
                    self.carregarCombatentes();
                    Toast.success('Alterações salvas com sucesso!');
                    btn.disabled = false;
                    btn.textContent = loadingOptions.idleText;
                }
            } catch (err) {
                Toast.error(err.message || 'Erro ao salvar alterações');
                console.error(err);
                if (!window.AsyncButtonState?.run && btn) {
                    btn.disabled = false;
                    btn.textContent = loadingOptions.idleText;
                }
            }
        });
    }

    _configurarUpload(sufixo) {
        const self = this;
        const area = document.getElementById('uploadPlaceholder' + sufixo);
        const input = document.getElementById('inputFoto' + sufixo);
        if (!input) return;

        if (area) {
            area.addEventListener('click', () => input.click());
        }
        
        input.addEventListener('change', () => {
            self._previewImagem(input, 'uploadPreview' + sufixo, 'previewImage' + sufixo, 'uploadPlaceholder' + sufixo);
        });
    }

    _configurarUploadEdicao() {
        const self = this;
        const area = document.getElementById('dashEditUploadArea');
        const input = document.getElementById('dashEditFoto');
        if (!area || !input) return;
        
        area.addEventListener('click', () => input.click());
        input.addEventListener('change', () => {
            self._previewImagem(input, 'dashEditUploadPreview', 'dashEditPreviewImage', 'dashEditUploadPlaceholder');
        });
    }

    async carregarCombatentes() {
        try {
            let tipo = this.filtroAtual === 'todos' ? null : this.filtroAtual;
            tipo = this.rules.tipoPermitidoParaPerfil(tipo, this._isMestre());
            const somenteMeus = this._isMestre() && this.escopoMestre === 'meus';
            const combatentes = await this.service.listar(tipo, somenteMeus);
            this._renderizarTabela(combatentes);
            this._atualizarResumo(combatentes);
            this._atualizarIndicadorEscopoVazio(combatentes);
            await this._atualizarSelectPersonagensCampanha(combatentes);
        } catch (err) {
            Toast.error('Erro ao carregar combatentes');
            console.error(err);
        }
    }

    _configurarCampanhas() {
        if (!this._isMestre() || !this.campanhaService) return;
        const form = document.getElementById('formCampanha');
        const lista = document.getElementById('listaCampanhas');
        const formSessao = document.getElementById('formSessaoCampanha');
        if (!form || !lista) return;
        const inputBuscaPersonagem = document.getElementById('campanhaPersonagensBusca');
        const filtrosTipo = document.getElementById('campanhaPersonagensTipoFiltros');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const nome = (document.getElementById('campanhaNome')?.value || '').trim();
            const descricao = (document.getElementById('campanhaDescricao')?.value || '').trim();
            const personagemIds = this._coletarPersonagensCampanhaSelecionados();
            if (!nome) {
                Toast.error('Informe o nome da campanha.');
                return;
            }
            try {
                const emEdicao = Boolean(this.campanhaEmEdicaoId);
                const payload = {
                    nome,
                    descricao,
                    personagem_ids: personagemIds,
                };
                if (this.campanhaEmEdicaoId) {
                    await this.campanhaService.atualizar(this.campanhaEmEdicaoId, payload);
                } else {
                    await this.campanhaService.criar(payload);
                }
                this._resetFormCampanha();
                await this._carregarCampanhas();
                await this.carregarCombatentes();
                Toast.success(emEdicao ? 'Campanha atualizada com sucesso!' : 'Campanha criada com sucesso!');
            } catch (error) {
                Toast.error(error.message || 'Erro ao salvar campanha');
            }
        });

        const btnCancelarEdicao = document.getElementById('btnCancelarEdicaoCampanha');
        if (btnCancelarEdicao) {
            btnCancelarEdicao.addEventListener('click', () => this._resetFormCampanha());
        }
        if (inputBuscaPersonagem) {
            inputBuscaPersonagem.addEventListener('input', () => this._renderizarChecklistPersonagensCampanha());
        }
        if (filtrosTipo) {
            filtrosTipo.querySelectorAll('[data-campanha-tipo]').forEach((btn) => {
                btn.addEventListener('click', () => {
                    filtrosTipo.querySelectorAll('[data-campanha-tipo]').forEach((b) => b.classList.remove('active'));
                    btn.classList.add('active');
                    this.filtroTipoParticipanteCampanha = btn.getAttribute('data-campanha-tipo') || 'todos';
                    this._renderizarChecklistPersonagensCampanha();
                });
            });
        }
        form.addEventListener('input', () => this._atualizarEstadoEdicaoCampanha());
        form.addEventListener('change', () => this._atualizarEstadoEdicaoCampanha());
        if (formSessao) {
            const btnCancelarSessao = document.getElementById('btnCancelarEdicaoSessao');
            if (btnCancelarSessao) {
                btnCancelarSessao.addEventListener('click', () => this._resetFormSessaoCampanha());
            }
            formSessao.addEventListener('submit', async (event) => {
                event.preventDefault();
                const campanhaId = Number(document.getElementById('sessaoCampanhaId')?.value || 0);
                const resumo = String(document.getElementById('sessaoResumo')?.value || '').trim();
                const visivel = Boolean(document.getElementById('sessaoVisivelJogadores')?.checked);
                if (!Number.isFinite(campanhaId) || campanhaId <= 0) {
                    Toast.error('Selecione uma campanha para a sessão.');
                    return;
                }
                if (!resumo) {
                    Toast.error('Informe o resumo da sessão.');
                    return;
                }
                try {
                    const emEdicao = Boolean(this.sessaoEmEdicaoId);
                    if (emEdicao) {
                        await this.campanhaService.atualizarSessao(this.sessaoEmEdicaoId, {
                            resumo,
                            visivel_jogadores: visivel,
                        });
                    } else {
                        await this.campanhaService.criarSessao({
                            campanha_id: campanhaId,
                            resumo,
                            visivel_jogadores: visivel,
                        });
                    }
                    this._resetFormSessaoCampanha();
                    await this._carregarSessoesCampanha();
                    Toast.success(emEdicao ? 'Sessão atualizada com sucesso!' : 'Sessão registrada com sucesso!');
                } catch (error) {
                    Toast.error(error.message || 'Erro ao registrar sessão');
                }
            });
        }

        this._carregarCampanhas();
        this._carregarSessoesCampanha();
    }

    _configurarSubAbasCampanhas() {
        if (!this._isMestre()) return;
        const container = document.getElementById('campanhasSubAbas');
        if (!container) return;
        const ativar = (alvo) => {
            const subaba = alvo === 'sessoes' ? 'sessoes' : 'cadastro';
            container.querySelectorAll('[data-campanhas-subaba]').forEach((btn) => {
                btn.classList.toggle('active', btn.getAttribute('data-campanhas-subaba') === subaba);
            });
            const paneCadastro = document.getElementById('campanhasSubabaCadastro');
            const paneSessoes = document.getElementById('campanhasSubabaSessoes');
            if (paneCadastro) paneCadastro.classList.toggle('active', subaba === 'cadastro');
            if (paneSessoes) paneSessoes.classList.toggle('active', subaba === 'sessoes');
            this._persistirSubAbaCampanhas(subaba);
        };
        ativar(this._lerSubAbaCampanhasPersistida());
        container.querySelectorAll('[data-campanhas-subaba]').forEach((btn) => {
            btn.addEventListener('click', () => {
                ativar(btn.getAttribute('data-campanhas-subaba'));
            });
        });
    }

    _lerSubAbaCampanhasPersistida() {
        try {
            const valor = localStorage.getItem('dashboard:campanhas-subaba');
            return valor === 'sessoes' ? 'sessoes' : 'cadastro';
        } catch (_err) {
            return 'cadastro';
        }
    }

    _persistirSubAbaCampanhas(valor) {
        try {
            localStorage.setItem('dashboard:campanhas-subaba', valor === 'sessoes' ? 'sessoes' : 'cadastro');
        } catch (_err) {
            // ignore storage errors
        }
    }

    async _carregarCampanhas() {
        if (!this.campanhaService || !this._isMestre()) return;
        const lista = document.getElementById('listaCampanhas');
        if (!lista) return;
        lista.innerHTML = '<p class="dash-divcustom-vazio">Carregando campanhas...</p>';
        try {
            const campanhas = await this.campanhaService.listar();
            this.campanhas = Array.isArray(campanhas) ? campanhas : [];
            this._renderizarCampanhas();
            this._atualizarSelectCampanhasSessao();
        } catch (error) {
            lista.innerHTML = `<p class="dash-divcustom-vazio">${escapeHtml(error.message || 'Erro ao carregar campanhas')}</p>`;
        }
    }

    async _carregarSessoesCampanha() {
        if (!this.campanhaService || !this._isMestre()) return;
        const lista = document.getElementById('listaSessoesCampanha');
        if (!lista) return;
        lista.innerHTML = '<p class="dash-divcustom-vazio">Carregando sessões...</p>';
        try {
            const sessoes = await this.campanhaService.listarSessoes();
            this.sessoesCampanha = Array.isArray(sessoes) ? sessoes : [];
            this._renderizarSessoesCampanha();
        } catch (error) {
            lista.innerHTML = `<p class="dash-divcustom-vazio">${escapeHtml(error.message || 'Erro ao carregar sessões')}</p>`;
        }
    }

    _atualizarSelectCampanhasSessao() {
        const select = document.getElementById('sessaoCampanhaId');
        if (!select) return;
        const valorAtual = String(select.value || '');
        select.innerHTML = '<option value="">Selecione a campanha</option>';
        (this.campanhas || []).forEach((campanha) => {
            const opt = document.createElement('option');
            opt.value = String(campanha.id);
            opt.textContent = campanha.nome || `Campanha #${campanha.id}`;
            select.appendChild(opt);
        });
        if ([...select.options].some((opt) => opt.value === valorAtual)) {
            select.value = valorAtual;
        }
    }

    _renderizarSessoesCampanha() {
        const lista = document.getElementById('listaSessoesCampanha');
        if (!lista) return;
        if (!this.sessoesCampanha.length) {
            lista.innerHTML = '<p class="dash-divcustom-vazio">Nenhuma sessão registrada.</p>';
            return;
        }
        lista.innerHTML = this.sessoesCampanha.map((sessao) => `
            <div class="dash-divcustom-card">
                <div class="dash-divcustom-card-head">
                    <strong>${escapeHtml(sessao.campanha_nome || 'Campanha')}</strong>
                    <div style="display:flex; gap:.35rem;">
                        <span class="badge ${sessao.visivel_jogadores ? 'badge-jogador' : 'badge-npc'}">${sessao.visivel_jogadores ? 'Visível aos jogadores' : 'Privada do mestre'}</span>
                        <button type="button" class="btn-dash-cancel" data-sessao-edit="${sessao.id}" title="Editar sessão">Editar</button>
                        <button type="button" class="btn-dash-delete-div" data-sessao-delete="${sessao.id}" title="Excluir sessão">✕</button>
                    </div>
                </div>
                <div class="dash-divcustom-card-meta">
                    <span><b>Registrada em:</b> ${this._formatarDataSessao(sessao.created_at)}</span>
                </div>
                <p class="dash-divcustom-card-desc">${escapeHtml(sessao.resumo || '')}</p>
            </div>
        `).join('');
        lista.querySelectorAll('[data-sessao-edit]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const sessaoId = Number(btn.getAttribute('data-sessao-edit'));
                if (!Number.isFinite(sessaoId)) return;
                const sessao = this.sessoesCampanha.find((item) => item.id === sessaoId);
                if (!sessao) return;
                this._preencherFormSessaoParaEdicao(sessao);
            });
        });
        lista.querySelectorAll('[data-sessao-delete]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const sessaoId = Number(btn.getAttribute('data-sessao-delete'));
                if (!Number.isFinite(sessaoId)) return;
                try {
                    await this.campanhaService.deletarSessao(sessaoId);
                    await this._carregarSessoesCampanha();
                    Toast.success('Sessão removida.');
                } catch (error) {
                    Toast.error(error.message || 'Erro ao remover sessão');
                }
            });
        });
    }

    _preencherFormSessaoParaEdicao(sessao) {
        this.sessaoEmEdicaoId = sessao.id;
        const inputId = document.getElementById('sessaoIdEdicao');
        const selectCampanha = document.getElementById('sessaoCampanhaId');
        const inputResumo = document.getElementById('sessaoResumo');
        const inputVisivel = document.getElementById('sessaoVisivelJogadores');
        const btnSalvar = document.getElementById('btnSalvarSessaoCampanha');
        const btnCancelar = document.getElementById('btnCancelarEdicaoSessao');
        const badge = document.getElementById('sessaoEdicaoBadge');
        if (inputId) inputId.value = String(sessao.id);
        if (selectCampanha) selectCampanha.value = String(sessao.campanha_id || '');
        if (inputResumo) inputResumo.value = sessao.resumo || '';
        if (inputVisivel) inputVisivel.checked = Boolean(sessao.visivel_jogadores);
        if (btnSalvar) btnSalvar.textContent = '💾 Salvar Sessão';
        if (btnCancelar) btnCancelar.style.display = '';
        if (badge) {
            badge.textContent = `✏️ Editando sessão: ${sessao.campanha_nome || 'Campanha'}`;
            badge.style.display = '';
        }
        selectCampanha?.focus();
    }

    _resetFormSessaoCampanha() {
        this.sessaoEmEdicaoId = null;
        const form = document.getElementById('formSessaoCampanha');
        const inputId = document.getElementById('sessaoIdEdicao');
        const btnSalvar = document.getElementById('btnSalvarSessaoCampanha');
        const btnCancelar = document.getElementById('btnCancelarEdicaoSessao');
        const badge = document.getElementById('sessaoEdicaoBadge');
        if (form) form.reset();
        if (inputId) inputId.value = '';
        if (btnSalvar) btnSalvar.textContent = '📝 Registrar Sessão';
        if (btnCancelar) btnCancelar.style.display = 'none';
        if (badge) {
            badge.style.display = 'none';
            badge.textContent = '';
        }
    }

    _formatarDataSessao(valor) {
        if (!valor) return '—';
        const data = new Date(valor);
        if (Number.isNaN(data.getTime())) return '—';
        try {
            return new Intl.DateTimeFormat('pt-BR', {
                dateStyle: 'short',
                timeStyle: 'short',
            }).format(data);
        } catch (_err) {
            return data.toLocaleString('pt-BR');
        }
    }

    _renderizarCampanhas() {
        const lista = document.getElementById('listaCampanhas');
        if (!lista) return;
        if (!this.campanhas.length) {
            lista.innerHTML = '<p class="dash-divcustom-vazio">Nenhuma campanha cadastrada.</p>';
            return;
        }

        lista.innerHTML = this.campanhas.map((campanha) => `
            <div class="dash-divcustom-card">
                <div class="dash-divcustom-card-head">
                    <strong>${escapeHtml(campanha.nome || '')}</strong>
                    <div style="display:flex; gap:.35rem;">
                        <button
                            type="button"
                            class="btn-dash-cancel"
                            data-campanha-edit="${campanha.id}"
                            title="Editar campanha"
                        >Editar</button>
                        <button
                            type="button"
                            class="btn-dash-delete-div"
                            data-campanha-delete="${campanha.id}"
                            title="Excluir campanha"
                        >✕</button>
                    </div>
                </div>
                <div class="dash-divcustom-card-meta">
                    <span><b>Personagens:</b> ${Number(campanha.total_personagens || 0)}</span>
                </div>
                ${campanha.descricao ? `<p class="dash-divcustom-card-desc">${escapeHtml(campanha.descricao)}</p>` : ''}
            </div>
        `).join('');

        lista.querySelectorAll('[data-campanha-delete]').forEach((btn) => {
            btn.addEventListener('click', async () => {
                const campanhaId = Number(btn.getAttribute('data-campanha-delete'));
                if (!Number.isFinite(campanhaId)) return;
                try {
                    await this.campanhaService.deletar(campanhaId);
                    await this._carregarCampanhas();
                    await this.carregarCombatentes();
                    Toast.success('Campanha removida.');
                } catch (error) {
                    Toast.error(error.message || 'Erro ao remover campanha');
                }
            });
        });

        lista.querySelectorAll('[data-campanha-edit]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const campanhaId = Number(btn.getAttribute('data-campanha-edit'));
                if (!Number.isFinite(campanhaId)) return;
                const campanha = this.campanhas.find((item) => item.id === campanhaId);
                if (!campanha) return;
                this._preencherFormCampanhaParaEdicao(campanha);
            });
        });
    }

    _coletarPersonagensCampanhaSelecionados() {
        const container = document.getElementById('campanhaPersonagens');
        if (!container) return [];
        return Array.from(container.querySelectorAll('input[type="checkbox"][data-personagem-id]:checked'))
            .map((el) => Number(el.getAttribute('data-personagem-id')))
            .filter((id) => Number.isFinite(id) && id > 0);
    }

    async _atualizarSelectPersonagensCampanha(combatentes) {
        if (!this._isMestre()) return;
        const container = document.getElementById('campanhaPersonagens');
        if (!container) return;
        let personagensFonte = Array.isArray(combatentes) ? combatentes : [];
        if (this.escopoMestre === 'meus') {
            try {
                personagensFonte = await this.service.listar('jogador', false);
            } catch (_err) {
                // Em caso de falha, mantém a lista já carregada na tela.
            }
        }
        const tiposPermitidosCampanha = new Set(['jogador', 'monstro', 'npc']);
        this.personagensDisponiveisCampanha = (personagensFonte || []).filter((item) =>
            tiposPermitidosCampanha.has(String(item.tipo || '').toLowerCase())
        );
        this._renderizarChecklistPersonagensCampanha();
    }

    _renderizarChecklistPersonagensCampanha() {
        const container = document.getElementById('campanhaPersonagens');
        if (!container) return;
        const idsSelecionados = new Set(this._coletarPersonagensCampanhaSelecionados());
        const filtro = String(document.getElementById('campanhaPersonagensBusca')?.value || '').trim().toLowerCase();
        const filtroTipo = this.filtroTipoParticipanteCampanha || 'todos';
        const personagens = (this.personagensDisponiveisCampanha || []).filter((item) => {
            const tipo = String(item.tipo || '').toLowerCase();
            if (filtroTipo !== 'todos' && tipo !== filtroTipo) return false;
            if (!filtro) return true;
            const nome = String(item.nome || '').toLowerCase();
            return nome.includes(filtro);
        });
        if (!personagens.length) {
            const vazio = filtro
                ? 'Nenhum personagem encontrado para este filtro.'
                : 'Nenhum personagem disponível.';
            container.innerHTML = `<div class="campanha-personagens-vazio">${vazio}</div>`;
            return;
        }
        container.innerHTML = personagens.map((personagem) => {
            const checked = idsSelecionados.has(personagem.id) ? 'checked' : '';
            const tipoLabel = String(personagem.tipo || '').toLowerCase();
            const tipoExibicao = tipoLabel
                ? tipoLabel.charAt(0).toUpperCase() + tipoLabel.slice(1)
                : 'Personagem';
            return `
                <label class="campanha-personagem-item">
                    <input type="checkbox" data-personagem-id="${personagem.id}" ${checked} />
                    <span class="campanha-personagem-nome">${escapeHtml(personagem.nome)} (${tipoExibicao} • Nv ${personagem.nivel || 1})</span>
                </label>
            `;
        }).join('');
    }

    _limparSelectPersonagensCampanha() {
        const container = document.getElementById('campanhaPersonagens');
        if (container) {
            container.querySelectorAll('input[type="checkbox"][data-personagem-id]').forEach((el) => {
                el.checked = false;
            });
        }
    }

    _preencherFormCampanhaParaEdicao(campanha) {
        this.campanhaEmEdicaoId = campanha.id;
        const inputId = document.getElementById('campanhaIdEdicao');
        const inputNome = document.getElementById('campanhaNome');
        const inputDescricao = document.getElementById('campanhaDescricao');
        const btnSalvar = document.getElementById('btnSalvarCampanha');
        const btnCancelar = document.getElementById('btnCancelarEdicaoCampanha');
        const badgeEdicao = document.getElementById('campanhaEdicaoBadge');
        const container = document.getElementById('campanhaPersonagens');

        if (inputId) inputId.value = String(campanha.id);
        if (inputNome) inputNome.value = campanha.nome || '';
        if (inputDescricao) inputDescricao.value = campanha.descricao || '';
        if (btnSalvar) btnSalvar.textContent = '💾 Salvar Campanha';
        if (btnCancelar) btnCancelar.style.display = '';
        if (badgeEdicao) {
            badgeEdicao.textContent = `✏️ Editando campanha: ${campanha.nome || ''}`;
            badgeEdicao.style.display = '';
            badgeEdicao.classList.remove('is-dirty');
        }

        const idsSelecionados = new Set((campanha.personagem_ids || []).map((id) => Number(id)));
        if (container) {
            container.querySelectorAll('input[type="checkbox"][data-personagem-id]').forEach((el) => {
                const id = Number(el.getAttribute('data-personagem-id'));
                el.checked = idsSelecionados.has(id);
            });
        }
        this.snapshotCampanhaEmEdicao = this._capturarEstadoFormCampanha();
        this._atualizarEstadoEdicaoCampanha();
        inputNome?.focus();
    }

    _resetFormCampanha() {
        this.campanhaEmEdicaoId = null;
        this.snapshotCampanhaEmEdicao = null;
        const form = document.getElementById('formCampanha');
        const inputId = document.getElementById('campanhaIdEdicao');
        const btnSalvar = document.getElementById('btnSalvarCampanha');
        const btnCancelar = document.getElementById('btnCancelarEdicaoCampanha');
        const badgeEdicao = document.getElementById('campanhaEdicaoBadge');
        if (form) form.reset();
        if (inputId) inputId.value = '';
        if (btnSalvar) btnSalvar.textContent = '✅ Criar Campanha';
        if (btnCancelar) btnCancelar.style.display = 'none';
        if (badgeEdicao) {
            badgeEdicao.textContent = '';
            badgeEdicao.style.display = 'none';
            badgeEdicao.classList.remove('is-dirty');
        }
        const inputBuscaPersonagem = document.getElementById('campanhaPersonagensBusca');
        if (inputBuscaPersonagem) inputBuscaPersonagem.value = '';
        this.filtroTipoParticipanteCampanha = 'todos';
        const filtrosTipo = document.getElementById('campanhaPersonagensTipoFiltros');
        if (filtrosTipo) {
            filtrosTipo.querySelectorAll('[data-campanha-tipo]').forEach((btn) => {
                btn.classList.toggle('active', btn.getAttribute('data-campanha-tipo') === 'todos');
            });
        }
        this._limparSelectPersonagensCampanha();
    }

    _configurarFecharPainelCampanhas() {
        if (!this._isMestre()) return;
        const btnFechar = document.getElementById('btnFecharPainelCampanhas');
        const btnReabrir = document.getElementById('btnReabrirPainelCampanhas');
        const painel = document.getElementById('painelCampanhasMestre');
        const toggle = document.getElementById('campanhasPainelToggle');
        if (!painel || !toggle) return;
        if (!btnFechar) return;
        btnFechar.addEventListener('click', () => {
            painel.style.display = 'none';
            toggle.style.display = '';
        });
        if (btnReabrir) {
            btnReabrir.addEventListener('click', () => {
                painel.style.display = '';
                toggle.style.display = 'none';
            });
        }
    }

    _capturarEstadoFormCampanha() {
        const inputNome = document.getElementById('campanhaNome');
        const inputDescricao = document.getElementById('campanhaDescricao');
        const personagemIds = this._coletarPersonagensCampanhaSelecionados().sort((a, b) => a - b);
        return JSON.stringify({
            nome: (inputNome?.value || '').trim(),
            descricao: (inputDescricao?.value || '').trim(),
            personagem_ids: personagemIds,
        });
    }

    _atualizarEstadoEdicaoCampanha() {
        const badgeEdicao = document.getElementById('campanhaEdicaoBadge');
        if (!badgeEdicao || !this.campanhaEmEdicaoId || !this.snapshotCampanhaEmEdicao) return;
        const atual = this._capturarEstadoFormCampanha();
        const dirty = atual !== this.snapshotCampanhaEmEdicao;
        badgeEdicao.classList.toggle('is-dirty', dirty);
        if (dirty) {
            badgeEdicao.textContent = '✏️ Editando campanha (alteracoes nao salvas)';
        } else {
            const campanha = this.campanhas.find((item) => item.id === this.campanhaEmEdicaoId);
            badgeEdicao.textContent = `✏️ Editando campanha: ${campanha?.nome || ''}`;
        }
    }

    _renderizarTabela(combatentes) {
        const self = this;
        const tbody = document.getElementById('tabelaCombatentes');

        if (!combatentes.length) {
            const mensagemVazio = (this._isMestre() && this.escopoMestre === 'meus')
                ? 'Nenhum combatente encontrado no escopo "Meus".'
                : 'Nenhum combatente cadastrado.';
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:#64748b">${mensagemVazio}</td></tr>`;
            return;
        }

        let rows = '';
        for (const c of combatentes) {
            const podeVerStats = AuthService.podeVerStatsDe(c.tipo);
            const hpTexto = podeVerStats ? c.hp_maximo : '???';
            const iniTexto = podeVerStats ? c.iniciativa : '???';

            rows += `<tr>
                <td><span class="badge badge-${c.tipo}">${escapeHtml(c.tipo)}</span></td>
                <td>${escapeHtml(c.nome)}</td>
                <td>${escapeHtml(c.classe) || '-'}</td>
                <td>${c.nivel || 1}</td>
                <td style="${this._isMestre() ? '' : 'display:none'}">
                    <span class="${podeVerStats ? '' : 'stat-oculto'}">${hpTexto}</span>
                </td>
                <td style="${this._isMestre() ? '' : 'display:none'}">
                    <span class="${podeVerStats ? '' : 'stat-oculto'}">${iniTexto}</span>
                </td>
                <td>
                    <div class="tabela-acoes">
                        <button class="btn-acao btn-ver-ficha" data-id="${c.id}" title="Ver ficha">👁️</button>
                        <button class="btn-acao btn-editar" data-id="${c.id}" title="Editar">✏️</button>
                        ${this._isMestre() ? `<button class="btn-acao btn-excluir" data-id="${c.id}" title="Excluir">🗑️</button>` : ''}
                    </div>
                </td>
            </tr>`;
        }
        tbody.innerHTML = rows;

        // Vincular listeners
        tbody.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                self._abrirEdicao(id);
            });
        });

        tbody.querySelectorAll('.btn-ver-ficha').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                if (!Number.isFinite(id)) {
                    Toast.error('Combatente inválido para abrir ficha.');
                    return;
                }
                window.location.href = `/pages/ficha-personagem.html?id=${id}`;
            });
        });

        if (this._isMestre()) {
            tbody.querySelectorAll('.btn-excluir').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.dataset.id);
                    self._excluirCombatente(id);
                });
            });
        }

    }

    _atualizarResumo(combatentes) {
        const totalEl = document.getElementById('totalGeral');
        const jogEl = document.getElementById('totalJogadores');
        const monEl = document.getElementById('totalMonstros');
        const npcEl = document.getElementById('totalNPCs');
        
        if (totalEl) totalEl.textContent = combatentes.length;
        if (jogEl) jogEl.textContent = this.rules.countByTipo(combatentes, 'jogador');
        if (monEl) monEl.textContent = this.rules.countByTipo(combatentes, 'monstro');
        if (npcEl) npcEl.textContent = this.rules.countByTipo(combatentes, 'npc');
    }

    async _abrirEdicao(id) {
        try {
            const c = await this.service.obterPorId(id);

            if (!this._isMestre() && this.rules.isTipoRestritoParaMestre(c.tipo)) {
                Toast.error('Acesso restrito: você não pode editar monstros ou NPCs.');
                return;
            }

            this.combatenteEmEdicao = c;

            // Preencher campos
            document.getElementById('dashEditId').value = c.id;
            document.getElementById('dashEditTipo').value = c.tipo;
            document.getElementById('dashEditNome').value = c.nome;
            document.getElementById('dashEditHP').value = c.hp_maximo;
            document.getElementById('dashEditIniciativa').value = c.iniciativa;
            document.getElementById('dashEditClasse').value = c.classe || '';
            const editRaceSelect = document.getElementById('dashEditRacaSelect');
            const editRaceFinal = document.getElementById('dashEditRaca');
            const editRaceCustom = document.getElementById('dashEditRacaCustom');
            const raceValue = String(c.raca || '').trim();
            const raceSlug = String(c.raca_slug || '').trim();

            if (editRaceSelect && editRaceFinal && editRaceCustom) {
                const valorOutro = '__OUTRO__';
                const knownRaces = this._listarRacasParaSelect().map((item) => item.nome);
                const isKnownRace = knownRaces.includes(raceValue);
                const editRaceSlug = document.getElementById('dashEditRacaSlug');

                if (!raceValue) {
                    editRaceSelect.value = '';
                    editRaceCustom.value = '';
                } else if (isKnownRace) {
                    editRaceSelect.value = raceValue;
                    editRaceCustom.value = '';
                } else {
                    editRaceSelect.value = valorOutro;
                    editRaceCustom.value = raceValue;
                }

                const preview = document.getElementById('dashEditRacaPreview');
                this._atualizarCampoRaca(editRaceSelect, editRaceFinal, editRaceCustom, editRaceSlug, preview, false);
                if (editRaceSlug && raceSlug) {
                    editRaceSlug.value = raceSlug;
                    this._renderizarPreviewRaca(preview, raceSlug);
                }
            }
            document.getElementById('dashEditDivindade').value = c.divindade || '';
            document.getElementById('dashEditNivel').value = c.nivel || 1;
            document.getElementById('dashEditPontos').value = c.pontos || 0;

            document.getElementById('dashEditFOR').value = c.forca || 10;
            document.getElementById('dashEditDES').value = c.destreza || 10;
            document.getElementById('dashEditCON').value = c.constituicao || 10;
            document.getElementById('dashEditINT').value = c.inteligencia || 10;
            document.getElementById('dashEditSAB').value = c.sabedoria || 10;
            document.getElementById('dashEditCAR').value = c.carisma || 10;

            ['dashEditFOR','dashEditDES','dashEditCON','dashEditINT','dashEditSAB','dashEditCAR'].forEach(fid => {
                const el = document.getElementById(fid);
                if (el) this._calcularModificador(el);
            });

            this._aplicarRegraIniciativaEdicao(c.tipo);

            const secPagRef = document.getElementById('secaoPaginaReferencia');
            const inputPagRef = document.getElementById('dashEditPaginaReferencia');
            if (secPagRef) secPagRef.style.display = this.rules.isTipoMonstro(c.tipo) ? 'block' : 'none';
            if (inputPagRef) inputPagRef.value = this.rules.isTipoMonstro(c.tipo) ? (c.pagina_referencia || '') : '';

            const placeholder = document.getElementById('dashEditUploadPlaceholder');
            const preview = document.getElementById('dashEditUploadPreview');
            const img = document.getElementById('dashEditPreviewImage');
            if (c.foto_url) {
                img.src = c.foto_url;
                placeholder.style.display = 'none';
                preview.style.display = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display = 'none';
            }

            const secAtaques = document.getElementById('secaoAtaquesEdicao');
            if (secAtaques) {
                secAtaques.style.display = this.rules.isTipoJogador(c.tipo) ? 'block' : 'none';
                if (this.rules.isTipoJogador(c.tipo)) this._renderizarAtaquesEdicao(c.ataques || []);
            }

            this._abrirModal('modalEdicaoDashboard');

        } catch (err) {
            Toast.error('Erro ao carregar combatente');
            console.error(err);
        }
    }

    async _excluirCombatente(id) {
        if (!this._isMestre()) {
            Toast.error('Acesso restrito.');
            return;
        }

        if (typeof ModalConfirm === 'undefined') {
            Toast.error('Modal de confirmação não disponível');
            return;
        }

        const self = this;
        ModalConfirm.mostrar({
            icone: '🗑️',
            titulo: 'Excluir Combatente',
            texto: 'Deseja excluir este combatente? Esta ação não pode ser desfeita.',
            textoConfirmar: '🗑️ Excluir',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await self.service.deletar(id);
                    Toast.success('Combatente excluído!');
                    self.carregarCombatentes();
                } catch (err) {
                    Toast.error('Erro ao excluir: ' + err.message);
                    console.error(err);
                }
            }
        });
    }

    async _deletarCombatente() {
        if (!this._isMestre()) {
            Toast.error('Acesso restrito.');
            return;
        }

        if (!this.combatenteEmEdicao) {
            Toast.error('Nenhum combatente selecionado');
            return;
        }

        if (typeof ModalConfirm === 'undefined') {
            Toast.error('Modal de confirmação não disponível');
            return;
        }

        const self = this;
        const nome = this.combatenteEmEdicao.nome;

        ModalConfirm.mostrar({
            icone: '🗑️',
            titulo: 'Deletar Combatente',
            texto: `Deletar <strong>${nome}</strong>? Esta ação não pode ser desfeita.`,
            textoConfirmar: '🗑️ Deletar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await self.service.deletar(self.combatenteEmEdicao.id);
                    Toast.success('Combatente deletado!');
                    self._fecharModal('modalEdicaoDashboard');
                    self.combatenteEmEdicao = null;
                    self.carregarCombatentes();
                } catch (err) {
                    Toast.error('Erro ao deletar: ' + err.message);
                    console.error(err);
                }
            }
        });
    }

    _renderizarAtaquesEdicao(ataques) {
        const lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;
        lista.innerHTML = '';
        if (!ataques.length) {
            this._adicionarLinhaAtaque();
            return;
        }
        ataques.forEach(a => this._adicionarLinhaAtaque(a));
    }

    _adicionarLinhaAtaque(ataque) {
        const lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;

        const dados = {
            nome: ataque?.nome || '',
            bonus: ataque?.bonus_ataque || '+0',
            dano: ataque?.dano || '',
            tipo: ataque?.tipo_dano || '',
        };

        const div = document.createElement('div');
        div.className = 'ataque-linha';

        const inputNome = document.createElement('input');
        inputNome.type = 'text';
        inputNome.className = 'ataque-nome';
        inputNome.placeholder = 'Nome';
        inputNome.value = dados.nome;

        const inputBonus = document.createElement('input');
        inputBonus.type = 'text';
        inputBonus.className = 'ataque-bonus';
        inputBonus.placeholder = '+0';
        inputBonus.value = dados.bonus;
        inputBonus.style.width = '70px';

        const inputDano = document.createElement('input');
        inputDano.type = 'text';
        inputDano.className = 'ataque-dano';
        inputDano.placeholder = '1d6';
        inputDano.value = dados.dano;
        inputDano.style.width = '90px';

        const inputTipo = document.createElement('input');
        inputTipo.type = 'text';
        inputTipo.className = 'ataque-tipo';
        inputTipo.placeholder = 'tipo';
        inputTipo.value = dados.tipo;
        inputTipo.style.width = '120px';

        const btnRemover = document.createElement('button');
        btnRemover.type = 'button';
        btnRemover.className = 'btn-dash-delete';
        btnRemover.textContent = '✕';
        btnRemover.addEventListener('click', () => div.remove());

        div.append(inputNome, inputBonus, inputDano, inputTipo, btnRemover);
        lista.appendChild(div);
    }

    _coletarAtaquesEdicao() {
        return Array.from(document.querySelectorAll('#listaAtaquesEdicao .ataque-linha'))
            .map(l => ({
                nome: l.querySelector('.ataque-nome').value.trim(),
                bonus_ataque: l.querySelector('.ataque-bonus').value.trim() || '+0',
                dano: l.querySelector('.ataque-dano').value.trim() || '1d6',
                tipo_dano: l.querySelector('.ataque-tipo').value.trim()
            }))
            .filter(a => a.nome);
    }

    async _salvarAtaquesEdicao(combatenteId) {
        if (this.ataqueService) {
            await this.ataqueService.salvarAtaques(combatenteId, this._coletarAtaquesEdicao());
        }
    }

    async _salvarPericiasEdicao(combatenteId) {
        if (this.combatenteEmEdicao?.pericias) {
            try {
                sessionStorage.setItem('periciasEdit', JSON.stringify(this.combatenteEmEdicao.pericias));
                sessionStorage.setItem('combatenteEditId', combatenteId);
            } catch (err) {
                console.error('Erro ao salvar perícias:', err);
            }
        }
    }

    _abrirPaginaPericias() {
        if (!this.combatenteEmEdicao?.id) {
            Toast.error('❌ Selecione um combatente primeiro');
            return;
        }

        try {
            const params = new URLSearchParams({
                combatente_id: this.combatenteEmEdicao.id,
                nome: document.getElementById('dashEditNome')?.value || this.combatenteEmEdicao.nome,
                tipo: document.getElementById('dashEditTipo')?.value || this.combatenteEmEdicao.tipo,
                pericias: JSON.stringify(this.combatenteEmEdicao?.pericias || []),
                return_to: encodeURIComponent(window.location.pathname + window.location.search)
            });

            window.location.href = `/pages/pericias.html?${params.toString()}`;
        } catch (err) {
            Toast.error('❌ Erro ao abrir perícias');
            console.error(err);
        }
    }

    // ─── Divindades de Campanha (Mestre/Admin) ────────────────────────────

    _configurarDivindadesCustom() {
        if (!this._isMestre()) return;

        const btnAbrir = document.getElementById('btnNovaDivindade');
        const btnFechar = document.getElementById('btnFecharDivindadeCustom');
        const btnCancelar = document.getElementById('btnCancelarDivindadeCustom');
        const form = document.getElementById('formDivindadeCustom');

        if (btnAbrir) {
            btnAbrir.addEventListener('click', () => this._abrirModalDivindades());
        }
        if (btnFechar) {
            btnFechar.addEventListener('click', () => this._fecharModal('modalDivindadeCustom'));
        }
        if (btnCancelar) {
            btnCancelar.addEventListener('click', () => this._fecharModal('modalDivindadeCustom'));
        }
        if (form) {
            form.addEventListener('submit', (ev) => this._salvarDivindadeCustom(ev));
        }
    }

    async _abrirModalDivindades() {
        this._abrirModal('modalDivindadeCustom');
        await this._carregarDominiosParaModalDivindades();
        await this._recarregarListaDivindadesCustom();
    }

    async _carregarDominiosParaModalDivindades() {
        const container = document.getElementById('divCustomDominiosLista');
        if (!container) return;
        if (this._dominiosCatalogoCache) {
            this._renderizarCheckboxesDominios(container, this._dominiosCatalogoCache);
            return;
        }

        try {
            const res = await fetch(window.getApiUrl('/magias/dominios'), {
                headers: this._getAuthHeader(),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const dominios = await res.json();
            const fallback = ['Animal', 'Planta', 'Ordem', 'Agua'];
            const uniao = Array.from(new Set([...(dominios || []), ...fallback])).sort(
                (a, b) => String(a).localeCompare(String(b), 'pt-BR')
            );
            this._dominiosCatalogoCache = uniao;
            this._renderizarCheckboxesDominios(container, uniao);
        } catch (err) {
            console.warn('⚠️ Não foi possível carregar domínios do backend:', err);
            const fallback = [
                'Ar', 'Animal', 'Bem', 'Caos', 'Conhecimento', 'Cura', 'Destruicao',
                'Enganacao', 'Fogo', 'Forca', 'Guerra', 'Magia', 'Mal', 'Morte',
                'Ordem', 'Planta', 'Protecao', 'Sol', 'Sorte', 'Terra', 'Viagem', 'Agua',
            ].sort((a, b) => a.localeCompare(b, 'pt-BR'));
            this._dominiosCatalogoCache = fallback;
            this._renderizarCheckboxesDominios(container, fallback);
        }
    }

    _renderizarCheckboxesDominios(container, dominios) {
        const html = (dominios || []).map((dominio) => {
            const val = escapeHtml(String(dominio));
            return `
                <label class="dash-divcustom-dominio-item">
                    <input type="checkbox" name="dominios" value="${val}" />
                    <span>${val}</span>
                </label>`;
        }).join('');
        container.innerHTML = html || '<p class="dash-divcustom-vazio">Nenhum domínio disponível.</p>';
    }

    _coletarDominiosSelecionados() {
        const checks = document.querySelectorAll('#divCustomDominiosLista input[type="checkbox"]:checked');
        return Array.from(checks).map((c) => c.value).filter(Boolean);
    }

    async _salvarDivindadeCustom(ev) {
        ev.preventDefault();
        if (!this.divindadeService) {
            Toast.error('Serviço de divindades indisponível.');
            return;
        }
        const nome = document.getElementById('divCustomNome')?.value?.trim() || '';
        const titulo = document.getElementById('divCustomTitulo')?.value?.trim() || '';
        const tendencia = document.getElementById('divCustomTendencia')?.value?.trim() || '';
        const descricao = document.getElementById('divCustomDescricao')?.value?.trim() || '';
        const dominios = this._coletarDominiosSelecionados();

        if (!nome) {
            Toast.error('Informe o nome da divindade.');
            return;
        }
        if (!tendencia) {
            Toast.error('Selecione a tendência/alinhamento.');
            return;
        }
        if (dominios.length === 0) {
            Toast.error('Selecione ao menos um domínio.');
            return;
        }

        const btn = document.getElementById('btnSalvarDivindadeCustom');
        if (btn) btn.disabled = true;
        try {
            await this.divindadeService.criar({
                nome,
                titulo,
                tendencia,
                dominios,
                descricao: descricao || null,
            });
            Toast.success(`Divindade '${nome}' adicionada com sucesso!`);
            document.getElementById('formDivindadeCustom')?.reset();
            this._coletarDominiosSelecionados(); // apenas para consistência
            await this._recarregarListaDivindadesCustom();
        } catch (err) {
            console.error('❌ Erro ao criar divindade custom:', err);
            Toast.error(err?.message || 'Erro ao criar divindade.');
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    async _recarregarListaDivindadesCustom() {
        const box = document.getElementById('divCustomListagem');
        if (!box || !this.divindadeService) return;
        box.innerHTML = '<p class="dash-divcustom-vazio">Carregando…</p>';

        let itens = [];
        try {
            itens = await this.divindadeService.listarCustomizadas();
        } catch (err) {
            console.error('❌ Erro ao listar divindades custom:', err);
            box.innerHTML = `<p class="dash-divcustom-vazio">${escapeHtml(err?.message || 'Erro ao carregar.')}</p>`;
            return;
        }

        if (!Array.isArray(itens) || itens.length === 0) {
            box.innerHTML = '<p class="dash-divcustom-vazio">Nenhuma divindade de campanha cadastrada ainda.</p>';
            return;
        }

        const html = itens.map((item) => {
            const id = Number(item.id);
            const label = escapeHtml(item.label || item.nome || '');
            const tendencia = escapeHtml(item.tendencia || '');
            const dominios = Array.isArray(item.dominios) ? item.dominios.map(escapeHtml).join(', ') : '';
            const descricao = escapeHtml(item.descricao || '');
            return `
                <div class="dash-divcustom-card" data-id="${id}">
                    <div class="dash-divcustom-card-head">
                        <strong>${label}</strong>
                        <button type="button" class="btn-dash-delete-div" data-delete-div="${id}" title="Excluir divindade">✕</button>
                    </div>
                    <div class="dash-divcustom-card-meta">
                        <span><b>Tendência:</b> ${tendencia || '—'}</span>
                        <span><b>Domínios:</b> ${dominios || '—'}</span>
                    </div>
                    ${descricao ? `<p class="dash-divcustom-card-desc">${descricao}</p>` : ''}
                </div>`;
        }).join('');
        box.innerHTML = html;

        box.querySelectorAll('[data-delete-div]').forEach((btn) => {
            btn.addEventListener('click', () => {
                const id = Number(btn.getAttribute('data-delete-div'));
                if (Number.isFinite(id)) this._confirmarExclusaoDivindade(id, btn);
            });
        });
    }

    async _confirmarExclusaoDivindade(divindadeId, botaoOrigem) {
        const card = botaoOrigem?.closest('.dash-divcustom-card');
        const nomeLabel = card?.querySelector('strong')?.textContent || 'esta divindade';
        const confirmar = async () => {
            try {
                await this.divindadeService.deletar(divindadeId);
                Toast.success('Divindade removida.');
                await this._recarregarListaDivindadesCustom();
            } catch (err) {
                console.error('❌ Erro ao excluir divindade:', err);
                Toast.error(err?.message || 'Erro ao excluir divindade.');
            }
        };

        if (typeof ModalConfirm !== 'undefined' && typeof ModalConfirm.show === 'function') {
            ModalConfirm.show({
                titulo: 'Excluir divindade',
                mensagem: `Remover "${nomeLabel}" do catálogo de campanha?`,
                textoConfirmar: 'Excluir',
                textoCancelar: 'Cancelar',
                onConfirmar: confirmar,
            });
        } else if (window.confirm(`Remover "${nomeLabel}" do catálogo de campanha?`)) {
            await confirmar();
        }
    }

    // ─────────────────────────────────────────────────────────────────────

    _abrirModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('show');
    }

    _fecharModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('show');
    }

    _previewImagem(input, previewId, imgId, placeholderId) {
        const file = input.files?.[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const ph = document.getElementById(placeholderId);
            const pv = document.getElementById(previewId);
            const im = document.getElementById(imgId);
            if (ph) ph.style.display = 'none';
            if (pv) pv.style.display = 'block';
            if (im) im.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    _removerImagem(sufixo, isEdit) {
        const inputId = isEdit ? 'dashEditFoto' : 'inputFoto' + sufixo;
        const placeholderId = isEdit ? 'dashEditUploadPlaceholder' : 'uploadPlaceholder' + sufixo;
        const previewId = isEdit ? 'dashEditUploadPreview' : 'uploadPreview' + sufixo;
        
        const input = document.getElementById(inputId);
        const placeholder = document.getElementById(placeholderId);
        const preview = document.getElementById(previewId);
        
        if (input) input.value = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview) preview.style.display = 'none';
    }

    _calcularModificador(input) {
        const valor = parseInt(input.value) || 10;
        const mod = Math.floor((valor - 10) / 2);
        const modId = 'mod' + input.id.charAt(0).toUpperCase() + input.id.slice(1);
        const span = document.getElementById(modId);
        if (span) span.textContent = mod >= 0 ? `+${mod}` : `${mod}`;
    }

    _aplicarRegraIniciativaEdicao(tipo) {
        const grupoIniciativa = document.getElementById('dashEditGrupoIniciativa');
        const inputIniciativa = document.getElementById('dashEditIniciativa');
        const ehJogador = this.rules.isTipoJogador(tipo);
        if (!grupoIniciativa || !inputIniciativa) return;

        if (ehJogador) {
            grupoIniciativa.style.display = 'none';
            inputIniciativa.required = false;
            this._preencherIniciativaSugeridaPorDestrezaEdicao();
            return;
        }

        grupoIniciativa.style.display = '';
        inputIniciativa.required = true;
    }

    _preencherIniciativaSugeridaPorDestrezaEdicao() {
        if (!this.combatenteEmEdicao || !this.rules.isTipoJogador(this.combatenteEmEdicao.tipo)) return;
        const elDes = document.getElementById('dashEditDES');
        const elIni = document.getElementById('dashEditIniciativa');
        if (!elDes || !elIni) return;
        const d = parseInt(elDes.value, 10);
        const des = Number.isFinite(d) ? Math.min(30, Math.max(1, d)) : 10;
        const mod = Math.floor((des - 10) / 2);
        // Regra base D&D 3.5: iniciativa = mod DES (+ talentos/itens em etapa futura)
        elIni.value = String(mod);
    }

    _limparForm(form, tipo) {
        form.reset();
        this._sincronizarCamposRaca(form, true);
        const sufixos = { jogador: '', monstro: 'Monstro', npc: 'NPC' };
        const sufixo = sufixos[tipo] || '';
        const ph = document.getElementById('uploadPlaceholder' + sufixo);
        const pv = document.getElementById('uploadPreview' + sufixo);
        if (ph) ph.style.display = 'flex';
        if (pv) pv.style.display = 'none';
    }
}

// Serviço Global de Combatentes
class CombatenteServiceGlobal {
    _url(path) {
        return window.getApiUrl('/combatentes' + (path || '')); 
    }

    _headers() {
        const h = {};
        if (typeof AuthService !== 'undefined') {
            const t = AuthService.getToken();
            if (t) h['Authorization'] = `Bearer ${t}`;
        }
        return h;
    }

    async _handleResponse(res, fallbackMessage) {
        if (res.status === 401) {
            if (typeof AuthService !== 'undefined' && typeof AuthService.logout === 'function') {
                AuthService.logout();
            }
            throw new Error('Token inválido ou expirado. Faça login novamente.');
        }

        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || fallbackMessage);
        }

        return res;
    }

    async listar(tipo, somenteMeus = false) {
        const params = new URLSearchParams();
        if (tipo) params.set('tipo', tipo);
        if (somenteMeus) params.set('meus', 'true');
        const query = params.toString();
        const url = query ? `${this._url()}?${query}` : this._url();
        const res = await fetch(url, { headers: this._headers() });
        await this._handleResponse(res, 'Erro ao carregar combatentes');
        return res.json();
    }

    async obterPorId(id) {
        const res = await fetch(this._url(`/${id}`), { headers: this._headers() });
        await this._handleResponse(res, 'Combatente não encontrado');
        return res.json();
    }

    async criar(formData) {
        const res = await fetch(this._url(), { method: 'POST', headers: this._headers(), body: formData });
        await this._handleResponse(res, 'Erro ao criar');
        return res.json();
    }

    async atualizar(id, formData) {
        const res = await fetch(this._url(`/${id}`), { method: 'PUT', headers: this._headers(), body: formData });
        await this._handleResponse(res, 'Erro ao atualizar');
        return res.json();
    }

    async deletar(id) {
        const res = await fetch(this._url(`/${id}`), { method: 'DELETE', headers: this._headers() });
        await this._handleResponse(res, 'Erro ao deletar');
        return true;
    }
}

function _exibirFallbackDashboard(mensagem) {
    if (typeof Toast !== 'undefined' && Toast && typeof Toast.error === 'function') {
        Toast.error(mensagem);
        return;
    }

    const id = 'dashboard-degraded-banner';
    if (document.getElementById(id)) return;
    const banner = document.createElement('div');
    banner.id = id;
    banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:9999;background:#7f1d1d;color:#fff;padding:10px 14px;font-size:14px;';
    banner.textContent = mensagem;
    document.body.appendChild(banner);
}

function _inicializarDashboardComResiliencia() {
    try {
        window._dashboardController = new DashboardController();
    } catch (error) {
        console.error('❌ Falha no bootstrap do DashboardController:', error);
        _exibirFallbackDashboard('Falha ao iniciar dashboard. Tente recarregar a pagina.');
    }
}

// Inicializar após DOM pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _inicializarDashboardComResiliencia);
} else {
    _inicializarDashboardComResiliencia();
}