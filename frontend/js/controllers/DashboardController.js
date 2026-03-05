/**
 * DashboardController
 * SRP: orquestra a tela de dashboard (listagem, cadastro e edição de combatentes)
 * DIP: depende de CombatenteService e UploadService globais (carregados via script)
 *
 * NOTA: Este controller usa as classes globais (não ES modules) porque o dashboard
 * carrega scripts dinamicamente sem type="module". As classes ModalCadastroInline
 * e ModalEdicaoInline são definidas aqui mesmo para evitar conflito de escopo.
 */
class DashboardController {

    constructor() {
        this.service       = new CombatenteServiceGlobal();
        this.uploadService = new UploadServiceGlobal();
        this.filtroAtual   = 'todos';
        this.combatenteEmEdicao = null;

        this._registrarGlobais();
        this._inicializar();
    }

    // ── Registra funções globais chamadas pelos botões inline dos modais ──

    _registrarGlobais() {
        // Cadastro
        window.fecharModalCadastro        = () => this._fecharModal('modalCadastroJogador');
        window.fecharModalCadastroMonstro = () => this._fecharModal('modalCadastroMonstro');
        window.fecharModalCadastroNPC     = () => this._fecharModal('modalCadastroNPC');
        window.fecharSeletorTipo          = () => this._fecharModal('seletorTipo');

        window.abrirModalCadastro = (tipo) => {
            this._fecharModal('seletorTipo');
            const ids = { jogador: 'modalCadastroJogador', monstro: 'modalCadastroMonstro', npc: 'modalCadastroNPC' };
            this._abrirModal(ids[tipo]);
        };

        // Edição
        window.fecharModalEdicao   = () => this._fecharModal('modalEdicaoDashboard');
        window.confirmarDelecao    = () => this._deletarCombatente();
        window.atualizarModificador = (input) => this._calcularModificador(input);

        // Upload
        window.previewImagemUpload    = (input, previewId, imgId, placeholderId) =>
            this._previewImagem(input, previewId, imgId, placeholderId);
        window.removerImagem          = () => this._removerImagem('', false);
        window.removerImagemMonstro   = () => this._removerImagem('Monstro', false);
        window.removerImagemNPC       = () => this._removerImagem('NPC', false);
        window.removerImagemEdicao    = () => this._removerImagem('Edit', true);
    }

    // ── Init 

