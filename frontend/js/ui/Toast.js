/**
 * Toast
 * SRP: apenas exibir notificações visuais
 * Compatível com:
 *   - Scripts globais via createElement (window.Toast)
 *   - ES modules via import { Toast } (export)
 */
class Toast {

    static success(texto) { this.mostrar(texto, 'success'); }
    static error(texto)   { this.mostrar(texto, 'error');   }
    static warning(texto) { this.mostrar(texto, 'warning'); }
    static info(texto)    { this.mostrar(texto, 'info');    }

    static mostrar(texto, tipo = 'info') {
        Toast._injetarEstilos();

        const toast       = document.createElement('div');
        toast.className   = `toast toast-${tipo}`;
        toast.textContent = texto;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 50);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    static _injetarEstilos() {
        if (document.getElementById('toast-styles')) return;

        const style    = document.createElement('style');
        style.id       = 'toast-styles';
        style.textContent = `
            .toast {
                position: fixed;
                bottom: 1.5rem;
                right:  1.5rem;
                padding: .75rem 1.25rem;
                border-radius: .5rem;
                color: #fff;
                font-size: .9rem;
                font-weight: 500;
                opacity: 0;
                transform: translateY(1rem);
                transition: opacity .3s, transform .3s;
                z-index: 9999;
                max-width: 360px;
                box-shadow: 0 4px 12px rgba(0,0,0,.4);
            }
            .toast.show    { opacity: 1; transform: translateY(0); }
            .toast-success { background: #059669; }
            .toast-error   { background: #dc2626; }
            .toast-warning { background: #d97706; }
            .toast-info    { background: #2563eb; }
        `;
        document.head.appendChild(style);
    }
}

// ── Para scripts globais (DashboardController, UsuarioController) ─────────
window.Toast = Toast;

// ── Para ES modules (ConfiguracaoController, ArenaController) ─────────────
export { Toast };