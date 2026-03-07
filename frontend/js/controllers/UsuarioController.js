/**
 * UsuarioController
 * SRP: orquestra a tela de gerenciamento de usuários
 * Carregado via <script> dinâmico — depende de UsuarioService e ModalUsuario
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

    // ── Inicialização ─────────────────────────────────────────────────────────

    _bindBotoes() {
        document.getElementById('btnNovoUsuario')
            ?.addEventListener('click', () => this.modal.abrirParaCriar());
    }

    // ── Carregamento ──────────────────────────────────────────────────────────

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

    // ── Renderização ─────────────────────────────────────────────────────────

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

    // ── Helpers de badge ─────────────────────────────────────────────────────

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

    // Evita XSS ao renderizar dados da API no HTML
    _escapar(str = '') {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '<')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // ── Ações ─────────────────────────────────────────────────────────────────

    async editar(id) {
        try {
            const usuario = await this.service.buscarPorId(id);
            this.modal.abrirParaEditar(usuario);
        } catch (err) {
            alert(`Erro ao carregar usuário: ${err.message}`);
        }
    }

    async inativar(id) {
        if (!confirm('Deseja inativar este usuário? O acesso será bloqueado.')) return;
        try {
            await this.service.inativar(id);
            await this.carregar();
        } catch (err) {
            alert(`Erro ao inativar: ${err.message}`);
        }
    }

    async reativar(id) {
        if (!confirm('Deseja reativar este usuário?')) return;
        try {
            await this.service.atualizar(id, { ativo: true });
            await this.carregar();
        } catch (err) {
            alert(`Erro ao reativar: ${err.message}`);
        }
    }
}

// ── Instância global ──────────────────────────────────────────────────────────
let usuarioController;
(function init() {
    usuarioController = new UsuarioController();
})();