    _inicializar() {
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarFormCadastro('formCadastroJogador', 'jogador',  'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro',  'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC',     'npc',      'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarUpload('',       'modalCadastroJogador');
        this._configurarUpload('Monstro','modalCadastroMonstro');
        this._configurarUpload('NPC',    'modalCadastroNPC');
        this._configurarUploadEdicao();
        this.carregarCombatentes();
    }

    // ── Abas 

    _configurarAbas() {
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
            });
        });
    }

    // ── Filtros 

    _configurarFiltros() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filtroAtual = btn.dataset.tipo;
                this.carregarCombatentes();
            });
        });
    }

    // ── Botão novo 

    _configurarBotaoNovo() {
        document.getElementById('btnNovoCombatente')
            .addEventListener('click', () => this._abrirModal('seletorTipo'));
    }

    // ── Formulários de cadastro 

    _configurarFormCadastro(formId, tipo, modalId) {
        const form = document.getElementById(formId);
        if (!form) { console.error(`❌ Form não encontrado: ${formId}`); return; }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';

            try {
                const formData = new FormData(form);
                const combatente = await this.service.criar(formData);
                Toast.success(`${combatente.nome} cadastrado com sucesso!`);
                this._fecharModal(modalId);
                this._limparForm(form, tipo);
                this.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao cadastrar');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = tipo === 'jogador' ? '✅ Cadastrar Jogador'
                                : tipo === 'monstro' ? '✅ Cadastrar Monstro'
                                : '✅ Cadastrar NPC';
            }
        });
    }

    // ── Formulário de edição 

    _configurarFormEdicao() {
        const form = document.getElementById('formEdicaoDashboard');
        if (!form) { console.error('❌ Form edição não encontrado'); return; }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';

            try {
                const id       = parseInt(document.getElementById('dashEditId').value);
                const formData = new FormData(form);
                await this.service.atualizar(id, formData);
                Toast.success('Combatente atualizado! ✅');
                this._fecharModal('modalEdicaoDashboard');
                this.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao atualizar');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = '💾 Salvar Alterações';
            }
        });
    }

    // ── Upload de imagem (cadastro) ───────────────────────────────────────

    _configurarUpload(sufixo, modalId) {
        const inputId       = `inputFoto${sufixo}`;
        const placeholderId = `uploadPlaceholder${sufixo}`;
        const previewId     = `uploadPreview${sufixo}`;
        const imgId         = `previewImage${sufixo}`;

        const input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            this._previewImagem(input, previewId, imgId, placeholderId);
        });
    }

    // ── Upload de imagem (edição) 

    _configurarUploadEdicao() {
        const area  = document.getElementById('dashEditUploadArea');
        const input = document.getElementById('dashEditFoto');
        if (!area || !input) return;

        area.addEventListener('click', () => input.click());
        input.addEventListener('change', () => {
            this._previewImagem(
                input,
                'dashEditUploadPreview',
                'dashEditPreviewImage',
                'dashEditUploadPlaceholder'
            );
        });
    }

    // ── Carrega combatentes 

    async carregarCombatentes() {
        try {
            const tipo        = this.filtroAtual === 'todos' ? null : this.filtroAtual;
            const combatentes = await this.service.listar(tipo);
            this._renderizarTabela(combatentes);
            this._atualizarResumo(combatentes);
        } catch (err) {
            Toast.error('Erro ao carregar combatentes');
            console.error(err);
        }
    }

    // ── Renderiza tabela 

    _renderizarTabela(combatentes) {
        const tbody = document.getElementById('tabelaCombatentes');
        if (!combatentes.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align:center;padding:2rem;color:#64748b">
                        Nenhum combatente. Clique em "+ Novo Combatente" para cadastrar.
                    </td>
                </tr>`;
            return;
        }

        tbody.innerHTML = combatentes.map(c => `
            <tr>
                <td><span class="badge badge-${c.tipo}">${c.tipo}</span></td>
                <td>${c.nome}</td>
                <td>${c.classe || '—'}</td>
                <td>${c.nivel || 1}</td>
                <td>${c.hp_maximo}</td>
                <td>${c.iniciativa}</td>
                <td>
                    <button class="btn-acao" title="Editar"  data-id="${c.id}" data-acao="editar">✏️</button>
                    <button class="btn-acao" title="Excluir" data-id="${c.id}" data-acao="excluir">🗑️</button>
                </td>
            </tr>
        `).join('');

        tbody.querySelectorAll('[data-acao="editar"]').forEach(btn =>
            btn.addEventListener('click', () => this._abrirEdicao(parseInt(btn.dataset.id)))
        );
        tbody.querySelectorAll('[data-acao="excluir"]').forEach(btn =>
            btn.addEventListener('click', () => this._excluirCombatente(parseInt(btn.dataset.id)))
        );
    }

    // ── Resumo 

    _atualizarResumo(combatentes) {
        document.getElementById('totalGeral').textContent     = combatentes.length;
        document.getElementById('totalJogadores').textContent = combatentes.filter(c => c.tipo === 'jogador').length;
        document.getElementById('totalMonstros').textContent  = combatentes.filter(c => c.tipo === 'monstro').length;
        document.getElementById('totalNPCs').textContent      = combatentes.filter(c => c.tipo === 'npc').length;
    }

    // ── Edição 

    async _abrirEdicao(id) {
        try {
            const c = await this.service.obterPorId(id);
            this.combatenteEmEdicao = c;

            // Preenche formulário
            document.getElementById('dashEditId').value         = c.id;
            document.getElementById('dashEditTipo').value       = c.tipo;
            document.getElementById('dashEditNome').value       = c.nome;
            document.getElementById('dashEditHP').value         = c.hp_maximo;
            document.getElementById('dashEditIniciativa').value = c.iniciativa;
            document.getElementById('dashEditClasse').value     = c.classe   || '';
            document.getElementById('dashEditNivel').value      = c.nivel    || 1;
            document.getElementById('dashEditPontos').value     = c.pontos   || 0;
            document.getElementById('dashEditCA').value         = c.ca       ?? 10;
            document.getElementById('dashEditToque').value      = c.toque    ?? 10;
            document.getElementById('dashEditSurpresa').value   = c.surpresa ?? 10;
            document.getElementById('dashEditFOR').value        = c.forca         || 10;
            document.getElementById('dashEditDES').value        = c.destreza      || 10;
            document.getElementById('dashEditCON').value        = c.constituicao  || 10;
            document.getElementById('dashEditINT').value        = c.inteligencia  || 10;
            document.getElementById('dashEditSAB').value        = c.sabedoria     || 10;
            document.getElementById('dashEditCAR').value        = c.carisma       || 10;
            document.getElementById('dashEditFortitude').value  = c.fortitude     ?? 0;
            document.getElementById('dashEditReflexos').value   = c.reflexos      ?? 0;
            document.getElementById('dashEditVontade').value    = c.vontade       ?? 0;

            // Atualiza modificadores
            ['dashEditFOR','dashEditDES','dashEditCON','dashEditINT','dashEditSAB','dashEditCAR'].forEach(id => {
                const el = document.getElementById(id);
                if (el) this._calcularModificador(el);
            });

            // Preview da foto
            const placeholder = document.getElementById('dashEditUploadPlaceholder');
            const preview     = document.getElementById('dashEditUploadPreview');
            const img         = document.getElementById('dashEditPreviewImage');

            if (c.foto_url) {
                img.src                  = c.foto_url;
                placeholder.style.display = 'none';
                preview.style.display     = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display     = 'none';
            }

            this._abrirModal('modalEdicaoDashboard');
        } catch (err) {
            Toast.error('Erro ao carregar combatente');
            console.error(err);
        }
    }

    async _excluirCombatente(id) {
        if (!confirm('Deseja excluir este combatente?')) return;
        try {
            await this.service.deletar(id);
            Toast.success('Combatente excluído! 🗑️');
            this.carregarCombatentes();
        } catch (err) {
            Toast.error('Erro ao excluir combatente');
            console.error(err);
        }
    }

    async _deletarCombatente() {
        if (!this.combatenteEmEdicao) return;
        if (!confirm(`Deseja realmente deletar ${this.combatenteEmEdicao.nome}?`)) return;
        try {
            await this.service.deletar(this.combatenteEmEdicao.id);
            Toast.success('Combatente deletado! 🗑️');
            this._fecharModal('modalEdicaoDashboard');
            this.combatenteEmEdicao = null;
            this.carregarCombatentes();
        } catch (err) {
            Toast.error('Erro ao deletar');
            console.error(err);
        }
    }

    // ── Helpers de modal 

    _abrirModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('show');
        else console.error(`❌ Modal não encontrado: ${id}`);
    }

    _fecharModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('show');
    }

    // ── Helpers de upload 

    _previewImagem(input, previewId, imgId, placeholderId) {
        const file = (input instanceof HTMLInputElement) ? input.files[0] : input.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = e => {
            const ph = document.getElementById(placeholderId);
            const pv = document.getElementById(previewId);
            const im = document.getElementById(imgId);
            if (ph) ph.style.display = 'none';
            if (pv) pv.style.display = 'block';
            if (im) im.src           = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    _removerImagem(sufixo, isEdit) {
        const inputId       = isEdit ? 'dashEditFoto'              : `inputFoto${sufixo}`;
        const placeholderId = isEdit ? 'dashEditUploadPlaceholder' : `uploadPlaceholder${sufixo}`;
        const previewId     = isEdit ? 'dashEditUploadPreview'     : `uploadPreview${sufixo}`;

        const input       = document.getElementById(inputId);
        const placeholder = document.getElementById(placeholderId);
        const preview     = document.getElementById(previewId);

        if (input)       input.value             = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview)     preview.style.display     = 'none';
    }

    // ── Helpers de atributos D&D 

    _calcularModificador(input) {
        const valor = parseInt(input.value) || 10;
        const mod   = Math.floor((valor - 10) / 2);
        const span  = input.closest('.atributo-field')?.querySelector('.atributo-modificador');
        if (span) span.textContent = mod >= 0 ? `+${mod}` : `${mod}`;
    }

    // ── Limpa formulário de cadastro ──────────────────────────────────────

    _limparForm(form, tipo) {
        form.reset();
        const sufixo = tipo === 'jogador' ? '' : tipo === 'monstro' ? 'Monstro' : 'NPC';
        const ph = document.getElementById(`uploadPlaceholder${sufixo}`);
        const pv = document.getElementById(`uploadPreview${sufixo}`);
        if (ph) ph.style.display = 'flex';
        if (pv) pv.style.display = 'none';
    }
}

// ── CombatenteServiceGlobal 
// Versão global (sem import/export) para uso no dashboard
// SRP: apenas comunicação HTTP com a API de combatentes

class CombatenteServiceGlobal {

    _url(path = '') { return getApiUrl(`/combatentes${path}`); }

    async listar(tipo = null) {
        const url      = tipo ? `${this._url()}?tipo=${tipo}` : this._url();
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erro ao carregar combatentes');
        return response.json();
    }

    async obterPorId(id) {
        const response = await fetch(this._url(`/${id}`));
        if (!response.ok) throw new Error('Combatente não encontrado');
        return response.json();
    }

    async criar(formData) {
        const response = await fetch(this._url(), { method: 'POST', body: formData });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erro ao criar combatente');
        }
        return response.json();
    }

    async atualizar(id, formData) {
        const response = await fetch(this._url(`/${id}`), { method: 'PUT', body: formData });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Erro ao atualizar combatente');
        }
        return response.json();
    }

    async deletar(id) {
        const response = await fetch(this._url(`/${id}`), { method: 'DELETE' });
        if (!response.ok) throw new Error('Erro ao deletar combatente');
        return true;
    }
}

// ── UploadServiceGlobal 
// Versão global (sem import/export) para preview de imagens

class UploadServiceGlobal {
    criarPreview(file, callback) {
        if (!file.type.startsWith('image/')) throw new Error('Arquivo deve ser uma imagem');
        const reader = new FileReader();
        reader.onload = e => callback(e.target.result);
        reader.readAsDataURL(file);
    }
}

// ── Instancia após DOM pronto 
new DashboardController();