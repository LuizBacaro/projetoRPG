/**
 * Entry Point da Aplicação Frontend
 * Inicializa todos os controllers e componentes
 */
import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController } from './controllers/ArenaController.js';
import { ModalCadastro } from './ui/ModalCadastro.js';
import { ModalEdicao } from './ui/ModalEdicao.js';
import { TipoSelector } from './ui/TipoSelector.js';
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
    app.controllers.arena = new ArenaController();
    
    // Inicializar modais
    app.modals.cadastroJogador = new ModalCadastro('jogador');
    app.modals.cadastroMonstro = new ModalCadastro('monstro');
    app.modals.cadastroNPC = new ModalCadastro('npc');
    app.modals.edicao = new ModalEdicao();
    
    console.log('✅ Modais criados:', {
        jogador: app.modals.cadastroJogador,
        monstro: app.modals.cadastroMonstro,
        npc: app.modals.cadastroNPC
    });
    
    // Configurar botão único de cadastro
    configurarBotaoCadastro();
    
    // Configurar eventos de recarregamento
    configurarEventosRecarregamento();
    
    // Expor funções globais necessárias para HTML
    window.atualizarModificador = atualizarModificadorDOM;
    window.fecharModalCadastro = () => app.modals.cadastroJogador.fechar();
    window.fecharModalCadastroMonstro = () => app.modals.cadastroMonstro.fechar();
    window.fecharModalCadastroNPC = () => app.modals.cadastroNPC.fechar();
    window.fecharModalEdicao = () => app.modals.edicao.fechar();
    window.confirmarDelecao = () => app.modals.edicao.deletar();
    window.removerImagem = () => removerImagemUpload('');
    window.removerImagemMonstro = () => removerImagemUpload('Monstro');
    window.removerImagemNPC = () => removerImagemUpload('NPC');
    window.removerImagemEdicao = () => removerImagemUpload('', true);
    
    console.log('✅ Aplicação inicializada com sucesso!');
});

// ==================== CONFIGURAÇÕES ====================

/**
 * Configura botão único de adicionar combatente
 */
function configurarBotaoCadastro() {
    const listaCombatentes = document.getElementById('listaCombatentes');
    
    if (!listaCombatentes) return;
    
    // Criar botão único
    const btnAdicionar = document.createElement('button');
    btnAdicionar.className = 'btn-add-combatente';
    btnAdicionar.innerHTML = '⚔️ Adicionar Combatente';
    
    btnAdicionar.addEventListener('click', () => {
        console.log('🎯 Botão Adicionar Combatente clicado');
        
        TipoSelector.mostrar((tipo) => {
            console.log(`📝 Callback recebeu tipo: ${tipo}`);
            
            if (tipo === 'jogador') {
                console.log('➡️ Abrindo modal de Jogador');
                app.modals.cadastroJogador.abrir();
            } else if (tipo === 'monstro') {
                console.log('➡️ Abrindo modal de Monstro');
                app.modals.cadastroMonstro.abrir();
            } else if (tipo === 'npc') {
                console.log('➡️ Abrindo modal de NPC');
                app.modals.cadastroNPC.abrir();
            } else {
                console.error('❌ Tipo desconhecido:', tipo);
            }
        });
    });
    
    listaCombatentes.parentElement.insertBefore(btnAdicionar, listaCombatentes);
}

/**
 * Configura eventos de recarregamento
 */
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

/**
 * Remove preview de imagem
 */
function removerImagemUpload(sufixo = '', isEdit = false) {
    const prefix = isEdit ? 'edit' : 'input';
    const inputId = `${prefix}Foto${sufixo}`;
    const placeholderId = isEdit ? `${prefix}UploadPlaceholder` : `uploadPlaceholder${sufixo}`;
    const previewId = isEdit ? `${prefix}UploadPreview` : `uploadPreview${sufixo}`;
    
    const input = document.getElementById(inputId);
    const placeholder = document.getElementById(placeholderId);
    const preview = document.getElementById(previewId);
    
    if (input) input.value = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview) preview.style.display = 'none';
}

/**
 * Abre modal de cadastro do tipo específico
 */
window.abrirModalCadastro = function(tipo) {
    console.log(`🔓 abrirModalCadastro chamado com tipo: ${tipo}`);
    
    // Fechar seletor de tipo
    window.fecharSeletorTipo();
    
    // Abrir modal correspondente
    if (tipo === 'jogador' && app.modals.cadastroJogador) {
        app.modals.cadastroJogador.abrir();
    } else if (tipo === 'monstro' && app.modals.cadastroMonstro) {
        app.modals.cadastroMonstro.abrir();
    } else if (tipo === 'npc' && app.modals.cadastroNPC) {
        app.modals.cadastroNPC.abrir();
    } else {
        console.error('❌ Modal não encontrado para tipo:', tipo);
    }
};

/**
 * Fecha seletor de tipo
 */
window.fecharSeletorTipo = function() {
    TipoSelector.fechar();
};

// ==================== EXPORT ====================

export { app };

// ← ADICIONAR ESTA LINHA PARA DEBUG
window.app = app;