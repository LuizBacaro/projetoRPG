/**
 * Entry Point da Aplicação Frontend
 * DanoCuraService e ModalDanoCura são classes globais (sem export)
 * Os demais são ES Modules com export nomeado
 */
import { ConfiguracaoController }  from './controllers/ConfiguracaoController.js';
import { ArenaController }         from './controllers/ArenaController.js';
import { ModalCadastro }           from './ui/ModalCadastro.js';
import { ModalEdicao }             from './ui/ModalEdicao.js';
import { TipoSelector }            from './ui/TipoSelector.js';
import { atualizarModificadorDOM } from './utils/dnd.js';

// ⚠️ DanoCuraService e ModalDanoCura NÃO têm export — são carregadas
// como scripts globais via <script> no index.html, não como módulos

const app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Arena de Combate TTRPG - Iniciando...');

    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();

    app.modals.cadastroJogador   = new ModalCadastro('jogador');
    app.modals.cadastroMonstro   = new ModalCadastro('monstro');
    app.modals.cadastroNPC       = new ModalCadastro('npc');
    app.modals.edicao            = new ModalEdicao();

    // DanoCuraService e ModalDanoCura são globais — acessadas via window
    // Só instancia se as classes estiverem disponíveis no escopo global
    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            const danoCuraService        = new DanoCuraService();
            window.modalDanoCuraInstance = new ModalDanoCura(danoCuraService, app.controllers.arena);
            console.log('✅ Modal de Dano/Cura inicializado');
        } catch (error) {
            console.error('❌ Erro ao inicializar Modal de Dano/Cura:', error);
        }
    } else {
        console.warn('⚠️ DanoCuraService ou ModalDanoCura não encontrados no escopo global');
    }

    configurarBotaoCadastro();
    configurarEventosRecarregamento();

    window.atualizarModificador       = atualizarModificadorDOM;
    window.fecharModalCadastro        = () => app.modals.cadastroJogador.fechar();
    window.fecharModalCadastroMonstro = () => app.modals.cadastroMonstro.fechar();
    window.fecharModalCadastroNPC     = () => app.modals.cadastroNPC.fechar();
    window.fecharModalEdicao          = () => app.modals.edicao.fechar();
    window.confirmarDelecao           = () => app.modals.edicao.deletar();
    window.removerImagem              = () => removerImagemUpload('');
    window.removerImagemMonstro       = () => removerImagemUpload('Monstro');
    window.removerImagemNPC           = () => removerImagemUpload('NPC');
    window.removerImagemEdicao        = () => removerImagemUpload('', true);

    console.log('✅ Aplicação inicializada com sucesso!');
});

function configurarBotaoCadastro() {
    const listaCombatentes = document.getElementById('listaCombatentes');
    if (!listaCombatentes) return;

    // Evita duplicar o botão se já existir
    if (listaCombatentes.parentElement.querySelector('.btn-add-combatente')) return;

    const btnAdicionar     = document.createElement('button');
    btnAdicionar.className = 'btn-add-combatente';
    btnAdicionar.innerHTML = '⚔️ Adicionar Combatente';
    btnAdicionar.addEventListener('click', () => TipoSelector.abrir());
    listaCombatentes.parentElement.insertBefore(btnAdicionar, listaCombatentes);
}

function configurarEventosRecarregamento() {
    ['combatenteCriado', 'combatenteAtualizado', 'combatenteDeletado'].forEach(evento => {
        document.addEventListener(evento, () => {
            app.controllers.configuracao.carregarCombatentes();
            app.controllers.configuracao.atualizarSelecionados();
        });
    });

    document.addEventListener('voltarConfiguracao', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.combatentesSelecionados = [];
        app.controllers.configuracao.atualizarSelecionados();
    });
}

function removerImagemUpload(sufixo = '', isEdit = false) {
    const prefix      = isEdit ? 'edit' : 'input';
    const input       = document.getElementById(`${prefix}Foto${sufixo}`);
    const placeholder = document.getElementById(isEdit ? `${prefix}UploadPlaceholder` : `uploadPlaceholder${sufixo}`);
    const preview     = document.getElementById(isEdit ? `${prefix}UploadPreview`     : `uploadPreview${sufixo}`);

    if (input)       input.value             = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display     = 'none';
}

window.abrirModalCadastro = function(tipo) {
    window.fecharSeletorTipo();
    if      (tipo === 'jogador' && app.modals.cadastroJogador) app.modals.cadastroJogador.abrir();
    else if (tipo === 'monstro' && app.modals.cadastroMonstro) app.modals.cadastroMonstro.abrir();
    else if (tipo === 'npc'     && app.modals.cadastroNPC)     app.modals.cadastroNPC.abrir();
    else console.error('❌ Modal não encontrado para tipo:', tipo);
};

window.fecharSeletorTipo  = function() { TipoSelector.fechar(); };

window.abrirModalDanoCura = function() {
    if (window.modalDanoCuraInstance) {
        window.modalDanoCuraInstance.abrir();
    } else {
        console.error('❌ Modal de Dano/Cura não disponível');
    }
};

export { app };
window.app = app;