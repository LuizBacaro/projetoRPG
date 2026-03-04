/**
 * ModalUsuario
 * SRP: renderização e controle do modal de cadastro/edição de usuário
 * Carregado via <script>
 */

class ModalUsuario {

    constructor(usuarioService, onSucesso) {
        this.service    = usuarioService;
        this.onSucesso  = onSucesso;
        this.usuarioId  = null;
    }

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

    _renderizar(usuario = {}) {
        const titulo  = this.usuarioId ? 'Editar Usuário' : 'Novo Usuário';
        const inativo = this.usuarioId && !usuario.ativo;

        document.getElementById('modalUsuarioTitulo').textContent = titulo;

        document.getElementById('inputNome').value  = usuario.nome  || '';
        document.getElementById('inputEmail').value = usuario.email || '';
        document.getElementById('inputSenha').value = '';

        // Perfil
        const selPerfil = document.getElementById('selectPerfil');
        selPerfil.value    = usuario.perfil || 'jogador';
        selPerfil.disabled = inativo;

        // Status
        const selStatus = document.getElementById('selectStatus');
        selStatus.value = usuario.ativo ? 'ativo' : 'inativo';

        // Campos bloqueados se inativo (exceto status)
        ['inputNome', 'inputEmail', 'inputSenha'].forEach(id => {
            document.getElementById(id).disabled = inativo;
        });

        // Mensagem de aviso
        const aviso = document.getElementById('avisoInativo');
        if (aviso) aviso.style.display = inativo ? 'block' : 'none';
    }

    async salvar() {
        const nome   = document.getElementById('inputNome').value.trim();
        const email  = document.getElementById('inputEmail').value.trim();
        const senha  = document.getElementById('inputSenha').value;
        const perfil = document.getElementById('selectPerfil').value;
        const ativo  = document.getElementById('selectStatus').value === 'ativo';

        try {
            if (this.usuarioId) {
                // Edição — envia apenas campos preenchidos
                const dados = { perfil, ativo };
                if (nome)  dados.nome  = nome;
                if (email) dados.email = email;
                if (senha) dados.senha = senha;
                await this.service.atualizar(this.usuarioId, dados);
            } else {
                // Criação — todos os campos obrigatórios
                if (!nome || !email || !senha) {
                    alert('Preencha todos os campos obrigatórios.');
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