/**
 * RF-T12i — toggle vista resumida vs completa na ficha do jogador.
 */
(function () {
    const LS_KEY = 't20FichaLayoutCompacto';
    const CLASSE = 'ficha-layout-dnd--compacto';

    function wrapEl() {
        return document.querySelector('.tormenta-ficha-wrap.ficha-layout-dnd');
    }

    function lerPreferencia() {
        try {
            return localStorage.getItem(LS_KEY) === '1';
        } catch (_e) {
            return false;
        }
    }

    function gravarPreferencia(compacto) {
        try {
            localStorage.setItem(LS_KEY, compacto ? '1' : '0');
        } catch (_e) {
            /* ignore */
        }
    }

    function atualizarBotao(btn, compacto) {
        if (!btn) return;
        btn.setAttribute('aria-pressed', compacto ? 'true' : 'false');
        btn.textContent = compacto ? 'Vista completa' : 'Vista compacta';
        btn.title = compacto
            ? 'Mostrar equipamentos, grimório e demais seções da ficha'
            : 'Ocultar seções secundárias — foco em combate e perícias';
    }

    function aplicar(compacto) {
        const wrap = wrapEl();
        if (wrap) wrap.classList.toggle(CLASSE, !!compacto);
        const btn = document.getElementById('btnT20FichaLayoutCompacto');
        atualizarBotao(btn, !!compacto);
        gravarPreferencia(!!compacto);
    }

    function init() {
        const btn = document.getElementById('btnT20FichaLayoutCompacto');
        if (!btn || btn.dataset.bound) return;
        btn.dataset.bound = '1';
        const inicial = lerPreferencia();
        aplicar(inicial);
        btn.addEventListener('click', () => {
            const wrap = wrapEl();
            const agora = wrap ? wrap.classList.contains(CLASSE) : false;
            aplicar(!agora);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window.T20FichaLayoutCompacto = { aplicar, init };
})();
