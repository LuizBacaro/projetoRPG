/**
 * UsuarioController
 * SRP: orquestra a tela de gerenciamento de usuários
 * Carregado via <script> dinâmico — usa window.ModalConfirm
 */
class UsuarioController {

    constructor() {
        this.service  = new UsuarioService();
        this.modal    = new ModalUsuario(this.service, () => this.carregar());
        this.usuarios = [];
        this.totalApi = 0;
        this.filtros  = {
            busca: '',
            perfil: 'todos',
            status: 'todos',
        };
        this._bindBotoes();
        this._bindTabelaAcoes();
        this._aplicarBuscaDaUrl();
        this.carregar();
    }

    _aplicarBuscaDaUrl() {
        try {
            const params = new URLSearchParams(window.location.search || '');
            const q = (params.get('q') || params.get('email') || params.get('busca') || '').trim();
            if (!q) return;
            this.filtros.busca = q.toLowerCase();
            const input = document.getElementById('filtroBuscaUsuarios');
            if (input) input.value = q;
            this.filtros.perfil = 'todos';
            this.filtros.status = 'todos';
            const selPerfil = document.getElementById('filtroPerfilUsuarios');
            const selStatus = document.getElementById('filtroStatusUsuarios');
            if (selPerfil) selPerfil.value = 'todos';
            if (selStatus) selStatus.value = 'todos';
        } catch (_) {
            /* ignore */
        }
    }

    _limparFiltros() {
        this.filtros = { busca: '', perfil: 'todos', status: 'todos' };
        const input = document.getElementById('filtroBuscaUsuarios');
        const selPerfil = document.getElementById('filtroPerfilUsuarios');
        const selStatus = document.getElementById('filtroStatusUsuarios');
        if (input) input.value = '';
        if (selPerfil) selPerfil.value = 'todos';
        if (selStatus) selStatus.value = 'todos';
        this._atualizarPainel();
    }

    _bindBotoes() {
        document.getElementById('btnNovoUsuario')
            ?.addEventListener('click', () => this.modal.abrirParaCriar());

        document.getElementById('btnLimparFiltrosUsuarios')
            ?.addEventListener('click', () => this._limparFiltros());

        document.getElementById('filtroBuscaUsuarios')
            ?.addEventListener('input', (event) => {
                this.filtros.busca = event.target.value.trim().toLowerCase();
                this._atualizarPainel();
            });

        document.getElementById('filtroPerfilUsuarios')
            ?.addEventListener('change', (event) => {
                this.filtros.perfil = event.target.value;
                this._atualizarPainel();
            });

        document.getElementById('filtroStatusUsuarios')
            ?.addEventListener('change', (event) => {
                this.filtros.status = event.target.value;
                this._atualizarPainel();
            });
    }

    _bindTabelaAcoes() {
        document.getElementById('tabelaUsuarios')
            ?.addEventListener('click', (event) => {
                const button = event.target.closest('[data-action][data-id]');
                if (!button) return;

                const id = Number(button.dataset.id);
                const action = button.dataset.action;

                if (action === 'editar') {
                    this.editar(id);
                    return;
                }

                if (action === 'inativar') {
                    this.inativar(id);
                    return;
                }

                if (action === 'reativar') {
                    this.reativar(id);
                    return;
                }

                if (action === 'excluir') {
                    this.excluir(id);
                }
            });
    }

    _normalizarPerfil(perfil) {
        return String(perfil || '').trim().toLowerCase();
    }

    async carregar() {
        try {
            const res = await this.service.listar(false);
            this.usuarios = (res.usuarios || []).map((u) => ({
                ...u,
                perfil: this._normalizarPerfil(u.perfil),
            }));
            this.totalApi = Number.isFinite(Number(res.total))
                ? Number(res.total)
                : this.usuarios.length;
            this._atualizarPainel();
            if (this.filtros.busca) {
                this._rolarAtePrimeiroFiltrado();
            }
        } catch (err) {
            console.error('Erro ao carregar usuários:', err);
            this._renderizarErro();
        }
    }

