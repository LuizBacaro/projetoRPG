/**
 * DashboardController
 * SRP: orquestra a tela de dashboard (listagem e cadastro de combatentes)
 * DIP: depende de abstrações (CombatenteService, ModalCadastro, ModalEdicao)
 */
class DashboardController {

    constructor() {
        this.combatenteService = new CombatenteService();
        this.filtroAtual       = 'todos';

        this.modalJogador = new ModalCadastro('jogador');
        this.modalMonstro = new ModalCadastro('monstro');
        this.modalNPC     = new ModalCadastro('npc');
        this.modalEdicao  = new ModalEdicao();

        // Expõe funções globais que os botões inline dos modais precisam
        window.fecharModalCadastro        = () => this.modalJogador.fechar();
        window.fecharModalCadastroMonstro = () => this.modalMonstro.fechar();
        window.fecharModalCadastroNPC     = () => this.modalNPC.fechar();
        window.fecharModalEdicao          = () => this.modalEdicao.fechar();
        window.confirmarDelecao           = () => this.modalEdicao.deletar();
        window.atualizarModificador       = atualizarModificadorDOM;
        window.removerImagem              = () => this._removerImagem('');
        window.removerImagemMonstro       = () => this._removerImagem('Monstro');
        window.removerImagemNPC           = () => this._removerImagem('NPC');
        window.removerImagemEdicao        = () => this._removerImagemEdicao();
        window.previewImagemUpload        = this._previewImagemUpload;

        window.abrirModalCadastro = (tipo) => {
            this._fecharSeletorTipo();
            if (tipo === 'jogador') this.modalJogador.abrir();
            else if (tipo === 'monstro') this.modalMonstro.abrir();
            else if (tipo === 'npc')     this.modalNPC.abrir();
        };
        window.fecharSeletorTipo = () => this._fecharSeletorTipo();

        this._inicializar();
    }

    // ── Init 

    _inicializar() {
        this._configurarAbas();
        this._configurarFiltros();
        this._configurarBotaoNovo();
        this._configurarEventosRecarregamento();
        this.carregarCombatentes();
    }

    // ── Abas 

    _configurarAbas() {
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
            });
        });
    }

    // ── Filtros 

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

    // ── Botão novo 

    _configurarBotaoNovo() {
        document.getElementById('btnNovoCombatente').addEventListener('click', () => {
            document.getElementById('seletorTipo').style.display = 'flex';
        });
    }

    _fecharSeletorTipo() {
        document.getElementById('seletorTipo').style.display = 'none';
    }

    // ── Carrega combatentes 

    async carregarCombatentes() {
        try {
            const tipo        = this.filtroAtual === 'todos' ? null : this.filtroAtual;
            const combatentes = await this.combatenteService.listar(tipo);
            this._renderizarTabela(combatentes);
            this._atualizarResumo(combatentes);
        } catch (err) {
            Toast.error('Erro ao carregar combatentes');
            console.error(err);
        }
    }

    // ── Renderiza tabela 

    _renderizarTabela(combatentes) {
        const tbody = document.getElementById('tabelaCombatentes');

        if (!combatentes.length) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:#64748b">
                Nenhum combatente encontrado. Clique em "+ Novo Combatente" para cadastrar.
            </td></tr>`;
            return;
        }

        tbody.innerHTML = combatentes.map(c => `
            <tr>
                <td><span class="badge badge-${c.tipo}">${c.tipo}</span></td>
                <td>${c.nome}</td>
                <td>${c.classe || '—'}</td>
                <td>${c.nivel}</td>
                <td>${c.hp_maximo}</td>
                <td>${c.iniciativa}</td>
                <td>
                    <button class="btn-acao" title="Editar" data-id="${c.id}" data-acao="editar">✏️</button>
                    <button class="btn-acao" title="Excluir" data-id="${c.id}" data-acao="excluir">🗑️</button>
                </td>
            </tr>
        `).join('');

        // Eventos dos botões de ação
        tbody.querySelectorAll('[data-acao="editar"]').forEach(btn => {
            btn.addEventListener('click', () => this._abrirEdicao(parseInt(btn.dataset.id)));
        });
        tbody.querySelectorAll('[data-acao="excluir"]').forEach(btn => {
            btn.addEventListener('click', () => this._confirmarExclusao(parseInt(btn.dataset.id)));
        });
    }

    // ── Resumo 

    _atualizarResumo(combatentes) {
        const todos    = combatentes.length;
        const jogadores = combatentes.filter(c => c.tipo === 'jogador').length;
        const monstros  = combatentes.filter(c => c.tipo === 'monstro').length;
        const npcs      = combatentes.filter(c => c.tipo === 'npc').length;

        document.getElementById('totalGeral').textContent    = todos;
        document.getElementById('totalJogadores').textContent = jogadores;
        document.getElementById('totalMonstros').textContent  = monstros;
        document.getElementById('totalNPCs').textContent      = npcs;
    }

    // ── Edição / Exclusão 

    _abrirEdicao(id) {
        document.dispatchEvent(new CustomEvent('abrirEdicao', { detail: { id } }));
    }

    async _confirmarExclusao(id) {
        if (!confirm('Deseja excluir este combatente?')) return;
        try {
            await this.combatenteService.deletar(id);
            Toast.success('Combatente excluído!');
            this.carregarCombatentes();
        } catch (err) {
            Toast.error('Erro ao excluir combatente');
        }
    }

    // ── Reload após eventos 

    _configurarEventosRecarregamento() {
        ['combatenteCriado', 'combatenteAtualizado', 'combatenteDeletado'].forEach(ev => {
            document.addEventListener(ev, () => this.carregarCombatentes());
        });
    }

    // ── Upload helpers (globais) 

    _previewImagemUpload(input, previewId, imgId, placeholderId) {
        const file = input.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = e => {
            document.getElementById(placeholderId).style.display = 'none';
            document.getElementById(previewId).style.display     = 'block';
            document.getElementById(imgId).src                   = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    _removerImagem(sufixo) {
        const input       = document.getElementById(`inputFoto${sufixo}`);
        const placeholder = document.getElementById(`uploadPlaceholder${sufixo}`);
        const preview     = document.getElementById(`uploadPreview${sufixo}`);
        if (input)       input.value             = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview)     preview.style.display     = 'none';
    }

    _removerImagemEdicao() {
        const input       = document.getElementById('editFoto');
        const placeholder = document.getElementById('editUploadPlaceholder');
        const preview     = document.getElementById('editUploadPreview');
        if (input)       input.value             = '';
        if (placeholder) placeholder.style.display = 'flex';
        if (preview)     preview.style.display     = 'none';
    }
}

// Instancia após DOM pronto (script já carregado dinamicamente após DOM)
new DashboardController();