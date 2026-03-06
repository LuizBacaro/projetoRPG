/**
 * DashboardController
 * SRP: orquestra listagem, cadastro e edição de combatentes no dashboard
 * DIP: depende de CombatenteServiceGlobal e AtaqueService via window global
 *
 * Carregado via createElement (sem type="module")
 * Ordem obrigatória: AuthService → Toast → AtaqueService → DashboardController
 */
class DashboardController {

    constructor() {
        this.service            = new CombatenteServiceGlobal();
        this.ataqueService      = new AtaqueService();
        this.filtroAtual        = 'todos';
        this.combatenteEmEdicao = null;
        this._registrarGlobais();
        this._inicializar();
    }

    // ── Globais ───────────────────────────────────────────────────────────

    _registrarGlobais() {
        window.fecharModalCadastro        = () => this._fecharModal('modalCadastroJogador');
        window.fecharModalCadastroMonstro = () => this._fecharModal('modalCadastroMonstro');
        window.fecharModalCadastroNPC     = () => this._fecharModal('modalCadastroNPC');
        window.fecharSeletorTipo          = () => this._fecharModal('seletorTipo');
        window.fecharModalEdicao          = () => this._fecharModal('modalEdicaoDashboard');

        window.abrirModalCadastro = (tipo) => {
            this._fecharModal('seletorTipo');
            const mapa = {
                jogador: 'modalCadastroJogador',
                monstro: 'modalCadastroMonstro',
                npc:     'modalCadastroNPC'
            };
            this._abrirModal(mapa[tipo]);
        };

        window.confirmarDelecao     = () => this._deletarCombatente();
        window.atualizarModificador = (input) => this._calcularModificador(input);

        window.previewImagemUpload  = (input, previewId, imgId, placeholderId) =>
            this._previewImagem(input, previewId, imgId, placeholderId);
        window.removerImagem        = () => this._removerImagem('',        false);
        window.removerImagemMonstro = () => this._removerImagem('Monstro', false);
        window.removerImagemNPC     = () => this._removerImagem('NPC',     false);
        window.removerImagemEdicao  = () => this._removerImagem('',        true);

        window.adicionarLinhaAtaque = () => this._adicionarLinhaAtaque();
        window.removerLinhaAtaque   = (btn) => btn.closest('.ataque-linha').remove();
    }

    // ── Inicialização ─────────────────────────────────────────────────────

