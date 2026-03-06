/**
 * Toast
 * SRP: apenas exibir notificacoes visuais
 * Compativel com:
 *   - Scripts globais via createElement (window.Toast)
 *   - ES modules via import { Toast } (export)
 */
class Toast {

    static success(texto) { this.mostrar(texto, 'success'); }
    static error(texto)   { this.mostrar(texto, 'error');   }
    static warning(texto) { this.mostrar(texto, 'warning'); }
    static info(texto)    { this.mostrar(texto, 'info');    }

    static mostrar(texto, tipo) {
        if (tipo === undefined) tipo = 'info';
        Toast._injetarEstilos();

        var toast       = document.createElement('div');
        toast.className = 'toast toast-' + tipo;
        toast.textContent = texto;
        document.body.appendChild(toast);

        setTimeout(function() { toast.classList.add('show'); }, 50);
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() { toast.remove(); }, 300);
        }, 3000);
    }

    static _injetarEstilos() {
        if (document.getElementById('toast-styles')) return;

        var style = document.createElement('style');
        style.id  = 'toast-styles';

        var css = '';
        css += '.toast {';
        css += 'position:fixed;';
        css += 'bottom:1.5rem;';
        css += 'right:1.5rem;';
        css += 'padding:.75rem 1.25rem;';
        css += 'border-radius:.5rem;';
        css += 'color:#fff;';
        css += 'font-size:.9rem;';
        css += 'font-weight:500;';
        css += 'opacity:0;';
        css += 'transform:translateY(1rem);';
        css += 'transition:opacity .3s,transform .3s;';
        css += 'z-index:9999;';
        css += 'max-width:360px;';
        css += 'box-shadow:0 4px 12px rgba(0,0,0,.4);';
        css += '}';
        css += '.toast.show{opacity:1;transform:translateY(0);}';
        css += '.toast-success{background:#059669;}';
        css += '.toast-error{background:#dc2626;}';
        css += '.toast-warning{background:#d97706;}';
        css += '.toast-info{background:#2563eb;}';

        style.textContent = css;
        document.head.appendChild(style);
    }
}

window.Toast = Toast;

export { Toast };