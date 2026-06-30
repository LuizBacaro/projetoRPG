/**
 * Ofício v1.3 — especialidades múltiplas (RF-T04-v13b).
 */
(function (global) {
    'use strict';

    let lista = [];

    function q(id) {
        return document.getElementById(id);
    }

    function isV13() {
        if (typeof global.getRegraVersaoAtiva === 'function') {
            return global.T20RegraVersao && global.T20RegraVersao.isV13(global.getRegraVersaoAtiva());
        }
        return false;
    }

    function rowOficio() {
        return document.querySelector('#tblPericias tbody tr[data-per-slug="oficio"]');
    }

    function wrapEsp() {
        return q('t20OficioEspWrap');
    }

    function renderTags() {
        const host = q('t20OficioEspTags');
        if (!host) return;
        host.innerHTML = '';
        lista.forEach((nome, idx) => {
            const tag = document.createElement('span');
            tag.className = 't20-oficio-esp-tag';
            tag.textContent = nome;
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 't20-oficio-esp-del';
            btn.textContent = '×';
            btn.title = 'Remover';
            btn.addEventListener('click', () => {
                lista.splice(idx, 1);
                renderTags();
                atualizarRotuloOficio();
            });
            tag.appendChild(btn);
            host.appendChild(tag);
        });
    }

    function atualizarRotuloOficio() {
        const tr = rowOficio();
        if (!tr) return;
        const span = tr.querySelector('.t20-p-nome');
        if (!span) return;
        if (!isV13() || !lista.length) {
            span.textContent = 'Ofício';
            return;
        }
        span.textContent = `Ofício (${lista.join(', ')})`;
    }

    function ensureUi() {
        const tr = rowOficio();
        const existing = wrapEsp();
        if (!tr || existing) return;
        const td = tr.querySelector('td:nth-child(2)');
        if (!td) return;
        const div = document.createElement('div');
        div.id = 't20OficioEspWrap';
        div.className = 't20-oficio-esp-wrap';
        div.style.display = 'none';
        div.innerHTML =
            '<div id="t20OficioEspTags" class="t20-oficio-esp-tags"></div>' +
            '<div class="t20-oficio-esp-add">' +
            '<input id="t20OficioEspInput" class="t20-input" maxlength="60" placeholder="Especialidade (ex.: alquimia)" />' +
            '<button type="button" class="tormenta-btn" id="t20OficioEspBtn">+</button>' +
            '</div>';
        td.appendChild(div);
        q('t20OficioEspBtn')?.addEventListener('click', adicionar);
        q('t20OficioEspInput')?.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                adicionar();
            }
        });
    }

    function adicionar() {
        const inp = q('t20OficioEspInput');
        if (!inp) return;
        const v = inp.value.trim();
        if (!v) return;
        const key = v.toLowerCase();
        if (lista.some((x) => x.toLowerCase() === key)) {
            inp.value = '';
            return;
        }
        lista.push(v);
        inp.value = '';
        renderTags();
        atualizarRotuloOficio();
    }

    function syncVisibilidade() {
        ensureUi();
        const w = wrapEsp();
        if (w) w.style.display = isV13() ? '' : 'none';
        if (!isV13()) {
            lista = [];
            renderTags();
            atualizarRotuloOficio();
        }
    }

    function lerLista() {
        return lista.slice();
    }

    function aplicarLista(arr) {
        lista = Array.isArray(arr)
            ? arr.map((x) => String(x || '').trim()).filter(Boolean)
            : [];
        syncVisibilidade();
        renderTags();
        atualizarRotuloOficio();
    }

    function initAposTabelaPericias() {
        syncVisibilidade();
    }

    global.T20OficioEspecialidadesV13 = {
        initAposTabelaPericias,
        syncVisibilidade,
        lerLista,
        aplicarLista,
    };
})(typeof window !== 'undefined' ? window : globalThis);
