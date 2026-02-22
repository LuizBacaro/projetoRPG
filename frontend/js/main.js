/**
 * Entry Point da Aplicação Frontend
 * SOLID: SRP - apenas inicialização e orquestração global
 *
 * Arquivos globais (via <script> no index.html, SEM type="module"):
 *   - DanoCuraService.js
 *   - ModalDanoCura.js
 *   - CondicaoService.js
 *   - CondicaoUI.js  (contém class ModalCondicao)
 */
import { ConfiguracaoController }  from './controllers/ConfiguracaoController.js';
import { ArenaController }         from './controllers/ArenaController.js';
import { ModalCadastro }           from './ui/ModalCadastro.js';
import { ModalEdicao }             from './ui/ModalEdicao.js';
import { TipoSelector }            from './ui/TipoSelector.js';
import { atualizarModificadorDOM } from './utils/dnd.js';

const app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Arena de Combate TTRPG - Iniciando...');

    // ── Controllers
    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();

    // ── Modais de cadastro
    app.modals.cadastroJogador = new ModalCadastro('jogador');
    app.modals.cadastroMonstro = new ModalCadastro('monstro');
    app.modals.cadastroNPC     = new ModalCadastro('npc');
    app.modals.edicao          = new ModalEdicao();

    // ── Modal Dano/Cura (classe global via <script>)
    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            window.modalDanoCuraInstance = new ModalDanoCura(
                new DanoCuraService(),
                app.controllers.arena
            );
            console.log('✅ Modal de Dano/Cura inicializado');
        } catch (error) {
            console.error('❌ Erro ao inicializar Modal de Dano/Cura:', error);
        }
    }

    // ── Modal Condição (classe global via <script>)
    if (typeof ModalCondicao !== 'undefined' && typeof CondicaoService !== 'undefined') {
        try {
            window.modalCondicaoInstance = new ModalCondicao(
                new CondicaoService('/api'),
                app.controllers.arena
            );
            console.log('✅ Modal de Condição inicializado');
        } catch (error) {
            console.error('❌ Erro ao inicializar Modal de Condição:', error);
        }
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
    if (listaCombatentes.parentElement.querySelector('.btn-add-combatente')) return;

    const btn     = document.createElement('button');
    btn.className = 'btn-add-combatente';
    btn.innerHTML = '⚔️ Adicionar Combatente';
    btn.addEventListener('click', () => {
        TipoSelector.mostrar((tipo) => {
            if      (tipo === 'jogador') app.modals.cadastroJogador.abrir();
            else if (tipo === 'monstro') app.modals.cadastroMonstro.abrir();
            else if (tipo === 'npc')     app.modals.cadastroNPC.abrir();
        });
    });
    listaCombatentes.parentElement.insertBefore(btn, listaCombatentes);
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
    if      (tipo === 'jogador') app.modals.cadastroJogador?.abrir();
    else if (tipo === 'monstro') app.modals.cadastroMonstro?.abrir();
    else if (tipo === 'npc')     app.modals.cadastroNPC?.abrir();
};

window.fecharSeletorTipo  = () => TipoSelector.fechar();

window.abrirModalDanoCura = function() {
    window.modalDanoCuraInstance
        ? window.modalDanoCuraInstance.abrir()
        : console.error('❌ modalDanoCuraInstance não inicializado');
};

window.abrirModalCondicao = function() {
    window.modalCondicaoInstance
        ? window.modalCondicaoInstance.abrir()
        : console.error('❌ modalCondicaoInstance não inicializado');
};

export { app };
window.app = app;