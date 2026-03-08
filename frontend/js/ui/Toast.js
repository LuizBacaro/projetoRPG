/*
   Toast.js
   SRP: notificações visuais — carregado como script CLÁSSICO via carregar()
   ✅ window.Toast → usado pelo dashboard e qualquer script clássico
   ❌ export REMOVIDO → causa SyntaxError em scripts clássicos
*/

class Toast {
    static success(texto) { Toast.mostrar(texto, 'success'); }
    static error(texto)   { Toast.mostrar(texto, 'error');   }
    static warning(texto) { Toast.mostrar(texto, 'warning'); }
    static info(texto)    { Toast.mostrar(texto, 'info');    }

    static mostrar(texto, tipo) {
        if (!tipo) tipo = 'info';
        Toast._injetarEstilos();
        const el       = document.createElement('div');
        el.className   = 'toast toast-' + tipo;
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
        const s  = document.createElement('style');
        s.id     = 'toast-styles';
        s.textContent = `
            .toast {
                position: fixed; bottom: 1.5rem; right: 1.5rem;
                padding: .75rem 1.25rem; border-radius: .5rem;
                color: #fff; font-size: .9rem; font-weight: 500;
                opacity: 0; transform: translateY(1rem);
                transition: opacity .3s, transform .3s;
                z-index: 9999; max-width: 360px;
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

// ✅ Global — disponível em TODOS os contextos
window.Toast = Toast;