    _rolarAtePrimeiroFiltrado() {
        const row = document.querySelector('#tabelaUsuarios tr[data-usuario-id]');
        if (row && typeof row.scrollIntoView === 'function') {
            row.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    _atualizarPainel() {
        this._atualizarResumo();
        this._renderizarTabela();
    }

    _usuariosFiltrados() {
        return this.usuarios.filter((usuario) => {
            const perfil = this._normalizarPerfil(usuario.perfil);
            const matchPerfil = this.filtros.perfil === 'todos'
                || perfil === this.filtros.perfil;

            const matchStatus = this.filtros.status === 'todos'
                || (this.filtros.status === 'ativo' ? !!usuario.ativo : !usuario.ativo);

            const termo = this.filtros.busca;
            const matchBusca = !termo || [
                usuario.nome,
                usuario.email,
                usuario.usuario_responsavel,
                String(usuario.id),
            ]
                .filter(Boolean)
                .some((valor) => String(valor).toLowerCase().includes(termo));

            return matchPerfil && matchStatus && matchBusca;
        });
    }

    _atualizarResumo() {
        const carregados = this.usuarios.length;
        const total = Math.max(this.totalApi || 0, carregados);
        const ativos = this.usuarios.filter((usuario) => usuario.ativo).length;
        const governanca = this.usuarios.filter((usuario) =>
            ['administrador', 'mestre'].includes(this._normalizarPerfil(usuario.perfil))
        ).length;
        const inativos = carregados - ativos;
        const filtrados = this._usuariosFiltrados().length;

        this._definirTexto('statTotalUsuarios', total);
        this._definirTexto('statUsuariosAtivos', ativos);
        this._definirTexto('statUsuariosGovernanca', governanca);
        this._definirTexto('statUsuariosInativos', inativos);

        const resumo = document.getElementById('resumoFiltrado');
        if (!resumo) return;

        let texto = filtrados === carregados
            ? `${carregados} usuário(s) na lista global (Excluir/Inativar aqui).`
            : `${filtrados} de ${carregados} usuário(s) visíveis com os filtros atuais.`;
        if (this.totalApi > carregados) {
            texto += ` Atenção: API reportou total ${this.totalApi}, mas só ${carregados} foram carregados.`;
        }
        resumo.textContent = texto;
    }

    _renderizarTabela() {
        const tbody = document.getElementById('tabelaUsuarios');
        if (!tbody) return;

        const usuarios = this._usuariosFiltrados();

        if (this.usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="usuarios-loading">
                        Nenhum usuário cadastrado. Clique em "+ Novo Usuário" para começar.
                    </td>
                </tr>`;
            return;
        }

        if (usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="usuarios-loading">
                        Nenhum registro corresponde aos filtros atuais.
                        Use <strong>Limpar filtros</strong> para ver todos os ${this.usuarios.length} usuário(s).
                    </td>
                </tr>`;
            return;
        }

        tbody.innerHTML = usuarios.map(u => `
            <tr class="${u.ativo ? '' : 'usuario-inativo'}" data-usuario-id="${u.id}" data-usuario-email="${this._escapar(u.email)}">
                <td>${this._badgePerfil(u.perfil)}</td>
                <td>
                    <div class="usuarios-coluna-nome">
                        <strong>${this._escapar(u.nome)}</strong>
                        <small>ID ${u.id}</small>
                    </div>
                </td>
                <td><span class="usuarios-coluna-meta">${this._escapar(u.email)}</span></td>
                <td>${this._badgeStatus(u.ativo)}</td>
                <td><span class="usuarios-coluna-meta">${u.usuario_responsavel ? this._escapar(u.usuario_responsavel) : '—'}</span></td>
                <td><span class="usuarios-coluna-meta">${this._formatarData(u.data_acao)}</span></td>
                <td>
                    <div class="usuarios-acoes">
                        <button class="btn-acao btn-acao-editar" data-action="editar" data-id="${u.id}" title="Editar usuário">
                            <span>✏️</span><span>Editar</span>
                        </button>
                        ${u.ativo
                            ? `<button class="btn-acao btn-acao-inativar" data-action="inativar" data-id="${u.id}" title="Inativar usuário"><span>🚫</span><span>Inativar</span></button>`
                            : `<button class="btn-acao btn-acao-reativar" data-action="reativar" data-id="${u.id}" title="Reativar usuário"><span>✅</span><span>Reativar</span></button>`
                        }
                        <button class="btn-acao btn-acao-excluir" data-action="excluir" data-id="${u.id}" title="Excluir usuário definitivamente">
                            <span>🗑️</span><span>Excluir</span>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    _renderizarErro() {
        const tbody = document.getElementById('tabelaUsuarios');
        if (!tbody) return;
        this._definirTexto('resumoFiltrado', 'Falha ao carregar registros.');
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="usuarios-loading">
                    ⚠️ Erro ao carregar usuários. Verifique o servidor.
                </td>
            </tr>`;
    }

    _badgePerfil(perfil) {
        const p = this._normalizarPerfil(perfil);
        const map = {
            administrador: '<span class="badge badge-admin">Administrador</span>',
            mestre:        '<span class="badge badge-mestre">Mestre</span>',
            jogador:       '<span class="badge badge-jogador">Jogador</span>',
        };
        return map[p] ?? `<span class="badge">${this._escapar(perfil)}</span>`;
    }

    _badgeStatus(ativo) {
        return ativo
            ? '<span class="badge badge-ativo">Ativo</span>'
            : '<span class="badge badge-inativo">Inativo</span>';
    }

    _escapar(str = '') {
        return String(str)
            .replace(/&/g,  '&amp;')
            .replace(/</g,  '&lt;')
            .replace(/>/g,  '&gt;')
            .replace(/"/g,  '&quot;')
            .replace(/'/g, '&#039;');
    }

    _formatarData(data) {
        if (!data) return '—';

        const date = new Date(data);
        if (Number.isNaN(date.getTime())) return '—';

        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
        }).format(date);
    }

    _definirTexto(id, valor) {
        const element = document.getElementById(id);
        if (element) element.textContent = String(valor);
    }

    async editar(id) {
        try {
            const usuario = await this.service.buscarPorId(id);
            this.modal.abrirParaEditar(usuario);
        } catch (err) {
            Toast.error('Erro ao carregar usuário: ' + err.message);
        }
    }

    inativar(id) {
        ModalConfirm.mostrar({
            icone:           '🚫',
            titulo:          'Inativar Usuário',
            texto:           'Deseja inativar este usuário? O acesso será bloqueado.',
            textoConfirmar:  '🚫 Inativar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar:     () => this._executarInativar(id),
        });
    }

    async _executarInativar(id) {
        try {
            await this.service.inativar(id);
            await this.carregar();
        } catch (err) {
            Toast.error('Erro ao inativar: ' + err.message);
        }
    }

    reativar(id) {
        ModalConfirm.mostrar({
            icone:          '✅',
            titulo:         'Reativar Usuário',
            texto:          'Deseja reativar este usuário? O acesso será restaurado.',
            textoConfirmar: '✅ Reativar',
            onConfirmar:    () => this._executarReativar(id),
        });
    }

    async _executarReativar(id) {
        try {
            await this.service.atualizar(id, { ativo: true });
            await this.carregar();
        } catch (err) {
            Toast.error('Erro ao reativar: ' + err.message);
        }
    }

    excluir(id) {
        const u = this.usuarios.find((x) => Number(x.id) === Number(id));
        const rotulo = u ? `${u.nome} (${u.email})` : `ID ${id}`;
        ModalConfirm.mostrar({
            icone:           '🗑️',
            titulo:          'Excluir Usuário',
            texto:           `Excluir definitivamente ${rotulo}? Esta ação não pode ser desfeita. Se houver campanha/personagem vinculados, a API pode recusar — nesse caso inative ou limpe os vínculos antes.`,
            textoConfirmar:  '🗑️ Excluir',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar:     () => this._executarExcluir(id),
        });
    }

    async _executarExcluir(id) {
        try {
            await this.service.excluir(id);
            Toast.success('Usuário excluído com sucesso.');
            await this.carregar();
        } catch (err) {
            Toast.error('Erro ao excluir: ' + err.message);
        }
    }
}

// ── Instância global ──────────────────────────────────────────────────────────
let usuarioController;
(function init() {
    try {
        usuarioController = new UsuarioController();
        window.usuarioController = usuarioController;
    } catch (error) {
        console.error('❌ Falha no bootstrap do UsuarioController:', error);
        const tbody = document.getElementById('tabelaUsuarios');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align:center; padding:2rem; color:#f87171;">
                        ⚠️ Falha ao iniciar gerenciamento de usuarios. Recarregue a pagina.
                    </td>
                </tr>`;
        }
        if (typeof Toast !== 'undefined' && Toast && typeof Toast.error === 'function') {
            Toast.error('Falha ao iniciar tela de usuarios.');
        }
    }
})();
