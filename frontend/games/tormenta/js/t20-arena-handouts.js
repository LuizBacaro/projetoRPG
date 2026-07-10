/**
 * RF-T12f — Handouts revelados na sidebar da arena (mesa ativa).
 */
(function (global) {
    'use strict';

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function campanhaAtivaId() {
        if (global.__t20CampanhaWorkspace && global.__t20CampanhaWorkspace.getCampanhaAtivaId) {
            return global.__t20CampanhaWorkspace.getCampanhaAtivaId();
        }
        return null;
    }

    async function renderHandoutsArena() {
        const host = document.getElementById('t20ArenaHandoutsLista');
        if (!host) return;
        const cid = campanhaAtivaId();
        if (!cid) {
            host.innerHTML = '<li class="t20-arena-handout-vazio">Selecione uma campanha na aba Campanhas.</li>';
            return;
        }
        host.innerHTML = '<li class="t20-arena-handout-vazio">Carregando…</li>';
        try {
            const rows = await new global.TormentaCampanhaService().listarHandoutsVisiveis(cid);
            const arr = Array.isArray(rows) ? rows : [];
            if (!arr.length) {
                host.innerHTML =
                    '<li class="t20-arena-handout-vazio">Nenhum handout revelado nesta mesa.</li>';
                return;
            }
            host.innerHTML = arr
                .map((h) => {
                    const txt = esc((h.corpo_md || '').slice(0, 120));
                    const img = h.imagem_url
                        ? ` <span class="t20-arena-handout-tag">img</span>`
                        : '';
                    return `<li class="t20-arena-handout-item" title="${esc(h.corpo_md || '')}">
                        <strong>${esc(h.titulo)}</strong>${img}
                        ${txt ? `<span class="t20-arena-handout-snippet">${txt}</span>` : ''}
                    </li>`;
                })
                .join('');
        } catch (e) {
            host.innerHTML = `<li class="t20-arena-handout-vazio">${esc(e.message || 'Erro')}</li>`;
        }
    }

    global.T20ArenaHandouts = {
        render: renderHandoutsArena,
        agendar: () => {
            void renderHandoutsArena();
        },
    };

    document.addEventListener('DOMContentLoaded', () => {
        const btn = document.getElementById('t20ArenaHandoutsAtualizar');
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => void renderHandoutsArena());
        }
    });
})(typeof window !== 'undefined' ? window : globalThis);
