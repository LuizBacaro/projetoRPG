import { ConfiguracaoController } from './controllers/ConfiguracaoController.js';
import { ArenaController        } from './controllers/ArenaController.js?v=20260331a';
import { atualizarModificadorDOM} from './utils/dnd.js';
import {
    installGlobalErrorGuards,
    reportDegradedMode,
    safeBootstrap,
} from './utils/graceful-degradation.js';

var app = { controllers: {}, modals: {} };

document.addEventListener('DOMContentLoaded', function() {
    console.log('Arena de Combate TTRPG - Iniciando...');
    installGlobalErrorGuards('arena');

    if (typeof AuthService !== 'undefined') {
        safeBootstrap(
            'auth-arena',
            function() {
                AuthService.exigirLogin();
                _exibirUsuarioHeader();
            },
            'Falha ao validar autenticacao da arena. Recarregue a pagina.'
        );
    }

    app.controllers.configuracao = safeBootstrap(
        'configuracao-controller',
        function() { return new ConfiguracaoController(); },
        'Nao foi possivel iniciar o painel de configuracao. Recursos de pre-combate podem ficar indisponiveis.'
    );
    app.controllers.arena = safeBootstrap(
        'arena-controller',
        function() { return new ArenaController(); },
        'Nao foi possivel iniciar a arena. Tente recarregar a pagina.'
    );
    app.modals.edicao = safeBootstrap(
        'modal-edicao',
        function() { return new ModalEdicao(); },
        'Falha ao iniciar modal de edicao. Acoes de editar podem ficar indisponiveis.'
    );

    if (typeof DanoCuraService !== 'undefined' && typeof ModalDanoCura !== 'undefined') {
        try {
            window.modalDanoCuraInstance = new ModalDanoCura(new DanoCuraService(), app.controllers.arena);
            console.log('Modal de Dano/Cura inicializado');
        } catch (e) {
            reportDegradedMode('modal-dano-cura', e, 'Falha ao iniciar modal de dano/cura.');
        }
    }

    if (typeof ModalCondicao !== 'undefined' && typeof CondicaoService !== 'undefined') {
        try {
            window.modalCondicaoInstance = new ModalCondicao(new CondicaoService('/api'), app.controllers.arena);
            console.log('Modal de Condicao inicializado');
        } catch (e) {
            reportDegradedMode('modal-condicao', e, 'Falha ao iniciar modal de condicoes.');
        }
    }

    _configurarEventosRecarregamento();

    window.atualizarModificador = atualizarModificadorDOM;
    window.fecharModalEdicao    = function() {
        if (app.modals.edicao && typeof app.modals.edicao.fechar === 'function') {
            app.modals.edicao.fechar();
            return;
        }
        reportDegradedMode('modal-edicao', null, 'Modal de edicao indisponivel no momento.');
    };
    window.confirmarDelecao     = function() {
        if (app.modals.edicao && typeof app.modals.edicao.deletar === 'function') {
            app.modals.edicao.deletar();
            return;
        }
        reportDegradedMode('modal-edicao', null, 'Confirmacao de delecao indisponivel no momento.');
    };
    window.removerImagemEdicao  = function() { _removerImagemUpload('', true); };

    window.abrirModalDanoCura = function() {
        if (window.modalDanoCuraInstance) window.modalDanoCuraInstance.abrir();
        else console.error('modalDanoCuraInstance nao inicializado');
    };

    window.abrirModalCondicao = function() {
        if (window.modalCondicaoInstance) window.modalCondicaoInstance.abrir();
        else console.error('modalCondicaoInstance nao inicializado');
    };

    window._finalizarCombate = function() {
        var arena = app.controllers.arena;
        if (arena && typeof arena.finalizarCombate === 'function') {
            arena.finalizarCombate();
            return;
        }
        reportDegradedMode('arena-controller', null, 'Acao de encerrar combate indisponivel no momento.');
    };

    var btnEncerrarCombate = document.getElementById('btnEncerrarCombate');
    if (btnEncerrarCombate) {
        btnEncerrarCombate.addEventListener('click', function() {
            window._finalizarCombate();
        });
    }

    var btnAbrirModalDanoCura = document.getElementById('btnAbrirModalDanoCura');
    if (btnAbrirModalDanoCura) {
        btnAbrirModalDanoCura.addEventListener('click', function() {
            window.abrirModalDanoCura();
        });
    }

    var btnAbrirModalCondicao = document.getElementById('btnAbrirModalCondicao');
    if (btnAbrirModalCondicao) {
        btnAbrirModalCondicao.addEventListener('click', function() {
            window.abrirModalCondicao();
        });
    }

    var btnFecharModalDanoCuraTopo = document.getElementById('btnFecharModalDanoCuraTopo');
    if (btnFecharModalDanoCuraTopo) {
        btnFecharModalDanoCuraTopo.addEventListener('click', function() {
            if (window.modalDanoCuraInstance) {
                window.modalDanoCuraInstance.fechar();
            }
        });
    }

    var btnCancelarModalDanoCura = document.getElementById('btnCancelarModalDanoCura');
    if (btnCancelarModalDanoCura) {
        btnCancelarModalDanoCura.addEventListener('click', function() {
            if (window.modalDanoCuraInstance) {
                window.modalDanoCuraInstance.fechar();
            }
        });
    }

    var btnAplicarModalDanoCura = document.getElementById('btnAplicarModalDanoCura');
    if (btnAplicarModalDanoCura) {
        btnAplicarModalDanoCura.addEventListener('click', function() {
            if (window.modalDanoCuraInstance) {
                window.modalDanoCuraInstance.aplicar();
            }
        });
    }

    var btnFecharModalEdicaoTopo = document.getElementById('btnFecharModalEdicaoTopo');
    if (btnFecharModalEdicaoTopo) {
        btnFecharModalEdicaoTopo.addEventListener('click', function() {
            window.fecharModalEdicao();
        });
    }

    var btnCancelarEdicao = document.getElementById('btnCancelarEdicao');
    if (btnCancelarEdicao) {
        btnCancelarEdicao.addEventListener('click', function() {
            window.fecharModalEdicao();
        });
    }

    var btnDeletarEdicao = document.getElementById('btnDeletarEdicao');
    if (btnDeletarEdicao) {
        btnDeletarEdicao.addEventListener('click', function() {
            window.confirmarDelecao();
        });
    }

    var btnRemoverImagemEdicao = document.getElementById('btnRemoverImagemEdicao');
    if (btnRemoverImagemEdicao) {
        btnRemoverImagemEdicao.addEventListener('click', function(event) {
            event.stopPropagation();
            window.removerImagemEdicao();
        });
    }

    var inputsAtributoEdicao = document.querySelectorAll('.arena-edit-atributo-input');
    inputsAtributoEdicao.forEach(function(input) {
        input.addEventListener('input', function() {
            atualizarModificadorDOM(input);
        });
    });

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
    for (var i = 0; i < eventos.length; i++) {
        (function(ev) {
            document.addEventListener(ev, function() {
                if (!app.controllers.configuracao) return;
                app.controllers.configuracao.carregarCombatentes();
                app.controllers.configuracao.atualizarSelecionados();
            });
        })(eventos[i]);
    }
    document.addEventListener('voltarConfiguracao', function() {
        if (!app.controllers.configuracao) return;
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
    if (input)       input.value               = '';
    if (placeholder) placeholder.style.display = 'flex';
    if (preview)     preview.style.display     = 'none';
}

export { app };
window.app = app;