    _inicializar() {
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarFormCadastro('formCadastroJogador', 'jogador', 'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro', 'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC',     'npc',     'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarUpload('');
        this._configurarUpload('Monstro');
        this._configurarUpload('NPC');
        this._configurarUploadEdicao();
        this.carregarCombatentes();
    }

    // ── Abas ──────────────────────────────────────────────────────────────

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

    // ── Filtros ───────────────────────────────────────────────────────────

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

    // ── Botão novo ────────────────────────────────────────────────────────

    _configurarBotaoNovo() {
        const btn = document.getElementById('btnNovoCombatente');
        if (btn) btn.addEventListener('click', () => this._abrirModal('seletorTipo'));
    }

    // ── Formulários de cadastro ───────────────────────────────────────────

    _configurarFormCadastro(formId, tipo, modalId) {
        const form = document.getElementById(formId);
        if (!form) { console.error('Form nao encontrado: ' + formId); return; }

        const textos = {
            jogador: 'Cadastrar Jogador',
            monstro: 'Cadastrar Monstro',
            npc:     'Cadastrar NPC'
        };

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';
            try {
                const c = await this.service.criar(new FormData(form));
                Toast.success(c.nome + ' cadastrado com sucesso!');
                this._fecharModal(modalId);
                this._limparForm(form, tipo);
                this.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao cadastrar');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = textos[tipo];
            }
        });
    }

    // ── Formulário de edição ──────────────────────────────────────────────

    _configurarFormEdicao() {
        const form = document.getElementById('formEdicaoDashboard');
        if (!form) { console.error('Form de edicao nao encontrado'); return; }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled    = true;
            btn.textContent = 'Salvando...';
            try {
                const id = parseInt(document.getElementById('dashEditId').value);
                await this.service.atualizar(id, new FormData(form));

                await Promise.all([
                    this._salvarAtaquesEdicao(id),
                    this._salvarMagiasEdicao(id)
                ]);

                // ✅ Toast sem quebra de linha — string simples
                Toast.success('Combatente atualizado com sucesso!');
                this._fecharModal('modalEdicaoDashboard');
                this.combatenteEmEdicao = null;
                this.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao atualizar');
                console.error(err);
            } finally {
                btn.disabled    = false;
                btn.textContent = 'Salvar Alteracoes';
            }
        });
    }

    // ── Upload (cadastro) ─────────────────────────────────────────────────

    _configurarUpload(sufixo) {
        const input = document.getElementById('inputFoto' + sufixo);
        if (!input) return;
        input.addEventListener('change', () =>
            this._previewImagem(
                input,
                'uploadPreview'     + sufixo,
                'previewImage'      + sufixo,
                'uploadPlaceholder' + sufixo
            )
        );
    }

    // ── Upload (edição) ───────────────────────────────────────────────────

    _configurarUploadEdicao() {
        const area  = document.getElementById('dashEditUploadArea');
        const input = document.getElementById('dashEditFoto');
        if (!area || !input) return;
        area.addEventListener('click', () => input.click());
        input.addEventListener('change', () =>
            this._previewImagem(
                input,
                'dashEditUploadPreview',
                'dashEditPreviewImage',
                'dashEditUploadPlaceholder'
            )
        );
    }

    // ── Carrega combatentes ───────────────────────────────────────────────

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

    // ── Renderiza tabela ──────────────────────────────────────────────────

    _renderizarTabela(combatentes) {
        const tbody = document.getElementById('tabelaCombatentes');
        if (!combatentes.length) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:2rem;color:#64748b">Nenhum combatente cadastrado.</td></tr>';
            return;
        }
        tbody.innerHTML = combatentes.map(function(c) {
            return '<tr>' +
                '<td><span class="badge badge-' + c.tipo + '">' + c.tipo + '</span></td>' +
                '<td>' + c.nome + '</td>' +
                '<td>' + (c.classe || '-') + '</td>' +
                '<td>' + (c.nivel || 1) + '</td>' +
                '<td>' + c.hp_maximo + '</td>' +
                '<td>' + c.iniciativa + '</td>' +
                '<td>' +
                    '<button class="btn-acao" data-id="' + c.id + '" data-acao="editar" title="Editar">✏️</button>' +
                    '<button class="btn-acao" data-id="' + c.id + '" data-acao="excluir" title="Excluir">🗑️</button>' +
                '</td>' +
                '</tr>';
        }).join('');

        tbody.querySelectorAll('[data-acao="editar"]').forEach((btn) => {
            btn.addEventListener('click', () => this._abrirEdicao(parseInt(btn.dataset.id)));
        });
        tbody.querySelectorAll('[data-acao="excluir"]').forEach((btn) => {
            btn.addEventListener('click', () => this._excluirCombatente(parseInt(btn.dataset.id)));
        });
    }

    // ── Resumo ────────────────────────────────────────────────────────────

    _atualizarResumo(combatentes) {
        document.getElementById('totalGeral').textContent     = combatentes.length;
        document.getElementById('totalJogadores').textContent = combatentes.filter(function(c) { return c.tipo === 'jogador'; }).length;
        document.getElementById('totalMonstros').textContent  = combatentes.filter(function(c) { return c.tipo === 'monstro'; }).length;
        document.getElementById('totalNPCs').textContent      = combatentes.filter(function(c) { return c.tipo === 'npc'; }).length;
    }

    // ── Edição ────────────────────────────────────────────────────────────

    async _abrirEdicao(id) {
        try {
            const c = await this.service.obterPorId(id);
            this.combatenteEmEdicao = c;

            document.getElementById('dashEditId').value         = c.id;
            document.getElementById('dashEditTipo').value       = c.tipo;
            document.getElementById('dashEditNome').value       = c.nome;
            document.getElementById('dashEditHP').value         = c.hp_maximo;
            document.getElementById('dashEditIniciativa').value = c.iniciativa;
            document.getElementById('dashEditClasse').value     = c.classe       || '';
            document.getElementById('dashEditNivel').value      = c.nivel        || 1;
            document.getElementById('dashEditPontos').value     = c.pontos       || 0;

            // ✅ Sem ?? — usa operador ternário para compatibilidade total
            document.getElementById('dashEditCA').value         = c.ca        !== null && c.ca        !== undefined ? c.ca        : 10;
            document.getElementById('dashEditToque').value      = c.toque     !== null && c.toque     !== undefined ? c.toque     : 10;
            document.getElementById('dashEditSurpresa').value   = c.surpresa  !== null && c.surpresa  !== undefined ? c.surpresa  : 10;
            document.getElementById('dashEditFortitude').value  = c.fortitude !== null && c.fortitude !== undefined ? c.fortitude : 0;
            document.getElementById('dashEditReflexos').value   = c.reflexos  !== null && c.reflexos  !== undefined ? c.reflexos  : 0;
            document.getElementById('dashEditVontade').value    = c.vontade   !== null && c.vontade   !== undefined ? c.vontade   : 0;

            document.getElementById('dashEditFOR').value = c.forca        || 10;
            document.getElementById('dashEditDES').value = c.destreza     || 10;
            document.getElementById('dashEditCON').value = c.constituicao || 10;
            document.getElementById('dashEditINT').value = c.inteligencia || 10;
            document.getElementById('dashEditSAB').value = c.sabedoria    || 10;
            document.getElementById('dashEditCAR').value = c.carisma      || 10;

            ['dashEditFOR','dashEditDES','dashEditCON',
             'dashEditINT','dashEditSAB','dashEditCAR'].forEach((fid) => {
                const el = document.getElementById(fid);
                if (el) this._calcularModificador(el);
            });

            const placeholder = document.getElementById('dashEditUploadPlaceholder');
            const preview     = document.getElementById('dashEditUploadPreview');
            const img         = document.getElementById('dashEditPreviewImage');
            if (c.foto_url) {
                img.src                   = c.foto_url;
                placeholder.style.display = 'none';
                preview.style.display     = 'block';
            } else {
                placeholder.style.display = 'flex';
                preview.style.display     = 'none';
            }

            const secAtaques = document.getElementById('secaoAtaquesEdicao');
            const secMagias  = document.getElementById('secaoMagiasEdicao');
            const isJogador  = c.tipo === 'jogador';

            if (secAtaques) secAtaques.style.display = isJogador ? 'block' : 'none';
            if (secMagias)  secMagias.style.display  = isJogador ? 'block' : 'none';

            if (isJogador) {
                this._renderizarAtaquesEdicao(c.ataques      || []);
                this._renderizarMagiasEdicao (c.magias_slots || []);
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
            Toast.success('Combatente excluido!');
            this.carregarCombatentes();
        } catch (err) {
            Toast.error('Erro ao excluir');
            console.error(err);
        }
    }

    async _deletarCombatente() {
        if (!this.combatenteEmEdicao) return;
        if (!confirm('Deletar ' + this.combatenteEmEdicao.nome + '? Esta acao nao pode ser desfeita.')) return;
        try {
            await this.service.deletar(this.combatenteEmEdicao.id);
            Toast.success('Combatente deletado!');
            this._fecharModal('modalEdicaoDashboard');
            this.combatenteEmEdicao = null;
            this.carregarCombatentes();
        } catch (err) {
            Toast.error('Erro ao deletar');
            console.error(err);
        }
    }

    // ── Ataques ───────────────────────────────────────────────────────────

    _renderizarAtaquesEdicao(ataques) {
        const lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;
        lista.innerHTML = '';
        if (!ataques.length) { this._adicionarLinhaAtaque(); return; }
        ataques.forEach((a) => this._adicionarLinhaAtaque(a));
    }

    _adicionarLinhaAtaque(ataque) {
        const lista = document.getElementById('listaAtaquesEdicao');
        if (!lista) return;
        const div     = document.createElement('div');
        div.className = 'ataque-linha';
        div.innerHTML =
            '<input type="text"  class="ataque-nome"  placeholder="Nome do ataque" value="' + (ataque && ataque.nome         ? ataque.nome         : '') + '" />' +
            '<input type="text"  class="ataque-bonus" placeholder="+0"             value="' + (ataque && ataque.bonus_ataque ? ataque.bonus_ataque : '+0') + '" style="width:70px" />' +
            '<input type="text"  class="ataque-dano"  placeholder="1d6"            value="' + (ataque && ataque.dano         ? ataque.dano         : '') + '" style="width:90px" />' +
            '<input type="text"  class="ataque-tipo"  placeholder="ex: cortante"   value="' + (ataque && ataque.tipo_dano   ? ataque.tipo_dano   : '') + '" style="width:120px" />' +
            '<button type="button" class="btn-dash-delete" style="padding:.3rem .6rem;font-size:.8rem" onclick="removerLinhaAtaque(this)">x</button>';
        lista.appendChild(div);
    }

    _coletarAtaquesEdicao() {
        return Array.from(document.querySelectorAll('#listaAtaquesEdicao .ataque-linha'))
            .map(function(l) {
                return {
                    nome:         l.querySelector('.ataque-nome').value.trim(),
                    bonus_ataque: l.querySelector('.ataque-bonus').value.trim() || '+0',
                    dano:         l.querySelector('.ataque-dano').value.trim()  || '1d6',
                    tipo_dano:    l.querySelector('.ataque-tipo').value.trim()
                };
            })
            .filter(function(a) { return a.nome; });
    }

    async _salvarAtaquesEdicao(combatenteId) {
        await this.ataqueService.salvarAtaques(combatenteId, this._coletarAtaquesEdicao());
    }

    // ── Magias ────────────────────────────────────────────────────────────

    _renderizarMagiasEdicao(slots) {
        const container = document.getElementById('gridMagiasEdicao');
        if (!container) return;
        var html = '';
        for (var nivel = 0; nivel <= 9; nivel++) {
            var slot  = slots.find(function(s) { return s.nivel === nivel; });
            var total = slot && slot.total !== undefined ? slot.total : 0;
            html +=
                '<div class="magia-edicao-linha">' +
                    '<span class="magia-nivel-label">Nivel ' + nivel + '</span>' +
                    '<div style="flex:1">' +
                        '<input type="number"' +
                               ' class="magia-total-input"' +
                               ' data-nivel="' + nivel + '"' +
                               ' value="' + total + '"' +
                               ' min="0" max="20"' +
                               ' placeholder="Total de slots"' +
                               ' style="width:100%;padding:.4rem .6rem;border-radius:.35rem;' +
                                       'border:1px solid #334155;background:#0f0f23;' +
                                       'color:#e2e8f0;font-size:.85rem;box-sizing:border-box" />' +
                    '</div>' +
                '</div>';
        }
        container.innerHTML = html;
    }

    _coletarMagiasEdicao() {
        return Array.from(document.querySelectorAll('#gridMagiasEdicao .magia-total-input'))
            .map(function(input) {
                return {
                    nivel:  parseInt(input.dataset.nivel),
                    total:  parseInt(input.value) || 0,
                    usados: 0
                };
            });
    }

    async _salvarMagiasEdicao(combatenteId) {
        await this.ataqueService.salvarMagias(combatenteId, this._coletarMagiasEdicao());
    }

    // ── Helpers de modal ──────────────────────────────────────────────────

    _abrirModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('show');
        else    console.error('Modal nao encontrado: ' + id);
    }

    _fecharModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('show');
    }

    // ── Helpers de upload ─────────────────────────────────────────────────

    _previewImagem(input, previewId, imgId, placeholderId) {
        const file = input.files ? input.files[0] : null;
        if (!file) return;
        const reader  = new FileReader();
        reader.onload = function(e) {
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
        const inputId       = isEdit ? 'dashEditFoto'              : 'inputFoto'        + sufixo;
        const placeholderId = isEdit ? 'dashEditUploadPlaceholder' : 'uploadPlaceholder' + sufixo;
        const previewId     = isEdit ? 'dashEditUploadPreview'     : 'uploadPreview'    + sufixo;
        const input       = document.getElementById(inputId);
        const placeholder = document.getElementById(placeholderId);
        const preview     = document.getElementById(previewId);
        if (input)       input.value             = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview)     preview.style.display     = 'none';
    }

    // ── Helpers D&D ───────────────────────────────────────────────────────

    _calcularModificador(input) {
        const valor = parseInt(input.value) || 10;
        const mod   = Math.floor((valor - 10) / 2);
        const modId = 'mod' + input.id.charAt(0).toUpperCase() + input.id.slice(1);
        const span  = document.getElementById(modId);
        if (span) span.textContent = mod >= 0 ? '+' + mod : '' + mod;
    }

    _limparForm(form, tipo) {
        form.reset();
        const sufixos = { jogador: '', monstro: 'Monstro', npc: 'NPC' };
        const sufixo  = sufixos[tipo] || '';
        const ph = document.getElementById('uploadPlaceholder' + sufixo);
        const pv = document.getElementById('uploadPreview'     + sufixo);
        if (ph) ph.style.display = 'flex';
        if (pv) pv.style.display = 'none';
    }
}

