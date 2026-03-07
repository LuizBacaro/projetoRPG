import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController        } from './controllers/ArenaController.js';
import { ModalEdicao            } from './ui/ModalEdicao.js';
import { ArenaAtaquesMagias     } from './ui/ArenaAtaquesMagias.js';
import { atualizarModificadorDOM} from './utils/dnd.js';

var app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', function() {
    console.log('Arena de Combate TTRPG - Iniciando...');

    if (typeof AuthService !== 'undefined') {
        AuthService.exigirLogin();
        _exibirUsuarioHeader();
    }

    app.controllers.configuracao = new ConfiguracaoController();
    app.controllers.arena        = new ArenaController();
    app.modals.edicao            = new ModalEdicao();

    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            window.modalDanoCuraInstance = new ModalDanoCura(new DanoCuraService(), app.controllers.arena);
            console.log('Modal de Dano/Cura inicializado');
        } catch (e) { console.error('Erro Modal Dano/Cura:', e); }
    }

    if (typeof ModalCondicao !== 'undefined' && typeof CondicaoService !== 'undefined') {
        try {
            window.modalCondicaoInstance = new ModalCondicao(new CondicaoService('/api'), app.controllers.arena);
            console.log('Modal de Condicao inicializado');
        } catch (e) { console.error('Erro Modal Condicao:', e); }
    }

    _configurarEventosRecarregamento();

    document.addEventListener('combatenteAtivoMudou', function(e) {
        var combatente = (e.detail && e.detail.combatente) ? e.detail.combatente : null;
        if (!combatente) return;

        var isJogador = (combatente.tipo === 'jogador');

        ArenaAtaquesMagias.renderAtaques(
            combatente.ataques || [],
            'arenaAtaquesContainer'
        );

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

    window.atualizarModificador = atualizarModificadorDOM;
    window.fecharModalEdicao    = function() { app.modals.edicao.fechar();  };
    window.confirmarDelecao     = function() { app.modals.edicao.deletar(); };
    window.removerImagemEdicao  = function() { _removerImagemUpload('', true); };

    window.abrirModalDanoCura = function() {
        if (window.modalDanoCuraInstance) window.modalDanoCuraInstance.abrir();
        else console.error('modalDanoCuraInstance nao inicializado');
    };

    window.abrirModalCondicao = function() {
        if (window.modalCondicaoInstance) window.modalCondicaoInstance.abrir();
        else console.error('modalCondicaoInstance nao inicializado');
    };

    console.log('Arena inicializada com sucesso!');
});

function _exibirUsuarioHeader() {
    var nomeEl   = document.getElementById('nomeUsuarioArena');
    var badgeEl  = document.getElementById('badgePerfilArena');
    var logoutEl = document.getElementById('btnLogoutArena');
    if (nomeEl)   nomeEl.textContent  = AuthService.getNome();
    if (badgeEl)  badgeEl.textContent = AuthService.getPerfil();
    if (logoutEl) logoutEl.addEventListener('click', function() { AuthService.logout(); });
}

function _configurarEventosRecarregamento() {
    var eventos = ['combatenteCriado', 'combatenteAtualizado', 'combatenteDeletado'];
    for (var i = 0; i &lt; eventos.length; i++) {
        (function(ev) {
            document.addEventListener(ev, function() {
                app.controllers.configuracao.carregarCombatentes();
                app.controllers.configuracao.atualizarSelecionados();
            });
        })(eventos[i]);
    }
    document.addEventListener('voltarConfiguracao', function() {
        app.controllers.configuracao.carregarCombatentes();
        app.controllers.configuracao.combatentesSelecionados = [];
        app.controllers.configuracao.atualizarSelecionados();
    });
}

function _removerImagemUpload(sufixo, isEdit) {
    if (!sufixo) sufixo = '';
    if (!isEdit) isEdit = false;
    var inputId       = isEdit ? 'editFoto'              : 'inputFoto'         + sufixo;
    var placeholderId = isEdit ? 'editUploadPlaceholder' : 'uploadPlaceholder' + sufixo;
    var previewId     = isEdit ? 'editUploadPreview'     : 'uploadPreview'     + sufixo;
    var input         = document.getElementById(inputId);
    var placeholder   = document.getElementById(placeholderId);
    var preview       = document.getElementById(previewId);
    if (input)       input.value              = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display     = 'none';
}

export { app };
window.app = app;