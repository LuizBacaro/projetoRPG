/**
 * UsuarioController
 * SRP: orquestra a tela de gerenciamento de usuários
 * Carregado via <script>
 */

class UsuarioController {

    constructor() {
        this.service = new UsuarioService();
        this.modal   = new ModalUsuario(this.service, () => this.carregar());
        this.usuarios = [];
        this.carregar();
        this._bindBotoes();
        console.log('✅ UsuarioController inicializado');
    }

    _bindBotoes() {
        document.getElementById('btnNovoUsuario')
            ?.addEventListener('click', () => this.modal.abrirParaCriar());
    }

    async carregar() {
        try {
            const res = await this.service.listar();
            this.usuarios = res.usuarios || [];
            this._renderizarTabela();
        } catch (err) {
            console.error('Erro ao carregar usuários:', err);
        }
    }

    _renderizarTabela() {
        const tbody = document.getElementById('tabelaUsuarios');
        if (!tbody) return;

        if (this.usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding:2rem; color:#888;">
                        Nenhum usuário cadastrado
                    </td>
                </tr>`;
            return;
        }

        tbody.innerHTML = this.usuarios.map(u => `
            <tr class="${u.ativo ? '' : 'usuario-inativo'}">
                <td>${this._badgePerfil(u.perfil)}</td>
                <td>${u.nome}</td>
                <td>${u.email}</td>
                <td>${this._badgeStatus(u.ativo)}</td>
                <td>${u.usuario_responsavel || '-'}</td>
                <td>${u.data_acao ? new Date(u.data_acao).toLocaleDateString('pt-BR') : '-'}</td>
                <td>
                    <button class="btn-acao btn-editar" onclick="usuarioController.editar(${u.id})" title="Editar">✏️</button>
                    ${u.ativo
                        ? `<button class="btn-acao btn-inativar" onclick="usuarioController.inativar(${u.id})" title="Inativar">🚫</button>`
                        : `<button class="btn-acao btn-reativar" onclick="usuarioController.reativar(${u.id})" title="Reativar">✅</button>`
                    }
                </td>
            </tr>
        `).join('');
    }

    _badgePerfil(perfil) {
        const map = {
            administrador: '<span class="badge badge-admin">Administrador</span>',
            mestre:        '<span class="badge badge-mestre">Mestre</span>',
            jogador:       '<span class="badge badge-jogador">Jogador</span>',
        };
        return map[perfil] || perfil;
    }

    _badgeStatus(ativo) {
        return ativo
            ? '<span class="badge badge-ativo">Ativo</span>'
            : '<span class="badge badge-inativo">Inativo</span>';
    }

    async editar(id) {
        const usuario = await this.service.buscarPorId(id);
        this.modal.abrirParaEditar(usuario);
    }

    async inativar(id) {
        if (!confirm('Deseja inativar este usuário?')) return;
        await this.service.inativar(id);
        await this.carregar();
    }

    async reativar(id) {
        await this.service.atualizar(id, { ativo: true });
        await this.carregar();
    }
}

// Instância global
let usuarioController;
document.addEventListener('DOMContentLoaded', () => {
    usuarioController = new UsuarioController();
});