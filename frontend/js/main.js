/**
 * Entry Point da Aplicação Frontend
 * Inicializa todos os controllers e componentes
 */
import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController }        from './controllers/ArenaController.js';
import { ModalCadastro }          from './ui/ModalCadastro.js';
import { ModalEdicao }            from './ui/ModalEdicao.js';
import { TipoSelector }           from './ui/TipoSelector.js';
import { ModalDanoCura }          from './ui/ModalDanoCura.js';
import { DanoCuraService }        from './services/DanoCuraService.js';
import { atualizarModificadorDOM } from './utils/dnd.js';

// ==================== STATE GLOBAL ====================
const app = {
    controllers: {},
    modals: {}
};

// ==================== INICIALIZAÇÃO ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Arena de Combate TTRPG - Iniciando...');

    // Inicializar controllers
    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();

    // Inicializar modais de cadastro
    app.modals.cadastroJogador = new ModalCadastro('jogador');
    app.modals.cadastroMonstro = new ModalCadastro('monstro');
    app.modals.cadastroNPC     = new ModalCadastro('npc');
    app.modals.edicao          = new ModalEdicao();

    console.log('✅ Modais criados:', {
        jogador: app.modals.cadastroJogador,
        monstro: app.modals.cadastroMonstro,
        npc:     app.modals.cadastroNPC
    });

    // Inicializar Modal de Dano/Cura
    try {
        const danoCuraService = new DanoCuraService();
        window.modalDanoCuraInstance = new ModalDanoCura(danoCuraService, app.controllers.arena);
        console.log('✅ Modal de Dano/Cura inicializado');
    } catch (error) {
        console.error('❌ Erro ao inicializar Modal de Dano/Cura:', error);
    }

    // Configurar botão de cadastro
    configurarBotaoCadastro();

    // Configurar eventos de recarregamento
    configurarEventosRecarregamento();

    // Expor funções globais necessárias para HTML
    window.atualizarModificador      = atualizarModificadorDOM;
    window.fecharModalCadastro       = () => app.modals.cadastroJogador.fechar();
    window.fecharModalCadastroMonstro = () => app.modals.cadastroMonstro.fechar();
    window.fecharModalCadastroNPC    = () => app.modals.cadastroNPC.fechar();
    window.fecharModalEdicao         = () => app.modals.edicao.fechar();
    window.confirmarDelecao          = () => app.modals.edicao.deletar();
    window.removerImagem             = () => removerImagemUpload('');
    window.removerImagemMonstro      = () => removerImagemUpload('Monstro');
    window.removerImagemNPC          = () => removerImagemUpload('NPC');
    window.removerImagemEdicao       = () => removerImagemUpload('', true);

    console.log('✅ Aplicação inicializada com sucesso!');
});

// ==================== CONFIGURAÇÕES ====================

function configurarBotaoCadastro() {
    const listaCombatentes = document.getElementById('listaCombatentes');
    if (!listaCombatentes) return;

    const btnAdicionar = document.createElement('button');
    btnAdicionar.className = 'btn-add-combatente';
    btnAdicionar.innerHTML = '⚔️ Adicionar Combatente';
    btnAdicionar.addEventListener('click', () => {
        console.log('🎯 Botão Adicionar Combatente clicado');
        TipoSelector.abrir();
    });
    listaCombatentes.parentElement.insertBefore(btnAdicionar, listaCombatentes);
}

function configurarEventosRecarregamento() {
    document.addEventListener('combatenteCriado', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.atualizarSelecionados();
    });
    document.addEventListener('combatenteAtualizado', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.atualizarSelecionados();
    });
    document.addEventListener('combatenteDeletado', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.atualizarSelecionados();
    });
    document.addEventListener('voltarConfiguracao', () => {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.combatentesSelecionados = [];
        app.controllers.configuracao.atualizarSelecionados();
    });
}

function removerImagemUpload(sufixo = '', isEdit = false) {
    const prefix      = isEdit ? 'edit' : 'input';
    const inputId     = `${prefix}Foto${sufixo}`;
    const placeholderId = isEdit ? `${prefix}UploadPlaceholder` : `uploadPlaceholder${sufixo}`;
    const previewId   = isEdit ? `${prefix}UploadPreview` : `uploadPreview${sufixo}`;

    const input       = document.getElementById(inputId);
    const placeholder = document.getElementById(placeholderId);
    const preview     = document.getElementById(previewId);

    if (input)       input.value = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display = 'none';
}

// ==================== GLOBAIS ====================

window.abrirModalCadastro = function(tipo) {
    console.log(`🔓 abrirModalCadastro chamado com tipo: ${tipo}`);
    window.fecharSeletorTipo();
    if      (tipo === 'jogador' && app.modals.cadastroJogador) app.modals.cadastroJogador.abrir();
    else if (tipo === 'monstro' && app.modals.cadastroMonstro) app.modals.cadastroMonstro.abrir();
    else if (tipo === 'npc'     && app.modals.cadastroNPC)     app.modals.cadastroNPC.abrir();
    else console.error('❌ Modal não encontrado para tipo:', tipo);
};

window.fecharSeletorTipo = function() {
    TipoSelector.fechar();
};

window.abrirModalDanoCura = function() {
    console.log('🎯 Tentando abrir modal de Dano/Cura...');
    if (window.modalDanoCuraInstance) {
        window.modalDanoCuraInstance.abrir();
    } else {
        console.error('❌ Modal de Dano/Cura não foi inicializado');
        alert('Erro: Modal de Dano/Cura não está disponível. Recarregue a página.');
    }
};

// ==================== EXPORT ====================
export { app };
window.app = app;