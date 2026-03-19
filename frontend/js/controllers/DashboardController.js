/**
 * DashboardController.js
 * SOLID: SRP - gerencia apenas dashboard de combatentes
 * Dependências globais: AuthService, Toast, ModalConfirm, AtaqueService
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
        this.filtroAtual        = 'todos';
        this.combatenteEmEdicao = null;
        this.perfil             = AuthService.getPerfil();

        this._registrarGlobais();
        this._inicializar();
        console.log('✅ DashboardController inicializado');
    }

    _isMestre() {
        return this.perfil === 'mestre' || this.perfil === 'administrador';
    }

    _registrarGlobais() {
        const self = this;
        
        window.fecharModalCadastro        = () => self._fecharModal('modalCadastroJogador');
        window.fecharModalCadastroMonstro = () => self._fecharModal('modalCadastroMonstro');
        window.fecharModalCadastroNPC     = () => self._fecharModal('modalCadastroNPC');
        window.fecharSeletorTipo          = () => self._fecharModal('seletorTipo');
        window.fecharModalEdicao          = () => self._fecharModal('modalEdicaoDashboard');

        window.abrirModalCadastro = (tipo) => {
            if (!self._isMestre() && (tipo === 'monstro' || tipo === 'npc')) {
                Toast.error('Acesso restrito: apenas Mestre pode cadastrar monstros e NPCs.');
                return;
            }
            self._fecharModal('seletorTipo');
            const mapa = { jogador: 'modalCadastroJogador', monstro: 'modalCadastroMonstro', npc: 'modalCadastroNPC' };
            self._abrirModal(mapa[tipo]);
        };

        window.confirmarDelecao     = () => self._deletarCombatente();
        window.atualizarModificador = (input) => self._calcularModificador(input);
        window.previewImagemUpload  = (input, previewId, imgId, placeholderId) => self._previewImagem(input, previewId, imgId, placeholderId);
        window.removerImagem        = () => self._removerImagem('', false);
        window.removerImagemMonstro = () => self._removerImagem('Monstro', false);
        window.removerImagemNPC     = () => self._removerImagem('NPC', false);
        window.removerImagemEdicao  = () => self._removerImagem('', true);
        window.adicionarLinhaAtaque = () => self._adicionarLinhaAtaque();
        window.removerLinhaAtaque   = (btn) => btn.closest('.ataque-linha').remove();
        window.abrirPaginaPericias  = () => self._abrirPaginaPericias();
    }

    _inicializar() {
        this._aplicarRestricoesPerfil();
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarFormCadastro('formCadastroJogador', 'jogador', 'modalCadastroJogador');
        this._configurarFormCadastro('formCadastroMonstro', 'monstro', 'modalCadastroMonstro');
        this._configurarFormCadastro('formCadastroNPC', 'npc', 'modalCadastroNPC');
        this._configurarFormEdicao();
        this._configurarUpload('');
        this._configurarUpload('Monstro');
        this._configurarUpload('NPC');
        this._configurarUploadEdicao();
        this.carregarCombatentes();
    }

    _aplicarRestricoesPerfil() {
        if (this._isMestre()) return;

        const elementos = [
            { query: '.nav-tab[data-tab="arena"]', id: null },
            { query: '.filter-btn[data-tipo="monstro"]', id: null },
            { query: '.filter-btn[data-tipo="npc"]', id: null },
            { id: 'btnNovoCombatente', query: null },
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
                if (!self._isMestre() && (btn.dataset.tipo === 'monstro' || btn.dataset.tipo === 'npc')) return;
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                self.filtroAtual = btn.dataset.tipo;
                self.carregarCombatentes();
            });
        });
    }

    _configurarBotaoNovo() {
        const btn = document.getElementById('btnNovoCombatente');
        if (btn) btn.addEventListener('click', () => this._abrirModal('seletorTipo'));
    }

    _configurarFormCadastro(formId, tipo, modalId) {
        const self = this;
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled = true;
            btn.textContent = 'Salvando...';
            
            try {
                const c = await self.service.criar(new FormData(form));
                Toast.success(`${c.nome} cadastrado com sucesso!`);
                self._fecharModal(modalId);
                self._limparForm(form, tipo);
                self.carregarCombatentes();
            } catch (err) {
                Toast.error(err.message || 'Erro ao cadastrar');
                console.error(err);
            } finally {
                btn.disabled = false;
                btn.textContent = `✅ Cadastrar ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`;
            }
        });
    }

    _configurarFormEdicao() {
        const self = this;
        const form = document.getElementById('formEdicaoDashboard');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('[type="submit"]');
            btn.disabled = true;
            btn.textContent = 'Salvando...';
            
            try {
                const id = parseInt(document.getElementById('dashEditId').value);
                await self.service.atualizar(id, new FormData(form));
                await self._salvarAtaquesEdicao(id);
                await self._salvarPericiasEdicao(id);
                
                self._fecharModal('modalEdicaoDashboard');
                self.combatenteEmEdicao = null;
                self.carregarCombatentes();
                Toast.success('Alterações salvas com sucesso!');
            } catch (err) {
                Toast.error(err.message || 'Erro ao salvar alterações');
                console.error(err);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Salvar Alterações';
            }
        });
    }

    _configurarUpload(sufixo) {
        const self = this;
        const input = document.getElementById('inputFoto' + sufixo);
        if (!input) return;
        
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
            if (!this._isMestre() && (tipo === 'monstro' || tipo === 'npc')) tipo = 'jogador';
            if (!this._isMestre() && tipo === null) tipo = 'jogador';

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
                <td><span class="badge badge-${c.tipo}">${c.tipo}</span></td>
                <td>${c.nome}</td>
                <td>${c.classe || '-'}</td>
                <td>${c.nivel || 1}</td>
                <td style="${this._isMestre() ? '' : 'display:none'}">
                    <span class="${podeVerStats ? '' : 'stat-oculto'}">${hpTexto}</span>
                </td>
                <td style="${this._isMestre() ? '' : 'display:none'}">
                    <span class="${podeVerStats ? '' : 'stat-oculto'}">${iniTexto}</span>
                </td>
                <td>
                    <div class="tabela-acoes">
                        <button class="btn-acao btn-ver-ficha" data-id="${c.id}" title="Ver ficha" onclick="window.open('/pages/ficha-personagem.html?id=${c.id}', '_blank')">👁️</button>
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

        if (this._isMestre()) {
            tbody.querySelectorAll('.btn-excluir').forEach(btn => {
                btn.addEventListener('click', () => {
                    const id = parseInt(btn.dataset.id);
                    self._excluirCombatente(id);
                });
            });
        }

        console.log(`📋 Renderizando tabela com ${combatentes.length} combatente(s)...`);
    }

    _atualizarResumo(combatentes) {
        const totalEl = document.getElementById('totalGeral');
        const jogEl = document.getElementById('totalJogadores');
        const monEl = document.getElementById('totalMonstros');
        const npcEl = document.getElementById('totalNPCs');
        
        if (totalEl) totalEl.textContent = combatentes.length;
        if (jogEl) jogEl.textContent = combatentes.filter(c => c.tipo === 'jogador').length;
        if (monEl) monEl.textContent = combatentes.filter(c => c.tipo === 'monstro').length;
        if (npcEl) npcEl.textContent = combatentes.filter(c => c.tipo === 'npc').length;
    }

    async _abrirEdicao(id) {
        try {
            const c = await this.service.obterPorId(id);

            if (!this._isMestre() && (c.tipo === 'monstro' || c.tipo === 'npc')) {
                Toast.error('Acesso restrito: você não pode editar monstros ou NPCs.');
                return;
            }

            this.combatenteEmEdicao = c;
            window.combatenteEmEdicao = c;

            // Preencher campos
            document.getElementById('dashEditId').value = c.id;
            document.getElementById('dashEditTipo').value = c.tipo;
            document.getElementById('dashEditNome').value = c.nome;
            document.getElementById('dashEditHP').value = c.hp_maximo;
            document.getElementById('dashEditIniciativa').value = c.iniciativa;
            document.getElementById('dashEditClasse').value = c.classe || '';
            document.getElementById('dashEditRaca').value = c.raca || '';
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
            if (secPagRef) secPagRef.style.display = c.tipo === 'monstro' ? 'block' : 'none';
            if (inputPagRef) inputPagRef.value = c.tipo === 'monstro' ? (c.pagina_referencia || '') : '';

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
                secAtaques.style.display = c.tipo === 'jogador' ? 'block' : 'none';
                if (c.tipo === 'jogador') this._renderizarAtaquesEdicao(c.ataques || []);
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
        
        const div = document.createElement('div');
        div.className = 'ataque-linha';
        div.innerHTML = `
            <input type="text" class="ataque-nome" placeholder="Nome" value="${ataque?.nome || ''}" />
            <input type="text" class="ataque-bonus" placeholder="+0" value="${ataque?.bonus_ataque || '+0'}" style="width:70px" />
            <input type="text" class="ataque-dano" placeholder="1d6" value="${ataque?.dano || ''}" style="width:90px" />
            <input type="text" class="ataque-tipo" placeholder="tipo" value="${ataque?.tipo_dano || ''}" style="width:120px" />
            <button type="button" class="btn-dash-delete" onclick="removerLinhaAtaque(this)">✕</button>
        `;
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
        if (window.combatenteEmEdicao?.pericias) {
            try {
                sessionStorage.setItem('periciasEdit', JSON.stringify(window.combatenteEmEdicao.pericias));
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
                pericias: JSON.stringify(window.combatenteEmEdicao?.pericias || [])
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
        return window.getApiUrl('/v1/combatentes' + (path || '')); 
    }

    _headers() {
        const h = {};
        if (typeof AuthService !== 'undefined') {
            const t = AuthService.getToken();
            if (t) h['Authorization'] = `Bearer ${t}`;
        }
        return h;
    }

    async listar(tipo) {
        const url = tipo ? `${this._url()}?tipo=${tipo}` : this._url();
        const res = await fetch(url, { headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao carregar combatentes');
        return res.json();
    }

    async obterPorId(id) {
        const res = await fetch(this._url(`/${id}`), { headers: this._headers() });
        if (!res.ok) throw new Error('Combatente não encontrado');
        return res.json();
    }

    async criar(formData) {
        const res = await fetch(this._url(), { method: 'POST', headers: this._headers(), body: formData });
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || 'Erro ao criar');
        }
        return res.json();
    }

    async atualizar(id, formData) {
        const res = await fetch(this._url(`/${id}`), { method: 'PUT', headers: this._headers(), body: formData });
        if (!res.ok) {
            const e = await res.json().catch(() => ({}));
            throw new Error(e.detail || 'Erro ao atualizar');
        }
        return res.json();
    }

    async deletar(id) {
        const res = await fetch(this._url(`/${id}`), { method: 'DELETE', headers: this._headers() });
        if (!res.ok) throw new Error('Erro ao deletar');
        return true;
    }
}

// Inicializar após DOM pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new DashboardController();
    });
} else {
    new DashboardController();
}