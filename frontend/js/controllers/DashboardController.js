/**
 * DashboardController.js
 * SOLID: SRP - gerencia apenas dashboard de combatentes
 * Dependências globais: AuthService, Toast, ModalConfirm, AtaqueService
 */

const DIVINDADES_SUGERIDAS_FALLBACK = [
    'Boccob',
    'Corellon Larethian',
    'Ehlonna',
    'Erythnul',
    'Heironeous',
    'Hextor',
    'Kord',
    'Nerull',
    'Obad-Hai',
    'St. Cuthbert',
    'Wee Jas',
];

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
        this.filtroAtual        = 'todos';
        this.combatenteEmEdicao = null;
        this.actions             = {};
        this.perfil              = AuthService.getPerfil();
        this.divindadesSugeridas = [...DIVINDADES_SUGERIDAS_FALLBACK];
        this.fonteDivindades     = 'fallback';
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
        this._renderizarListaDivindades();
        this._atualizarHintDivindades();
        this._carregarDivindadesSugeridas();
        this._configurarLinksGovernanca();

        this._aplicarRestricoesPerfil();
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarCombosRaca();
        this._configurarFormCadastro('formCadastroJogador', 'jogador', 'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro', 'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC', 'npc', 'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarAcoesModaisSemInline();
        this._configurarUpload('');
        this._configurarUpload('Monstro');
        this._configurarUpload('NPC');
        this._configurarUploadEdicao();
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

    async _carregarDivindadesSugeridas() {
        try {
            const response = await fetch(window.getApiUrl('/magias/divindades'), {
                headers: this._getAuthHeader(),
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const divindades = await response.json();
            if (Array.isArray(divindades) && divindades.length > 0) {
                this.divindadesSugeridas = [...new Set(
                    divindades
                        .map((divindade) => String(divindade).trim())
                        .filter(Boolean),
                )];
                this.fonteDivindades = 'catalogo';
            }
        } catch (error) {
            console.warn('⚠️ Não foi possível carregar divindades sugeridas no dashboard:', error);
            this.divindadesSugeridas = [...DIVINDADES_SUGERIDAS_FALLBACK];
            this.fonteDivindades = 'fallback';
        }

        this._renderizarListaDivindades();
        this._atualizarHintDivindades();
    }

    _renderizarListaDivindades() {
        const lista = document.getElementById('listaDivindadesDashboard');
        if (!lista) return;

        lista.innerHTML = this.divindadesSugeridas
            .map((divindade) => `<option value="${escapeHtml(divindade)}"></option>`)
            .join('');
    }

    _atualizarHintDivindades() {
        const hintCadastro = document.getElementById('hintDivindadeCadastroJogador');
        const hintEdicao = document.getElementById('hintDivindadeEdicao');
        const veioDoCatalogo = this.fonteDivindades === 'catalogo';
        const total = Array.isArray(this.divindadesSugeridas) ? this.divindadesSugeridas.length : 0;
        const singular = total === 1;
        const sufixoQuantidade = `${total} sugest${singular ? 'ão' : 'ões'}`;
        const sufixoCarga = singular ? 'carregada' : 'carregadas';
        const sufixoLocal = singular ? 'local ativa' : 'locais ativas';

        if (total === 0) {
            [hintCadastro, hintEdicao].forEach((hint) => {
                if (!hint) return;
                hint.textContent = 'Nenhuma sugestão disponível no momento.';
                hint.classList.toggle('is-fallback', true);
            });
            return;
        }

        const texto = veioDoCatalogo
            ? `${sufixoQuantidade} ${sufixoCarga} do catálogo.`
            : `${sufixoQuantidade} ${sufixoLocal} (catálogo indisponível no momento).`;

        [hintCadastro, hintEdicao].forEach((hint) => {
            if (!hint) return;
            hint.textContent = texto;
            hint.classList.toggle('is-fallback', !veioDoCatalogo);
        });
    }

    _configurarLinksGovernanca() {
        const linkMagias = document.getElementById('linkMagias');
        if (linkMagias) {
            linkMagias.style.display = this._isMestre() ? '' : 'none';
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
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!self._isMestre() && self.rules.isTipoRestritoParaMestre(btn.dataset.tipo)) return;
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                self.filtroAtual = btn.dataset.tipo;
                self.carregarCombatentes();
            });
        });
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
            { selectId: 'cadastroJogadorRacaSelect', finalId: 'cadastroJogadorRacaFinal', customId: 'cadastroJogadorRacaCustom' },
            { selectId: 'cadastroNpcRacaSelect', finalId: 'cadastroNpcRacaFinal', customId: 'cadastroNpcRacaCustom' },
            { selectId: 'dashEditRacaSelect', finalId: 'dashEditRaca', customId: 'dashEditRacaCustom' },
        ];

        combos.forEach((cfg) => {
            const selectEl = document.getElementById(cfg.selectId);
            const finalEl = document.getElementById(cfg.finalId);
            const customEl = document.getElementById(cfg.customId);

            if (!selectEl || !finalEl || !customEl) return;

            if (window.RacasPHB?.preencherSelect) {
                window.RacasPHB.preencherSelect(selectEl, {
                    incluirVazio: true,
                    textoVazio: '-- Selecione uma raça --',
                    incluirOutro: true,
                });
            }

            selectEl.addEventListener('change', () => this._atualizarCampoRaca(selectEl, finalEl, customEl));
            customEl.addEventListener('input', () => this._atualizarCampoRaca(selectEl, finalEl, customEl));

            this._atualizarCampoRaca(selectEl, finalEl, customEl, true);
        });
    }

    _atualizarCampoRaca(selectEl, finalEl, customEl, limparCustom = false) {
        if (!selectEl || !finalEl || !customEl) return;

        const valorOutro = window.RacasPHB?.valorOutro?.() || '__OUTRO__';
        const selecionouOutro = selectEl.value === valorOutro;

        if (selecionouOutro) {
            customEl.style.display = 'block';
            if (limparCustom) customEl.value = '';
            finalEl.value = String(customEl.value || '').trim();
            return;
        }

        if (limparCustom) customEl.value = '';
        customEl.style.display = 'none';
        finalEl.value = String(selectEl.value || '').trim();
    }

    _sincronizarCamposRaca(form, limparCustom = false) {
        if (!form) return;

        const selects = form.querySelectorAll('[data-raca-select]');
        selects.forEach((selectEl) => {
            const key = selectEl.getAttribute('data-raca-key');
            if (!key) return;

            const finalEl = form.querySelector(`[data-raca-final][data-raca-key="${key}"]`);
            const customEl = form.querySelector(`[data-raca-custom][data-raca-key="${key}"]`);
            this._atualizarCampoRaca(selectEl, finalEl, customEl, limparCustom);
        });
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
            input.addEventListener('input', () => this._calcularModificador(input));
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

            const combatentes = await this.service.listar(tipo);
            this._renderizarTabela(combatentes);
            this._atualizarResumo(combatentes);
        } catch (err) {
            Toast.error('Erro ao carregar combatentes');
            console.error(err);
        }
    }

    _renderizarTabela(combatentes) {
        const self = this;
        const tbody = document.getElementById('tabelaCombatentes');

        if (!combatentes.length) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:#64748b">Nenhum combatente cadastrado.</td></tr>';
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

            if (editRaceSelect && editRaceFinal && editRaceCustom) {
                const valorOutro = window.RacasPHB?.valorOutro?.() || '__OUTRO__';
                const knownRaces = window.RacasPHB?.listar?.() || [];
                const isKnownRace = knownRaces.includes(raceValue);

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

                this._atualizarCampoRaca(editRaceSelect, editRaceFinal, editRaceCustom, false);
            }
            document.getElementById('dashEditDivindade').value = c.divindade || '';
            document.getElementById('dashEditNivel').value = c.nivel || 1;
            document.getElementById('dashEditPontos').value = c.pontos || 0;

            document.getElementById('dashEditCA').value = c.ca ?? 10;
            document.getElementById('dashEditToque').value = c.toque ?? 10;
            document.getElementById('dashEditSurpresa').value = c.surpresa ?? 10;
            document.getElementById('dashEditFortitude').value = c.fortitude ?? 0;
            document.getElementById('dashEditReflexos').value = c.reflexos ?? 0;
            document.getElementById('dashEditVontade').value = c.vontade ?? 0;

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

    async listar(tipo) {
        const url = tipo ? `${this._url()}?tipo=${tipo}` : this._url();
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