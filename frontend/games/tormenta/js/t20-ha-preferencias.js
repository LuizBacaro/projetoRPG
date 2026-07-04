/**
 * Preferências de sessão — checkbox Heróis de Arton no wizard de criação.
 */
(function (global) {
    'use strict';

    const KEY = 't20_cad_usar_herois_arton';

    function lerUsarHeroisArton() {
        try {
            return sessionStorage.getItem(KEY) === '1';
        } catch (_e) {
            return false;
        }
    }

    function salvarUsarHeroisArton(ativo) {
        try {
            sessionStorage.setItem(KEY, ativo ? '1' : '0');
        } catch (_e) {
            /* ignore */
        }
    }

    function aplicarCheckboxHeroisArton(cb) {
        if (!cb) return;
        cb.checked = lerUsarHeroisArton();
    }

    global.T20HaPreferencias = {
        lerUsarHeroisArton,
        salvarUsarHeroisArton,
        aplicarCheckboxHeroisArton,
    };
})(typeof window !== 'undefined' ? window : globalThis);
