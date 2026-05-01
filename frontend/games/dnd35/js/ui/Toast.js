/*
   Toast.js
   Implementação clássica (sem ES modules) — usada por GURPS, dashboard, etc.
   Mantém a mesma API de toast.module.js.
 */
(function (global) {
    class Toast {
        static success(texto) {
            Toast.mostrar(texto, 'success');
        }
        static error(texto) {
            Toast.mostrar(texto, 'error');
        }
        static warning(texto) {
            Toast.mostrar(texto, 'warning');
        }
        static info(texto) {
            Toast.mostrar(texto, 'info');
        }

        static mostrar(texto, tipo) {
            if (!tipo) tipo = 'info';
            Toast._injetarEstilos();
            const el = document.createElement('div');
            el.className = 'toast toast-' + tipo;
            el.textContent = texto;
            document.body.appendChild(el);
            setTimeout(() => el.classList.add('show'), 50);
            setTimeout(() => {
                el.classList.remove('show');
                setTimeout(() => el.remove(), 300);
            }, 3000);
        }

        static _injetarEstilos() {
            if (document.getElementById('toast-styles')) return;
            const s = document.createElement('style');
            s.id = 'toast-styles';
            s.textContent = `
            .toast {
                position: fixed; bottom: 1.5rem; right: 1.5rem;
                padding: .75rem 1.25rem; border-radius: .5rem;
                color: #fff; font-size: .9rem; font-weight: 500;
                opacity: 0; transform: translateY(1rem);
                transition: opacity .3s, transform .3s;
                z-index: 99999; max-width: 360px;
                box-shadow: 0 4px 12px rgba(0,0,0,.4);
            }
            .toast.show    { opacity: 1; transform: translateY(0); }
            .toast-success { background: #059669; }
            .toast-error   { background: #dc2626; }
            .toast-warning { background: #d97706; }
            .toast-info    { background: #2563eb; }
        `;
            document.head.appendChild(s);
        }
    }

    global.Toast = Toast;
})(typeof window !== 'undefined' ? window : self);
