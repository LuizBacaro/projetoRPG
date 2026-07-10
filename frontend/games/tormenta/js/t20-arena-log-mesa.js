/**
 * RF-T12j — log de mesa na arena (rolagens e ações da sessão de combate).
 */
(function (global) {
    'use strict';

    const MAX = 50;
    const TIPOS = {
        sistema: 'Sistema',
        ataque: 'Ataque',
        dano: 'Dano',
        pericia: 'Perícia',
        iniciativa: 'Iniciativa',
        resistencia: 'Resist.',
        pv: 'PV',
        condicao: 'Condição',
        turno: 'Turno',
    };

    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;');
    }

    function fmtHora(ts) {
        try {
            return new Date(ts).toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
            });
        } catch (_e) {
            return '';
        }
    }

    function lista() {
        if (!Array.isArray(global.__t20LogMesa)) global.__t20LogMesa = [];
        return global.__t20LogMesa;
    }

    function render() {
        const host = document.getElementById('t20ArenaLogLista');
        if (!host) return;
        const rows = lista();
        if (!rows.length) {
            host.innerHTML = '<li class="t20-arena-log-vazio">Nenhuma ação registrada neste combate.</li>';
            return;
        }
        host.innerHTML = rows
            .map((row) => {
                const tipo = esc(TIPOS[row.tipo] || row.tipo || '—');
                const hora = esc(fmtHora(row.ts));
                const txt = esc(row.texto || '');
                return `<li class="t20-arena-log-item t20-arena-log-item--${esc(row.tipo || 'sistema')}"><span class="t20-arena-log-meta"><span class="t20-arena-log-hora">${hora}</span> <span class="t20-arena-log-tipo">${tipo}</span></span><span class="t20-arena-log-txt">${txt}</span></li>`;
            })
            .join('');
    }

    function append(tipo, texto) {
        if (!texto) return;
        const arr = lista();
        arr.unshift({
            ts: Date.now(),
            tipo: String(tipo || 'sistema'),
            texto: String(texto),
        });
        if (arr.length > MAX) arr.length = MAX;
        render();
    }

    function clear() {
        global.__t20LogMesa = [];
        render();
    }

    function bindOnce() {
        const btn = document.getElementById('t20ArenaLogLimpar');
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                clear();
                append('sistema', 'Log limpo.');
            });
        }
        render();
    }

    global.T20ArenaLogMesa = {
        append,
        clear,
        render,
        MAX,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindOnce);
    } else {
        bindOnce();
    }
})(typeof window !== 'undefined' ? window : globalThis);
