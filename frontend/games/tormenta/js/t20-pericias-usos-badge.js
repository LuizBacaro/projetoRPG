/**
 * RF-T04i — badge na linha da perícia quando há bônus de uso gravados.
 */
(function (global) {
    'use strict';

    function api() {
        return global.T20PericiasUsos;
    }

    function rowPorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return null;
        return document.querySelector(`#tblPericias tbody tr[data-per-slug="${s}"]`);
    }

    function atualizarBadgeSlug(slugOuNome) {
        const usos = api();
        if (!usos || typeof usos.normalizarSlug !== 'function') return;
        const slug = usos.normalizarSlug(slugOuNome);
        const tr = rowPorSlug(slug);
        if (!tr) return;
        const nomeWrap = tr.querySelector('.t20-p-nome-wrap') || tr.querySelector('.t20-p-nome-cell');
        if (!nomeWrap) return;

        let badge = nomeWrap.querySelector('.t20-pericia-usos-badge');
        const n = typeof usos.contarUsosComBonus === 'function' ? usos.contarUsosComBonus(slug) : 0;
        if (n <= 0) {
            if (badge) badge.remove();
            return;
        }
        const lista =
            typeof usos.listarUsosComBonus === 'function' ? usos.listarUsosComBonus(slug) : [];
        const title = lista.length
            ? `Bônus por uso: ${lista.join(', ')}`
            : `${n} uso(s) com bônus`;
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 't20-pericia-usos-badge';
            badge.setAttribute('role', 'status');
            const nomeSpan = nomeWrap.querySelector('.t20-p-nome');
            if (nomeSpan) nomeSpan.insertAdjacentElement('afterend', badge);
            else nomeWrap.appendChild(badge);
            badge.addEventListener('click', (ev) => {
                ev.preventDefault();
                ev.stopPropagation();
            });
        }
        badge.textContent = n === 1 ? '1 uso' : `${n} usos`;
        badge.title = title;
        badge.hidden = false;
    }

    function atualizarTodosBadges() {
        const usos = api();
        if (!usos || !usos.USOS_POR_SLUG) return;
        Object.keys(usos.USOS_POR_SLUG).forEach((slug) => atualizarBadgeSlug(slug));
        // Limpa badges de slugs sem mapa (ex.: após migração)
        document.querySelectorAll('#tblPericias tbody tr[data-per-slug]').forEach((tr) => {
            const slug = tr.getAttribute('data-per-slug') || '';
            if (!usos.temUsos(slug)) {
                const b = tr.querySelector('.t20-pericia-usos-badge');
                if (b) b.remove();
            }
        });
    }

    global.T20PericiasUsosBadge = atualizarBadgeSlug;
    global.T20PericiasUsosBadgeAll = atualizarTodosBadges;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(atualizarTodosBadges, 400);
        });
    } else {
        setTimeout(atualizarTodosBadges, 400);
    }
})(typeof window !== 'undefined' ? window : globalThis);
