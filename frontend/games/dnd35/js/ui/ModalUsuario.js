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
        this.modalEl   = document.getElementById('modalUsuario');
        this.btnSalvar = document.getElementById('btnSalvarModal');
        this._textoSalvarOriginal = this.btnSalvar?.textContent || 'Salvar';
        this._salvando = false;

        // Bind dos botões do modal
        document.getElementById('btnCancelarModal')
            ?.addEventListener('click', () => this.fechar());
        document.getElementById('formUsuario')
            ?.addEventListener('submit', (event) => {
                event.preventDefault();
                this.salvar();
            });
        document.getElementById('btnFecharModalUsuario')
            ?.addEventListener('click', () => this.fechar());

        this.modalEl?.addEventListener('click', (event) => {
            if (event.target === this.modalEl) {
                this.fechar();
            }
        });

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.modalEl?.classList.contains('show')) {
                this.fechar();
            }
        });
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
        this.modalEl?.classList.add('show');
    }

    fechar() {
        this.modalEl?.classList.remove('show');
    }

    // ── Renderização ─────────────────────────────────────────────────────────

    _renderizar(usuario = {}) {
        const editando = !!this.usuarioId;
        const inativo  = editando && !usuario.ativo;

        // Título
        document.getElementById('modalUsuarioTitulo').textContent =
            editando ? 'Editar Usuário' : 'Novo Usuário';
        document.getElementById('modalUsuarioDescricao').textContent = editando
            ? 'Revise perfil, estado operacional e dados sensíveis deste usuário.'
            : 'Crie um novo acesso administrativo ou operacional com parâmetros claros.';

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

    _setEstadoSalvar(salvando) {
        this._salvando = salvando;
        if (!this.btnSalvar) return;

        this.btnSalvar.disabled = salvando;
        this.btnSalvar.textContent = salvando ? 'Salvando...' : this._textoSalvarOriginal;
        this.btnSalvar.setAttribute('aria-busy', salvando ? 'true' : 'false');
    }

    _mostrarMensagemPadrao({
        icone = '⚠️',
        titulo = 'Atenção',
        texto = 'Revise as informações e tente novamente.',
    } = {}) {
        if (window.ModalConfirm && typeof window.ModalConfirm.mostrar === 'function') {
            window.ModalConfirm.mostrar({
                icone,
                titulo,
                texto,
                textoCancelar: 'Fechar',
                textoConfirmar: 'Entendi',
                onCancelar: () => {},
                onConfirmar: () => {},
            });
            return;
        }

        if (window.Toast && typeof window.Toast.error === 'function') {
            window.Toast.error(texto);
            return;
        }

        console.error(texto);
    }

    async salvar() {
        if (this._salvando) return;

        const nome   = document.getElementById('inputNome').value.trim();
        const email  = document.getElementById('inputEmail').value.trim();
        const senha  = document.getElementById('inputSenha').value;
        const perfil = document.getElementById('selectPerfil').value;
        const ativo  = document.getElementById('selectStatus').value === 'ativo';

        if (!this.usuarioId && (!nome || !email || !senha)) {
            this._mostrarMensagemPadrao({
                icone: '🧾',
                titulo: 'Campos obrigatórios',
                texto: 'Preencha todos os campos obrigatórios: Nome, E-mail e Senha.',
            });
            return;
        }

        this._setEstadoSalvar(true);

        try {
            if (this.usuarioId) {
                // ── Edição: envia apenas campos preenchidos
                const dados = { perfil, ativo };
                if (nome)  dados.nome  = nome;
                if (email) dados.email = email;
                if (senha) dados.senha = senha;
                await this.service.atualizar(this.usuarioId, dados);

            } else {
                // ── Criação
                await this.service.criar({ nome, email, senha, perfil, ativo });
            }

            this.fechar();
            this.onSucesso?.();

        } catch (erro) {
            this._mostrarMensagemPadrao({
                icone: '❌',
                titulo: 'Falha ao salvar usuário',
                texto: erro?.message ? `Erro: ${erro.message}` : 'Nao foi possivel salvar o usuario.',
            });
        } finally {
            this._setEstadoSalvar(false);
        }
    }
}