/**
 * ModalUsuario
 * SRP: renderização e controle do modal de cadastro/edição de usuário
 * Carregado via <script> dinâmico
 */
class ModalUsuario {

    /**
     * @param {UsuarioService} usuarioService
     * @param {Function} onSucesso - callback chamado após salvar com sucesso
     */
    constructor(usuarioService, onSucesso) {
        this.service   = usuarioService;
        this.onSucesso = onSucesso;
        this.usuarioId = null;

        // Bind dos botões do modal
        document.getElementById('btnCancelarModal')
            ?.addEventListener('click', () => this.fechar());
        document.getElementById('btnSalvarModal')
            ?.addEventListener('click', () => this.salvar());
    }

    // ── Abertura ──────────────────────────────────────────────────────────────

    abrirParaCriar() {
        this.usuarioId = null;
        this._renderizar({ perfil: 'jogador', ativo: true });
        this._abrir();
    }

    abrirParaEditar(usuario) {
        this.usuarioId = usuario.id;
        this._renderizar(usuario);
        this._abrir();
    }

    _abrir() {
        document.getElementById('modalUsuario').style.display = 'flex';
    }

    fechar() {
        document.getElementById('modalUsuario').style.display = 'none';
    }

    // ── Renderização ─────────────────────────────────────────────────────────

    _renderizar(usuario = {}) {
        const editando = !!this.usuarioId;
        const inativo  = editando && !usuario.ativo;

        // Título
        document.getElementById('modalUsuarioTitulo').textContent =
            editando ? 'Editar Usuário' : 'Novo Usuário';

        // Campos
        document.getElementById('inputNome').value  = usuario.nome  || '';
        document.getElementById('inputEmail').value = usuario.email || '';
        document.getElementById('inputSenha').value = '';

        // Perfil
        const selPerfil = document.getElementById('selectPerfil');
        selPerfil.value    = usuario.perfil || 'jogador';
        selPerfil.disabled = inativo;

        // Status
        document.getElementById('selectStatus').value =
            usuario.ativo ? 'ativo' : 'inativo';

        // Bloqueia campos se inativo (exceto status — regra do PDF item f)
        ['inputNome', 'inputEmail', 'inputSenha'].forEach(id => {
            document.getElementById(id).disabled = inativo;
        });

        // Aviso de inativo
        const aviso = document.getElementById('avisoInativo');
        if (aviso) aviso.style.display = inativo ? 'block' : 'none';
    }

    // ── Salvar ────────────────────────────────────────────────────────────────

    async salvar() {
        const nome   = document.getElementById('inputNome').value.trim();
        const email  = document.getElementById('inputEmail').value.trim();
        const senha  = document.getElementById('inputSenha').value;
        const perfil = document.getElementById('selectPerfil').value;
        const ativo  = document.getElementById('selectStatus').value === 'ativo';

        try {
            if (this.usuarioId) {
                // ── Edição: envia apenas campos preenchidos
                const dados = { perfil, ativo };
                if (nome)  dados.nome  = nome;
                if (email) dados.email = email;
                if (senha) dados.senha = senha;
                await this.service.atualizar(this.usuarioId, dados);

            } else {
                // ── Criação: todos os campos são obrigatórios
                if (!nome || !email || !senha) {
                    alert('Preencha todos os campos obrigatórios (Nome, E-mail e Senha).');
                    return;
                }
                await this.service.criar({ nome, email, senha, perfil, ativo });
            }

            this.fechar();
            this.onSucesso?.();

        } catch (erro) {
            alert(`Erro: ${erro.message}`);
        }
    }
}