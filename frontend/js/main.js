/**
 * main.js
 * Entry Point da Aplicacao Frontend — Arena de Combate
 * SRP: inicializacao e orquestracao dos controllers da Arena APENAS
 */
import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController        } from './controllers/ArenaController.js';
import { ModalEdicao            } from './ui/ModalEdicao.js';
import { ArenaAtaquesMagias     } from './ui/ArenaAtaquesMagias.js';
import { atualizarModificadorDOM} from './utils/dnd.js';

const app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', async function() {
    console.log('Arena de Combate TTRPG - Iniciando...');

    // Protecao JWT
    if (typeof AuthService !== 'undefined') {
        AuthService.exigirLogin();
        _exibirUsuarioHeader();
    }

    // Controllers
    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();

    // Modal de Edicao
    app.modals.edicao = new ModalEdicao();

    // Modal Dano/Cura (classe global via script)
    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            window.modalDanoCuraInstance = new ModalDanoCura(
                new DanoCuraService(),
                app.controllers.arena
            );
            console.log('Modal de Dano/Cura inicializado');
        } catch (error) {
            console.error('Erro ao inicializar Modal de Dano/Cura:', error);
        }
    }

    // Modal Condicao (classe global via script)
    if (typeof ModalCondicao !== 'undefined' && typeof CondicaoService !== 'undefined') {
        try {
            window.modalCondicaoInstance = new ModalCondicao(
                new CondicaoService('/api'),
                app.controllers.arena
            );
            console.log('Modal de Condicao inicializado');
        } catch (error) {
            console.error('Erro ao inicializar Modal de Condicao:', error);
        }
    }

    // Eventos de recarregamento apos CRUD no Dashboard
    _configurarEventosRecarregamento();

    // Evento: combatente ativo mudou — renderiza ataques e magias
    // Disparado pelo ArenaController ao avancar turno ou iniciar combate
    // jogador  — exibe ataques e magias cadastrados no Dashboard
    // monstro  — exibe ataques (se houver), sem magias
    // npc      — exibe ataques (se houver), sem magias
    document.addEventListener('combatenteAtivoMudou', function(e) {
        var combatente = e.detail && e.detail.combatente ? e.detail.combatente : null;
        if (!combatente) return;

        var isJogador = combatente.tipo === 'jogador';

        // Renderiza ataques para todos os tipos
        ArenaAtaquesMagias.renderAtaques(
            combatente.ataques || [],
            'arenaAtaquesContainer'
        );

        // Renderiza magias apenas para jogadores
        ArenaAtaquesMagias.renderMagias(
            isJogador ? (combatente.magias_slots || []) : [],
            'arenaMagiasContainer',
            function(slotId, nivel, usados) {
                if (!slotId) return;
                var token = sessionStorage.getItem('rpg_token');
                fetch('/api/magias_slots/' + slotId + '/usados', {
                    method:  'PATCH',
                    headers: {
                        'Content-Type':  'application/json',
                        'Authorization': 'Bearer ' + token
                    },
                    body: JSON.stringify({ usados: usados })
                }).catch(function(err) {
                    console.error('Erro ao persistir slot de magia:', err);
                });
            }
        );
    });

    // Funcoes globais expostas para HTML inline
    window.atualizarModificador = atualizarModificadorDOM;
    window.fecharModalEdicao    = function() { app.modals.edicao.fechar();  };
    window.confirmarDelecao     = function() { app.modals.edicao.deletar(); };
    window.removerImagemEdicao  = function() { _removerImagemUpload('', true); };

    window.abrirModalDanoCura = function() {
        if (window.modalDanoCuraInstance) {
            window.modalDanoCuraInstance.abrir();
        } else {
            console.error('modalDanoCuraInstance nao inicializado');
        }
    };

    window.abrirModalCondicao = function() {
        if (window.modalCondicaoInstance) {
            window.modalCondicaoInstance.abrir();
        } else {
            console.error('modalCondicaoInstance nao inicializado');
        }
    };

    console.log('Arena inicializada com sucesso!');
});

// Exibe nome e perfil do usuario no header da arena
function _exibirUsuarioHeader() {
    var nomeEl   = document.getElementById('nomeUsuarioArena');
    var badgeEl  = document.getElementById('badgePerfilArena');
    var logoutEl = document.getElementById('btnLogoutArena');

    if (nomeEl)   nomeEl.textContent  = AuthService.getNome();
    if (badgeEl)  badgeEl.textContent = AuthService.getPerfil();
    if (logoutEl) logoutEl.addEventListener('click', function() { AuthService.logout(); });
}

// Eventos de recarregamento apos CRUD no Dashboard
function _configurarEventosRecarregamento() {
    ['combatenteCriado', 'combatenteAtualizado', 'combatenteDeletado'].forEach(function(evento) {
        document.addEventListener(evento, function() {
            app.controllers.configuracao.carregarCombatentes();
            app.controllers.configuracao.atualizarSelecionados();
        });
    });

    document.addEventListener('voltarConfiguracao', function() {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.combatentesSelecionados = [];
        app.controllers.configuracao.atualizarSelecionados();
    });
}

// Helper de remocao de imagem (edicao)
function _removerImagemUpload(sufixo, isEdit) {
    if (sufixo === undefined) sufixo = '';
    if (isEdit === undefined) isEdit = false;

    var inputId       = isEdit ? 'editFoto'              : 'inputFoto'         + sufixo;
    var placeholderId = isEdit ? 'editUploadPlaceholder' : 'uploadPlaceholder' + sufixo;
    var previewId     = isEdit ? 'editUploadPreview'     : 'uploadPreview'     + sufixo;

    var input       = document.getElementById(inputId);
    var placeholder = document.getElementById(placeholderId);
    var preview     = document.getElementById(previewId);

    if (input)       input.value             = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display     = 'none';
}

export { app };
window.app = app;