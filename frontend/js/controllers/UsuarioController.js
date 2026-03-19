/**
 * UsuarioController
 * SRP: orquestra a tela de gerenciamento de usuários
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
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    async editar(id) {
        try {
            const usuario = await this.service.buscarPorId(id);
            this.modal.abrirParaEditar(usuario);
        } catch (err) {
            // ✅ CORRIGIDO: Toast em vez de alert()
            Toast.error('Erro ao carregar usuário: ' + err.message);
        }
    }

    /**
     * ✅ CORRIGIDO: modal customizado em vez de confirm() nativo
     */
    inativar(id) {
        this._mostrarModalConfirmacao({
            icone:          '🚫',
            titulo:         'Inativar Usuário',
            texto:          'Deseja inativar este usuário? O acesso será bloqueado.',
            textoCancelar:  'Cancelar',
            textoConfirmar: '🚫 Inativar',
            classeConfirmar: 'modal-confirm-btn-perigo',
            onConfirmar:    () => this._executarInativar(id),
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

    /**
     * ✅ CORRIGIDO: modal customizado em vez de confirm() nativo
     */
    reativar(id) {
        this._mostrarModalConfirmacao({
            icone:          '✅',
            titulo:         'Reativar Usuário',
            texto:          'Deseja reativar este usuário? O acesso será restaurado.',
            textoCancelar:  'Cancelar',
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

    /**
     * Modal customizado de confirmação — SRP: apenas DOM
     */
    _mostrarModalConfirmacao(opcoes) {
        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

        const overlay = document.createElement('div');
        overlay.id        = '_modalConfirmGlobal';
        overlay.className = 'modal-confirm-overlay';
        overlay.innerHTML = `
            <div class="modal-confirm-box">
                <div class="modal-confirm-header">
                    <span class="modal-confirm-icone">${opcoes.icone || '⚠️'}</span>
                    <h3 class="modal-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="modal-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="modal-confirm-botoes">
                    <button class="modal-confirm-btn modal-confirm-cancelar" id="_confirmCancelar">
                        ${opcoes.textoCancelar || 'Cancelar'}
                    </button>
                    <button class="modal-confirm-btn ${opcoes.classeConfirmar || 'modal-confirm-ok'}" id="_confirmOk">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        requestAnimationFrame(() => overlay.classList.add('show'));

        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 250);
        };

        document.getElementById('_confirmCancelar').addEventListener('click', () => {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        });
        document.getElementById('_confirmOk').addEventListener('click', () => {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        });
        overlay.addEventListener('click', (e) => { if (e.target === overlay) fechar(); });

        const onEsc = (e) => {
            if (e.key === 'Escape') { fechar(); document.removeEventListener('keydown', onEsc); }
        };
        document.addEventListener('keydown', onEsc);
    }
}

// ── Instância global ──────────────────────────────────────────────────────────
let usuarioController;
(function init() {
    usuarioController = new UsuarioController();
})();