// ── CombatenteServiceGlobal ───────────────────────────────────────────────────

class CombatenteServiceGlobal {
    _url(path) { return window.getApiUrl('/combatentes' + (path || '')); }
    _headers() {
        const h = {};
        if (typeof AuthService !== 'undefined') {
            const t = AuthService.getToken();
            if (t) h['Authorization'] = 'Bearer ' + t;
        }
        return h;
    }
    async listar(tipo) {
        const url = tipo ? this._url() + '?tipo=' + tipo : this._url();
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao carregar combatentes');
        return res.json();
    }
    async obterPorId(id) {
        const res = await fetch(this._url('/' + id), { headers: this._headers() });
        if (!res.ok) throw new Error('Combatente nao encontrado');
        return res.json();
    }
    async criar(formData) {
        const res = await fetch(this._url(), { method: 'POST', headers: this._headers(), body: formData });
        if (!res.ok) { const e = await res.json().catch(function() { return {}; }); throw new Error(e.detail || 'Erro ao criar'); }
        return res.json();
    }
    async atualizar(id, formData) {
        const res = await fetch(this._url('/' + id), { method: 'PUT', headers: this._headers(), body: formData });
        if (!res.ok) { const e = await res.json().catch(function() { return {}; }); throw new Error(e.detail || 'Erro ao atualizar'); }
        return res.json();
    }
    async deletar(id) {
        const res = await fetch(this._url('/' + id), { method: 'DELETE', headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao deletar');
        return true;
    }
}

// ── UploadServiceGlobal ───────────────────────────────────────────────────────

class UploadServiceGlobal {
    criarPreview(file, callback) {
        if (!file.type.startsWith('image/')) throw new Error('Arquivo deve ser uma imagem');
        const reader  = new FileReader();
        reader.onload = function(e) { callback(e.target.result); };
        reader.readAsDataURL(file);
    }
}

new DashboardController();