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
        this._bindBotoes();
        this.carregar();
        console.log('✅ UsuarioController inicializado');
    }

    _bindBotoes() {
        document.getElementById('btnNovoUsuario')
            ?.addEventListener('click', () => this.modal.abrirParaCriar());
    }

    async carregar() {
        try {
            const res     = await this.service.listar();
            this.usuarios = res.usuarios || [];
            this._renderizarTabela();
        } catch (err) {
            console.error('Erro ao carregar usuários:', err);
            this._renderizarErro();
        }
    }

    _renderizarTabela() {
        const tbody = document.getElementById('tabelaUsuarios');
        if (!tbody) return;

        if (this.usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align:center; padding:2.5rem; color:#64748b;">
                        Nenhum usuário cadastrado. Clique em "+ Novo Usuário" para começar.
                    </td>
                </tr>`;
            return;
        }

        tbody.innerHTML = this.usuarios.map(u => `
            <tr class="${u.ativo ? '' : 'usuario-inativo'}">
                <td>${this._badgePerfil(u.perfil)}</td>
                <td>${this._escapar(u.nome)}</td>
                <td>${this._escapar(u.email)}</td>
                <td>${this._badgeStatus(u.ativo)}</td>
                <td>${u.usuario_responsavel ? this._escapar(u.usuario_responsavel) : '—'}</td>
                <td>${u.data_acao ? new Date(u.data_acao).toLocaleDateString('pt-BR') : '—'}</td>
                <td>
                    <button class="btn-acao" onclick="usuarioController.editar(${u.id})" title="Editar">✏️</button>
                    ${u.ativo
                        ? `<button class="btn-acao" onclick="usuarioController.inativar(${u.id})" title="Inativar">🚫</button>`
                        : `<button class="btn-acao" onclick="usuarioController.reativar(${u.id})" title="Reativar">✅</button>`
                    }
                </td>
            </tr>
        `).join('');
    }

    _renderizarErro() {
        const tbody = document.getElementById('tabelaUsuarios');
        if (!tbody) return;
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center; padding:2rem; color:#f87171;">
                    ⚠️ Erro ao carregar usuários. Verifique o servidor.
                </td>
            </tr>`;
    }

    _badgePerfil(perfil) {
        const map = {
            administrador: '<span class="badge badge-admin">Administrador</span>',
            mestre:        '<span class="badge badge-mestre">Mestre</span>',
            jogador:       '<span class="badge badge-jogador">Jogador</span>',
        };
        return map[perfil] ?? `<span class="badge">${perfil}</span>`;
    }

    _badgeStatus(ativo) {
        return ativo
            ? '<span class="badge badge-ativo">Ativo</span>'
            : '<span class="badge badge-inativo">Inativo</span>';
    }

    _escapar(str = '') {
        return String(str)
            .replace(/&/g,  '&amp;')
            .replace(/</g,  '<')
            .replace(/>/g,  '&gt;')
            .replace(/"/g,  '&quot;');
    }

    async editar(id) {
        try {
            const usuario = await this.service.buscarPorId(id);
            this.modal.abrirParaEditar(usuario);
        } catch (err) {
            Toast.error('Erro ao carregar usuário: ' + err.message);
        }
    }

    // ✅ REFATORADO: usa window.ModalConfirm centralizado
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

    // ✅ REFATORADO: usa window.ModalConfirm centralizado
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
}

// ── Instância global ──────────────────────────────────────────────────────────
let usuarioController;
(function init() {
    try {
        usuarioController = new UsuarioController();
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